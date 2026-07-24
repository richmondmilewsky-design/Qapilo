import React from "react";
import { Pressable, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useI18n } from "@/src/i18n/I18nContext";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export function LanguageButton() {
  const { locale, openPicker } = useI18n();
  return (
    <Pressable testID="language-button" onPress={openPicker} style={styles.btn} hitSlop={8}>
      <Ionicons name="globe-outline" size={16} color={colors.onSurface} />
      <Text style={styles.text}>{locale.toUpperCase()}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: spacing.md,
    height: 34,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
  },
  text: { fontFamily: fonts.bodySemi, fontSize: 12, color: colors.onSurface },
});
