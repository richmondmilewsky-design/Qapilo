import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Platform } from "react-native";
import { colors, fonts } from "@/src/theme/theme";
import { useI18n } from "@/src/i18n/I18nContext";

export default function TabsLayout() {
  const { t } = useI18n();
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brand,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: {
          backgroundColor: colors.surfaceSecondary,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          height: Platform.OS === "ios" ? 88 : 68,
          paddingTop: 8,
          paddingBottom: Platform.OS === "ios" ? 28 : 10,
        },
        tabBarLabelStyle: { fontFamily: fonts.bodyMed, fontSize: 11 },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t("tab.learn"),
          tabBarIcon: ({ color, size }) => <Ionicons name="school" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: t("tab.explore"),
          tabBarIcon: ({ color, size }) => <Ionicons name="stats-chart" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="tutor"
        options={{
          title: t("tab.tutor"),
          tabBarIcon: ({ color, size }) => <Ionicons name="chatbubbles" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="leaderboard"
        options={{
          title: t("tab.leaderboard"),
          tabBarIcon: ({ color, size }) => <Ionicons name="trophy" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: t("tab.profile"),
          tabBarIcon: ({ color, size }) => <Ionicons name="person" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
