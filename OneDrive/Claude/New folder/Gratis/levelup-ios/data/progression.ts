import type { TraitKey } from './traits';

export interface Task {
  id: string;
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  duration: number; // in minutes
  category: TraitKey;
  xpReward: number;
  icon: string;
  evidenceMode: 'check' | 'timer' | 'photo';
}

export interface WeekPlan {
  week: number;
  theme: string;
  description: string;
  tasks: Task[];
  activeDays: number[]; // Day numbers (1-7) when tasks are scheduled
  restDays: number[];   // Day numbers (1-7) for rest
  totalMinutes: number; // Total minutes for the week
}

export interface WeeklyPlan {
  avatarId: string;
  totalWeeks: number;
  weeks: WeekPlan[];
}

// Week progression templates with wave-linear bounds
const WEEK_TEMPLATES = {
  1: { minMinutes: 15, maxMinutes: 25, difficulty: 'easy' as const, avgMinutes: 20 },
  2: { minMinutes: 20, maxMinutes: 30, difficulty: 'easy' as const, avgMinutes: 25 },
  3: { minMinutes: 25, maxMinutes: 35, difficulty: 'medium' as const, avgMinutes: 30 },
  4: { minMinutes: 30, maxMinutes: 40, difficulty: 'medium' as const, avgMinutes: 35 },
  5: { minMinutes: 35, maxMinutes: 45, difficulty: 'medium' as const, avgMinutes: 40 },
  6: { minMinutes: 32, maxMinutes: 42, difficulty: 'medium' as const, avgMinutes: 37 }, // Micro-deload
  7: { minMinutes: 40, maxMinutes: 55, difficulty: 'hard' as const, avgMinutes: 47 },
  8: { minMinutes: 45, maxMinutes: 60, difficulty: 'hard' as const, avgMinutes: 52 },
};

