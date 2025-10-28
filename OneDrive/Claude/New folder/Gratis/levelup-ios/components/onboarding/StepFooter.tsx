import { View, Text, Pressable } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

interface StepFooterProps {
  onNext?: () => void;
  onPrev?: () => void;
  nextLabel?: string;
  prevLabel?: string;
  nextDisabled?: boolean;
  showNext?: boolean;
}

export function StepFooter({
  onNext,
  onPrev,
  nextLabel = 'Continue',
  prevLabel = 'Back',
  nextDisabled = false,
  showNext = true,
}: StepFooterProps) {
  const insets = useSafeAreaInsets();

  return (
    <View
      className="bg-white border-t border-gray-100 px-6 pt-4 flex-row justify-between"
      style={{ paddingBottom: insets.bottom + 20 }}
    >
      {onPrev ? (
        <Pressable
          onPress={onPrev}
          className="px-6 py-3 rounded-xl active:opacity-70"
        >
          <Text className="text-gray-700 font-semibold">{prevLabel}</Text>
        </Pressable>
      ) : (
        <View />
      )}

      {onNext && showNext && (
        <Pressable
          onPress={onNext}
          disabled={nextDisabled}
          className={`px-8 py-3 rounded-xl active:opacity-70 ${
            nextDisabled
              ? 'bg-gray-200'
              : 'bg-primary'
          }`}
        >
          <Text
            className={`font-bold ${
              nextDisabled ? 'text-gray-400' : 'text-white'
            }`}
          >
            {nextLabel}
          </Text>
        </Pressable>
      )}
    </View>
  );
}