# LevelUp Quick Start Guide

## 🚀 Ready to Code? Start Here!

### Current Status
✅ Database configured and tested (Neon PostgreSQL)
✅ Landing page complete (`/landing`)
✅ Avatar system designed (10 archetypes)
✅ State management ready (Zustand)
⏳ **NEXT**: Build onboarding pages

## 📋 Today's Priority: Create Onboarding Flow

### Step 1: Create Welcome Page
```bash
cd levelup
# Create: app/(onboarding)/welcome/page.tsx
```

```typescript
// Quick template to start:
export default function WelcomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <ProgressHeader step={1} total={9} />
      <main className="flex-1">
        <h1>Welcome to LevelUp</h1>
        <Button onClick={() => router.push('/onboarding/auth')}>
          Get Started
        </Button>
      </main>
    </div>
  )
}
```

### Step 2: Create Trait Selection Page
```bash
# Create: app/(onboarding)/traits/page.tsx
```
- Import from `data/avatars.ts`
- Use `useOnboardingStore` from `store/onboarding-enhanced.ts`
- Max 3 traits validation

### Step 3: Connect to Database
```javascript
// Your database is ready at:
// Host: ep-soft-water-a49zauo9-pooler.us-east-1.aws.neon.tech
// Database: neondb
// All tables created and tested!

import { query } from '@/lib/db'

// Example: Create user
const user = await query(
  'INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING *',
  [email, hashedPassword]
)
```

## 🎮 Key Files You'll Use

| File | Purpose | Status |
|------|---------|--------|
| `levelup/app/landing/page.tsx` | Landing page | ✅ Complete |
| `levelup/data/avatars.ts` | 10 avatar definitions | ✅ Complete |
| `levelup/store/onboarding-enhanced.ts` | State management | ✅ Complete |
| `levelup/lib/db.ts` | Database connection | ✅ Working |
| `levelup/app/(onboarding)/` | Onboarding pages | ⏳ Need to create |

## 🔧 Development Commands

```bash
# Start web dev server
cd levelup
npm run dev
# Visit: http://localhost:3000

# Test database
node test-database-ready.js

# View landing page
# http://localhost:3000/landing

# Start mobile app
cd levelup-ios
npm start
```

## 📝 Onboarding Pages to Create

### Web (9 steps) - Create these files:
```
app/(onboarding)/
├── layout.tsx          # Shared layout with progress
├── welcome/page.tsx    # 1. Welcome message
├── auth/page.tsx       # 2. Sign up form
├── traits/page.tsx     # 3. Select 1-3 traits
├── goals/page.tsx      # 4. Add goals
├── stakes/page.tsx     # 5. Financial commitment
├── evidence/page.tsx   # 6. How to track
├── permissions/page.tsx # 7. Notifications
├── party/page.tsx      # 8. Invite friends
└── summary/page.tsx    # 9. Review & confirm
```

### Mobile (7 steps) - Create these files:
```
levelup-ios/app/(onboarding)/
├── _layout.tsx
├── welcome.tsx         # 1. Welcome
├── select-traits.tsx   # 2. Traits (max 3)
├── quiz.tsx           # 3. 10 questions
├── avatar-result.tsx  # 4. Show matched avatar
├── plan-preview.tsx   # 5. 8-week overview
├── permissions.tsx    # 6. iOS permissions
└── start.tsx         # 7. First task
```

## 🎨 UI Components Available

### From shadcn/ui (already installed):
- `Button` - All buttons
- `Card` - Content containers
- `Input` - Form inputs
- `Label` - Form labels
- `Alert` - Messages
- `Progress` - Progress bars

### Icons from Lucide (already installed):
```typescript
import {
  ArrowRight, CheckCircle, Star,
  Trophy, Target, Brain, Zap
} from 'lucide-react'
```

## 🗄️ Database Tables Ready to Use

```sql
-- All these tables exist and are ready:
users              -- Authentication
user_profiles      -- Avatar, traits, XP
tasks              -- Daily challenges
goals              -- User objectives
stakes             -- Financial accountability
parties            -- Social groups
achievements       -- Badges & rewards
```

## 🔑 Quick Code Snippets

### Use Onboarding Store:
```typescript
import { useOnboardingStore } from '@/store/onboarding-enhanced'

function MyComponent() {
  const {
    selectedTraits,
    setSelectedTraits,
    nextStep,
    currentStep
  } = useOnboardingStore()
}
```

### Query Database:
```typescript
import { query } from '@/lib/db'

const result = await query(
  'SELECT * FROM users WHERE email = $1',
  [email]
)
```

### Track Analytics:
```typescript
import { analytics } from '@/lib/analytics'

analytics.onboardingStepCompleted(2)
analytics.traitSelected('mindfulness')
```

## ⚡ Quick Wins for Today

1. **Create Welcome Page** (30 min)
   - Use existing landing page components
   - Add "Get Started" button

2. **Create Auth Page** (45 min)
   - Email/password form
   - Connect to `/api/auth/register`

3. **Create Trait Selection** (45 min)
   - Import avatar data
   - Max 3 validation
   - Connect to store

4. **Test Flow** (30 min)
   - Navigate through pages
   - Check store updates
   - Verify database writes

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `npm install` in levelup folder |
| Database connection error | Check `.env.real` has correct credentials |
| Page not loading | Make sure dev server is running |
| Styles not working | Tailwind needs `className` not `class` |

## 📞 Key Resources

- **Database Dashboard**: https://console.neon.tech
- **Your Project**: `C:\Users\jgewi\OneDrive\Claude\New folder\Gratis\levelup`
- **Test DB**: Run `node test-database-ready.js`
- **View Landing**: http://localhost:3000/landing

## 🎯 Success Checklist for Today

- [ ] Welcome page created and styled
- [ ] Auth page with registration form
- [ ] Trait selection with 3-max validation
- [ ] Navigation between pages works
- [ ] Store updates on each step
- [ ] Progress bar shows current step
- [ ] Can reach summary page
- [ ] Data persists on refresh

---

**You're all set!** The infrastructure is ready, the database is connected, and the landing page is live. Focus on creating the onboarding pages one by one, connecting them to the store, and you'll have a working app soon!

**Next Command to Run:**
```bash
cd levelup
npm run dev
# Then start creating pages in app/(onboarding)/
```