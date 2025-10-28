# LevelUp MCP Configuration Plan

## Overview
This document outlines the optimal Model Context Protocol (MCP) configuration for building the LevelUp gamified self-improvement app with Neon PostgreSQL integration and Figma design system.

## Current MCP Environment

### Available MCPs
1. **figma-developer-mcp** - Figma design extraction and component data
2. **figma-desktop** - Figma desktop integration
3. **ide** - VS Code IDE integration for diagnostics and code execution

### Required Additional MCPs
Based on the LevelUp requirements, we need to configure these additional MCPs:

## 1. Database Layer - Neon PostgreSQL MCP

### Configuration
```json
{
  "postgres-neon": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-postgres"],
    "env": {
      "PGHOST": "ep-wild-water-ade30whr-pooler.us-east-1.aws.neon.tech",
      "PGDATABASE": "levelup_db",
      "PGUSER": "neondb_owner",
      "PGPASSWORD": "YOUR_SECURE_PASSWORD",
      "PGPORT": "5432",
      "PGSSLMODE": "require"
    }
  }
}
```

### Database Schema for LevelUp
```sql
-- Core User Tables
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  timezone VARCHAR(50) DEFAULT 'UTC'
);

-- Avatar & Profile
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  avatar_id VARCHAR(50) NOT NULL,
  avatar_name VARCHAR(100) NOT NULL,
  selected_traits TEXT[] NOT NULL CHECK (array_length(selected_traits, 1) <= 3),
  quiz_answers JSONB NOT NULL,
  trait_scores JSONB NOT NULL,
  total_xp INTEGER DEFAULT 0,
  current_level INTEGER DEFAULT 1,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  full_potential_progress DECIMAL(5,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id)
);

-- Goals
CREATE TABLE goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,
  cadence VARCHAR(20) NOT NULL CHECK (cadence IN ('daily', 'weekly', 'monthly')),
  target INTEGER,
  unit VARCHAR(50),
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8-Week Progression Plan
CREATE TABLE progression_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  week_number INTEGER NOT NULL CHECK (week_number BETWEEN 1 AND 8),
  tasks JSONB NOT NULL, -- Array of task objects
  min_time_minutes INTEGER NOT NULL,
  max_time_minutes INTEGER NOT NULL,
  difficulty_level VARCHAR(20) NOT NULL CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, week_number)
);

-- Daily Tasks
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id UUID REFERENCES progression_plans(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  trait VARCHAR(50) NOT NULL,
  difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  xp_reward INTEGER NOT NULL,
  duration_minutes INTEGER NOT NULL,
  evidence_mode VARCHAR(20) NOT NULL CHECK (evidence_mode IN ('check', 'timer', 'photo')),
  scheduled_date DATE NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Evidence Submissions
CREATE TABLE evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  evidence_type VARCHAR(20) NOT NULL CHECK (evidence_type IN ('check', 'timer', 'photo')),
  photo_url TEXT, -- S3 or Cloudinary URL
  timer_seconds INTEGER,
  notes TEXT,
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  is_valid BOOLEAN DEFAULT TRUE
);

-- Stakes & Financial Accountability (Web only)
CREATE TABLE stakes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  amount_cents INTEGER NOT NULL CHECK (amount_cents BETWEEN 100 AND 10000), -- $1-$100
  model VARCHAR(20) NOT NULL CHECK (model IN ('flat', 'escalating')),
  destination VARCHAR(50) NOT NULL CHECK (destination IN ('charity', 'antiCharity', 'friend')),
  recipient_email VARCHAR(255),
  stripe_customer_id VARCHAR(255),
  stripe_payment_method_id VARCHAR(255),
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grace & Charges
CREATE TABLE grace_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  week_start_date DATE NOT NULL,
  grace_used BOOLEAN DEFAULT FALSE,
  grace_used_at TIMESTAMP WITH TIME ZONE,
  daily_charge_used BOOLEAN DEFAULT FALSE,
  charge_amount_cents INTEGER,
  charge_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, week_start_date)
);

-- Party System (Social Features)
CREATE TABLE parties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  code VARCHAR(20) UNIQUE NOT NULL,
  creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  active BOOLEAN DEFAULT TRUE
);

CREATE TABLE party_members (
  party_id UUID REFERENCES parties(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  role VARCHAR(20) DEFAULT 'member',
  PRIMARY KEY (party_id, user_id)
);

-- Analytics & Performance Metrics
CREATE TABLE user_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  event_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_tasks_user_date ON tasks(user_id, scheduled_date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_evidence_task ON evidence(task_id);
CREATE INDEX idx_stakes_user_active ON stakes(user_id, active);
CREATE INDEX idx_analytics_user_event ON user_analytics(user_id, event_type);
CREATE INDEX idx_party_members_user ON party_members(user_id);

-- Row Level Security (RLS) Policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE stakes ENABLE ROW LEVEL SECURITY;
```

