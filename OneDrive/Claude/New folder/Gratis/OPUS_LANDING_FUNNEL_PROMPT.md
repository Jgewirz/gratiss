# Opus Build Prompt: LevelUp Landing Pages & Onboarding Funnel

## Project Context

You are building the **landing pages and onboarding funnel** for **LevelUp**, a gamified self-improvement app that transforms personal development into a video game experience. Users complete daily habit-building tasks to "level up" their avatar from 0% to 100% potential over 8 weeks.

This is a **dual-platform implementation**:
- **Web**: Next.js 14 (App Router, TypeScript, Tailwind CSS, shadcn/ui)
- **Mobile**: Expo/React Native (TypeScript, NativeWind)

## Required Reading

Before starting, thoroughly read these two documents in the repository:

1. **`CLAUDE.md`** - Technical architecture, database schema, API structure, development commands, and implementation constraints
2. **`Onboarding Pipeline for a Gamified Self-.sty`** - Complete 6-step onboarding flow, scientific foundations, 10 avatar archetypes, gamification psychology, and UX design principles

## Your Mission

Build a **conversion-optimized landing page funnel** and **complete onboarding pipeline** that:

1. Captures visitors and converts them to sign-ups
2. Guides new users through the 6-step onboarding flow (Web: 9 steps with stakes, Mobile: 7 steps with avatar quiz)
3. Immediately engages users with their first task completion
4. Implements the scientific habit-formation principles from the onboarding document

## Landing Page Requirements

### Public Landing Page (`app/page.tsx` or `/landing`)

**Structure:**
```
Hero Section
├── Compelling headline: "Transform Your Life Into A Video Game"
├── Subheadline: Scientific-backed habit formation meets RPG progression
├── Primary CTA: "Start Your Journey" (leads to onboarding)
├── Secondary CTA: "Watch How It Works" (video/demo)
└── Hero visual: Avatar transformation (0% → 100% potential)

Social Proof Section
├── User testimonials with avatars and level badges
├── Stats: "X users building habits", "Y total XP earned globally"
└── Trust indicators: "Research-backed methods", "Privacy-first"

How It Works (3-Step Process)
├── 1. Choose Your Focus (select up to 3 traits)
├── 2. Match Your Avatar (10 unique archetypes)
└── 3. Complete Daily Missions (progressive 8-week plan)

Avatar Showcase
├── Grid of 10 avatar archetypes with hover states
├── Brief descriptions of each (Stoic Monk, Charismatic Agent, etc.)
└── "Find your match" CTA

Science Section
├── "Backed by Research" headline
├── Key stats: "66 days to form a habit", "2-month transformation"
├── Citations to studies (mindfulness, willpower, gamification)
└── Visual timeline: Week 1 (beginner) → Week 8 (advanced)

Features Grid
├── Daily Missions (progressive difficulty)
├── XP & Leveling (exponential growth curve)
├── Evidence System (photo, timer, check-ins)
├── Stakes (optional $1-$100/day commitment - Web only)
├── Party System (social accountability)
└── Reward Store (avatar customization)

Pricing/Commitment (Web)
├── Free core experience
├── Optional stakes for accountability ($1-$100/day)
└── Premium features TBD

Final CTA Section
├── Strong call-to-action
├── Low-friction signup (email + password OR social OAuth)
└── "No credit card required" / "Free to start"
```

**Design Principles:**
- **Mobile-first responsive design** (Next.js for web, but mobile users will access via mobile browser initially)
- **Fast loading** (<2s FCP, optimized images, lazy loading)
- **Accessibility** (WCAG 2.1 AA compliant, semantic HTML, keyboard navigation)
- **Conversion optimization** (clear CTAs, minimal friction, urgency/scarcity if appropriate)
- **Gamified aesthetics** (vibrant colors, progress bars, RPG-inspired visuals, but not childish)

**Technical Stack:**
- Next.js 14 App Router
- Tailwind CSS + shadcn/ui components
- Framer Motion for animations (avatar transitions, XP bars)
- Next.js Image for optimized hero images
- TypeScript strict mode

## Onboarding Funnel Requirements

