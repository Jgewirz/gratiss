export const ONBOARDING_STEPS = [
  'welcome',
  'select-traits',
  'quiz',
  'avatar-result',
  'plan-preview',
  'permissions',
  'start',
] as const;

export type OnboardingStep = (typeof ONBOARDING_STEPS)[number];

export function nextPathFrom(stepKey: OnboardingStep): string {
  const idx = ONBOARDING_STEPS.indexOf(stepKey);
  return idx < ONBOARDING_STEPS.length - 1
    ? `/onboarding/${ONBOARDING_STEPS[idx + 1]}`
    : '/dashboard';
}

export function prevPathFrom(stepKey: OnboardingStep): string {
  const idx = ONBOARDING_STEPS.indexOf(stepKey);
  return idx > 0
    ? `/onboarding/${ONBOARDING_STEPS[idx - 1]}`
    : '/onboarding/welcome';
}

export function getStepIndex(stepKey: string): number {
  return ONBOARDING_STEPS.indexOf(stepKey as OnboardingStep);
}

export function isValidOnboardingStep(step: string): step is OnboardingStep {
  return ONBOARDING_STEPS.includes(step as OnboardingStep);
}