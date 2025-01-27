// src/App.js
import React, { useState } from "react";
import Login from './components/Login';

function App() {
  // State to hold user input and response
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Show loading state while waiting for API response
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Log the request for debugging
      console.log('Sending request to:', "http://localhost:5000/api/yap");
      console.log('Request body:', { content: input });
      
      const res = await fetch("http://localhost:5000/api/yap", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ content: input }),
      });
      
      // Log the response for debugging
      console.log('Response status:', res.status);
      
      if (!res.ok) {
        if (res.status === 401) {
          localStorage.removeItem('token');
          setIsLoggedIn(false);
          throw new Error('Session expired. Please login again.');
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      if (data.refined_text) {
        setResponse(data.refined_text);
      } else if (data.error) {
        setResponse(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error("Error:", error);
      setResponse(`Error: ${error.message}`);
    }
    setIsLoading(false); //End loading state
  };

  if (!isLoggedIn) {
    return <Login onLoginSuccess={() => setIsLoggedIn(true)} />;
  }

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