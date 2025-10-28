import { useState, useEffect } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { StepFooter } from '@/components/onboarding/StepFooter';
import { QuizCard } from '@/components/onboarding/QuizCard';
import { QUIZ_QUESTIONS } from '@/data/quiz';
import { useOnboardingStore } from '@/store/onboarding';
import { computeAvatarMatch } from '@/lib/gamification';
import { AVATARS } from '@/data/avatars';

export default function QuizScreen() {
  const router = useRouter();
  const { quizAnswers, setAnswer, selectedTraits, matchAvatar } = useOnboardingStore();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [localAnswers, setLocalAnswers] = useState<Record<string, number>>(quizAnswers);

  const currentQuestion = QUIZ_QUESTIONS[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === QUIZ_QUESTIONS.length - 1;
  const progress = ((currentQuestionIndex + 1) / QUIZ_QUESTIONS.length) * 100;

  const handleAnswer = (value: number) => {
    const newAnswers = {
      ...localAnswers,
      [currentQuestion.id]: value
    };
    setLocalAnswers(newAnswers);
    setAnswer(currentQuestion.id, value);

    if (!isLastQuestion) {
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }, 300);
    }
  };

  const handleComplete = () => {
    // Compute best matching avatar
    const avatarId = computeAvatarMatch(selectedTraits, localAnswers, AVATARS);
    matchAvatar(avatarId);
    router.push('/onboarding/avatar-result');
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    } else {
      router.back();
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView
        className="flex-1 px-6"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ flexGrow: 1 }}
      >
        {/* Quiz Progress */}
        <View className="mt-8 mb-6">
          <View className="flex-row justify-between items-center mb-2">
            <Text className="text-sm text-gray-600">
              Question {currentQuestionIndex + 1} of {QUIZ_QUESTIONS.length}
            </Text>
            <Text className="text-sm font-semibold text-primary">
              {Math.round(progress)}%
            </Text>
          </View>
          <View className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <View
              className="h-full bg-primary rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </View>
        </View>

        {/* Question Card */}
        <QuizCard
          question={currentQuestion}
          selectedValue={localAnswers[currentQuestion.id]}
          onSelect={handleAnswer}
        />

        {/* Navigation Hints */}
        <View className="mt-8 mb-4">
          <Text className="text-center text-sm text-gray-500">
            {isLastQuestion
              ? "Last question! Review your journey after this."
              : "Your answers help us find your perfect avatar archetype"}
          </Text>
        </View>

        <View className="flex-1" />
      </ScrollView>

      <StepFooter
        onNext={isLastQuestion ? handleComplete : undefined}
        onPrev={handlePrevious}
        nextLabel={isLastQuestion ? "See My Avatar" : undefined}
        showNext={isLastQuestion && !!localAnswers[currentQuestion.id]}
      />
    </SafeAreaView>
  );
}