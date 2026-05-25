"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch("http://localhost:8000");
        const data = await res.json();
        setMessage(data.message);
      } catch {
        setMessage("Backend not reachable");
      }
    }
    fetchData();
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui" }}>
      <h1>Welcome to Journex University</h1>
      <p>{message}</p>
    </div>
  );
}