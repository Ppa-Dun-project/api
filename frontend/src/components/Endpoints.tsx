function Endpoints() {
  return (
    <section>
      <h2>Endpoints</h2>

      <h3>POST /player</h3>
      <p>Returns recommended bid and player value for a given player.</p>

      <h4>Request</h4>
      <pre>
        {JSON.stringify({ player_name: "Shohei Ohtani" }, null, 2)}
      </pre>

      <h4>Response</h4>
      <pre>
        {JSON.stringify(
          {
            player_name: "Shohei Ohtani",
            recommended_bid: 42,
            player_value: 87,
          },
          null,
          2
        )}
      </pre>

      <h4>Authentication</h4>
      <pre>X-API-Key: your_api_key_here</pre>
    </section>
  );
}

export default Endpoints;