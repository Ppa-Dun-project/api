import { useState } from "react";

function Demo() {
  const [playerName, setPlayerName] = useState("");
  const [result, setResult] = useState<null | {
    player_name: string;
    recommended_bid: number;
    player_value: number;
  }>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleDemo = async () => {
    if (!playerName) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/demo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_name: playerName }),
      });

      if (!response.ok) {
        setError("Something went wrong. Please try again.");
        return;
      }

      const data = await response.json();
      setResult(data);
    } catch (e) {
      setError("Failed to connect to the API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Try it out</h2>
      <p>Enter a player name and see the API response.</p>

      <input
        type="text"
        placeholder="e.g. Shohei Ohtani"
        value={playerName}
        onChange={(e) => setPlayerName(e.target.value)}
      />
      <button onClick={handleDemo} disabled={loading}>
        {loading ? "Loading..." : "Submit"}
      </button>

      {error && <p>{error}</p>}

      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}
    </section>
  );
}

export default Demo;