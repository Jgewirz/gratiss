import { View, Text, ScrollView, Pressable, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import { StepFooter } from '@/components/onboarding/StepFooter';
import { TraitPills } from '@/components/onboarding/TraitPills';
import { TRAITS } from '@/data/traits';
import { useOnboardingStore } from '@/store/onboarding';
import type { TraitKey } from '@/data/traits';

export default function SelectTraitsScreen() {
  const router = useRouter();
  const { selectedTraits, setTraits } = useOnboardingStore();
  const [localTraits, setLocalTraits] = useState<TraitKey[]>(selectedTraits);

  const handleTraitToggle = (traitKey: TraitKey) => {
    if (localTraits.includes(traitKey)) {
      setLocalTraits(localTraits.filter(t => t !== traitKey));
    } else {
      if (localTraits.length >= 3) {
        Alert.alert(
          'Maximum Reached',
          'You can select up to 3 traits. Deselect one to choose another.',
          [{ text: 'OK' }]
        );
        return;
      }
      setLocalTraits([...localTraits, traitKey]);
    }
  };

  const handleNext = () => {
    if (localTraits.length === 0) {
      Alert.alert('Select Traits', 'Please select at least one trait to continue.');
      return;
    }
    setTraits(localTraits);
    router.push('/onboarding/quiz');
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1 px-6"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="mt-8 mb-6">
          <Text className="text-3xl font-bold text-gray-900 mb-3">
            Choose Your Path
          </Text>
          <Text className="text-lg text-gray-600 leading-relaxed">
            Select up to 3 traits that resonate with your growth journey
          </Text>
        </View>

        {/* Selection Counter */}
        <View className="bg-primary/10 px-4 py-3 rounded-lg mb-6">
          <Text className="text-primary font-semibold text-center">
            {localTraits.length}/3 traits selected
          </Text>
        </View>

        {/* Traits Grid */}
        <TraitPills
          traits={TRAITS}
          selectedTraits={localTraits}
          onToggle={handleTraitToggle}
        />

        {/* Selected Traits Summary */}
        {localTraits.length > 0 && (
          <View className="mt-8 mb-6 p-4 bg-gray-50 rounded-xl">
            <Text className="text-sm font-semibold text-gray-700 mb-2">
              Your Focus Areas:
            </Text>
            <View className="flex-row flex-wrap">
              {localTraits.map(key => {
                const trait = TRAITS.find(t => t.key === key);
                return (
                  <View key={key} className="flex-row items-center bg-white px-3 py-2 rounded-full mr-2 mb-2">
                    <Text className="text-lg mr-1">{trait?.emoji}</Text>
                    <Text className="text-sm font-medium text-gray-700">
                      {trait?.label}
                    </Text>
                  </View>
                );
              })}
            </View>
          </View>
        )}

        <View className="h-24" />
      </ScrollView>

      <StepFooter
        onNext={handleNext}
        onPrev={() => router.back()}
        nextLabel="Start Quiz"
        nextDisabled={localTraits.length === 0}
      />
    </SafeAreaView>
  );
}