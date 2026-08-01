import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, Pressable, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export default function ForgotPassword() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState("");

  const submit = async () => {
    if (!email.trim()) return;
    setLoading(true);
    try {
      const res = await apiRequest<{ message: string }>("/auth/forgot-password", {
        method: "POST",
        auth: false,
        body: { email: email.trim().toLowerCase(), lang: locale },
      });
      setDone(res.message);
    } catch {
      setDone(t("forgot.subtitle"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.root} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="forgot-back" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
      </View>
      <View style={styles.body}>
        <Text style={styles.title}>{t("forgot.title")}</Text>
        <Text style={styles.subtitle}>{t("forgot.subtitle")}</Text>

        {done ? (
          <View style={styles.doneBox}>
            <Ionicons name="mail-outline" size={22} color={colors.brand} />
            <Text testID="forgot-done" style={styles.doneText}>{done}</Text>
          </View>
        ) : (
          <TextInput
            testID="forgot-email"
            placeholder={t("auth.email")}
            placeholderTextColor={colors.muted}
            value={email}
            onChangeText={setEmail}
            style={styles.input}
            autoCapitalize="none"
            keyboardType="email-address"
            autoCorrect={false}
            returnKeyType="go"
            onSubmitEditing={submit}
          />
        )}

        {!done && (
          <PrimaryButton
            testID="forgot-send"
            label={t("forgot.send")}
            onPress={submit}
            loading={loading}
            style={{ marginTop: spacing.md }}
          />
        )}

        <Pressable
          testID="forgot-to-reset"
          onPress={() => router.push("/reset-password")}
          style={{ alignSelf: "center", marginTop: spacing.lg }}
        >
          <Text style={styles.link}>{t("reset.title")}</Text>
        </Pressable>
        <Pressable onPress={() => router.replace("/auth")} style={{ alignSelf: "center", marginTop: spacing.md }}>
          <Text style={styles.muted}>{t("forgot.back")}</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: { paddingHorizontal: spacing.lg, paddingBottom: spacing.sm },
  body: { flex: 1, paddingHorizontal: spacing.lg },
  title: { fontFamily: fonts.display, fontSize: 28, color: colors.onSurface, marginBottom: spacing.sm },
  subtitle: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, lineHeight: 22, marginBottom: spacing.xl },
  input: {
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, paddingHorizontal: spacing.md, height: 52,
    fontFamily: fonts.body, fontSize: 16, color: colors.onSurface,
  },
  doneBox: {
    flexDirection: "row", gap: spacing.md, alignItems: "flex-start",
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, padding: spacing.md,
  },
  doneText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurface, lineHeight: 21 },
  link: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.brand },
  muted: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.muted },
});
