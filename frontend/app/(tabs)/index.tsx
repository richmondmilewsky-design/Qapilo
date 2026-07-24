import React, { useCallback, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  RefreshControl,
} from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { BlurView } from "expo-blur";
import * as Haptics from "expo-haptics";
import { useAuth } from "@/src/context/AuthContext";
import { apiRequest } from "@/src/api/client";
import { colors, fonts, radius, spacing, LESSON_ICONS } from "@/src/theme/theme";
import { Loading } from "@/src/components/ui";

type Lesson = {
  id: string;
  title: string;
  icon: string;
  xp: number;
  completed: boolean;
  unlocked: boolean;
  perfect: boolean;
  pro_locked: boolean;
};
type Unit = { id: string; title: string; subtitle: string; color: string; lessons: Lesson[] };

const OFFSETS = [0, 52, 74, 52, 0, -52, -74, -52];

export default function LearnScreen() {
  const { user, refresh } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await apiRequest<{ units: Unit[] }>("/curriculum");
      setUnits(data.units);
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      (async () => {
        await Promise.all([load(), refresh()]);
        setLoading(false);
      })();
    }, [load, refresh])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([load(), refresh()]);
    setRefreshing(false);
  };

  if (loading || !user) return <Loading testID="learn-loading" />;

  const dailyPct = Math.min(100, Math.round((user.daily_xp / user.daily_goal) * 100));
  let currentAssigned = false;

  return (
    <View style={styles.root}>
      {/* Sticky glass header */}
      <BlurView intensity={40} tint="dark" style={[styles.header, { paddingTop: insets.top + spacing.sm }]}>
        <View style={styles.headerRow}>
          <View style={styles.statChip} testID="header-streak">
            <MaterialCommunityIcons name="fire" size={20} color={colors.amber} />
            <Text style={styles.statChipText}>{user.streak}</Text>
          </View>
          <View style={styles.levelWrap}>
            <Text style={styles.levelLabel}>LEVEL {user.level}</Text>
            <View style={styles.xpBarBg}>
              <View style={[styles.xpBarFill, { width: `${(user.level_current / user.level_needed) * 100}%` }]} />
            </View>
          </View>
          <View style={styles.statChip} testID="header-xp">
            <MaterialCommunityIcons name="flash" size={18} color={colors.brand} />
            <Text style={styles.statChipText}>{user.xp}</Text>
          </View>
        </View>
        <View style={styles.dailyRow}>
          <Text style={styles.dailyText}>
            Daily goal · {user.daily_xp}/{user.daily_goal} XP
          </Text>
          <Text style={[styles.dailyText, { color: dailyPct >= 100 ? colors.brand : colors.muted }]}>
            {dailyPct >= 100 ? "Complete!" : `${dailyPct}%`}
          </Text>
        </View>
      </BlurView>

      <ScrollView
        contentContainerStyle={{
          paddingTop: insets.top + 108,
          paddingBottom: spacing.xxxl,
        }}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />
        }
      >
        {units.map((unit) => (
          <View key={unit.id} style={styles.unit}>
            <View style={[styles.unitHeader, { borderLeftColor: unit.color }]}>
              <Text style={styles.unitTitle}>{unit.title}</Text>
              <Text style={styles.unitSubtitle}>{unit.subtitle}</Text>
            </View>

            {unit.lessons.map((lesson, i) => {
              const isCurrent = !currentAssigned && lesson.unlocked && !lesson.completed;
              if (isCurrent) currentAssigned = true;
              const offset = OFFSETS[i % OFFSETS.length];
              return (
                <Node
                  key={lesson.id}
                  lesson={lesson}
                  color={unit.color}
                  offset={offset}
                  isCurrent={isCurrent}
                  onPress={() => {
                    if (!lesson.unlocked) {
                      if (lesson.pro_locked) {
                        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                        router.push("/paywall");
                        return;
                      }
                      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
                      return;
                    }
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                    router.push(`/lesson/${lesson.id}`);
                  }}
                />
              );
            })}
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

function Node({
  lesson,
  color,
  offset,
  isCurrent,
  onPress,
}: {
  lesson: Lesson;
  color: string;
  offset: number;
  isCurrent: boolean;
  onPress: () => void;
}) {
  const iconName = (LESSON_ICONS[lesson.icon] || "book-open-variant") as any;
  const size = isCurrent ? 92 : 74;
  const proLocked = !lesson.unlocked && lesson.pro_locked;
  const bg = lesson.completed ? color : lesson.unlocked ? colors.surfaceTertiary : colors.surfaceSecondary;
  const iconColor = lesson.completed ? colors.onBrand : lesson.unlocked ? colors.onSurface : colors.muted;

  return (
    <View style={[styles.nodeWrap, { transform: [{ translateX: offset }] }]}>
      {isCurrent && (
        <Pressable onPress={onPress} style={styles.startPill} testID="current-lesson-pill">
          <Text style={styles.startPillText}>START</Text>
        </Pressable>
      )}
      {proLocked && (
        <Pressable onPress={onPress} style={styles.proNodePill} testID={`pro-pill-${lesson.id}`}>
          <MaterialCommunityIcons name="crown" size={11} color={colors.onAmber} />
          <Text style={styles.startPillText}>PRO</Text>
        </Pressable>
      )}
      <Pressable
        testID={`lesson-node-${lesson.id}`}
        onPress={onPress}
        style={({ pressed }) => [
          styles.node,
          {
            width: size,
            height: size,
            borderRadius: size / 2,
            backgroundColor: bg,
            borderWidth: isCurrent ? 3 : lesson.completed ? 0 : 2,
            borderColor: isCurrent ? colors.amber : proLocked ? colors.amber : colors.border,
            transform: [{ scale: pressed && lesson.unlocked ? 0.94 : 1 }],
            opacity: lesson.unlocked ? 1 : 0.65,
          },
        ]}
      >
        {proLocked ? (
          <MaterialCommunityIcons name="crown" size={size * 0.34} color={colors.amber} />
        ) : !lesson.unlocked ? (
          <Ionicons name="lock-closed" size={size * 0.32} color={colors.muted} />
        ) : (
          <MaterialCommunityIcons name={iconName} size={size * 0.4} color={iconColor} />
        )}
        {lesson.completed && (
          <View style={styles.checkBadge}>
            <Ionicons name="checkmark" size={13} color={colors.onBrand} />
          </View>
        )}
        {lesson.perfect && (
          <View style={styles.perfectBadge}>
            <MaterialCommunityIcons name="star" size={12} color={colors.onAmber} />
          </View>
        )}
      </Pressable>
      <Text style={styles.nodeLabel} numberOfLines={2}>
        {lesson.title}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    overflow: "hidden",
  },
  headerRow: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  statChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: colors.surfaceSecondary,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statChipText: { fontFamily: fonts.display, fontSize: 18, color: colors.onSurface },
  levelWrap: { flex: 1 },
  levelLabel: { fontFamily: fonts.displayMed, fontSize: 12, color: colors.muted, letterSpacing: 1, marginBottom: 4 },
  xpBarBg: { height: 8, borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary, overflow: "hidden" },
  xpBarFill: { height: "100%", backgroundColor: colors.brand, borderRadius: radius.pill },
  dailyRow: { flexDirection: "row", justifyContent: "space-between", marginTop: spacing.sm },
  dailyText: { fontFamily: fonts.bodyMed, fontSize: 12, color: colors.muted },
  unit: { marginBottom: spacing.xl },
  unitHeader: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    paddingLeft: spacing.md,
    borderLeftWidth: 4,
  },
  unitTitle: { fontFamily: fonts.display, fontSize: 24, color: colors.onSurface },
  unitSubtitle: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginTop: 2 },
  nodeWrap: { alignItems: "center", marginBottom: spacing.xl, alignSelf: "center" },
  node: { alignItems: "center", justifyContent: "center" },
  nodeLabel: {
    fontFamily: fonts.bodyMed,
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    marginTop: spacing.sm,
    textAlign: "center",
    maxWidth: 110,
  },
  checkBadge: {
    position: "absolute",
    bottom: 2,
    right: 2,
    backgroundColor: colors.brandDark,
    borderRadius: radius.pill,
    width: 22,
    height: 22,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: colors.surface,
  },
  perfectBadge: {
    position: "absolute",
    top: 0,
    right: 0,
    backgroundColor: colors.amber,
    borderRadius: radius.pill,
    width: 20,
    height: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  startPill: {
    backgroundColor: colors.amber,
    paddingHorizontal: spacing.md,
    paddingVertical: 4,
    borderRadius: radius.pill,
    marginBottom: spacing.xs,
  },
  proNodePill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
    backgroundColor: colors.amber,
    paddingHorizontal: spacing.md,
    paddingVertical: 4,
    borderRadius: radius.pill,
    marginBottom: spacing.xs,
  },
  startPillText: { fontFamily: fonts.bodySemi, fontSize: 11, color: colors.onAmber, letterSpacing: 1 },
});
