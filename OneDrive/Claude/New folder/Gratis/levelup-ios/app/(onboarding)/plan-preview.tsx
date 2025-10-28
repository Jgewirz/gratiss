import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useEffect } from 'react';
import { StepFooter } from '@/components/onboarding/StepFooter';
import { WeekPlanList } from '@/components/onboarding/WeekPlanList';
import { useOnboardingStore } from '@/store/onboarding';
import { generateWeeklyPlan } from '@/data/progression';

export default function PlanPreviewScreen() {
  const router = useRouter();
  const { matchedAvatarId, selectedTraits, weeklyPlan, buildPlan } = useOnboardingStore();

  useEffect(() => {
    if (!weeklyPlan && matchedAvatarId) {
      const plan = generateWeeklyPlan(matchedAvatarId, selectedTraits);
      buildPlan(plan);
    }
  }, [matchedAvatarId, selectedTraits]);

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1 px-6"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="mt-8 mb-6">
          <Text className="text-3xl font-bold text-gray-900 mb-3">
            Your 8-Week Journey
          </Text>
          <Text className="text-lg text-gray-600 leading-relaxed">
            A progressive plan tailored to your avatar and traits
          </Text>
        </View>

        {/* Journey Overview */}
        <View className="bg-gradient-to-r from-primary/10 to-secondary/10 p-6 rounded-2xl mb-8">
          <View className="flex-row items-center mb-3">
            <Text className="text-4xl mr-3">🎯</Text>
            <View>
              <Text className="text-xl font-bold text-gray-900">
                Full Potential in 8 Weeks
              </Text>
              <Text className="text-sm text-gray-700">
                Research-backed progression system
              </Text>
            </View>
          </View>
        </View>

        {/* Week Plan */}
        {weeklyPlan && <WeekPlanList weeklyPlan={weeklyPlan} />}

        {/* Key Features */}
        <View className="bg-gray-50 rounded-2xl p-6 mb-8">
          <Text className="text-lg font-bold text-gray-900 mb-4">
            How It Works
          </Text>
          <View className="space-y-3">
            <View className="flex-row items-start">
              <Text className="text-lg mr-3">📈</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-gray-800">
                  Progressive Difficulty
                </Text>
                <Text className="text-sm text-gray-600 mt-1">
                  Tasks gradually increase in challenge each week
                </Text>
              </View>
            </View>

            <View className="flex-row items-start">
              <Text className="text-lg mr-3">🎮</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-gray-800">
                  XP & Levels
                </Text>
                <Text className="text-sm text-gray-600 mt-1">
                  Earn experience points and level up your avatar
                </Text>
              </View>
            </View>

            <View className="flex-row items-start">
              <Text className="text-lg mr-3">🏆</Text>
              <View className="flex-1">
                <Text className="text-base font-semibold text-gray-800">
                  Achievements
                </Text>
                <Text className="text-sm text-gray-600 mt-1">
                  Unlock badges and rewards for consistency
                </Text>
              </View>
            </View>
          </View>
        </View>

        <View className="h-24" />
      </ScrollView>

      <StepFooter
        onNext={() => router.push('/onboarding/permissions')}
        onPrev={() => router.back()}
        nextLabel="Continue"
      />
    </SafeAreaView>
  );
}