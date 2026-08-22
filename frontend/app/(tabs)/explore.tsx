import React, { useCallback, useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  FlatList,
  Pressable,
  TextInput,
  RefreshControl,
} from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { LanguageButton } from "@/src/components/LanguageButton";
import HomeLogo from "@/src/components/HomeLogo";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";
import { Loading } from "@/src/components/ui";
import StockLogo from "@/src/components/StockLogo";

type Stock = {
  symbol: string;
  name: string;
  category: string;
  logo: string;
  explain: string;
  price: number;
  change: number;
  change_pct: number;
  source: string;
  in_watchlist: boolean;
};

const CATEGORIES = ["All", "Tech", "Auto", "Finance", "Retail", "Media", "ETF"];

export default function ExploreScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [category, setCategory] = useState("All");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async (cat: string) => {
    try {
      const q = cat && cat !== "All" ? `?category=${cat}` : "";
      const data = await apiRequest<{ stocks: Stock[] }>(`/stocks${q}`);
      setStocks(data.stocks);
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      (async () => {
        await load(category);
        setLoading(false);
      })();
    }, [load, category])
  );

  useEffect(() => {
    setLoading(true);
    load(category).then(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locale]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load(category);
    setRefreshing(false);
  };

  const sortByWatch = (list: Stock[]) =>
    [...list].sort((a, b) => Number(!a.in_watchlist) - Number(!b.in_watchlist));

  const toggleWatch = async (symbol: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {});
    setStocks((prev) =>
      sortByWatch(
        prev.map((s) => (s.symbol === symbol ? { ...s, in_watchlist: !s.in_watchlist } : s))
      )
    );
    try {
      await apiRequest(`/watchlist/${symbol}/toggle`, { method: "POST" });
    } catch {
      // revert on failure
      setStocks((prev) =>
        sortByWatch(
          prev.map((s) => (s.symbol === symbol ? { ...s, in_watchlist: !s.in_watchlist } : s))
        )
      );
    }
  };

  const filtered = stocks.filter(
    (s) =>
      s.symbol.toLowerCase().includes(query.toLowerCase()) ||
      s.name.toLowerCase().includes(query.toLowerCase())
  );
  const watchedCount = filtered.filter((s) => s.in_watchlist).length;

  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.md }]}>
      <View style={styles.headerBlock}>
        <View style={styles.titleRow}>
          <HomeLogo />
          <View style={{ flex: 1, marginLeft: spacing.sm }}>
            <Text style={styles.title}>{t("explore.title")}</Text>
            <Text style={styles.subtitle}>{t("explore.subtitle")}</Text>
          </View>
          <LanguageButton />
        </View>

        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color={colors.muted} />
          <TextInput
            testID="stock-search-input"
            placeholder={t("explore.search")}
            placeholderTextColor={colors.muted}
            value={query}
            onChangeText={setQuery}
            style={styles.searchInput}
            autoCapitalize="characters"
            autoCorrect={false}
          />
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.chipRow}
          style={styles.chipScroller}
        >
          {CATEGORIES.map((cat) => {
            const active = cat === category;
            return (
              <Pressable
                key={cat}
                testID={`category-chip-${cat}`}
                onPress={() => {
                  setCategory(cat);
                  setLoading(true);
                }}
                style={[styles.chip, active && styles.chipActive]}
              >
                <Text style={[styles.chipText, active && styles.chipTextActive]}>{cat}</Text>
              </Pressable>
            );
          })}
        </ScrollView>
      </View>

      {loading ? (
        <Loading testID="explore-loading" />
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(s) => s.symbol}
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.xxxl }}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.brand} />
          }
          ListEmptyComponent={
            <View style={styles.empty}>
              <Ionicons name="search" size={40} color={colors.muted} />
              <Text style={styles.emptyText}>{t("explore.empty")}</Text>
            </View>
          }
          renderItem={({ item, index }) => {
            const up = item.change_pct >= 0;
            const showWatchHeader = watchedCount > 0 && index === 0;
            const showAllHeader = watchedCount > 0 && index === watchedCount;
            return (
              <>
                {showWatchHeader && (
                  <View style={styles.sectionHeader}>
                    <Ionicons name="star" size={14} color={colors.amber} />
                    <Text style={styles.sectionText}>{t("explore.watchlist")}</Text>
                  </View>
                )}
                {showAllHeader && (
                  <View style={[styles.sectionHeader, { marginTop: spacing.sm }]}>
                    <Text style={styles.sectionText}>{t("explore.allStocks")}</Text>
                  </View>
                )}
                <Pressable
                  testID={`stock-card-${item.symbol}`}
                  onPress={() => router.push(`/stock/${item.symbol}`)}
                  style={({ pressed }) => [styles.card, { opacity: pressed ? 0.85 : 1 }]}
                >
                  <View style={styles.cardTop}>
                    <StockLogo uri={item.logo} symbol={item.symbol} size={42} borderRadius={radius.sm} />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.symbol}>{item.symbol}</Text>
                      <Text style={styles.name} numberOfLines={1}>{item.name}</Text>
                    </View>
                    <View style={{ alignItems: "flex-end" }}>
                      <Text style={styles.price}>${item.price.toLocaleString()}</Text>
                      <View style={[styles.changeTag, { backgroundColor: up ? "#0C2E22" : "#2E0C0C" }]}>
                        <Ionicons
                          name={up ? "caret-up" : "caret-down"}
                          size={11}
                          color={up ? colors.brand : colors.error}
                        />
                        <Text style={[styles.changeText, { color: up ? colors.brand : colors.error }]}>
                          {Math.abs(item.change_pct).toFixed(2)}%
                        </Text>
                      </View>
                    </View>
                    <Pressable
                      testID={`watch-toggle-${item.symbol}`}
                      hitSlop={10}
                      onPress={() => toggleWatch(item.symbol)}
                      style={styles.starBtn}
                    >
                      <Ionicons
                        name={item.in_watchlist ? "star" : "star-outline"}
                        size={22}
                        color={item.in_watchlist ? colors.amber : colors.muted}
                      />
                    </Pressable>
                  </View>
                  <Text style={styles.explain} numberOfLines={2}>{item.explain}</Text>
                </Pressable>
              </>
            );
          }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  headerBlock: { paddingHorizontal: spacing.lg },
  titleRow: { flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between" },
  title: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface },
  subtitle: { fontFamily: fonts.body, fontSize: 14, color: colors.muted, marginTop: 2 },
  searchBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    height: 48,
    marginTop: spacing.lg,
  },
  searchInput: { flex: 1, color: colors.onSurface, fontFamily: fonts.body, fontSize: 15 },
  chipScroller: { marginTop: spacing.md, height: 56 },
  chipRow: { gap: spacing.sm, paddingRight: spacing.lg, alignItems: "center" },
  chip: {
    flexShrink: 0,
    height: 36,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurfaceSecondary },
  chipTextActive: { color: colors.onBrand },
  card: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  cardTop: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  starBtn: { paddingLeft: spacing.sm, paddingVertical: spacing.xs },
  sectionHeader: { flexDirection: "row", alignItems: "center", gap: spacing.xs, marginBottom: spacing.sm, marginLeft: spacing.xs },
  sectionText: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.muted, letterSpacing: 0.5, textTransform: "uppercase" },
  logo: { width: 42, height: 42, borderRadius: radius.sm, backgroundColor: "#FFFFFF" },
  symbol: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  name: { fontFamily: fonts.body, fontSize: 13, color: colors.muted },
  price: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  changeTag: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.sm,
    marginTop: 2,
  },
  changeText: { fontFamily: fonts.bodySemi, fontSize: 12 },
  explain: { fontFamily: fonts.body, fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 19, marginTop: spacing.md },
  empty: { alignItems: "center", paddingTop: spacing.xxxl, gap: spacing.md },
  emptyText: { fontFamily: fonts.body, fontSize: 14, color: colors.muted },
});
