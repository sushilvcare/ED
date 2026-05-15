"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiRequest, Course } from "../../lib/api";

export default function CatalogPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCourses() {
      try {
        const data = await apiRequest<Course[]>("/courses?status=published");
        setCourses(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load courses");
      }
    }
    void loadCourses();
  }, []);

  return (
    <section>
      <h1>Course Catalog</h1>
      {error ? <p>{error}</p> : null}
      <div className="grid">
        {courses.map((course) => (
          <div className="card" key={course.id}>
            <h3>{course.title}</h3>
            <p>{course.description}</p>
            <p>Price: Rs.{course.price_inr}</p>
            <p>Modules: {course.module_slugs.join(", ") || "-"}</p>
            <Link href={`/checkout/${course.id}`}>Buy now</Link>
          </div>
        ))}
      </div>
      {!error && courses.length === 0 ? <p>No published courses yet.</p> : null}
    </section>
  );
}
