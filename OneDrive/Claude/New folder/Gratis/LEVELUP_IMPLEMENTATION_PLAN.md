# LevelUp Landing & Onboarding Implementation Plan

## 🎯 Project Overview

Building a **conversion-optimized landing funnel** and **complete onboarding pipeline** for LevelUp - a gamified self-improvement app that transforms personal development into an RPG experience.

### Key Components
- **Landing Page**: High-conversion public page
- **Web Onboarding**: 9-step flow with financial stakes
- **Mobile Onboarding**: 7-step flow with personality quiz
- **Avatar System**: 10 unique archetypes with trait matching
- **Database**: Neon PostgreSQL (already configured)
- **State Management**: Zustand with persistence

## 📊 Phase 1: Foundation (Day 1-2)

### 1.1 Project Setup & Structure

```bash
# Web (Next.js)
levelup/
├── app/
│   ├── page.tsx                    # Landing page
│   ├── (onboarding)/               # Onboarding group route
│   │   ├── layout.tsx              # Shared onboarding layout
│   │   ├── welcome/page.tsx        # Step 1
│   │   ├── auth/page.tsx           # Step 2
│   │   ├── traits/page.tsx         # Step 3
│   │   ├── goals/page.tsx          # Step 4
│   │   ├── stakes/page.tsx         # Step 5
│   │   ├── evidence/page.tsx       # Step 6
│   │   ├── permissions/page.tsx    # Step 7
│   │   ├── party/page.tsx          # Step 8
│   │   └── summary/page.tsx        # Step 9
│   ├── api/
│   │   ├── auth/
│   │   │   ├── register/route.ts
│   │   │   └── login/route.ts
│   │   └── onboarding/route.ts
│   └── dashboard/page.tsx          # Post-onboarding

# Mobile (Expo/React Native)
levelup-ios/
├── app/
│   ├── (onboarding)/
│   │   ├── _layout.tsx
│   │   ├── welcome.tsx             # Step 1
│   │   ├── select-traits.tsx       # Step 2
│   │   ├── quiz.tsx                # Step 3
│   │   ├── avatar-result.tsx       # Step 4
│   │   ├── plan-preview.tsx        # Step 5
│   │   ├── permissions.tsx         # Step 6
│   │   └── start.tsx               # Step 7
```

### 1.2 Database Schema (Already Created)

```sql
-- Key tables for onboarding:
users                  -- Authentication
user_profiles         -- Avatar, traits, XP
goals                 -- User-defined objectives
tasks                 -- Daily challenges
stakes                -- Financial accountability
parties               -- Social groups
achievements          -- Badges and milestones
```

### 1.3 Install Dependencies

```bash
# Web dependencies
cd levelup
npm install @tanstack/react-query     # Data fetching
npm install framer-motion              # Animations
npm install react-hook-form            # Form handling
npm install @radix-ui/react-*          # UI components
npm install zustand                    # State management
npm install bcryptjs jsonwebtoken      # Auth
npm install mixpanel-browser           # Analytics

# Mobile dependencies
cd levelup-ios
npm install @react-native-async-storage/async-storage
npm install expo-notifications
npm install expo-image-picker
npm install react-native-reanimated
npm install zustand
```

## 📊 Phase 2: Landing Page (Day 2-3)

### 2.1 Landing Page Components

```typescript
// app/page.tsx - Landing Page Structure
import { Hero } from '@/components/landing/Hero'
import { SocialProof } from '@/components/landing/SocialProof'
import { HowItWorks } from '@/components/landing/HowItWorks'
import { AvatarShowcase } from '@/components/landing/AvatarShowcase'
import { ScienceSection } from '@/components/landing/ScienceSection'
import { Features } from '@/components/landing/Features'
import { Pricing } from '@/components/landing/Pricing'
import { FinalCTA } from '@/components/landing/FinalCTA'

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Hero />
      <SocialProof />
      <HowItWorks />
      <AvatarShowcase />
      <ScienceSection />
      <Features />
      <Pricing />
      <FinalCTA />
    </main>
  )
}
```

### 2.2 Hero Section Implementation

