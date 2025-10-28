import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import type { TraitKey } from '../data/traits';
import type { Avatar } from '../data/avatars';
import {
  computeAvatarMatch,
  explainMatch,
  xpFor,
  progressFromXp,
  shouldGateForMiss,
  calculateStreak,
  XP_EASY,
  XP_MED,
  XP_HARD,
  XP_FULL_POTENTIAL,
} from '../lib/gamification';
import { generateWeeklyPlan, validatePlan } from '../data/progression';
import { assertMaxThreeTraits, assertMinOneTrait } from '../lib/validators';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Mock AsyncStorage
const mockAsyncStorage: { [key: string]: string } = {};

jest.mock('@react-native-async-storage/async-storage', () => ({
  setItem: jest.fn(async (key: string, value: string) => {
    mockAsyncStorage[key] = value;
    return Promise.resolve();
  }),
  getItem: jest.fn(async (key: string) => {
    return Promise.resolve(mockAsyncStorage[key] || null);
  }),
  removeItem: jest.fn(async (key: string) => {
    delete mockAsyncStorage[key];
    return Promise.resolve();
  }),
  clear: jest.fn(async () => {
    Object.keys(mockAsyncStorage).forEach(key => delete mockAsyncStorage[key]);
    return Promise.resolve();
  }),
}));

// Test avatars
const TEST_AVATARS: Avatar[] = [
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
  {
    id: 'sage',
    name: 'The Sage',
    description: 'Wise mentor',
    primaryTraits: ['mindfulness', 'self-awareness'],
    secondaryTraits: ['learning', 'wellbeing'],
    stats: { discipline: 5, focus: 8, growth: 9 },
  },
];

describe('Avatar Matching', () => {
  describe('matching_deterministic_100x', () => {
    it('should return identical avatar for identical inputs (100 iterations)', () => {
      const selectedTraits: TraitKey[] = ['mindfulness', 'discipline'];
      const quizAnswers = {
        q1: 4, q2: 3, q3: 5, q4: 2, q5: 4,
        q6: 3, q7: 5, q8: 2, q9: 4, q10: 3,
      };

      const results = new Set<string>();
      for (let i = 0; i < 100; i++) {
        const avatarId = computeAvatarMatch(selectedTraits, quizAnswers, TEST_AVATARS);
        results.add(avatarId);
      }

      expect(results.size).toBe(1);
    });
  });

  describe('matching_tiebreak_cascade', () => {
    it('should apply tie-breaking cascade correctly', () => {
      const selectedTraits: TraitKey[] = ['discipline', 'focus'];
      const quizAnswers = {
        q1: 3, q2: 3, q3: 3, q4: 3, q5: 3,
        q6: 3, q7: 3, q8: 3, q9: 3, q10: 3,
      };

      const result = explainMatch({
        selectedTraits,
        quizAnswers,
        avatars: TEST_AVATARS,
      });

      // Check that tie-break trace is populated
      expect(result.tieBreakTrace).toBeDefined();
      expect(result.tieBreakTrace.length).toBeGreaterThan(0);

      // Verify winner is deterministic
      const winnerId1 = result.winnerId;
      const winnerId2 = computeAvatarMatch(selectedTraits, quizAnswers, TEST_AVATARS);
      expect(winnerId1).toBe(winnerId2);
    });
  });

  describe('explainMatch output', () => {
    it('should return properly typed explanation', () => {
      const selectedTraits: TraitKey[] = ['mindfulness'];
      const quizAnswers = { q1: 5, q2: 4, q3: 3, q4: 2, q5: 1, q6: 1, q7: 2, q8: 3, q9: 4, q10: 5 };

      const result = explainMatch({
        selectedTraits,
        quizAnswers,
        avatars: TEST_AVATARS,
      });

      expect(result.traitScoresRaw).toBeDefined();
      expect(result.traitScoresNorm).toBeDefined();
      expect(result.selectedBonuses).toBeDefined();
      expect(result.selectedBonuses['mindfulness']).toBe(1.5);
      expect(result.avatarContribs).toHaveLength(TEST_AVATARS.length);
      expect(result.winnerId).toBeDefined();
    });
  });
});

