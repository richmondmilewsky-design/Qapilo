import React from "react";
import { Pressable, Platform, Alert } from "react-native";
import { Image } from "expo-image";
import { useRouter } from "expo-router";
import { useI18n } from "@/src/i18n/I18nContext";

/**
 * The Qapilo wordmark/logo, tappable to jump back to the home tab (Learn).
 * Pass `confirm` on screens with unsaved progress (lesson/quiz) to show a
 * "leave?" dialog first. Subtle pressed state, no other visual change.
 */
export default function HomeLogo({
  confirm = false,
  size = 30,
  testID = "home-logo",
}: {
  confirm?: boolean;
  size?: number;
  testID?: string;
}) {
  const router = useRouter();
  const { t } = useI18n();

  const go = () => router.navigate("/(tabs)");

  const onPress = () => {
    if (!confirm) return go();
    const title = t("nav.leaveTitle");
    const msg = t("nav.leaveMsg");
    if (Platform.OS === "web") {
      if (typeof window !== "undefined" && window.confirm(`${title}\n\n${msg}`)) go();
      return;
    }
    Alert.alert(title, msg, [
      { text: t("common.cancel"), style: "cancel" },
      { text: t("nav.leaveConfirm"), style: "destructive", onPress: go },
    ]);
  };

  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      hitSlop={10}
      accessibilityRole="button"
      style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}
    >
      <Image
        source={require("../../assets/images/qapilo-logo.png")}
        style={{ width: size, height: size }}
        contentFit="contain"
      />
    </Pressable>
  );
}
