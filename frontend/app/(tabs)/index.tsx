import React, { useCallback, useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  RefreshControl,
  Animated,
} from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { BlurView } from "expo-blur";
import * as Haptics from "expo-haptics";
import { useAuth } from "@/src/context/AuthContext";
import { apiRequest } from "@/src/api/client";
import { storage } from "@/src/utils/storage";
import { useI18n } from "@/src/i18n/I18nContext";
import { LanguageButton } from "@/src/components/LanguageButton";
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
type Unit = { id: string; title: string; subtitle: string; color: string; tier: number; lessons: Lesson[] };

const OFFSETS = [0, 52, 74, 52, 0, -52, -74, -52];

export default function LearnScreen() {
  const { user, refresh } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [nudgeDismissed, setNudgeDismissed] = useState(false);
  const [welcome, setWelcome] = useState<{ name: string; mode: string } | null>(null);
  const welcomeAnim = useRef(new Animated.Value(0)).current;

  const todayKey = new Date().toISOString().slice(0, 10);

  const load = useCallback(async () => {
    try {
      const data = await apiRequest<{ units: Unit[] }>("/curriculum");
      setUnits(data.units);
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      (async () => {
        const dismissed = await storage.getItem(`tq_trial_nudge_${todayKey}`, false);
        setNudgeDismissed(!!dismissed);
        const w = await storage.getItem<string>("qapilo_welcome", "");
        if (w) {
          await storage.removeItem("qapilo_welcome");
          const [mode, ...rest] = w.split("::");
          setWelcome({ mode, name: rest.join("::") });
        }
        await Promise.all([load(), refresh()]);
        setLoading(false);
      })();
    }, [load, refresh, todayKey])
  );

  const dismissNudge = async () => {
    setNudgeDismissed(true);
    await storage.setItem(`tq_trial_nudge_${todayKey}`, true);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([load(), refresh()]);
    setRefreshing(false);
  };

  useEffect(() => {
    load();
  }, [locale, load]);

  useEffect(() => {
    if (!welcome) return;
    welcomeAnim.setValue(0);
    Animated.sequence([
      Animated.timing(welcomeAnim, { toValue: 1, duration: 300, useNativeDriver: true }),
      Animated.delay(2400),
      Animated.timing(welcomeAnim, { toValue: 0, duration: 300, useNativeDriver: true }),
    ]).start(({ finished }) => {
      if (finished) setWelcome(null);
    });
  }, [welcome, welcomeAnim]);

  if (loading || !user) return <Loading testID="learn-loading" />;

  const dailyPct = Math.min(100, Math.round((user.daily_xp / user.daily_goal) * 100));
  const showNudge = user.in_trial && user.trial_days_left <= 2 && !nudgeDismissed;
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
            <Text style={styles.levelLabel}>{t("learn.level")} {user.level}</Text>
            <View style={styles.xpBarBg}>
              <View style={[styles.xpBarFill, { width: `${(user.level_current / user.level_needed) * 100}%` }]} />
            </View>
          </View>
          <View style={styles.statChip} testID="header-xp">
            <MaterialCommunityIcons name="flash" size={18} color={colors.brand} />
            <Text style={styles.statChipText}>{user.xp}</Text>
          </View>
          <LanguageButton />
        </View>
        <View style={styles.dailyRow}>
          <Text style={styles.dailyText}>
            {t("learn.dailyGoal")} · {user.daily_xp}/{user.daily_goal} XP
          </Text>
          <Text style={[styles.dailyText, { color: dailyPct >= 100 ? colors.brand : colors.muted }]}>
            {dailyPct >= 100 ? t("learn.complete") : `${dailyPct}%`}
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
        {showNudge && (
          <Pressable
            testID="trial-nudge-banner"
            onPress={() => router.push("/paywall")}
            style={styles.nudge}
          >
            <View style={styles.nudgeIcon}>
              <MaterialCommunityIcons name="clock-alert-outline" size={22} color={colors.onAmber} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.nudgeTitle}>
                {t("learn.trialEnds")} {user.trial_days_left}{" "}
                {user.trial_days_left === 1 ? t("learn.day") : t("learn.days")}
              </Text>
              <Text style={styles.nudgeSub}>{t("learn.keepPro")}</Text>
            </View>
            <Pressable
              testID="trial-nudge-dismiss"
              onPress={dismissNudge}
              hitSlop={10}
              style={styles.nudgeClose}
            >
              <Ionicons name="close" size={18} color={colors.onSurfaceSecondary} />
            </Pressable>
          </Pressable>
        )}

        <Pressable
          testID="practice-cta"
          onPress={() => {
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
            router.push("/practice");
          }}
          style={styles.practiceCta}
        >
          <View style={styles.practiceIcon}>
            <MaterialCommunityIcons name="dumbbell" size={24} color={colors.onBrand} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.practiceTitle}>{t("learn.practiceTitle")}</Text>
            <Text style={styles.practiceSub}>{t("learn.practiceSub")}</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color={colors.muted} />
        </Pressable>

        {units.map((unit) => (
          <View key={unit.id} style={styles.unit}>
            <View style={[styles.unitHeader, { borderLeftColor: unit.color }]}>
              <Text style={[styles.tierLabel, { color: unit.color }]}>
                {t("learn.level")} {unit.id.replace("u", "")} · {t(`tier.${unit.tier}` as any)}
              </Text>
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

      {welcome && (
        <Animated.View
          pointerEvents="none"
          testID="welcome-toast"
          style={[
            styles.welcomeWrap,
            {
              top: insets.top + 112,
              opacity: welcomeAnim,
              transform: [
                {
                  translateY: welcomeAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [-12, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.welcomeToast}>
            <MaterialCommunityIcons name="hand-wave" size={18} color={colors.onBrand} />
            <Text style={styles.welcomeText} numberOfLines={1}>
              {(welcome.mode === "signup" ? t("welcome.new") : t("welcome.back"))}, {welcome.name}!
            </Text>
          </View>
        </Animated.View>
      )}
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
  const { t } = useI18n();
  const bg = lesson.completed ? color : lesson.unlocked ? colors.surfaceTertiary : colors.surfaceSecondary;
  const iconColor = lesson.completed ? colors.onBrand : lesson.unlocked ? colors.onSurface : colors.muted;

  return (
    <View style={[styles.nodeWrap, { transform: [{ translateX: offset }] }]}>
      {isCurrent && (
        <Pressable onPress={onPress} style={styles.startPill} testID="current-lesson-pill">
          <Text style={styles.startPillText}>{t("learn.start")}</Text>
        </Pressable>
      )}
      {proLocked && (
        <Pressable onPress={onPress} style={styles.proNodePill} testID={`pro-pill-${lesson.id}`}>
          <MaterialCommunityIcons name="crown" size={11} color={colors.onAmber} />
          <Text style={styles.startPillText}>{t("learn.pro")}</Text>
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
  welcomeWrap: {
    position: "absolute",
    left: 0,
    right: 0,
    alignItems: "center",
    zIndex: 20,
  },
  welcomeToast: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    maxWidth: "90%",
    backgroundColor: colors.brand,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 6,
  },
  welcomeText: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.onBrand },
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
  tierLabel: { fontFamily: fonts.displayMed, fontSize: 11, letterSpacing: 1.5, marginBottom: 2 },
  practiceCta: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.xl,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.brandDark,
    borderRadius: radius.lg,
    padding: spacing.md,
  },
  practiceIcon: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  practiceTitle: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  practiceSub: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: 1 },
  nudge: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: "#1A1405",
    borderWidth: 1,
    borderColor: colors.amber,
    borderRadius: radius.lg,
    padding: spacing.md,
  },
  nudgeIcon: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    backgroundColor: colors.amber,
    alignItems: "center",
    justifyContent: "center",
  },
  nudgeTitle: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.onSurface },
  nudgeSub: { fontFamily: fonts.body, fontSize: 12, color: colors.onSurfaceSecondary, marginTop: 1 },
  nudgeClose: { padding: 4 },  unitHeader: {
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
