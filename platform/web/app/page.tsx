import Link from "next/link";

export default function HomePage() {
  return (
    <section>
      <h1>EdTech Creator Platform</h1>
      <p>Generate feature-based engineering courses and sell them through your own catalog.</p>
      <div className="grid" style={{ marginTop: 18 }}>
        <div className="card">
          <h3>1) Course Generator</h3>
          <p>Repo parse, module extraction, bilingual video generation.</p>
        </div>
        <div className="card">
          <h3>2) Commerce Backend</h3>
          <p>Users, courses, orders, enrollments, role-based access.</p>
        </div>
        <div className="card">
          <h3>3) Learner Frontend</h3>
          <p>Catalog, checkout, dashboard, locale-based video delivery.</p>
        </div>
      </div>
      <p style={{ marginTop: 18 }}>
        Go to <Link href="/catalog">Catalog</Link> to view publishable courses.
      </p>
    </section>
  );
}
