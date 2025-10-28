import { View, Text, Pressable } from 'react-native';
import type { QuizQuestion } from '@/data/quiz';
import { LIKERT_SCALE } from '@/data/quiz';

interface QuizCardProps {
  question: QuizQuestion;
  selectedValue?: number;
  onSelect: (value: number) => void;
}

export function QuizCard({ question, selectedValue, onSelect }: QuizCardProps) {
  return (
    <View className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      {/* Question Text */}
      <Text className="text-xl font-semibold text-gray-900 mb-8 text-center leading-relaxed">
        {question.text}
      </Text>

      {/* Likert Scale Options */}
      <View className="space-y-3">
        {LIKERT_SCALE.map((option) => {
          const isSelected = selectedValue === option.value;

          return (
            <Pressable
              key={option.value}
              onPress={() => onSelect(option.value)}
              className={`flex-row items-center px-4 py-4 rounded-xl border-2 active:scale-98 ${
                isSelected
                  ? 'bg-primary/10 border-primary'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <Text className="text-3xl mr-4">{option.emoji}</Text>
              <View className="flex-1">
                <Text
                  className={`font-semibold ${
                    isSelected ? 'text-primary' : 'text-gray-700'
                  }`}
                >
                  {option.label}
                </Text>
              </View>
              {isSelected && (
                <View className="w-6 h-6 rounded-full bg-primary items-center justify-center">
                  <Text className="text-white text-xs font-bold">✓</Text>
                </View>
              )}
            </Pressable>
          );
        })}
      </View>

      {/* Question Type Indicator */}
      <View className="mt-6 items-center">
        <Text className="text-xs text-gray-500 uppercase tracking-wide">
          {question.type === 'agreement' && 'Rate Your Agreement'}
          {question.type === 'preference' && 'Your Preference'}
          {question.type === 'frequency' && 'How Often'}
        </Text>
      </View>
    </View>
  );
}