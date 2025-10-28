export type TraitKey =
  | 'mindfulness'
  | 'discipline'
  | 'productivity'
  | 'focus'
  | 'self-awareness'
  | 'confidence'
  | 'resilience'
  | 'creativity'
  | 'learning'
  | 'wellbeing';

export interface Trait {
  key: TraitKey;
  label: string;
  emoji: string;
  description: string;
  color: string;
}

export const TRAITS: Trait[] = [
  {
    key: 'mindfulness',
    label: 'Mindfulness',
    emoji: '🧘',
    description: 'Cultivate present-moment awareness and inner peace',
    color: '#8B5CF6', // purple
  },
  {
    key: 'discipline',
    label: 'Discipline',
    emoji: '⚔️',
    description: 'Build unwavering self-control and consistency',
    color: '#EF4444', // red
  },
  {
    key: 'productivity',
    label: 'Productivity',
    emoji: '🚀',
    description: 'Maximize output and achieve more in less time',
    color: '#3B82F6', // blue
  },
  {
    key: 'focus',
    label: 'Focus',
    emoji: '🎯',
    description: 'Develop laser-sharp concentration and deep work',
    color: '#F59E0B', // amber
  },
  {
    key: 'self-awareness',
    label: 'Self-Awareness',
    emoji: '🪞',
    description: 'Understand your thoughts, emotions, and behaviors',
    color: '#EC4899', // pink
  },
  {
    key: 'confidence',
    label: 'Confidence',
    emoji: '🦁',
    description: 'Build unshakeable belief in yourself',
    color: '#F97316', // orange
  },
  {
    key: 'resilience',
    label: 'Resilience',
    emoji: '🛡️',
    description: 'Bounce back stronger from setbacks',
    color: '#10B981', // emerald
  },
  {
    key: 'creativity',
    label: 'Creativity',
    emoji: '🎨',
    description: 'Unlock innovative thinking and expression',
    color: '#A855F7', // violet
  },
  {
    key: 'learning',
    label: 'Growth',
    emoji: '🌱',
    description: 'Continuous learning and personal evolution',
    color: '#22C55E', // green
  },
  {
    key: 'wellbeing',
    label: 'Wellbeing',
    emoji: '💚',
    description: 'Holistic health across mind, body, and spirit',
    color: '#06B6D4', // cyan
  },
];