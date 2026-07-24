import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, RefreshControl } from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { Image } from "expo-image";
import { LinearGradient } from "expo-linear-gradient";
import { useAuth } from "@/src/context/AuthContext";
import { apiRequest } from "@/src/api/client";
import { colors, fonts, radius, spacing, BADGE_ICONS } from "@/src/theme/theme";
import { Loading } from "@/src/components/ui";

const COVER =
  "https://images.unsplash.com/photo-1638184984605-af1f05249a56?crop=entropy&cs=srgb&fm=jpg&q=85&w=1000";

type Badge = { id: string; name: string; desc: string; icon: string; earned: boolean };

export default function ProfileScreen() {
  const { user, logout, refresh } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [badges, setBadges] = useState<Badge[]>([]);
  const [total, setTotal] = useState(15);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await apiRequest<{ badges: Badge[]; total_lessons: number }>("/progress");
      setBadges(data.badges);
      setTotal(data.total_lessons);
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

  const doLogout = async () => {
    await logout();
    router.replace("/auth");
  };

  if (loading || !user) return <Loading testID="profile-loading" />;

  const earnedCount = badges.filter((b) => b.earned).length;
  const stats = [
    { icon: "flash", label: "TOTAL XP", value: user.xp, color: colors.brand },
    { icon: "fire", label: "STREAK", value: user.streak, color: colors.amber },
    { icon: "trending-up", label: "LEVEL", value: user.level, color: colors.brand },
    { icon: "check-circle", label: "LESSONS", value: `${user.completed_lessons.length}/${total}`, color: colors.brand },
  ];

  return (
    <View style={styles.root}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: spacing.xxxl }}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />
        }
      >
        {/* Hero banner */}
        <View style={styles.banner}>
          <Image source={{ uri: COVER }} style={StyleSheet.absoluteFill} contentFit="cover" />
          <LinearGradient
            colors={["rgba(9,9,11,0.2)", colors.surface]}
            style={StyleSheet.absoluteFill}
          />
          <View style={[styles.bannerContent, { paddingTop: insets.top + spacing.xl }]}>
            {user.picture ? (
              <Image source={{ uri: user.picture }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarFallback}>
                <Text style={styles.avatarInitial}>{user.name.charAt(0).toUpperCase()}</Text>
              </View>
            )}
            <Text style={styles.name} testID="profile-name">{user.name}</Text>
            <Text style={styles.email}>{user.email}</Text>
          </View>
        </View>

        {/* Level progress */}
        <View style={styles.section}>
          <Pressable
            testID="pro-banner"
            onPress={() => router.push("/paywall")}
            style={styles.proBanner}
          >
            <View style={styles.proBannerLeft}>
              <View style={styles.proCrown}>
                <MaterialCommunityIcons name="crown" size={22} color={colors.onAmber} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.proBannerTitle}>
                  {user.is_pro
                    ? user.pro_source === "subscription"
                      ? "TradeQuest Pro"
                      : "Pro Trial Active"
                    : "Unlock TradeQuest Pro"}
                </Text>
                <Text style={styles.proBannerSub}>
                  {user.is_pro
                    ? user.pro_source === "subscription"
                      ? "Unlimited access · thank you!"
                      : `${user.trial_days_left} day${user.trial_days_left === 1 ? "" : "s"} of free Pro left`
                    : "Unlimited AI Tutor + advanced lessons"}
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.muted} />
          </Pressable>

          <View style={styles.levelCard}>
            <View style={styles.levelHeaderRow}>
              <Text style={styles.levelText}>Level {user.level}</Text>
              <Text style={styles.levelSub}>
                {user.level_current}/{user.level_needed} XP to level {user.level + 1}
              </Text>
            </View>
            <View style={styles.xpBarBg}>
              <View style={[styles.xpBarFill, { width: `${(user.level_current / user.level_needed) * 100}%` }]} />
            </View>
          </View>

          {/* Stats grid */}
          <View style={styles.statsGrid}>
            {stats.map((s) => (
              <View key={s.label} style={styles.statCard} testID={`stat-${s.label}`}>
                <MaterialCommunityIcons name={s.icon as any} size={24} color={s.color} />
                <Text style={styles.statValue}>{s.value}</Text>
                <Text style={styles.statLabel}>{s.label}</Text>
              </View>
            ))}
          </View>

          {/* Badges */}
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>Badges</Text>
            <Text style={styles.sectionCount}>{earnedCount}/{badges.length}</Text>
          </View>
          <View style={styles.badgeGrid}>
            {badges.map((b) => (
              <View key={b.id} style={styles.badgeItem} testID={`badge-${b.id}`}>
                <View style={[styles.badgeCircle, { opacity: b.earned ? 1 : 0.35 }]}>
                  <MaterialCommunityIcons
                    name={(BADGE_ICONS[b.icon] || "medal") as any}
                    size={28}
                    color={b.earned ? colors.amber : colors.muted}
                  />
                </View>
                <Text style={[styles.badgeLabel, { opacity: b.earned ? 1 : 0.5 }]} numberOfLines={2}>
                  {b.name}
                </Text>
              </View>
            ))}
          </View>

          <Pressable testID="disclaimer-link" onPress={() => router.push("/disclaimer")} style={styles.linkRow}>
            <Ionicons name="document-text-outline" size={20} color={colors.onSurfaceSecondary} />
            <Text style={styles.linkText}>Disclaimer &amp; Terms</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.muted} />
          </Pressable>

          <Pressable testID="logout-button" onPress={doLogout} style={styles.logout}>
            <Ionicons name="log-out-outline" size={20} color={colors.error} />
            <Text style={styles.logoutText}>Log Out</Text>
          </Pressable>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  banner: { height: 260, justifyContent: "flex-end" },
  bannerContent: { alignItems: "center", paddingBottom: spacing.lg },
  avatar: { width: 88, height: 88, borderRadius: radius.pill, borderWidth: 3, borderColor: colors.brand },
  avatarFallback: {
    width: 88,
    height: 88,
    borderRadius: radius.pill,
    backgroundColor: colors.brandDark,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 3,
    borderColor: colors.brand,
  },
  avatarInitial: { fontFamily: fonts.display, fontSize: 40, color: colors.onSurface },
  name: { fontFamily: fonts.display, fontSize: 28, color: colors.onSurface, marginTop: spacing.md },
  email: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginTop: 2 },
  section: { paddingHorizontal: spacing.lg },
  proBanner: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "#1A1405",
    borderWidth: 1,
    borderColor: colors.amber,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  proBannerLeft: { flexDirection: "row", alignItems: "center", gap: spacing.md, flex: 1 },
  proCrown: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: colors.amber,
    alignItems: "center",
    justifyContent: "center",
  },
  proBannerTitle: { fontFamily: fonts.display, fontSize: 18, color: colors.onSurface },
  proBannerSub: { fontFamily: fonts.body, fontSize: 12, color: colors.onSurfaceSecondary, marginTop: 1 },
  levelCard: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  levelHeaderRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end", marginBottom: spacing.md },
  levelText: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface },
  levelSub: { fontFamily: fonts.body, fontSize: 12, color: colors.muted },
  xpBarBg: { height: 10, borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary, overflow: "hidden" },
  xpBarFill: { height: "100%", backgroundColor: colors.brand, borderRadius: radius.pill },
  statsGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md, marginBottom: spacing.xl },
  statCard: {
    width: "47%",
    flexGrow: 1,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: 6,
  },
  statValue: { fontFamily: fonts.display, fontSize: 26, color: colors.onSurface },
  statLabel: { fontFamily: fonts.displayMed, fontSize: 11, color: colors.muted, letterSpacing: 1 },
  sectionHeaderRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.md },
  sectionTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface },
  sectionCount: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.amber },
  badgeGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  badgeItem: { width: "22%", alignItems: "center", gap: spacing.xs },
  badgeCircle: {
    width: 60,
    height: 60,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    alignItems: "center",
    justifyContent: "center",
  },
  badgeLabel: { fontFamily: fonts.body, fontSize: 10, color: colors.onSurfaceSecondary, textAlign: "center" },
  logout: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    marginTop: spacing.md,
    height: 52,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.error,
  },
  linkRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginTop: spacing.xxl,
    height: 52,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
  },
  linkText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 15, color: colors.onSurface },
  logoutText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.error },
});