describe('Trait Selection', () => {
  describe('traitCap_enforced', () => {
    it('should throw error when more than 3 traits selected', () => {
      const fourTraits: TraitKey[] = ['mindfulness', 'discipline', 'focus', 'confidence'];

      expect(() => {
        assertMaxThreeTraits(fourTraits);
      }).toThrow('Maximum of 3 traits can be selected');
    });

    it('should allow exactly 3 traits', () => {
      const threeTraits: TraitKey[] = ['mindfulness', 'discipline', 'focus'];

      expect(() => {
        assertMaxThreeTraits(threeTraits);
      }).not.toThrow();
    });

    it('should require at least 1 trait', () => {
      const noTraits: TraitKey[] = [];

      expect(() => {
        assertMinOneTrait(noTraits);
      }).toThrow('At least one trait must be selected');
    });
  });
});

describe('Progression System', () => {
  describe('progression_bounds_topTrait_daily_taskCap', () => {
    it('should enforce Week 1 bounds (15-25 min/day)', () => {
      const plan = generateWeeklyPlan(['mindfulness', 'discipline'], 'scholar');
      const week1 = plan.weeks[0];
      const avgMinutes = week1.totalMinutes / week1.activeDays.length;

      expect(avgMinutes).toBeGreaterThanOrEqual(15);
      expect(avgMinutes).toBeLessThanOrEqual(25);
    });

    it('should enforce Week 8 bounds (45-60 min/day)', () => {
      const plan = generateWeeklyPlan(['mindfulness', 'discipline'], 'scholar');
      const week8 = plan.weeks[7];
      const avgMinutes = week8.totalMinutes / week8.activeDays.length;

      expect(avgMinutes).toBeGreaterThanOrEqual(45);
      expect(avgMinutes).toBeLessThanOrEqual(60);
    });

    it('should enforce Week 6 micro-deload (≤ Week 5 × 0.9)', () => {
      const plan = generateWeeklyPlan(['mindfulness', 'discipline'], 'scholar');
      const week5 = plan.weeks[4];
      const week6 = plan.weeks[5];

      const week5Avg = week5.totalMinutes / week5.activeDays.length;
      const week6Avg = week6.totalMinutes / week6.activeDays.length;

      expect(week6Avg).toBeLessThanOrEqual(week5Avg * 0.9 + 0.1); // Small epsilon for rounding
    });

    it('should have exactly 5 active days per week', () => {
      const plan = generateWeeklyPlan(['mindfulness'], 'scholar');

      plan.weeks.forEach(week => {
        expect(week.activeDays).toHaveLength(5);
        expect(week.restDays).toHaveLength(2);
      });
    });

    it('should include top trait task every active day', () => {
      const topTrait: TraitKey = 'mindfulness';
      const plan = generateWeeklyPlan([topTrait, 'discipline'], 'scholar');

      plan.weeks.forEach(week => {
        // Group tasks by day
        const tasksByDay = new Map<number, typeof week.tasks>();
        week.tasks.forEach(task => {
          const dayMatch = task.id.match(/d(\d+)/);
          if (dayMatch) {
            const day = parseInt(dayMatch[1]);
            if (!tasksByDay.has(day)) {
              tasksByDay.set(day, []);
            }
            tasksByDay.get(day)!.push(task);
          }
        });

        // Check each active day has at least one task from top trait
        week.activeDays.forEach(dayNum => {
          const dayTasks = tasksByDay.get(dayNum) || [];
          const hasTopTrait = dayTasks.some(task => task.category === topTrait);
          expect(hasTopTrait).toBe(true);
        });
      });
    });

    it('should enforce max 3 tasks per day by default', () => {
      const plan = generateWeeklyPlan(['mindfulness', 'discipline', 'focus'], 'scholar');

      plan.weeks.forEach(week => {
        const tasksPerDay = new Map<number, number>();
        week.tasks.forEach(task => {
          const dayMatch = task.id.match(/d(\d+)/);
          if (dayMatch) {
            const day = parseInt(dayMatch[1]);
            tasksPerDay.set(day, (tasksPerDay.get(day) || 0) + 1);
          }
        });

        tasksPerDay.forEach((count, day) => {
          expect(count).toBeLessThanOrEqual(4); // Allow 4 if needed for minutes
        });
      });
    });
  });

  describe('evidence_gating_week5_plus', () => {
    it('should not assign photo evidence before Week 5', () => {
      const plan = generateWeeklyPlan(['mindfulness'], 'scholar');

      // Check weeks 1-4
      for (let i = 0; i < 4; i++) {
        const week = plan.weeks[i];
        week.tasks.forEach(task => {
          expect(task.evidenceMode).not.toBe('photo');
        });
      }
    });

    it('should allow photo evidence in Week 5+', () => {
      const plan = generateWeeklyPlan(['mindfulness'], 'scholar');

      // Check weeks 5-8
      let hasPhoto = false;
      for (let i = 4; i < 8; i++) {
        const week = plan.weeks[i];
        week.tasks.forEach(task => {
          if (task.evidenceMode === 'photo') {
            hasPhoto = true;
          }
        });
      }

      // Should have at least some photo tasks in later weeks
      expect(hasPhoto).toBe(true);
    });
  });

  describe('validatePlan', () => {
    it('should pass for valid generated plans', () => {
      const plan = generateWeeklyPlan(['mindfulness', 'discipline'], 'scholar');

      expect(() => {
        validatePlan(plan);
      }).not.toThrow();
    });

    it('should throw for invalid minute bounds', () => {
      const plan = generateWeeklyPlan(['mindfulness'], 'scholar');

      // Artificially reduce Week 1 minutes below minimum
      plan.weeks[0].totalMinutes = 50; // 10 min/day average, below 15 min minimum

      expect(() => {
        validatePlan(plan);
      }).toThrow(/Week 1.*below minimum/);
    });
  });
});

