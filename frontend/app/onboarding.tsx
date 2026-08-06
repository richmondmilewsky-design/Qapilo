import React, { useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Animated,
  Platform,
  Pressable,
  useWindowDimensions,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { storage } from "@/src/utils/storage";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, spacing } from "@/src/theme/theme";

export const ONBOARDING_KEY = "qapilo_onboarding_done";

type Slide = { key: string; emoji: string; title: string; sub: string };

export default function Onboarding() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const { width } = useWindowDimensions();
  const listRef = useRef<FlatList>(null);
  const scrollX = useRef(new Animated.Value(0)).current;
  const [index, setIndex] = useState(0);

  const slides: Slide[] = [
    {
      key: "s1",
      emoji: "📈",
      title: t("onboarding.s1.title"),
      sub: t("onboarding.s1.sub"),
    },
    {
      key: "s2",
      emoji: "🎮",
      title: t("onboarding.s2.title"),
      sub: t("onboarding.s2.sub"),
    },
    {
      key: "s3",
      emoji: "🤖",
      title: t("onboarding.s3.title"),
      sub: t("onboarding.s3.sub"),
    },
  ];

  const finish = async () => {
    await storage.setItem(ONBOARDING_KEY, true);
    router.replace("/auth");
  };

  const next = () => {
    Haptics.selectionAsync();
    if (index < slides.length - 1) {
      const target = index + 1;
      setIndex(target);
      listRef.current?.scrollToIndex({ index: target, animated: true });
    } else {
      finish();
    }
  };

  const onScroll = (e: any) => {
    const i = Math.round(e.nativeEvent.contentOffset.x / width);
    if (i !== index) setIndex(i);
  };

  const handleScroll = Animated.event(
    [{ nativeEvent: { contentOffset: { x: scrollX } } }],
    { useNativeDriver: Platform.OS !== "web" }
  );

  const isLast = index === slides.length - 1;

  return (
    <View style={styles.root}>
      <LinearGradient colors={["#163b2c", "#0f2820", colors.surface]} locations={[0, 0.5, 1]} style={StyleSheet.absoluteFill} />

      <View style={[styles.topBar, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="onboarding-skip" onPress={finish} hitSlop={12}>
          <Text style={styles.skip}>{t("onboarding.skip")}</Text>
        </Pressable>
      </View>

      <Animated.FlatList
        ref={listRef as any}
        data={slides}
        keyExtractor={(s: any) => s.key}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        scrollEventThrottle={16}
        onScroll={handleScroll}
        onMomentumScrollEnd={onScroll}
        getItemLayout={(_: any, i: number) => ({ length: width, offset: width * i, index: i })}
        renderItem={({ item, index: i }: { item: Slide; index: number }) => {
          const inputRange = [(i - 1) * width, i * width, (i + 1) * width];
          const opacity = scrollX.interpolate({ inputRange, outputRange: [0.2, 1, 0.2], extrapolate: "clamp" });
          const translateY = scrollX.interpolate({ inputRange, outputRange: [26, 0, 26], extrapolate: "clamp" });
          return (
            <View style={[styles.slide, { width }]}>
              <Animated.View style={{ alignItems: "center", opacity, transform: [{ translateY }] }}>
                <View style={styles.badge}><Text style={styles.emoji}>{item.emoji}</Text></View>
                <Text testID={`onboarding-title-${item.key}`} style={styles.title}>{item.title}</Text>
                <Text style={styles.sub}>{item.sub}</Text>
                {item.key === "s3" && (
                  <View style={styles.ctaCard}>
                    <Text style={styles.ctaTitle}>{t("onboarding.s3.ctaTitle")}</Text>
                    <Text style={styles.ctaSub}>{t("onboarding.s3.ctaSub")}</Text>
                  </View>
                )}
              </Animated.View>
            </View>
          );
        }}
      />

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.lg }]}>
        <View style={styles.dots}>
          {slides.map((_, i) => (
            <View key={i} style={[styles.dot, i === index && styles.dotActive]} />
          ))}
        </View>
        <PrimaryButton
          testID="onboarding-next"
          label={isLast ? t("onboarding.start") : t("onboarding.next")}
          onPress={next}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  topBar: { flexDirection: "row", justifyContent: "flex-end", paddingHorizontal: spacing.lg, paddingBottom: spacing.sm },
  skip: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.muted },
  slide: { flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.xl },
  badge: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.xxl,
  },
  title: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface, textAlign: "center", marginBottom: spacing.md },
  sub: { fontFamily: fonts.body, fontSize: 16, color: colors.muted, textAlign: "center", lineHeight: 24, maxWidth: 320 },
  emoji: { fontSize: 64, lineHeight: 76, textAlign: "center" },
  ctaCard: {
    marginTop: spacing.xl,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.lg,
    maxWidth: 340,
  },
  ctaTitle: { fontFamily: fonts.bodySemi, fontSize: 17, color: colors.brand, textAlign: "center", marginBottom: spacing.xs },
  ctaSub: { fontFamily: fonts.body, fontSize: 14, color: colors.muted, textAlign: "center", lineHeight: 21 },
  footer: { paddingHorizontal: spacing.xl, paddingTop: spacing.md, gap: spacing.lg },
  dots: { flexDirection: "row", justifyContent: "center", gap: spacing.sm },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.border },
  dotActive: { width: 22, backgroundColor: colors.brand },
});
