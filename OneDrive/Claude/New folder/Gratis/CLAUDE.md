# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This monorepo contains two parallel implementations of **LevelUp**, a gamified self-improvement app that transforms personal development into a video game experience:

- **`levelup/`** - Next.js 14 web application (TypeScript, React, Tailwind)
- **`levelup-ios/`** - Expo/React Native mobile app (TypeScript, NativeWind)


Both apps share the same core concept but diverge in implementation:
- **Web**: 9-step onboarding with optional financial stakes ($1-$100/day)
- **iOS**: 7-step onboarding with personality quiz matching to 10 avatar archetypes, 8-week progression system

## Development Commands

### Web App (levelup/)
```bash
# Install dependencies
npm install
# or
pnpm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Test database connection
node test-neon-connection.js
```

### iOS/Mobile App (levelup-ios/)
```bash
# Install dependencies
pnpm install

# Run on iOS simulator
npx expo run:ios

# Run on Android emulator
npx expo run:android

# Start Expo dev server
pnpm start

# Type checking
npx tsc --noEmit

# Run tests
pnpm test
jest --watch  # Watch mode for development

# Build for production (requires EAS CLI)
eas build --platform ios
eas build --platform android
```

## Architecture Overview

### Web App Architecture

**Framework**: Next.js 14 with App Router and Server Components

**State Management**:
- Zustand stores in `store/onboarding.ts` for onboarding flow state
- Client-side state persisted via Zustand middleware

**Database Layer** (`lib/db.ts`):
- Dual-mode connection handling:
  - **Node.js runtime**: PostgreSQL connection pool (pg)
  - **Edge runtime**: Neon serverless driver over HTTP
- Type-safe query builders: `insert()`, `update()`, `findById()`, `deleteById()`
- Transaction support with automatic rollback
- Connection pooling configuration:
  - Max 20 clients
  - 30s idle timeout
  - 2s connection timeout
  - Prepared statements disabled for Neon optimization

**Routing Structure**:
```
app/
├── (onboarding)/          # 9-step onboarding group route
│   ├── welcome/           # Step 1: Introduction
│   ├── auth/              # Step 2: Authentication
│   ├── avatar/            # Step 3: Character creation
│   ├── goals/             # Step 4: Goal setting
│   ├── stakes/            # Step 5: Financial accountability
│   ├── evidence/          # Step 6: Proof method selection
│   ├── permissions/       # Step 7: Notifications/integrations
│   ├── party/             # Step 8: Friend invites
│   └── summary/           # Step 9: Review & confirm
├── api/
│   ├── auth/route.ts      # Authentication endpoints
│   └── onboarding/route.ts # Onboarding data submission
└── app/page.tsx           # Main dashboard (post-onboarding)
```

### Mobile App Architecture

**Framework**: Expo (React Native) with Expo Router file-based routing

**State Management**:
- Two distinct Zustand stores:
  - `store/onboarding.ts`: Ephemeral onboarding state with AsyncStorage persistence
  - `store/user.ts`: Long-term user profile and game progress

**Core Systems**:
- **Avatar Matching** (`lib/gamification.ts`): Deterministic algorithm using normalized trait scores with +1.5 weight for selected traits, tie-breaking cascade for consistency
- **Task Progression** (`data/progression.ts`): Wave-linear progression (Week 1: 15-25min → Week 8: 45-60min) with Week 6 micro-deload, 5 active days/week, max 3 tasks/day
- **XP System**: Fixed rewards (Easy: 10 XP, Medium: 20 XP, Hard: 30 XP), exponential level formula: `100 * 1.2^(level-1)`

**Routing Structure**:
```
app/
├── (onboarding)/          # 7-step onboarding group route
│   ├── welcome/           # Step 1: Introduction
│   ├── select-traits/     # Step 2: Choose 3 traits (hard limit)
│   ├── quiz/              # Step 3: Personality quiz
│   ├── avatar-result/     # Step 4: Matched avatar reveal
│   ├── plan-preview/      # Step 5: 8-week plan preview
│   ├── permissions/       # Step 6: Notifications/health data
│   └── start/             # Step 7: Begin journey
└── index.tsx              # Entry point with onboarding redirect
```

## Database Schema (Neon PostgreSQL)