## 2. Figma Design Integration MCP

### Configuration
Already configured as `figma-developer-mcp`. Here's how to use it for LevelUp:

### Design Extraction Pipeline
```javascript
// Extract LevelUp design tokens and components
const figmaConfig = {
  fileKey: "YOUR_FIGMA_FILE_KEY", // From Figma URL
  personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,

  // Key screens to extract
  screens: [
    "Onboarding/Welcome",
    "Onboarding/TraitSelection",
    "Onboarding/Quiz",
    "Onboarding/AvatarResult",
    "Dashboard/Today",
    "Dashboard/Progress",
    "Evidence/PhotoCapture",
    "Evidence/Timer"
  ],

  // Component extraction
  components: {
    avatars: "Components/Avatars/*",
    traits: "Components/Traits/*",
    buttons: "Components/Buttons/*",
    cards: "Components/Cards/*",
    progressBars: "Components/Progress/*"
  },

  // Design tokens
  tokens: {
    colors: true,
    typography: true,
    spacing: true,
    borderRadius: true,
    shadows: true
  }
};
```

### Figma to Code Workflow
```typescript
// 1. Extract design data
const designData = await mcp.figma.getFigmaData({
  fileKey: figmaConfig.fileKey,
  nodeId: "specific-node-id", // Optional
  depth: 3
});

// 2. Download avatar and icon assets
await mcp.figma.downloadFigmaImages({
  fileKey: figmaConfig.fileKey,
  localPath: "C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/levelup-ios/assets/avatars",
  nodes: [
    { nodeId: "avatar-scholar-id", fileName: "scholar.png" },
    { nodeId: "avatar-warrior-id", fileName: "warrior.png" },
    // ... other avatars
  ],
  pngScale: 2 // 2x for retina
});

// 3. Generate theme files from design tokens
const generateTheme = (tokens) => {
  // For iOS (NativeWind)
  const iosTheme = {
    colors: tokens.colors,
    fontFamily: tokens.typography.fontFamily,
    // ... map to NativeWind config
  };

  // For Web (Tailwind)
  const webTheme = {
    extend: {
      colors: tokens.colors,
      fontFamily: tokens.typography,
      spacing: tokens.spacing,
      // ... map to Tailwind config
    }
  };

  return { iosTheme, webTheme };
};
```

## 3. Development Workflow MCPs

### File System MCP (Already Available)
Use for reading/writing project files:
```typescript
// Read current configs
const packageJson = await mcp.filesystem.read({
  path: "C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/levelup/package.json"
});

// Write generated files
await mcp.filesystem.write({
  path: "C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/levelup/lib/generated/theme.ts",
  content: generatedTheme
});
```

### GitHub MCP (Recommended)
```json
{
  "github": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
    }
  }
}
```

Use for:
- Version control
- PR creation
- Issue tracking
- CI/CD triggers