### Web App (9 Steps)

Implement these pages in `app/(onboarding)/` group route:

**Step 1: Welcome (`/welcome`)**
- Hero welcome message
- Brief video/animation showing app concept
- "Let's Begin" CTA
- Exit option (returns to landing page)

**Step 2: Auth (`/auth`)**
- Email/password sign-up form (NextAuth.js integration ready)
- OAuth providers (Google, Facebook placeholders)
- Zod validation for email/password
- Account creation via API endpoint
- Auto-advance to Step 3 on success

**Step 3: Trait Selection (`/avatar` or `/traits`)**
- Display 8-10 trait options with icons:
  - Mindfulness (calm, present, reduce stress)
  - Self-Awareness (understand emotions, personal growth)
  - Productivity (time management, efficiency)
  - Focus (concentration, avoid distractions)
  - Discipline (self-control, consistent habits)
  - Confidence (assertiveness, self-assuredness)
  - Resilience (mental toughness, bounce back)
  - Creativity (imaginative thinking, innovation)
- **Hard limit: Select up to 3 traits** (enforced in UI with shake animation at 4th selection)
- Each trait shows brief benefit description
- Visual feedback on selected traits (highlighted, checkmark)
- Store selections in Zustand onboarding store
- Advance to Step 4

**Step 4: Goals (`/goals`)**
- Goal builder form (add multiple goals)
- Each goal: Title, Category (dropdown), Cadence (daily/weekly/monthly), Target (optional number + unit)
- Zod validation via `lib/validators/goal.ts`
- Preview of how goals translate to daily tasks
- Store in onboarding store
- Advance to Step 5

**Step 5: Stakes (`/stakes`)** - Web Only
- Explanation of financial accountability concept
- Amount selector: $1-$100/day (slider or input)
- Model selector: Flat (same amount daily) vs Escalating (increases on failures)
- Destination selector: Charity, Anti-charity, Friend (with email input)
- Visual representation of stakes math
- "Skip for now" option (can add later)
- Zod validation via `lib/validators/stake.ts`
- Store in onboarding store
- Advance to Step 6

**Step 6: Evidence (`/evidence`)**
- Explain 3 evidence modes:
  - Self-report (honor system, checkmark)
  - Photo proof (camera/gallery upload)
  - Timer (time-based tracking)
- Select default preference (can be task-specific later)
- Privacy explanation for photos (EXIF stripped, local storage)
- Store preference in onboarding store
- Advance to Step 7

**Step 7: Permissions (`/permissions`)**
- Toggle for push notifications
- Toggle for health data sync (future integration)
- Explanation of each permission and benefits
- Request browser notification permission (web)
- Store in onboarding store
- Advance to Step 8

**Step 8: Party (`/party`)**
- Invite friends via email or share code
- Create party name (optional)
- Or "Skip, I'll do this solo" option
- Explanation of party benefits (accountability, shared progress)
- Store invites in onboarding store
- Advance to Step 9

**Step 9: Summary (`/summary`)**
- Review all onboarding selections:
  - Selected traits (with icons)
  - Goals list
  - Stakes commitment (if any)
  - Evidence mode
  - Party invites (if any)
- "Confirm & Start" CTA
- "Go back to edit" option
- On confirm: POST to `/api/onboarding` with full state
- Redirect to dashboard with first task

### Mobile App (7 Steps) - Expo/React Native

Implement in `app/(onboarding)/` with Expo Router:

**Step 1: Welcome (`/welcome`)**
- Similar to web but mobile-optimized
- Animated avatar transition

**Step 2: Trait Selection (`/select-traits`)**
- Same trait options as web
- Touch-optimized grid layout
- Hard 3-trait limit with haptic feedback
- Smooth animations on selection

**Step 3: Personality Quiz (`/quiz`)**
- 10-question quiz based on onboarding document
- Questions assess:
  - Current habits (meditation frequency, routine preferences)
  - Challenges (focus, calm, procrastination)
  - Motivation style (mentor vs action hero)
  - Lifestyle (structured vs spontaneous)
- Progress indicator (1/10, 2/10...)
- Store quiz answers in onboarding store
- Advance to Step 4

