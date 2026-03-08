from api.models.player import (
    PlayerValueRequest,
    PlayerBidRequest,
    PlayerValueResponse,
    PlayerBidResponse,
    ValueBreakdown,
    BidBreakdown,
    BatterStats,
    PitcherStats,
)

# ── League Baseline Constants (Roto 5x5 standard) ───────────────────────────
# These values represent average and standard deviation of stats
# across a typical 12-team Roto 5x5 fantasy-relevant player pool.
# Source: derived from historical MLB fantasy league data.

BATTER_BASELINES = {
    "R":   {"mean": 75.0,  "std": 20.0},
    "HR":  {"mean": 18.0,  "std": 10.0},
    "RBI": {"mean": 72.0,  "std": 20.0},
    "SB":  {"mean": 12.0,  "std": 10.0},
    "AVG": {"mean": 0.260, "std": 0.025},
}

PITCHER_BASELINES = {
    "W":    {"mean": 10.0,  "std": 4.0},
    "SV":   {"mean": 10.0,  "std": 14.0},
    "K":    {"mean": 130.0, "std": 50.0},
    "ERA":  {"mean": 4.00,  "std": 0.70},
    "WHIP": {"mean": 1.25,  "std": 0.15},
}

# Maximum theoretical raw z-score sum for normalization
# Set to the approximate z_total of an all-time elite player
Z_MAX_BATTER  = 10.0
Z_MAX_PITCHER = 10.0
RAW_MAX       = 12.0   # z_total + max possible position_bonus

# Hitter/pitcher budget split (standard Roto 5x5 convention)
HIT_PITCH_RATIO = {
    "batter":  0.67,
    "pitcher": 0.33,
}

# Positional scarcity bonus (in z-score units)
POSITION_BONUS = {
    "C":  1.5,
    "SS": 0.8,
    "RP": 0.6,
    "CL": 0.6,
    "SP": 0.4,
    "2B": 0.5,
    "3B": 0.3,
    "1B": 0.0,
    "OF": 0.0,
    "DH": 0.0,
}

# Positional scarcity multiplier for bid calculation
SCARCITY_MULTIPLIER = {
    "C":  1.15,
    "SS": 1.08,
    "2B": 1.05,
    "SP": 1.05,
    "RP": 1.05,
    "CL": 1.05,
    "3B": 1.02,
    "1B": 1.00,
    "OF": 1.00,
    "DH": 1.00,
}


# ── Internal Helpers ─────────────────────────────────────────────────────────

def _zscore(value: float, mean: float, std: float) -> float:
    """Compute z-score. Returns 0.0 if std is 0 to prevent division by zero."""
    if std == 0:
        return 0.0
    return (value - mean) / std


def _normalize(value: float, max_val: float) -> float:
    """Scale value to [0.0, 100.0] range, clipped at boundaries."""
    if max_val == 0:
        return 0.0
    scaled = (value / max_val) * 100.0
    return max(0.0, min(100.0, scaled))


def _compute_z_scores(stats: BatterStats | PitcherStats, player_type: str) -> float:
    """
    Compute total z-score across all 5 Roto categories.
    For pitchers, ERA and WHIP are inverted (lower is better).
    """
    if player_type == "batter":
        b = BATTER_BASELINES
        z_total = (
            _zscore(stats.R,   b["R"]["mean"],   b["R"]["std"])
            + _zscore(stats.HR,  b["HR"]["mean"],  b["HR"]["std"])
            + _zscore(stats.RBI, b["RBI"]["mean"], b["RBI"]["std"])
            + _zscore(stats.SB,  b["SB"]["mean"],  b["SB"]["std"])
            + _zscore(stats.AVG, b["AVG"]["mean"], b["AVG"]["std"])
        )
    else:
        p = PITCHER_BASELINES
        # ERA and WHIP: negate z-score so that lower value = higher z
        z_total = (
            _zscore(stats.W,    p["W"]["mean"],    p["W"]["std"])
            + _zscore(stats.SV,   p["SV"]["mean"],   p["SV"]["std"])
            + _zscore(stats.K,    p["K"]["mean"],    p["K"]["std"])
            - _zscore(stats.ERA,  p["ERA"]["mean"],  p["ERA"]["std"])
            - _zscore(stats.WHIP, p["WHIP"]["mean"], p["WHIP"]["std"])
        )
    return z_total


def _get_position_bonus(position: str) -> float:
    """Return positional scarcity bonus in z-score units."""
    return POSITION_BONUS.get(position.upper(), 0.0)


