import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, Modal, ActivityIndicator, Alert, Linking, Platform } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

const CONTACT = "privacy@qapilo.app";

// Cross-platform confirm: RN Alert on native, window.confirm on web (Alert with
// multiple buttons is a no-op on react-native-web).
function confirmAction(title: string, message: string, confirmLabel: string, cancelLabel: string, onConfirm: () => void) {
  if (Platform.OS === "web") {
    if (typeof window !== "undefined" && window.confirm(`${title}\n\n${message}`)) onConfirm();
    return;
  }
  Alert.alert(title, message, [
    { text: cancelLabel, style: "cancel" },
    { text: confirmLabel, style: "destructive", onPress: onConfirm },
  ]);
}

function Row({ icon, label, onPress, testID, danger, right, loading }: any) {
  return (
    <Pressable testID={testID} onPress={onPress} style={styles.row}>
      <Ionicons name={icon} size={20} color={danger ? colors.error : colors.onSurfaceSecondary} />
      <Text style={[styles.rowText, danger && { color: colors.error }]}>{label}</Text>
      {loading ? <ActivityIndicator size="small" color={colors.muted} /> : (right ?? <Ionicons name="chevron-forward" size={18} color={colors.muted} />)}
    </Pressable>
  );
}

export default function SettingsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { logout } = useAuth();
  const { t, openPicker } = useI18n();
  const [exporting, setExporting] = useState(false);
  const [exportText, setExportText] = useState("");

  const goDoc = (type: string) => router.push(`/doc?type=${type}` as any);

  const exportData = async () => {
    setExporting(true);
    try {
      const data = await apiRequest<any>("/account/export");
      setExportText(JSON.stringify(data, null, 2));
    } catch {
      Alert.alert(t("common.error"), t("profile.exportError"));
    } finally {
      setExporting(false);
    }
  };

  const clearChat = () => {
    confirmAction(
      t("profile.clearChatTitle"), t("profile.clearChatMsg"),
      t("profile.clearChatConfirm"), t("common.cancel"),
      async () => {
        try {
          await apiRequest("/tutor/history", { method: "DELETE" });
        } catch {
          Alert.alert(t("common.error"), t("profile.clearChatError"));
        }
      }
    );
  };

  const confirmDelete = () => {
    confirmAction(
      t("profile.deleteTitle"), t("profile.deleteMsg"),
      t("profile.deleteConfirm"), t("common.cancel"),
      async () => {
        try {
          await apiRequest("/account", { method: "DELETE" });
          await logout();
          router.replace("/auth");
        } catch {
          Alert.alert(t("common.error"), t("profile.deleteError"));
        }
      }
    );
  };

  const doLogout = async () => {
    await logout();
    router.replace("/auth");
  };

  return (
    <View style={styles.root}>
      <View style={[styles.topBar, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="settings-back" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.topTitle}>{t("settings.title")}</Text>
        <View style={{ width: 26 }} />
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: insets.bottom + spacing.xxl }} showsVerticalScrollIndicator={false}>
        <Text style={styles.groupLabel}>{t("settings.privacyData")}</Text>
        <View style={styles.card}>
          <Row testID="row-privacy" icon="shield-checkmark-outline" label={t("profile.privacy")} onPress={() => router.push("/privacy")} />
          <Row testID="row-terms" icon="reader-outline" label={t("profile.terms")} onPress={() => goDoc("terms")} />
          <Row testID="row-disclaimer" icon="document-text-outline" label={t("profile.financialDisclaimer")} onPress={() => router.push("/disclaimer")} />
          <Row testID="row-ai" icon="sparkles-outline" label={t("profile.aiTransparency")} onPress={() => goDoc("ai")} />
          <Row testID="row-market" icon="trending-up-outline" label={t("profile.marketData")} onPress={() => goDoc("market")} />
          <Row testID="row-export" icon="download-outline" label={t("profile.exportData")} onPress={exportData} loading={exporting} />
          <Row testID="row-correct" icon="create-outline" label={t("profile.correctData")} onPress={() => goDoc("correct")} />
          <Row testID="row-clear-chat" icon="trash-bin-outline" label={t("profile.clearChat")} onPress={clearChat} />
          <Row testID="row-contact" icon="mail-outline" label={t("profile.privacyContact")} onPress={() => Linking.openURL(`mailto:${CONTACT}`)} right={<Text style={styles.contactEmail}>{CONTACT}</Text>} />
          <Row testID="row-delete" icon="close-circle-outline" label={t("profile.deleteAccount")} onPress={confirmDelete} danger right={<View />} />
        </View>

        <Text style={styles.groupLabel}>{t("settings.preferences")}</Text>
        <View style={styles.card}>
          <Row testID="row-language" icon="language-outline" label={t("profile.language")} onPress={openPicker} />
          <Row testID="row-logout" icon="log-out-outline" label={t("profile.logout")} onPress={doLogout} right={<View />} />
        </View>
      </ScrollView>

      <Modal visible={!!exportText} transparent animationType="slide" onRequestClose={() => setExportText("")}>
        <View style={styles.modalBackdrop}>
          <View style={[styles.modalCard, { paddingBottom: insets.bottom + spacing.lg }]}>
            <Text style={styles.modalTitle}>{t("profile.exportData")}</Text>
            <Text style={styles.modalMsg}>{t("profile.exportDone")}</Text>
            <ScrollView style={styles.exportBox} nestedScrollEnabled>
              <Text selectable style={styles.exportText}>{exportText}</Text>
            </ScrollView>
            <Pressable testID="export-close" onPress={() => setExportText("")} style={styles.modalPrimary}>
              <Text style={styles.modalPrimaryText}>{t("profile.close")}</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  topBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.lg, paddingBottom: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border },
  topTitle: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  groupLabel: { fontFamily: fonts.displayMed, fontSize: 12, color: colors.muted, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: spacing.sm, marginTop: spacing.lg },
  card: { backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, paddingHorizontal: spacing.md },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.md, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: colors.border, minHeight: 52 },
  rowText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 15, color: colors.onSurface },
  contactEmail: { fontFamily: fonts.body, fontSize: 12, color: colors.muted },
  modalBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.6)", justifyContent: "flex-end" },
  modalCard: { backgroundColor: colors.surfaceSecondary, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "80%" },
  modalTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface, marginBottom: spacing.xs },
  modalMsg: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginBottom: spacing.md },
  exportBox: { backgroundColor: colors.surface, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md, marginBottom: spacing.md },
  exportText: { fontFamily: "monospace", fontSize: 11, color: colors.onSurfaceSecondary },
  modalPrimary: { backgroundColor: colors.brand, borderRadius: radius.md, paddingVertical: spacing.md, alignItems: "center" },
  modalPrimaryText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onBrand },
});
