# LevelUp MCP Implementation Guide

## Quick Start: Using MCPs to Build LevelUp

This guide provides practical examples of how to use the configured MCPs to accelerate LevelUp development.

## 1. Figma Design Extraction (Available Now)

### Extract LevelUp UI Components
```javascript
// Get Figma file data for LevelUp designs
const figmaData = await mcp__figma_developer_mcp__get_figma_data({
  fileKey: "YOUR_FIGMA_FILE_KEY", // Get from Figma URL
  nodeId: "1234:5678", // Optional: specific screen/component
  depth: 3 // How deep to traverse the node tree
});

// Download avatar images from Figma
await mcp__figma_developer_mcp__download_figma_images({
  fileKey: "YOUR_FIGMA_FILE_KEY",
  localPath: "C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/levelup-ios/assets",
  nodes: [
    {
      nodeId: "100:200", // Scholar avatar node
      fileName: "avatar-scholar.png"
    },
    {
      nodeId: "100:201", // Warrior avatar node
      fileName: "avatar-warrior.png"
    },
    // Add all 10 avatars
  ],
  pngScale: 2 // 2x for retina displays
});
```

### Generate Theme from Figma
```typescript
// Extract design tokens from Figma
function extractDesignTokens(figmaData: any) {
  const tokens = {
    colors: {
      primary: figmaData.document.fills?.[0]?.color,
      secondary: figmaData.styles?.colors?.secondary,
      // Map all color styles
    },
    typography: {
      headings: figmaData.styles?.text?.heading,
      body: figmaData.styles?.text?.body,
      // Map text styles
    },
    spacing: {
      xs: "4px",
      sm: "8px",
      md: "16px",
      lg: "24px",
      xl: "32px",
      // Extract from Figma auto-layout
    }
  };

  return tokens;
}

// Generate platform-specific themes
function generatePlatformThemes(tokens: DesignTokens) {
  // iOS NativeWind theme
  const iosTheme = `
export const theme = {
  colors: ${JSON.stringify(tokens.colors, null, 2)},
  fontSizes: ${JSON.stringify(tokens.typography, null, 2)},
  spacing: ${JSON.stringify(tokens.spacing, null, 2)}
};
  `;

  // Web Tailwind config
  const webTheme = `
module.exports = {
  theme: {
    extend: {
      colors: ${JSON.stringify(tokens.colors, null, 2)},
      fontFamily: ${JSON.stringify(tokens.typography.fontFamily, null, 2)},
      spacing: ${JSON.stringify(tokens.spacing, null, 2)}
    }
  }
};
  `;

  return { iosTheme, webTheme };
}
```

## 2. Neon Database Setup

### Step 1: Create Neon Project
```bash
# Sign up at https://neon.tech
# Create a new project named "levelup"
# Get your connection string
```

### Step 2: Database Schema Creation
```sql
-- Core schema for LevelUp
-- Run these in order using your PostgreSQL client

-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Create users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  onboarding_completed BOOLEAN DEFAULT FALSE,
  timezone VARCHAR(50) DEFAULT 'America/New_York'
);

-- 3. Create user profiles with avatar data
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,

  -- Avatar selection
  avatar_id VARCHAR(50) NOT NULL,
  avatar_name VARCHAR(100) NOT NULL,

  -- Trait system (max 3 traits)
  selected_traits TEXT[] NOT NULL CHECK (array_length(selected_traits, 1) <= 3),
  quiz_answers JSONB NOT NULL DEFAULT '[]',
  trait_scores JSONB NOT NULL DEFAULT '{}',

  -- Gamification
  total_xp INTEGER DEFAULT 0,
  current_level INTEGER DEFAULT 1,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  full_potential_progress DECIMAL(5,2) DEFAULT 0.00,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Create tasks table
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  -- Task details
  title VARCHAR(255) NOT NULL,
  description TEXT,
  trait VARCHAR(50) NOT NULL,
  difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  xp_reward INTEGER NOT NULL,
  duration_minutes INTEGER NOT NULL,

  -- Evidence tracking
  evidence_mode VARCHAR(20) NOT NULL CHECK (evidence_mode IN ('check', 'timer', 'photo')),

  -- Scheduling
  week_number INTEGER NOT NULL CHECK (week_number BETWEEN 1 AND 8),
  scheduled_date DATE NOT NULL,

  -- Completion tracking
  completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMPTZ,
  evidence_submitted JSONB,

  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Indexes for performance
  INDEX idx_user_date (user_id, scheduled_date),
  INDEX idx_completed (completed)
);

-- 5. Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Add triggers for auto-updating timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Step 3: Connection Configuration
```typescript
// lib/db.ts for Next.js Web
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';

