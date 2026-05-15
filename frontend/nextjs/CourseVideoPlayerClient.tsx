"use client";

import CourseVideoPlayer from "../CourseVideoPlayer";
import { LocaleManifest } from "../videoManifest";

type CourseVideoPlayerClientProps = {
  moduleSlug: string;
  countryCode: string;
  manifest?: LocaleManifest | null;
};

export default function CourseVideoPlayerClient({
  moduleSlug,
  countryCode,
  manifest = null,
}: CourseVideoPlayerClientProps) {
  return (
    <CourseVideoPlayer
      moduleSlug={moduleSlug}
      countryCode={countryCode}
      initialManifest={manifest}
      title="Course Video"
    />
  );
}

