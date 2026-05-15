"use client";

import { useEffect, useMemo, useState } from "react";

type LocaleManifest = {
  country_to_locale: Record<string, string>;
  modules: Record<string, Record<string, string>>;
};

function normalizePath(path: string): string {
  if (path.startsWith("/work/output/videos/")) {
    return path.replace("/work/output/videos/", "/videos/");
  }
  return path;
}

export default function CourseVideoPlayer({
  moduleSlug,
  countryCode,
}: {
  moduleSlug: string;
  countryCode: string;
}) {
  const [manifest, setManifest] = useState<LocaleManifest | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadManifest() {
      try {
        const response = await fetch("/videos/locale-manifest.json");
        if (!response.ok) {
          throw new Error(`Manifest not found (${response.status})`);
        }
        setManifest((await response.json()) as LocaleManifest);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load video manifest");
      }
    }
    void loadManifest();
  }, []);

  const videoUrl = useMemo(() => {
    if (!manifest) {
      return null;
    }
    const locale = manifest.country_to_locale[countryCode] ?? "en-US";
    const moduleVideos = manifest.modules[moduleSlug] ?? {};
    const path = moduleVideos[locale] ?? moduleVideos["en-US"] ?? null;
    return path ? normalizePath(path) : null;
  }, [manifest, moduleSlug, countryCode]);

  if (error) {
    return <p>Video load error: {error}</p>;
  }
  if (!manifest) {
    return <p>Loading module video...</p>;
  }
  if (!videoUrl) {
    return <p>No video available for this locale yet.</p>;
  }

  return (
    <video controls preload="metadata" style={{ width: "100%", maxWidth: 960 }}>
      <source src={videoUrl} type="video/mp4" />
      Your browser does not support video playback.
    </video>
  );
}
