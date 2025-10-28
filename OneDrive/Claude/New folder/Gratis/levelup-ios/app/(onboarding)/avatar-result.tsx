import { View, Text, ScrollView, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StepFooter } from '@/components/onboarding/StepFooter';
import { AvatarCard } from '@/components/onboarding/AvatarCard';
import { useOnboardingStore } from '@/store/onboarding';
import { AVATARS } from '@/data/avatars';

export default function AvatarResultScreen() {
  const router = useRouter();
  const { matchedAvatarId, selectedTraits } = useOnboardingStore();
  const avatar = AVATARS.find(a => a.id === matchedAvatarId);

  if (!avatar) {
    return null;
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 100 }}
      >
        {/* Reveal Animation Container */}
        <View className="items-center px-6">
          {/* Header */}
          <View className="mt-8 mb-6">
            <Text className="text-center text-lg text-gray-600 mb-2">
              Your Avatar Archetype
            </Text>
            <Text className="text-center text-4xl font-bold text-gray-900">
              {avatar.name}
            </Text>
          </View>

          {/* Avatar Card */}
          <AvatarCard avatar={avatar} />

          {/* Description */}
          <View className="mt-8 mb-6 px-4">
            <Text className="text-lg text-gray-700 leading-relaxed text-center">
              {avatar.description}
            </Text>
          </View>

          {/* Core Strengths */}
          <View className="w-full bg-gray-50 rounded-2xl p-6 mb-6">
            <Text className="text-lg font-bold text-gray-900 mb-4">
              Core Strengths
            </Text>
            <View className="space-y-3">
              {avatar.strengths.map((strength, index) => (
                <View key={index} className="flex-row items-center">
                  <View className="w-2 h-2 bg-primary rounded-full mr-3" />
                  <Text className="text-base text-gray-700">{strength}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Trait Alignment */}
          <View className="w-full bg-primary/10 rounded-2xl p-6 mb-6">
            <Text className="text-lg font-bold text-gray-900 mb-3">
              Perfect Match For Your Traits
            </Text>
            <Text className="text-base text-gray-700 leading-relaxed">
              Your selected traits align perfectly with {avatar.name}'s path to mastery.
              This archetype will guide you through personalized challenges designed for maximum growth.
            </Text>
          </View>

          {/* Stats Preview */}
          <View className="w-full flex-row justify-around bg-gray-50 rounded-2xl p-6">
            <View className="items-center">
              <Text className="text-3xl font-bold text-primary">
                {avatar.stats.discipline}
              </Text>
              <Text className="text-xs text-gray-600 mt-1">Discipline</Text>
            </View>
            <View className="items-center">
              <Text className="text-3xl font-bold text-secondary">
                {avatar.stats.focus}
              </Text>
              <Text className="text-xs text-gray-600 mt-1">Focus</Text>
            </View>
            <View className="items-center">
              <Text className="text-3xl font-bold text-accent">
                {avatar.stats.growth}
              </Text>
              <Text className="text-xs text-gray-600 mt-1">Growth</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      <StepFooter
        onNext={() => router.push('/onboarding/plan-preview')}
        onPrev={() => router.back()}
        nextLabel="View Your Plan"
      />
    </SafeAreaView>
  );
}