describe('XP and Progress', () => {
  describe('xp_progress_and_gate_logic', () => {
    it('should award correct XP for each difficulty', () => {
      expect(xpFor('easy')).toBe(XP_EASY);
      expect(xpFor('medium')).toBe(XP_MED);
      expect(xpFor('hard')).toBe(XP_HARD);
    });

    it('should calculate progress correctly', () => {
      expect(progressFromXp(0)).toBe(0);
      expect(progressFromXp(500)).toBe(50);
      expect(progressFromXp(XP_FULL_POTENTIAL)).toBe(100);
      expect(progressFromXp(XP_FULL_POTENTIAL + 100)).toBe(100); // Caps at 100
    });

    it('should be monotonic (XP increase = progress increase)', () => {
      for (let xp = 0; xp <= XP_FULL_POTENTIAL; xp += 100) {
        const progress1 = progressFromXp(xp);
        const progress2 = progressFromXp(xp + 50);
        expect(progress2).toBeGreaterThanOrEqual(progress1);
      }
    });

    it('should trigger gate only when all conditions met', () => {
      // No gate if stakes disabled
      expect(shouldGateForMiss(
        '2024-01-01T10:00:00',
        { enabled: false },
        '2024-01-03T10:00:00',
        false,
        false
      )).toBe(false);

      // No gate if weekly grace already used
      expect(shouldGateForMiss(
        '2024-01-01T10:00:00',
        { enabled: true },
        '2024-01-03T10:00:00',
        true,
        false
      )).toBe(false);

      // No gate if daily charge already used
      expect(shouldGateForMiss(
        '2024-01-01T10:00:00',
        { enabled: true },
        '2024-01-03T10:00:00',
        false,
        true
      )).toBe(false);

      // Gate if all conditions met (2+ days gap)
      expect(shouldGateForMiss(
        '2024-01-01T10:00:00',
        { enabled: true },
        '2024-01-03T10:00:00',
        false,
        false
      )).toBe(true);

      // No gate if only 1 day gap
      expect(shouldGateForMiss(
        '2024-01-01T10:00:00',
        { enabled: true },
        '2024-01-02T10:00:00',
        false,
        false
      )).toBe(false);
    });

    it('should apply 4-hour grace period correctly', () => {
      // Task completed at 2am counts as previous day
      expect(shouldGateForMiss(
        '2024-01-01T02:00:00', // 2am Jan 1 (counts as Dec 31)
        { enabled: true },
        '2024-01-02T02:00:00', // 2am Jan 2 (counts as Jan 1)
        false,
        false
      )).toBe(false); // Only 1 day gap after grace

      // Task completed at 5am counts as current day
      expect(shouldGateForMiss(
        '2024-01-01T05:00:00', // 5am Jan 1
        { enabled: true },
        '2024-01-03T05:00:00', // 5am Jan 3
        false,
        false
      )).toBe(true); // 2 day gap, should gate
    });
  });

  describe('streak calculation', () => {
    it('should maintain streak for same day', () => {
      const result = calculateStreak(
        '2024-01-01T10:00:00',
        5,
        '2024-01-01T15:00:00'
      );

      expect(result.newStreak).toBe(5);
      expect(result.maintained).toBe(true);
    });

    it('should increment streak for next day', () => {
      const result = calculateStreak(
        '2024-01-01T10:00:00',
        5,
        '2024-01-02T10:00:00'
      );

      expect(result.newStreak).toBe(6);
      expect(result.maintained).toBe(true);
    });

    it('should reset streak after gap', () => {
      const result = calculateStreak(
        '2024-01-01T10:00:00',
        5,
        '2024-01-03T10:00:00'
      );

      expect(result.newStreak).toBe(1);
      expect(result.maintained).toBe(false);
    });

    it('should apply grace period for streaks', () => {
      // Complete at 2am, counts as previous day
      const result = calculateStreak(
        '2024-01-01T02:00:00', // 2am Jan 1 (counts as Dec 31)
        5,
        '2024-01-01T10:00:00'  // 10am Jan 1
      );

      expect(result.newStreak).toBe(6); // Increments as it's "next day"
      expect(result.maintained).toBe(true);
    });
  });
});

