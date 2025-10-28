import { View, Text, ScrollView, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { FirstTaskCard } from '@/components/onboarding/FirstTaskCard';
import { useOnboardingStore } from '@/store/onboarding';
import { useUserStore } from '@/store/user';
import { AVATARS } from '@/data/avatars';

export default function StartScreen() {
  const router = useRouter();
  const onboarding = useOnboardingStore();
  const { completeOnboarding } = useUserStore();

  const avatar = AVATARS.find(a => a.id === onboarding.matchedAvatarId);
  const firstTask = onboarding.weeklyPlan?.weeks[0]?.tasks[0];

  const handleStart = () => {
    // Save onboarding data
    completeOnboarding({
      avatarId: onboarding.matchedAvatarId!,
      selectedTraits: onboarding.selectedTraits,
      weeklyPlan: onboarding.weeklyPlan!,
      permissions: onboarding.permissions,
    });

    // Reset onboarding state
    onboarding.reset();

    // Navigate to main app
    router.replace('/dashboard');
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ flexGrow: 1 }}
      >
        <View className="flex-1 px-6 pb-8">
          {/* Success Header */}
          <View className="items-center mt-12 mb-8">
            <View className="w-24 h-24 bg-green-100 rounded-full items-center justify-center mb-6">
              <Text className="text-5xl">✨</Text>
            </View>

            <Text className="text-3xl font-bold text-gray-900 text-center mb-3">
              You're All Set!
            </Text>

            <Text className="text-lg text-gray-600 text-center leading-relaxed">
              Welcome to your transformation journey as
            </Text>

            <Text className="text-2xl font-bold text-primary text-center mt-2">
              {avatar?.name}
            </Text>
          </View>

          {/* First Task Preview */}
          {firstTask && (
            <View className="mb-8">
              <Text className="text-lg font-bold text-gray-900 mb-4">
                Your First Challenge
              </Text>
              <FirstTaskCard task={firstTask} />
            </View>
          )}

          {/* Summary Stats */}
          <View className="bg-gray-50 rounded-2xl p-6 mb-8">
            <Text className="text-lg font-bold text-gray-900 mb-4">
              Your Journey Summary
            </Text>

            <View className="space-y-3">
              <View className="flex-row justify-between">
                <Text className="text-gray-600">Avatar</Text>
                <Text className="font-semibold text-gray-900">
                  {avatar?.name}
                </Text>
              </View>

              <View className="flex-row justify-between">
                <Text className="text-gray-600">Traits</Text>
                <Text className="font-semibold text-gray-900">
                  {onboarding.selectedTraits.length} selected
                </Text>
              </View>

              <View className="flex-row justify-between">
                <Text className="text-gray-600">Duration</Text>
                <Text className="font-semibold text-gray-900">
                  8 weeks
                </Text>
              </View>

              <View className="flex-row justify-between">
                <Text className="text-gray-600">Total Tasks</Text>
                <Text className="font-semibold text-gray-900">
                  {onboarding.weeklyPlan?.weeks.reduce((acc, week) =>
                    acc + week.tasks.length, 0
                  )}
                </Text>
              </View>
            </View>
          </View>

          {/* Motivational Message */}
          <View className="bg-gradient-to-r from-primary/10 to-secondary/10 p-6 rounded-2xl mb-8">
            <Text className="text-center text-base text-gray-700 leading-relaxed">
              "The journey of a thousand miles begins with a single step.
              Today, you take that step toward your Full Potential."
            </Text>
          </View>

          {/* CTA Button */}
          <Pressable
            onPress={handleStart}
            className="bg-primary py-4 rounded-2xl active:bg-primary-dark"
          >
            <LinearGradient
              colors={['#4F46E5', '#6366F1']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              className="py-4 rounded-2xl"
            >
              <Text className="text-white text-center text-lg font-bold">
                Begin Your Journey
              </Text>
            </LinearGradient>
          </Pressable>

          <View className="h-8" />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}