### Memory MCP (Recommended)
```json
{
  "memory": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-memory"]
  }
}
```

Use for:
- Storing design decisions
- Tracking completed migrations
- Caching frequently used queries
- Maintaining context across sessions

## 4. API & Integration MCPs

### Fetch MCP (Recommended)
```json
{
  "fetch": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-fetch"]
  }
}
```

Use for:
- Testing API endpoints
- Webhook simulations
- Third-party integrations (Stripe, SendGrid, etc.)

### Puppeteer MCP (Optional)
```json
{
  "puppeteer": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-puppeteer"]
  }
}
```

Use for:
- E2E testing
- Screenshot generation for evidence
- Web scraping for research

## 5. Monitoring & Logging MCPs

### Suggested MCP Server Configuration
```javascript
// mcp-levelup-server.js
import { Server } from '@modelcontextprotocol/sdk';

const server = new Server({
  name: 'levelup-mcp-server',
  version: '1.0.0',
});

// Custom tools for LevelUp
server.addTool({
  name: 'migrate_database',
  description: 'Run database migrations for LevelUp',
  inputSchema: {
    type: 'object',
    properties: {
      direction: { type: 'string', enum: ['up', 'down'] },
      target: { type: 'string' }
    }
  },
  handler: async ({ direction, target }) => {
    // Run migrations using Neon connection
  }
});

server.addTool({
  name: 'generate_weekly_tasks',
  description: 'Generate tasks for a user week',
  inputSchema: {
    type: 'object',
    properties: {
      userId: { type: 'string' },
      weekNumber: { type: 'number' },
      avatarId: { type: 'string' },
      traits: { type: 'array', items: { type: 'string' } }
    }
  },
  handler: async ({ userId, weekNumber, avatarId, traits }) => {
    // Generate tasks using the progression algorithm
  }
});

server.addTool({
  name: 'sync_figma_assets',
  description: 'Sync design assets from Figma',
  inputSchema: {
    type: 'object',
    properties: {
      fileKey: { type: 'string' },
      assetType: { type: 'string', enum: ['avatars', 'icons', 'illustrations'] }
    }
  },
  handler: async ({ fileKey, assetType }) => {
    // Extract and download assets
  }
});

server.addTool({
  name: 'calculate_xp',
  description: 'Calculate XP and level progression',
  inputSchema: {
    type: 'object',
    properties: {
      userId: { type: 'string' },
      taskId: { type: 'string' },
      difficulty: { type: 'string' }
    }
  },
  handler: async ({ userId, taskId, difficulty }) => {
    // Calculate XP using gamification rules
  }
});
```

## 6. Complete MCP Configuration File

### claude-mcp-config.json
```json
{
  "mcpServers": {
    "postgres-neon": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-postgres"],
      "env": {
        "PGHOST": "ep-wild-water-ade30whr-pooler.us-east-1.aws.neon.tech",
        "PGDATABASE": "levelup_db",
        "PGUSER": "neondb_owner",
        "PGPASSWORD": "${PGPASSWORD}",
        "PGSSLMODE": "require"
      }
    },
    "figma-developer-mcp": {
      "command": "node",
      "args": ["C:/Users/jgewi/figma-mcp-server/index.js"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "${FIGMA_ACCESS_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem"],
      "env": {
        "FILESYSTEM_ROOT": "C:/Users/jgewi/OneDrive/Claude/New folder/Gratis"
      }
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-fetch"]
    },
    "levelup-custom": {
      "command": "node",
      "args": ["C:/Users/jgewi/OneDrive/Claude/New folder/Gratis/mcp-levelup-server.js"]
    }
  }
}
```

## 7. Development Workflow with MCPs

### Phase 1: Design Import
```typescript
// 1. Extract design from Figma
const design = await mcp.figma.getFigmaData({
  fileKey: "abc123",
  depth: 3
});

// 2. Generate theme files
const themes = generateThemeFromFigma(design);

// 3. Write theme files
await mcp.filesystem.write({
  path: "levelup-ios/theme/generated.ts",
  content: themes.ios
});

await mcp.filesystem.write({
  path: "levelup/tailwind.config.generated.js",
  content: themes.web
});
```

