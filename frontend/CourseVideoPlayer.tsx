import React, { useEffect, useMemo, useState } from "react";
import { LocaleManifest, normalizeVideoPath, resolveVideoUrl } from "./videoManifest";

type CourseVideoPlayerProps = {
  moduleSlug: string;
  countryCode: string;
  manifestUrl?: string;
  initialManifest?: LocaleManifest | null;
  className?: string;
  title?: string;
};

export default function CourseVideoPlayer({
  moduleSlug,
  countryCode,
  manifestUrl = "/videos/locale-manifest.json",
  initialManifest = null,
  className,
  title,
}: CourseVideoPlayerProps) {
  const [manifest, setManifest] = useState<LocaleManifest | null>(initialManifest);
  const [loading, setLoading] = useState(!initialManifest);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialManifest) {
      return;
    }
    let isActive = true;
    async function loadManifest() {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(manifestUrl);
        if (!response.ok) {
          throw new Error(`Manifest fetch failed (${response.status})`);
        }
        const data = (await response.json()) as LocaleManifest;
        if (isActive) {
          setManifest(data);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof Error ? err.message : "Unknown manifest error");
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    void loadManifest();
    return () => {
      isActive = false;
    };
  }, [manifestUrl, initialManifest]);

  const resolvedVideoUrl = useMemo(() => {
    if (!manifest) {
      return null;
    }
    const path = resolveVideoUrl(manifest, moduleSlug, countryCode);
    return path ? normalizeVideoPath(path) : null;
  }, [manifest, moduleSlug, countryCode]);

  if (loading) {
    return (
      <div className={className}>
        <p>Loading course video...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={className}>
        <p>Could not load video manifest.</p>
        <small>{error}</small>
      </div>
    );
  }

  if (!resolvedVideoUrl) {
    return (
      <div className={className}>
        <p>Video not available for this module/country yet.</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {title ? <h3>{title}</h3> : null}
      <video controls preload="metadata" width={960}>
        <source src={resolvedVideoUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
}

