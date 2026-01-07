import React, { useEffect, useState } from "react";
import "./App.css";

import {
  collection,
  addDoc,
  onSnapshot,
  query,
  orderBy,
} from "firebase/firestore";
import { db } from "../firebase";

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [comments, setComments] = useState<string[]>([]);

  // 🔹 Start Collaboration (Session create)
  const startSession = () => {
  setSessionId("988ce244-094d-402a-bb94-3d492b811e6e");
};


  // 🔹 Add Comment
  const addComment = async () => {
    if (!comment.trim() || !sessionId) return;

    await addDoc(
      collection(db, "sessions", sessionId, "comments"),
      {
        text: comment,
        createdAt: Date.now(),
      }
    );

    setComment("");
  };

  // 🔹 Realtime listener
  useEffect(() => {
    if (!sessionId) return;

    const q = query(
      collection(db, "sessions", sessionId, "comments"),
      orderBy("createdAt")
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      console.log("Realtime users synced via Firestore");

      const list: string[] = [];
      snapshot.forEach((doc) => {
        list.push(doc.data().text);
      });
      setComments(list);
    });

    return () => unsubscribe();
  }, [sessionId]);

  return (
    <div className="container">
      <h2>CollabBoard</h2>
      <p className="subtitle">Collaborative feedback for Adobe Express</p>

      {/* Start Collaboration */}
      {!sessionId && (
        <button onClick={startSession}>
          Start Collaboration
        </button>
      )}

      {/* Session Active */}
      {sessionId && (
        <>
          <div className="session-box">
            <p className="status">Collaboration Active 🟢</p>
            <p className="session">
              Session ID: <b>{sessionId}</b>
            </p>
          </div>

          {/* Add Comment */}
          <input
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Write a comment..."
          />

          <button onClick={addComment}>
            Add Comment
          </button>

          {/* Comments */}
          <div className="comments">
            <h4>Feedback</h4>

            {comments.length === 0 && (
              <p className="muted">No comments yet</p>
            )}

            {comments.map((c, i) => (
              <div key={i} className="comment">
                💬 {c}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
