import { View, Text, Switch, Pressable } from 'react-native';
import { useState } from 'react';

interface Permissions {
  notifications: boolean;
  health: boolean;
}

interface PermissionTogglesProps {
  permissions: Permissions;
  onChange: (permissions: Permissions) => void;
}

export function PermissionToggles({
  permissions,
  onChange,
}: PermissionTogglesProps) {
  const handleToggle = (key: keyof Permissions) => {
    onChange({
      ...permissions,
      [key]: !permissions[key],
    });
  };

  return (
    <View className="space-y-4">
      {/* Notifications */}
      <View className="bg-white rounded-2xl p-4 border border-gray-100">
        <View className="flex-row items-start">
          <Text className="text-3xl mr-4">🔔</Text>
          <View className="flex-1">
            <View className="flex-row justify-between items-center">
              <View className="flex-1 mr-4">
                <Text className="text-base font-semibold text-gray-900 mb-1">
                  Daily Reminders
                </Text>
                <Text className="text-sm text-gray-600 leading-relaxed">
                  Get gentle nudges to complete your daily tasks and maintain streaks
                </Text>
              </View>
              <Switch
                value={permissions.notifications}
                onValueChange={() => handleToggle('notifications')}
                trackColor={{ false: '#d1d5db', true: '#4F46E5' }}
                thumbColor="white"
              />
            </View>

            {permissions.notifications && (
              <View className="mt-3 bg-blue-50 p-3 rounded-lg">
                <Text className="text-xs text-blue-700">
                  We'll send reminders at optimal times based on your habits
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>

      {/* Health Data */}
      <View className="bg-white rounded-2xl p-4 border border-gray-100">
        <View className="flex-row items-start">
          <Text className="text-3xl mr-4">❤️</Text>
          <View className="flex-1">
            <View className="flex-row justify-between items-center">
              <View className="flex-1 mr-4">
                <Text className="text-base font-semibold text-gray-900 mb-1">
                  Health Integration
                </Text>
                <Text className="text-sm text-gray-600 leading-relaxed">
                  Sync with Apple Health to track wellness goals automatically
                </Text>
              </View>
              <Switch
                value={permissions.health}
                onValueChange={() => handleToggle('health')}
                trackColor={{ false: '#d1d5db', true: '#4F46E5' }}
                thumbColor="white"
              />
            </View>

            {permissions.health && (
              <View className="mt-3 bg-green-50 p-3 rounded-lg">
                <Text className="text-xs text-green-700">
                  Auto-complete fitness tasks when workouts are detected
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>

      {/* Analytics (Always On) */}
      <View className="bg-gray-50 rounded-2xl p-4">
        <View className="flex-row items-start">
          <Text className="text-3xl mr-4 opacity-50">📊</Text>
          <View className="flex-1">
            <Text className="text-base font-semibold text-gray-500 mb-1">
              Progress Tracking
            </Text>
            <Text className="text-sm text-gray-500 leading-relaxed">
              Always enabled to track your journey and provide insights
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
}