import type { TraitKey } from '@/data/traits';
import type { Avatar } from '@/data/avatars';
import type { WeeklyPlan } from '@/data/progression';

// Constants
const EPS = 1e-9; // Epsilon for safe division
export const XP_EASY = 10;
export const XP_MED = 20;
export const XP_HARD = 30;
export const XP_FULL_POTENTIAL = 1000;

// XP calculation for task difficulty
export function xpFor(difficulty: 'easy' | 'medium' | 'hard'): number {
  switch (difficulty) {
    case 'easy': return XP_EASY;
    case 'medium': return XP_MED;
    case 'hard': return XP_HARD;
  }
}

// Progress percentage from XP (0-100)
export function progressFromXp(xp: number): number {
  return Math.min(100, Math.round((xp / XP_FULL_POTENTIAL) * 100));
}

/**
 * Compute normalized trait scores from quiz answers
 * @param quizAnswers Quiz responses (questionId -> 1-5 Likert)
 * @param traits All available traits
 * @returns Normalized trait scores (0-1) with epsilon safety
 */
function computeTraitScores(
  quizAnswers: Record<string, number>,
  traits: TraitKey[]
): Record<TraitKey, number> {
  const scores: Record<TraitKey, number> = {} as Record<TraitKey, number>;

  // Initialize all traits to 0
  traits.forEach(trait => {
    scores[trait] = 0;
  });

  // Map quiz answers to trait scores (simplified - in production would use question metadata)
  Object.entries(quizAnswers).forEach(([questionId, value]) => {
    const questionIndex = parseInt(questionId.replace('q', '')) - 1;
    if (questionIndex < traits.length) {
      const trait = traits[questionIndex % traits.length];
      scores[trait] += (value - 3) / 2; // Convert 1-5 to -1 to +1
    }
  });

  return scores;
}

/**
 * Normalize scores to 0-1 range with epsilon safety
 * @param scores Raw scores
 * @returns Normalized scores
 */
function normalizeScores(scores: Record<TraitKey, number>): Record<TraitKey, number> {
  const values = Object.values(scores);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min + EPS; // Add epsilon to prevent division by zero

  const normalized: Record<TraitKey, number> = {} as Record<TraitKey, number>;
  Object.keys(scores).forEach(trait => {
    normalized[trait as TraitKey] = (scores[trait as TraitKey] - min) / range;
  });

  return normalized;
}

/**
 * Apply selection bonus to trait scores
 * @param normalizedScores Normalized trait scores (0-1)
 * @param selectedTraits User-selected traits
 * @returns Scores with selection bonus applied
 */
function applySelectionBonus(
  normalizedScores: Record<TraitKey, number>,
  selectedTraits: TraitKey[]
): Record<TraitKey, number> {
  const bonusScores = { ...normalizedScores };
  selectedTraits.forEach(trait => {
    bonusScores[trait] = (bonusScores[trait] || 0) + 1.5; // +1.5 weight for selected traits
  });
  return bonusScores;
}

/**
 * Calculate avatar match scores
 * @param traitScores Trait scores with bonuses
 * @param avatars Available avatars
 * @returns Array of avatar contributions with scores
 */
function calculateAvatarScores(
  traitScores: Record<TraitKey, number>,
  avatars: Avatar[]
): Array<{
  avatarId: string;
  perTrait: Record<TraitKey, number>;
  finalScore: number;
  overlapCount: number;
  highestContribution: number;
}> {
  return avatars.map(avatar => {
    const perTrait: Record<TraitKey, number> = {} as Record<TraitKey, number>;
    let finalScore = 0;
    let overlapCount = 0;
    let highestContribution = 0;

    // Calculate contributions from each trait
    Object.keys(traitScores).forEach(trait => {
      const traitKey = trait as TraitKey;
      let contribution = 0;

      if (avatar.primaryTraits.includes(traitKey)) {
        contribution = traitScores[traitKey] * 2; // 2x weight for primary
        overlapCount++;
      } else if (avatar.secondaryTraits.includes(traitKey)) {
        contribution = traitScores[traitKey] * 1; // 1x weight for secondary
        overlapCount++;
      }

      perTrait[traitKey] = contribution;
      finalScore += contribution;
      highestContribution = Math.max(highestContribution, contribution);
    });

    return {
      avatarId: avatar.id,
      perTrait,
      finalScore,
      overlapCount,
      highestContribution,
    };
  });
}

