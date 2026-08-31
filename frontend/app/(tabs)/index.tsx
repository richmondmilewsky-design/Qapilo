import React, { useCallback, useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  RefreshControl,
  Animated,
  Modal,
  TextInput,
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
const PAGE_SIZE = 20; // levels (units) shown per page
const LOOKAHEAD = 10; // reveal the current level + this many upcoming levels

// Index of the unit holding the user's current position: the first unit that
// still has an unlocked, not-yet-completed lesson (falls back to the last).
function currentUnitIndex(units: Unit[]): number {
  if (!units.length) return 0;
  const idx = units.findIndex((u) => u.lessons.some((l) => l.unlocked && !l.completed));
  return idx >= 0 ? idx : units.length - 1;
}
function currentPageFor(units: Unit[]): number {
  return Math.floor(currentUnitIndex(units) / PAGE_SIZE);
}

export default function LearnScreen() {
  const { user, refresh, verifyEmail, resendVerification } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const [units, setUnits] = useState<Unit[]>([]);
  const [page, setPage] = useState(0);
  const scrollRef = useRef<ScrollView>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [nudgeDismissed, setNudgeDismissed] = useState(false);
  const [welcome, setWelcome] = useState<{ name: string; mode: string } | null>(null);
  const welcomeAnim = useRef(new Animated.Value(0)).current;
  const [justLoggedIn, setJustLoggedIn] = useState(false);
  const [cele, setCele] = useState<{ kind: "daily" | "milestone"; n: number } | null>(null);
  const celeAnim = useRef(new Animated.Value(0)).current;
  const [reminderOpen, setReminderOpen] = useState(false);
  const [verifyOpen, setVerifyOpen] = useState(false);
  const [verifyCode, setVerifyCode] = useState("");
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [verifyErr, setVerifyErr] = useState("");
  const [verifyMsg, setVerifyMsg] = useState("");
  const [verifyDone, setVerifyDone] = useState(false);

  const todayKey = new Date().toISOString().slice(0, 10);

  const load = useCallback(async () => {
    try {
      const data = await apiRequest<{ units: Unit[] }>("/curriculum");
      setUnits(data.units);
      // On (re)load, jump to the page holding the user's current level.
      setPage(currentPageFor(data.units));
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
          setJustLoggedIn(true);
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

  // Celebrate streak milestones (7/30/100) — highest new one, once each.
  useEffect(() => {
    if (!user) return;
    (async () => {
      for (const m of [100, 30, 7]) {
        if (user.streak >= m) {
          const k = `tq_streak_milestone_${m}`;
          const done = await storage.getItem(k, false);
          if (!done) {
            await storage.setItem(k, true);
            setCele({ kind: "milestone", n: m });
          }
          break;
        }
      }
    })();
  }, [user]);

  // Celebrate the streak once on the first login of the day (if no milestone took over).
  useEffect(() => {
    if (!justLoggedIn || !user) return;
    (async () => {
      const key = `tq_streak_celebrated_${todayKey}`;
      const done = await storage.getItem(key, false);
      if (!done && user.streak >= 1) {
        await storage.setItem(key, true);
        setCele((prev) => prev ?? { kind: "daily", n: user.streak });
      }
      setJustLoggedIn(false);
    })();
  }, [justLoggedIn, user, todayKey]);

  useEffect(() => {
    if (!cele) return;
    celeAnim.setValue(0);
    Animated.spring(celeAnim, { toValue: 1, friction: 6, useNativeDriver: true }).start();
    const timer = setTimeout(() => {
      Animated.timing(celeAnim, { toValue: 0, duration: 250, useNativeDriver: true }).start(
        ({ finished }) => { if (finished) setCele(null); }
      );
    }, cele.kind === "milestone" ? 3600 : 2600);
    return () => clearTimeout(timer);
  }, [cele, celeAnim]);

  // Gentle second reminder for unverified users after a few days.
  useEffect(() => {
    if (!user || user.email_verified) return;
    (async () => {
      const created = user.created_at ? new Date(user.created_at).getTime() : 0;
      const ageDays = created ? (Date.now() - created) / 86400000 : 0;
      if (ageDays < 3) return;
      const last = await storage.getItem<string>("tq_verify_reminded", "");
      const lastTime = last ? new Date(last).getTime() : 0;
      if (Date.now() - lastTime < 3 * 86400000) return;
      await storage.setItem("tq_verify_reminded", new Date().toISOString());
      setReminderOpen(true);
    })();
  }, [user]);

  const submitVerify = async () => {
    setVerifyErr(""); setVerifyMsg("");
    if (verifyCode.trim().length < 6) return;
    setVerifyLoading(true);
    try {
      await verifyEmail(verifyCode.trim(), locale);
      setVerifyDone(true);
      setTimeout(() => { setVerifyOpen(false); setVerifyDone(false); setVerifyCode(""); }, 1500);
    } catch (e: any) {
      setVerifyErr(e.message || t("common.somethingWrong"));
    } finally {
      setVerifyLoading(false);
    }
  };

  const resendVerify = async () => {
    setVerifyErr(""); setVerifyMsg("");
    try {
      await resendVerification(locale);
      setVerifyMsg(t("verify.resent"));
    } catch (e: any) {
      setVerifyErr(e.message || t("common.somethingWrong"));
    }
  };

  if (loading || !user) return <Loading testID="learn-loading" />;

  const dailyPct = Math.min(100, Math.round((user.daily_xp / user.daily_goal) * 100));
  const showNudge = user.in_trial && user.trial_days_left <= 2 && !nudgeDismissed;
  let currentAssigned = false;

  const revealedMax = currentUnitIndex(units) + LOOKAHEAD;
  const totalPages = Math.max(1, Math.ceil((revealedMax + 1) / PAGE_SIZE));
  const safePage = Math.min(page, totalPages - 1);
  const pageUnits = units.slice(safePage * PAGE_SIZE, safePage * PAGE_SIZE + PAGE_SIZE);
  const rangeStart = safePage * PAGE_SIZE + 1;
  const rangeEnd = Math.min(revealedMax + 1, safePage * PAGE_SIZE + PAGE_SIZE);
  const goToPage = (p: number) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setPage(Math.max(0, Math.min(totalPages - 1, p)));
    scrollRef.current?.scrollTo({ y: 0, animated: true });
  };

  return (
    <View style={styles.root}>
      {/* Sticky glass header */}
      <BlurView intensity={40} tint="dark" style={[styles.header, { paddingTop: insets.top + spacing.sm }]}>
        <View style={styles.headerRow}>
          <Pressable
            testID="header-stats-link"
            style={styles.headerStatsLink}
            onPress={() => {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              router.push("/(tabs)/profile");
            }}
          >
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
          </Pressable>
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
        ref={scrollRef}
        contentContainerStyle={{
          paddingTop: insets.top + 108,
          paddingBottom: spacing.xxxl,
        }}
        showsVerticalScrollIndicator={false}
        bounces={false}
        overScrollMode="never"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />
        }
      >
        {!user.email_verified && (
          <Pressable
            testID="verify-email-banner"
            onPress={() => { setVerifyErr(""); setVerifyMsg(""); setVerifyOpen(true); }}
            style={styles.verifyBanner}
          >
            <Ionicons name="mail-unread-outline" size={22} color={colors.amber} />
            <Text style={styles.verifyBannerText}>{t("verify.banner")}</Text>
            <Text style={styles.verifyBannerCta}>{t("verify.bannerCta")}</Text>
          </Pressable>
        )}

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

        {totalPages > 1 && (
          <View style={styles.pager} testID="level-pager-top">
            <Pressable
              testID="pager-prev"
              disabled={safePage === 0}
              onPress={() => goToPage(safePage - 1)}
              style={[styles.pagerBtn, safePage === 0 && styles.pagerBtnDisabled]}
              hitSlop={8}
            >
              <Ionicons name="chevron-back" size={22} color={safePage === 0 ? colors.muted : colors.onSurface} />
            </Pressable>
            <View style={styles.pagerLabel}>
              <Text style={styles.pagerTitle}>
                {t("learn.level")} {rangeStart}–{rangeEnd}
              </Text>
            </View>
            <Pressable
              testID="pager-next"
              disabled={safePage >= totalPages - 1}
              onPress={() => goToPage(safePage + 1)}
              style={[styles.pagerBtn, safePage >= totalPages - 1 && styles.pagerBtnDisabled]}
              hitSlop={8}
            >
              <Ionicons name="chevron-forward" size={22} color={safePage >= totalPages - 1 ? colors.muted : colors.onSurface} />
            </Pressable>
          </View>
        )}

        {pageUnits.map((unit, pi) => {
          const absIndex = safePage * PAGE_SIZE + pi;
          if (absIndex > revealedMax) return null;
          return (
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
          );
        })}

        {totalPages > 1 && (
          <View style={styles.pagerBottom} testID="level-pager-bottom">
            <Pressable
              disabled={safePage === 0}
              onPress={() => goToPage(safePage - 1)}
              style={[styles.pagerNavBtn, safePage === 0 && styles.pagerBtnDisabled]}
            >
              <Ionicons name="chevron-back" size={20} color={safePage === 0 ? colors.muted : colors.onSurface} />
              <Text style={[styles.pagerNavText, safePage === 0 && { color: colors.muted }]}>
                {t("learn.level")} {Math.max(1, rangeStart - PAGE_SIZE)}–{Math.max(PAGE_SIZE, rangeStart - 1)}
              </Text>
            </Pressable>
            <Pressable
              disabled={safePage >= totalPages - 1}
              onPress={() => goToPage(safePage + 1)}
              style={[styles.pagerNavBtn, safePage >= totalPages - 1 && styles.pagerBtnDisabled]}
            >
              {safePage < totalPages - 1 && (
                <Text style={styles.pagerNavText}>
                  {t("learn.level")} {Math.min(revealedMax + 1, rangeEnd + 1)}–{Math.min(revealedMax + 1, rangeEnd + PAGE_SIZE)}
                </Text>
              )}
              <Ionicons name="chevron-forward" size={20} color={safePage >= totalPages - 1 ? colors.muted : colors.onSurface} />
            </Pressable>
          </View>
        )}
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

      {cele && user && (
        <View style={styles.celeOverlay} testID={cele.kind === "milestone" ? "streak-milestone" : "streak-celebration"}>
          <Pressable style={styles.celeBackdrop} onPress={() => setCele(null)} />
          <Animated.View
            style={[
              styles.celeCard,
              cele.kind === "milestone" && styles.celeCardMilestone,
              {
                opacity: celeAnim,
                transform: [
                  { scale: celeAnim.interpolate({ inputRange: [0, 1], outputRange: [0.7, 1] }) },
                ],
              },
            ]}
          >
            <MaterialCommunityIcons
              name={cele.kind === "milestone" ? "trophy" : "fire"}
              size={64}
              color={colors.amber}
            />
            <Text style={styles.celeNum}>{cele.n}</Text>
            <Text style={styles.celeLabel}>{t("streak.label")}</Text>
            {cele.kind === "milestone" ? (
              <>
                <Text style={styles.celeMilestoneTitle}>{t("milestone.title")}</Text>
                <Text style={styles.celeSub}>{t("milestone.badge")}</Text>
              </>
            ) : (
              <Text style={styles.celeSub}>{t("streak.keepGoing")}</Text>
            )}
          </Animated.View>
        </View>
      )}

      <Modal visible={reminderOpen} transparent animationType="fade" onRequestClose={() => setReminderOpen(false)}>
        <View style={styles.verifyBackdrop}>
          <View style={styles.verifyCard} testID="verify-reminder-modal">
            <Ionicons name="mail-unread-outline" size={40} color={colors.amber} style={{ marginBottom: spacing.sm }} />
            <Text style={styles.verifyTitle}>{t("remind.title")}</Text>
            <Text style={styles.verifySubtitle}>{t("remind.body")}</Text>
            <Pressable
              testID="reminder-verify-now"
              onPress={() => { setReminderOpen(false); setVerifyErr(""); setVerifyMsg(""); setVerifyOpen(true); }}
              style={styles.verifyBtn}
            >
              <Text style={styles.verifyBtnText}>{t("remind.now")}</Text>
            </Pressable>
            <Pressable onPress={() => setReminderOpen(false)} style={{ alignSelf: "center", marginTop: spacing.md }}>
              <Text style={styles.verifyClose}>{t("remind.later")}</Text>
            </Pressable>
          </View>
        </View>
      </Modal>

      <Modal visible={verifyOpen} transparent animationType="fade" onRequestClose={() => setVerifyOpen(false)}>
        <View style={styles.verifyBackdrop}>
          <View style={styles.verifyCard} testID="verify-modal">
            <Text style={styles.verifyTitle}>{t("verify.title")}</Text>
            <Text style={styles.verifySubtitle}>{t("verify.subtitle")}</Text>
            {verifyDone ? (
              <View style={styles.verifyDoneRow}>
                <Ionicons name="checkmark-circle" size={22} color={colors.brand} />
                <Text style={styles.verifyDoneText} testID="verify-success">{t("verify.success")}</Text>
              </View>
            ) : (
              <>
                <TextInput
                  testID="verify-code-input"
                  value={verifyCode}
                  onChangeText={(v) => setVerifyCode(v.replace(/[^0-9]/g, ""))}
                  keyboardType="number-pad"
                  maxLength={6}
                  placeholder={t("verify.placeholder")}
                  placeholderTextColor={colors.muted}
                  style={styles.verifyInput}
                />
                {verifyErr ? <Text style={styles.verifyErr}>{verifyErr}</Text> : null}
                {verifyMsg ? <Text style={styles.verifyMsg}>{verifyMsg}</Text> : null}
                <Pressable testID="verify-submit" onPress={submitVerify} style={styles.verifyBtn}>
                  <Text style={styles.verifyBtnText}>{verifyLoading ? "…" : t("verify.submit")}</Text>
                </Pressable>
                <Pressable testID="verify-resend" onPress={resendVerify} style={{ alignSelf: "center", marginTop: spacing.md }}>
                  <Text style={styles.verifyResend}>{t("verify.resend")}</Text>
                </Pressable>
              </>
            )}
            <Pressable onPress={() => setVerifyOpen(false)} style={{ alignSelf: "center", marginTop: spacing.md }}>
              <Text style={styles.verifyClose}>{t("profile.close")}</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
    </View>
  );
}

function Node({
  lesson,
  color,
  offset,
  isCurrent,
  hideLabel,
  onPress,
}: {
  lesson: Lesson;
  color: string;
  offset: number;
  isCurrent: boolean;
  hideLabel?: boolean;
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
        {hideLabel ? "\u00A0" : lesson.title}
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
  verifyBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: "#1A1405",
    borderWidth: 1,
    borderColor: colors.amber,
    borderRadius: radius.lg,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
  },
  verifyBannerText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 13, color: colors.onSurface },
  verifyBannerCta: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.amber },
  celeOverlay: {
    position: "absolute",
    top: 0, left: 0, right: 0, bottom: 0,
    alignItems: "center",
    justifyContent: "center",
    zIndex: 30,
  },
  celeBackdrop: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.75)" },
  celeCard: {
    backgroundColor: colors.elevated,
    borderRadius: radius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.xxl,
    paddingHorizontal: spacing.xxl,
    alignItems: "center",
    minWidth: 220,
  },
  celeNum: { fontFamily: fonts.display, fontSize: 56, color: colors.onSurface, marginTop: spacing.sm },
  celeLabel: {
    fontFamily: fonts.bodySemi, fontSize: 13, color: colors.muted,
    letterSpacing: 1.5, textTransform: "uppercase", marginTop: -spacing.xs,
  },
  celeSub: { fontFamily: fonts.bodySemi, fontSize: 16, color: colors.brand, marginTop: spacing.md },
  celeCardMilestone: { borderColor: colors.amber, borderWidth: 2 },
  celeMilestoneTitle: {
    fontFamily: fonts.display, fontSize: 20, color: colors.amber,
    marginTop: spacing.md, textAlign: "center",
  },
  verifyBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.75)", justifyContent: "center", padding: spacing.lg },
  verifyCard: {
    backgroundColor: colors.elevated, borderRadius: radius.lg, borderWidth: 1,
    borderColor: colors.border, padding: spacing.lg,
  },
  verifyTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface, marginBottom: spacing.sm },
  verifySubtitle: { fontFamily: fonts.body, fontSize: 14, color: colors.onSurfaceSecondary, lineHeight: 21, marginBottom: spacing.lg },
  verifyInput: {
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, paddingHorizontal: spacing.md, height: 54,
    fontFamily: fonts.bodySemi, fontSize: 22, letterSpacing: 6, textAlign: "center", color: colors.onSurface,
  },
  verifyErr: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.error, marginTop: spacing.sm },
  verifyMsg: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.brand, marginTop: spacing.sm },
  verifyBtn: {
    backgroundColor: colors.brand, borderRadius: radius.md, paddingVertical: spacing.md,
    alignItems: "center", marginTop: spacing.md,
  },
  verifyBtnText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onBrand },
  verifyResend: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.brand },
  verifyClose: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.muted },
  verifyDoneRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.md },
  verifyDoneText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 15, color: colors.onSurface },
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
  headerStatsLink: { flex: 1, flexDirection: "row", alignItems: "center", gap: spacing.md },
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
  pager: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.lg,
    padding: spacing.sm,
  },
  pagerBtn: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceTertiary,
    alignItems: "center",
    justifyContent: "center",
  },
  pagerBtnDisabled: { opacity: 0.4 },
  pagerLabel: { flex: 1, alignItems: "center" },
  pagerTitle: { fontFamily: fonts.display, fontSize: 18, color: colors.onSurface },
  pagerSub: { fontFamily: fonts.bodyMed, fontSize: 12, color: colors.muted, marginTop: 2 },
  pagerBottom: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: spacing.md,
    marginHorizontal: spacing.lg,
    marginTop: spacing.sm,
  },
  pagerNavBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  pagerNavText: { fontFamily: fonts.bodyMed, fontSize: 12, color: colors.onSurface },
  lockedUnitRow: { flexDirection: "row", alignItems: "center", gap: spacing.xs, marginTop: 2 },
  lockedUnitTitle: { fontFamily: fonts.display, fontSize: 20, color: colors.muted },
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
