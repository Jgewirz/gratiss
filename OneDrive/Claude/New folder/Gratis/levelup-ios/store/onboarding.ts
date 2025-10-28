import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { TraitKey } from '@/data/traits';
import type { WeeklyPlan } from '@/data/progression';
import { xpFor, progressFromXp, calculateStreak, shouldGateForMiss } from '@/lib/gamification';

interface OnboardingState {
  // State
  selectedTraits: TraitKey[];
  quizAnswers: Record<string, number>; // questionId -> 1-5 Likert
  matchedAvatarId?: string;
  weeklyPlan?: WeeklyPlan;
  permissions: {
    notifications: boolean;
    health: boolean;
  };
  stakes: {
    enabled: boolean;
  };
  step: number;
  onboardingDone: boolean;

  // XP and Progress
  xp: number;
  progressPercent: number;
  completedTasks: string[];
  level: number;
  streakDays: number;

  // Streak and Grace
  lastCompletionLocalISO?: string;
  weeklyGraceUsed: boolean;
  dailyChargeUsed: boolean;

  // Actions
  setTraits: (traits: TraitKey[]) => void;
  setAnswer: (questionId: string, value: number) => void;
  matchAvatar: (avatarId: string) => void;
  buildPlan: (plan: WeeklyPlan) => void;
  setPermissions: (permissions: { notifications: boolean; health: boolean }) => void;
  setStakes: (stakes: { enabled: boolean }) => void;
  completeTask: (difficulty: 'easy' | 'medium' | 'hard', taskId: string) => void;
  markDailyChargeUsed: () => void;
  useWeeklyGrace: () => void;
  resetWeeklyGraceOnMonday: () => void;
  checkMissGate: () => boolean;
  next: () => void;
  prev: () => void;
  finishOnboarding: () => void;
  reset: () => void;
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      // Initial state
      selectedTraits: [],
      quizAnswers: {},
      matchedAvatarId: undefined,
      weeklyPlan: undefined,
      permissions: {
        notifications: true,
        health: false,
      },
      stakes: {
        enabled: false,
      },
      step: 0,
      onboardingDone: false,

      // XP and Progress
      xp: 0,
      progressPercent: 0,
      completedTasks: [],
      level: 1,
      streakDays: 0,

      // Streak and Grace
      lastCompletionLocalISO: undefined,
      weeklyGraceUsed: false,
      dailyChargeUsed: false,

      // Actions
      setTraits: (traits) => set({ selectedTraits: traits }),

      setAnswer: (questionId, value) =>
        set((state) => ({
          quizAnswers: { ...state.quizAnswers, [questionId]: value },
        })),

      matchAvatar: (avatarId) => set({ matchedAvatarId: avatarId }),

      buildPlan: (plan) => set({ weeklyPlan: plan }),

      setPermissions: (permissions) => set({ permissions }),

      setStakes: (stakes) => set({ stakes }),

      completeTask: (difficulty, taskId) => {
        const nowLocalISO = new Date().toISOString();
        const xpGained = xpFor(difficulty);

        set((state) => {
          // Calculate new XP and progress
          const newXp = state.xp + xpGained;
          const newProgress = progressFromXp(newXp);

          // Calculate streak
          const { newStreak, maintained } = calculateStreak(
            state.lastCompletionLocalISO,
            state.streakDays,
            nowLocalISO
          );

          // Calculate level (simplified - in production would use levelFromXP)
          const newLevel = Math.floor(newXp / 100) + 1;

          return {
            completedTasks: [...state.completedTasks, taskId],
            xp: newXp,
            progressPercent: newProgress,
            level: newLevel,
            streakDays: newStreak,
            lastCompletionLocalISO: nowLocalISO,
          };
        });
      },

      markDailyChargeUsed: () => set({ dailyChargeUsed: true }),

      useWeeklyGrace: () => set({ weeklyGraceUsed: true }),

      resetWeeklyGraceOnMonday: () => {
        const now = new Date();
        if (now.getDay() === 1) {
          // Monday
          set({ weeklyGraceUsed: false });
        }
      },

      checkMissGate: () => {
        const state = get();
        const nowLocalISO = new Date().toISOString();
        return shouldGateForMiss(
          state.lastCompletionLocalISO,
          state.stakes,
          nowLocalISO,
          state.weeklyGraceUsed,
          state.dailyChargeUsed
        );
      },

      next: () => set((state) => ({ step: state.step + 1 })),

      prev: () => set((state) => ({ step: Math.max(0, state.step - 1) })),

      finishOnboarding: () => set({ onboardingDone: true }),

      reset: () =>
        set({
          selectedTraits: [],
          quizAnswers: {},
          matchedAvatarId: undefined,
          weeklyPlan: undefined,
          permissions: {
            notifications: true,
            health: false,
          },
          stakes: {
            enabled: false,
          },
          step: 0,
          onboardingDone: false,
          xp: 0,
          progressPercent: 0,
          completedTasks: [],
          level: 1,
          streakDays: 0,
          lastCompletionLocalISO: undefined,
          weeklyGraceUsed: false,
          dailyChargeUsed: false,
        }),
    }),
    {
      name: 'levelup-onboarding',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        // Persist everything except step (UI state)
        selectedTraits: state.selectedTraits,
        quizAnswers: state.quizAnswers,
        matchedAvatarId: state.matchedAvatarId,
        weeklyPlan: state.weeklyPlan,
        permissions: state.permissions,
        stakes: state.stakes,
        onboardingDone: state.onboardingDone,
        xp: state.xp,
        progressPercent: state.progressPercent,
        completedTasks: state.completedTasks,
        level: state.level,
        streakDays: state.streakDays,
        lastCompletionLocalISO: state.lastCompletionLocalISO,
        weeklyGraceUsed: state.weeklyGraceUsed,
        dailyChargeUsed: state.dailyChargeUsed,
      }),
    }
  )
);