---
name: levelup-state-management
description: Zustand state management patterns with AsyncStorage persistence for LevelUp iOS. Use when working on stores, state updates, persistence layer, onboarding flow state, user profile state, or task completion tracking. Covers two-store architecture with ephemeral and persistent data.
---

# LevelUp State Management

## Architecture Overview

LevelUp uses **two Zustand stores** with distinct persistence strategies:

1. **`store/onboarding.ts`**: Ephemeral onboarding flow state
2. **`store/user.ts`**: Long-term user profile and game progress

### Design Philosophy

- **Unidirectional data flow**: User Action → Store Action → State Update → Component Re-render
- **Immutable updates**: Never mutate state directly, use `set()` with new objects
- **Selective persistence**: Only persist what needs to survive app restarts
- **Computed values**: Derive state in selectors, don't store redundantly

## Onboarding Store

Located in `store/onboarding.ts`

### Purpose

Temporary state for the 7-step onboarding flow. Cleared after completion.

### State Shape

```typescript
interface OnboardingState {
  // Progress tracking
  currentStep: number
  completedSteps: Set<number>
  
  // Quiz data
  selectedTraits: TraitKey[]           // Max 3
  quizAnswers: Record<TraitKey, number>  // 0-1 normalized
  xpEarned: number                      // Total XP from quiz
  
  // Avatar result
  matchedAvatar: Avatar | null
  avatarScore: number
  
  // Actions
  selectTrait: (trait: TraitKey) => void
  deselectTrait: (trait: TraitKey) => void
  submitQuizAnswer: (trait: TraitKey, score: number) => void
  addXP: (amount: number) => void
  setMatchedAvatar: (avatar: Avatar, score: number) => void
  reset: () => void
}
```

### Persistence

```typescript
const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      // ... state
    }),
    {
      name: 'levelup-onboarding',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        selectedTraits: state.selectedTraits,
        quizAnswers: state.quizAnswers,
        matchedAvatar: state.matchedAvatar,
        // Don't persist: currentStep, completedSteps, xpEarned
      })
    }
  )
)
```

### Key Actions

#### Select Trait

```typescript
selectTrait: (trait) => {
  set((state) => {
    if (state.selectedTraits.length >= 3) {
      // Trigger shake animation
      return state
    }
    return {
      selectedTraits: [...state.selectedTraits, trait]
    }
  })
}
```

#### Submit Quiz Answer

```typescript
submitQuizAnswer: (trait, score) => {
  set((state) => ({
    quizAnswers: {
      ...state.quizAnswers,
      [trait]: Math.max(0, Math.min(1, score)) // Clamp 0-1
    }
  }))
}
```

#### Add XP

```typescript
addXP: (amount) => {
  set((state) => ({
    xpEarned: state.xpEarned + amount
  }))
}
```

### Validation

See `lib/validators.ts`:

```typescript
export function validateTraits(traits: TraitKey[]): void {
  if (traits.length === 0) {
    throw new Error(COPY.ERRORS.TRAIT_REQUIRED)
  }
  if (traits.length > 3) {
    throw new Error(COPY.ERRORS.TRAIT_LIMIT)
  }
  if (new Set(traits).size !== traits.length) {
    throw new Error(COPY.ERRORS.TRAIT_DUPLICATE)
  }
}
```

## User Store

Located in `store/user.ts`

### Purpose

Long-term user profile, game progress, achievements, and streaks. Persisted across app lifecycle.

### State Shape

```typescript
interface UserState {
  // Profile
  onboardingDone: boolean
  avatarId: string
  selectedTraits: TraitKey[]
  
  // Progress
  level: number
  totalXP: number
  currentWeek: number           // 1-8
  weeklyProgress: number        // 0-100
  
  // Weekly plan
  weeklyPlan: WeeklyPlan
  startDate: string             // ISO date
  
  // Task completion
  completedTasks: Record<string, CompletedTask>  // taskId -> completion data
  
  // Streaks & gates
  currentStreak: number
  longestStreak: number
  weeklyGraceUsed: boolean
  lastGraceReset: string        // ISO date (Monday)
  dailyChargeUsed: boolean
  lastChargeDate: string        // ISO date
  
  // Stakes
  stakesEnabled: boolean
  
  // Actions
  completeOnboarding: (avatar: Avatar, plan: WeeklyPlan) => void
  completeTask: (taskId: string, evidenceData?: any) => void
  advanceWeek: () => void
  useWeeklyGrace: () => void
  markDailyChargeUsed: () => void
  resetWeeklyGraceOnMonday: () => void
  reset: () => void
}
```

