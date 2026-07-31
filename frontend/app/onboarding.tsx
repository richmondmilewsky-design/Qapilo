import React, { useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Pressable,
  useWindowDimensions,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { storage } from "@/src/utils/storage";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, spacing } from "@/src/theme/theme";

export const ONBOARDING_KEY = "qapilo_onboarding_done";

type Slide = { key: string; icon: React.ReactNode; title: string; sub: string };

export default function Onboarding() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const { width } = useWindowDimensions();
  const listRef = useRef<FlatList>(null);
  const [index, setIndex] = useState(0);

  const slides: Slide[] = [
    {
      key: "s1",
      icon: <MaterialCommunityIcons name="chart-line-variant" size={64} color={colors.brand} />,
      title: t("onboarding.s1.title"),
      sub: t("onboarding.s1.sub"),
    },
    {
      key: "s2",
      icon: <MaterialCommunityIcons name="robot-happy" size={64} color={colors.brand} />,
      title: t("onboarding.s2.title"),
      sub: t("onboarding.s2.sub"),
    },
    {
      key: "s3",
      icon: <Ionicons name="game-controller" size={60} color={colors.brand} />,
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

  const isLast = index === slides.length - 1;

  return (
    <View style={styles.root}>
      <LinearGradient colors={["#052E20", colors.surface, colors.surface]} style={StyleSheet.absoluteFill} />

      <View style={[styles.topBar, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="onboarding-skip" onPress={finish} hitSlop={12}>
          <Text style={styles.skip}>{t("onboarding.skip")}</Text>
        </Pressable>
      </View>

      <FlatList
        ref={listRef}
        data={slides}
        keyExtractor={(s) => s.key}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={onScroll}
        getItemLayout={(_, i) => ({ length: width, offset: width * i, index: i })}
        renderItem={({ item }) => (
          <View style={[styles.slide, { width }]}>
            <View style={styles.badge}>{item.icon}</View>
            <Text testID={`onboarding-title-${item.key}`} style={styles.title}>{item.title}</Text>
            <Text style={styles.sub}>{item.sub}</Text>
          </View>
        )}
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
  footer: { paddingHorizontal: spacing.xl, paddingTop: spacing.md, gap: spacing.lg },
  dots: { flexDirection: "row", justifyContent: "center", gap: spacing.sm },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.border },
  dotActive: { width: 22, backgroundColor: colors.brand },
});
