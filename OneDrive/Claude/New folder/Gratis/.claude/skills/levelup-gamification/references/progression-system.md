# Task Progression System

## Wave-Linear Formula

The progression follows a wave-linear pattern with a strategic micro-deload in Week 6:

```
Week 1: 15-25 min/day (avg 20) - Gentle introduction
Week 2: 20-30 min/day (avg 25) - Early momentum
Week 3: 25-35 min/day (avg 30) - Building consistency
Week 4: 30-40 min/day (avg 35) - Establishing routine
Week 5: 35-45 min/day (avg 40) - Peak load phase 1
Week 6: 32-42 min/day (avg 37) - MICRO-DELOAD (≤90% of Week 5)
Week 7: 40-55 min/day (avg 47) - Peak load phase 2
Week 8: 45-60 min/day (avg 52) - Maximum capacity
```

### Deload Week Purpose

Week 6 is intentionally scaled back to prevent burnout:
- Prevents cumulative fatigue
- Allows recovery before final push
- Maintains long-term adherence
- Must be ≤90% of Week 5 average minutes

## Active Days Pattern

```
Monday: Active
Tuesday: Active
Wednesday: Active
Thursday: Active
Friday: Active
Saturday: REST
Sunday: REST
```

**5:2 ratio** - 5 active days, 2 rest days per week.

## Task Allocation Algorithm

### Step 1: Determine Daily Minute Target

For each active day in the week, calculate target minutes:

```typescript
const weekBounds = WEEK_BOUNDS[weekIndex] // e.g., [15, 25] for Week 1
const targetMinutes = Math.floor(
  Math.random() * (weekBounds[1] - weekBounds[0] + 1) + weekBounds[0]
)
```

**Note**: In production, use deterministic seeding instead of `Math.random()`:

```typescript
const seed = hashString(avatarId + weekIndex + dayIndex)
const targetMinutes = seededRandom(seed, weekBounds[0], weekBounds[1])
```

### Step 2: Allocate Top Trait Task

First selected trait MUST appear on every active day:

```typescript
const topTrait = selectedTraits[0]
const topTraitTask = selectTaskForTrait(topTrait, targetMinutes)
remainingMinutes = targetMinutes - topTraitTask.duration
```

### Step 3: Fill Remaining Minutes

Rotate through other selected traits:

```typescript
let traitIndex = 1
while (remainingMinutes >= MIN_TASK_DURATION && tasksToday.length < 3) {
  const trait = selectedTraits[traitIndex % selectedTraits.length]
  const task = selectTaskForTrait(trait, remainingMinutes)
  tasksToday.push(task)
  remainingMinutes -= task.duration
  traitIndex++
}
```

### Step 4: Add 4th Task If Needed

Only if minute target not met and we're under cap:

```typescript
if (remainingMinutes > 5 && tasksToday.length < 4) {
  const fillTask = selectShortTask(remainingMinutes)
  tasksToday.push(fillTask)
}
```

### Task Cap Rules

- **Default max**: 3 tasks per day
- **Emergency 4th**: Only when needed to meet minute minimum
- **Never exceed**: 4 tasks per day under any circumstance

## Task Difficulty Distribution

### Per Week

```
Week 1-2: 60% Easy, 30% Medium, 10% Hard
Week 3-4: 40% Easy, 40% Medium, 20% Hard
Week 5-6: 20% Easy, 40% Medium, 40% Hard
Week 7-8: 10% Easy, 30% Medium, 60% Hard
```

### Duration by Difficulty

```
Easy:   5-10 minutes
Medium: 10-20 minutes
Hard:   20-30 minutes
```

## Evidence Mode Assignment

Progressive unlocking based on week and day:

```typescript
function assignEvidenceMode(weekIndex: number, dayIndex: number): EvidenceMode {
  const week = weekIndex + 1 // Convert to 1-based
  
  if (week >= 5 && dayIndex % 2 === 0) {
    return 'photo'
  } else if (dayIndex % 2 === 0) {
    return 'timer'
  } else {
    return 'check'
  }
}
```

### Evidence Mode Rules

- **Photo**: Week 5+ only, even-indexed days (0, 2, 4)
- **Timer**: Before Week 5, even-indexed days
- **Check**: All odd-indexed days

**Privacy Note**: Photo evidence requires consent on first use. Show privacy notice explaining local storage and no cloud upload.

## Validation Rules

### Weekly Bounds Check

```typescript
for (let weekIndex = 0; weekIndex < 8; weekIndex++) {
  const [min, max] = WEEK_BOUNDS[weekIndex]
  
  for (const day of week.activeDays) {
    const totalMinutes = day.tasks.reduce((sum, t) => sum + t.duration, 0)
    assert(totalMinutes >= min && totalMinutes <= max, 
      `Week ${weekIndex + 1} day out of bounds: ${totalMinutes}`)
  }
}
```

