import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, Pressable, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

const CATEGORIES = ["learning", "account", "billing", "technical", "other"] as const;

export default function Support() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const { user } = useAuth();
  const [category, setCategory] = useState<(typeof CATEGORIES)[number]>("learning");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [replyEmail, setReplyEmail] = useState(user?.email || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [ref, setRef] = useState("");

  const catLabel = (c: string) =>
    t(`support.cat${c.charAt(0).toUpperCase() + c.slice(1)}` as any);

  const submit = async () => {
    setError("");
    if (!subject.trim() || !message.trim()) {
      setError(t("support.error"));
      return;
    }
    setLoading(true);
    try {
      const res = await apiRequest<{ ref: string }>("/support/request", {
        method: "POST",
        body: {
          category,
          subject: subject.trim(),
          message: message.trim(),
          reply_email: replyEmail.trim() || undefined,
          lang: locale,
        },
      });
      setRef(res.ref);
    } catch (e: any) {
      setError(e.message || t("support.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.root} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="support-back" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.headerTitle}>{t("support.title")}</Text>
        <View style={{ width: 26 }} />
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.xxl }} keyboardShouldPersistTaps="handled">
        {ref ? (
          <View style={styles.doneBox}>
            <Ionicons name="checkmark-circle" size={22} color={colors.brand} />
            <Text testID="support-sent" style={styles.doneText}>{t("support.sent")} {ref}</Text>
          </View>
        ) : (
          <>
            <Text style={styles.subtitle}>{t("support.subtitle")}</Text>

            <Text style={styles.label}>{t("support.category")}</Text>
            <View style={styles.chips}>
              {CATEGORIES.map((c) => (
                <Pressable
                  key={c}
                  testID={`support-cat-${c}`}
                  onPress={() => setCategory(c)}
                  style={[styles.chip, category === c && styles.chipActive]}
                >
                  <Text style={[styles.chipText, category === c && styles.chipTextActive]}>{catLabel(c)}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.label}>{t("support.subject")}</Text>
            <TextInput
              testID="support-subject"
              value={subject}
              onChangeText={setSubject}
              style={styles.input}
              maxLength={120}
              placeholderTextColor={colors.muted}
            />

            {!user && (
              <>
                <Text style={styles.label}>{t("support.replyEmail")}</Text>
                <TextInput
                  testID="support-reply-email"
                  value={replyEmail}
                  onChangeText={setReplyEmail}
                  style={styles.input}
                  autoCapitalize="none"
                  keyboardType="email-address"
                  autoCorrect={false}
                  placeholderTextColor={colors.muted}
                />
              </>
            )}

            <Text style={styles.label}>{t("support.message")}</Text>
            <TextInput
              testID="support-message"
              value={message}
              onChangeText={setMessage}
              style={[styles.input, styles.textarea]}
              multiline
              maxLength={4000}
              placeholderTextColor={colors.muted}
            />

            {error ? <Text testID="support-error" style={styles.error}>{error}</Text> : null}

            <PrimaryButton
              testID="support-send"
              label={t("support.send")}
              onPress={submit}
              loading={loading}
              style={{ marginTop: spacing.lg }}
            />
          </>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.lg, paddingBottom: spacing.sm },
  headerTitle: { fontFamily: fonts.displayMed, fontSize: 17, color: colors.onSurface },
  subtitle: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, lineHeight: 22, marginBottom: spacing.lg },
  label: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.onSurfaceSecondary, marginBottom: spacing.sm, marginTop: spacing.md },
  chips: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  chip: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: 999, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.onSurface },
  chipTextActive: { color: colors.onBrand },
  input: {
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, paddingHorizontal: spacing.md, height: 50,
    fontFamily: fonts.body, fontSize: 15, color: colors.onSurface,
  },
  textarea: { height: 140, paddingTop: spacing.md, textAlignVertical: "top" },
  error: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.error, marginTop: spacing.sm },
  doneBox: {
    flexDirection: "row", gap: spacing.md, alignItems: "flex-start",
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1,
    borderColor: colors.border, padding: spacing.md,
  },
  doneText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurface, lineHeight: 21 },
});