def _get_risk_penalty(stats: BatterStats | PitcherStats, player_type: str) -> float:
    """
    Compute total risk penalty in z-score units.
    Multiple conditions can apply simultaneously.
    """
    penalty = 0.0

    if player_type == "batter":
        # Insufficient playing time
        if stats.AB < 300:
            penalty += 0.5
        # Poor stolen base efficiency
        total_attempts = stats.SB + stats.CS
        if total_attempts > 0 and (stats.CS / total_attempts) > 0.35:
            penalty += 0.2

    else:
        # Insufficient innings pitched (starting pitcher threshold)
        if stats.IP < 100:
            penalty += 0.5
        # High ERA hurts roto standings significantly
        if stats.ERA > 4.50:
            penalty += 0.3

    return penalty


# ── Core Function 1: player_value ────────────────────────────────────────────

def compute_player_value(request: PlayerValueRequest) -> PlayerValueResponse:
    """
    Compute player_value (0.0 ~ 100.0) using Roto 5x5 z-score method.

    Pipeline:
      1. z_total      = sum of z-scores for 5 roto categories
      2. raw_score    = z_total + position_bonus - risk_penalty
      3. stat_score   = normalize(z_total, Z_MAX)
      4. player_value = normalize(raw_score, RAW_MAX)
    """
    z_max = Z_MAX_BATTER if request.player_type == "batter" else Z_MAX_PITCHER

    z_total         = _compute_z_scores(request.stats, request.player_type)
    position_bonus  = _get_position_bonus(request.position)
    risk_penalty    = _get_risk_penalty(request.stats, request.player_type)

    raw_score    = z_total + position_bonus - risk_penalty
    stat_score   = _normalize(z_total,   z_max)
    player_value = _normalize(raw_score, RAW_MAX)

    # Scale bonus and penalty to 0~100 for readable breakdown
    bonus_scaled   = _normalize(position_bonus, RAW_MAX)
    penalty_scaled = _normalize(risk_penalty,   RAW_MAX)

    return PlayerValueResponse(
        player_name=request.player_name,
        player_type=request.player_type,
        player_value=round(player_value, 1),
        value_breakdown=ValueBreakdown(
            stat_score=round(stat_score,     1),
            position_bonus=round(bonus_scaled,   1),
            risk_penalty=round(penalty_scaled,   1),
        ),
    )


# ── Core Function 2: recommended_bid ─────────────────────────────────────────

def compute_recommended_bid(request: PlayerBidRequest) -> PlayerBidResponse:
    """
    Compute recommended_bid (integer dollar amount) using player_value
    adjusted for positional scarcity and real-time draft context.

    Pipeline:
      1. base_price       = (player_value / 100) * total_budget * HIT_PITCH_RATIO
      2. adjusted_price   = base_price * scarcity_multiplier
      3. spendable        = my_remaining_budget - (my_remaining_roster_spots - 1)
      4. draft_adjustment = 1.0 + (budget_ratio - 0.5) * 0.2 * draft_progress
      5. recommended_bid  = clip(round(adjusted_price * draft_adjustment), 1, spendable)
    """
    # Reuse player_value computation
    value_response = compute_player_value(
        PlayerValueRequest(
            player_name=request.player_name,
            player_type=request.player_type,
            position=request.position,
            stats=request.stats,
            league_context=request.league_context,
        )
    )
    player_value = value_response.player_value

    lc = request.league_context
    dc = request.draft_context
    pos = request.position.upper()

    # Step 1: base price
    ratio      = HIT_PITCH_RATIO.get(request.player_type, 0.5)
    base_price = (player_value / 100.0) * lc.total_budget * ratio

    # Step 2: scarcity multiplier
    multiplier     = SCARCITY_MULTIPLIER.get(pos, 1.0)
    adjusted_price = base_price * multiplier
    scarcity_adj   = adjusted_price - base_price

    # Step 3: budget ceiling
    min_reserve = dc.my_remaining_roster_spots - 1
    spendable   = max(1, dc.my_remaining_budget - min_reserve)

    # Step 4: draft progress adjustment
    total_players  = lc.league_size * lc.roster_size
    draft_progress = dc.drafted_players_count / total_players if total_players > 0 else 0.0
    budget_ratio   = spendable / dc.my_remaining_budget if dc.my_remaining_budget > 0 else 0.5

    draft_multiplier = 1.0 + (budget_ratio - 0.5) * 0.2 * draft_progress
    draft_adj        = adjusted_price * draft_multiplier - adjusted_price

    # Step 5: final bid
    raw_bid         = adjusted_price * draft_multiplier
    recommended_bid = max(1, min(round(raw_bid), spendable))

    return PlayerBidResponse(
        player_name=request.player_name,
        player_type=request.player_type,
        player_value=player_value,
        recommended_bid=recommended_bid,
        bid_breakdown=BidBreakdown(
            base_price=round(base_price,   2),
            scarcity_adjustment=round(scarcity_adj, 2),
            draft_adjustment=round(draft_adj,    2),
            max_spendable=spendable,
        ),
    )