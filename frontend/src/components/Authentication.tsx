function Authentication() {
  return (
    <section>
      <h2>Authentication</h2>
      <p>
        All endpoints except <code>/health</code> and <code>/demo</code> require
        an API Key.
      </p>
      <p>Include your API Key in the request header as shown below.</p>

      <h4>Header</h4>
      <pre>X-API-Key: your_api_key_here</pre>

      <h4>Example</h4>
      <pre>
        {`curl -X POST http://localhost:8000/player \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_api_key_here" \\
  -d '{"player_name": "Shohei Ohtani"}'`}
      </pre>
    </section>
  );
}

export default Authentication;