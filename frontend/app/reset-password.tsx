import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, Pressable } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { Ionicons } from "@expo/vector-icons";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export default function ResetPassword() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const params = useLocalSearchParams<{ token?: string }>();
  const [token, setToken] = useState((params.token as string) || "");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const submit = async () => {
    setError("");
    if (!token.trim() || password.length < 8) {
      setError(t("reset.newPassword"));
      return;
    }
    setLoading(true);
    try {
      await apiRequest("/auth/reset-password", {
        method: "POST",
        auth: false,
        body: { token: token.trim(), new_password: password, lang: locale },
      });
      setDone(true);
    } catch (e: any) {
      setError(e.message || t("support.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.root}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="reset-back" onPress={() => router.replace("/auth")} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
      </View>
      <KeyboardAwareScrollView
        style={{ flex: 1 }}
        contentContainerStyle={styles.body}
        keyboardShouldPersistTaps="handled"
        keyboardDismissMode="on-drag"
        showsVerticalScrollIndicator={false}
        bottomOffset={24}
      >
        <Text style={styles.title}>{t("reset.title")}</Text>
        <Text style={styles.subtitle}>{t("reset.subtitle")}</Text>

        {done ? (
          <View style={styles.doneBox}>
            <Ionicons name="checkmark-circle" size={22} color={colors.brand} />
            <Text testID="reset-success" style={styles.doneText}>{t("reset.success")}</Text>
          </View>
        ) : (
          <>
            <TextInput
              testID="reset-token"
              placeholder={t("reset.tokenPlaceholder")}
              placeholderTextColor={colors.muted}
              value={token}
              onChangeText={setToken}
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <TextInput
              testID="reset-password"
              placeholder={t("reset.newPassword")}
              placeholderTextColor={colors.muted}
              value={password}
              onChangeText={setPassword}
              style={[styles.input, { marginTop: spacing.md }]}
              secureTextEntry
              returnKeyType="go"
              onSubmitEditing={submit}
            />
            {error ? <Text testID="reset-error" style={styles.error}>{error}</Text> : null}
            <PrimaryButton
              testID="reset-submit"
              label={t("reset.submit")}
              onPress={submit}
              loading={loading}
              style={{ marginTop: spacing.md }}
            />
          </>
        )}

        {done && (
          <PrimaryButton
            testID="reset-go-login"
            label={t("forgot.back")}
            onPress={() => router.replace("/auth")}
            style={{ marginTop: spacing.lg }}
          />
        )}
      </KeyboardAwareScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: { paddingHorizontal: spacing.lg, paddingBottom: spacing.sm },
  body: { paddingHorizontal: spacing.lg },
  title: { fontFamily: fonts.display, fontSize: 28, color: colors.onSurface, marginBottom: spacing.sm },
  subtitle: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, lineHeight: 22, marginBottom: spacing.xl },
  input: {
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, paddingHorizontal: spacing.md, height: 52,
    fontFamily: fonts.body, fontSize: 16, color: colors.onSurface,
  },
  error: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.error, marginTop: spacing.sm },
  doneBox: {
    flexDirection: "row", gap: spacing.md, alignItems: "flex-start",
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, padding: spacing.md,
  },
  doneText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurface, lineHeight: 21 },
});