### Persistence

```typescript
const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      // ... state
    }),
    {
      name: 'levelup-user',
      storage: createJSONStorage(() => AsyncStorage),
      // Persist everything except computed values
    }
  )
)
```

### Key Actions

#### Complete Onboarding

```typescript
completeOnboarding: (avatar, plan) => {
  set({
    onboardingDone: true,
    avatarId: avatar.id,
    selectedTraits: get().selectedTraits,
    weeklyPlan: plan,
    startDate: new Date().toISOString(),
    level: 1,
    totalXP: 0,
    currentWeek: 1,
  })
}
```

#### Complete Task

```typescript
completeTask: (taskId, evidenceData) => {
  const task = findTaskById(taskId)
  
  set((state) => ({
    completedTasks: {
      ...state.completedTasks,
      [taskId]: {
        taskId,
        completedAt: new Date().toISOString(),
        evidenceData,
        xpEarned: task.xp,
      }
    },
    totalXP: state.totalXP + task.xp,
    weeklyProgress: calculateProgress(state, task.xp),
  }))
  
  // Check for level up
  const newLevel = calculateLevel(get().totalXP)
  if (newLevel > get().level) {
    set({ level: newLevel })
  }
}
```

#### Use Weekly Grace

```typescript
useWeeklyGrace: () => {
  set({
    weeklyGraceUsed: true,
    lastGraceReset: new Date().toISOString(),
  })
}
```

#### Reset Weekly Grace on Monday

```typescript
resetWeeklyGraceOnMonday: () => {
  const now = new Date()
  const lastReset = new Date(get().lastGraceReset)
  
  // Check if it's Monday and a week has passed
  if (now.getDay() === 1 && differenceInDays(now, lastReset) >= 7) {
    set({
      weeklyGraceUsed: false,
      lastGraceReset: now.toISOString(),
    })
  }
}
```

## Time & Grace Management

### Local Time with 4-Hour Grace

All time calculations use local ISO strings with 4-hour grace period:

```typescript
function getEffectiveDate(date: Date = new Date()): Date {
  const hours = date.getHours()
  
  // 00:00-03:59 counts as previous day
  if (hours < 4) {
    return subDays(date, 1)
  }
  
  return date
}
```

### Streak Calculation

```typescript
function calculateStreak(completedTasks: Record<string, CompletedTask>): number {
  const today = getEffectiveDate()
  const yesterday = subDays(today, 1)
  
  const todayTasks = getTasksForDate(completedTasks, today)
  const yesterdayTasks = getTasksForDate(completedTasks, yesterday)
  
  if (todayTasks.length > 0) {
    // Same day maintains streak
    return get().currentStreak
  } else if (yesterdayTasks.length > 0) {
    // Completed yesterday, increment
    return get().currentStreak + 1
  } else {
    // Gap detected, reset
    return 0
  }
}
```

### Stakes Gating Logic

```typescript
function shouldGateForMiss(): boolean {
  const state = get()
  
  return (
    state.stakesEnabled &&
    getCompletionsYesterday() === 0 &&
    !state.weeklyGraceUsed &&
    !state.dailyChargeUsed
  )
}
```

## Computed Selectors

### Weekly Progress

```typescript
const selectWeeklyProgress = (state: UserState) => {
  const currentWeekTasks = getCurrentWeekTasks(state)
  const completedWeekTasks = currentWeekTasks.filter(
    t => state.completedTasks[t.id]
  )
  
  const earnedXP = completedWeekTasks.reduce(
    (sum, t) => sum + t.xp, 
    0
  )
  
  return (earnedXP / 1000) * 100 // 1000 XP = 100%
}
```

### Current Level

```typescript
const selectCurrentLevel = (state: UserState) => {
  let level = 1
  let xpForLevel = 100
  let remainingXP = state.totalXP
  
  while (remainingXP >= xpForLevel) {
    remainingXP -= xpForLevel
    level++
    xpForLevel = Math.floor(100 * Math.pow(1.2, level - 1))
  }
  
  return {
    level,
    remainingXP,
    xpForNextLevel: xpForLevel,
  }
}
```

