# Avatar Archetypes

## Overview

LevelUp uses 10 avatar archetypes, each representing a unique combination of traits. Every avatar has:

- **Primary Trait**: Highest stat value (8-10)
- **Secondary Trait**: Second-highest stat value (6-8)
- **Other Traits**: Supporting values (2-6)

## Complete Avatar Definitions

### 1. Warrior

**Primary**: Strength (10)  
**Secondary**: Courage (8)

```typescript
{
  id: 'warrior',
  name: 'The Warrior',
  description: 'Masters physical challenges through power and bravery',
  primaryTrait: 'strength',
  secondaryTrait: 'courage',
  stats: {
    strength: 10,
    courage: 8,
    discipline: 6,
    resilience: 7,
    leadership: 5,
    focus: 4,
    wisdom: 3,
    compassion: 3,
    creativity: 2,
    curiosity: 2,
  },
  color: '#D32F2F', // Deep Red
  icon: 'sword'
}
```

**Personality**: Bold, action-oriented, thrives on physical challenges. Prefers high-intensity tasks with tangible results.

**Ideal Tasks**: Workouts, physical challenges, competitive goals, outdoor adventures.

---

### 2. Scholar

**Primary**: Wisdom (10)  
**Secondary**: Curiosity (8)

```typescript
{
  id: 'scholar',
  name: 'The Scholar',
  description: 'Pursues knowledge and understanding through study and exploration',
  primaryTrait: 'wisdom',
  secondaryTrait: 'curiosity',
  stats: {
    wisdom: 10,
    curiosity: 8,
    focus: 7,
    discipline: 6,
    creativity: 5,
    compassion: 4,
    resilience: 3,
    courage: 3,
    leadership: 2,
    strength: 2,
  },
  color: '#1976D2', // Royal Blue
  icon: 'book'
}
```

**Personality**: Analytical, inquisitive, loves learning. Prefers intellectual challenges and deep dives into subjects.

**Ideal Tasks**: Reading, research, skill development, puzzle-solving, language learning.

---

### 3. Guardian

**Primary**: Compassion (10)  
**Secondary**: Resilience (8)

```typescript
{
  id: 'guardian',
  name: 'The Guardian',
  description: 'Protects and supports others through empathy and endurance',
  primaryTrait: 'compassion',
  secondaryTrait: 'resilience',
  stats: {
    compassion: 10,
    resilience: 8,
    wisdom: 6,
    discipline: 5,
    courage: 5,
    strength: 4,
    leadership: 4,
    focus: 3,
    creativity: 3,
    curiosity: 2,
  },
  color: '#388E3C', // Forest Green
  icon: 'shield'
}
```

**Personality**: Nurturing, supportive, emotionally intelligent. Motivated by helping others and building community.

**Ideal Tasks**: Volunteering, caregiving, mentoring, acts of service, relationship building.

---

### 4. Sage

**Primary**: Discipline (10)  
**Secondary**: Focus (8)

```typescript
{
  id: 'sage',
  name: 'The Sage',
  description: 'Achieves mastery through consistent practice and concentration',
  primaryTrait: 'discipline',
  secondaryTrait: 'focus',
  stats: {
    discipline: 10,
    focus: 8,
    wisdom: 7,
    resilience: 6,
    curiosity: 5,
    compassion: 4,
    creativity: 3,
    courage: 3,
    leadership: 2,
    strength: 2,
  },
  color: '#7B1FA2', // Deep Purple
  icon: 'lotus'
}
```

**Personality**: Meditative, patient, values routine. Excels at long-term practices requiring sustained attention.

**Ideal Tasks**: Meditation, journaling, habit tracking, deliberate practice, mindfulness exercises.

---

### 5. Pioneer

**Primary**: Courage (10)  
**Secondary**: Curiosity (8)

```typescript
{
  id: 'pioneer',
  name: 'The Pioneer',
  description: 'Explores new frontiers through bravery and inquisitiveness',
  primaryTrait: 'courage',
  secondaryTrait: 'curiosity',
  stats: {
    courage: 10,
    curiosity: 8,
    creativity: 7,
    resilience: 6,
    strength: 5,
    leadership: 5,
    focus: 4,
    discipline: 3,
    wisdom: 2,
    compassion: 2,
  },
  color: '#F57C00', // Amber
  icon: 'compass'
}
```

**Personality**: Adventurous, risk-taking, embraces uncertainty. Thrives when trying new experiences.

**Ideal Tasks**: New hobbies, social challenges, public speaking, travel, stepping outside comfort zone.

---

### 6. Artist

**Primary**: Creativity (10)  
**Secondary**: Focus (8)

```typescript
{
  id: 'artist',
  name: 'The Artist',
  description: 'Expresses inner vision through imaginative and focused creation',
  primaryTrait: 'creativity',
  secondaryTrait: 'focus',
  stats: {
    creativity: 10,
    focus: 8,
    curiosity: 7,
    discipline: 5,
    compassion: 5,
    wisdom: 4,
    resilience: 3,
    courage: 3,
    leadership: 2,
    strength: 2,
  },
  color: '#C2185B', // Magenta
  icon: 'palette'
}
```

**Personality**: Imaginative, aesthetically driven, values self-expression. Motivated by creating beauty and meaning.