```typescript
// components/landing/Hero.tsx
export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 to-blue-600">
      <div className="container mx-auto px-4 text-center text-white">
        <h1 className="text-5xl md:text-7xl font-bold mb-6">
          Transform Your Life Into A Video Game
        </h1>
        <p className="text-xl md:text-2xl mb-8 opacity-90">
          Science-backed habit formation meets RPG progression
        </p>

        <div className="flex gap-4 justify-center">
          <Link href="/onboarding/welcome">
            <Button size="lg" className="text-lg px-8 py-6">
              Start Your Journey →
            </Button>
          </Link>
          <Button variant="outline" size="lg" onClick={playDemo}>
            <Play className="mr-2" /> Watch How It Works
          </Button>
        </div>

        {/* Avatar transformation visual */}
        <div className="mt-12 relative">
          <AvatarProgressAnimation />
        </div>
      </div>
    </section>
  )
}
```

### 2.3 Avatar Showcase with Data

```typescript
// data/avatars.ts
export const AVATAR_ARCHETYPES = [
  {
    id: 'zen-guru',
    name: 'The Zen Guru',
    description: 'A calm, wise mentor figure',
    primaryTrait: 'mindfulness',
    secondaryTrait: 'selfAwareness',
    image: '/avatars/zen-guru.png',
    color: '#6B46C1'
  },
  {
    id: 'stoic-monk',
    name: 'The Stoic Monk',
    description: 'Serene yet iron-willed',
    primaryTrait: 'mindfulness',
    secondaryTrait: 'discipline',
    image: '/avatars/stoic-monk.png',
    color: '#1F2937'
  },
  // ... 8 more avatars
]

// components/landing/AvatarShowcase.tsx
export function AvatarShowcase() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12">
          Meet Your Avatar Guides
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
          {AVATAR_ARCHETYPES.map(avatar => (
            <AvatarCard key={avatar.id} avatar={avatar} />
          ))}
        </div>
      </div>
    </section>
  )
}
```

## 📊 Phase 3: Web Onboarding Flow (Day 3-4)

### 3.1 Zustand Store Setup

```typescript
// store/onboarding.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface OnboardingState {
  // User data
  userId: string | null
  email: string | null

  // Selections
  selectedTraits: TraitKey[]
  goals: Goal[]
  stakesConfig: StakesConfig | null
  evidenceMode: EvidenceMode
  permissions: Permissions
  partyInvites: string[]

  // Navigation
  currentStep: number
  completedSteps: number[]

  // Actions
  setSelectedTraits: (traits: TraitKey[]) => void
  addGoal: (goal: Goal) => void
  setStakes: (config: StakesConfig) => void
  nextStep: () => void
  prevStep: () => void
  submitOnboarding: () => Promise<void>
  reset: () => void
}

export const useOnboarding = create<OnboardingState>()(
  persist(
    (set, get) => ({
      // Initial state
      userId: null,
      email: null,
      selectedTraits: [],
      goals: [],
      stakesConfig: null,
      evidenceMode: 'check',
      permissions: {
        notifications: false,
        healthSync: false
      },
      partyInvites: [],
      currentStep: 1,
      completedSteps: [],

      // Actions
      setSelectedTraits: (traits) => {
        if (traits.length > 3) {
          throw new Error('Maximum 3 traits allowed')
        }
        set({ selectedTraits: traits })
      },

      addGoal: (goal) => set(state => ({
        goals: [...state.goals, goal]
      })),

      setStakes: (config) => set({ stakesConfig: config }),

      nextStep: () => set(state => ({
        currentStep: state.currentStep + 1,
        completedSteps: [...state.completedSteps, state.currentStep]
      })),

      prevStep: () => set(state => ({
        currentStep: Math.max(1, state.currentStep - 1)
      })),

      submitOnboarding: async () => {
        const state = get()

        const response = await fetch('/api/onboarding', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: state.userId,
            selectedTraits: state.selectedTraits,
            goals: state.goals,
            stakesConfig: state.stakesConfig,
            evidenceMode: state.evidenceMode,
            permissions: state.permissions,
            partyInvites: state.partyInvites
          })
        })

        if (!response.ok) throw new Error('Onboarding submission failed')

        const data = await response.json()
        set({ userId: data.userId })

        // Reset and redirect
        get().reset()
        window.location.href = '/dashboard'
      },

      reset: () => set({
        currentStep: 1,
        completedSteps: [],
        selectedTraits: [],
        goals: [],
        stakesConfig: null,
        partyInvites: []
      })
    }),
    {
      name: 'levelup-onboarding',
      partialize: (state) => ({
        currentStep: state.currentStep,
        completedSteps: state.completedSteps,
        selectedTraits: state.selectedTraits,
        goals: state.goals
      })
    }
  )
)
```

