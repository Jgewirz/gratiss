import { useEffect } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useUserStore } from '@/store/user';

export default function HomeScreen() {
  const router = useRouter();
  const hasCompletedOnboarding = useUserStore(state => state.hasCompletedOnboarding);

  useEffect(() => {
    // Check if user has completed onboarding
    if (!hasCompletedOnboarding) {
      router.replace('/onboarding/welcome');
    } else {
      // TODO: Navigate to main app dashboard
      router.replace('/dashboard');
    }
  }, [hasCompletedOnboarding]);

  return (
    <View className="flex-1 items-center justify-center bg-white">
      <ActivityIndicator size="large" color="#4F46E5" />
    </View>
  );
}