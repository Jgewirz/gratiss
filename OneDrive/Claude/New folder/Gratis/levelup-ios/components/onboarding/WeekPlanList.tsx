import { View, Text, ScrollView } from 'react-native';
import type { WeeklyPlan, WeekPlan } from '@/data/progression';

interface WeekPlanListProps {
  weeklyPlan: WeeklyPlan;
}

export function WeekPlanList({ weeklyPlan }: WeekPlanListProps) {
  return (
    <View className="space-y-4">
      {weeklyPlan.weeks.slice(0, 4).map((week, index) => (
        <WeekCard key={week.week} week={week} isFirst={index === 0} />
      ))}

      {/* Teaser for remaining weeks */}
      <View className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl p-6">
        <View className="flex-row items-center">
          <Text className="text-3xl mr-3">🔒</Text>
          <View className="flex-1">
            <Text className="text-base font-bold text-gray-900">
              Weeks 5-8: Advanced Mastery
            </Text>
            <Text className="text-sm text-gray-700 mt-1">
              Unlock harder challenges as you progress
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
}

function WeekCard({ week, isFirst }: { week: WeekPlan; isFirst: boolean }) {
  const difficultyColors = {
    easy: 'bg-green-100 text-green-700',
    medium: 'bg-amber-100 text-amber-700',
    hard: 'bg-red-100 text-red-700',
  };

  return (
    <View
      className={`bg-white rounded-2xl p-5 border ${
        isFirst ? 'border-primary border-2' : 'border-gray-100'
      }`}
    >
      {/* Week Header */}
      <View className="flex-row justify-between items-start mb-3">
        <View>
          <Text className="text-lg font-bold text-gray-900">
            {week.theme}
          </Text>
          <Text className="text-sm text-gray-600 mt-0.5">
            {week.tasks.length} tasks
          </Text>
        </View>
        {isFirst && (
          <View className="bg-primary/10 px-3 py-1 rounded-full">
            <Text className="text-xs font-semibold text-primary">
              START HERE
            </Text>
          </View>
        )}
      </View>

      {/* Sample Tasks */}
      <View className="space-y-2">
        {week.tasks.slice(0, 2).map((task) => (
          <View key={task.id} className="flex-row items-center">
            <Text className="text-lg mr-2">{task.icon}</Text>
            <View className="flex-1">
              <Text className="text-sm text-gray-700" numberOfLines={1}>
                {task.title}
              </Text>
            </View>
            <View
              className={`px-2 py-0.5 rounded-full ${
                difficultyColors[task.difficulty]
              }`}
            >
              <Text className="text-xs font-medium">
                {task.xpReward} XP
              </Text>
            </View>
          </View>
        ))}
        {week.tasks.length > 2 && (
          <Text className="text-xs text-gray-500 text-center mt-2">
            +{week.tasks.length - 2} more tasks
          </Text>
        )}
      </View>
    </View>
  );
}