/**
 * Apply tie-breaking cascade to find winner
 * @param avatarScores Avatar scores with metadata
 * @returns Winning avatar ID and trace of tie-breaking decisions
 */
function applyTieBreaking(
  avatarScores: Array<{
    avatarId: string;
    finalScore: number;
    overlapCount: number;
    highestContribution: number;
  }>
): { winnerId: string; tieBreakTrace: string[] } {
  const tieBreakTrace: string[] = [];
  let candidates = [...avatarScores];

  // Sort by score (descending)
  candidates.sort((a, b) => b.finalScore - a.finalScore);
  const topScore = candidates[0].finalScore;
  candidates = candidates.filter(c => Math.abs(c.finalScore - topScore) < 0.001);

  if (candidates.length > 1) {
    tieBreakTrace.push('score');

    // Tie on score, check overlap count
    const maxOverlap = Math.max(...candidates.map(c => c.overlapCount));
    candidates = candidates.filter(c => c.overlapCount === maxOverlap);

    if (candidates.length > 1) {
      tieBreakTrace.push('overlap');

      // Tie on overlap, check highest contribution
      const maxContrib = Math.max(...candidates.map(c => c.highestContribution));
      candidates = candidates.filter(c => Math.abs(c.highestContribution - maxContrib) < 0.001);

      if (candidates.length > 1) {
        tieBreakTrace.push('highestTrait');

        // Final tie-breaker: lexicographic ID
        candidates.sort((a, b) => a.avatarId.localeCompare(b.avatarId));
        tieBreakTrace.push('lex');
      }
    }
  }

  return {
    winnerId: candidates[0].avatarId,
    tieBreakTrace: tieBreakTrace.length > 0 ? tieBreakTrace : ['score'],
  };
}

/**
 * Deterministic avatar matching algorithm
 * @param selectedTraits User-selected traits (max 3)
 * @param quizAnswers Quiz responses (questionId -> 1-5 Likert)
 * @param avatars Available avatar archetypes
 * @returns Matched avatar ID
 */
export function computeAvatarMatch(
  selectedTraits: TraitKey[],
  quizAnswers: Record<string, number>,
  avatars: Avatar[]
): string {
  const allTraits: TraitKey[] = [
    'mindfulness', 'discipline', 'productivity', 'focus', 'self-awareness',
    'confidence', 'resilience', 'creativity', 'learning', 'wellbeing'
  ];

  const rawScores = computeTraitScores(quizAnswers, allTraits);
  const normalizedScores = normalizeScores(rawScores);
  const withBonus = applySelectionBonus(normalizedScores, selectedTraits);
  const avatarScores = calculateAvatarScores(withBonus, avatars);
  const { winnerId } = applyTieBreaking(avatarScores);

  return winnerId;
}

/**
 * Explain avatar matching decision with full trace
 * @param selectedTraits User-selected traits
 * @param quizAnswers Quiz responses
 * @param avatars Available avatars
 * @returns Detailed explanation of matching decision
 */
export function explainMatch(input: {
  selectedTraits: TraitKey[];
  quizAnswers: Record<string, number>;
  avatars: Avatar[];
}): {
  traitScoresRaw: Record<TraitKey, number>;
  traitScoresNorm: Record<TraitKey, number>;
  selectedBonuses: Record<TraitKey, number>;
  avatarContribs: Array<{
    avatarId: string;
    perTrait: Record<TraitKey, number>;
    finalScore: number;
  }>;
  tieBreakTrace: string[];
  winnerId: string;
} {
  const allTraits: TraitKey[] = [
    'mindfulness', 'discipline', 'productivity', 'focus', 'self-awareness',
    'confidence', 'resilience', 'creativity', 'learning', 'wellbeing'
  ];

  const traitScoresRaw = computeTraitScores(input.quizAnswers, allTraits);
  const traitScoresNorm = normalizeScores(traitScoresRaw);
  const withBonus = applySelectionBonus(traitScoresNorm, input.selectedTraits);

  // Calculate selected bonuses
  const selectedBonuses: Record<TraitKey, number> = {} as Record<TraitKey, number>;
  input.selectedTraits.forEach(trait => {
    selectedBonuses[trait] = 1.5;
  });

  const avatarScores = calculateAvatarScores(withBonus, input.avatars);
  const { winnerId, tieBreakTrace } = applyTieBreaking(avatarScores);

  return {
    traitScoresRaw,
    traitScoresNorm,
    selectedBonuses,
    avatarContribs: avatarScores.map(({ avatarId, perTrait, finalScore }) => ({
      avatarId,
      perTrait,
      finalScore,
    })),
    tieBreakTrace,
    winnerId,
  };
}

