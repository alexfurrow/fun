// src/App.js
import React, { useState } from "react";

function App() {
  // State to hold user input and response
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Replace with your backend API URL
      const res = await fetch("http://localhost:5000/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      if (data.reply) {
        setResponse(data.reply); // Update resopnse with the reply from OpenAi
      } else if (data.error) {
        setResponse('Error: ${data.error}');
      }
    } catch (error) {
      console.error("Error:", error);
      setResponse("An error occurred while communicating with the server.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>React Frontend</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type something..."
          style={{ padding: "10px", width: "200px" }}
        />
        <button type="submit" style={{ padding: "10px 20px", marginLeft: "10px" }}>
          Submit
        </button>
      </form>
      {response && (
        <div style={{ marginTop: "20px", fontSize: "18px", color: "blue" }}>
          <strong>Response:</strong> {response}
        </div>
      )}
    </div>
  );
}

export default App;