// Task templates by trait and difficulty
const TASK_TEMPLATES: Record<TraitKey, Record<'easy' | 'medium' | 'hard', Array<{
  title: string;
  description: string;
  duration: number;
  icon: string;
}>>> = {
  mindfulness: {
    easy: [
      { title: '5-minute breathing', description: 'Practice box breathing for 5 minutes', duration: 5, icon: '🫁' },
      { title: 'Gratitude moment', description: 'Write 3 things you\'re grateful for', duration: 5, icon: '🙏' },
      { title: 'Mindful minute', description: 'One minute of present awareness', duration: 1, icon: '🧘' },
    ],
    medium: [
      { title: '10-minute meditation', description: 'Guided or silent meditation', duration: 10, icon: '🧘' },
      { title: 'Mindful walk', description: 'Take a walk focusing on sensations', duration: 15, icon: '🚶' },
      { title: 'Body awareness', description: 'Progressive muscle relaxation', duration: 12, icon: '🔍' },
    ],
    hard: [
      { title: '20-minute meditation', description: 'Deep meditation session', duration: 20, icon: '🧘‍♂️' },
      { title: 'Body scan', description: 'Complete body scan meditation', duration: 25, icon: '🔍' },
      { title: 'Loving kindness', description: 'Metta meditation practice', duration: 30, icon: '❤️' },
    ],
  },
  discipline: {
    easy: [
      { title: 'Make your bed', description: 'Start the day with discipline', duration: 2, icon: '🛏️' },
      { title: 'No snooze', description: 'Wake up without hitting snooze', duration: 1, icon: '⏰' },
      { title: 'Clean workspace', description: 'Organize your work area', duration: 10, icon: '🧹' },
    ],
    medium: [
      { title: 'Cold shower', description: 'Take a 2-minute cold shower', duration: 5, icon: '🚿' },
      { title: 'Digital detox', description: '1 hour without phone/social media', duration: 60, icon: '📵' },
      { title: 'Morning routine', description: 'Complete full morning routine', duration: 30, icon: '☀️' },
    ],
    hard: [
      { title: 'Early workout', description: 'Complete workout before 7am', duration: 45, icon: '💪' },
      { title: '4-hour deep work', description: 'No distractions for 4 hours', duration: 240, icon: '🎯' },
      { title: 'Dopamine fast', description: 'No stimulation for 2 hours', duration: 120, icon: '🚫' },
    ],
  },
  productivity: {
    easy: [
      { title: 'Plan tomorrow', description: 'Write tomorrow\'s top 3 tasks', duration: 5, icon: '📝' },
      { title: 'Inbox zero', description: 'Clear your email inbox', duration: 15, icon: '📧' },
      { title: 'Quick wins', description: 'Complete 3 small tasks', duration: 10, icon: '✅' },
    ],
    medium: [
      { title: 'Pomodoro session', description: '25 min focused work', duration: 25, icon: '🍅' },
      { title: 'Weekly review', description: 'Review and plan your week', duration: 30, icon: '📊' },
      { title: 'Time blocking', description: 'Plan your day in blocks', duration: 15, icon: '📅' },
    ],
    hard: [
      { title: 'Deep work block', description: '2 hours uninterrupted work', duration: 120, icon: '🔥' },
      { title: 'Complete project', description: 'Finish a pending project', duration: 180, icon: '✅' },
      { title: 'System design', description: 'Design a productivity system', duration: 90, icon: '⚙️' },
    ],
  },
  focus: {
    easy: [
      { title: 'Single-task', description: 'Complete one task without switching', duration: 15, icon: '🎯' },
      { title: 'Phone-free meal', description: 'Eat without distractions', duration: 20, icon: '🍽️' },
      { title: 'Focus breathing', description: '5 minutes of focused breathing', duration: 5, icon: '💨' },
    ],
    medium: [
      { title: 'Flow state', description: '45 min deep focus session', duration: 45, icon: '🌊' },
      { title: 'Reading sprint', description: 'Read for 30 min without breaks', duration: 30, icon: '📖' },
      { title: 'Focus challenge', description: 'Complete task with timer', duration: 25, icon: '⏱️' },
    ],
    hard: [
      { title: 'Marathon focus', description: '90 min unbroken concentration', duration: 90, icon: '🏃' },
      { title: 'Learn new skill', description: '2 hours learning something new', duration: 120, icon: '🎓' },
      { title: 'Deep thinking', description: '1 hour problem solving', duration: 60, icon: '🧠' },
    ],
  },
  'self-awareness': {
    easy: [
      { title: 'Mood check', description: 'Log your current emotional state', duration: 2, icon: '😊' },
      { title: 'Journal entry', description: 'Write about your day', duration: 10, icon: '✍️' },
      { title: 'Feeling scan', description: 'Name 3 current feelings', duration: 3, icon: '💭' },
    ],
    medium: [
      { title: 'Values reflection', description: 'Identify your core values', duration: 20, icon: '💭' },
      { title: 'Feedback request', description: 'Ask for honest feedback', duration: 15, icon: '💬' },
      { title: 'Pattern tracking', description: 'Identify behavior patterns', duration: 25, icon: '📊' },
    ],
    hard: [
      { title: 'Life audit', description: 'Review all life areas', duration: 60, icon: '🔍' },
      { title: 'Shadow work', description: 'Explore difficult emotions', duration: 45, icon: '🌑' },
      { title: 'Deep reflection', description: 'Examine core beliefs', duration: 50, icon: '🪞' },
    ],
  },
  confidence: {
    easy: [
      { title: 'Power pose', description: '2 min confidence pose', duration: 2, icon: '🦸' },
      { title: 'Compliment yourself', description: 'List 3 strengths', duration: 5, icon: '⭐' },
      { title: 'Win list', description: 'Write 3 recent wins', duration: 5, icon: '🏆' },
    ],
    medium: [
      { title: 'Speak up', description: 'Share opinion in meeting/group', duration: 10, icon: '🗣️' },
      { title: 'New introduction', description: 'Introduce yourself to someone', duration: 10, icon: '👋' },
      { title: 'Skill showcase', description: 'Demonstrate a skill publicly', duration: 20, icon: '✨' },
    ],
    hard: [
      { title: 'Public speaking', description: 'Present to a group', duration: 30, icon: '🎤' },
      { title: 'Bold request', description: 'Ask for something challenging', duration: 15, icon: '💪' },
      { title: 'Leadership task', description: 'Lead a group activity', duration: 45, icon: '👑' },
    ],
  },
  resilience: {
    easy: [
      { title: 'Reframe thought', description: 'Turn negative to positive', duration: 5, icon: '🔄' },
      { title: 'Stress breather', description: '5 min stress relief', duration: 5, icon: '😮‍💨' },
      { title: 'Gratitude practice', description: 'Find silver linings', duration: 5, icon: '🌈' },
    ],
    medium: [
      { title: 'Face a fear', description: 'Do something slightly scary', duration: 20, icon: '😨' },
      { title: 'Failure review', description: 'Learn from a mistake', duration: 15, icon: '📈' },
      { title: 'Stress workout', description: 'Physical stress relief', duration: 30, icon: '🏃' },
    ],
    hard: [
      { title: 'Comfort zone break', description: 'Major comfort zone exit', duration: 60, icon: '🚀' },
      { title: 'Difficult conversation', description: 'Have that tough talk', duration: 30, icon: '💬' },
      { title: 'Challenge acceptance', description: 'Take on hard challenge', duration: 90, icon: '⛰️' },
    ],
  },
  creativity: {
    easy: [
      { title: 'Doodle break', description: '5 min free drawing', duration: 5, icon: '✏️' },
      { title: 'Word association', description: 'Creative word game', duration: 5, icon: '💭' },
      { title: 'Random photo', description: 'Take an artistic photo', duration: 3, icon: '📸' },
    ],
    medium: [
      { title: 'Create something', description: 'Make art/music/writing', duration: 30, icon: '🎨' },
      { title: 'Brainstorm ideas', description: '20 ideas on any topic', duration: 15, icon: '💡' },
      { title: 'Remix project', description: 'Reimagine existing work', duration: 25, icon: '🔀' },
    ],
    hard: [
      { title: 'Complete project', description: 'Finish creative project', duration: 120, icon: '🎭' },
      { title: 'Share creation', description: 'Publish/share your work', duration: 30, icon: '🌟' },
      { title: 'Creative marathon', description: '3-hour creation session', duration: 180, icon: '🎪' },
    ],
  },
  learning: {
    easy: [
      { title: 'Learn a fact', description: 'Research something new', duration: 10, icon: '🔍' },
      { title: 'Watch tutorial', description: '10 min educational video', duration: 10, icon: '📺' },
      { title: 'Quick skill', description: 'Learn one small thing', duration: 5, icon: '💡' },
    ],
    medium: [
      { title: 'Read chapter', description: 'Read educational content', duration: 30, icon: '📚' },
      { title: 'Practice skill', description: '30 min skill practice', duration: 30, icon: '⚡' },
      { title: 'Take notes', description: 'Study with note-taking', duration: 25, icon: '📝' },
    ],
    hard: [
      { title: 'Complete course', description: 'Finish online lesson', duration: 90, icon: '🎓' },
      { title: 'Teach someone', description: 'Share your knowledge', duration: 45, icon: '👨‍🏫' },
      { title: 'Deep study', description: '2-hour learning session', duration: 120, icon: '🔬' },
    ],
  },
  wellbeing: {
    easy: [
      { title: 'Hydrate', description: 'Drink 2 glasses of water', duration: 2, icon: '💧' },
      { title: 'Stretch break', description: '5 min stretching', duration: 5, icon: '🤸' },
      { title: 'Fresh air', description: 'Step outside briefly', duration: 5, icon: '🌤️' },
    ],
    medium: [
      { title: 'Healthy meal', description: 'Prepare nutritious food', duration: 30, icon: '🥗' },
      { title: 'Nature time', description: 'Spend time outdoors', duration: 30, icon: '🌳' },
      { title: 'Movement break', description: '15 min physical activity', duration: 15, icon: '🏃' },
    ],
    hard: [
      { title: 'Full workout', description: 'Complete exercise session', duration: 45, icon: '🏋️' },
      { title: 'Meal prep', description: 'Prepare healthy meals', duration: 90, icon: '🍱' },
      { title: 'Recovery session', description: 'Yoga/stretching/massage', duration: 60, icon: '🧘‍♀️' },
    ],
  },
};

