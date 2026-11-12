export type MarketPoint = {
  time: number;
  close: number;
};

export type MarketSnapshot = {
  symbol: string;
  price: number | null;
  previousClose: number | null;
  change: number | null;
  changePercent: number | null;
  currency: string | null;
  exchange: string | null;
  sessionDate: string | null;
  retrievedAt: string;
  history: MarketPoint[];
};

function num(value: unknown) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export async function getMarketSnapshot(symbolInput: string): Promise<MarketSnapshot | null> {
  const symbol = symbolInput.toUpperCase().trim();
  if (!/^[A-Z0-9.^=-]{1,15}$/.test(symbol)) return null;

  const url =
    `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}` +
    "?range=6mo&interval=1d&includePrePost=false&events=div%2Csplits";

  try {
    const response = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 EquityLens/1.0"
      },
      next: { revalidate: 300 }
    });

    if (!response.ok) return null;

    const payload = await response.json();
    const result = payload?.chart?.result?.[0];
    if (!result) return null;

    const meta = result.meta || {};
    const timestamps: number[] = Array.isArray(result.timestamp) ? result.timestamp : [];
    const closes: Array<number | null> =
      result?.indicators?.quote?.[0]?.close || [];

    const history = timestamps
      .map((time, index) => ({
        time,
        close: num(closes[index])
      }))
      .filter((point): point is MarketPoint => point.close !== null);

    const price =
      num(meta.regularMarketPrice) ??
      (history.length ? history[history.length - 1].close : null);

    const previousClose =
      num(meta.chartPreviousClose) ??
      num(meta.previousClose) ??
      (history.length > 1 ? history[history.length - 2].close : null);

    const change =
      price !== null && previousClose !== null ? price - previousClose : null;
    const changePercent =
      change !== null && previousClose ? (change / previousClose) * 100 : null;

    const marketTime = num(meta.regularMarketTime);
    const sessionDate = marketTime
      ? new Date(marketTime * 1000).toISOString().slice(0, 10)
      : history.length
        ? new Date(history[history.length - 1].time * 1000).toISOString().slice(0, 10)
        : null;

    return {
      symbol,
      price,
      previousClose,
      change,
      changePercent,
      currency: meta.currency || null,
      exchange: meta.exchangeName || meta.fullExchangeName || null,
      sessionDate,
      retrievedAt: new Date().toISOString(),
      history
    };
  } catch {
    return null;
  }
}
