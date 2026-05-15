import { headers } from "next/headers";

const COUNTRY_HEADER_CANDIDATES = [
  "x-vercel-ip-country",
  "cloudfront-viewer-country",
  "cf-ipcountry",
  "x-country-code",
];

export function getCountryCode(defaultCountry = "US"): string {
  const h = headers();
  for (const key of COUNTRY_HEADER_CANDIDATES) {
    const value = h.get(key);
    if (value && value.trim().length >= 2) {
      return value.trim().toUpperCase();
    }
  }
  return defaultCountry;
}

