import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { StepFooter } from '@/components/onboarding/StepFooter';
import { PermissionToggles } from '@/components/onboarding/PermissionToggles';
import { useOnboardingStore } from '@/store/onboarding';

export default function PermissionsScreen() {
  const router = useRouter();
  const { permissions, setPermissions } = useOnboardingStore();

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1 px-6"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="mt-8 mb-6">
          <Text className="text-3xl font-bold text-gray-900 mb-3">
            Enhance Your Experience
          </Text>
          <Text className="text-lg text-gray-600 leading-relaxed">
            Enable features to maximize your growth potential
          </Text>
        </View>

        {/* Benefits Card */}
        <View className="bg-primary/10 rounded-2xl p-6 mb-8">
          <Text className="text-lg font-bold text-gray-900 mb-3">
            Why Enable Permissions?
          </Text>
          <View className="space-y-2">
            <View className="flex-row items-center">
              <Text className="text-base mr-2">✓</Text>
              <Text className="text-sm text-gray-700">
                Never miss a task with smart reminders
              </Text>
            </View>
            <View className="flex-row items-center">
              <Text className="text-base mr-2">✓</Text>
              <Text className="text-sm text-gray-700">
                Track progress automatically
              </Text>
            </View>
            <View className="flex-row items-center">
              <Text className="text-base mr-2">✓</Text>
              <Text className="text-sm text-gray-700">
                Sync with health apps for holistic growth
              </Text>
            </View>
          </View>
        </View>

        {/* Permission Toggles */}
        <PermissionToggles
          permissions={permissions}
          onChange={setPermissions}
        />

        {/* Privacy Note */}
        <View className="bg-gray-50 rounded-xl p-4 mt-8 mb-6">
          <View className="flex-row items-start">
            <Text className="text-lg mr-3">🔒</Text>
            <View className="flex-1">
              <Text className="text-sm font-semibold text-gray-800 mb-1">
                Your Privacy Matters
              </Text>
              <Text className="text-xs text-gray-600 leading-relaxed">
                We never share your data. All information is encrypted and used solely
                to enhance your personal growth journey. You can change these settings
                anytime.
              </Text>
            </View>
          </View>
        </View>

        <View className="h-24" />
      </ScrollView>

      <StepFooter
        onNext={() => router.push('/onboarding/start')}
        onPrev={() => router.back()}
        nextLabel="Almost Done"
      />
    </SafeAreaView>
  );
}