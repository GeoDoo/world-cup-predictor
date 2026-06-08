export interface Team {
  name: string;
  iso: string;
  points: number;
  ranking: number;
  confederation: string;
}

export interface MatchResult {
  teamA: Team;
  teamB: Team;
  winner: Team;
  probability: number;
}

export interface GroupStanding {
  team: Team;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalsFor: number;
  goalsAgainst: number;
  points: number;
  goalDifference: number;
}

export const TEAMS: Record<string, Team> = {
  "France": { name: "France", iso: "fr", points: 1877.32, ranking: 1, confederation: "UEFA" },
  "Spain": { name: "Spain", iso: "es", points: 1876.40, ranking: 2, confederation: "UEFA" },
  "Argentina": { name: "Argentina", iso: "ar", points: 1874.81, ranking: 3, confederation: "CONMEBOL" },
  "England": { name: "England", iso: "gb-eng", points: 1825.97, ranking: 4, confederation: "UEFA" },
  "Portugal": { name: "Portugal", iso: "pt", points: 1763.83, ranking: 5, confederation: "UEFA" },
  "Brazil": { name: "Brazil", iso: "br", points: 1761.16, ranking: 6, confederation: "CONMEBOL" },
  "Netherlands": { name: "Netherlands", iso: "nl", points: 1757.87, ranking: 7, confederation: "UEFA" },
  "Morocco": { name: "Morocco", iso: "ma", points: 1755.87, ranking: 8, confederation: "CAF" },
  "Belgium": { name: "Belgium", iso: "be", points: 1734.71, ranking: 9, confederation: "UEFA" },
  "Germany": { name: "Germany", iso: "de", points: 1730.37, ranking: 10, confederation: "UEFA" },
  "Croatia": { name: "Croatia", iso: "hr", points: 1717.07, ranking: 11, confederation: "UEFA" },
  "Colombia": { name: "Colombia", iso: "co", points: 1693.09, ranking: 13, confederation: "CONMEBOL" },
  "Senegal": { name: "Senegal", iso: "sn", points: 1688.99, ranking: 14, confederation: "CAF" },
  "Mexico": { name: "Mexico", iso: "mx", points: 1681.03, ranking: 15, confederation: "CONCACAF" },
  "USA": { name: "USA", iso: "us", points: 1673.13, ranking: 16, confederation: "CONCACAF" },
  "Uruguay": { name: "Uruguay", iso: "uy", points: 1673.07, ranking: 17, confederation: "CONMEBOL" },
  "Japan": { name: "Japan", iso: "jp", points: 1660.43, ranking: 18, confederation: "AFC" },
  "Switzerland": { name: "Switzerland", iso: "ch", points: 1649.40, ranking: 19, confederation: "UEFA" },
  "Iran": { name: "Iran", iso: "ir", points: 1615.30, ranking: 21, confederation: "AFC" },
  "Turkey": { name: "Turkey", iso: "tr", points: 1599.04, ranking: 22, confederation: "UEFA" },
  "Ecuador": { name: "Ecuador", iso: "ec", points: 1594.78, ranking: 23, confederation: "CONMEBOL" },
  "Austria": { name: "Austria", iso: "at", points: 1593.45, ranking: 24, confederation: "UEFA" },
  "South Korea": { name: "South Korea", iso: "kr", points: 1588.66, ranking: 25, confederation: "AFC" },
  "Australia": { name: "Australia", iso: "au", points: 1580.67, ranking: 27, confederation: "AFC" },
  "Algeria": { name: "Algeria", iso: "dz", points: 1564.26, ranking: 28, confederation: "CAF" },
  "Egypt": { name: "Egypt", iso: "eg", points: 1563.24, ranking: 29, confederation: "CAF" },
  "Canada": { name: "Canada", iso: "ca", points: 1556.48, ranking: 30, confederation: "CONCACAF" },
  "Norway": { name: "Norway", iso: "no", points: 1550.94, ranking: 31, confederation: "UEFA" },
  "Panama": { name: "Panama", iso: "pa", points: 1540.64, ranking: 33, confederation: "CONCACAF" },
  "Ivory Coast": { name: "Ivory Coast", iso: "ci", points: 1532.98, ranking: 34, confederation: "CAF" },
  "Sweden": { name: "Sweden", iso: "se", points: 1514.77, ranking: 38, confederation: "UEFA" },
  "Paraguay": { name: "Paraguay", iso: "py", points: 1503.50, ranking: 40, confederation: "CONMEBOL" },
  "Czechia": { name: "Czechia", iso: "cz", points: 1501.38, ranking: 41, confederation: "UEFA" },
  "Scotland": { name: "Scotland", iso: "gb-sct", points: 1498.35, ranking: 43, confederation: "UEFA" },
  "Tunisia": { name: "Tunisia", iso: "tn", points: 1479.04, ranking: 44, confederation: "CAF" },
  "DR Congo": { name: "DR Congo", iso: "cd", points: 1478.35, ranking: 46, confederation: "CAF" },
  "Uzbekistan": { name: "Uzbekistan", iso: "uz", points: 1465.34, ranking: 50, confederation: "AFC" },
  "Qatar": { name: "Qatar", iso: "qa", points: 1454.96, ranking: 55, confederation: "AFC" },
  "Iraq": { name: "Iraq", iso: "iq", points: 1447.14, ranking: 57, confederation: "AFC" },
  "South Africa": { name: "South Africa", iso: "za", points: 1429.73, ranking: 60, confederation: "CAF" },
  "Saudi Arabia": { name: "Saudi Arabia", iso: "sa", points: 1421.43, ranking: 61, confederation: "AFC" },
  "Jordan": { name: "Jordan", iso: "jo", points: 1391.45, ranking: 63, confederation: "AFC" },
  "Bosnia": { name: "Bosnia", iso: "ba", points: 1385.84, ranking: 65, confederation: "UEFA" },
  "Cape Verde": { name: "Cape Verde", iso: "cv", points: 1366.13, ranking: 69, confederation: "CAF" },
  "Ghana": { name: "Ghana", iso: "gh", points: 1346.31, ranking: 74, confederation: "CAF" },
  "Curacao": { name: "Curacao", iso: "cw", points: 1294.65, ranking: 82, confederation: "CONCACAF" },
  "Haiti": { name: "Haiti", iso: "ht", points: 1291.71, ranking: 83, confederation: "CONCACAF" },
  "New Zealand": { name: "New Zealand", iso: "nz", points: 1281.57, ranking: 85, confederation: "OFC" },
};

