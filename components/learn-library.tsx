"use client";

import { useMemo, useState } from "react";

export type LearnItem = {
  term: string;
  category: string;
  definition: string;
  why: string;
  how: string;
  watch: string;
  sourceUrl?: string;
};

export default function LearnLibrary({ items }: { items: LearnItem[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");

  const categories = useMemo(
    () => Array.from(new Set(items.map((item) => item.category))).sort(),
    [items]
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((item) => {
      const matchesCategory = !category || item.category === category;
      const matchesQuery =
        !q ||
        item.term.toLowerCase().includes(q) ||
        item.definition.toLowerCase().includes(q) ||
        item.why.toLowerCase().includes(q);
      return matchesCategory && matchesQuery;
    });
  }, [items, query, category]);

  return (
    <section className="learn-workspace">
      <div className="learn-controls">
        <label>
          <span>Search concepts</span>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Revenue, 10-K, CPI, SOFR..." />
        </label>
        <label>
          <span>Category</span>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {categories.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
      </div>

      <div className="learn-grid">
        {filtered.map((item) => (
          <details className="learn-card" key={item.term}>
            <summary>
              <span>
                <small>{item.category}</small>
                <strong>{item.term}</strong>
              </span>
              <b>+</b>
            </summary>
            <div className="learn-card-body">
              <section><h3>What it is</h3><p>{item.definition}</p></section>
              <section><h3>Why it matters</h3><p>{item.why}</p></section>
              <section><h3>How to use it</h3><p>{item.how}</p></section>
              <section><h3>Watch for</h3><p>{item.watch}</p></section>
              {item.sourceUrl && <a href={item.sourceUrl} target="_blank" rel="noreferrer">Open primary source ↗</a>}
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}
