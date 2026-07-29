import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, RefreshControl } from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { Image } from "expo-image";
import { LinearGradient } from "expo-linear-gradient";
import { useAuth } from "@/src/context/AuthContext";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { colors, fonts, radius, spacing, BADGE_ICONS } from "@/src/theme/theme";
import { Loading } from "@/src/components/ui";
import StockLogo from "@/src/components/StockLogo";

const COVER =
  "https://images.unsplash.com/photo-1638184984605-af1f05249a56?crop=entropy&cs=srgb&fm=jpg&q=85&w=1000";

type Badge = { id: string; name: string; desc: string; icon: string; earned: boolean };
type WatchStock = { symbol: string; name: string; logo: string; price: number; change_pct: number; in_watchlist: boolean };

export default function ProfileScreen() {
  const { user, refresh } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const [badges, setBadges] = useState<Badge[]>([]);
  const [total, setTotal] = useState(15);
  const [watchlist, setWatchlist] = useState<WatchStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const [prog, stocks] = await Promise.all([
        apiRequest<{ badges: Badge[]; total_lessons: number }>("/progress"),
        apiRequest<{ stocks: WatchStock[] }>("/stocks"),
      ]);
      setBadges(prog.badges);
      setTotal(prog.total_lessons);
      setWatchlist(stocks.stocks.filter((s) => s.in_watchlist));
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

  if (loading || !user) return <Loading testID="profile-loading" />;

  const earnedCount = badges.filter((b) => b.earned).length;
  const stats = [
    { icon: "flash", label: t("profile.totalXp"), value: user.xp, color: colors.brand },
    { icon: "fire", label: t("profile.streak"), value: user.streak, color: colors.amber },
    { icon: "trending-up", label: t("profile.levelStat"), value: user.level, color: colors.brand },
    { icon: "check-circle", label: t("profile.lessons"), value: `${user.completed_lessons.length}/${total}`, color: colors.brand },
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
                      ? t("profile.pro")
                      : t("profile.proTrial")
                    : t("profile.unlock")}
                </Text>
                <Text style={styles.proBannerSub}>
                  {user.is_pro
                    ? user.pro_source === "subscription"
                      ? t("profile.unlimited")
                      : `${user.trial_days_left} ${user.trial_days_left === 1 ? t("learn.day") : t("learn.days")} ${t("profile.trialLeftSuffix")}`
                    : t("profile.proSub")}
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.muted} />
          </Pressable>

          <View style={styles.levelCard}>
            <View style={styles.levelHeaderRow}>
              <Text style={styles.levelText}>{t("profile.level")} {user.level}</Text>
              <Text style={styles.levelSub}>
                {user.level_current}/{user.level_needed} {t("profile.toLevel")} {user.level + 1}
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

          {/* Watchlist widget */}
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>{t("profile.watchlist")}</Text>
            {watchlist.length > 0 && (
              <Pressable testID="watchlist-see-all" onPress={() => router.push("/(tabs)/explore")}>
                <Text style={styles.seeAll}>{t("profile.seeAll")}</Text>
              </Pressable>
            )}
          </View>
          {watchlist.length === 0 ? (
            <Pressable testID="watchlist-empty" onPress={() => router.push("/(tabs)/explore")} style={styles.watchEmpty}>
              <Ionicons name="star-outline" size={22} color={colors.muted} />
              <Text style={styles.watchEmptyText}>{t("profile.watchEmpty")}</Text>
            </Pressable>
          ) : (
            <View style={styles.watchCard}>
              {watchlist.slice(0, 5).map((s, idx) => {
                const up = s.change_pct >= 0;
                return (
                  <Pressable
                    key={s.symbol}
                    testID={`profile-watch-${s.symbol}`}
                    onPress={() => router.push(`/stock/${s.symbol}`)}
                    style={[styles.watchRow, idx > 0 && styles.watchRowBorder]}
                  >
                    <StockLogo uri={s.logo} symbol={s.symbol} size={34} borderRadius={radius.sm} />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.watchSymbol}>{s.symbol}</Text>
                      <Text style={styles.watchName} numberOfLines={1}>{s.name}</Text>
                    </View>
                    <View style={{ alignItems: "flex-end" }}>
                      <Text style={styles.watchPrice}>${s.price.toLocaleString()}</Text>
                      <Text style={[styles.watchChange, { color: up ? colors.brand : colors.error }]}>
                        {up ? "+" : ""}{s.change_pct.toFixed(2)}%
                      </Text>
                    </View>
                  </Pressable>
                );
              })}
            </View>
          )}

          {/* Badges */}
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>{t("profile.badges")}</Text>
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

          <Pressable testID="settings-row" onPress={() => router.push("/settings")} style={[styles.linkRow, { marginTop: spacing.xxl }]}>
            <Ionicons name="settings-outline" size={20} color={colors.onSurfaceSecondary} />
            <Text style={styles.linkText}>{t("profile.settings")}</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.muted} />
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
  modalBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.6)", justifyContent: "flex-end" },
  modalCard: { backgroundColor: colors.surfaceSecondary, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "80%" },
  modalTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface, marginBottom: spacing.xs },
  modalMsg: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginBottom: spacing.md },
  exportBox: { backgroundColor: colors.surface, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md, marginBottom: spacing.md },
  exportText: { fontFamily: "monospace", fontSize: 11, color: colors.onSurfaceSecondary },
  modalPrimary: { backgroundColor: colors.brand, borderRadius: radius.md, paddingVertical: spacing.md, alignItems: "center" },
  modalPrimaryText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onBrand },
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
  seeAll: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.brand },
  watchCard: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.xl,
  },
  watchRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.md },
  watchRowBorder: { borderTopWidth: 1, borderTopColor: colors.border },
  watchSymbol: { fontFamily: fonts.display, fontSize: 17, color: colors.onSurface },
  watchName: { fontFamily: fonts.body, fontSize: 12, color: colors.muted },
  watchPrice: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface },
  watchChange: { fontFamily: fonts.bodySemi, fontSize: 12, marginTop: 1 },
  watchEmpty: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    borderStyle: "dashed",
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  watchEmptyText: { flex: 1, fontFamily: fonts.body, fontSize: 13, color: colors.muted },
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
  langValue: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.brand, marginRight: spacing.xs },
  logoutText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.error },
});
