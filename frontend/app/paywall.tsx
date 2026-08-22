import React, { useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import {
  PLANS,
  DEFAULT_PLAN_ID,
  FREE_FEATURE_KEYS,
  PREMIUM_FEATURE_KEYS,
  PlanId,
  PlanOffer,
} from "@/src/constants/plans";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

function trialKey(days: number) {
  return days === 30 ? "pw.trial30" : days === 7 ? "pw.trial7" : "pw.noTrial";
}

export default function Paywall() {
  const { user, setUser } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const [selected, setSelected] = useState<PlanId>(DEFAULT_PLAN_ID);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  const isPremium = !!user?.is_pro && user?.pro_source === "subscription";
  const selectedPlan: PlanOffer = PLANS.find((p) => p.id === selected) || PLANS[0];

  const close = () => {
    if (router.canGoBack()) router.back();
    else router.replace("/(tabs)");
  };

  // Placeholder purchase — real StoreKit / Play Billing arrives in a later step.
  const purchase = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setNote(t("pw.placeholderNote"));
  };

  const restore = async () => {
    setBusy(true);
    setNote("");
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    try {
      const res = await apiRequest<{ user: any }>("/subscription/status");
      setUser(res.user);
      if (res.user.is_pro) setNote(t("pw.premiumActive"));
      else setNote(t("pw.placeholderNote"));
    } catch {
      setNote(t("pw.placeholderNote"));
    } finally {
      setBusy(false);
    }
  };

  // For plans with an annual price the MONTHLY figure is shown big/white on top
  // and the yearly figure small/muted underneath. The monthly-only plan (no
  // perMonth) is unchanged.
  const priceLine = (p: PlanOffer) =>
    p.perMonth
      ? `${p.perMonth} ${p.currency} ${t("pw.per_month")}`
      : `${p.price} ${p.currency} ${t(p.period === "year" ? "pw.per_year" : "pw.per_month")}`;
  const perMonthLine = (p: PlanOffer) =>
    p.perMonth ? `${t("pw.equals")} ${p.price} ${p.currency} ${t("pw.per_year")}` : null;

  const ctaLabel = selectedPlan.cta === "trial" ? t("pw.ctaTrial") : t("pw.ctaUnlock");

  return (
    <View style={styles.root}>
      <LinearGradient colors={["#1A1405", colors.surface, colors.surface]} style={StyleSheet.absoluteFill} />
      <ScrollView
        contentContainerStyle={{
          padding: spacing.lg,
          paddingTop: insets.top + spacing.lg,
          paddingBottom: insets.bottom + spacing.xxxl,
        }}
        showsVerticalScrollIndicator={false}
      >
        <Pressable testID="paywall-close" onPress={close} style={styles.close} hitSlop={12}>
          <Ionicons name="close" size={26} color={colors.muted} />
        </Pressable>

        <View style={styles.crown}>
          <MaterialCommunityIcons name="crown" size={38} color={colors.onAmber} />
        </View>
        <Text style={styles.title} testID="paywall-title">{t("pw.title")}</Text>
        <Text style={styles.subtitle}>{t("pw.subtitle")}</Text>

        {isPremium ? (
          <View style={styles.activeBadge} testID="pro-active-badge">
            <MaterialCommunityIcons name="check-decagram" size={20} color={colors.brand} />
            <Text style={styles.activeText}>{t("pw.premiumActive")}</Text>
          </View>
        ) : null}

        {/* Free vs Premium comparison */}
        <View style={styles.compareRow}>
          <View style={styles.compareCol}>
            <Text style={styles.compareHead}>{t("pw.freeTitle")}</Text>
            {FREE_FEATURE_KEYS.map((k) => (
              <View key={k} style={styles.compItem}>
                <Ionicons name="remove-circle-outline" size={16} color={colors.muted} />
                <Text style={styles.compFree}>{t(k)}</Text>
              </View>
            ))}
          </View>
          <View style={[styles.compareCol, styles.compareColPro]}>
            <Text style={[styles.compareHead, { color: colors.brand }]}>{t("pw.premiumTitle")}</Text>
            {PREMIUM_FEATURE_KEYS.map((k) => (
              <View key={k} style={styles.compItem}>
                <Ionicons name="checkmark-circle" size={16} color={colors.brand} />
                <Text style={styles.compPrem}>{t(k)}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Offers */}
        {!isPremium && (
          <View style={{ marginTop: spacing.xl, gap: spacing.md }}>
            {PLANS.map((p) => {
              const active = selected === p.id;
              const perMonth = perMonthLine(p);
              return (
                <Pressable
                  key={p.id}
                  testID={`plan-${p.id}`}
                  onPress={() => {
                    Haptics.selectionAsync();
                    setSelected(p.id);
                  }}
                  style={[styles.plan, active && styles.planActive]}
                >
                  {p.highlight && (
                    <View style={styles.popular}>
                      <Text style={styles.popularText}>{t("pw.mostPopular")}</Text>
                    </View>
                  )}
                  <View style={styles.planTop}>
                    <View style={{ flex: 1, paddingRight: spacing.md }}>
                      <Text style={[styles.planTitle, active && { color: colors.brand }]}>{t(p.titleKey)}</Text>
                      <Text style={styles.planTrial}>{t(trialKey(p.trialDays))}</Text>
                    </View>
                    <View style={[styles.radio, active && styles.radioActive]}>
                      {active && <Ionicons name="checkmark" size={15} color={colors.onBrand} />}
                    </View>
                  </View>
                  <Text style={styles.planPrice}>{priceLine(p)}</Text>
                  {perMonth ? <Text style={styles.planPer}>{perMonth}</Text> : null}
                  {p.members ? <Text style={styles.planPer}>{t("pw.members")}</Text> : null}
                  {p.descKey ? <Text style={styles.planDesc}>{t(p.descKey)}</Text> : null}
                </Pressable>
              );
            })}
          </View>
        )}

        {note ? <Text style={styles.note} testID="paywall-note">{note}</Text> : null}

        {!isPremium && (
          <>
            <PrimaryButton
              testID="paywall-cta"
              label={ctaLabel}
              variant="amber"
              loading={busy}
              onPress={purchase}
              style={{ marginTop: spacing.xl }}
            />
            <Text style={styles.cancel}>{t("pw.cancelAnytime")}</Text>

            <Pressable testID="restore-button" onPress={restore} disabled={busy} style={styles.restore}>
              <Ionicons name="refresh" size={16} color={colors.onSurfaceSecondary} />
              <Text style={styles.restoreText}>{t("pw.restore")}</Text>
            </Pressable>
          </>
        )}

        <View style={styles.legalRow}>
          <Text testID="link-privacy" style={styles.legalLink} onPress={() => router.push("/privacy")}>
            {t("pw.privacy")}
          </Text>
          <Text style={styles.legalDot}>·</Text>
          <Text testID="link-terms" style={styles.legalLink} onPress={() => router.push("/doc?type=terms" as any)}>
            {t("pw.terms")}
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  close: { alignSelf: "flex-end", marginBottom: spacing.sm },
  crown: {
    width: 72, height: 72, borderRadius: radius.lg, backgroundColor: colors.amber,
    alignItems: "center", justifyContent: "center", alignSelf: "center", marginBottom: spacing.md,
  },
  title: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface, textAlign: "center", lineHeight: 36 },
  subtitle: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, textAlign: "center", marginTop: spacing.sm, lineHeight: 22 },
  activeBadge: {
    flexDirection: "row", alignItems: "center", justifyContent: "center", gap: spacing.sm,
    backgroundColor: "#0C2E22", borderRadius: radius.md, padding: spacing.lg, marginTop: spacing.xl,
  },
  activeText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.brand },
  compareRow: { flexDirection: "row", gap: spacing.md, marginTop: spacing.xl },
  compareCol: {
    flex: 1, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border, padding: spacing.md, gap: spacing.sm,
  },
  compareColPro: { borderColor: colors.brand },
  compareHead: { fontFamily: fonts.displayMed, fontSize: 13, color: colors.muted, letterSpacing: 1, textTransform: "uppercase", marginBottom: spacing.xs },
  compItem: { flexDirection: "row", alignItems: "flex-start", gap: spacing.xs },
  compFree: { flex: 1, fontFamily: fonts.body, fontSize: 12.5, color: colors.muted, lineHeight: 18 },
  compPrem: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 12.5, color: colors.onSurface, lineHeight: 18 },
  plan: {
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1.5,
    borderColor: colors.border, padding: spacing.lg,
  },
  planActive: { borderColor: colors.brand, backgroundColor: "rgba(45, 212, 160, 0.08)" },
  popular: {
    position: "absolute", top: -10, right: spacing.lg, backgroundColor: colors.amber,
    borderRadius: radius.pill, paddingHorizontal: spacing.md, paddingVertical: 3,
  },
  popularText: { fontFamily: fonts.bodySemi, fontSize: 11, color: colors.onAmber, letterSpacing: 0.3 },
  planTop: { flexDirection: "row", alignItems: "center" },
  planTitle: { fontFamily: fonts.bodySemi, fontSize: 17, color: colors.onSurface },
  planTrial: { fontFamily: fonts.bodyMed, fontSize: 12.5, color: colors.brand, marginTop: 2 },
  planPrice: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface, marginTop: spacing.md },
  planPer: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginTop: 2 },
  planDesc: { fontFamily: fonts.body, fontSize: 13, color: colors.onSurfaceSecondary, marginTop: spacing.sm, lineHeight: 19 },
  radio: {
    width: 26, height: 26, borderRadius: 13, borderWidth: 2, borderColor: colors.borderStrong,
    alignItems: "center", justifyContent: "center",
  },
  radioActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  note: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.amber, textAlign: "center", marginTop: spacing.lg },
  cancel: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.muted, textAlign: "center", marginTop: spacing.md },
  restore: {
    flexDirection: "row", alignItems: "center", justifyContent: "center", gap: spacing.sm,
    marginTop: spacing.lg, paddingVertical: spacing.md,
  },
  restoreText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurfaceSecondary },
  legalRow: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: spacing.sm, marginTop: spacing.lg },
  legalLink: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.brand },
  legalDot: { color: colors.muted },
});
