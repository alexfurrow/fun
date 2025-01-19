// src/App.js
import React, { useState } from "react";

function App() {
  // State to hold user input and response
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Show loading state while waiting for API response
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
    setIsLoading(false); //End loading state
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Loremasater</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your prompt"
          style={{
            padding: "10px",
            width: "300px",
            fontSize: "16px",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "10px 20px",
            marginLeft: "10px",
            fontSize: "16px",
            cursor: "pointer",
          }}
        >
          Submit
        </button>
      </form>

      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div
          style={{
            border: "1px solid #ddd",
            padding: "15px",
            width: "60%",
            margin: "0 auto",
            textAlign: "left",
          }}
        >
          <h3>API Response:</h3>
          <p>{response || "No response yet!"}</p>
        </div>
      )}
    </div>
  );
}

export default App;