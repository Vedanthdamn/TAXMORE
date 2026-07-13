// Mirrors docs/extracted/hra_cities.json (kept in sync manually - that
// file is UNVERIFIED, see its note: Rule 2A isn't in the source PDFs,
// this list is from general knowledge, not extracted from them).
export const METRO_CITIES = ["Mumbai", "Delhi", "Kolkata", "Chennai"] as const;

export const OTHER_CITY_OPTION = "Other (non-metro)";

export const CITY_OPTIONS = [...METRO_CITIES, OTHER_CITY_OPTION];
