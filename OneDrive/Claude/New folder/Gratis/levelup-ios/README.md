# LevelUp iOS - Gamified Self-Improvement

Transform your life through personalized avatar archetypes and research-backed habit formation.

## Features

- **Avatar Archetype System**: 10 unique archetypes matched through personality quiz
- **Trait-Based Personalization**: Select up to 3 core traits from mindfulness, discipline, productivity, focus, self-awareness, confidence, resilience, creativity, learning, and wellbeing
- **8-Week Progression**: Research-backed tasks that progressively increase in difficulty
- **Gamification**: XP system, levels, and progress tracking toward "Full Potential"
- **Smart Task Generation**: AI-generated tasks based on your avatar and selected traits

## Tech Stack

- **Framework**: Expo (React Native)
- **Language**: TypeScript
- **Routing**: Expo Router (file-based)
- **Styling**: NativeWind (Tailwind for React Native)
- **State**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **UI**: React Native Reanimated & SVG

## Setup

```bash
# Install dependencies
pnpm install

# iOS development
npx expo run:ios

# Android development
npx expo run:android

# Start development server
pnpm start
```

## Project Structure

```
levelup-ios/
├── app/                    # Expo Router screens
│   ├── (onboarding)/      # Onboarding flow
│   ├── _layout.tsx        # Root layout
│   └── index.tsx          # Entry point
├── components/            # Reusable components
│   └── onboarding/        # Onboarding-specific
├── store/                 # Zustand stores
│   ├── onboarding.ts      # Onboarding state
│   └── user.ts            # User state
├── data/                  # Static data & seeds
│   ├── traits.ts          # Trait definitions
│   ├── avatars.ts         # Avatar archetypes
│   ├── quiz.ts            # Quiz questions
│   └── progression.ts     # 8-week plans
├── lib/                   # Utilities
│   ├── routing.ts         # Navigation helpers
│   ├── gamification.ts    # XP & scoring logic
│   └── validators.ts      # Input validation
└── assets/                # Images & icons
```

## Onboarding Flow

1. **Welcome** - Introduction and value proposition
2. **Select Traits** - Choose up to 3 core traits
3. **Quiz** - 10 questions to determine avatar archetype
4. **Avatar Result** - Reveal matched archetype with description
5. **Plan Preview** - 8-week progression overview
6. **Permissions** - Notifications and health data
7. **Start** - Begin first task

## Avatar Archetypes

1. **The Scholar** - Knowledge and continuous learning
2. **The Warrior** - Discipline and physical prowess
3. **The Sage** - Mindfulness and wisdom
4. **The Builder** - Productivity and creation
5. **The Monk** - Focus and minimalism
6. **The Leader** - Confidence and influence
7. **The Phoenix** - Resilience and transformation
8. **The Artist** - Creativity and expression
9. **The Explorer** - Growth and adventure
10. **The Guardian** - Wellbeing and balance

## Development

```bash
# Run type checking
npx tsc --noEmit

# Run linting
npx eslint .

# Build for production
npx expo build:ios
```

## License

MIT