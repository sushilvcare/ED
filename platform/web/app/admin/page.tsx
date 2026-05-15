"use client";

import { FormEvent, useState } from "react";

import { apiRequest } from "../../lib/api";

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [summary, setSummary] = useState<Record<string, number> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("Payment Architecture Masterclass");
  const [slug, setSlug] = useState("payment-architecture-masterclass");
  const [description, setDescription] = useState("Learn payment flows from code-level examples.");
  const [price, setPrice] = useState(1499);
  const [moduleSlugs, setModuleSlugs] = useState("payment-processing,webhooks");
  const [videoLocales, setVideoLocales] = useState(
    '{"hi-IN":"/videos/payment-processing/hi-IN/payment-processing.mp4","en-US":"/videos/payment-processing/en-US/payment-processing.mp4"}'
  );

  async function loadSummary() {
    setError(null);
    try {
      const data = await apiRequest<Record<string, number>>("/admin/summary", { token });
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin summary");
    }
  }

  async function createCourse(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiRequest("/courses", {
        method: "POST",
        token,
        body: {
          title,
          slug,
          description,
          price_inr: price,
          status: "published",
          module_slugs: moduleSlugs.split(",").map((item) => item.trim()),
          video_locales: JSON.parse(videoLocales),
        },
      });
      alert("Course created");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create course");
    }
  }

  return (
    <section>
      <h1>Admin Console</h1>
      <div className="card">
        <label>
          Admin token
          <input value={token} onChange={(e) => setToken(e.target.value)} />
        </label>
        <button onClick={loadSummary}>Load Summary</button>
        {summary ? <pre>{JSON.stringify(summary, null, 2)}</pre> : null}
      </div>

      <form className="card" style={{ marginTop: 14 }} onSubmit={createCourse}>
        <h3>Create Course</h3>
        <label>Title<input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
        <label>Slug<input value={slug} onChange={(e) => setSlug(e.target.value)} /></label>
        <label>Description<textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label>
        <label>Price INR<input type="number" value={price} onChange={(e) => setPrice(Number(e.target.value))} /></label>
        <label>Module slugs (comma separated)<input value={moduleSlugs} onChange={(e) => setModuleSlugs(e.target.value)} /></label>
        <label>Video locales JSON<textarea value={videoLocales} onChange={(e) => setVideoLocales(e.target.value)} /></label>
        <button type="submit">Create Published Course</button>
      </form>

      {error ? <p>{error}</p> : null}
    </section>
  );
}
