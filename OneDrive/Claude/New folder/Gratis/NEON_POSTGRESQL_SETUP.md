# Neon PostgreSQL MCP Server Setup Guide

## Step 1: Create Neon Account & Database

### 1.1 Sign up for Neon (Free Tier)
1. Go to https://neon.tech
2. Sign up with GitHub/Google/Email
3. Create a new project named "levelup"
4. Select the nearest region (e.g., US East)

### 1.2 Get Connection Details
Once your project is created, you'll get:
- Host: `ep-xxx-xxx-xxx.us-east-1.aws.neon.tech`
- Database: `neondb` (default) or `levelup_db` (custom)
- Username: `neondb_owner` or your custom username
- Password: Auto-generated secure password

### 1.3 Connection String Format
```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

## Step 2: Install PostgreSQL MCP Server

### Option A: Global Installation (Recommended)
```bash
# Install globally
npm install -g @modelcontextprotocol/server-postgres

# Verify installation
npx @modelcontextprotocol/server-postgres --version
```

### Option B: Local Installation
```bash
# In your project directory
cd "C:\Users\jgewi\OneDrive\Claude\New folder\Gratis"
npm install @modelcontextprotocol/server-postgres

# Create package.json if it doesn't exist
npm init -y
```

## Step 3: Configure Environment Variables

### 3.1 Update .env.real
```env
NEXT_PUBLIC_APP_NAME=LevelUp
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Auth (NextAuth configuration)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here-generate-with-openssl

# Neon PostgreSQL Database
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-xxx-xxx.us-east-1.aws.neon.tech/levelup_db?sslmode=require

# Separate Neon credentials for MCP
PGHOST=ep-xxx-xxx.us-east-1.aws.neon.tech
PGDATABASE=levelup_db
PGUSER=neondb_owner
PGPASSWORD=YOUR_PASSWORD
PGPORT=5432
PGSSLMODE=require

# Payment processing (Stripe - optional for now)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# File storage (optional)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

### 3.2 Create .env.local for Development
```env
# Copy .env.real to .env.local
# Never commit .env.local to git
```

## Step 4: Configure MCP for Claude

### 4.1 Create/Update claude_desktop_config.json
Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "postgres-neon": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-postgres",
        "postgresql://neondb_owner:YOUR_PASSWORD@ep-xxx-xxx.us-east-1.aws.neon.tech/levelup_db?sslmode=require"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\jgewi\\OneDrive\\Claude\\New folder\\Gratis"
      ]
    },
    "figma-developer-mcp": {
      "command": "node",
      "args": ["C:\\path\\to\\figma-mcp-server\\index.js"]
    }
  }
}
```

### 4.2 Alternative: Use Environment Variables in MCP Config
```json
{
  "mcpServers": {
    "postgres-neon": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-postgres"],
      "env": {
        "PGHOST": "ep-xxx-xxx.us-east-1.aws.neon.tech",
        "PGDATABASE": "levelup_db",
        "PGUSER": "neondb_owner",
        "PGPASSWORD": "YOUR_PASSWORD",
        "PGPORT": "5432",
        "PGSSLMODE": "require"
      }
    }
  }
}
```

## Step 5: Test MCP Connection

### 5.1 Restart Claude Desktop
After updating the config:
1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. The MCP server should connect automatically

### 5.2 Verify Connection in Claude
Ask Claude to test the connection:
```
"Can you query the postgres-neon MCP to list all tables?"
```

Expected response should show available tables or indicate the database is empty.

## Step 6: Initialize Database Schema

### 6.1 Create Migration File
Save as `migrations/001_initial_schema.sql`:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    timezone VARCHAR(50) DEFAULT 'America/New_York'
);

-- User profiles with avatar data
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    avatar_id VARCHAR(50) NOT NULL,
    avatar_name VARCHAR(100) NOT NULL,
    selected_traits TEXT[] NOT NULL CHECK (array_length(selected_traits, 1) <= 3),
    quiz_answers JSONB NOT NULL DEFAULT '[]',
    trait_scores JSONB NOT NULL DEFAULT '{}',
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    full_potential_progress DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    trait VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    xp_reward INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    evidence_mode VARCHAR(20) NOT NULL CHECK (evidence_mode IN ('check', 'timer', 'photo')),
    week_number INTEGER NOT NULL CHECK (week_number BETWEEN 1 AND 8),
    scheduled_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    evidence_submitted JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Goals table
CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cadence VARCHAR(20) NOT NULL CHECK (cadence IN ('daily', 'weekly', 'monthly')),
    target INTEGER,
    unit VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evidence submissions
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    evidence_type VARCHAR(20) NOT NULL CHECK (evidence_type IN ('check', 'timer', 'photo')),
    photo_url TEXT,
    timer_seconds INTEGER,
    notes TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    is_valid BOOLEAN DEFAULT TRUE
);

-- Stakes (financial accountability)
CREATE TABLE IF NOT EXISTS stakes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount_cents INTEGER NOT NULL CHECK (amount_cents BETWEEN 100 AND 10000),
    model VARCHAR(20) NOT NULL CHECK (model IN ('flat', 'escalating')),
    destination VARCHAR(50) NOT NULL CHECK (destination IN ('charity', 'antiCharity', 'friend')),
    recipient_email VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    stripe_payment_method_id VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Party system
CREATE TABLE IF NOT EXISTS parties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS party_members (
    party_id UUID NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    role VARCHAR(20) DEFAULT 'member',
    PRIMARY KEY (party_id, user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_date ON tasks(user_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_evidence_task ON evidence(task_id);
CREATE INDEX IF NOT EXISTS idx_stakes_user_active ON stakes(user_id, active);
CREATE INDEX IF NOT EXISTS idx_party_members_user ON party_members(user_id);

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stakes_updated_at BEFORE UPDATE ON stakes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 6.2 Run Migration
You can run this through:
1. Neon's SQL Editor in the web console
2. Using a PostgreSQL client (pgAdmin, DBeaver, TablePlus)
3. Through the MCP once configured

## Step 7: Test Database Connection

### 7.1 Create Test Script
Save as `test-neon-connection.js`:

```javascript
const { Pool } = require('pg');
require('dotenv').config({ path: '.env.real' });