/**
 * Check if user should be gated for missing yesterday's tasks
 * @param lastCompletionLocalISO Last task completion in local ISO format
 * @param stakes Stakes configuration with enabled flag
 * @param nowLocalISO Current time in local ISO format
 * @param weeklyGraceUsed Whether weekly grace has been used
 * @param dailyChargeUsed Whether today's charge has been used
 * @returns True if user should be charged/gated
 */
export function shouldGateForMiss(
  lastCompletionLocalISO: string | undefined,
  stakes: { enabled: boolean },
  nowLocalISO: string,
  weeklyGraceUsed: boolean,
  dailyChargeUsed: boolean
): boolean {
  // No gating if stakes not enabled
  if (!stakes.enabled) return false;

  // No gating if weekly grace already used
  if (weeklyGraceUsed) return false;

  // No gating if already charged today
  if (dailyChargeUsed) return false;

  // No gating if no previous completion (first day)
  if (!lastCompletionLocalISO) return false;

  // Parse dates
  const lastDate = new Date(lastCompletionLocalISO);
  const nowDate = new Date(nowLocalISO);

  // Apply 4-hour grace period (00:00-03:59 counts as previous day)
  const graceHours = 4;
  const lastDateAdjusted = new Date(lastDate);
  if (lastDate.getHours() < graceHours) {
    lastDateAdjusted.setDate(lastDateAdjusted.getDate() - 1);
  }

  const nowDateAdjusted = new Date(nowDate);
  if (nowDate.getHours() < graceHours) {
    nowDateAdjusted.setDate(nowDateAdjusted.getDate() - 1);
  }

  // Get day strings for comparison
  const lastDayStr = lastDateAdjusted.toISOString().split('T')[0];
  const nowDayStr = nowDateAdjusted.toISOString().split('T')[0];

  // Calculate days difference
  const daysDiff = Math.floor(
    (nowDateAdjusted.getTime() - lastDateAdjusted.getTime()) / (1000 * 60 * 60 * 24)
  );

  // Gate if yesterday had zero completions (more than 1 day gap)
  return daysDiff > 1;
}

// Level calculation from XP
export function levelFromXP(totalXP: number): {
  level: number;
  currentLevelXP: number;
  nextLevelXP: number;
  progress: number;
} {
  let level = 1;
  let xpForNextLevel = 100;
  let remainingXP = totalXP;
  let currentLevelStart = 0;

  while (remainingXP >= xpForNextLevel) {
    currentLevelStart += xpForNextLevel;
    remainingXP -= xpForNextLevel;
    level++;
    xpForNextLevel = Math.floor(100 * Math.pow(1.2, level - 1));
  }

  const progress = (remainingXP / xpForNextLevel) * 100;

  return {
    level,
    currentLevelXP: remainingXP,
    nextLevelXP: xpForNextLevel,
    progress,
  };
}

// Streak calculation with local time and grace period
export function calculateStreak(
  lastActiveLocalISO: string | undefined,
  currentStreak: number,
  nowLocalISO: string
): { newStreak: number; maintained: boolean } {
  if (!lastActiveLocalISO) {
    return { newStreak: 1, maintained: true };
  }

  const lastDate = new Date(lastActiveLocalISO);
  const nowDate = new Date(nowLocalISO);

  // Apply 4-hour grace period
  const graceHours = 4;
  const lastDateAdjusted = new Date(lastDate);
  if (lastDate.getHours() < graceHours) {
    lastDateAdjusted.setDate(lastDateAdjusted.getDate() - 1);
  }

  const nowDateAdjusted = new Date(nowDate);
  if (nowDate.getHours() < graceHours) {
    nowDateAdjusted.setDate(nowDateAdjusted.getDate() - 1);
  }

  const lastDayStr = lastDateAdjusted.toISOString().split('T')[0];
  const nowDayStr = nowDateAdjusted.toISOString().split('T')[0];

  if (lastDayStr === nowDayStr) {
    // Same day - streak maintained
    return { newStreak: currentStreak, maintained: true };
  }

  const daysDiff = Math.floor(
    (nowDateAdjusted.getTime() - lastDateAdjusted.getTime()) / (1000 * 60 * 60 * 24)
  );

  if (daysDiff === 1) {
    // Next day - streak increases
    return { newStreak: currentStreak + 1, maintained: true };
  } else {
    // Streak broken
    return { newStreak: 1, maintained: false };
  }
}

