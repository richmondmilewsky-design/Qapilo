import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, Modal, ActivityIndicator, Alert, Linking, Platform, Switch, TextInput } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import HomeLogo from "@/src/components/HomeLogo";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

const CONTACT = "privacy@qapilo.de";

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

function ConsentRow({ label, desc, value, onToggle, loading, testID, last }: any) {
  return (
    <View style={[styles.consentRow, last && { borderBottomWidth: 0 }]}>
      <View style={{ flex: 1, paddingRight: spacing.md }}>
        <Text style={styles.consentLabel}>{label}</Text>
        <Text style={styles.consentDesc}>{desc}</Text>
      </View>
      {loading ? (
        <ActivityIndicator size="small" color={colors.muted} />
      ) : (
        <Switch
          testID={testID}
          value={value}
          onValueChange={onToggle}
          trackColor={{ false: colors.borderStrong, true: colors.brand }}
          thumbColor={colors.onBrand}
        />
      )}
    </View>
  );
}

export default function SettingsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { logout, user, setUser } = useAuth();
  const { t, openPicker, locale } = useI18n();
  const [exporting, setExporting] = useState(false);
  const [exportText, setExportText] = useState("");
  const [savingConsent, setSavingConsent] = useState<string | null>(null);
  const [marketingPending, setMarketingPending] = useState(false);
  const [marketingCode, setMarketingCode] = useState("");
  const [marketingBusy, setMarketingBusy] = useState(false);
  const [marketingResendBusy, setMarketingResendBusy] = useState(false);
  const [marketingErr, setMarketingErr] = useState("");
  const [marketingMsg, setMarketingMsg] = useState("");

  const consents = {
    analytics: !!user?.consent_analytics,
    product: !!user?.consent_product,
    marketing: !!user?.consent_marketing,
  };

  const toggleConsent = async (key: "analytics" | "product" | "marketing", value: boolean) => {
    const next = { ...consents, [key]: value };
    setSavingConsent(key);
    if (key === "marketing") { setMarketingErr(""); setMarketingMsg(""); }
    try {
      const res = await apiRequest<{ user: any }>("/auth/consents", {
        method: "PATCH",
        body: {
          consent_analytics: next.analytics,
          consent_product: next.product,
          consent_marketing: next.marketing,
        },
      });
      setUser(res.user);
      if (key === "marketing") {
        if (value && res.user?.consent_marketing_pending) {
          setMarketingPending(true);
          setMarketingCode("");
        } else {
          setMarketingPending(false);
        }
      }
    } catch {
      Alert.alert(t("common.error"), t("consent.error"));
    } finally {
      setSavingConsent(null);
    }
  };

  const confirmMarketing = async () => {
    if (marketingCode.trim().length < 6) return;
    setMarketingErr(""); setMarketingMsg("");
    setMarketingBusy(true);
    try {
      const res = await apiRequest<{ user: any }>("/auth/confirm-marketing-consent", {
        method: "POST",
        body: { code: marketingCode.trim(), lang: locale },
      });
      setUser(res.user);
      setMarketingPending(false);
      setMarketingCode("");
      setMarketingMsg(t("consent.marketingConfirmedMsg"));
    } catch (e: any) {
      setMarketingErr(e.message || t("consent.marketingConfirmError"));
    } finally {
      setMarketingBusy(false);
    }
  };

  const resendMarketing = async () => {
    setMarketingErr(""); setMarketingMsg("");
    setMarketingResendBusy(true);
    try {
      await apiRequest("/auth/resend-marketing-code", { method: "POST", body: { lang: locale } });
      setMarketingMsg(t("verify.resent"));
    } catch (e: any) {
      setMarketingErr(e.message || t("common.somethingWrong"));
    } finally {
      setMarketingResendBusy(false);
    }
  };

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
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
          <HomeLogo size={26} />
          <Pressable testID="settings-back" onPress={() => router.back()} hitSlop={12}>
            <Ionicons name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
        </View>
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

        <Text style={styles.groupLabel}>{t("settings.consents")}</Text>
        <Text style={styles.consentSubtitle}>{t("consent.subtitle")}</Text>
        <View style={styles.card}>
          <ConsentRow testID="consent-analytics" label={t("agree.optAnalytics")} desc={t("agree.optAnalyticsDesc")} value={consents.analytics} loading={savingConsent === "analytics"} onToggle={(v: boolean) => toggleConsent("analytics", v)} />
          <ConsentRow testID="consent-product" label={t("agree.optProduct")} desc={t("agree.optProductDesc")} value={consents.product} loading={savingConsent === "product"} onToggle={(v: boolean) => toggleConsent("product", v)} />
          <ConsentRow testID="consent-marketing" label={t("agree.optMarketing")} desc={t("agree.optMarketingDesc")} value={consents.marketing || marketingPending} loading={savingConsent === "marketing"} onToggle={(v: boolean) => toggleConsent("marketing", v)} last />
        </View>
        {marketingPending && (
          <View style={styles.marketingPendingBox} testID="marketing-pending-box">
            <Text style={styles.marketingPendingTitle}>{t("consent.marketingPendingTitle")}</Text>
            <Text style={styles.marketingPendingMsg}>{t("consent.marketingPendingMsg")}</Text>
            <TextInput
              testID="marketing-code-input"
              value={marketingCode}
              onChangeText={(v) => setMarketingCode(v.replace(/[^0-9]/g, ""))}
              keyboardType="number-pad"
              maxLength={6}
              placeholder={t("consent.marketingCodePlaceholder")}
              placeholderTextColor={colors.muted}
              style={styles.marketingInput}
            />
            {marketingErr ? <Text style={styles.marketingErr}>{marketingErr}</Text> : null}
            {marketingMsg ? <Text style={styles.marketingMsg}>{marketingMsg}</Text> : null}
            <Pressable testID="marketing-confirm" onPress={confirmMarketing} style={styles.marketingBtn}>
              {marketingBusy ? <ActivityIndicator size="small" color={colors.onBrand} /> : <Text style={styles.marketingBtnText}>{t("consent.marketingConfirmBtn")}</Text>}
            </Pressable>
            <Pressable testID="marketing-resend" onPress={resendMarketing} style={{ alignSelf: "center", marginTop: spacing.sm }}>
              <Text style={styles.marketingResend}>{marketingResendBusy ? "…" : t("consent.marketingResendBtn")}</Text>
            </Pressable>
          </View>
        )}
        <Text style={styles.consentNote}>{t("consent.reqNote")}</Text>

        <Text style={styles.groupLabel}>{t("settings.preferences")}</Text>
        <View style={styles.card}>
          <Row testID="row-language" icon="language-outline" label={t("profile.language")} onPress={openPicker} />
          <Row testID="row-support" icon="help-buoy-outline" label={t("settings.support")} onPress={() => router.push("/support")} />
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
  consentSubtitle: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginBottom: spacing.sm, marginTop: -spacing.xs, lineHeight: 17 },
  consentRow: { flexDirection: "row", alignItems: "center", paddingVertical: spacing.md, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: colors.border, minHeight: 52 },
  consentLabel: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface },
  consentDesc: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: 2, lineHeight: 17 },
  consentNote: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, marginTop: spacing.sm, lineHeight: 17 },
  marketingPendingBox: { backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, padding: spacing.md, marginTop: spacing.sm },
  marketingPendingTitle: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.onSurface, marginBottom: 4 },
  marketingPendingMsg: { fontFamily: fonts.body, fontSize: 12, color: colors.muted, lineHeight: 17, marginBottom: spacing.sm },
  marketingInput: { backgroundColor: colors.surface, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, paddingHorizontal: spacing.md, height: 48, fontFamily: fonts.bodySemi, fontSize: 18, letterSpacing: 4, textAlign: "center", color: colors.onSurface },
  marketingErr: { fontFamily: fonts.bodyMed, fontSize: 12, color: colors.error, marginTop: spacing.sm },
  marketingMsg: { fontFamily: fonts.bodyMed, fontSize: 12, color: colors.brand, marginTop: spacing.sm },
  marketingBtn: { backgroundColor: colors.brand, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center", marginTop: spacing.sm, minHeight: 44, justifyContent: "center" },
  marketingBtnText: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.onBrand },
  marketingResend: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.brand, textAlign: "center" },
  contactEmail: { fontFamily: fonts.body, fontSize: 12, color: colors.muted },
  modalBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.75)", justifyContent: "flex-end" },
  modalCard: { backgroundColor: colors.elevated, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "80%" },
  modalTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface, marginBottom: spacing.xs },
  modalMsg: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginBottom: spacing.md },
  exportBox: { backgroundColor: colors.surface, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md, marginBottom: spacing.md },
  exportText: { fontFamily: "monospace", fontSize: 11, color: colors.onSurfaceSecondary },
  modalPrimary: { backgroundColor: colors.brand, borderRadius: radius.md, paddingVertical: spacing.md, alignItems: "center" },
  modalPrimaryText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onBrand },
});
