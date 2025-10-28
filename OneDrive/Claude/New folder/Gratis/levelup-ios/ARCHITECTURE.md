# LevelUp iOS - Architecture Documentation

## Overview

This is a gamified self-improvement iOS app built with Expo and React Native that transforms personal growth into an RPG-like journey. Users complete a personality assessment, get matched with one of 10 avatar archetypes, and progress through an 8-week program of research-backed challenges.

## Tech Stack

- **Framework**: Expo SDK 50
- **Language**: TypeScript
- **Navigation**: Expo Router (file-based routing)
- **Styling**: NativeWind (Tailwind CSS for React Native)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **UI Components**: React Native core + custom components
- **Animations**: React Native Reanimated
- **Graphics**: React Native SVG + Linear Gradient

## Architecture Decisions

### 1. State Management

We use **Zustand** for state management with two stores:

- **`onboarding.ts`**: Temporary state for the onboarding flow
- **`user.ts`**: Persistent state with AsyncStorage for user data, progress, and achievements

### 2. Avatar Matching Algorithm

The `computeAvatarMatch()` function in `lib/gamification.ts` uses a weighted scoring system:

- **Trait Alignment (0-100 points)**:
  - Primary trait match: +30 points
  - Secondary trait match: +15 points

- **Quiz Answers (0-50 points)**:
  - Maps Likert scale responses (1-5) to avatar compatibility

### 3. Task Progression System

Tasks follow a research-backed difficulty curve:

- **Weeks 1-2**: Easy tasks (10 XP each)
- **Weeks 3-5**: Medium tasks (25 XP each)
- **Weeks 6-8**: Hard tasks (50 XP each)

Tasks increase both in difficulty and quantity as users progress.

### 4. Gamification Mechanics

#### XP & Leveling
- Level calculation: `100 * 1.2^(level-1)` XP required per level
- Creates exponential growth requiring more effort at higher levels

#### Streaks
- Daily activity tracking
- Automatic streak calculation based on last active date
- Streak breaks if >1 day gap

#### Achievements
- Condition-based unlocking
- Checked automatically on task completion
- Examples: First Step, Week Warrior, Streak achievements

## Data Models

### Core Types

```typescript
// Traits (10 total)
type TraitKey = 'mindfulness' | 'discipline' | 'productivity' | 'focus' |
                'self-awareness' | 'confidence' | 'resilience' |
                'creativity' | 'learning' | 'wellbeing';

// Avatar
interface Avatar {
  id: string;
  name: string;
  primaryTraits: TraitKey[];
  secondaryTraits: TraitKey[];
  stats: { discipline: number; focus: number; growth: number };
}

// Task
interface Task {
  id: string;
  title: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: TraitKey;
  xpReward: number;
}
```

## Onboarding Flow

The 7-step onboarding flow is designed for progressive disclosure:

1. **Welcome** → Value proposition
2. **Select Traits** → Choose 1-3 focus areas
3. **Quiz** → 10 personality questions
4. **Avatar Result** → Reveal matched archetype
5. **Plan Preview** → Show 8-week journey
6. **Permissions** → Request notifications/health
7. **Start** → Begin first task

## Component Architecture

### Layout Components
- `_layout.tsx`: Root layout with providers
- `(onboarding)/_layout.tsx`: Onboarding wrapper with progress header

### Smart Components (Connected to State)
- Onboarding screens (7 screens)
- Dashboard screen

### Presentation Components
- `ProgressHeader`: Visual progress indicator
- `StepFooter`: Navigation controls
- `TraitPills`: Trait selection UI
- `QuizCard`: Likert scale question UI
- `AvatarCard`: Avatar reveal display
- `WeekPlanList`: Task preview list
- `PermissionToggles`: Settings switches
- `FirstTaskCard`: Task preview

## File Structure

```
levelup-ios/
├── app/                    # Screens (Expo Router)
│   ├── (onboarding)/      # Onboarding flow
│   ├── _layout.tsx        # Root layout
│   ├── index.tsx          # Entry redirect
│   └── dashboard.tsx      # Main app
├── components/            # Reusable components
├── store/                 # Zustand stores
├── data/                  # Static data seeds
│   ├── traits.ts          # 10 trait definitions
│   ├── avatars.ts         # 10 avatar archetypes
│   ├── quiz.ts            # Quiz questions
│   └── progression.ts     # Task templates
├── lib/                   # Utilities
│   ├── routing.ts         # Navigation helpers
│   ├── gamification.ts    # Game logic
│   ├── validators.ts      # Input validation
│   └── copy.ts           # Text content
└── assets/               # Images/icons
```

## Performance Optimizations

1. **Lazy Loading**: Screens loaded on-demand via Expo Router
2. **Memoization**: Heavy computations cached in stores
3. **List Optimization**: FlatList for long task lists (future)
4. **Image Optimization**: SVG for avatars, compressed PNGs for photos

## Security Considerations

1. **Input Validation**: All user inputs validated with Zod-like validators
2. **Data Persistence**: Encrypted AsyncStorage for sensitive data
3. **Permissions**: Explicit user consent for notifications/health
4. **Privacy**: No data sharing, local-first architecture

## Future Enhancements

### Phase 2
- Social features (parties, leaderboards)
- Cloud sync with backend API
- Premium features ($1/day accountability)
- Advanced achievements system

### Phase 3
- AI-generated personalized tasks
- Integration with wearables
- Habit stacking recommendations
- Community challenges

## Development Commands

```bash
# Install dependencies
pnpm install

# Run on iOS simulator
npx expo run:ios

# Run on Android
npx expo run:android

# Start dev server
pnpm start

# Type checking
npx tsc --noEmit

# Build for production
eas build --platform ios
```

## Testing Strategy

### Unit Tests (TODO)
- Avatar matching algorithm
- XP/level calculations
- Streak logic
- Task generation

### Integration Tests (TODO)
- Onboarding flow completion
- State persistence
- Achievement unlocking

### E2E Tests (TODO)
- Full user journey
- Edge cases (network failure, etc.)

## Deployment

### iOS App Store
1. Configure app.json with production values
2. Build with EAS Build
3. Submit via EAS Submit or Xcode

### Future: Android
- Similar process for Google Play Store
- Ensure adaptive icon configured

## Monitoring (Future)

- Crash reporting: Sentry
- Analytics: Mixpanel/Amplitude
- Performance: React Native Performance Monitor

---

This architecture is designed to be scalable, maintainable, and provide an excellent user experience while keeping the codebase simple and focused on the core value proposition: gamified self-improvement through personalized challenges.