const pool = new Pool({
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  port: process.env.PGPORT || 5432,
  ssl: {
    rejectUnauthorized: false
  }
});

async function testConnection() {
  try {
    console.log('Testing Neon PostgreSQL connection...');

    // Test basic connection
    const client = await pool.connect();
    console.log('✅ Connected to Neon PostgreSQL');

    // Test query
    const result = await client.query('SELECT NOW()');
    console.log('✅ Current time from database:', result.rows[0].now);

    // List tables
    const tables = await client.query(`
      SELECT tablename
      FROM pg_tables
      WHERE schemaname = 'public'
    `);

    if (tables.rows.length > 0) {
      console.log('✅ Found tables:');
      tables.rows.forEach(row => {
        console.log(`   - ${row.tablename}`);
      });
    } else {
      console.log('ℹ️ No tables found. Run migrations first.');
    }

    client.release();
    await pool.end();

    console.log('\n✅ All tests passed! Neon PostgreSQL is configured correctly.');
  } catch (error) {
    console.error('❌ Connection failed:', error.message);
    console.error('Please check your credentials in .env.real');
  }
}

testConnection();
```

### 7.2 Run Test
```bash
node test-neon-connection.js
```

## Step 8: Configure for Next.js

### 8.1 Install Database Packages
```bash
cd levelup
npm install pg @types/pg
npm install drizzle-orm drizzle-kit # Optional: for ORM
npm install @neondatabase/serverless # For edge runtime
```

### 8.2 Create Database Connection Module
Save as `levelup/lib/db.ts`:

```typescript
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';

// For server-side Node.js
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  },
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

export const db = drizzle(pool);
export { pool };

// For edge runtime (Vercel Edge Functions)
import { neon } from '@neondatabase/serverless';

export const sql = neon(process.env.DATABASE_URL!);
```

## Troubleshooting

### Common Issues

1. **"Connection refused" error**
   - Check if your IP is whitelisted in Neon (usually automatic)
   - Verify SSL mode is set to 'require'
   - Check credentials are correct

2. **"Database does not exist" error**
   - Create the database in Neon console
   - Or use the default 'neondb' database

3. **MCP not connecting in Claude**
   - Restart Claude Desktop completely
   - Check the path to npx is correct
   - Verify the PostgreSQL MCP server is installed

4. **SSL Certificate error**
   - Set `rejectUnauthorized: false` in development
   - For production, download Neon's CA certificate

### Verify MCP is Working
Once configured, you should be able to ask Claude:
- "Query the postgres-neon database to show all tables"
- "Create a test table in the database"
- "Insert sample data into the users table"

## Next Steps

1. ✅ Neon account created and database provisioned
2. ✅ PostgreSQL MCP server installed
3. ✅ Environment variables configured
4. ✅ MCP configuration updated
5. ✅ Database schema created
6. ⏭️ Test the connection
7. ⏭️ Start building API endpoints
8. ⏭️ Implement authentication