export const GROUPS: Record<string, string[]> = {
  A: ["Mexico", "South Africa", "South Korea", "Czechia"],
  B: ["Canada", "Bosnia", "Qatar", "Switzerland"],
  C: ["Brazil", "Morocco", "Haiti", "Scotland"],
  D: ["USA", "Paraguay", "Australia", "Turkey"],
  E: ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
  F: ["Netherlands", "Japan", "Sweden", "Tunisia"],
  G: ["Belgium", "Egypt", "Iran", "New Zealand"],
  H: ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
  I: ["France", "Senegal", "Iraq", "Norway"],
  J: ["Argentina", "Algeria", "Austria", "Jordan"],
  K: ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
  L: ["England", "Croatia", "Ghana", "Panama"],
};

export const R32_BRACKET = {
  left: [
    { id: "M73", slotA: "2A", slotB: "2B" },
    { id: "M74", slotA: "1E", slotB: "3ABCDF" },
    { id: "M75", slotA: "1F", slotB: "2C" },
    { id: "M76", slotA: "1C", slotB: "2F" },
    { id: "M77", slotA: "1I", slotB: "3CDFGH" },
    { id: "M78", slotA: "2E", slotB: "2I" },
    { id: "M79", slotA: "1A", slotB: "3CEFHI" },
    { id: "M80", slotA: "1D", slotB: "3EHIJK" },
  ],
  right: [
    { id: "M81", slotA: "2D", slotB: "2L" },
    { id: "M82", slotA: "1G", slotB: "3ABEFJ" },
    { id: "M83", slotA: "1H", slotB: "2J" },
    { id: "M84", slotA: "1J", slotB: "2H" },
    { id: "M85", slotA: "1K", slotB: "3BEFIJ" },
    { id: "M86", slotA: "2G", slotB: "2K" },
    { id: "M87", slotA: "1L", slotB: "3DGHKL" },
    { id: "M88", slotA: "1B", slotB: "3DGHKL" },
  ],
};

export const R16_MATCHES = [
  { id: "M89", srcA: "M74", srcB: "M77" },
  { id: "M90", srcA: "M73", srcB: "M75" },
  { id: "M91", srcA: "M76", srcB: "M78" },
  { id: "M92", srcA: "M79", srcB: "M80" },
  { id: "M93", srcA: "M82", srcB: "M83" },
  { id: "M94", srcA: "M81", srcB: "M84" },
  { id: "M95", srcA: "M85", srcB: "M86" },
  { id: "M96", srcA: "M87", srcB: "M88" },
];

export const QF_MATCHES = [
  { id: "M97", srcA: "M89", srcB: "M90" },
  { id: "M98", srcA: "M91", srcB: "M92" },
  { id: "M99", srcA: "M93", srcB: "M94" },
  { id: "M100", srcA: "M95", srcB: "M96" },
];

export const SF_MATCHES = [
  { id: "M101", srcA: "M97", srcB: "M98" },
  { id: "M102", srcA: "M99", srcB: "M100" },
];

export const FINAL_MATCH = { id: "M103", srcA: "M101", srcB: "M102" };

export function getFlagUrl(iso: string): string {
  return `https://flagcdn.com/w80/${iso}.png`;
}