### 3.2 Trait Selection Component

```typescript
// app/(onboarding)/traits/page.tsx
'use client'

import { useOnboarding } from '@/store/onboarding'
import { TraitCard } from '@/components/onboarding/TraitCard'
import { TRAITS } from '@/data/traits'

export default function TraitSelectionPage() {
  const { selectedTraits, setSelectedTraits, nextStep } = useOnboarding()

  const handleTraitToggle = (trait: TraitKey) => {
    if (selectedTraits.includes(trait)) {
      setSelectedTraits(selectedTraits.filter(t => t !== trait))
    } else {
      if (selectedTraits.length >= 3) {
        // Trigger shake animation
        return
      }
      setSelectedTraits([...selectedTraits, trait])
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <ProgressHeader step={3} total={9} />

      <main className="flex-1 container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-4">
          Choose Your Focus Areas
        </h1>
        <p className="text-gray-600 mb-8">
          Select up to 3 traits you want to develop (you can change these later)
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {TRAITS.map(trait => (
            <TraitCard
              key={trait.id}
              trait={trait}
              selected={selectedTraits.includes(trait.id)}
              onToggle={() => handleTraitToggle(trait.id)}
            />
          ))}
        </div>

        {selectedTraits.length === 3 && (
          <Alert className="mt-4">
            Maximum 3 traits selected. Deselect one to choose another.
          </Alert>
        )}
      </main>

      <StepFooter
        onNext={nextStep}
        nextDisabled={selectedTraits.length === 0}
        onBack={() => window.history.back()}
      />
    </div>
  )
}
```

### 3.3 API Endpoints

```typescript
// app/api/auth/register/route.ts
import { hash } from 'bcryptjs'
import { sign } from 'jsonwebtoken'
import { query, insert } from '@/lib/db'

export async function POST(request: Request) {
  const { email, password } = await request.json()

  // Validate input
  if (!email || !password) {
    return Response.json(
      { error: 'Email and password required' },
      { status: 400 }
    )
  }

  try {
    // Check if user exists
    const existing = await query(
      'SELECT id FROM users WHERE email = $1',
      [email]
    )

    if (existing.rows.length > 0) {
      return Response.json(
        { error: 'User already exists' },
        { status: 409 }
      )
    }

    // Hash password
    const passwordHash = await hash(password, 10)

    // Create user
    const user = await insert('users', {
      email,
      password_hash: passwordHash,
      created_at: new Date()
    })

    // Generate JWT
    const token = sign(
      { userId: user.id, email },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    )

    return Response.json({
      userId: user.id,
      email,
      token
    })
  } catch (error) {
    console.error('Registration error:', error)
    return Response.json(
      { error: 'Registration failed' },
      { status: 500 }
    )
  }
}
```

## 📊 Phase 4: Mobile Onboarding (Day 4-5)

### 4.1 Personality Quiz Implementation

```typescript
// levelup-ios/app/(onboarding)/quiz.tsx
import { useOnboarding } from '@/store/onboarding'
import { QUIZ_QUESTIONS } from '@/data/quiz'

export default function QuizScreen() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const { addQuizAnswer, nextStep } = useOnboarding()

  const handleAnswer = (value: number) => {
    addQuizAnswer({
      questionId: QUIZ_QUESTIONS[currentQuestion].id,
      value
    })

    if (currentQuestion < QUIZ_QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      // Quiz complete, calculate avatar match
      nextStep()
    }
  }

  const question = QUIZ_QUESTIONS[currentQuestion]

  return (
    <View style={styles.container}>
      <ProgressHeader
        current={currentQuestion + 1}
        total={QUIZ_QUESTIONS.length}
      />

      <View style={styles.content}>
        <Text style={styles.question}>
          {question.text}
        </Text>

        <View style={styles.options}>
          {question.options.map((option, index) => (
            <TouchableOpacity
              key={index}
              style={styles.optionButton}
              onPress={() => handleAnswer(option.value)}
            >
              <Text style={styles.optionText}>
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </View>
  )
}
```

