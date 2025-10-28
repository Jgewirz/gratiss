# Grace Period & Time Management

## 4-Hour Grace Window

All time calculations in LevelUp use a 4-hour grace period: **00:00-03:59 counts as the previous day**.

### Rationale

- Accommodates late-night completion (up to 4am)
- Maintains streaks for users who stay up late
- Prevents arbitrary midnight cutoffs
- More forgiving for real-world behavior

## Implementation

### Get Effective Date

```typescript
import { subDays } from 'date-fns'

export function getEffectiveDate(date: Date = new Date()): Date {
  const hours = date.getHours()
  
  // 00:00-03:59 → previous day
  if (hours < 4) {
    return subDays(date, 1)
  }
  
  return date
}
```

### Examples

```typescript
// User completes task at 2:30am on Tuesday
getEffectiveDate(new Date('2025-01-28T02:30:00'))
// Returns: Monday 2025-01-27

// User completes task at 4:00am on Tuesday
getEffectiveDate(new Date('2025-01-28T04:00:00'))
// Returns: Tuesday 2025-01-28

// User completes task at 11:59pm on Monday
getEffectiveDate(new Date('2025-01-27T23:59:00'))
// Returns: Monday 2025-01-27
```

## Streak Calculation

### Logic Flow

```
Current Streak = 
  IF completed_today:
    MAINTAIN current_streak
  ELSE IF completed_yesterday (after grace):
    INCREMENT current_streak + 1
  ELSE:
    RESET to 0
```

### Implementation

```typescript
export function calculateStreak(
  completedTasks: Record<string, CompletedTask>
): number {
  const now = new Date()
  const effectiveToday = getEffectiveDate(now)
  const effectiveYesterday = subDays(effectiveToday, 1)
  
  const todayTasks = getTasksForDate(completedTasks, effectiveToday)
  const yesterdayTasks = getTasksForDate(completedTasks, effectiveYesterday)
  
  if (todayTasks.length > 0) {
    // Completed today (or in grace window), maintain streak
    return useUserStore.getState().currentStreak
  } else if (yesterdayTasks.length > 0) {
    // Completed yesterday, increment streak
    const newStreak = useUserStore.getState().currentStreak + 1
    
    // Update longest streak if exceeded
    const longestStreak = Math.max(
      newStreak,
      useUserStore.getState().longestStreak
    )
    
    return newStreak
  } else {
    // Gap detected, reset to 0
    return 0
  }
}
```

### Get Tasks for Date

```typescript
function getTasksForDate(
  completedTasks: Record<string, CompletedTask>,
  targetDate: Date
): CompletedTask[] {
  return Object.values(completedTasks).filter(task => {
    const taskDate = new Date(task.completedAt)
    const effectiveTaskDate = getEffectiveDate(taskDate)
    
    return isSameDay(effectiveTaskDate, targetDate)
  })
}
```

## Weekly Grace System

### Grace Rules

- **One free miss per week**: User can skip one day without penalty
- **Resets Monday**: Grace becomes available again every Monday
- **Automatic reset**: System checks on app launch

### State Management

```typescript
interface GraceState {
  weeklyGraceUsed: boolean     // Has grace been used this week?
  lastGraceReset: string        // ISO date of last Monday reset
}
```

### Reset Logic

```typescript
export function resetWeeklyGraceOnMonday(): void {
  const now = new Date()
  const state = useUserStore.getState()
  const lastReset = new Date(state.lastGraceReset)
  
  // Check if today is Monday (day 1)
  const isMonday = now.getDay() === 1
  
  // Check if at least 7 days have passed
  const daysSinceReset = differenceInDays(now, lastReset)
  const weekHasPassed = daysSinceReset >= 7
  
  if (isMonday && weekHasPassed) {
    useUserStore.setState({
      weeklyGraceUsed: false,
      lastGraceReset: now.toISOString(),
    })
  }
}
```

### Using Grace

```typescript
export function useWeeklyGrace(): void {
  useUserStore.setState({
    weeklyGraceUsed: true,
  })
}
```

## Daily Charge System

### Charge Rules

- **Max one charge per day**: User can only be charged once
- **Resets at 4am**: New charge possible after grace window
- **Stakes required**: Only applies when stakes enabled

### State Management

```typescript
interface ChargeState {
  dailyChargeUsed: boolean     // Has charge been applied today?
  lastChargeDate: string        // ISO date of last charge
}
```

### Mark Charge Used

```typescript
export function markDailyChargeUsed(): void {
  useUserStore.setState({
    dailyChargeUsed: true,
    lastChargeDate: new Date().toISOString(),
  })
}
```

### Reset Daily Charge

Called on app launch:

```typescript
export function resetDailyChargeIfNeeded(): void {
  const now = new Date()
  const state = useUserStore.getState()
  const lastChargeDate = new Date(state.lastChargeDate)
  
  const effectiveNow = getEffectiveDate(now)
  const effectiveLastCharge = getEffectiveDate(lastChargeDate)
  
  // If different effective dates, reset charge
  if (!isSameDay(effectiveNow, effectiveLastCharge)) {
    useUserStore.setState({
      dailyChargeUsed: false,
    })
  }
}
```

## Miss Detection & Gating

### Should Gate Logic

Gate user if ALL conditions met:

1. Stakes are enabled
2. Yesterday had zero completions (after grace)
3. Weekly grace not yet used
4. Daily charge not yet used today