**Step 4: Avatar Result (`/avatar-result`)**
- Run deterministic avatar matching algorithm (`lib/gamification.ts`)
- Display matched avatar with:
  - Avatar image/illustration
  - Name (e.g., "The Stoic Monk")
  - Description and backstory
  - Primary/secondary traits
  - Role model inspiration
- "Meet Your Guide" narrative
- Customization options (male/female variant, minor cosmetics)
- Store avatar in onboarding store
- Advance to Step 5

**Step 5: Plan Preview (`/plan-preview`)**
- Show 8-week progression overview:
  - Week 1: 15-25 min/day (beginner tasks)
  - Week 8: 45-60 min/day (advanced challenges)
  - Week 6: Micro-deload visualization
- Sample tasks for Week 1
- XP progression chart (0 → 1000 XP)
- "I'm ready!" CTA
- Advance to Step 6

**Step 6: Permissions (`/permissions`)**
- Request iOS notifications permission
- Optional: Health data (HealthKit) access
- Camera/photo library access (for evidence)
- Explanation of each
- Advance to Step 7

**Step 7: Start (`/start`)**
- Final summary screen
- "Your journey begins now" message
- Show first day's tasks (3 tasks max)
- "Complete First Task" CTA
- Upon task completion: Award first XP, show progress
- Redirect to main dashboard

## Shared Components to Build

Create reusable components in `components/onboarding/`:

1. **`ProgressHeader.tsx`**
   - Shows step indicator (1/9 or 1/7)
   - Progress bar visualization
   - Back button (navigates to previous step)

2. **`StepFooter.tsx`**
   - Primary CTA button ("Next", "Continue", "Confirm")
   - Secondary action ("Skip", "Back")
   - Disabled state when validation fails

3. **`TraitCard.tsx`**
   - Display trait with icon, name, description
   - Selected state styling
   - Click/tap handler
   - Hover/focus states (web)

4. **`AvatarShowcase.tsx`** (Mobile)
   - Large avatar illustration
   - Name and description
   - Customization controls
   - Animation on reveal

5. **`TaskPreviewCard.tsx`**
   - Show sample task with difficulty indicator
   - XP reward display
   - Evidence mode icon
   - Duration estimate

6. **`ValidationFeedback.tsx`**
   - Error messages for form validation
   - Success indicators
   - Inline validation states

7. **`QuizQuestion.tsx`** (Mobile)
   - Question text
   - Multiple choice options (2-4 per question)
   - Selected state
   - Progress indicator integration

## State Management (Zustand)

Enhance existing `store/onboarding.ts`:

```typescript
interface OnboardingState {
  // Auth
  userId: string | null;
  email: string | null;

  // Trait Selection
  selectedTraits: TraitKey[]; // Max 3

  // Quiz (Mobile)
  quizAnswers: QuizAnswer[];

  // Avatar (Mobile)
  matchedAvatar: Avatar | null;
  avatarCustomization: AvatarCustomization;

  // Goals (Web)
  goals: Goal[];

  // Stakes (Web)
  stakesEnabled: boolean;
  stakeAmount: number; // cents
  stakeModel: 'flat' | 'escalating';
  stakeDestination: 'charity' | 'antiCharity' | 'friend';
  stakeRecipientEmail?: string;

  // Evidence
  preferredEvidenceMode: 'check' | 'timer' | 'photo';

  // Permissions
  notificationsEnabled: boolean;
  healthSyncEnabled: boolean;

  // Party
  partyName?: string;
  partyInvites: string[]; // emails

  // Navigation
  currentStep: number;
  completedSteps: number[];

  // Actions
  setSelectedTraits: (traits: TraitKey[]) => void;
  addQuizAnswer: (answer: QuizAnswer) => void;
  setMatchedAvatar: (avatar: Avatar) => void;
  addGoal: (goal: Goal) => void;
  removeGoal: (goalId: string) => void;
  setStakes: (stakes: StakesConfig) => void;
  setEvidenceMode: (mode: EvidenceMode) => void;
  setPermissions: (permissions: Permissions) => void;
  addPartyInvite: (email: string) => void;
  nextStep: () => void;
  prevStep: () => void;
  reset: () => void;
  submitOnboarding: () => Promise<void>;
}
```