### Core Tables
- **users**: Authentication, timezone, onboarding status
- **user_profiles**: Avatar data, XP/level, streaks, trait scores (JSONB)
- **tasks**: Daily challenges with difficulty, XP rewards, evidence mode, week number
- **goals**: User-defined objectives with cadence (daily/weekly/monthly)
- **evidence**: Photo URLs, timer durations, validation status
- **stakes**: Financial accountability ($1-$100 range), Stripe integration
- **parties**: Social features with join codes
- **party_members**: Group accountability tracking

### Critical Indexes
```sql
idx_tasks_user_date ON tasks(user_id, scheduled_date)
idx_tasks_completed ON tasks(completed)
idx_evidence_task ON evidence(task_id)
idx_stakes_user_active ON stakes(user_id, active)
```

### Connection Details
Database uses Neon PostgreSQL cloud service with:
- SSL required (`PGSSLMODE=require`)
- Connection pooling enabled
- Row-level security policies (RLS) for multi-tenant isolation

## Key Technical Constraints

### Web App
- **Stakes Range**: $1-$100/day enforced in validation and database CHECK constraints
- **Evidence Modes**: `self-report`, `photo`, `integration` (HealthKit, Strava, etc.)
- **Onboarding Persistence**: All steps stored in Zustand with AsyncStorage backup
- **API Validation**: Zod schemas in `lib/validators/` validate all user inputs server-side

### Mobile App
- **Trait Selection**: Hard limit of 3 traits enforced in UI (`lib/validators.ts`) with shake animation feedback
- **Avatar Matching**: Deterministic - identical inputs always produce same avatar (critical for user trust)
- **Photo Evidence**: Week-gated to Week 5+ only, EXIF stripped, local storage only
- **Accessibility**: All interactive elements require `accessibilityLabel` and `accessibilityRole`, 44x44px minimum touch targets
- **Copy Management**: All user-facing strings centralized in `lib/copy.ts` - no inline strings

### Shared Constraints
- **Time Zone Handling**: All timestamps use `TIMESTAMPTZ` with user timezone stored separately
- **Type Safety**: TypeScript strict mode enabled, no `any` without runtime guards
- **Performance**: Slow queries (>100ms) logged in development for optimization

## Validation & Testing

### Web App Validation
Zod schemas in `lib/validators/`:
- `goal.ts`: Goal title, category, cadence, target validation
- `stake.ts`: Amount ($1-$100), model (flat/escalating), destination validation
- `evidence.ts`: Evidence mode enum validation
- `onboarding.ts`: Complete onboarding data validation

### Mobile App Testing Matrix
Critical test coverage in `__tests__/onboarding.spec.ts`:
- ✅ `matching_deterministic_100x`: Avatar matching consistency (100 iterations)
- ✅ `matching_tiebreak_cascade`: Tie-breaker order verification
- ✅ `traitCap_enforced`: Max 3 traits, min 1 trait enforcement
- ✅ `progression_bounds_topTrait_daily_taskCap`: Week progression constraints
- ✅ `evidence_gating_week5_plus`: Photo evidence gating to Week 5+
- ✅ `xp_progress_and_gate_logic`: XP calculations and progress updates
- ✅ `persistence_and_routing_basic`: AsyncStorage and navigation flows

## MCP (Model Context Protocol) Integration

### Configured MCPs
1. **postgres-neon**: Neon PostgreSQL cloud database access
2. **figma-developer-mcp**: Design asset extraction and sync
3. **filesystem**: Local file operations
4. **ide**: VS Code diagnostics and code execution

### Database Operations via MCP
```typescript
// Query database through postgres-neon MCP
SELECT * FROM users WHERE onboarding_completed = true;

// Check database health
SELECT COUNT(*) FROM tasks WHERE completed_at > NOW() - INTERVAL '7 days';

// Insert test data
INSERT INTO user_profiles (user_id, avatar_id, selected_traits)
VALUES ('test-uuid', 'warrior', ARRAY['discipline', 'focus', 'resilience']);
```

### Environment Variables
Located in `.env.real` (never commit):
```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
PGHOST=ep-xxx-xxx.us-east-1.aws.neon.tech
PGDATABASE=levelup_db
PGUSER=neondb_owner
PGPASSWORD=<secure-password>
PGSSLMODE=require

# Auth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<generate-with-openssl>

# Payments (Web only)
STRIPE_SECRET_KEY=<stripe-key>
STRIPE_WEBHOOK_SECRET=<stripe-webhook>
```