// Achievement conditions
export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  condition: (state: any) => boolean;
}

export const ACHIEVEMENTS: Achievement[] = [
  {
    id: 'first-task',
    name: 'First Step',
    description: 'Complete your first task',
    icon: '👣',
    condition: (state) => state.completedTasks.length >= 1,
  },
  {
    id: 'week-warrior',
    name: 'Week Warrior',
    description: 'Complete all tasks in a week',
    icon: '⚔️',
    condition: (state) => false, // Would need week completion tracking
  },
  {
    id: 'streak-7',
    name: 'Consistent',
    description: '7-day streak',
    icon: '🔥',
    condition: (state) => state.streakDays >= 7,
  },
  {
    id: 'streak-30',
    name: 'Unstoppable',
    description: '30-day streak',
    icon: '💪',
    condition: (state) => state.streakDays >= 30,
  },
  {
    id: 'level-5',
    name: 'Rising Star',
    description: 'Reach level 5',
    icon: '⭐',
    condition: (state) => state.level >= 5,
  },
  {
    id: 'level-10',
    name: 'Master',
    description: 'Reach level 10',
    icon: '👑',
    condition: (state) => state.level >= 10,
  },
  {
    id: 'xp-1000',
    name: 'Full Potential',
    description: 'Reach 1000 XP',
    icon: '⚡',
    condition: (state) => state.totalXP >= XP_FULL_POTENTIAL,
  },
];

// Check for new achievements
export function checkAchievements(
  gameState: any,
  currentAchievements: string[]
): string[] {
  const newAchievements: string[] = [];

  ACHIEVEMENTS.forEach((achievement) => {
    if (
      !currentAchievements.includes(achievement.id) &&
      achievement.condition(gameState)
    ) {
      newAchievements.push(achievement.id);
    }
  });

  return newAchievements;
}

/**
 * Self-test function for development builds
 * Validates determinism and monotonic XP mapping
 * @returns True if all tests pass
 */
export function __selfTest(): boolean {
  try {
    // Test 1: Determinism check
    const testTraits: TraitKey[] = ['mindfulness', 'discipline'];
    const testAnswers = { q1: 4, q2: 3, q3: 5, q4: 2, q5: 4, q6: 3, q7: 5, q8: 2, q9: 4, q10: 3 };
    const testAvatars: Avatar[] = [
      {
        id: 'scholar',
        name: 'The Scholar',
        description: 'Knowledge seeker',
        primaryTraits: ['learning', 'focus'],
        secondaryTraits: ['discipline', 'productivity'],
        stats: { discipline: 7, focus: 9, growth: 8 },
      },
      {
        id: 'warrior',
        name: 'The Warrior',
        description: 'Disciplined fighter',
        primaryTraits: ['discipline', 'resilience'],
        secondaryTraits: ['confidence', 'focus'],
        stats: { discipline: 10, focus: 7, growth: 6 },
      },
    ];

    // Run 5 times, should get same result
    const results = new Set<string>();
    for (let i = 0; i < 5; i++) {
      results.add(computeAvatarMatch(testTraits, testAnswers, testAvatars));
    }
    if (results.size !== 1) return false;

    // Test 2: XP to progress is monotonic
    for (let xp = 0; xp <= XP_FULL_POTENTIAL; xp += 100) {
      const progress1 = progressFromXp(xp);
      const progress2 = progressFromXp(xp + 50);
      if (progress2 < progress1) return false;
    }

    // Test 3: Progress caps at 100
    if (progressFromXp(XP_FULL_POTENTIAL + 100) !== 100) return false;

    return true;
  } catch {
    return false;
  }
}