Persist state with Zustand middleware (localStorage for web, AsyncStorage for mobile).

## API Endpoints to Implement

Create in `app/api/`:

**`POST /api/auth/register`**
- Input: `{ email, password, name }`
- Output: `{ userId, token, refreshToken }`
- Creates user in database
- Returns JWT for session

**`POST /api/onboarding`**
- Input: Complete onboarding state (from Zustand store)
- Output: `{ success, userId, dashboardUrl }`
- Creates user_profile record
- Generates Week 1 tasks
- Stores avatar, traits, goals, stakes configuration
- Idempotent (can be called multiple times)

**`GET /api/onboarding`**
- Check if user has completed onboarding
- Output: `{ completed: boolean, step?: number }`
- Used to redirect returning users

## Database Operations

Use functions from `lib/db.ts`:

```typescript
// Insert user profile after onboarding
await insert<UserProfile>('user_profiles', {
  user_id: userId,
  avatar_id: state.matchedAvatar.id,
  avatar_name: state.matchedAvatar.name,
  selected_traits: state.selectedTraits,
  quiz_answers: state.quizAnswers, // JSONB
  trait_scores: computedScores, // JSONB
  total_xp: 0,
  current_level: 1,
  current_streak: 0
});

// Generate initial tasks
const weeklyPlan = generateWeeklyPlan(state.matchedAvatar, state.selectedTraits, 1);
for (const task of weeklyPlan) {
  await insert<Task>('tasks', {
    user_id: userId,
    title: task.title,
    difficulty: task.difficulty,
    xp_reward: task.xpReward,
    week_number: 1,
    scheduled_date: task.date,
    // ... other fields
  });
}

// Create stakes record (if enabled)
if (state.stakesEnabled) {
  await insert<Stake>('stakes', {
    user_id: userId,
    amount_cents: state.stakeAmount,
    model: state.stakeModel,
    destination: state.stakeDestination,
    active: true
  });
}
```

## Validation Schemas

Use existing Zod schemas in `lib/validators/`:

**Trait Selection:**
```typescript
const traitSelectionSchema = z.object({
  selectedTraits: z.array(z.enum([
    'mindfulness', 'selfAwareness', 'productivity',
    'focus', 'discipline', 'confidence', 'resilience', 'creativity'
  ])).min(1).max(3)
});
```

**Goal:**
```typescript
// Already exists in lib/validators/goal.ts
const goalSchema = z.object({
  title: z.string().min(1).max(255),
  category: z.enum(['health', 'learning', 'work', 'relationships', 'habits']),
  cadence: z.enum(['daily', 'weekly', 'monthly']),
  target: z.number().int().positive().optional(),
  unit: z.string().max(50).optional()
});
```

**Stakes:**
```typescript
// Already exists in lib/validators/stake.ts
const stakeSchema = z.object({
  amount: z.number().min(1).max(100),
  model: z.enum(['flat', 'escalating']),
  destination: z.enum(['charity', 'antiCharity', 'friend']),
  recipientEmail: z.string().email().optional()
});
```

## Avatar Matching Algorithm (Mobile)

Implement in `lib/gamification.ts`:

```typescript
/**
 * Deterministic avatar matching algorithm
 * Inputs: trait scores (normalized 0-1), selected traits
 * Output: Best-matching avatar from 10 archetypes
 */
export function computeAvatarMatch(
  traitScores: Record<TraitKey, number>,
  selectedTraits: TraitKey[]
): { avatarId: string; score: number; reasoning: string } {

  const SELECTED_TRAIT_BONUS = 1.5;

  // Normalize all trait scores to 0-1
  const normalizedScores = normalizeTraitScores(traitScores);

  // Apply bonus to selected traits
  selectedTraits.forEach(trait => {
    normalizedScores[trait] *= SELECTED_TRAIT_BONUS;
  });

  // Calculate match score for each avatar
  const avatarScores = AVATAR_ARCHETYPES.map(avatar => {
    const primaryScore = normalizedScores[avatar.primaryTrait] || 0;
    const secondaryScore = normalizedScores[avatar.secondaryTrait] || 0;
    const totalScore = primaryScore * 0.6 + secondaryScore * 0.4;

    // Tie-breaking: overlap count with selected traits
    const overlapCount = selectedTraits.filter(t =>
      t === avatar.primaryTrait || t === avatar.secondaryTrait
    ).length;

    return {
      avatar,
      score: totalScore,
      overlapCount,
      primaryScore
    };
  });

  // Sort by score, then overlap, then primary score, then lexicographic ID
  avatarScores.sort((a, b) => {
    if (Math.abs(a.score - b.score) > 0.01) return b.score - a.score;
    if (a.overlapCount !== b.overlapCount) return b.overlapCount - a.overlapCount;
    if (Math.abs(a.primaryScore - b.primaryScore) > 0.01) return b.primaryScore - a.primaryScore;
    return a.avatar.id.localeCompare(b.avatar.id);
  });

  const bestMatch = avatarScores[0];

  return {
    avatarId: bestMatch.avatar.id,
    score: bestMatch.score,
    reasoning: `Matched based on ${bestMatch.avatar.primaryTrait} (primary) and ${bestMatch.avatar.secondaryTrait} (secondary) traits`
  };
}
```

## 10 Avatar Archetypes Data

Define in `data/avatars.ts`:

```typescript
export const AVATAR_ARCHETYPES: Avatar[] = [
  {
    id: 'zen-guru',
    name: 'The Zen Guru',
    description: 'A calm, wise mentor figure who remains present and centered.',
    primaryTrait: 'mindfulness',
    secondaryTrait: 'selfAwareness',
    backstory: 'Embodies inner peace, reflection, and emotional balance. Inspired by mindfulness teachers and peaceful warriors.',
    tagline: 'Calm is contagious',
    inspirations: ['Thich Nhat Hanh', 'Buddhist monks']
  },
  {
    id: 'stoic-monk',
    name: 'The Stoic Monk',
    description: 'A serene yet iron-willed character who approaches life with calm rigor.',
    primaryTrait: 'mindfulness',
    secondaryTrait: 'discipline',
    backstory: 'Combines serenity with self-control. Inspired by Shaolin monks and stoic philosophers.',
    tagline: 'Stillness in motion',
    inspirations: ['Marcus Aurelius', 'Shaolin masters']
  },
  {
    id: 'focused-strategist',
    name: 'The Focused Strategist',
    description: 'A master planner who is laser-focused and organized.',
    primaryTrait: 'focus',
    secondaryTrait: 'productivity',
    backstory: 'Excels at eliminating distractions and executing plans efficiently. Like a brilliant general or project manager.',
    tagline: 'Every move is calculated',
    inspirations: ['Chess grandmasters', 'Military strategists']
  },
  {
    id: 'taskmaster',
    name: 'The Taskmaster',
    description: 'A results-driven, persistent character who excels at building routines and hitting goals.',
    primaryTrait: 'productivity',
    secondaryTrait: 'discipline',
    backstory: 'The ultimate executor. Like a strict but effective coach who gets results.',
    tagline: 'Progress over perfection',
    inspirations: ['Elite coaches', 'Navy SEALs']
  },
  {
    id: 'charismatic-agent',
    name: 'The Charismatic Agent',
    description: 'A suave, confident persona inspired by James Bond – poised under pressure, physically and mentally disciplined.',
    primaryTrait: 'confidence',
    secondaryTrait: 'discipline',
    backstory: 'Embodies assertiveness, courage, and reliability. Always prepared, never rattled.',
    tagline: 'Nothing rattles the Agent\'s cool',
    inspirations: ['James Bond', 'Secret agents']
  },
  {
    id: 'creative-sage',
    name: 'The Creative Sage',
    description: 'An imaginative thinker with a reflective mind who pairs creative exploration with introspection.',
    primaryTrait: 'creativity',
    secondaryTrait: 'selfAwareness',
    backstory: 'Seeks personal insight through creative expression. Like a wise artist or innovator.',
    tagline: 'Creation through reflection',
    inspirations: ['Leonardo da Vinci', 'Innovative artists']
  },
  {
    id: 'resilient-warrior',
    name: 'The Resilient Warrior',
    description: 'A courageous fighter archetype who bounces back from setbacks, showing grit and bravery.',
    primaryTrait: 'confidence',
    secondaryTrait: 'resilience',
    backstory: 'Focused on mental toughness and physical fitness. Like a determined athlete or soldier.',
    tagline: 'Defeat is temporary',
    inspirations: ['Olympic athletes', 'Military heroes']
  },
  {
    id: 'balanced-optimizer',
    name: 'The Balanced Optimizer',
    description: 'A balanced persona who emphasizes both efficiency and well-being.',
    primaryTrait: 'mindfulness',
    secondaryTrait: 'productivity',
    backstory: 'Achieves high productivity without burnout by staying mindful. Like a meditating CEO.',
    tagline: 'Balance is the ultimate efficiency',
    inspirations: ['Tim Ferriss', 'Mindful leaders']
  },
  {
    id: 'social-navigator',
    name: 'The Social Navigator',
    description: 'A charismatic communicator who is empathetic, self-assured, and great at building relationships.',
    primaryTrait: 'selfAwareness',
    secondaryTrait: 'confidence',
    backstory: 'Excels in social contexts with emotional intelligence. Like a friendly leader or diplomat.',
    tagline: 'Connection is strength',
    inspirations: ['Dale Carnegie', 'Great diplomats']
  },
  {
    id: 'diligent-scholar',
    name: 'The Diligent Scholar',
    description: 'A studious, growth-oriented character who relentlessly hones skills every day.',
    primaryTrait: 'focus',
    secondaryTrait: 'discipline',
    backstory: 'Dedicated to continuous learning and mastery. Like a martial arts student or academic.',
    tagline: 'Mastery through practice',
    inspirations: ['Bruce Lee', 'Scholar monks']
  }
];
```

