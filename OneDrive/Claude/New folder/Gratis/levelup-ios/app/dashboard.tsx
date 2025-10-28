import { View, Text, ScrollView, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useUserStore } from '@/store/user';
import { levelFromXP } from '@/lib/gamification';
import { LinearGradient } from 'expo-linear-gradient';

export default function DashboardScreen() {
  const { profile, gameProgress } = useUserStore();
  const levelInfo = levelFromXP(gameProgress.totalXP);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Header */}
        <LinearGradient
          colors={['#4F46E5', '#6366F1']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          className="px-6 py-8"
        >
          <View className="items-center">
            <Text className="text-white text-3xl font-bold mb-2">
              Level {levelInfo.level}
            </Text>
            <View className="w-full bg-white/20 h-3 rounded-full overflow-hidden mb-2">
              <View
                className="h-full bg-white rounded-full"
                style={{ width: `${levelInfo.progress}%` }}
              />
            </View>
            <Text className="text-white/80 text-sm">
              {levelInfo.currentLevelXP} / {levelInfo.nextLevelXP} XP
            </Text>
          </View>

          {/* Stats Row */}
          <View className="flex-row justify-around mt-6">
            <View className="items-center">
              <Text className="text-white text-2xl font-bold">
                {gameProgress.streakDays}
              </Text>
              <Text className="text-white/70 text-xs">Day Streak</Text>
            </View>
            <View className="items-center">
              <Text className="text-white text-2xl font-bold">
                {gameProgress.completedTasks.length}
              </Text>
              <Text className="text-white/70 text-xs">Tasks Done</Text>
            </View>
            <View className="items-center">
              <Text className="text-white text-2xl font-bold">
                {gameProgress.achievements.length}
              </Text>
              <Text className="text-white/70 text-xs">Achievements</Text>
            </View>
          </View>
        </LinearGradient>

        {/* Today's Tasks */}
        <View className="px-6 py-6">
          <Text className="text-2xl font-bold text-gray-900 mb-4">
            Today's Challenges
          </Text>

          <View className="bg-white rounded-2xl p-6 shadow-sm">
            <Text className="text-center text-gray-500">
              Dashboard coming soon! Your tasks will appear here.
            </Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View className="px-6 pb-8">
          <View className="flex-row space-x-4">
            <Pressable className="flex-1 bg-primary/10 rounded-xl p-4">
              <Text className="text-primary font-semibold text-center">
                View Progress
              </Text>
            </Pressable>
            <Pressable className="flex-1 bg-secondary/10 rounded-xl p-4">
              <Text className="text-secondary font-semibold text-center">
                Achievements
              </Text>
            </Pressable>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}