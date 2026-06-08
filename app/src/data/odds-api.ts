const API_KEY = import.meta.env.VITE_ODDS_API_KEY;
const SPORT = "soccer_fifa_world_cup_winner";

export interface LiveOdds {
  team: string;
  american: number;
  implied: number;
  bookmaker: string;
}

const NAME_MAP: Record<string, string> = {
  "Czech Republic": "Czechia",
  "Bosnia & Herzegovina": "Bosnia",
  "Curaçao": "Curacao",
};

export async function fetchLiveOdds(): Promise<Record<string, LiveOdds>> {
  const url = `https://api.the-odds-api.com/v4/sports/${SPORT}/odds?apiKey=${API_KEY}&regions=us&markets=outrights&oddsFormat=american`;

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Odds API returned ${res.status}`);

  const data = await res.json();
  const result: Record<string, LiveOdds> = {};

  const event = data[0];
  if (!event?.bookmakers?.length) return result;

  // Average odds across bookmakers for each team
  const teamOdds: Record<string, number[]> = {};
  let bestBookmaker = event.bookmakers[0].title;

  for (const bk of event.bookmakers) {
    for (const outcome of bk.markets[0].outcomes) {
      const name = NAME_MAP[outcome.name] || outcome.name;
      if (!teamOdds[name]) teamOdds[name] = [];
      teamOdds[name].push(outcome.price);
    }
  }

  for (const [name, prices] of Object.entries(teamOdds)) {
    const avg = Math.round(prices.reduce((a, b) => a + b, 0) / prices.length);
    result[name] = {
      team: name,
      american: avg,
      implied: 100 / (avg + 100),
      bookmaker: bestBookmaker,
    };
  }

  return result;
}
