# LevelUp Skills

This directory contains specialized skills for the LevelUp project. These skills provide deep domain knowledge and best practices for specific areas of the codebase.

## Available Skills

### 1. levelup-ios-core
**Location**: `levelup-ios-core/SKILL.md`

**When to use**: Working on routing, navigation, component structure, styling with NativeWind, or file organization.

**Coverage**:
- Expo Router file-based routing patterns
- NativeWind styling conventions
- Accessibility requirements (WCAG compliance)
- Copy management (centralized strings in `lib/copy.ts`)
- Component patterns and error boundaries
- File organization structure
- Performance considerations

**Key principles**:
- All UI strings must be in `lib/copy.ts`
- Minimum 44x44px touch targets
- NativeWind classes, no StyleSheet.create()
- TypeScript strict mode with proper type guards

---

### 2. levelup-gamification
**Location**: `levelup-gamification/SKILL.md`

**When to use**: Working on avatar matching, XP calculations, task progression, or evidence modes.

**Coverage**:
- Deterministic avatar matching algorithm
- XP & progression system (fixed constants)
- 8-week task progression (wave-linear formula)
- Evidence mode gating (photo from Week 5+)
- Validation suite for plan generation
- Trait system (10 core traits, max 3 selection)

**Key principles**:
- **Determinism is critical** - No Math.random() or Date.now()
- Identical inputs must produce identical outputs
- All scoring functions are pure and testable
- Self-test functions verify consistency

**Reference files**:
- `references/progression-system.md` - Complete wave-linear formula
- `references/avatar-archetypes.md` - Full avatar definitions

---

### 3. levelup-state-management
**Location**: `levelup-state-management/SKILL.md`

**When to use**: Working on Zustand stores, state updates, persistence, or task completion tracking.

**Coverage**:
- Two-store architecture (onboarding + user stores)
- AsyncStorage persistence patterns
- Immutable state updates with Zustand
- Computed selectors for derived values
- Time & grace period management (4-hour grace window)
- Streak calculation logic
- Stakes gating logic

**Key principles**:
- Unidirectional data flow
- Never mutate state directly
- Selective persistence (only what needs to survive restarts)
- Compute derived values in selectors

**Reference files**:
- `references/grace-period-reference.md` - Time calculations and grace logic

---

## Skill Structure

Each skill follows this format:

```
levelup-{name}/
├── SKILL.md              # Main skill documentation
└── references/           # Optional deep-dive references
    ├── system-1.md
    └── system-2.md
```

## How Claude Code Uses Skills

Claude Code will automatically detect these skills and use them as context when:
1. You're working on files related to the skill's domain
2. You explicitly mention the skill area (e.g., "use gamification skill")
3. The code patterns match the skill's expertise

## Testing Skills

Each skill includes testing patterns and requirements:

- **ios-core**: Component testing, routing tests, validator tests
- **gamification**: Determinism tests (100+ iterations), progression bounds, trait cap
- **state-management**: Action tests, persistence tests, computed selector tests

## Skill Dependencies

```
levelup-state-management
    └─> levelup-gamification (XP calculations, level formula)
        └─> levelup-ios-core (type definitions, validators)
```

## Adding New Skills

To add a new skill:

1. Create a directory: `.claude/skills/skillname/`
2. Add `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skillname
   description: Brief description of when to use this skill
   ---
   ```
3. Add optional `references/` directory for deep-dive docs
4. Package as `.skill` file (ZIP archive) if sharing

## Maintenance

- Keep skills focused on specific domains
- Update when architecture patterns change
- Ensure examples match actual codebase
- Add new reference docs as systems evolve

---

**Last Updated**: October 28, 2025
**Project**: LevelUp (Gamified Self-Improvement App)
**Skills Version**: 1.0.0
