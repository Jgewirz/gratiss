// All app copy/text content in one place for easy updates

export const COPY = {
  welcome: {
    title: 'Unlock Your Full Potential',
    subtitle: 'Transform your life through personalized growth challenges and gamified habits',
    features: [
      {
        emoji: '🎯',
        title: 'Personalized Avatar',
        description: 'Discover your unique archetype through our personality assessment',
      },
      {
        emoji: '📈',
        title: 'Progressive Challenges',
        description: 'Start easy and build momentum with research-backed task progression',
      },
      {
        emoji: '🎮',
        title: 'Gamified Growth',
        description: 'Earn XP, level up, and unlock achievements as you improve',
      },
      {
        emoji: '🏆',
        title: '8-Week Transformation',
        description: 'Structured journey from beginner to mastery in your chosen traits',
      },
    ],
    cta: 'Begin Your Journey',
  },

  traits: {
    title: 'Choose Your Path',
    subtitle: 'Select up to 3 traits that resonate with your growth journey',
    maxReachedTitle: 'Maximum Reached',
    maxReachedMessage: 'You can select up to 3 traits. Deselect one to choose another.',
    minRequiredTitle: 'Select Traits',
    minRequiredMessage: 'Please select at least one trait to continue.',
  },

  quiz: {
    title: 'Personality Assessment',
    progressLabel: 'Question',
    lastQuestionHint: 'Last question! Review your journey after this.',
    defaultHint: 'Your answers help us find your perfect avatar archetype',
  },

  avatarResult: {
    subtitle: 'Your Avatar Archetype',
    strengthsTitle: 'Core Strengths',
    matchTitle: 'Perfect Match For Your Traits',
    matchDescription: 'Your selected traits align perfectly with {avatarName}\'s path to mastery. This archetype will guide you through personalized challenges designed for maximum growth.',
  },

  planPreview: {
    title: 'Your 8-Week Journey',
    subtitle: 'A progressive plan tailored to your avatar and traits',
    goalTitle: 'Full Potential in 8 Weeks',
    goalSubtitle: 'Research-backed progression system',
    howItWorksTitle: 'How It Works',
    features: [
      {
        icon: '📈',
        title: 'Progressive Difficulty',
        description: 'Tasks gradually increase in challenge each week',
      },
      {
        icon: '🎮',
        title: 'XP & Levels',
        description: 'Earn experience points and level up your avatar',
      },
      {
        icon: '🏆',
        title: 'Achievements',
        description: 'Unlock badges and rewards for consistency',
      },
    ],
    lockedWeeksTitle: 'Weeks 5-8: Advanced Mastery',
    lockedWeeksDescription: 'Unlock harder challenges as you progress',
  },

  permissions: {
    title: 'Enhance Your Experience',
    subtitle: 'Enable features to maximize your growth potential',
    benefitsTitle: 'Why Enable Permissions?',
    benefits: [
      'Never miss a task with smart reminders',
      'Track progress automatically',
      'Sync with health apps for holistic growth',
    ],
    notifications: {
      title: 'Daily Reminders',
      description: 'Get gentle nudges to complete your daily tasks and maintain streaks',
      enabledHint: 'We\'ll send reminders at optimal times based on your habits',
    },
    health: {
      title: 'Health Integration',
      description: 'Sync with Apple Health to track wellness goals automatically',
      enabledHint: 'Auto-complete fitness tasks when workouts are detected',
    },
    analytics: {
      title: 'Progress Tracking',
      description: 'Always enabled to track your journey and provide insights',
    },
    privacyTitle: 'Your Privacy Matters',
    privacyDescription: 'We never share your data. All information is encrypted and used solely to enhance your personal growth journey. You can change these settings anytime.',
  },

  EVIDENCE_CONSENT: {
    title: 'Photo Evidence Privacy',
    description: 'When you enable photo evidence for tasks:',
    points: [
      'Photos are stored locally on your device only',
      'EXIF location data is automatically removed',
      'Avoid including faces or personal identifying information',
      'Photos are queued offline and can be reviewed before syncing',
      'You can preview and delete any photo before it\'s saved',
      'No photos are shared without your explicit consent',
    ],
    consentText: 'I understand and agree to these privacy practices',
  },

  stakes: {
    title: 'Accountability Stakes',
    subtitle: 'Stay motivated with optional daily accountability',
    description: 'Enable $1/day stakes to maintain your commitment',
    safetyTitle: 'Your Safety Net',
    safetyPoints: [
      'Maximum one charge per day ($1 cap)',
      'One free weekly grace day for emergencies',
      'Pause Week feature for vacations or illness',
      '4-hour grace period (midnight to 4am counts as previous day)',
      'Cancel anytime with no penalty',
      'All charges go toward app development and charity',
    ],
    weeklyGraceTitle: 'Weekly Grace',
    weeklyGraceDescription: 'You get one free miss per week without charge. Resets every Monday.',
    pauseWeekTitle: 'Pause Week',
    pauseWeekDescription: 'Going on vacation or feeling unwell? Pause your stakes for up to 7 days.',
    enableButton: 'Enable Stakes ($1/day)',
    disableButton: 'Continue Without Stakes',
  },

  start: {
    title: 'You\'re All Set!',
    subtitle: 'Welcome to your transformation journey as',
    firstTaskTitle: 'Your First Challenge',
    summaryTitle: 'Your Journey Summary',
    summaryLabels: {
      avatar: 'Avatar',
      traits: 'Traits',
      duration: 'Duration',
      totalTasks: 'Total Tasks',
    },
    motivationalQuote: 'The journey of a thousand miles begins with a single step. Today, you take that step toward your Full Potential.',
    ctaButton: 'Begin Your Journey',
  },

  common: {
    continue: 'Continue',
    back: 'Back',
    next: 'Next',
    skip: 'Skip',
    done: 'Done',
    cancel: 'Cancel',
    save: 'Save',
    loading: 'Loading...',
    error: 'Something went wrong',
    tryAgain: 'Try Again',
  },

  errors: {
    maxTraitsReached: 'Maximum 3 traits allowed',
    minTraitsRequired: 'Select at least one trait',
    quizIncomplete: 'Please answer all questions',
    invalidAnswer: 'Please select a valid answer',
    planGenerationFailed: 'Failed to generate plan. Please try again.',
  },

  achievements: {
    firstStep: {
      title: 'First Step',
      description: 'Complete your first task',
    },
    weekWarrior: {
      title: 'Week Warrior',
      description: 'Complete all tasks in a week',
    },
    consistent7: {
      title: 'Consistent',
      description: '7-day streak achieved',
    },
    unstoppable30: {
      title: 'Unstoppable',
      description: '30-day streak achieved',
    },
    risingStar: {
      title: 'Rising Star',
      description: 'Reach level 5',
    },
    master: {
      title: 'Master',
      description: 'Reach level 10',
    },
    fullPotential: {
      title: 'Full Potential',
      description: 'Reach 1000 XP',
    },
  },

  dashboard: {
    greeting: {
      morning: 'Good morning',
      afternoon: 'Good afternoon',
      evening: 'Good evening',
    },
    todaysTasks: 'Today\'s Tasks',
    streakCounter: '{count} day streak',
    xpProgress: '{current} / {next} XP',
    levelLabel: 'Level {level}',
    completeButton: 'Complete',
    skipButton: 'Skip Today',
  },
};