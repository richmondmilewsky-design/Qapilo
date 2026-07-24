import React from "react";
import {
  Pressable,
  Text,
  StyleSheet,
  View,
  ActivityIndicator,
  ViewStyle,
} from "react-native";
import * as Haptics from "expo-haptics";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

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
  const bg =
    variant === "brand" ? colors.brand : variant === "amber" ? colors.amber : "transparent";
  const fg =
    variant === "brand" ? colors.onBrand : variant === "amber" ? colors.onAmber : colors.onSurface;
  const isDisabled = disabled || loading;
  return (
    <Pressable
      testID={testID}
      disabled={isDisabled}
      onPress={() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        onPress();
      }}
      style={({ pressed }) => [
        styles.btn,
        {
          backgroundColor: bg,
          borderWidth: variant === "outline" ? 1.5 : 0,
          borderColor: colors.borderStrong,
          opacity: isDisabled ? 0.5 : pressed ? 0.85 : 1,
          transform: [{ scale: pressed ? 0.98 : 1 }],
        },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={fg} />
      ) : (
        <Text style={[styles.btnText, { color: fg }]}>{label}</Text>
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
  btnText: { fontFamily: fonts.bodySemi, fontSize: 16, letterSpacing: 0.3 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.surface },
});
