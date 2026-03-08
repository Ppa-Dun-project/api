from fastapi import APIRouter
from api.models.player import (
    PlayerValueRequest,
    PlayerValueResponse,
    PlayerBidRequest,
    PlayerBidResponse,
)
from api.services.player import compute_player_value, compute_recommended_bid

router = APIRouter()


@router.post("/player/value", response_model=PlayerValueResponse)
def player_value(request: PlayerValueRequest):
    """
    Compute player_value (0.0 ~ 100.0) for a given player.
    Requires player stats and league context in the request body.
    """
    return compute_player_value(request)


@router.post("/player/bid", response_model=PlayerBidResponse)
def player_bid(request: PlayerBidRequest):
    """
    Compute recommended_bid (integer dollar) for auction drafts.
    Requires player stats, league context, and draft context in the request body.
    """
    return compute_recommended_bid(request)