const pool = new Pool({
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  port: 5432,
  ssl: { rejectUnauthorized: false },
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

export const db = drizzle(pool);

// For React Native iOS
// Use a REST API layer instead of direct DB connection
```

## 3. IDE Integration for Development

### Use VS Code Diagnostics
```typescript
// The IDE MCP can help catch errors
await mcp__ide__getDiagnostics({
  uri: "file:///C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/levelup/app/page.tsx"
});

// Execute code in Jupyter for data analysis
await mcp__ide__executeCode({
  code: `
import pandas as pd
import matplotlib.pyplot as plt

# Analyze user engagement data
df = pd.read_sql("SELECT * FROM user_analytics", connection)
df['completion_rate'].plot(kind='line')
plt.show()
  `
});
```

## 4. Complete Development Workflow

### Phase 1: Design Import & Setup
```javascript
// 1. Extract Figma designs
const designs = await mcp__figma_developer_mcp__get_figma_data({
  fileKey: "abc123xyz",
  depth: 2
});

// 2. Download all assets
const avatarNodes = [
  { nodeId: "1:10", fileName: "scholar.png" },
  { nodeId: "1:11", fileName: "warrior.png" },
  { nodeId: "1:12", fileName: "sage.png" },
  { nodeId: "1:13", fileName: "builder.png" },
  { nodeId: "1:14", fileName: "monk.png" },
  { nodeId: "1:15", fileName: "leader.png" },
  { nodeId: "1:16", fileName: "phoenix.png" },
  { nodeId: "1:17", fileName: "artist.png" },
  { nodeId: "1:18", fileName: "explorer.png" },
  { nodeId: "1:19", fileName: "guardian.png" }
];

await mcp__figma_developer_mcp__download_figma_images({
  fileKey: "abc123xyz",
  localPath: "C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/levelup-ios/assets/avatars",
  nodes: avatarNodes,
  pngScale: 2
});

// 3. Generate theme files
const tokens = extractDesignTokens(designs);
const themes = generatePlatformThemes(tokens);

// Write iOS theme
await fs.writeFile('levelup-ios/theme/generated.ts', themes.iosTheme);

// Write Web theme
await fs.writeFile('levelup/tailwind.theme.js', themes.webTheme);
```

### Phase 2: API Development
```typescript
// app/api/onboarding/complete/route.ts
import { db } from '@/lib/db';
import { users, userProfiles, tasks } from '@/lib/schema';
import { generateWeeklyPlan } from '@/lib/gamification';

export async function POST(request: Request) {
  const body = await request.json();
  const {
    userId,
    avatarId,
    selectedTraits,
    quizAnswers,
    traitScores
  } = body;

  // Start a transaction
  await db.transaction(async (tx) => {
    // 1. Update user onboarding status
    await tx.update(users)
      .set({ onboarding_completed: true })
      .where(eq(users.id, userId));

    // 2. Create user profile
    await tx.insert(userProfiles).values({
      user_id: userId,
      avatar_id: avatarId,
      avatar_name: getAvatarName(avatarId),
      selected_traits: selectedTraits,
      quiz_answers: quizAnswers,
      trait_scores: traitScores
    });

    // 3. Generate 8-week plan
    for (let week = 1; week <= 8; week++) {
      const weekPlan = generateWeeklyPlan(avatarId, selectedTraits, week);

      // Insert tasks for this week
      for (const task of weekPlan.tasks) {
        await tx.insert(tasks).values({
          user_id: userId,
          title: task.title,
          description: task.description,
          trait: task.trait,
          difficulty: task.difficulty,
          xp_reward: task.xpReward,
          duration_minutes: task.duration,
          evidence_mode: task.evidenceMode,
          week_number: week,
          scheduled_date: task.scheduledDate
        });
      }
    }
  });

  return Response.json({ success: true });
}
```

### Phase 3: Task Generation Algorithm
```typescript
// lib/gamification/taskGenerator.ts
export function generateWeeklyPlan(
  avatarId: string,
  traits: string[],
  weekNumber: number
) {
  // Week difficulty mapping
  const weekConfig = {
    1: { difficulty: 'easy', minMinutes: 15, maxMinutes: 25 },
    2: { difficulty: 'easy', minMinutes: 20, maxMinutes: 30 },
    3: { difficulty: 'medium', minMinutes: 25, maxMinutes: 35 },
    4: { difficulty: 'medium', minMinutes: 30, maxMinutes: 40 },
    5: { difficulty: 'medium', minMinutes: 35, maxMinutes: 45 },
    6: { difficulty: 'medium', minMinutes: 32, maxMinutes: 42 }, // Deload
    7: { difficulty: 'hard', minMinutes: 40, maxMinutes: 55 },
    8: { difficulty: 'hard', minMinutes: 45, maxMinutes: 60 }
  };

  const config = weekConfig[weekNumber];
  const tasks = [];

  // 5 active days per week
  const activeDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  for (const day of activeDays) {
    const dayTasks = [];
    let dayMinutes = 0;

    // Ensure primary trait gets a task each day
    const primaryTrait = traits[0];
    const primaryTask = generateTaskForTrait(
      primaryTrait,
      avatarId,
      config.difficulty,
      weekNumber
    );
    dayTasks.push(primaryTask);
    dayMinutes += primaryTask.duration;

    // Add secondary trait tasks if needed for time
    if (dayMinutes < config.minMinutes && traits.length > 1) {
      const secondaryTask = generateTaskForTrait(
        traits[1],
        avatarId,
        config.difficulty,
        weekNumber
      );
      dayTasks.push(secondaryTask);
      dayMinutes += secondaryTask.duration;
    }

    // Add third trait if still under minimum
    if (dayMinutes < config.minMinutes && traits.length > 2) {
      const tertiaryTask = generateTaskForTrait(
        traits[2],
        avatarId,
        config.difficulty,
        weekNumber
      );
      dayTasks.push(tertiaryTask);
      dayMinutes += tertiaryTask.duration;
    }

    tasks.push(...dayTasks);
  }

  return {
    weekNumber,
    tasks,
    totalMinutes: tasks.reduce((sum, t) => sum + t.duration, 0),
    config
  };
}

function generateTaskForTrait(
  trait: string,
  avatarId: string,
  difficulty: string,
  weekNumber: number
) {
  // Task templates by trait
  const taskTemplates = {
    mindfulness: [
      { title: "Morning Meditation", duration: 10 },
      { title: "Gratitude Journal", duration: 5 },
      { title: "Breathing Exercise", duration: 8 }
    ],
    discipline: [
      { title: "Cold Shower", duration: 5 },
      { title: "No Phone Hour", duration: 60 },
      { title: "Wake Up Routine", duration: 15 }
    ],
    productivity: [
      { title: "Deep Work Session", duration: 25 },
      { title: "Task Prioritization", duration: 10 },
      { title: "Email Zero", duration: 20 }
    ],
    // ... add all traits
  };

  const templates = taskTemplates[trait];
  const template = templates[Math.floor(Math.random() * templates.length)];

  // Adjust duration based on difficulty
  const durationMultiplier = {
    easy: 0.8,
    medium: 1.0,
    hard: 1.3
  }[difficulty];

  // XP rewards
  const xpReward = {
    easy: 10,
    medium: 20,
    hard: 30
  }[difficulty];

  // Evidence mode (photo only after week 5)
  let evidenceMode = 'check';
  if (weekNumber >= 5 && Math.random() > 0.5) {
    evidenceMode = 'photo';
  } else if (Math.random() > 0.5) {
    evidenceMode = 'timer';
  }

  return {
    title: template.title,
    description: `${difficulty} level ${trait} challenge`,
    trait,
    difficulty,
    xpReward,
    duration: Math.round(template.duration * durationMultiplier),
    evidenceMode,
    scheduledDate: new Date() // Calculate actual date
  };
}
```

### Phase 4: Testing with MCPs
```typescript
// Test API endpoints
async function testOnboardingFlow() {
  // 1. Create test user
  const signupResponse = await fetch('/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'test@example.com',
      password: 'securepass123'
    })
  });

  const { userId } = await signupResponse.json();

  // 2. Complete onboarding
  const onboardingData = {
    userId,
    avatarId: 'warrior',
    selectedTraits: ['discipline', 'focus', 'resilience'],
    quizAnswers: [
      { questionId: 1, answer: 4 },
      { questionId: 2, answer: 5 },
      // ... 10 questions
    ],
    traitScores: {
      discipline: 0.85,
      focus: 0.72,
      resilience: 0.68,
      // ... all traits
    }
  };

  const onboardingResponse = await fetch('/api/onboarding/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(onboardingData)
  });

  // 3. Verify tasks were created
  const tasksResponse = await fetch(`/api/tasks?userId=${userId}`);
  const tasks = await tasksResponse.json();

  console.log(`Created ${tasks.length} tasks for 8-week plan`);

  // 4. Test task completion
  const firstTask = tasks[0];
  const completeResponse = await fetch(`/api/tasks/${firstTask.id}/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      evidenceType: 'check',
      notes: 'Completed successfully'
    })
  });

  // 5. Check XP update
  const profileResponse = await fetch(`/api/profile?userId=${userId}`);
  const profile = await profileResponse.json();

  console.log(`User XP: ${profile.total_xp}, Level: ${profile.current_level}`);
}
```

## 5. Monitoring & Analytics

### Performance Monitoring
```sql
-- Query to monitor task completion rates
SELECT
  DATE_TRUNC('day', scheduled_date) as day,
  COUNT(*) FILTER (WHERE completed = true) * 100.0 / COUNT(*) as completion_rate,
  AVG(EXTRACT(EPOCH FROM (completed_at - scheduled_date))) as avg_completion_time_seconds
FROM tasks
WHERE scheduled_date >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', scheduled_date)
ORDER BY day DESC;

-- User engagement metrics
SELECT
  COUNT(DISTINCT user_id) as daily_active_users,
  COUNT(*) FILTER (WHERE completed = true) as tasks_completed,
  AVG(xp_reward) as avg_xp_per_task
FROM tasks
WHERE scheduled_date = CURRENT_DATE;

-- Streak analysis
SELECT
  current_streak,
  COUNT(*) as user_count
FROM user_profiles
GROUP BY current_streak
ORDER BY current_streak DESC;
```

### Error Tracking
```typescript
// Setup error boundary with reporting
export function ErrorBoundary({ children }) {
  return (
    <ErrorBoundaryComponent
      fallback={(error) => <ErrorFallback error={error} />}
      onError={(error, errorInfo) => {
        // Log to monitoring service
        console.error('App Error:', error);

        // Track in database
        db.insert(errorLogs).values({
          error_message: error.toString(),
          stack_trace: errorInfo.componentStack,
          user_id: getCurrentUserId(),
          created_at: new Date()
        });
      }}
    >
      {children}
    </ErrorBoundaryComponent>
  );
}
```

## 6. Deployment Checklist

### Pre-Deployment
- [ ] Run database migrations on production Neon instance
- [ ] Verify all environment variables are set
- [ ] Test authentication flow end-to-end
- [ ] Verify Figma assets are downloaded and optimized
- [ ] Run performance tests on task queries
- [ ] Check mobile app builds successfully

### Deployment Commands
```bash
# Web (Vercel)
vercel --prod

# iOS (EAS)
eas build --platform ios --profile production
eas submit --platform ios

# Android (EAS)
eas build --platform android --profile production
eas submit --platform android
```

### Post-Deployment
- [ ] Monitor error rates in first 24 hours
- [ ] Check database query performance
- [ ] Verify push notifications working
- [ ] Test payment flow (if stakes enabled)
- [ ] Monitor user onboarding completion rate

## Summary

This implementation guide provides:
1. **Figma Integration** - Extract designs and generate themes
2. **Neon Database** - Complete schema and connection setup
3. **API Development** - RESTful endpoints for all features
4. **Task Generation** - Algorithm for 8-week progression
5. **Testing Strategy** - End-to-end testing approach
6. **Monitoring** - Performance and error tracking
7. **Deployment** - Production checklist

The MCP configuration enables efficient development by:
- Automating design-to-code workflow
- Providing robust database operations
- Enabling comprehensive testing
- Facilitating monitoring and analytics

Next steps:
1. Get Figma file key from designer
2. Create Neon database instance
3. Run database migrations
4. Start building API endpoints
5. Implement task generation
6. Test with real data