### 4.2 Avatar Matching Algorithm

```typescript
// lib/gamification.ts
export function computeAvatarMatch(
  quizAnswers: QuizAnswer[],
  selectedTraits: TraitKey[]
): { avatarId: string; score: number; explanation: string } {

  // Calculate trait scores from quiz answers
  const traitScores: Record<TraitKey, number> = {
    mindfulness: 0,
    selfAwareness: 0,
    productivity: 0,
    focus: 0,
    discipline: 0,
    confidence: 0,
    resilience: 0,
    creativity: 0
  }

  // Process quiz answers to compute trait scores
  quizAnswers.forEach(answer => {
    const question = QUIZ_QUESTIONS.find(q => q.id === answer.questionId)
    if (question) {
      question.traitWeights.forEach((weight, trait) => {
        traitScores[trait] += answer.value * weight
      })
    }
  })

  // Normalize scores to 0-1
  const maxScore = Math.max(...Object.values(traitScores))
  Object.keys(traitScores).forEach(trait => {
    traitScores[trait] = traitScores[trait] / maxScore
  })

  // Apply bonus to selected traits
  const SELECTED_TRAIT_BONUS = 1.5
  selectedTraits.forEach(trait => {
    traitScores[trait] *= SELECTED_TRAIT_BONUS
  })

  // Find best matching avatar
  let bestMatch = null
  let bestScore = -1

  AVATAR_ARCHETYPES.forEach(avatar => {
    const primaryScore = traitScores[avatar.primaryTrait] || 0
    const secondaryScore = traitScores[avatar.secondaryTrait] || 0
    const totalScore = primaryScore * 0.6 + secondaryScore * 0.4

    if (totalScore > bestScore) {
      bestScore = totalScore
      bestMatch = avatar
    }
  })

  return {
    avatarId: bestMatch.id,
    score: bestScore,
    explanation: `Based on your quiz results and selected traits, you matched with ${bestMatch.name}`
  }
}
```

## 📊 Phase 5: Task Generation & XP System (Day 5-6)

### 5.1 8-Week Task Generation

```typescript
// lib/taskGeneration.ts
export function generateWeeklyTasks(
  avatarId: string,
  selectedTraits: TraitKey[],
  weekNumber: number
): Task[] {
  const tasks: Task[] = []

  // Week difficulty mapping
  const weekConfig = {
    1: { difficulty: 'easy', minMinutes: 15, maxMinutes: 25, tasksPerDay: 2 },
    2: { difficulty: 'easy', minMinutes: 20, maxMinutes: 30, tasksPerDay: 2 },
    3: { difficulty: 'medium', minMinutes: 25, maxMinutes: 35, tasksPerDay: 3 },
    4: { difficulty: 'medium', minMinutes: 30, maxMinutes: 40, tasksPerDay: 3 },
    5: { difficulty: 'medium', minMinutes: 35, maxMinutes: 45, tasksPerDay: 3 },
    6: { difficulty: 'medium', minMinutes: 32, maxMinutes: 42, tasksPerDay: 3 }, // Deload
    7: { difficulty: 'hard', minMinutes: 40, maxMinutes: 55, tasksPerDay: 3 },
    8: { difficulty: 'hard', minMinutes: 45, maxMinutes: 60, tasksPerDay: 4 }
  }[weekNumber]

  // Generate tasks for 5 active days (Mon-Fri)
  const activeDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

  activeDays.forEach((day, dayIndex) => {
    // Ensure primary trait gets a task each day
    const primaryTrait = selectedTraits[0]
    tasks.push(generateTaskForTrait(
      primaryTrait,
      avatarId,
      weekConfig.difficulty,
      weekNumber,
      dayIndex
    ))

    // Add secondary tasks
    if (weekConfig.tasksPerDay >= 2 && selectedTraits[1]) {
      tasks.push(generateTaskForTrait(
        selectedTraits[1],
        avatarId,
        weekConfig.difficulty,
        weekNumber,
        dayIndex
      ))
    }

    // Add tertiary tasks for later weeks
    if (weekConfig.tasksPerDay >= 3 && selectedTraits[2]) {
      tasks.push(generateTaskForTrait(
        selectedTraits[2],
        avatarId,
        weekConfig.difficulty,
        weekNumber,
        dayIndex
      ))
    }
  })

  return tasks
}

function generateTaskForTrait(
  trait: TraitKey,
  avatarId: string,
  difficulty: 'easy' | 'medium' | 'hard',
  weekNumber: number,
  dayIndex: number
): Task {
  // Task templates by trait
  const templates = TASK_TEMPLATES[trait][difficulty]
  const template = templates[dayIndex % templates.length]

  // Evidence mode (photo only after week 5)
  const evidenceMode = weekNumber >= 5 && dayIndex % 2 === 0
    ? 'photo'
    : dayIndex % 2 === 0 ? 'timer' : 'check'

  return {
    title: template.title,
    description: template.description,
    trait,
    difficulty,
    xp_reward: { easy: 10, medium: 20, hard: 30 }[difficulty],
    duration_minutes: template.duration,
    evidence_mode: evidenceMode,
    week_number: weekNumber,
    scheduled_date: getDateForWeekAndDay(weekNumber, dayIndex)
  }
}
```

