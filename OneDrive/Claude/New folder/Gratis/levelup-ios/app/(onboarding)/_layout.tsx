import { Stack } from 'expo-router';
import { View } from 'react-native';
import { ProgressHeader } from '@/components/onboarding/ProgressHeader';

export default function OnboardingLayout() {
  return (
    <View className="flex-1 bg-gray-50">
      <ProgressHeader />
      <Stack
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="welcome" />
        <Stack.Screen name="select-traits" />
        <Stack.Screen name="quiz" />
        <Stack.Screen name="avatar-result" />
        <Stack.Screen name="plan-preview" />
        <Stack.Screen name="permissions" />
        <Stack.Screen name="start" />
      </Stack>
    </View>
  );
}