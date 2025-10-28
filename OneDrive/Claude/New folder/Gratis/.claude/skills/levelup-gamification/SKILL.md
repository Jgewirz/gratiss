---
name: levelup-gamification
description: Avatar matching algorithm, XP calculations, task progression system, and deterministic gamification logic for LevelUp iOS. Use when working on avatar archetypes, quiz scoring, XP rewards, level progression, weekly task planning, or evidence modes. Critical for maintaining determinism and user trust.
---

# LevelUp Gamification System

## Core Principle: Determinism

**All gamification logic must be deterministic.** Identical inputs always produce identical outputs. No `Math.random()`, no `Date.now()` inside scoring functions. This is critical for user trust and testing.

## Avatar Matching Algorithm

Located in `lib/gamification.ts` → `computeAvatarMatch()`

### Inputs

```typescript
interface MatchInput {
  quizAnswers: Record<TraitKey, number>  // 0-1 normalized scores
  selectedTraits: TraitKey[]              // Exactly 3 traits
}
```

### Algorithm Steps

1. **Apply Selection Bonus**: Selected traits get +1.5 weight
2. **Calculate Avatar Scores**: For each of 10 avatars, compute weighted match
3. **Break Ties**: Use cascade: Score → Overlap → Contribution → Lexicographic

### Scoring Formula

```typescript
avatarScore = sum(
  avatar.stats[trait] * (
    quizAnswers[trait] * (selectedTraits.includes(trait) ? 2.5 : 1.0)
  )
)
```

### Tie-Breaking Cascade

When multiple avatars have same score:

1. **Overlap Count**: Count how many selected traits match avatar's primary/secondary
2. **Highest Contribution**: Which trait contributed most to score
3. **Lexicographic**: Alphabetical by avatar ID (last resort)

### Example

```typescript
const match = computeAvatarMatch({
  quizAnswers: {
    strength: 0.8,
    discipline: 0.6,
    courage: 0.9,
    // ...
  },
  selectedTraits: ['strength', 'courage', 'wisdom']
})
// Returns: { avatarId: 'warrior', score: 87.5, ... }
```

### Validation

Export `__selfTest()` that runs 5 iterations and verifies identical results.

## XP & Progression System

### XP Values (Fixed Constants)

```typescript
const XP_VALUES = {
  EASY: 10,
  MEDIUM: 20,
  HARD: 30,
  FULL_POTENTIAL: 1000  // 100% weekly progress
}
```

### Level Formula

```typescript
xpForLevel(level: number): number {
  return Math.floor(100 * Math.pow(1.2, level - 1))
}
```

Creates exponential growth curve:
- Level 1: 100 XP
- Level 2: 120 XP
- Level 3: 144 XP
- Level 10: 516 XP

### Progress Calculation

```typescript
weeklyProgress = (earnedXP / 1000) * 100  // Percentage
shouldGate = progress < 75 && !graceUsed && !pauseWeek
```

## Task Progression System

See `references/progression-system.md` for complete wave-linear formula and task allocation rules.

### Quick Reference

```
Week 1: 15-25 min/day (avg 20)
Week 2: 20-30 min/day (avg 25)
Week 3: 25-35 min/day (avg 30)
Week 4: 30-40 min/day (avg 35)
Week 5: 35-45 min/day (avg 40)
Week 6: 32-42 min/day (avg 37) ← Micro-deload
Week 7: 40-55 min/day (avg 47)
Week 8: 45-60 min/day (avg 52)
```

### Active Days Pattern

- **5 active days**: Mon-Fri
- **2 rest days**: Sat-Sun
- Never schedule tasks on rest days

### Task Allocation Rules

1. **Top Trait Daily**: First selected trait gets ≥1 task per active day
2. **Rotation**: Other traits rotate through remaining slots
3. **Task Cap**: Max 3 tasks/day default, 4th only if needed for minute target
4. **Evidence Mode Assignment**: 
   - Photo: Week 5+, even-indexed days
   - Timer: Even-indexed days before Week 5
   - Check: Odd-indexed days

