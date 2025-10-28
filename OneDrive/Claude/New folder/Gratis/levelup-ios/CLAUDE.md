# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LevelUp iOS is a gamified self-improvement mobile app built with Expo and React Native. It matches users to one of 10 avatar archetypes through a personality quiz, then guides them through an 8-week progression of research-backed challenges.

## Development Commands

```bash
# Install dependencies (use pnpm)
pnpm install

# Run on iOS simulator
npx expo run:ios

# Run on Android emulator
npx expo run:android

# Start Expo dev server (interactive mode)
pnpm start

# Type checking
npx tsc --noEmit

# Run tests (when configured)
pnpm test
jest --watch  # Watch mode for single test development

# Build for production (requires EAS CLI)
eas build --platform ios
eas build --platform android
```

## Core Architecture

### State Management Strategy
The app uses **Zustand** with two distinct stores:
- **`store/onboarding.ts`**: Ephemeral onboarding flow state with XP tracking, trait selection, and quiz answers. Persisted via AsyncStorage wrapper.
- **`store/user.ts`**: Long-term user profile, game progress, achievements. Full persistence across app restarts.

State updates follow a unidirectional flow: User Action → Store Action → State Update → Component Re-render.

### Avatar Matching Algorithm
Located in `lib/gamification.ts`, the `computeAvatarMatch()` function is **deterministic** and uses:
1. Normalized trait scores (0-1) from quiz answers
2. Selected traits get +1.5 weight bonus
3. Tie-breaking cascade: Score → Overlap Count → Highest Contribution → Lexicographic ID

This ensures identical inputs always produce the same avatar, critical for user trust.

### Task Progression System
The `generateWeeklyPlan()` in `data/progression.ts` implements:
- **Wave-linear progression**: Week 1 (15-25 min/day) → Week 8 (45-60 min/day) with Week 6 micro-deload
- **5 active days per week** with 2 rest days for sustainability
- **Max 3 tasks/day default**, 4 only when needed for minute targets
- **Photo evidence gated** to Week 5+ (earlier weeks use check/timer only)

### Routing & Navigation
Uses **Expo Router** file-based routing:
- `app/(onboarding)/` group contains 7-step flow: welcome → select-traits → quiz → avatar-result → plan-preview → permissions → start
- Entry point `app/index.tsx` redirects based on `onboardingDone` flag
- Navigation helpers in `lib/routing.ts` manage step progression

### XP & Gamification Constants
Fixed in `lib/gamification.ts`:
- Easy tasks: 10 XP
- Medium tasks: 20 XP
- Hard tasks: 30 XP
- Full Potential: 1000 XP (100% progress)

Level formula: `100 * 1.2^(level-1)` XP per level creates exponential growth curve.

## Critical Constraints

### Trait Selection
- **Hard limit of 3 traits** enforced in `lib/validators.ts` and UI
- Visual feedback via shake animation when limit reached
- At least 1 trait required to proceed

### Accessibility Requirements
- All interactive elements must have `accessibilityLabel` and `accessibilityRole`
- Touch targets minimum 44x44 pixels
- Focus order: Header → Content → Footer buttons

### Copy Management
All user-facing strings centralized in `lib/copy.ts`. Components must import from COPY object, no inline strings except for debugging.

### Evidence Modes
Three types with progressive unlocking:
- `check`: Manual confirmation (always available)
- `timer`: Time-based tracking (always available)
- `photo`: Photo proof (Week 5+ only)

## Testing Approach

Tests should be added to `__tests__/` directory. Key areas requiring coverage:
- Avatar matching determinism (100 iterations should yield same result)
- Trait cap validation (>3 throws error)
- Week progression bounds (W1: 15-25min, W8: 45-60min)
- XP calculations and progress updates
- AsyncStorage persistence mocking

Use lightweight mocks for React Native modules - see existing jest.setup.js for patterns.

## Performance Considerations

- Components use NativeWind (Tailwind) classes for styling - compiled at build time
- Heavy computations (avatar matching, plan generation) are memoized in stores
- Images should use SVG for avatars, compressed PNG for photos
- Zustand persist middleware handles AsyncStorage batching automatically

## Type Safety

TypeScript strict mode enabled. Key types:
- `TraitKey`: Union of 10 trait strings
- `Avatar`: Archetype with primary/secondary traits and stats
- `Task`: Individual challenge with difficulty, duration, XP
- `WeeklyPlan`: 8-week structure with progressive tasks

Never use `any` without runtime type guards. Prefer discriminated unions for state machines.

## Determinism & Debugging

