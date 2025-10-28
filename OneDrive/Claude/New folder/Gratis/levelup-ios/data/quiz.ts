import type { TraitKey } from './traits';

export interface QuizQuestion {
  id: string;
  text: string;
  category: TraitKey;
  type: 'agreement' | 'preference' | 'frequency';
}

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 'q1',
    text: 'I find myself most energized when learning something completely new',
    category: 'learning',
    type: 'agreement',
  },
  {
    id: 'q2',
    text: 'I prefer having a strict routine and rarely deviate from it',
    category: 'discipline',
    type: 'agreement',
  },
  {
    id: 'q3',
    text: 'I often lose track of time when deeply focused on a task',
    category: 'focus',
    type: 'frequency',
  },
  {
    id: 'q4',
    text: 'I bounce back quickly from setbacks and see them as opportunities',
    category: 'resilience',
    type: 'agreement',
  },
  {
    id: 'q5',
    text: 'I regularly practice meditation or mindfulness exercises',
    category: 'mindfulness',
    type: 'frequency',
  },
  {
    id: 'q6',
    text: 'I enjoy taking charge and leading others toward a goal',
    category: 'confidence',
    type: 'preference',
  },
  {
    id: 'q7',
    text: 'I prioritize efficiency and getting maximum results with minimum effort',
    category: 'productivity',
    type: 'agreement',
  },
  {
    id: 'q8',
    text: 'I often come up with unconventional solutions to problems',
    category: 'creativity',
    type: 'frequency',
  },
  {
    id: 'q9',
    text: 'I spend time reflecting on my emotions and understanding why I feel certain ways',
    category: 'self-awareness',
    type: 'frequency',
  },
  {
    id: 'q10',
    text: 'I maintain a good balance between work, health, and relationships',
    category: 'wellbeing',
    type: 'agreement',
  },
];

export const LIKERT_SCALE = [
  { value: 1, label: 'Strongly Disagree', emoji: '😔' },
  { value: 2, label: 'Disagree', emoji: '🙁' },
  { value: 3, label: 'Neutral', emoji: '😐' },
  { value: 4, label: 'Agree', emoji: '🙂' },
  { value: 5, label: 'Strongly Agree', emoji: '😄' },
];