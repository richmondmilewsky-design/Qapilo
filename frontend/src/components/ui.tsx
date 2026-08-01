import React from "react";
import {
  Pressable,
  Text,
  StyleSheet,
  View,
  ActivityIndicator,
  ViewStyle,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { colors, fonts, radius, spacing, gradients, shadows } from "@/src/theme/theme";

export function PrimaryButton({
  label,
  onPress,
  loading,
  disabled,
  variant = "brand",
  testID,
  style,
}: {
  label: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: "brand" | "amber" | "outline";
  testID?: string;
  style?: ViewStyle;
}) {
  const fg =
    variant === "brand" ? colors.onBrand : variant === "amber" ? colors.onAmber : colors.onSurface;
  const isDisabled = disabled || loading;
  const gradient = variant === "brand" ? gradients.brand : variant === "amber" ? ["#f0a83e", "#d98420"] as const : null;

  return (
    <Pressable
      testID={testID}
      disabled={isDisabled}
      onPress={() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        onPress();
      }}
      style={({ pressed }) => [
        variant === "brand" ? shadows.brand : null,
        {
          borderRadius: radius.md,
          opacity: isDisabled ? 0.5 : pressed ? 0.9 : 1,
          transform: [{ scale: pressed ? 0.98 : 1 }],
        },
        style,
      ]}
    >
      {gradient ? (
        <LinearGradient colors={gradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.btn}>
          {loading ? <ActivityIndicator color={fg} /> : <Text style={[styles.btnText, { color: fg }]}>{label}</Text>}
        </LinearGradient>
      ) : (
        <View style={[styles.btn, styles.outline]}>
          {loading ? <ActivityIndicator color={fg} /> : <Text style={[styles.btnText, { color: fg }]}>{label}</Text>}
        </View>
      )}
    </Pressable>
  );
}

export function Loading({ testID }: { testID?: string }) {
  return (
    <View testID={testID} style={styles.center}>
      <ActivityIndicator size="large" color={colors.brand} />
    </View>
  );
}

const styles = StyleSheet.create({
  btn: {
    height: 54,
    borderRadius: radius.md,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.lg,
  },
  outline: {
    backgroundColor: "rgba(255,255,255,0.06)",
    borderWidth: 1,
    borderColor: colors.border,
  },
  btnText: { fontFamily: fonts.bodySemi, fontSize: 16, letterSpacing: 0.2 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.surface },
});
