import React from "react";
import CourseVideoPlayer from "./CourseVideoPlayer";

export default function CoursePage() {
  const moduleSlug = "payment-processing";
  const countryCode = "IN"; // Replace with geo-IP or user profile country.

  return (
    <main>
      <h2>Payment Processing Module</h2>
      <CourseVideoPlayer
        moduleSlug={moduleSlug}
        countryCode={countryCode}
        title="Module Video"
      />
    </main>
  );
}