## Evidence Modes

### Three Types

```typescript
type EvidenceMode = 'check' | 'timer' | 'photo'
```

- **check**: Manual confirmation (always available)
- **timer**: Time-based tracking (always available)
- **photo**: Photo proof (Week 5+ only)

### Gating Logic

```typescript
evidenceMode: 
  week >= 5 && dayIndex % 2 === 0 ? 'photo' :
  dayIndex % 2 === 0 ? 'timer' : 
  'check'
```

### Privacy Rules

- Photos stored locally only
- EXIF data stripped
- Consent shown on first photo task
- Preview/delete capability

## Validation Suite

Located in `lib/gamification.ts` → `validatePlan()`

### Checks

- Minute bounds per week
- Week 6 deload (≤90% of Week 5)
- Active/rest day counts (5:2 ratio)
- Task cap violations
- Photo evidence before Week 5
- Top trait daily appearance

### Usage

```typescript
try {
  validatePlan(weeklyPlan)
} catch (error) {
  // Plan violated constraints
  console.error(error.message)
}
```

## Determinism Debugging

### Decision Trace

```typescript
const result = explainMatch(input)
// Returns full trace:
// - Normalized scores
// - Selection bonuses
// - Avatar calculations
// - Tie-break decisions
```

### Self-Test Integration

```typescript
export function __selfTest(): boolean {
  const testInput = { /* ... */ }
  const results = Array(5).fill(null).map(() => 
    computeAvatarMatch(testInput)
  )
  return results.every(r => r.avatarId === results[0].avatarId)
}
```

## Common Pitfalls

### ❌ Non-Deterministic

```typescript
// WRONG: Uses Math.random
function selectAvatar() {
  return avatars[Math.floor(Math.random() * avatars.length)]
}

// WRONG: Uses current time
function generatePlan() {
  const seed = Date.now()
  // ...
}
```

### ✅ Deterministic

```typescript
// CORRECT: Deterministic based on inputs
function selectAvatar(quizAnswers, selectedTraits) {
  return computeAvatarMatch({ quizAnswers, selectedTraits })
}

// CORRECT: Seeded by avatar ID
function generatePlan(avatarId: string, week: number) {
  const seed = hashString(avatarId + week)
  // ...
}
```

## Trait System

### 10 Core Traits

```typescript
const TRAITS: TraitKey[] = [
  'strength',     // Physical power
  'discipline',   // Self-control
  'courage',      // Bravery
  'wisdom',       // Knowledge
  'compassion',   // Empathy
  'creativity',   // Innovation
  'focus',        // Concentration
  'resilience',   // Endurance
  'leadership',   // Influence
  'curiosity'     // Exploration
]
```

### Trait Cap

- **Maximum**: 3 traits (hard limit in validators)
- **Minimum**: 1 trait (required to proceed)
- Visual feedback via shake animation when limit reached

## Testing Requirements

### Critical Test Coverage

```typescript
// Avatar matching determinism
test('matching_deterministic_100x', () => {
  const input = { /* ... */ }
  const results = Array(100).fill(null).map(() => 
    computeAvatarMatch(input)
  )
  expect(new Set(results.map(r => r.avatarId)).size).toBe(1)
})

// Trait cap enforcement
test('traitCap_enforced', () => {
  expect(() => validateTraits(['a', 'b', 'c', 'd'])).toThrow()
})

// Progression bounds
test('progression_bounds', () => {
  const plan = generateWeeklyPlan('warrior')
  plan.weeks.forEach((week, i) => {
    expect(week.minutesPerDay).toBeWithinRange(BOUNDS[i])
  })
})
```

## Resources

### references/progression-system.md

Complete wave-linear progression formula, task allocation algorithm, and validation rules. Read when implementing or debugging weekly plan generation.

### references/avatar-archetypes.md

Full avatar definitions with primary/secondary traits, stat distributions, and personality profiles. Read when working on avatar display or matching explanations.