**Ideal Tasks**: Art projects, music practice, writing, design, creative experiments.

---

### 7. Leader

**Primary**: Leadership (10)  
**Secondary**: Discipline (8)

```typescript
{
  id: 'leader',
  name: 'The Leader',
  description: 'Inspires and organizes others through influence and structure',
  primaryTrait: 'leadership',
  secondaryTrait: 'discipline',
  stats: {
    leadership: 10,
    discipline: 8,
    courage: 7,
    wisdom: 6,
    compassion: 6,
    strength: 5,
    focus: 4,
    resilience: 3,
    creativity: 2,
    curiosity: 2,
  },
  color: '#FFA000', // Gold
  icon: 'crown'
}
```

**Personality**: Charismatic, organized, takes initiative. Thrives when coordinating groups or managing projects.

**Ideal Tasks**: Team projects, event planning, mentorship, goal setting, organizational tasks.

---

### 8. Monk

**Primary**: Resilience (10)  
**Secondary**: Discipline (8)

```typescript
{
  id: 'monk',
  name: 'The Monk',
  description: 'Endures hardship through unwavering practice and inner strength',
  primaryTrait: 'resilience',
  secondaryTrait: 'discipline',
  stats: {
    resilience: 10,
    discipline: 8,
    focus: 7,
    wisdom: 6,
    compassion: 5,
    courage: 4,
    strength: 4,
    curiosity: 2,
    creativity: 2,
    leadership: 2,
  },
  color: '#5D4037', // Brown
  icon: 'mountain'
}
```

**Personality**: Stoic, persistent, values simplicity. Excels at pushing through difficulty and maintaining long streaks.

**Ideal Tasks**: Endurance challenges, fasting, cold exposure, early wake-ups, difficult routines.

---

### 9. Strategist

**Primary**: Focus (10)  
**Secondary**: Wisdom (8)

```typescript
{
  id: 'strategist',
  name: 'The Strategist',
  description: 'Plans and executes through careful analysis and concentration',
  primaryTrait: 'focus',
  secondaryTrait: 'wisdom',
  stats: {
    focus: 10,
    wisdom: 8,
    discipline: 7,
    curiosity: 6,
    leadership: 5,
    resilience: 4,
    creativity: 3,
    courage: 2,
    compassion: 2,
    strength: 2,
  },
  color: '#0097A7', // Teal
  icon: 'chess'
}
```

**Personality**: Methodical, analytical, big-picture thinker. Enjoys optimization and systems design.

**Ideal Tasks**: Planning, productivity systems, financial tracking, goal mapping, strategic projects.

---

### 10. Explorer

**Primary**: Curiosity (10)  
**Secondary**: Creativity (8)

```typescript
{
  id: 'explorer',
  name: 'The Explorer',
  description: 'Discovers possibilities through wonder and inventive thinking',
  primaryTrait: 'curiosity',
  secondaryTrait: 'creativity',
  stats: {
    curiosity: 10,
    creativity: 8,
    courage: 7,
    focus: 5,
    wisdom: 5,
    compassion: 4,
    resilience: 3,
    strength: 3,
    discipline: 2,
    leadership: 2,
  },
  color: '#00796B', // Emerald
  icon: 'telescope'
}
```

**Personality**: Playful, experimental, open-minded. Motivated by novelty and connecting unexpected ideas.

**Ideal Tasks**: Experiments, hobby sampling, idea generation, exploration, learning diverse topics.

---

## Stat Distribution Guidelines

### Stat Value Meanings

- **10**: Core identity trait, defines the archetype
- **8-9**: Strong secondary characteristic
- **6-7**: Notable supporting trait
- **4-5**: Present but not dominant
- **2-3**: Underdeveloped or less relevant

### Balance Rules

- Total stats per avatar: ~50 points
- Primary + Secondary: ≥16 points
- No more than 3 traits at 7+
- At least 3 traits at ≤3

## Matching Algorithm Integration

### Weighted Scoring

When computing matches:

```typescript
score = sum(
  avatarStat[trait] * quizScore[trait] * (selected[trait] ? 2.5 : 1.0)
)
```

### Example Match Calculation

User selects: `['strength', 'courage', 'discipline']`  
Quiz results: `{ strength: 0.9, courage: 0.8, discipline: 0.7, ... }`

**Warrior** score:
```
= (10 * 0.9 * 2.5) + (8 * 0.8 * 2.5) + (6 * 0.7 * 1.0) + ...
= 22.5 + 16.0 + 4.2 + ...
= ~85.7
```

**Scholar** score would be lower since wisdom/curiosity weren't selected and have lower quiz scores.

## Avatar Display Patterns

### Result Screen

Show matched avatar with:
- Name and description
- Primary/secondary trait badges
- Stat visualization (radar chart)
- Explanation of why matched

### Progress Screen

Display avatar as:
- Profile icon
- Level indicator overlay
- XP progress bar beneath
- Unlockable cosmetic variants at milestones

## Color Palette Usage

Each avatar color should be used for:
- Avatar card background (10% opacity)
- Trait tags and badges
- Progress indicators
- Button accents in avatar context

Ensure WCAG AA contrast compliance when using avatar colors for text.