### 5.2 XP & Level Calculation

```typescript
// lib/xp.ts
export function calculateLevel(totalXp: number): number {
  let level = 1
  let requiredXp = 100

  while (totalXp >= requiredXp) {
    totalXp -= requiredXp
    level++
    requiredXp = Math.floor(100 * Math.pow(1.2, level - 1))
  }

  return level
}

export function getXpForNextLevel(currentLevel: number): number {
  return Math.floor(100 * Math.pow(1.2, currentLevel - 1))
}

export function getProgressToNextLevel(totalXp: number): number {
  const level = calculateLevel(totalXp)
  const xpForCurrentLevel = getXpForNextLevel(level)
  const xpProgress = totalXp - getTotalXpForLevel(level - 1)

  return (xpProgress / xpForCurrentLevel) * 100
}
```

## 📊 Phase 6: Analytics & Tracking (Day 6)

### 6.1 Analytics Setup

```typescript
// lib/analytics.ts
import mixpanel from 'mixpanel-browser'

mixpanel.init(process.env.NEXT_PUBLIC_MIXPANEL_TOKEN!)

export function trackEvent(
  event: string,
  properties?: Record<string, any>
) {
  if (process.env.NODE_ENV === 'production') {
    mixpanel.track(event, {
      ...properties,
      timestamp: new Date().toISOString()
    })
  }

  // Also log to database for custom analytics
  fetch('/api/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event, properties })
  })
}

// Conversion tracking
export const analytics = {
  // Landing page
  landingPageView: () => trackEvent('landing_page_view'),
  ctaClicked: (location: string) => trackEvent('cta_clicked', { location }),
  avatarHovered: (avatarId: string) => trackEvent('avatar_hovered', { avatarId }),

  // Onboarding
  onboardingStarted: () => trackEvent('onboarding_started'),
  onboardingStepCompleted: (step: number) => trackEvent('onboarding_step_completed', { step }),
  traitSelected: (trait: string) => trackEvent('trait_selected', { trait }),
  quizCompleted: (avatarMatched: string) => trackEvent('quiz_completed', { avatarMatched }),
  stakesEnabled: (amount: number) => trackEvent('stakes_enabled', { amount }),
  onboardingCompleted: (duration: number) => trackEvent('onboarding_completed', { duration }),
  onboardingAbandoned: (lastStep: number) => trackEvent('onboarding_abandoned', { lastStep }),

  // Engagement
  taskCompleted: (taskId: string, xpEarned: number) => trackEvent('task_completed', { taskId, xpEarned }),
  levelUp: (newLevel: number) => trackEvent('level_up', { newLevel }),
  streakMaintained: (days: number) => trackEvent('streak_maintained', { days }),
  achievementUnlocked: (achievementId: string) => trackEvent('achievement_unlocked', { achievementId })
}
```

