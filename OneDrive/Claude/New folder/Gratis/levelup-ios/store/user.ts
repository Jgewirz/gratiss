import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { TraitKey } from '@/data/traits';
import type { WeeklyPlan, Task } from '@/data/progression';

interface UserProfile {
  avatarId: string;
  selectedTraits: TraitKey[];
  weeklyPlan: WeeklyPlan;
  permissions: {
    notifications: boolean;
    health: boolean;
  };
}

interface GameProgress {
  level: number;
  currentXP: number;
  totalXP: number;
  currentWeek: number;
  completedTasks: string[]; // taskIds
  streakDays: number;
  lastActiveDate: string;
  achievements: string[]; // achievementIds
}

interface UserState {
  // Profile
  hasCompletedOnboarding: boolean;
  profile?: UserProfile;
  gameProgress: GameProgress;

  // Actions
  completeOnboarding: (profile: UserProfile) => void;
  completeTask: (taskId: string, xpEarned: number) => void;
  updateStreak: () => void;
  addAchievement: (achievementId: string) => void;
  advanceWeek: () => void;
  reset: () => void;
}

const initialGameProgress: GameProgress = {
  level: 1,
  currentXP: 0,
  totalXP: 0,
  currentWeek: 1,
  completedTasks: [],
  streakDays: 0,
  lastActiveDate: new Date().toISOString().split('T')[0],
  achievements: [],
};

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      // Initial state
      hasCompletedOnboarding: false,
      profile: undefined,
      gameProgress: initialGameProgress,

      // Actions
      completeOnboarding: (profile) =>
        set({
          hasCompletedOnboarding: true,
          profile,
          gameProgress: initialGameProgress,
        }),

      completeTask: (taskId, xpEarned) =>
        set((state) => {
          const newTotalXP = state.gameProgress.totalXP + xpEarned;
          const newCurrentXP = state.gameProgress.currentXP + xpEarned;

          // Calculate level (100 XP per level, exponential growth)
          let newLevel = state.gameProgress.level;
          let xpForNextLevel = 100 * Math.pow(1.2, newLevel);
          let remainingXP = newCurrentXP;

          while (remainingXP >= xpForNextLevel) {
            newLevel++;
            remainingXP -= xpForNextLevel;
            xpForNextLevel = 100 * Math.pow(1.2, newLevel);
          }

          return {
            gameProgress: {
              ...state.gameProgress,
              totalXP: newTotalXP,
              currentXP: remainingXP,
              level: newLevel,
              completedTasks: [...state.gameProgress.completedTasks, taskId],
            },
          };
        }),

      updateStreak: () =>
        set((state) => {
          const today = new Date().toISOString().split('T')[0];
          const lastActive = state.gameProgress.lastActiveDate;

          // Calculate days between dates
          const daysDiff = Math.floor(
            (new Date(today).getTime() - new Date(lastActive).getTime()) /
            (1000 * 60 * 60 * 24)
          );

          let newStreak = state.gameProgress.streakDays;

          if (daysDiff === 0) {
            // Same day, no change
          } else if (daysDiff === 1) {
            // Consecutive day
            newStreak++;
          } else {
            // Streak broken
            newStreak = 1;
          }

          return {
            gameProgress: {
              ...state.gameProgress,
              streakDays: newStreak,
              lastActiveDate: today,
            },
          };
        }),

      addAchievement: (achievementId) =>
        set((state) => ({
          gameProgress: {
            ...state.gameProgress,
            achievements: [...state.gameProgress.achievements, achievementId],
          },
        })),

      advanceWeek: () =>
        set((state) => ({
          gameProgress: {
            ...state.gameProgress,
            currentWeek: Math.min(state.gameProgress.currentWeek + 1, 8),
          },
        })),

      reset: () =>
        set({
          hasCompletedOnboarding: false,
          profile: undefined,
          gameProgress: initialGameProgress,
        }),
    }),
    {
      name: 'levelup-user-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);