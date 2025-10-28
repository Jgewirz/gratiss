import { View, Text, Pressable, ScrollView } from 'react-native';
import type { Trait, TraitKey } from '@/data/traits';

interface TraitPillsProps {
  traits: Trait[];
  selectedTraits: TraitKey[];
  onToggle: (trait: TraitKey) => void;
}

export function TraitPills({ traits, selectedTraits, onToggle }: TraitPillsProps) {
  return (
    <View className="flex-row flex-wrap">
      {traits.map((trait) => {
        const isSelected = selectedTraits.includes(trait.key);

        return (
          <Pressable
            key={trait.key}
            onPress={() => onToggle(trait.key)}
            className={`m-1.5 px-4 py-3 rounded-2xl border-2 active:scale-95 ${
              isSelected
                ? 'bg-primary border-primary'
                : 'bg-white border-gray-200'
            }`}
            style={{ transform: [{ scale: 1 }] }}
          >
            <View className="flex-row items-center">
              <Text className="text-2xl mr-2">{trait.emoji}</Text>
              <View>
                <Text
                  className={`font-semibold ${
                    isSelected ? 'text-white' : 'text-gray-900'
                  }`}
                >
                  {trait.label}
                </Text>
                <Text
                  className={`text-xs mt-0.5 ${
                    isSelected ? 'text-white/80' : 'text-gray-500'
                  }`}
                  numberOfLines={1}
                  style={{ maxWidth: 120 }}
                >
                  {trait.description}
                </Text>
              </View>
            </View>
          </Pressable>
        );
      })}
    </View>
  );
}