/**
 * Deterministically shuffle an array using a seed
 * @param array Array to shuffle
 * @param seed Seed string for determinism
 */
function deterministicShuffle<T>(array: T[], seed: string): T[] {
  const shuffled = [...array];
  let seedNum = 0;
  for (let i = 0; i < seed.length; i++) {
    seedNum += seed.charCodeAt(i);
  }

  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor((seedNum * (i + 1)) % (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    seedNum = (seedNum * 1103515245 + 12345) & 0x7fffffff; // LCG
  }

  return shuffled;
}

/**
 * Generate a weekly plan with wave-linear progression
 * @param selectedTraits User-selected traits (1-3)
 * @param avatarId Avatar ID for deterministic generation
 * @returns 8-week progressive plan
 */
export function generateWeeklyPlan(selectedTraits: TraitKey[], avatarId: string): WeeklyPlan {
  const weeks: WeekPlan[] = [];
  const ACTIVE_DAYS_PER_WEEK = 5;
  const REST_DAYS_PER_WEEK = 2;

  for (let week = 1; week <= 8; week++) {
    const template = WEEK_TEMPLATES[week as keyof typeof WEEK_TEMPLATES];
    const { difficulty, minMinutes, maxMinutes, avgMinutes } = template;

    // Determine active and rest days (Mon-Fri active, Sat-Sun rest by default)
    const activeDays = [1, 2, 3, 4, 5]; // Monday to Friday
    const restDays = [6, 7]; // Saturday, Sunday

    // Calculate tasks needed for this week
    const targetMinutesPerDay = avgMinutes;
    const tasks: Task[] = [];

    // Ensure top trait appears each active day
    const topTrait = selectedTraits[0];

    // Generate tasks for each active day
    for (let dayIndex = 0; dayIndex < ACTIVE_DAYS_PER_WEEK; dayIndex++) {
      let dayMinutes = 0;
      const dayTasks: Task[] = [];

      // Always include one task from the top trait
      const topTraitTemplates = TASK_TEMPLATES[topTrait][difficulty];
      const topTraitTemplate = topTraitTemplates[dayIndex % topTraitTemplates.length];

      const topTask: Task = {
        id: `w${week}d${dayIndex + 1}t1`,
        title: topTraitTemplate.title,
        description: topTraitTemplate.description,
        difficulty,
        duration: topTraitTemplate.duration,
        category: topTrait,
        xpReward: difficulty === 'easy' ? 10 : difficulty === 'medium' ? 20 : 30,
        icon: topTraitTemplate.icon,
        evidenceMode: week >= 5 && dayIndex % 2 === 0 ? 'photo' : (dayIndex % 2 === 0 ? 'timer' : 'check'),
      };

      dayTasks.push(topTask);
      dayMinutes += topTask.duration;

      // Add tasks from other traits to meet minute target
      let taskCount = 1;
      const otherTraits = selectedTraits.slice(1);

      while (dayMinutes < targetMinutesPerDay && taskCount < 3) {
        // Max 3 tasks per day by default
        const traitIndex = taskCount % Math.max(1, otherTraits.length);
        const trait = otherTraits[traitIndex] || topTrait;

        const templates = TASK_TEMPLATES[trait][difficulty];
        const template = templates[(dayIndex + taskCount) % templates.length];

        const task: Task = {
          id: `w${week}d${dayIndex + 1}t${taskCount + 1}`,
          title: template.title,
          description: template.description,
          difficulty,
          duration: template.duration,
          category: trait,
          xpReward: difficulty === 'easy' ? 10 : difficulty === 'medium' ? 20 : 30,
          icon: template.icon,
          evidenceMode: week >= 5 && taskCount === 1 ? 'photo' : (taskCount % 2 === 0 ? 'timer' : 'check'),
        };

        dayTasks.push(task);
        dayMinutes += task.duration;
        taskCount++;
      }

      // Allow 4th task only if still under target minutes
      if (dayMinutes < targetMinutesPerDay - 10 && taskCount === 3) {
        const trait = selectedTraits[dayIndex % selectedTraits.length];
        const templates = TASK_TEMPLATES[trait][difficulty];
        const template = templates[(dayIndex + 3) % templates.length];

        const task: Task = {
          id: `w${week}d${dayIndex + 1}t4`,
          title: template.title,
          description: template.description,
          difficulty,
          duration: Math.min(template.duration, targetMinutesPerDay - dayMinutes + 5),
          category: trait,
          xpReward: difficulty === 'easy' ? 10 : difficulty === 'medium' ? 20 : 30,
          icon: template.icon,
          evidenceMode: 'check', // 4th task always check mode
        };

        dayTasks.push(task);
        dayMinutes += task.duration;
      }

      tasks.push(...dayTasks);
    }

    // Calculate total minutes for the week
    const totalMinutes = tasks.reduce((sum, task) => sum + task.duration, 0);

    weeks.push({
      week,
      theme: `Week ${week}: ${difficulty === 'easy' ? 'Foundation' : difficulty === 'medium' ? 'Building' : 'Mastery'}`,
      description: `Focus on ${selectedTraits.join(', ')} with ${difficulty} challenges`,
      tasks,
      activeDays,
      restDays,
      totalMinutes,
    });
  }

  return {
    avatarId,
    totalWeeks: 8,
    weeks,
  };
}

/**
 * Validate a weekly plan against all constraints
 * @param plan Weekly plan to validate
 * @throws Error if any constraint is violated
 */
export function validatePlan(plan: WeeklyPlan): void {
  const errors: string[] = [];

  plan.weeks.forEach((week, weekIndex) => {
    const weekNum = weekIndex + 1;
    const template = WEEK_TEMPLATES[weekNum as keyof typeof WEEK_TEMPLATES];

    // Check week minute bounds
    const avgMinutesPerDay = week.totalMinutes / week.activeDays.length;
    if (avgMinutesPerDay < template.minMinutes) {
      errors.push(`Week ${weekNum}: Average ${avgMinutesPerDay.toFixed(1)} min/day below minimum ${template.minMinutes}`);
    }
    if (avgMinutesPerDay > template.maxMinutes) {
      errors.push(`Week ${weekNum}: Average ${avgMinutesPerDay.toFixed(1)} min/day above maximum ${template.maxMinutes}`);
    }

    // Check Week 6 micro-deload
    if (weekNum === 6) {
      const week5 = plan.weeks[4];
      const week5Avg = week5.totalMinutes / week5.activeDays.length;
      const week6Avg = avgMinutesPerDay;
      if (week6Avg > week5Avg * 0.9) {
        errors.push(`Week 6: Micro-deload violation - ${week6Avg.toFixed(1)} min/day exceeds 90% of Week 5 (${(week5Avg * 0.9).toFixed(1)})`);
      }
    }

    // Check active/rest days
    if (week.activeDays.length !== 5) {
      errors.push(`Week ${weekNum}: Must have exactly 5 active days, found ${week.activeDays.length}`);
    }
    if (week.restDays.length !== 2) {
      errors.push(`Week ${weekNum}: Must have exactly 2 rest days, found ${week.restDays.length}`);
    }

    // Check task count per day (max 3 default, 4 if needed)
    const tasksPerDay = new Map<number, number>();
    week.tasks.forEach(task => {
      const dayMatch = task.id.match(/d(\d+)t/);
      if (dayMatch) {
        const day = parseInt(dayMatch[1]);
        tasksPerDay.set(day, (tasksPerDay.get(day) || 0) + 1);
      }
    });

    tasksPerDay.forEach((count, day) => {
      if (count > 4) {
        errors.push(`Week ${weekNum} Day ${day}: Too many tasks (${count}), max 4 allowed`);
      }
    });

    // Check evidence gating
    week.tasks.forEach(task => {
      if (weekNum < 5 && task.evidenceMode === 'photo') {
        errors.push(`Week ${weekNum} Task ${task.id}: Photo evidence not allowed before Week 5`);
      }
    });

    // Check difficulty matches week template
    const expectedDifficulty = template.difficulty;
    const wrongDifficultyTasks = week.tasks.filter(t => t.difficulty !== expectedDifficulty);
    if (wrongDifficultyTasks.length > 0) {
      errors.push(`Week ${weekNum}: Found ${wrongDifficultyTasks.length} tasks with wrong difficulty (expected ${expectedDifficulty})`);
    }
  });

  if (errors.length > 0) {
    throw new Error(`Plan validation failed:\n${errors.join('\n')}`);
  }
}