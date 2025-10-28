import { View, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import type { Avatar } from '@/data/avatars';

interface AvatarCardProps {
  avatar: Avatar;
}

export function AvatarCard({ avatar }: AvatarCardProps) {
  return (
    <View className="w-full">
      <LinearGradient
        colors={avatar.gradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        className="rounded-3xl p-8 items-center"
      >
        {/* Avatar Emoji */}
        <View className="w-32 h-32 bg-white/20 rounded-full items-center justify-center mb-6">
          <Text className="text-7xl">{avatar.emoji}</Text>
        </View>

        {/* Avatar Name Badge */}
        <View className="bg-white/20 px-6 py-2 rounded-full">
          <Text className="text-white font-bold text-lg">
            {avatar.name}
          </Text>
        </View>
      </LinearGradient>
    </View>
  );
}