import React, { useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

type Level = "beginner" | "some" | "advanced";

export default function Experience() {
  const { setExperience } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const [selected, setSelected] = useState<Level | null>(null);
  const [busy, setBusy] = useState(false);

  const options: { key: Level; label: string; desc: string }[] = [
    { key: "beginner", label: t("experience.beginner"), desc: t("experience.beginnerDesc") },
    { key: "some", label: t("experience.some"), desc: t("experience.someDesc") },
    { key: "advanced", label: t("experience.advanced"), desc: t("experience.advancedDesc") },
  ];

  const submit = async () => {
    if (!selected || busy) return;
    setBusy(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      await setExperience(selected);
      if (selected === "beginner") {
        router.replace("/(tabs)");
      } else {
        router.replace(`/placement-quiz?experience=${selected}`);
      }
    } catch {
      setBusy(false);
    }
  };

  return (
    <View style={styles.root}>
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{
          padding: spacing.lg,
          paddingTop: insets.top + spacing.xxl,
          paddingBottom: spacing.xl,
        }}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title} testID="experience-title">{t("experience.title")}</Text>
        <Text style={styles.subtitle}>{t("experience.subtitle")}</Text>

        <View style={{ marginTop: spacing.xxl, gap: spacing.md }}>
          {options.map((o) => {
            const active = selected === o.key;
            return (
              <Pressable
                key={o.key}
                testID={`experience-option-${o.key}`}
                onPress={() => {
                  Haptics.selectionAsync();
                  setSelected(o.key);
                }}
                style={[styles.option, active && styles.optionActive]}
              >
                <View style={{ flex: 1, paddingRight: spacing.md }}>
                  <Text style={[styles.optLabel, active && styles.optLabelActive]}>{o.label}</Text>
                  <Text style={styles.optDesc}>{o.desc}</Text>
                </View>
                <View style={[styles.radio, active && styles.radioActive]}>
                  {active && <Ionicons name="checkmark" size={16} color={colors.onBrand} />}
                </View>
              </Pressable>
            );
          })}
        </View>
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <PrimaryButton
          testID="experience-continue"
          label={t("experience.continue")}
          onPress={submit}
          disabled={!selected}
          loading={busy}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  title: { fontFamily: fonts.display, fontSize: 28, color: colors.onSurface, lineHeight: 34 },
  subtitle: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, marginTop: spacing.sm, lineHeight: 22 },
  option: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.lg,
    padding: spacing.lg,
    minHeight: 72,
  },
  optionActive: { borderColor: colors.brand, backgroundColor: "rgba(45, 212, 160, 0.08)" },
  optLabel: { fontFamily: fonts.bodySemi, fontSize: 17, color: colors.onSurface },
  optLabelActive: { color: colors.brand },
  optDesc: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginTop: 3, lineHeight: 18 },
  radio: {
    width: 26,
    height: 26,
    borderRadius: 13,
    borderWidth: 2,
    borderColor: colors.borderStrong,
    alignItems: "center",
    justifyContent: "center",
  },
  radioActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
  },
});
