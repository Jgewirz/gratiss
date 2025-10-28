# LevelUp MCP Setup Checklist

## ✅ Complete Implementation Checklist

### **Step 1: Neon Database Setup**

- [ ] **Sign up for Neon** at https://neon.tech (free tier)
- [ ] **Create project** named "levelup"
- [ ] **Copy connection credentials** from Neon console:
  - Host: `ep-xxxxx.us-east-1.aws.neon.tech`
  - Database: `levelup_db`
  - User: `neondb_owner`
  - Password: [COPY THIS!]
- [ ] **Open Neon SQL Editor** (https://console.neon.tech)
- [ ] **Run migration** from `sql/migrations/001_initial_schema.sql`
- [ ] **Verify tables created** by running:
  ```sql
  SELECT table_name FROM information_schema.tables
  WHERE table_schema = 'public';
  ```
  You should see: users, user_profiles, goals, tasks, evidence, stakes, parties, etc.

---

### **Step 2: Install MCP Server Packages**

Open PowerShell as Administrator and run:

```bash
# Install globally (recommended)
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-fetch

# Verify installation
npx @modelcontextprotocol/server-postgres --version
```

**Troubleshooting:**
- If `npm` not found: Install Node.js from https://nodejs.org (LTS version)
- If permission errors: Run PowerShell as Administrator
- If `npx` not working: Restart terminal after npm install

---

### **Step 3: Update Environment Variables**

- [ ] **Edit Claude Desktop config** (already updated in previous step)
- [ ] **Replace placeholders** in `%APPDATA%\Claude\claude_desktop_config.json`:
  - Line 30: `PGPASSWORD` → Your Neon password
  - Line 46: `GITHUB_PERSONAL_ACCESS_TOKEN` → Your GitHub PAT (optional)

**To get GitHub PAT:**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:org`
4. Copy token and paste into config

- [ ] **Create `.env.local`** in project root:
  ```bash
  cd "C:\Users\jgewi\OneDrive\Claude\New folder\Gratis\levelup"
  cp ../.env.levelup.example .env.local
  ```
- [ ] **Fill in `.env.local`** with your credentials

---

### **Step 4: Test Database Connection**

- [ ] **Restart Claude Desktop** (close completely and reopen)
- [ ] **Test MCP connection** in Claude:

  Ask Claude: "Can you query the postgres-neon MCP to list all tables in the database?"

  Expected response: Should list the tables we created (users, tasks, etc.)

- [ ] **Run Node.js test script**:
  ```bash
  cd "C:\Users\jgewi\OneDrive\Claude\New folder\Gratis\levelup"
  node test-neon-connection.js
  ```

  Expected output:
  ```
  ✅ Connected to Neon PostgreSQL
  ✅ Current time from database: [timestamp]
  ✅ Found tables:
     - users
     - user_profiles
     - goals
     - tasks
     ... (all 11 tables)
  ✅ All tests passed!
  ```

---

### **Step 5: Verify MCP Integration**

Test each MCP server in Claude Desktop:

**Postgres MCP:**
```
Ask: "Query the database: SELECT COUNT(*) FROM users;"
Expected: Should return 0 (no users yet)
```

**Filesystem MCP:**
```
Ask: "List all files in the levelup directory"
Expected: Should show package.json, app/, components/, etc.
```

**Memory MCP:**
```
Ask: "Store this in memory: project_name=LevelUp"
Then ask: "What's the project name from memory?"
Expected: Should retrieve "LevelUp"
```

**Fetch MCP:**
```
Ask: "Fetch https://jsonplaceholder.typicode.com/todos/1"
Expected: Should return JSON data
```

**GitHub MCP (if configured):**
```
Ask: "List my GitHub repositories"
Expected: Should show your repos
```

---

### **Step 6: Install Project Dependencies**

```bash
# Web app
cd "C:\Users\jgewi\OneDrive\Claude\New folder\Gratis\levelup"
npm install

# Mobile app (if starting mobile)
cd "C:\Users\jgewi\OneDrive\Claude\New folder\Gratis\levelup-ios"
pnpm install
```

---

### **Step 7: Start Development**

**Web App:**
```bash
cd levelup
npm run dev
# Opens http://localhost:3000
```

**Mobile App:**
```bash
cd levelup-ios
pnpm start
# Opens Expo dev server
```

---

## 🎯 Quick Reference

### MCP Servers Configured:
1. ✅ **postgres-neon** - Neon PostgreSQL database
2. ✅ **filesystem** - Local file operations
3. ✅ **github** - GitHub integration (optional)
4. ✅ **memory** - Persistent key-value storage
5. ✅ **fetch** - HTTP requests
6. ✅ **figma-mcp** - Figma design extraction (already configured)
7. ✅ **n8n-mcp** - N8N workflow automation (already configured)

### Database Schema Created:
- `users` - User authentication
- `user_profiles` - Avatar, XP, levels, streaks
- `goals` - User-defined objectives
- `tasks` - Daily challenges
- `evidence` - Task completion proof
- `stakes` - Financial accountability
- `parties` - Social groups
- `grace_usage` - Streak grace tracking
- `user_analytics` - Event tracking

### Key Files Created:
- ✅ `sql/migrations/001_initial_schema.sql` - Database schema
- ✅ `.env.levelup.example` - Environment variable template
- ✅ `%APPDATA%\Claude\claude_desktop_config.json` - MCP configuration
- ✅ `SETUP_CHECKLIST.md` - This file

---

## 🐛 Troubleshooting

### Claude Desktop won't connect to MCP
1. Check if npm packages are installed: `npm list -g`
2. Verify config file has no JSON syntax errors
3. Check Windows event logs for errors
4. Restart Claude Desktop completely (close from system tray)

### Database connection fails
1. Verify Neon credentials in config
2. Check if database exists in Neon console
3. Test connection string with psql or database client
4. Ensure SSL mode is set to 'require'

### NPM commands not found
1. Install Node.js LTS from https://nodejs.org
2. Restart terminal after installation
3. Verify PATH includes npm: `echo $env:PATH` (PowerShell)

### MCP server crashes
1. Check logs in Claude Desktop (Help → View Logs)
2. Test individual server: `npx @modelcontextprotocol/server-postgres`
3. Verify all environment variables are set correctly

---

## 📚 Next Steps

Once setup is complete:

1. **Create first user** via API or directly in database
2. **Test onboarding flow** by building landing page
3. **Generate first tasks** using progression algorithm
4. **Test XP/leveling system** by completing tasks
5. **Build dashboard** to display user progress

---

## 🔗 Useful Links

- **Neon Console**: https://console.neon.tech
- **MCP Documentation**: https://modelcontextprotocol.io
- **Next.js Docs**: https://nextjs.org/docs
- **Expo Docs**: https://docs.expo.dev
- **Figma Access Token**: https://www.figma.com/developers/api#access-tokens
- **GitHub PAT**: https://github.com/settings/tokens

---

**Last Updated**: [Your date here]
**Status**: Ready for development ✅