### Phase 2: Database Setup
```sql
-- Using postgres-neon MCP
-- Create database
CREATE DATABASE levelup_db;

-- Run migrations
\i migrations/001_create_users.sql
\i migrations/002_create_profiles.sql
\i migrations/003_create_tasks.sql
-- etc.

-- Verify schema
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

### Phase 3: API Development
```typescript
// Test endpoints using fetch MCP
const response = await mcp.fetch.request({
  url: "http://localhost:3000/api/onboarding",
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    userId: "test-user",
    avatar: "warrior",
    traits: ["discipline", "focus"],
    // ...
  })
});
```

### Phase 4: Testing Pipeline
```typescript
// E2E testing with puppeteer MCP
const browser = await mcp.puppeteer.launch();
const page = await browser.newPage();

await page.goto("http://localhost:3000");
await page.click('[data-testid="start-onboarding"]');
// ... test flow
```

## 8. Monitoring & Analytics

### Query Performance (Neon)
```sql
-- Monitor slow queries
SELECT
  query,
  calls,
  mean_exec_time,
  total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;
```

### User Analytics
```typescript
// Track key metrics
const analytics = {
  onboardingCompletion: await db.query(`
    SELECT COUNT(*) FILTER (WHERE onboarding_completed = true) * 100.0 / COUNT(*) as rate
    FROM users
  `),

  weeklyActiveUsers: await db.query(`
    SELECT COUNT(DISTINCT user_id)
    FROM tasks
    WHERE completed_at > NOW() - INTERVAL '7 days'
  `),

  averageStreak: await db.query(`
    SELECT AVG(current_streak)
    FROM user_profiles
  `)
};
```

## 9. Security Considerations

### Environment Variables
```bash
# .env.local
PGPASSWORD=secure_password_here
FIGMA_ACCESS_TOKEN=figma_token_here
GITHUB_PAT=github_token_here
STRIPE_SECRET_KEY=stripe_key_here
NEXTAUTH_SECRET=random_secret_here
```

### Database Security
- Use Row Level Security (RLS) policies
- Implement connection pooling with Neon
- Use parameterized queries
- Regular backups with point-in-time recovery

### API Security
- Rate limiting on all endpoints
- JWT authentication with refresh tokens
- Input validation with Zod schemas
- CORS configuration for production domains

## 10. Performance Optimization

### Database Optimization
```sql
-- Optimize frequently accessed queries
CREATE INDEX CONCURRENTLY idx_tasks_user_date_completed
ON tasks(user_id, scheduled_date, completed);

-- Partition large tables
CREATE TABLE user_analytics_2025 PARTITION OF user_analytics
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Caching Strategy
```typescript
// Use memory MCP for caching
await mcp.memory.set({
  key: `user_profile_${userId}`,
  value: userProfile,
  ttl: 3600 // 1 hour
});

// Check cache before database
const cached = await mcp.memory.get(`user_profile_${userId}`);
if (cached) return cached;
```

## Summary

This MCP configuration provides:
1. **Neon PostgreSQL** for scalable cloud database
2. **Figma Integration** for design-to-code workflow
3. **IDE Integration** for development efficiency
4. **Custom Tools** for LevelUp-specific operations
5. **Testing Pipeline** with puppeteer
6. **Version Control** with GitHub
7. **Memory Caching** for performance
8. **API Testing** with fetch

The configuration enables:
- Automated design updates from Figma
- Efficient database operations with Neon
- Comprehensive testing coverage
- Performance monitoring
- Secure authentication flow
- Scalable architecture

Next steps:
1. Install required MCP servers
2. Configure environment variables
3. Run database migrations
4. Import Figma designs
5. Begin API development