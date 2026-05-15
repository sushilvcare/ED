"use client";

import { FormEvent, useState } from "react";

import { apiRequest } from "../../lib/api";

export default function AuthPage() {
  const [mode, setMode] = useState<"login" | "register">("register");
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin12345");
  const [fullName, setFullName] = useState("Admin User");
  const [role, setRole] = useState("admin");
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (mode === "register") {
        await apiRequest("/auth/register", {
          method: "POST",
          body: { email, password, full_name: fullName, role },
        });
        setMode("login");
        return;
      }
      const data = await apiRequest<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: { email, password },
      });
      setToken(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Auth failed");
    }
  }

  return (
    <section>
      <h1>Auth</h1>
      <p>Use this page to create users and get JWT token.</p>
      <form className="card" onSubmit={submit}>
        <label>
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value as "login" | "register")}>
            <option value="register">Register</option>
            <option value="login">Login</option>
          </select>
        </label>
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        {mode === "register" ? (
          <>
            <label>Full name<input value={fullName} onChange={(e) => setFullName(e.target.value)} /></label>
            <label>
              Role
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="admin">admin</option>
                <option value="creator">creator</option>
                <option value="student">student</option>
              </select>
            </label>
          </>
        ) : null}
        <button type="submit">{mode === "register" ? "Register" : "Login"}</button>
      </form>
      {token ? <pre className="card">{token}</pre> : null}
      {error ? <p>{error}</p> : null}
    </section>
  );
}
