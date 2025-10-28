import { View, Text } from 'react-native';
import type { Task } from '@/data/progression';

interface FirstTaskCardProps {
  task: Task;
}

export function FirstTaskCard({ task }: FirstTaskCardProps) {
  const difficultyColors = {
    easy: 'bg-green-100 border-green-200',
    medium: 'bg-amber-100 border-amber-200',
    hard: 'bg-red-100 border-red-200',
  };

  const difficultyTextColors = {
    easy: 'text-green-700',
    medium: 'text-amber-700',
    hard: 'text-red-700',
  };

  return (
    <View
      className={`rounded-2xl p-5 border-2 ${difficultyColors[task.difficulty]}`}
    >
      {/* Task Header */}
      <View className="flex-row items-start justify-between mb-3">
        <View className="flex-row items-center flex-1">
          <Text className="text-4xl mr-3">{task.icon}</Text>
          <View className="flex-1">
            <Text className="text-lg font-bold text-gray-900">
              {task.title}
            </Text>
            <View className="flex-row items-center mt-1">
              <Text className={`text-xs font-medium ${difficultyTextColors[task.difficulty]}`}>
                {task.difficulty.toUpperCase()}
              </Text>
              <Text className="text-xs text-gray-500 mx-2">•</Text>
              <Text className="text-xs text-gray-500">
                {task.duration} min
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* Task Description */}
      <Text className="text-sm text-gray-700 leading-relaxed mb-4">
        {task.description}
      </Text>

      {/* Reward Preview */}
      <View className="bg-white/70 rounded-xl p-3 flex-row justify-between items-center">
        <Text className="text-sm font-semibold text-gray-700">
          Complete to earn:
        </Text>
        <View className="flex-row items-center">
          <Text className="text-2xl mr-1">⚡</Text>
          <Text className="text-base font-bold text-primary">
            +{task.xpReward} XP
          </Text>
        </View>
      </View>
    </View>
  );
}