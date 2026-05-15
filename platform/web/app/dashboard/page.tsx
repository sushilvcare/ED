"use client";

import { useState } from "react";

import CourseVideoPlayer from "../../components/CourseVideoPlayer";
import { apiRequest } from "../../lib/api";

type Enrollment = {
  id: string;
  course_id: string;
};

export default function DashboardPage() {
  const [token, setToken] = useState("");
  const [countryCode, setCountryCode] = useState("IN");
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedModule, setSelectedModule] = useState("payment-processing");

  async function loadEnrollments() {
    setError(null);
    try {
      const data = await apiRequest<Enrollment[]>("/enrollments/my", { token });
      setEnrollments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load enrollments");
    }
  }

  return (
    <section>
      <h1>Student Dashboard</h1>
      <div className="card">
        <label>
          Access token
          <input value={token} onChange={(e) => setToken(e.target.value)} />
        </label>
        <button onClick={loadEnrollments}>Load my enrollments</button>
        {error ? <p>{error}</p> : null}
        <p>Enrollments: {enrollments.length}</p>
      </div>

      <div className="card" style={{ marginTop: 14 }}>
        <h3>Course Video Player</h3>
        <label>
          Country code
          <input value={countryCode} onChange={(e) => setCountryCode(e.target.value.toUpperCase())} />
        </label>
        <label>
          Module slug
          <input value={selectedModule} onChange={(e) => setSelectedModule(e.target.value)} />
        </label>
        <CourseVideoPlayer moduleSlug={selectedModule} countryCode={countryCode} />
      </div>
    </section>
  );
}
