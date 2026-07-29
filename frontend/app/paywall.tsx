import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as WebBrowser from "expo-web-browser";
import * as Linking from "expo-linking";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton, Loading } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

const BACKEND = process.env.EXPO_PUBLIC_BACKEND_URL;

type Plan = {
  price: string;
  currency: string;
  trial_days: number;
  paypal_configured: boolean;
  features: string[];
  is_pro: boolean;
  pro_source: string;
  in_trial: boolean;
  trial_days_left: number;
};

export default function Paywall() {
  const { refresh, setUser } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();
  const [plan, setPlan] = useState<Plan | null>(null);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  const load = useCallback(async () => {
    try {
      const p = await apiRequest<Plan>("/pro/plan");
      setPlan(p);
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const subscribe = async () => {
    setNote("");
    setBusy(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const res = await apiRequest<{ subscription_id: string; approval_url: string }>(
        "/subscription/create",
        { method: "POST", body: { return_base: BACKEND } }
      );
      const returnUrl = `${BACKEND}/api/subscription/return`;
      const result = await WebBrowser.openAuthSessionAsync(res.approval_url, returnUrl);

      let subId: string | null = res.subscription_id;
      if (result.type === "success" && result.url) {
        const parsed = Linking.parse(result.url);
        subId = (parsed.queryParams?.subscription_id as string) || subId;
      }
      // Verify + activate
      const act = await apiRequest<{ activated: boolean; user: any }>("/subscription/activate", {
        method: "POST",
        body: { subscription_id: subId },
      });
      if (act.activated) {
        setUser(act.user);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        router.back();
      } else {
        await refresh();
        setNote("Subscription not active yet. If you just approved it, pull to refresh in a moment.");
        await load();
      }
    } catch (e: any) {
      setNote(e.message || t("paywall.subError"));
    } finally {
      setBusy(false);
    }
  };

  const restore = async () => {
    setBusy(true);
    setNote("");
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    try {
      const res = await apiRequest<{ user: any }>("/subscription/status");
      setUser(res.user);
      await load();
      setNote(
        res.user.is_pro
          ? "Subscription restored — Pro is active!"
          : "No active subscription found yet. If you just paid, wait a moment and try again."
      );
    } catch (e: any) {
      setNote(e.message || t("paywall.refreshError"));
    } finally {
      setBusy(false);
    }
  };

  const manageCancel = async () => {    setBusy(true);
    try {
      const res = await apiRequest<{ user: any }>("/subscription/cancel", { method: "POST" });
      setUser(res.user);
      await load();
      setNote("Your subscription has been cancelled.");
    } catch (e: any) {
      setNote(e.message || t("paywall.cancelError"));
    } finally {
      setBusy(false);
    }
  };

  if (!plan) return <Loading testID="paywall-loading" />;

  const alreadyPro = plan.is_pro;
  const isSubscriber = plan.pro_source === "subscription";

  return (
    <View style={styles.root}>
      <LinearGradient colors={["#1A1405", colors.surface, colors.surface]} style={StyleSheet.absoluteFill} />
      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingTop: insets.top + spacing.lg, paddingBottom: spacing.xxxl }}>
        <Pressable testID="paywall-close" onPress={() => router.back()} style={styles.close} hitSlop={12}>
          <Ionicons name="close" size={26} color={colors.muted} />
        </Pressable>

        <View style={styles.crown}>
          <MaterialCommunityIcons name="crown" size={40} color={colors.onAmber} />
        </View>
        <Text style={styles.title}>{t("paywall.title")}</Text>
        <Text style={styles.subtitle}>{t("paywall.subtitle")}</Text>

        {plan.in_trial && (
          <View testID="trial-banner" style={styles.trialBanner}>
            <MaterialCommunityIcons name="gift" size={18} color={colors.brand} />
            <Text style={styles.trialText}>
              {t("paywall.trialLeft")} {plan.trial_days_left}{" "}
              {plan.trial_days_left === 1 ? t("learn.day") : t("learn.days")} {t("paywall.left")}
            </Text>
          </View>
        )}

        <View style={styles.card}>
          {plan.features.map((f) => (
            <View key={f} style={styles.featureRow}>
              <View style={styles.checkCircle}>
                <Ionicons name="checkmark" size={15} color={colors.onBrand} />
              </View>
              <Text style={styles.featureText}>{f}</Text>
            </View>
          ))}
        </View>

        <View style={styles.priceRow}>
          <Text style={styles.price}>${plan.price}</Text>
          <Text style={styles.per}>{t("paywall.perMonth")}</Text>
        </View>
        <Text style={styles.trialNote}>
          {plan.trial_days}-{t("paywall.trialNote")}
        </Text>

        {note ? <Text style={styles.note} testID="paywall-note">{note}</Text> : null}

        {alreadyPro ? (
          <View>
            <View style={styles.activeBadge} testID="pro-active-badge">
              <MaterialCommunityIcons name="check-decagram" size={20} color={colors.brand} />
              <Text style={styles.activeText}>
                {isSubscriber ? t("paywall.subscriber") : t("paywall.trialUnlocked")}
              </Text>
            </View>
            {isSubscriber && (
              <Pressable testID="cancel-sub-button" onPress={manageCancel} disabled={busy} style={styles.cancelBtn}>
                <Text style={styles.cancelText}>{busy ? "…" : t("paywall.cancel")}</Text>
              </Pressable>
            )}
          </View>
        ) : plan.paypal_configured ? (
          <PrimaryButton
            testID="subscribe-button"
            label={t("paywall.subscribe")}
            variant="amber"
            loading={busy}
            onPress={subscribe}
          />
        ) : (
          <View style={styles.soon} testID="payments-not-configured">
            <Ionicons name="time-outline" size={18} color={colors.muted} />
            <Text style={styles.soonText}>{t("paywall.notConfigured")}</Text>
          </View>
        )}

        <Pressable testID="restore-sub-button" onPress={restore} disabled={busy} style={styles.restore}>
          <Ionicons name="refresh" size={16} color={colors.onSurfaceSecondary} />
          <Text style={styles.restoreText}>{t("paywall.restore")}</Text>
        </Pressable>

        <Text style={styles.legal}>{t("paywall.legal")}</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  close: { alignSelf: "flex-end", marginBottom: spacing.sm },
  crown: {
    width: 76,
    height: 76,
    borderRadius: radius.lg,
    backgroundColor: colors.amber,
    alignItems: "center",
    justifyContent: "center",
    alignSelf: "center",
    marginBottom: spacing.lg,
  },
  title: { fontFamily: fonts.display, fontSize: 36, color: colors.onSurface, textAlign: "center" },
  subtitle: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, textAlign: "center", marginTop: 4 },
  trialBanner: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    backgroundColor: "#0C2E22",
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.xl,
  },
  trialText: { fontFamily: fonts.bodySemi, fontSize: 13, color: colors.brand },
  card: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    padding: spacing.lg,
    marginTop: spacing.xl,
    gap: spacing.md,
  },
  featureRow: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  checkCircle: {
    width: 26,
    height: 26,
    borderRadius: radius.pill,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  featureText: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 15, color: colors.onSurface },
  priceRow: { flexDirection: "row", alignItems: "flex-end", justifyContent: "center", marginTop: spacing.xl },
  price: { fontFamily: fonts.display, fontSize: 48, color: colors.onSurface },
  per: { fontFamily: fonts.body, fontSize: 16, color: colors.muted, marginBottom: 8, marginLeft: 4 },
  trialNote: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, textAlign: "center", marginBottom: spacing.xl },
  note: { fontFamily: fonts.bodyMed, fontSize: 13, color: colors.amber, textAlign: "center", marginBottom: spacing.md },
  activeBadge: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    backgroundColor: "#0C2E22",
    borderRadius: radius.md,
    padding: spacing.lg,
  },
  activeText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.brand },
  cancelBtn: { alignItems: "center", marginTop: spacing.lg, padding: spacing.md },
  cancelText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.error },
  soon: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  soonText: { flex: 1, fontFamily: fonts.body, fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 19 },
  legal: { fontFamily: fonts.body, fontSize: 11, color: colors.muted, textAlign: "center", marginTop: spacing.xl, lineHeight: 16 },
  restore: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    marginTop: spacing.xl,
    paddingVertical: spacing.md,
  },
  restoreText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurfaceSecondary },
});