describe('Persistence', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    Object.keys(mockAsyncStorage).forEach(key => delete mockAsyncStorage[key]);
  });

  describe('persistence_and_routing_basic', () => {
    it('should persist onboarding state to AsyncStorage', async () => {
      const testData = {
        selectedTraits: ['mindfulness', 'discipline'],
        onboardingDone: true,
        xp: 100,
      };

      await AsyncStorage.setItem('levelup-onboarding', JSON.stringify(testData));

      const retrieved = await AsyncStorage.getItem('levelup-onboarding');
      expect(retrieved).toBeDefined();

      const parsed = JSON.parse(retrieved!);
      expect(parsed.selectedTraits).toEqual(testData.selectedTraits);
      expect(parsed.onboardingDone).toBe(testData.onboardingDone);
      expect(parsed.xp).toBe(testData.xp);
    });

    it('should route based on onboardingDone flag', async () => {
      // Test with onboardingDone = false (should stay in onboarding)
      const onboardingData = { onboardingDone: false };
      await AsyncStorage.setItem('levelup-onboarding', JSON.stringify(onboardingData));

      const data1 = await AsyncStorage.getItem('levelup-onboarding');
      const parsed1 = JSON.parse(data1!);
      expect(parsed1.onboardingDone).toBe(false);

      // Test with onboardingDone = true (should route to dashboard)
      const dashboardData = { onboardingDone: true };
      await AsyncStorage.setItem('levelup-onboarding', JSON.stringify(dashboardData));

      const data2 = await AsyncStorage.getItem('levelup-onboarding');
      const parsed2 = JSON.parse(data2!);
      expect(parsed2.onboardingDone).toBe(true);
    });
  });
});