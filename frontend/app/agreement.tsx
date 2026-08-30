import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { apiRequest } from "@/src/api/client";
import { PrimaryButton } from "@/src/components/ui";
import { getDisclaimer } from "@/src/constants/disclaimer";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export default function Agreement() {
  const { setUser, logout } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const disclaimerDoc = getDisclaimer(locale);
  const [terms, setTerms] = useState(false);
  const [disclaimer, setDisclaimer] = useState(false);
  const [analytics, setAnalytics] = useState(false);
  const [product, setProduct] = useState(false);
  const [marketing, setMarketing] = useState(false);
  const [busy, setBusy] = useState(false);

  const canContinue = terms && disclaimer;

  const agree = async () => {
    if (!canContinue) return;
    setBusy(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const res = await apiRequest<{ user: any }>("/auth/accept-terms", {
        method: "POST",
        body: {
          accepted_terms: terms,
          accepted_disclaimer: disclaimer,
          consent_analytics: analytics,
          consent_product: product,
          // Marketing opt-in is double opt-in server-side: res.user.consent_marketing
          // may still be false here until the user confirms an emailed code in Settings.
          consent_marketing: marketing,
        },
      });
      setUser(res.user);
      router.replace("/");
    } catch {
      setBusy(false);
    }
  };

  const decline = async () => {
    await logout();
    router.replace("/auth");
  };

  const CheckRow = ({ value, onToggle, label, testID, box = true }: any) => (
    <Pressable testID={testID} onPress={onToggle} style={styles.checkRow}>
      <View style={[box ? styles.checkbox : styles.toggleBox, value && (box ? styles.checkboxOn : styles.toggleBoxOn)]}>
        {value && <Ionicons name="checkmark" size={16} color={colors.onBrand} />}
      </View>
      <Text style={styles.checkLabel}>{label}</Text>
    </Pressable>
  );

  const OptRow = ({ value, onToggle, label, desc, testID }: any) => (
    <Pressable testID={testID} onPress={onToggle} style={styles.optRow}>
      <View style={{ flex: 1, paddingRight: spacing.md }}>
        <Text style={styles.optLabel}>{label}</Text>
        <Text style={styles.optDesc}>{desc}</Text>
      </View>
      <View style={[styles.checkbox, value && styles.checkboxOn]}>
        {value && <Ionicons name="checkmark" size={16} color={colors.onBrand} />}
      </View>
    </Pressable>
  );

  return (
    <View style={styles.root}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.lg }]}>
        <View style={styles.badge}>
          <MaterialCommunityIcons name="scale-balance" size={26} color={colors.onBrand} />
        </View>
        <Text style={styles.title}>{t("agree.title")}</Text>
        <Text style={styles.intro}>{t("agree.intro")}</Text>
      </View>

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.xl }}
        showsVerticalScrollIndicator={true}
      >
        {disclaimer_sections(disclaimerDoc).map((s) => (
          <View key={s.heading} style={styles.section}>
            <Text style={styles.heading}>{s.heading}</Text>
            <Text style={styles.body}>{s.body}</Text>
          </View>
        ))}

        {/* Required consents */}
        <Text style={styles.groupLabel}>{t("agree.requiredTitle")}</Text>
        <View style={styles.consentCard}>
          <CheckRow testID="req-terms" value={terms} onToggle={() => setTerms((v) => !v)} label={t("agree.reqTerms")} />
          <CheckRow testID="req-disclaimer" value={disclaimer} onToggle={() => setDisclaimer((v) => !v)} label={t("agree.reqDisclaimer")} />
        </View>

        {/* Optional consents */}
        <Text style={styles.groupLabel}>{t("agree.optionalTitle")}</Text>
        <View style={styles.consentCard}>
          <OptRow testID="opt-analytics" value={analytics} onToggle={() => setAnalytics((v) => !v)} label={t("agree.optAnalytics")} desc={t("agree.optAnalyticsDesc")} />
          <OptRow testID="opt-product" value={product} onToggle={() => setProduct((v) => !v)} label={t("agree.optProduct")} desc={t("agree.optProductDesc")} />
          <OptRow testID="opt-marketing" value={marketing} onToggle={() => setMarketing((v) => !v)} label={t("agree.optMarketing")} desc={t("agree.optMarketingDesc")} />
        </View>
        <Text style={styles.optionalHint}>{t("agree.optionalHint")}</Text>
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <Text style={styles.privacyLine}>
          {t("agree.privacyLine")}{" "}
          <Text
            testID="agree-privacy-link"
            style={styles.privacyLink}
            onPress={() => router.push("/privacy")}
          >
            {t("agree.viewPrivacy")}
          </Text>
        </Text>
        <PrimaryButton
          testID="agree-continue-button"
          label={t("agree.continue")}
          onPress={agree}
          disabled={!canContinue}
          loading={busy}
        />
        <Pressable testID="decline-button" onPress={decline} style={styles.decline}>
          <Text style={styles.declineText}>{t("agree.decline")}</Text>
        </Pressable>
      </View>
    </View>
  );
}

function disclaimer_sections(d: any) {
  return d.sections as { heading: string; body: string }[];
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: { paddingHorizontal: spacing.lg, paddingBottom: spacing.lg, borderBottomWidth: 1, borderBottomColor: colors.border },
  badge: {
    width: 56,
    height: 56,
    borderRadius: radius.md,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.md,
  },
  title: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface },
  intro: { fontFamily: fonts.body, fontSize: 14, color: colors.muted, marginTop: 4 },
  section: { marginBottom: spacing.lg },
  heading: { fontFamily: fonts.bodySemi, fontSize: 16, color: colors.brand, marginBottom: spacing.xs },
  body: { fontFamily: fonts.body, fontSize: 14, color: colors.onSurfaceSecondary, lineHeight: 22 },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
    gap: spacing.md,
  },
  checkRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.sm },
  checkbox: {
    width: 26,
    height: 26,
    borderRadius: radius.sm,
    borderWidth: 2,
    borderColor: colors.borderStrong,
    alignItems: "center",
    justifyContent: "center",
  },
  checkboxOn: { backgroundColor: colors.brand, borderColor: colors.brand },
  toggleBox: {
    width: 26, height: 26, borderRadius: radius.sm, borderWidth: 2,
    borderColor: colors.borderStrong, alignItems: "center", justifyContent: "center",
  },
  toggleBoxOn: { backgroundColor: colors.brand, borderColor: colors.brand },
  checkLabel: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurface, lineHeight: 20 },
  groupLabel: { fontFamily: fonts.displayMed, fontSize: 12, color: colors.muted, letterSpacing: 1.2, textTransform: "uppercase", marginTop: spacing.lg, marginBottom: spacing.sm },
  consentCard: { backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, paddingHorizontal: spacing.md },
  optRow: { flexDirection: "row", alignItems: "center", paddingVertical: spacing.md, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: colors.border, minHeight: 52 },
  optLabel: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface },
  optDesc: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: 2, lineHeight: 17 },
  optionalHint: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: spacing.sm, lineHeight: 18 },
  privacyLine: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, lineHeight: 18, marginTop: -spacing.xs },
  privacyLink: { fontFamily: fonts.bodySemi, color: colors.brand },
  decline: { alignItems: "center", paddingVertical: spacing.sm },
  declineText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.muted },
});