```typescript
export function shouldGateForMiss(): boolean {
  const state = useUserStore.getState()
  
  // Check condition 1: Stakes enabled
  if (!state.stakesEnabled) {
    return false
  }
  
  // Check condition 2: Zero completions yesterday
  const now = new Date()
  const effectiveYesterday = subDays(getEffectiveDate(now), 1)
  const yesterdayCompletions = getTasksForDate(
    state.completedTasks,
    effectiveYesterday
  )
  
  if (yesterdayCompletions.length > 0) {
    return false
  }
  
  // Check condition 3: Weekly grace not used
  if (state.weeklyGraceUsed) {
    return false
  }
  
  // Check condition 4: Daily charge not used
  if (state.dailyChargeUsed) {
    return false
  }
  
  // All conditions met, gate user
  return true
}
```

### Gate Screen Flow

```typescript
export function GateScreen() {
  const useGrace = () => {
    useWeeklyGrace()
    router.replace('/(authenticated)/home')
  }
  
  const acceptCharge = () => {
    markDailyChargeUsed()
    processPayment(1.00) // $1 charge
    router.replace('/(authenticated)/home')
  }
  
  return (
    <View>
      <Text>You missed yesterday's tasks</Text>
      <Button onPress={useGrace}>Use Weekly Grace</Button>
      <Button onPress={acceptCharge}>Pay $1 Penalty</Button>
    </View>
  )
}
```

## Initialization & Lifecycle

### App Launch Checks

Run these on app initialization:

```typescript
export function initializeTimeSystem(): void {
  resetWeeklyGraceOnMonday()
  resetDailyChargeIfNeeded()
  
  // Check if gate needed
  if (shouldGateForMiss()) {
    router.replace('/gate')
  }
}
```

### Component Integration

```typescript
// app/(authenticated)/_layout.tsx
export default function AuthenticatedLayout() {
  useEffect(() => {
    initializeTimeSystem()
  }, [])
  
  return <Slot />
}
```

## Edge Cases

### Timezone Changes

If user crosses timezone:

```typescript
// Always use device local time
const now = new Date() // Gets local time
const effectiveDate = getEffectiveDate(now)
```

System adapts automatically to user's current timezone.

### DST Transitions

Daylight saving time handled by Date API:

```typescript
// Spring forward (2am → 3am)
getEffectiveDate(new Date('2025-03-09T02:30:00')) // Still works

// Fall back (2am → 1am)
getEffectiveDate(new Date('2025-11-02T01:30:00')) // Still works
```

### Rapid Completion Near Grace Boundary

```typescript
// Task completed at 3:58am (counts as yesterday)
completeTask('task-1', new Date('2025-01-28T03:58:00'))
// Effective date: Jan 27

// Task completed at 4:02am (counts as today)
completeTask('task-2', new Date('2025-01-28T04:02:00'))
// Effective date: Jan 28
```

Both tasks credited correctly, no double-counting.

## Testing Time Logic

### Mock Current Time

```typescript
// __tests__/time.spec.ts
import { getEffectiveDate } from '@/lib/time'

test('grace period before 4am', () => {
  const lateNight = new Date('2025-01-28T02:30:00')
  const effective = getEffectiveDate(lateNight)
  
  expect(effective.getDate()).toBe(27) // Previous day
})

test('no grace after 4am', () => {
  const morning = new Date('2025-01-28T04:00:00')
  const effective = getEffectiveDate(morning)
  
  expect(effective.getDate()).toBe(28) // Same day
})
```

### Mock Streak Scenarios

```typescript
test('streak maintained when completed today', () => {
  const completedTasks = {
    'task-1': {
      taskId: 'task-1',
      completedAt: new Date().toISOString(),
      xpEarned: 10,
    }
  }
  
  const streak = calculateStreak(completedTasks)
  expect(streak).toBe(5) // Maintained from previous
})

test('streak increments when completed yesterday', () => {
  const yesterday = subDays(new Date(), 1)
  const completedTasks = {
    'task-1': {
      taskId: 'task-1',
      completedAt: yesterday.toISOString(),
      xpEarned: 10,
    }
  }
  
  const streak = calculateStreak(completedTasks)
  expect(streak).toBe(6) // Previous + 1
})

test('streak resets when gap detected', () => {
  const twoDaysAgo = subDays(new Date(), 2)
  const completedTasks = {
    'task-1': {
      taskId: 'task-1',
      completedAt: twoDaysAgo.toISOString(),
      xpEarned: 10,
    }
  }
  
  const streak = calculateStreak(completedTasks)
  expect(streak).toBe(0) // Reset
})
```

## Constants Reference

```typescript
export const TIME_CONSTANTS = {
  GRACE_HOURS: 4,
  DAYS_IN_WEEK: 7,
  MONDAY_DAY_INDEX: 1,
  CHARGE_AMOUNT: 1.00,
}
```

## Debugging Time Issues

### Enable Time Logging

```typescript
export function debugTime(label: string): void {
  const now = new Date()
  const effective = getEffectiveDate(now)
  
  console.log(`[TIME] ${label}:`, {
    actual: now.toISOString(),
    effective: effective.toISOString(),
    hours: now.getHours(),
    inGracePeriod: now.getHours() < 4,
  })
}
```

### Dev Panel Override

Allow manual time manipulation in dev mode:

```typescript
// Only for development/testing
let mockTime: Date | null = null

export function setMockTime(date: Date): void {
  if (__DEV__) {
    mockTime = date
  }
}

export function getEffectiveDate(date: Date = mockTime || new Date()): Date {
  // ... rest of implementation
}
```
