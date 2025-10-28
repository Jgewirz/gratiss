import { View, Text } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { usePathname } from 'expo-router';
import { ONBOARDING_STEPS } from '@/lib/routing';

export function ProgressHeader() {
  const insets = useSafeAreaInsets();
  const pathname = usePathname();

  // Extract step name from pathname
  const currentStepName = pathname.split('/').pop() || 'welcome';
  const currentStepIndex = ONBOARDING_STEPS.indexOf(currentStepName as any);
  const progress = ((currentStepIndex + 1) / ONBOARDING_STEPS.length) * 100;

  return (
    <View
      className="bg-white border-b border-gray-100 px-6 pb-4"
      style={{ paddingTop: insets.top + 12 }}
    >
      <View className="flex-row justify-between items-center mb-2">
        <Text className="text-xs text-gray-600">
          Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length}
        </Text>
        <Text className="text-xs font-semibold text-primary">
          {Math.round(progress)}%
        </Text>
      </View>

      <View className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <View
          className="h-full bg-primary rounded-full"
          style={{ width: `${progress}%` }}
        />
      </View>
    </View>
  );
}