### 6.2 A/B Testing Framework

```typescript
// lib/experiments.ts
export function getVariant(experimentId: string): 'control' | 'variant' {
  // Simple hash-based assignment
  const userId = getUserId() // From session
  const hash = hashCode(userId + experimentId)
  return hash % 2 === 0 ? 'control' : 'variant'
}

// Usage in landing page
export function Hero() {
  const ctaVariant = getVariant('hero-cta-text')

  const ctaText = ctaVariant === 'control'
    ? 'Start Your Journey'
    : 'Level Up Your Life'

  return (
    <Button onClick={() => {
      analytics.ctaClicked('hero')
      analytics.trackEvent('experiment_interaction', {
        experiment: 'hero-cta-text',
        variant: ctaVariant
      })
    }}>
      {ctaText} →
    </Button>
  )
}
```

## 📊 Phase 7: Integration & Testing (Day 6-7)

### 7.1 End-to-End Flow

```typescript
// app/api/onboarding/route.ts
export async function POST(request: Request) {
  const data = await request.json()
  const userId = getUserIdFromSession(request)

  // Start transaction
  const client = await getClient()

  try {
    await client.query('BEGIN')

    // 1. Update user as onboarded
    await client.query(
      'UPDATE users SET onboarding_completed = true WHERE id = $1',
      [userId]
    )

    // 2. Create user profile
    await client.query(`
      INSERT INTO user_profiles (
        user_id, avatar_id, avatar_name,
        selected_traits, quiz_answers, trait_scores,
        total_xp, current_level
      ) VALUES ($1, $2, $3, $4, $5, $6, 0, 1)
    `, [
      userId,
      data.avatarId || 'warrior',
      data.avatarName || 'The Warrior',
      data.selectedTraits,
      JSON.stringify(data.quizAnswers || []),
      JSON.stringify(data.traitScores || {})
    ])

    // 3. Generate Week 1 tasks
    const tasks = generateWeeklyTasks(
      data.avatarId,
      data.selectedTraits,
      1 // Week 1
    )

    for (const task of tasks) {
      await client.query(`
        INSERT INTO tasks (
          user_id, title, description, trait,
          difficulty, xp_reward, duration_minutes,
          evidence_mode, week_number, scheduled_date
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      `, [
        userId, task.title, task.description, task.trait,
        task.difficulty, task.xp_reward, task.duration_minutes,
        task.evidence_mode, task.week_number, task.scheduled_date
      ])
    }

    // 4. Create stakes if enabled
    if (data.stakesConfig) {
      await client.query(`
        INSERT INTO stakes (
          user_id, amount_cents, model,
          destination, recipient_email, active
        ) VALUES ($1, $2, $3, $4, $5, true)
      `, [
        userId,
        data.stakesConfig.amount * 100,
        data.stakesConfig.model,
        data.stakesConfig.destination,
        data.stakesConfig.recipientEmail
      ])
    }

    // 5. Create goals
    for (const goal of data.goals) {
      await client.query(`
        INSERT INTO goals (
          user_id, title, category, cadence, target, unit
        ) VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        userId, goal.title, goal.category,
        goal.cadence, goal.target, goal.unit
      ])
    }

    await client.query('COMMIT')

    // Track completion
    analytics.onboardingCompleted(Date.now() - data.startTime)

    return Response.json({
      success: true,
      userId,
      redirectUrl: '/dashboard'
    })

  } catch (error) {
    await client.query('ROLLBACK')
    console.error('Onboarding error:', error)
    return Response.json(
      { error: 'Failed to complete onboarding' },
      { status: 500 }
    )
  } finally {
    client.release()
  }
}
```

### 7.2 Testing Suite

```typescript
// __tests__/onboarding.test.ts
describe('Onboarding Flow', () => {
  test('Trait selection enforces max 3', () => {
    const { setSelectedTraits } = useOnboarding.getState()

    expect(() => {
      setSelectedTraits(['mindfulness', 'focus', 'discipline', 'creativity'])
    }).toThrow('Maximum 3 traits allowed')
  })

  test('Avatar matching is deterministic', () => {
    const answers = [
      { questionId: 1, value: 4 },
      { questionId: 2, value: 3 },
      // ... more answers
    ]

    const result1 = computeAvatarMatch(answers, ['mindfulness'])
    const result2 = computeAvatarMatch(answers, ['mindfulness'])

    expect(result1.avatarId).toBe(result2.avatarId)
  })

  test('Task generation follows week progression', () => {
    const week1Tasks = generateWeeklyTasks('warrior', ['discipline'], 1)
    const week8Tasks = generateWeeklyTasks('warrior', ['discipline'], 8)

    // Week 1 should be easier
    expect(week1Tasks.every(t => t.difficulty === 'easy')).toBe(true)

    // Week 8 should be harder
    expect(week8Tasks.some(t => t.difficulty === 'hard')).toBe(true)
  })
})
```

## 🚀 Deployment Strategy

### Production Checklist

```yaml
# .github/workflows/deploy.yml
name: Deploy LevelUp
on:
  push:
    branches: [main]

