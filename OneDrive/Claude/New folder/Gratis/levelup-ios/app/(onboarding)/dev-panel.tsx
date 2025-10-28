import { View, Text, ScrollView, Pressable } from 'react-native';
import { useOnboardingStore } from '@/store/onboarding';
import { generateWeeklyPlan, validatePlan } from '@/data/progression';
import { __selfTest } from '@/lib/gamification';
import { COPY } from '@/lib/copy';

export default function DevPanel() {
  // Only render in development mode
  if (process.env.EXPO_PUBLIC_DEV_PANEL !== '1') {
    return null;
  }

  const store = useOnboardingStore();

  const handleResetOnboarding = () => {
    store.reset();
    alert('Onboarding reset complete');
  };

  const handleRerunQuiz = () => {
    store.reset();
    store.setTraits(['mindfulness', 'discipline', 'focus']);
    alert('Quiz reset. Navigate to quiz screen to start');
  };

  const handleSimulateMiss = () => {
    // Set last completion to 2 days ago
    const twoDaysAgo = new Date();
    twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
    useOnboardingStore.setState({
      lastCompletionLocalISO: twoDaysAgo.toISOString(),
    });
    alert('Simulated missed day. Check gate should trigger');
  };

  const handleSimulatePay = () => {
    store.markDailyChargeUsed();
    alert('Simulated daily charge used');
  };

  const handleRunTests = () => {
    try {
      // Run self test
      const selfTestPass = __selfTest();

      // Generate and validate a sample plan
      const samplePlan = generateWeeklyPlan(['mindfulness', 'discipline'], 'scholar');
      let validationPass = false;

      try {
        validatePlan(samplePlan);
        validationPass = true;
      } catch (e) {
        console.error('Plan validation failed:', e);
      }

      if (selfTestPass && validationPass) {
        alert('✅ All tests passed!');
        return true;
      } else {
        alert(`❌ Tests failed: selfTest=${selfTestPass}, validation=${validationPass}`);
        return false;
      }
    } catch (e) {
      alert(`❌ Test error: ${e.message}`);
      return false;
    }
  };

  const testsPassed = handleRunTests();

  return (
    <ScrollView className="flex-1 bg-gray-900 p-4">
      <View className="mb-6">
        <Text className="text-2xl font-bold text-white mb-2">Dev Panel</Text>
        <Text className="text-gray-400">Debug tools for development</Text>
      </View>

      {testsPassed && (
        <View testID="selftest-ok" className="hidden" />
      )}

      <View className="space-y-4">
        <Pressable
          onPress={handleResetOnboarding}
          className="bg-blue-600 p-4 rounded-lg"
          accessibilityLabel="Reset onboarding"
          accessibilityRole="button"
        >
          <Text className="text-white font-semibold text-center">
            Reset Onboarding
          </Text>
        </Pressable>

        <Pressable
          onPress={handleRerunQuiz}
          className="bg-purple-600 p-4 rounded-lg"
          accessibilityLabel="Re-run quiz"
          accessibilityRole="button"
        >
          <Text className="text-white font-semibold text-center">
            Re-run Quiz
          </Text>
        </Pressable>

        <Pressable
          onPress={handleSimulateMiss}
          className="bg-yellow-600 p-4 rounded-lg"
          accessibilityLabel="Simulate missed day"
          accessibilityRole="button"
        >
          <Text className="text-white font-semibold text-center">
            Simulate Miss Day
          </Text>
        </Pressable>

        <Pressable
          onPress={handleSimulatePay}
          className="bg-red-600 p-4 rounded-lg"
          accessibilityLabel="Simulate pay to continue"
          accessibilityRole="button"
        >
          <Text className="text-white font-semibold text-center">
            Simulate Pay-to-Continue
          </Text>
        </Pressable>

        <Pressable
          onPress={handleRunTests}
          className="bg-green-600 p-4 rounded-lg"
          accessibilityLabel="Run validation tests"
          accessibilityRole="button"
        >
          <Text className="text-white font-semibold text-center">
            Run Tests
          </Text>
        </Pressable>
      </View>

      <View className="mt-8 p-4 bg-gray-800 rounded-lg">
        <Text className="text-white font-semibold mb-2">Store State</Text>
        <Text className="text-gray-300 text-xs">
          {JSON.stringify(
            {
              traits: store.selectedTraits,
              avatar: store.matchedAvatarId,
              xp: store.xp,
              level: store.level,
              streak: store.streakDays,
              graceUsed: store.weeklyGraceUsed,
              chargeUsed: store.dailyChargeUsed,
              onboardingDone: store.onboardingDone,
            },
            null,
            2
          )}
        </Text>
      </View>
    </ScrollView>
  );
}