import type { TraitKey } from './traits';

export interface Avatar {
  id: string;
  name: string;
  emoji: string;
  description: string;
  strengths: string[];
  primaryTraits: TraitKey[];
  secondaryTraits: TraitKey[];
  stats: {
    discipline: number;
    focus: number;
    growth: number;
  };
  color: string;
  gradient: [string, string];
}

export const AVATARS: Avatar[] = [
  {
    id: 'scholar',
    name: 'The Scholar',
    emoji: '📚',
    description: 'A lifelong learner who seeks wisdom through knowledge and understanding. You thrive on intellectual challenges and continuous education.',
    strengths: [
      'Deep analytical thinking',
      'Rapid knowledge acquisition',
      'Pattern recognition',
      'Teaching and mentoring others',
    ],
    primaryTraits: ['learning', 'focus', 'self-awareness'],
    secondaryTraits: ['productivity', 'creativity'],
    stats: { discipline: 7, focus: 9, growth: 10 },
    color: '#6366F1',
    gradient: ['#6366F1', '#8B5CF6'],
  },
  {
    id: 'warrior',
    name: 'The Warrior',
    emoji: '⚔️',
    description: 'A disciplined fighter who conquers challenges through strength and determination. You embody courage and never back down from adversity.',
    strengths: [
      'Unbreakable willpower',
      'Physical and mental toughness',
      'Leadership under pressure',
      'Tactical execution',
    ],
    primaryTraits: ['discipline', 'resilience', 'confidence'],
    secondaryTraits: ['focus', 'wellbeing'],
    stats: { discipline: 10, focus: 8, growth: 6 },
    color: '#EF4444',
    gradient: ['#EF4444', '#F97316'],
  },
  {
    id: 'sage',
    name: 'The Sage',
    emoji: '🧙',
    description: 'A wise mentor who finds truth through mindfulness and reflection. You guide others with insight gained from deep introspection.',
    strengths: [
      'Emotional intelligence',
      'Intuitive wisdom',
      'Calm under chaos',
      'Spiritual connection',
    ],
    primaryTraits: ['mindfulness', 'self-awareness', 'wellbeing'],
    secondaryTraits: ['learning', 'creativity'],
    stats: { discipline: 6, focus: 10, growth: 8 },
    color: '#8B5CF6',
    gradient: ['#8B5CF6', '#A855F7'],
  },
  {
    id: 'builder',
    name: 'The Builder',
    emoji: '🏗️',
    description: 'A productive creator who transforms ideas into reality. You excel at systematic execution and bringing visions to life.',
    strengths: [
      'Systems thinking',
      'Efficient execution',
      'Project management',
      'Resource optimization',
    ],
    primaryTraits: ['productivity', 'discipline', 'focus'],
    secondaryTraits: ['creativity', 'learning'],
    stats: { discipline: 9, focus: 7, growth: 7 },
    color: '#3B82F6',
    gradient: ['#3B82F6', '#06B6D4'],
  },
  {
    id: 'monk',
    name: 'The Monk',
    emoji: '☯️',
    description: 'A focused minimalist who achieves mastery through simplicity. You find power in elimination and depth over breadth.',
    strengths: [
      'Deep concentration',
      'Minimalist mindset',
      'Inner peace',
      'Mastery through repetition',
    ],
    primaryTraits: ['focus', 'mindfulness', 'discipline'],
    secondaryTraits: ['self-awareness', 'wellbeing'],
    stats: { discipline: 8, focus: 10, growth: 5 },
    color: '#F59E0B',
    gradient: ['#F59E0B', '#FCD34D'],
  },
  {
    id: 'leader',
    name: 'The Leader',
    emoji: '👑',
    description: 'A confident influencer who inspires and guides others to greatness. You naturally command respect and create positive change.',
    strengths: [
      'Charismatic influence',
      'Strategic vision',
      'Team empowerment',
      'Decisive action',
    ],
    primaryTraits: ['confidence', 'resilience', 'productivity'],
    secondaryTraits: ['discipline', 'self-awareness'],
    stats: { discipline: 7, focus: 6, growth: 9 },
    color: '#F97316',
    gradient: ['#F97316', '#FCD34D'],
  },
  {
    id: 'phoenix',
    name: 'The Phoenix',
    emoji: '🔥',
    description: 'A resilient transformer who rises stronger from every setback. You embody the power of reinvention and continuous rebirth.',
    strengths: [
      'Adaptability',
      'Recovery from failure',
      'Transformation catalyst',
      'Emotional resilience',
    ],
    primaryTraits: ['resilience', 'self-awareness', 'learning'],
    secondaryTraits: ['confidence', 'wellbeing'],
    stats: { discipline: 6, focus: 7, growth: 10 },
    color: '#10B981',
    gradient: ['#10B981', '#22C55E'],
  },
  {
    id: 'artist',
    name: 'The Artist',
    emoji: '🎨',
    description: 'A creative visionary who sees beauty and possibility everywhere. You express yourself through innovation and imagination.',
    strengths: [
      'Creative problem-solving',
      'Aesthetic sense',
      'Emotional expression',
      'Outside-the-box thinking',
    ],
    primaryTraits: ['creativity', 'self-awareness', 'mindfulness'],
    secondaryTraits: ['learning', 'wellbeing'],
    stats: { discipline: 5, focus: 8, growth: 9 },
    color: '#A855F7',
    gradient: ['#A855F7', '#EC4899'],
  },
  {
    id: 'explorer',
    name: 'The Explorer',
    emoji: '🧭',
    description: 'An adventurous pioneer who thrives on discovery and new experiences. You push boundaries and chart unknown territories.',
    strengths: [
      'Curiosity and wonder',
      'Risk-taking courage',
      'Diverse experiences',
      'Boundary pushing',
    ],
    primaryTraits: ['learning', 'creativity', 'confidence'],
    secondaryTraits: ['resilience', 'wellbeing'],
    stats: { discipline: 5, focus: 6, growth: 10 },
    color: '#22C55E',
    gradient: ['#22C55E', '#10B981'],
  },
  {
    id: 'guardian',
    name: 'The Guardian',
    emoji: '🛡️',
    description: 'A balanced protector who maintains harmony across all life domains. You excel at sustainable growth and holistic wellbeing.',
    strengths: [
      'Life balance',
      'Protective instincts',
      'Sustainable habits',
      'Nurturing support',
    ],
    primaryTraits: ['wellbeing', 'resilience', 'mindfulness'],
    secondaryTraits: ['self-awareness', 'discipline'],
    stats: { discipline: 8, focus: 7, growth: 8 },
    color: '#06B6D4',
    gradient: ['#06B6D4', '#3B82F6'],
  },
];