jobs:
  deploy:
    steps:
      - name: Run tests
        run: npm test

      - name: Check TypeScript
        run: npx tsc --noEmit

      - name: Run Lighthouse
        run: npx lighthouse https://staging.levelup.app

      - name: Deploy to Vercel
        run: vercel --prod

      - name: Run E2E tests
        run: npx playwright test
```

### Performance Targets
- **Lighthouse Score**: >90 all categories
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Bundle Size**: <200KB initial JS
- **Database Queries**: <50ms p95

### Monitoring Setup
```typescript
// lib/monitoring.ts
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV
})

// Track performance metrics
export function trackPerformance(metric: string, value: number) {
  Sentry.metrics.gauge(metric, value)

  // Also send to custom analytics
  fetch('/api/metrics', {
    method: 'POST',
    body: JSON.stringify({ metric, value })
  })
}
```

## 📈 Success Metrics & KPIs

### Conversion Funnel
1. **Landing → Sign-up**: Target >5%
2. **Sign-up → Complete Onboarding**: Target >60%
3. **Onboarding → First Task**: Target >80%
4. **First Task → Day 7 Retention**: Target >40%
5. **Day 7 → Day 30 Retention**: Target >25%

### Engagement Metrics
- **Daily Active Users** (DAU)
- **Tasks Completed per User per Day**
- **Average Session Duration**
- **Streak Length Distribution**
- **XP Earned per Session**

### Business Metrics
- **Customer Acquisition Cost** (CAC)
- **Lifetime Value** (LTV)
- **Stakes Adoption Rate**
- **Party Creation Rate**
- **Viral Coefficient** (invites sent)

## 🎯 Next Steps After Launch

1. **Week 1**: Monitor drop-off points, fix critical bugs
2. **Week 2**: A/B test CTA copy and hero images
3. **Week 3**: Optimize slow onboarding steps
4. **Week 4**: Launch referral program
5. **Month 2**: Build reward store and achievements
6. **Month 3**: Add social features and leaderboards

## 📁 Deliverables Summary

✅ **Phase 1**: Foundation
- Database configured with Neon
- Project structure created
- Dependencies installed

⏳ **Phase 2**: Landing Page
- Hero section with CTAs
- Avatar showcase
- Science section
- Conversion optimization

⏳ **Phase 3**: Web Onboarding
- 9-step flow implementation
- Zustand state management
- Form validation with Zod

⏳ **Phase 4**: Mobile Onboarding
- 7-step flow with quiz
- Avatar matching algorithm
- React Native components

⏳ **Phase 5**: Core Systems
- Task generation algorithm
- XP & leveling system
- Achievement tracking

⏳ **Phase 6**: Analytics
- Event tracking setup
- A/B testing framework
- Performance monitoring

⏳ **Phase 7**: Polish
- E2E testing
- Performance optimization
- Deployment pipeline

---

**Ready to build!** This comprehensive plan provides the complete roadmap for implementing the LevelUp landing page and onboarding funnel with all technical details, code examples, and best practices.