### Deload Week Validation

```typescript
const week5Avg = calculateWeekAverage(weeks[4])
const week6Avg = calculateWeekAverage(weeks[5])
assert(week6Avg <= week5Avg * 0.90, 
  'Week 6 must be ≤90% of Week 5')
```

### Active/Rest Day Count

```typescript
assert(week.activeDays.length === 5, 'Must have 5 active days')
assert(week.restDays.length === 2, 'Must have 2 rest days')
```

### Top Trait Appearance

```typescript
const topTrait = selectedTraits[0]
for (const day of week.activeDays) {
  const hasTopTrait = day.tasks.some(t => t.trait === topTrait)
  assert(hasTopTrait, `Top trait ${topTrait} missing from day`)
}
```

### Photo Evidence Gating

```typescript
for (let weekIndex = 0; weekIndex < 4; weekIndex++) {
  for (const day of weeks[weekIndex].activeDays) {
    for (const task of day.tasks) {
      assert(task.evidenceMode !== 'photo', 
        'Photo evidence not allowed before Week 5')
    }
  }
}
```

### Task Cap Enforcement

```typescript
for (const day of week.activeDays) {
  assert(day.tasks.length >= 1, 'Must have at least 1 task')
  assert(day.tasks.length <= 4, 'Cannot exceed 4 tasks per day')
  
  if (day.tasks.length === 4) {
    // 4th task only allowed if needed for minute target
    const without4th = day.tasks.slice(0, 3)
      .reduce((sum, t) => sum + t.duration, 0)
    assert(without4th < MIN_DAILY_MINUTES[weekIndex], 
      '4th task only allowed when 3 tasks insufficient')
  }
}
```

## Implementation Example

```typescript
export function generateWeeklyPlan(
  avatarId: string,
  selectedTraits: TraitKey[]
): WeeklyPlan {
  const weeks: Week[] = []
  
  for (let weekIndex = 0; weekIndex < 8; weekIndex++) {
    const week: Week = { activeDays: [], restDays: [] }
    const [minMinutes, maxMinutes] = WEEK_BOUNDS[weekIndex]
    
    // Generate 5 active days
    for (let dayIndex = 0; dayIndex < 5; dayIndex++) {
      const seed = hashString(`${avatarId}-${weekIndex}-${dayIndex}`)
      const targetMinutes = seededRandom(seed, minMinutes, maxMinutes)
      
      const day = {
        index: dayIndex,
        tasks: [],
        date: null // Will be set when plan starts
      }
      
      // Step 1: Top trait task
      const topTraitTask = selectTaskForTrait(
        selectedTraits[0], 
        targetMinutes,
        weekIndex
      )
      day.tasks.push(topTraitTask)
      
      // Step 2: Fill remaining minutes
      let remaining = targetMinutes - topTraitTask.duration
      let traitIndex = 1
      
      while (remaining >= 5 && day.tasks.length < 3) {
        const trait = selectedTraits[traitIndex % selectedTraits.length]
        const task = selectTaskForTrait(trait, remaining, weekIndex)
        day.tasks.push(task)
        remaining -= task.duration
        traitIndex++
      }
      
      // Step 3: Add 4th task if needed
      if (remaining > 5 && day.tasks.length < 4) {
        const fillTask = selectShortTask(remaining, weekIndex)
        day.tasks.push(fillTask)
      }
      
      // Assign evidence modes
      day.tasks.forEach((task, idx) => {
        task.evidenceMode = assignEvidenceMode(weekIndex, dayIndex)
      })
      
      week.activeDays.push(day)
    }
    
    // Add 2 rest days (Saturday, Sunday)
    week.restDays.push({ index: 5 }, { index: 6 })
    
    weeks.push(week)
  }
  
  // Validate before returning
  validatePlan({ weeks, avatarId, selectedTraits })
  
  return { weeks, avatarId, selectedTraits, createdAt: new Date().toISOString() }
}
```

## Constants Reference

```typescript
const WEEK_BOUNDS: [number, number][] = [
  [15, 25], // Week 1
  [20, 30], // Week 2
  [25, 35], // Week 3
  [30, 40], // Week 4
  [35, 45], // Week 5
  [32, 42], // Week 6 - Deload
  [40, 55], // Week 7
  [45, 60], // Week 8
]

const MIN_TASK_DURATION = 5
const MAX_TASKS_PER_DAY_DEFAULT = 3
const MAX_TASKS_PER_DAY_EMERGENCY = 4

const DIFFICULTY_DURATIONS = {
  easy: [5, 10],
  medium: [10, 20],
  hard: [20, 30],
}

const XP_BY_DIFFICULTY = {
  easy: 10,
  medium: 20,
  hard: 30,
}
```
