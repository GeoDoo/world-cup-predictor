import type { TournamentResult } from "./engine";
import { simulateTournament } from "./engine";

export interface MCProgressMessage {
  type: "progress";
  completed: number;
  total: number;
  winCounts: Record<string, number>;
  finalCounts: Record<string, number>;
  semiCounts: Record<string, number>;
  qfCounts: Record<string, number>;
  bestBracket: TournamentResult;
}

export interface MCDoneMessage {
  type: "done";
  completed: number;
  total: number;
  winCounts: Record<string, number>;
  finalCounts: Record<string, number>;
  semiCounts: Record<string, number>;
  qfCounts: Record<string, number>;
  bestBracket: TournamentResult;
}

export type MCWorkerMessage = MCProgressMessage | MCDoneMessage;

const BATCH_SIZE = 200;

self.onmessage = (e: MessageEvent<{ nSimulations: number }>) => {
  const { nSimulations } = e.data;

  const winCounts: Record<string, number> = {};
  const finalCounts: Record<string, number> = {};
  const semiCounts: Record<string, number> = {};
  const qfCounts: Record<string, number> = {};

  let bestBracket: TournamentResult | null = null;
  let bestScore = -1;
  let completed = 0;

  function runBatch() {
    const batchEnd = Math.min(completed + BATCH_SIZE, nSimulations);

    for (let i = completed; i < batchEnd; i++) {
      const result = simulateTournament();
      let score = 0;

      for (const match of result.knockoutRounds[0]) score += match.probability;
      for (const match of result.knockoutRounds[1]) score += match.probability;

      for (const match of result.knockoutRounds[2]) {
        qfCounts[match.winner.name] = (qfCounts[match.winner.name] || 0) + 1;
        score += match.probability;
      }

      for (const match of result.knockoutRounds[3]) {
        semiCounts[match.winner.name] = (semiCounts[match.winner.name] || 0) + 1;
        score += match.probability;
      }

      const finalMatch = result.knockoutRounds[4][0];
      finalCounts[finalMatch.teamA.name] = (finalCounts[finalMatch.teamA.name] || 0) + 1;
      finalCounts[finalMatch.teamB.name] = (finalCounts[finalMatch.teamB.name] || 0) + 1;
      winCounts[result.champion.name] = (winCounts[result.champion.name] || 0) + 1;
      score += finalMatch.probability;

      if (score > bestScore) {
        bestScore = score;
        bestBracket = result;
      }
    }

    completed = batchEnd;

    const msg: MCWorkerMessage = {
      type: completed >= nSimulations ? "done" : "progress",
      completed,
      total: nSimulations,
      winCounts: { ...winCounts },
      finalCounts: { ...finalCounts },
      semiCounts: { ...semiCounts },
      qfCounts: { ...qfCounts },
      bestBracket: bestBracket!,
    };

    self.postMessage(msg);

    if (completed < nSimulations) {
      setTimeout(runBatch, 0);
    }
  }

  runBatch();
};
