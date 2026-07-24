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
import { DISCLAIMER_SECTIONS } from "@/src/constants/disclaimer";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export default function Agreement() {
  const { setUser, logout } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const [checked, setChecked] = useState(false);
  const [busy, setBusy] = useState(false);

  const agree = async () => {
    if (!checked) return;
    setBusy(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const res = await apiRequest<{ user: any }>("/auth/accept-terms", { method: "POST" });
      setUser(res.user);
      router.replace("/(tabs)");
    } catch {
      setBusy(false);
    }
  };

  const decline = async () => {
    await logout();
    router.replace("/auth");
  };

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
        {DISCLAIMER_SECTIONS.map((s) => (
          <View key={s.heading} style={styles.section}>
            <Text style={styles.heading}>{s.heading}</Text>
            <Text style={styles.body}>{s.body}</Text>
          </View>
        ))}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <Pressable
          testID="agree-checkbox"
          onPress={() => setChecked((c) => !c)}
          style={styles.checkRow}
        >
          <View style={[styles.checkbox, checked && styles.checkboxOn]}>
            {checked && <Ionicons name="checkmark" size={16} color={colors.onBrand} />}
          </View>
          <Text style={styles.checkLabel}>
            {t("agree.checkbox")}
          </Text>
        </Pressable>
        <PrimaryButton
          testID="agree-continue-button"
          label={t("agree.continue")}
          onPress={agree}
          disabled={!checked}
          loading={busy}
        />
        <Pressable testID="decline-button" onPress={decline} style={styles.decline}>
          <Text style={styles.declineText}>{t("agree.decline")}</Text>
        </Pressable>
      </View>
    </View>
  );
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
  checkRow: { flexDirection: "row", alignItems: "center", gap: spacing.md },
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
  checkLabel: { flex: 1, fontFamily: fonts.body, fontSize: 13, color: colors.onSurface, lineHeight: 19 },
  decline: { alignItems: "center", paddingVertical: spacing.sm },
  declineText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.muted },
});
