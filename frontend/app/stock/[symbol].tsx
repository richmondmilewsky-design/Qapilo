import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, Dimensions, RefreshControl } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { LineChart } from "react-native-gifted-charts";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";
import { Loading } from "@/src/components/ui";
import StockLogo from "@/src/components/StockLogo";

type Detail = {
  symbol: string;
  name: string;
  category: string;
  logo: string;
  explain: string;
  price: number;
  change: number;
  change_pct: number;
  source: string;
  history: number[];
  in_watchlist: boolean;
};

export default function StockDetail() {
  const { symbol } = useLocalSearchParams<{ symbol: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const [data, setData] = useState<Detail | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    const d = await apiRequest<Detail>(`/stocks/${symbol}`);
    setData(d);
    return d;
  };

  useEffect(() => {
    (async () => {
      try {
        await fetchData();
      } catch {
        router.back();
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol, locale]);

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchData();
    } catch {}
    setRefreshing(false);
  };

  const toggleWatch = async () => {
    if (!data) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {});
    setData({ ...data, in_watchlist: !data.in_watchlist });
    try {
      await apiRequest(`/watchlist/${data.symbol}/toggle`, { method: "POST" });
    } catch {
      setData((prev) => (prev ? { ...prev, in_watchlist: !prev.in_watchlist } : prev));
    }
  };

  if (!data) return <Loading testID="stock-detail-loading" />;

  const up = data.change_pct >= 0;
  const accent = up ? colors.brand : colors.error;
  const chartData = data.history.map((v) => ({ value: v }));
  const width = Dimensions.get("window").width;

  return (
    <View style={styles.root}>
      <View style={[styles.topBar, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="stock-back-button" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.topTitle}>{data.symbol}</Text>
        <Pressable testID={`watch-toggle-detail-${data.symbol}`} onPress={toggleWatch} hitSlop={12}>
          <Ionicons
            name={data.in_watchlist ? "star" : "star-outline"}
            size={24}
            color={data.in_watchlist ? colors.amber : colors.muted}
          />
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={{ paddingBottom: insets.bottom + spacing.xxl }}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />}
      >
        <View style={styles.head}>
          <StockLogo uri={data.logo} symbol={data.symbol} size={56} borderRadius={radius.md} />
          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{data.name}</Text>
            <View style={styles.catTag}>
              <Text style={styles.catText}>{data.category}</Text>
            </View>
          </View>
        </View>

        <View style={styles.priceBlock}>
          <Text style={styles.price} testID="stock-price">${data.price.toLocaleString()}</Text>
          <View style={[styles.changeTag, { backgroundColor: up ? "#0C2E22" : "#2E0C0C" }]}>
            <Ionicons name={up ? "caret-up" : "caret-down"} size={14} color={accent} />
            <Text style={[styles.changeText, { color: accent }]}>
              {up ? "+" : ""}{data.change.toFixed(2)} ({Math.abs(data.change_pct).toFixed(2)}%)
            </Text>
          </View>
        </View>

        <View style={styles.chartWrap}>
          <LineChart
            data={chartData}
            areaChart
            curved
            hideDataPoints
            thickness={2.5}
            color={accent}
            startFillColor={accent}
            endFillColor={colors.surface}
            startOpacity={0.35}
            endOpacity={0.02}
            hideRules
            hideYAxisText
            yAxisThickness={0}
            xAxisThickness={0}
            initialSpacing={0}
            endSpacing={0}
            adjustToWidth
            width={width - spacing.lg * 2 - 8}
            height={160}
            disableScroll
          />
          <Text style={styles.chartLabel}>{t("stock.chartLabel")}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t("stock.whatIs").replace("{symbol}", data.symbol)}</Text>
          <Text style={styles.explain}>{data.explain}</Text>
        </View>

        <View style={styles.disclaimer}>
          <Ionicons name="information-circle-outline" size={16} color={colors.muted} />
          <Text style={styles.disclaimerText}>
            {data.source === "alphavantage"
              ? t("stock.disclaimerLive")
              : t("stock.disclaimerSample")}
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
  },
  topTitle: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  head: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, marginTop: spacing.sm },
  logo: { width: 56, height: 56, borderRadius: radius.md, backgroundColor: "#FFFFFF" },
  name: { fontFamily: fonts.display, fontSize: 24, color: colors.onSurface },
  catTag: {
    alignSelf: "flex-start",
    backgroundColor: colors.surfaceTertiary,
    paddingHorizontal: spacing.md,
    paddingVertical: 3,
    borderRadius: radius.pill,
    marginTop: 4,
  },
  catText: { fontFamily: fonts.bodyMed, fontSize: 12, color: colors.onSurfaceSecondary },
  priceBlock: { paddingHorizontal: spacing.lg, marginTop: spacing.xl },
  price: { fontFamily: fonts.display, fontSize: 44, color: colors.onSurface },
  changeTag: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    alignSelf: "flex-start",
    paddingHorizontal: spacing.md,
    paddingVertical: 4,
    borderRadius: radius.sm,
    marginTop: spacing.sm,
  },
  changeText: { fontFamily: fonts.bodySemi, fontSize: 14 },
  chartWrap: { marginTop: spacing.xl, paddingHorizontal: spacing.lg, alignItems: "center" },
  chartLabel: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: spacing.sm },
  section: { paddingHorizontal: spacing.lg, marginTop: spacing.xl },
  sectionTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface, marginBottom: spacing.sm },
  explain: { fontFamily: fonts.body, fontSize: 16, color: colors.onSurfaceSecondary, lineHeight: 25 },
  disclaimer: {
    flexDirection: "row",
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    marginTop: spacing.xl,
    alignItems: "flex-start",
  },
  disclaimerText: { flex: 1, fontFamily: fonts.body, fontSize: 12, color: colors.muted, lineHeight: 18 },
});
