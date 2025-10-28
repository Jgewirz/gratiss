import type { TraitKey } from '@/data/traits';

// Validation functions
export function assertMaxThreeTraits(traits: TraitKey[]): void {
  if (traits.length > 3) {
    throw new Error('Maximum of 3 traits can be selected');
  }
}

export function assertMinOneTrait(traits: TraitKey[]): void {
  if (traits.length < 1) {
    throw new Error('At least one trait must be selected');
  }
}

export function assertLikert1to5(value: number): void {
  if (!Number.isInteger(value) || value < 1 || value > 5) {
    throw new Error('Value must be an integer between 1 and 5');
  }
}

export function validateQuizAnswers(
  answers: Record<string, number>,
  totalQuestions: number
): boolean {
  const answerCount = Object.keys(answers).length;

  if (answerCount !== totalQuestions) {
    return false;
  }

  // Check all answers are valid Likert values
  for (const value of Object.values(answers)) {
    if (!Number.isInteger(value) || value < 1 || value > 5) {
      return false;
    }
  }

  return true;
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validateUsername(username: string): boolean {
  // Username must be 3-20 characters, alphanumeric with underscores
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
  return usernameRegex.test(username);
}

// Type guards
export function isValidTraitKey(key: string): key is TraitKey {
  const validTraits: TraitKey[] = [
    'mindfulness',
    'discipline',
    'productivity',
    'focus',
    'self-awareness',
    'confidence',
    'resilience',
    'creativity',
    'learning',
    'wellbeing',
  ];
  return validTraits.includes(key as TraitKey);
}

export function isValidDifficulty(
  difficulty: string
): difficulty is 'easy' | 'medium' | 'hard' {
  return ['easy', 'medium', 'hard'].includes(difficulty);
}

// Sanitization functions
export function sanitizeInput(input: string): string {
  return input.trim().replace(/[<>]/g, '');
}

export function sanitizeNumber(value: any, min: number, max: number): number {
  const num = Number(value);
  if (isNaN(num)) return min;
  return Math.max(min, Math.min(max, num));
}

// Validation schemas for forms
export interface OnboardingValidation {
  traits: TraitKey[];
  quizAnswers: Record<string, number>;
  permissions: {
    notifications: boolean;
    health: boolean;
  };
}

export function validateOnboardingData(
  data: Partial<OnboardingValidation>
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Validate traits
  if (!data.traits || data.traits.length === 0) {
    errors.push('Please select at least one trait');
  } else if (data.traits.length > 3) {
    errors.push('Maximum of 3 traits allowed');
  }

  // Validate quiz answers
  if (!data.quizAnswers || Object.keys(data.quizAnswers).length !== 10) {
    errors.push('Please complete all quiz questions');
  } else {
    for (const [key, value] of Object.entries(data.quizAnswers)) {
      if (!Number.isInteger(value) || value < 1 || value > 5) {
        errors.push(`Invalid answer for question ${key}`);
      }
    }
  }

  // Permissions are optional, so no validation needed

  return {
    isValid: errors.length === 0,
    errors,
  };
}