### Pure Functions
All scoring, matching, and progression functions are pure:
- `computeAvatarMatch()`: No side effects, no Date/Math.random inside
- `generateWeeklyPlan()`: Deterministic based on avatar ID seed
- `explainMatch()`: Returns full decision trace for debugging

### Self-Test
Export `__selfTest()` in `lib/gamification.ts` validates:
- Avatar matching determinism (5 iterations identical)
- XP → progress monotonic mapping
- Returns boolean for CI/CD integration

### Dev Panel
Available at `app/(onboarding)/dev-panel.tsx` when `EXPO_PUBLIC_DEV_PANEL=1`:
- Reset onboarding state
- Simulate missed days
- Trigger grace/charge states
- Run validation suite
- Displays `<View testID="selftest-ok" />` on pass

## Progression Allocator

### Wave-Linear Formula
```
Week 1: 15-25 min/day (avg 20)
Week 2: 20-30 min/day (avg 25)
Week 3: 25-35 min/day (avg 30)
Week 4: 30-40 min/day (avg 35)
Week 5: 35-45 min/day (avg 40)
Week 6: 32-42 min/day (avg 37) ← Micro-deload ≤90% of Week 5
Week 7: 40-55 min/day (avg 47)
Week 8: 45-60 min/day (avg 52)
```

### Task Distribution Rules
- **Top trait daily**: First selected trait gets ≥1 task per active day
- **Rotation**: Other traits rotate through remaining slots
- **Task cap**: Max 3 tasks/day default, 4th only if minutes unmet
- **Active days**: Mon-Fri active, Sat-Sun rest (5:2 ratio)

### Validation
`validatePlan()` throws on violations:
- Minute bounds exceeded
- Week 6 deload violation
- Wrong active/rest day counts
- Task cap violations
- Photo evidence before Week 5

## Time, Streaks & Grace

### Local Time with Grace
All time calculations use local ISO strings with 4-hour grace:
- **Grace window**: 00:00-03:59 counts as previous day
- **Streak calculation**: Same day maintains, next day increments, gap resets
- **Miss detection**: >1 day gap after grace triggers gate

### Stakes Gating Logic
`shouldGateForMiss()` returns true only when ALL conditions met:
1. Stakes enabled
2. Yesterday had zero completions (after grace)
3. Weekly grace not yet used
4. Daily charge not already used today

### Grace Management
- **Weekly grace**: One free miss per week, resets Monday
- **Daily charge cap**: Max one $1 charge per day
- **Pause Week**: Future feature for vacation/illness

## Evidence Privacy & Safety

### Photo Evidence Rules
- **Week gating**: Photos only available Week 5+
- **EXIF stripping**: Location data removed before storage
- **Local-only**: Photos stored on device, no cloud upload
- **Consent required**: Show privacy notice on first photo task

### Evidence Consent Copy
Located in `COPY.EVIDENCE_CONSENT`:
- Explain local storage
- Warn about faces/personal info
- Describe offline queue
- Preview/delete capability

### Evidence Mode Assignment
```typescript
evidenceMode: week >= 5 && dayIndex % 2 === 0 ? 'photo' :
              (dayIndex % 2 === 0 ? 'timer' : 'check')
```

## Failure & Recovery

### Graceful Degradation
- Missing avatar match: Default to first avatar
- Plan generation failure: Retry with reduced constraints
- AsyncStorage failure: Continue with in-memory state
- Network failure: Queue actions for later sync

### Error Boundaries
Each screen wrapped in error boundary that:
- Logs to console in dev
- Shows user-friendly message in prod
- Offers retry action
- Maintains navigation state

### Recovery Actions
- `reset()`: Full state reset
- `resetWeeklyGraceOnMonday()`: Automatic grace reset
- `markDailyChargeUsed()`: Prevent double charging
- `useWeeklyGrace()`: One-time grace activation

## Testing Matrix

### Critical Test Coverage
```
✅ matching_deterministic_100x - Same input → same avatar 100 times
✅ matching_tiebreak_cascade - Tie-breaker order verified
✅ traitCap_enforced - Max 3 traits, min 1 trait
✅ progression_bounds_topTrait_daily_taskCap - All week constraints
✅ evidence_gating_week5_plus - Photo only Week 5+
✅ xp_progress_and_gate_logic - XP awards, progress calc, gate triggers
✅ persistence_and_routing_basic - AsyncStorage and navigation
```

### Test Commands
```bash
# Run all tests
pnpm test

# Watch mode for TDD
jest --watch

# Coverage report
jest --coverage

# Single file
jest __tests__/onboarding.spec.ts
```

### Mock Strategy
- AsyncStorage: In-memory object
- React Native modules: Minimal stubs
- Expo modules: Return components as strings
- Animations: Disabled in tests