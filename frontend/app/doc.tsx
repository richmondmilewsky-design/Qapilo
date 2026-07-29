import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, TextInput, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { getDoc, DocType } from "@/src/constants/legalDocs";
import { useI18n } from "@/src/i18n/I18nContext";
import { useAuth } from "@/src/context/AuthContext";
import { apiRequest } from "@/src/api/client";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export default function DocScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { type } = useLocalSearchParams<{ type: DocType }>();
  const { t, locale } = useI18n();
  const { user, setUser } = useAuth();
  const docType = (type || "terms") as DocType;
  const doc = getDoc(docType, locale);

  const [name, setName] = useState(user?.name || "");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const saveName = async () => {
    if (!name.trim()) return;
    setSaving(true);
    setSaved(false);
    try {
      const res = await apiRequest<{ user: any }>("/account", { method: "PATCH", body: { name: name.trim() } });
      setUser(res.user);
      setSaved(true);
    } catch {} finally {
      setSaving(false);
    }
  };

  return (
    <View style={styles.root}>
      <View style={[styles.topBar, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="doc-back" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.topTitle} numberOfLines={1}>{doc.title}</Text>
        <View style={{ width: 26 }} />
      </View>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <ScrollView
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xxl }}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.intro}>{doc.intro}</Text>
          {doc.sections.map((s) => (
            <View key={s.heading} style={styles.section}>
              <Text style={styles.heading}>{s.heading}</Text>
              <Text style={styles.body}>{s.body}</Text>
            </View>
          ))}

          {docType === "correct" && (
            <View style={styles.editBox}>
              <TextInput
                testID="correct-name-input"
                value={name}
                onChangeText={(v) => { setName(v); setSaved(false); }}
                placeholder={t("correct.namePlaceholder")}
                placeholderTextColor={colors.muted}
                style={styles.input}
                autoCapitalize="words"
              />
              <Pressable testID="correct-save" onPress={saveName} disabled={saving} style={styles.saveBtn}>
                <Text style={styles.saveText}>{saved ? t("correct.saved") : t("correct.save")}</Text>
              </Pressable>
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  topBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.lg, paddingBottom: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border },
  topTitle: { flex: 1, textAlign: "center", fontFamily: fonts.display, fontSize: 19, color: colors.onSurface },
  intro: { fontFamily: fonts.body, fontSize: 14, color: colors.onSurfaceSecondary, lineHeight: 22, marginBottom: spacing.lg },
  section: { marginBottom: spacing.lg },
  heading: { fontFamily: fonts.bodySemi, fontSize: 16, color: colors.brand, marginBottom: spacing.xs },
  body: { fontFamily: fonts.body, fontSize: 14, color: colors.onSurfaceSecondary, lineHeight: 22 },
  editBox: { marginTop: spacing.sm, gap: spacing.md },
  input: { backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, paddingHorizontal: spacing.md, paddingVertical: spacing.md, fontFamily: fonts.bodyMed, fontSize: 16, color: colors.onSurface },
  saveBtn: { backgroundColor: colors.brand, borderRadius: radius.md, paddingVertical: spacing.md, alignItems: "center" },
  saveText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onBrand },
});
