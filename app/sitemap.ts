import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://equitylens-ai-web.vercel.app";
  return [
    "", "/company", "/compare", "/markets", "/filings", "/learn"
  ].map((path) => ({
    url: `${base}${path}`,
    changeFrequency: path === "/filings" || path === "/markets" ? "daily" : "weekly",
    priority: path === "" ? 1 : path === "/company" ? 0.9 : 0.8
  }));
}
