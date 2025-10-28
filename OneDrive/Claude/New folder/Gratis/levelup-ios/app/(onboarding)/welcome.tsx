import { View, Text, Image, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StepFooter } from '@/components/onboarding/StepFooter';
import { COPY } from '@/lib/copy';

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1"
        contentContainerStyle={{ flexGrow: 1 }}
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-1 px-6 pb-8">
          {/* Hero Section */}
          <View className="items-center mt-12 mb-8">
            <View className="w-32 h-32 bg-primary/10 rounded-full items-center justify-center mb-6">
              <Text className="text-6xl">🚀</Text>
            </View>

            <Text className="text-3xl font-bold text-gray-900 text-center mb-3">
              {COPY.welcome.title}
            </Text>

            <Text className="text-lg text-gray-600 text-center leading-relaxed">
              {COPY.welcome.subtitle}
            </Text>
          </View>

          {/* Features */}
          <View className="space-y-4 mb-8">
            {COPY.welcome.features.map((feature, index) => (
              <View key={index} className="flex-row items-start bg-gray-50 p-4 rounded-xl">
                <Text className="text-2xl mr-4">{feature.emoji}</Text>
                <View className="flex-1">
                  <Text className="text-base font-semibold text-gray-900 mb-1">
                    {feature.title}
                  </Text>
                  <Text className="text-sm text-gray-600 leading-relaxed">
                    {feature.description}
                  </Text>
                </View>
              </View>
            ))}
          </View>

          {/* CTA Section */}
          <View className="bg-gradient-to-r from-primary/10 to-secondary/10 p-6 rounded-2xl mb-8">
            <Text className="text-xl font-bold text-gray-900 text-center mb-2">
              Ready to unlock your Full Potential?
            </Text>
            <Text className="text-base text-gray-700 text-center">
              Join thousands achieving extraordinary results
            </Text>
          </View>

          {/* Stats */}
          <View className="flex-row justify-around mb-12">
            <View className="items-center">
              <Text className="text-2xl font-bold text-primary">94%</Text>
              <Text className="text-xs text-gray-600">Success Rate</Text>
            </View>
            <View className="items-center">
              <Text className="text-2xl font-bold text-secondary">8 Weeks</Text>
              <Text className="text-xs text-gray-600">To Transform</Text>
            </View>
            <View className="items-center">
              <Text className="text-2xl font-bold text-accent">10+</Text>
              <Text className="text-xs text-gray-600">Archetypes</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      <StepFooter
        onNext={() => router.push('/onboarding/select-traits')}
        nextLabel="Begin Journey"
      />
    </SafeAreaView>
  );
}