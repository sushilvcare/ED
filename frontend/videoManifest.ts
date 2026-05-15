export type LocaleManifest = {
  country_to_locale: Record<string, string>;
  style_to_locale?: Record<string, string>;
  modules: Record<string, Record<string, string>>;
};

export function resolveLocaleByCountry(
  manifest: LocaleManifest,
  countryCode: string,
  fallbackLocale = "en-US"
): string {
  return manifest.country_to_locale[countryCode] ?? fallbackLocale;
}

export function resolveVideoUrl(
  manifest: LocaleManifest,
  moduleSlug: string,
  countryCode: string,
  fallbackLocale = "en-US"
): string | null {
  const moduleVideos = manifest.modules[moduleSlug];
  if (!moduleVideos) {
    return null;
  }
  const locale = resolveLocaleByCountry(manifest, countryCode, fallbackLocale);
  return moduleVideos[locale] ?? moduleVideos[fallbackLocale] ?? null;
}

export function normalizeVideoPath(path: string): string {
  // Convert generator's container path to frontend static path.
  // Example: /work/output/videos/authentication/hi-IN/authentication.mp4
  // Result: /videos/authentication/hi-IN/authentication.mp4
  if (path.startsWith("/work/output/videos/")) {
    return path.replace("/work/output/videos/", "/videos/");
  }
  return path;
}