## Critical Implementation Details

### Web App: Database Transaction Pattern
```typescript
import { transaction } from '@/lib/db';

// Use transaction wrapper for multi-step operations
await transaction(async (client) => {
  await client.query('INSERT INTO users ...');
  await client.query('INSERT INTO user_profiles ...');
  // Automatic rollback on error
});
```

### Mobile App: Deterministic Avatar Matching
```typescript
// lib/gamification.ts
export function computeAvatarMatch(
  traitScores: Record<TraitKey, number>,
  selectedTraits: TraitKey[]
): { avatarId: string; score: number; reasoning: string } {
  // Normalize scores to 0-1 range
  // Apply +1.5 weight to selected traits
  // Tie-break: Score → Overlap Count → Highest Contribution → Lexicographic ID
  // MUST be deterministic - no Math.random() or Date.now() inside
}
```

### Mobile App: Week Progression Formula
```typescript
// data/progression.ts
const WEEK_RANGES = [
  [15, 25], // Week 1: 15-25 min/day (avg 20)
  [20, 30], // Week 2: 20-30 min/day (avg 25)
  [25, 35], // Week 3: 25-35 min/day (avg 30)
  [30, 40], // Week 4: 30-40 min/day (avg 35)
  [35, 45], // Week 5: 35-45 min/day (avg 40)
  [32, 42], // Week 6: 32-42 min/day (avg 37) ← Micro-deload ≤90% of Week 5
  [40, 55], // Week 7: 40-55 min/day (avg 47)
  [45, 60], // Week 8: 45-60 min/day (avg 52)
];
```

### Mobile App: Grace & Stakes Logic
```typescript
// 4-hour grace window: 00:00-03:59 counts as previous day
// Weekly grace: One free miss per week, resets Monday
// Daily charge cap: Max one $1 charge per day

function shouldGateForMiss(state: UserState): boolean {
  return (
    state.stakesEnabled &&
    yesterdayCompletions === 0 && // After grace adjustment
    !state.weeklyGraceUsed &&
    !state.dailyChargeUsedToday
  );
}
```

## Code Organization Principles

### Web App
- **Components**: Organized by feature (`onboarding/`, `ui/`)
- **API Routes**: RESTful with clear POST/GET separation
- **Database Queries**: Centralized in `lib/db.ts` with type-safe builders
- **Validation**: Server-side Zod schemas prevent client bypass

### Mobile App
- **Pure Functions**: All scoring/matching/progression logic is side-effect-free
- **Determinism**: Critical algorithms include self-test functions
- **Copy Centralization**: All strings in `lib/copy.ts` for easy localization
- **Type Safety**: Discriminated unions for state machines, never use `any`

## Performance Optimization

### Web App
- Use edge runtime (`@neondatabase/serverless`) for API routes when possible
- Connection pooling configured for Neon's architecture
- Slow query logging (>100ms) in development mode
- Database indexes on frequently queried columns

### Mobile App
- NativeWind (Tailwind) classes compiled at build time
- Heavy computations (avatar matching, plan generation) memoized in Zustand stores
- AsyncStorage batching handled automatically by persist middleware
- Images: SVG for avatars, compressed PNG for photos

## Common Gotchas

1. **Database Connections**: Always use `getPool()` in web app, never create new Pool instances
2. **Time Zones**: Store all timestamps as TIMESTAMPTZ, use user's timezone for display
3. **Trait Limit**: Mobile app has hard 3-trait cap with validation in multiple layers
4. **Evidence Gating**: Photo evidence locked until Week 5+ in mobile app
5. **Stakes Range**: $1-$100 enforced via CHECK constraints and Zod validation
6. **Avatar Matching**: Must be deterministic - add tests for any changes
7. **Async Storage**: Mobile app uses wrapper with error handling, never direct AsyncStorage calls

## Documentation References

- Web app README: `levelup/README.md`
- Web app structure: `levelup/STRUCTURE.md`
- Mobile app docs: `levelup-ios/README.md`, `levelup-ios/ARCHITECTURE.md`
- MCP configuration: `LEVELUP_MCP_CONFIGURATION.md`
- Database setup: `NEON_POSTGRESQL_SETUP.md`