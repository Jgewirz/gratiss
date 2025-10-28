---
name: levelup-ios-core
description: Core architecture patterns for LevelUp iOS app built with Expo/React Native. Use when working on routing, navigation, component structure, styling with NativeWind, or file organization. Covers Expo Router file-based routing, accessibility requirements, and copy management patterns.
---

# LevelUp iOS Core Architecture

## Project Tech Stack

- **Framework**: Expo (React Native)
- **Navigation**: Expo Router (file-based routing)
- **Styling**: NativeWind (Tailwind CSS for React Native)
- **State Management**: Zustand (see levelup-state-management skill)
- **Package Manager**: pnpm
- **Type System**: TypeScript strict mode

## Development Commands

```bash
# Install dependencies
pnpm install

# Run on iOS simulator
npx expo run:ios

# Run on Android
npx expo run:android

# Start dev server (interactive mode)
pnpm start

# Type checking
npx tsc --noEmit

# Run tests
pnpm test
jest --watch  # TDD mode
```

## Routing & Navigation

### File-Based Routing Pattern

Uses Expo Router with groups for flow isolation:

```
app/
├── index.tsx                    # Entry point, redirects based on onboardingDone
├── (onboarding)/               # Onboarding flow group
│   ├── welcome.tsx             # Step 1
│   ├── select-traits.tsx       # Step 2
│   ├── quiz.tsx                # Step 3
│   ├── avatar-result.tsx       # Step 4
│   ├── plan-preview.tsx        # Step 5
│   ├── permissions.tsx         # Step 6
│   └── start.tsx               # Step 7
└── (authenticated)/            # Main app group
    ├── home.tsx
    ├── progress.tsx
    └── settings.tsx
```

### Navigation Helpers

Located in `lib/routing.ts`:

```typescript
// Navigate to next onboarding step
router.push('/select-traits')

// Entry point redirect logic
const onboardingDone = useUserStore(state => state.onboardingDone)
useEffect(() => {
  if (onboardingDone) {
    router.replace('/(authenticated)/home')
  } else {
    router.replace('/(onboarding)/welcome')
  }
}, [onboardingDone])
```

## Styling with NativeWind

### Core Principles

- All styles use Tailwind utility classes
- Classes are compiled at build time
- No inline StyleSheet.create()
- Use semantic color tokens: `bg-primary`, `text-secondary`

### Common Patterns

```typescript
// Container with safe area
<View className="flex-1 bg-background px-4 pt-safe">

// Button with touch feedback
<Pressable 
  className="bg-primary rounded-lg px-6 py-3 active:opacity-80"
  accessibilityRole="button"
  accessibilityLabel="Continue to next step"
>
  <Text className="text-white font-semibold text-center">Continue</Text>
</Pressable>

// Card layout
<View className="bg-card rounded-xl p-4 shadow-sm border border-border">
```

### Responsive Sizing

- Use `w-full`, `max-w-sm`, `max-w-md` for constrained widths
- Minimum touch targets: 44x44 (use `min-w-[44px] min-h-[44px]`)
- Spacing scale: 2, 4, 6, 8, 12, 16 (use `gap-4`, `p-6`, `mt-8`)

## Accessibility Requirements

### Mandatory Properties

Every interactive element must have:

```typescript
<Pressable
  accessibilityRole="button"           // Required
  accessibilityLabel="Select Warrior"  // Required, descriptive
  accessibilityHint="Double tap to choose this avatar" // Optional
>
```

### Focus Order

Logical top-to-bottom flow:
1. Header/Navigation
2. Primary content
3. Secondary actions
4. Footer buttons

### Touch Targets

- Minimum 44x44 pixels
- Use padding to expand hitbox without visual change
- Test with accessibility inspector

## Copy Management

### Centralized Strings

All user-facing text lives in `lib/copy.ts`:

```typescript
export const COPY = {
  ONBOARDING: {
    WELCOME_TITLE: 'Welcome to LevelUp',
    WELCOME_SUBTITLE: 'Transform your habits into epic quests',
  },
  ERRORS: {
    TRAIT_LIMIT: 'You can only select 3 traits',
  },
  // ... etc
}
```

### Usage Pattern

```typescript
import { COPY } from '@/lib/copy'

<Text>{COPY.ONBOARDING.WELCOME_TITLE}</Text>
```

**Never use inline strings for UI text.** Debug logs and testIDs are exceptions.

## Type Safety

### Key Type Definitions

```typescript
// Trait system
type TraitKey = 'strength' | 'discipline' | 'courage' | ... // 10 total

// Avatar archetype
type Avatar = {
  id: string
  name: string
  primaryTrait: TraitKey
  secondaryTrait: TraitKey
  stats: {
    strength: number
    discipline: number
    // ...
  }
}

// Task structure
type Task = {
  id: string
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  duration: number // minutes
  xp: 10 | 20 | 30
  evidenceMode: 'check' | 'timer' | 'photo'
}
```

### Strict Mode Rules

- Never use `any` without runtime type guard
- Prefer discriminated unions for state machines
- Use generic constraints for reusable utilities

## Component Patterns

### Screen Structure

```typescript
export default function SelectTraitsScreen() {
  // 1. Hooks
  const router = useRouter()
  const selectedTraits = useOnboardingStore(state => state.selectedTraits)
  
  // 2. Handlers
  const handleContinue = () => {
    if (selectedTraits.length !== 3) return
    router.push('/quiz')
  }
  
  // 3. Render
  return (
    <View className="flex-1 bg-background">
      <ScrollView className="flex-1 px-4">
        {/* Content */}
      </ScrollView>
      <View className="px-4 pb-safe">
        <Button onPress={handleContinue} />
      </View>
    </View>
  )
}
```

### Error Boundaries

Wrap screens in error boundaries:

```typescript
export default function WrappedScreen() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <ActualScreen />
    </ErrorBoundary>
  )
}
```

## File Organization

```
lib/
├── copy.ts                 # All UI strings
├── routing.ts              # Navigation helpers
├── validators.ts           # Input validation
├── gamification.ts         # XP/avatar logic (see gamification skill)
└── types.ts                # Shared TypeScript types

components/
├── ui/                     # Reusable UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   └── TraitCard.tsx
└── screens/                # Screen-specific components
    └── AvatarDisplay.tsx

store/                      # Zustand stores (see state-management skill)
├── onboarding.ts
└── user.ts

data/
├── avatars.ts              # Avatar definitions
├── traits.ts               # Trait metadata
└── progression.ts          # Task templates
```

## Performance Considerations

- Heavy computations (avatar matching, plan generation) are memoized in stores
- Use SVG for avatars (vector scaling)
- Compress PNGs for photos
- AsyncStorage batching handled by Zustand persist middleware

## Testing Structure

```
__tests__/
├── onboarding.spec.ts      # Quiz, trait selection
├── gamification.spec.ts    # Avatar matching, XP
├── routing.spec.ts         # Navigation flows
└── validators.spec.ts      # Input validation
```

Test files co-located with implementation when unit-specific.