## Component Usage Patterns

### Reading State

```typescript
function SelectTraitsScreen() {
  const selectedTraits = useOnboardingStore(state => state.selectedTraits)
  const selectTrait = useOnboardingStore(state => state.selectTrait)
  
  return (
    <View>
      {TRAITS.map(trait => (
        <TraitCard
          key={trait}
          trait={trait}
          selected={selectedTraits.includes(trait)}
          onPress={() => selectTrait(trait)}
        />
      ))}
    </View>
  )
}
```

### Computed Selectors

```typescript
function ProgressScreen() {
  const progress = useUserStore(selectWeeklyProgress)
  const { level, remainingXP, xpForNextLevel } = useUserStore(selectCurrentLevel)
  
  return (
    <View>
      <Text>Level {level}</Text>
      <ProgressBar value={remainingXP / xpForNextLevel} />
      <Text>Weekly Progress: {progress.toFixed(1)}%</Text>
    </View>
  )
}
```

### Optimizing Re-renders

Use shallow equality for object selection:

```typescript
import { shallow } from 'zustand/shallow'

const { level, totalXP } = useUserStore(
  state => ({ level: state.level, totalXP: state.totalXP }),
  shallow
)
```

## Testing Patterns

### Mock Store

```typescript
// __tests__/mocks/stores.ts
export const mockOnboardingStore = {
  selectedTraits: ['strength', 'courage'],
  quizAnswers: {},
  selectTrait: jest.fn(),
  deselectTrait: jest.fn(),
  // ...
}

// Mock the actual store
jest.mock('@/store/onboarding', () => ({
  useOnboardingStore: (selector) => selector(mockOnboardingStore)
}))
```

### Testing Actions

```typescript
test('selectTrait enforces 3-trait cap', () => {
  const store = useOnboardingStore.getState()
  
  store.selectTrait('strength')
  store.selectTrait('courage')
  store.selectTrait('wisdom')
  store.selectTrait('discipline') // Should be ignored
  
  expect(store.selectedTraits).toHaveLength(3)
})
```

### Testing Persistence

```typescript
test('onboarding state persists', async () => {
  const store = useOnboardingStore.getState()
  
  store.selectTrait('strength')
  await new Promise(resolve => setTimeout(resolve, 100)) // Wait for AsyncStorage
  
  // Simulate app restart
  useOnboardingStore.persist.rehydrate()
  
  expect(useOnboardingStore.getState().selectedTraits).toContain('strength')
})
```

## Graceful Degradation

### AsyncStorage Failure

```typescript
const useUserStore = create<UserState>()(
  persist(
    // ... store definition
    {
      name: 'levelup-user',
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: () => (state, error) => {
        if (error) {
          console.error('Failed to rehydrate user store:', error)
          // Continue with initial state
        }
      },
    }
  )
)
```

### State Migration

```typescript
{
  name: 'levelup-user',
  version: 1,
  migrate: (persistedState: any, version: number) => {
    if (version === 0) {
      // Add new fields with defaults
      return {
        ...persistedState,
        weeklyGraceUsed: false,
        lastGraceReset: new Date().toISOString(),
      }
    }
    return persistedState
  },
}
```

## Common Pitfalls

### ❌ Direct Mutation

```typescript
// WRONG
const addTrait = (trait) => {
  state.selectedTraits.push(trait) // Mutates state
}
```

### ✅ Immutable Update

```typescript
// CORRECT
const addTrait = (trait) => {
  set((state) => ({
    selectedTraits: [...state.selectedTraits, trait]
  }))
}
```

### ❌ Async in Set

```typescript
// WRONG
const completeTask = async (taskId) => {
  const task = await fetchTask(taskId)
  set({ completedTasks: { ...completedTasks, [taskId]: task } })
}
```

### ✅ Async Before Set

```typescript
// CORRECT
const completeTask = async (taskId) => {
  const task = await fetchTask(taskId)
  
  // Set is synchronous
  set((state) => ({
    completedTasks: {
      ...state.completedTasks,
      [taskId]: task
    }
  }))
}
```

## References

For detailed examples of time calculations and grace period logic, see the grace-period-reference.md file.
