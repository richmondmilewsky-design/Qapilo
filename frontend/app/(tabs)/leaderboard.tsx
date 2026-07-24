import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, FlatList, RefreshControl } from "react-native";
import { useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { Image } from "expo-image";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";
import { Loading } from "@/src/components/ui";

type Row = {
  rank: number;
  user_id: string;
  name: string;
  picture: string | null;
  xp: number;
  level: number;
  streak: number;
  is_me: boolean;
};

const MEDALS = ["#F59E0B", "#A1A1AA", "#B45309"];

export default function LeaderboardScreen() {
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await apiRequest<{ leaderboard: Row[] }>("/leaderboard");
      setRows(data.leaderboard);
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      (async () => {
        await load();
        setLoading(false);
      })();
    }, [load])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  if (loading) return <Loading testID="leaderboard-loading" />;

  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.md }]}>
      <View style={styles.header}>
        <Text style={styles.title}>{t("leaderboard.title")}</Text>
        <Text style={styles.subtitle}>{t("leaderboard.subtitle")}</Text>
      </View>
      <FlatList
        data={rows}
        keyExtractor={(r) => r.user_id}
        contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.xxxl }}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />
        }
        ListEmptyComponent={
          <Text style={styles.empty}>{t("leaderboard.empty")}</Text>
        }
        renderItem={({ item }) => (
          <View
            testID={`leaderboard-row-${item.rank}`}
            style={[styles.row, item.is_me && styles.rowMe]}
          >
            <View style={styles.rankWrap}>
              {item.rank <= 3 ? (
                <MaterialCommunityIcons name="medal" size={26} color={MEDALS[item.rank - 1]} />
              ) : (
                <Text style={styles.rankNum}>{item.rank}</Text>
              )}
            </View>
            {item.picture ? (
              <Image source={{ uri: item.picture }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarFallback}>
                <Text style={styles.avatarInitial}>{item.name.charAt(0).toUpperCase()}</Text>
              </View>
            )}
            <View style={{ flex: 1 }}>
              <Text style={styles.name} numberOfLines={1}>
                {item.name} {item.is_me ? `(${t("leaderboard.you")})` : ""}
              </Text>
              <Text style={styles.meta}>
                Level {item.level} · {item.streak}🔥
              </Text>
            </View>
            <View style={styles.xpWrap}>
              <Text style={styles.xp}>{item.xp}</Text>
              <Text style={styles.xpLabel}>XP</Text>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: { paddingHorizontal: spacing.lg, marginBottom: spacing.sm },
  title: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface },
  subtitle: { fontFamily: fonts.body, fontSize: 14, color: colors.muted, marginTop: 2 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  rowMe: { borderColor: colors.brand, backgroundColor: "#0C2018" },
  rankWrap: { width: 32, alignItems: "center" },
  rankNum: { fontFamily: fonts.display, fontSize: 18, color: colors.muted },
  avatar: { width: 42, height: 42, borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary },
  avatarFallback: {
    width: 42,
    height: 42,
    borderRadius: radius.pill,
    backgroundColor: colors.brandDark,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarInitial: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  name: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface },
  meta: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: 1 },
  xpWrap: { alignItems: "flex-end" },
  xp: { fontFamily: fonts.display, fontSize: 20, color: colors.brand },
  xpLabel: { fontFamily: fonts.displayMed, fontSize: 10, color: colors.muted, letterSpacing: 1 },
  empty: { fontFamily: fonts.body, fontSize: 14, color: colors.muted, textAlign: "center", marginTop: spacing.xxxl },
});