## Design & UX Guidelines

**Landing Page:**
- Hero section must be **above the fold** with clear value proposition
- Use **action-oriented copy**: "Transform", "Level Up", "Unlock", "Achieve"
- **Social proof** early (testimonials, user count, success stories)
- **Scarcity/urgency** if appropriate ("Join 10,000+ users already leveling up")
- **Visual hierarchy**: Primary CTA should be most prominent element
- **Mobile-first**: Test on 375px width minimum

**Onboarding Flow:**
- **Progress indicator** always visible (user knows where they are)
- **One primary action per screen** (don't overwhelm)
- **Immediate feedback** on interactions (form validation, selections)
- **Escape hatches** (back button, skip options where appropriate)
- **Celebration moments** (avatar reveal, first XP earned)
- **Fast transitions** (<300ms animations, instant navigation)

**Accessibility:**
- Semantic HTML5 (`<header>`, `<nav>`, `<main>`, `<section>`)
- ARIA labels on all interactive elements
- Keyboard navigation support (Tab, Enter, Esc)
- Focus indicators visible
- Color contrast ratio ≥4.5:1 (WCAG AA)
- Touch targets ≥44x44px (mobile)

**Performance:**
- Lighthouse score >90 (Performance, Accessibility, Best Practices)
- Next.js Image component for all images
- Lazy load below-the-fold content
- Optimize Tailwind (purge unused classes)
- Minimize bundle size (<200KB JS for landing page)

## Conversion Tracking

Implement analytics events:

```typescript
// Landing page
trackEvent('landing_page_view');
trackEvent('cta_clicked', { location: 'hero' | 'footer' | 'features' });
trackEvent('avatar_hovered', { avatarId });
trackEvent('video_played');

// Onboarding
trackEvent('onboarding_started');
trackEvent('onboarding_step_completed', { step: number });
trackEvent('trait_selected', { trait: TraitKey });
trackEvent('quiz_completed', { avatarMatched: string });
trackEvent('stakes_enabled', { amount: number });
trackEvent('onboarding_completed', { duration: number });

// Drop-off points
trackEvent('onboarding_abandoned', { lastStep: number });
```

## Testing Requirements

**Unit Tests:**
- Trait selection validation (max 3)
- Avatar matching algorithm (deterministic)
- Zod schema validation (goals, stakes, evidence)
- Onboarding state management (Zustand actions)

**Integration Tests:**
- Complete onboarding flow (all 9 steps web, 7 steps mobile)
- API endpoint responses (auth, onboarding submission)
- Database record creation (user, profile, tasks)

**E2E Tests:**
- User signs up → completes onboarding → sees dashboard
- User abandons onboarding → returns → continues from last step
- User completes first task → earns first XP

## Success Metrics

Track these KPIs:

1. **Landing Page Conversion Rate**: Visitors → Sign-ups (Target: >5%)
2. **Onboarding Completion Rate**: Sign-ups → Completed onboarding (Target: >60%)
3. **Time to First Task**: Onboarding complete → First task done (Target: <5 minutes)
4. **Step Drop-off**: Identify which onboarding step loses most users
5. **Avatar Distribution**: Are all 10 avatars being matched relatively evenly?

## Deliverables Checklist

- [ ] Landing page (`app/page.tsx` or `app/landing/page.tsx`)
- [ ] Web onboarding pages (9 steps in `app/(onboarding)/`)
- [ ] Mobile onboarding screens (7 steps in `levelup-ios/app/(onboarding)/`)
- [ ] Shared onboarding components (`components/onboarding/`)
- [ ] Enhanced Zustand onboarding store (`store/onboarding.ts`)
- [ ] API routes (`/api/auth/register`, `/api/onboarding`)
- [ ] Avatar matching algorithm (`lib/gamification.ts`)
- [ ] 10 avatar archetypes data (`data/avatars.ts`)
- [ ] Validation schemas (leverage existing `lib/validators/`)
- [ ] Database operations (use `lib/db.ts` functions)
- [ ] Analytics tracking events
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility audit passed
- [ ] Unit + integration tests
- [ ] Documentation (onboarding flow diagram, component docs)

## Next Steps After Completion

Once landing and onboarding are complete:
1. User testing with 10-20 beta users
2. Analytics review (drop-off points, conversion rates)
3. A/B testing variations (CTA copy, hero images, onboarding order)
4. Build main dashboard and daily task interface
5. Implement XP/leveling system
6. Add evidence submission flows
7. Build reward store and achievement system

## Questions to Clarify Before Starting

1. Do we have brand assets (logo, colors, fonts) or should I use placeholder/generic design?
2. Should the landing page be separate (`/landing`) or replace root (`/`)?
3. OAuth providers: Just Google/Facebook or include Apple, GitHub, Twitter?
4. Avatar illustrations: Do we have assets or should I use placeholders (emojis, silhouettes)?
5. Email service for invites: SendGrid, AWS SES, Resend, or placeholder?
6. Analytics service: Mixpanel, Amplitude, PostHog, or custom?
7. Stripe integration: Test mode only for now or prepare for production?
8. Mobile app: Build in parallel or web-first then port?

## Your Approach

1. **Read both documents thoroughly** (`CLAUDE.md` + onboarding pipeline)
2. **Start with landing page** (highest ROI, sets conversion foundation)
3. **Build web onboarding flow** (9 steps, easier to test in browser)
4. **Port to mobile** (7 steps, leverage shared logic)
5. **Test end-to-end** (sign up → complete onboarding → first task)
6. **Iterate based on metrics** (optimize drop-off points)

**Prioritization:**
- Landing page hero + CTA (Day 1)
- Auth + first 3 onboarding steps (Day 2)
- Complete web onboarding (Day 3-4)
- Mobile onboarding with avatar matching (Day 5-6)
- Polish, testing, optimization (Day 7)

Now begin building! Start with the landing page hero section, and work through each component systematically. Ask for clarification if any requirements are unclear, but err on the side of building and iterating quickly.

**Good luck! You're building the entry point to a life-changing experience. Make it compelling, frictionless, and scientifically grounded. Transform visitors into committed users ready to unlock their full potential.**
