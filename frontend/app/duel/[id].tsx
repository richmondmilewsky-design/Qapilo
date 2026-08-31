import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, Share } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton, Loading } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

type DuelQuestion = { q: string; options: string[]; answer: number; explain: string; tier: number };
type DuelResult = { correct: number; total: number; completed_at: string };
type Duel = {
  duel_id: string;
  questions: DuelQuestion[];
  creator_user_id: string;
  creator_result: DuelResult | null;
  opponent_user_id: string | null;
  opponent_result: DuelResult | null;
};

export default function DuelScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const { user } = useAuth();
  const { t, locale } = useI18n();

  const [duel, setDuel] = useState<Duel | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  const loadDuel = async () => {
    setDuel(null);
    setNotFound(false);
    setStep(0);
    setSelected(null);
    setChecked(false);
    setCorrect(0);
    try {
      const data = await apiRequest<Duel>(`/duels/${id}`);
      setDuel(data);
    } catch {
      setNotFound(true);
    }
  };

  useEffect(() => {
    loadDuel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, locale]);

  if (notFound) {
    return (
      <View style={[styles.root, { paddingTop: insets.top + spacing.xxxl, alignItems: "center" }]}>
        <MaterialCommunityIcons name="sword-cross" size={56} color={colors.muted} />
        <Text style={styles.emptyText}>{t("duel.notFound")}</Text>
        <PrimaryButton testID="duel-back-error" label={t("practice.back")} onPress={() => router.back()} style={{ marginTop: spacing.lg }} />
      </View>
    );
  }

  if (!duel) return <Loading testID="duel-loading" />;

  const isCreator = user?.user_id === duel.creator_user_id;
  const myResult = isCreator ? duel.creator_result : duel.opponent_result;
  const otherResult = isCreator ? duel.opponent_result : duel.creator_result;
  const hasPlayed = !!myResult;

  const onShare = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    try {
      await Share.share({ message: `${t("duel.shareMessage")}${duel.duel_id}` });
    } catch {}
  };

  if (hasPlayed) {
    return (
      <View style={[styles.root, { paddingTop: insets.top }]}>
        <ScrollView contentContainerStyle={styles.resultScroll}>
          <MaterialCommunityIcons name="sword-cross" size={80} color={colors.brand} />
          <Text style={styles.resultTitle}>{t("duel.resultsTitle")}</Text>
          <View style={styles.duelScoreRow}>
            <View style={styles.duelScoreCard} testID="duel-score-you">
              <Text style={styles.duelScoreLabel}>{t("duel.you")}</Text>
              <Text style={styles.duelScoreValue}>{myResult!.correct}/{myResult!.total}</Text>
            </View>
            <View style={styles.duelScoreCard} testID="duel-score-friend">
              <Text style={styles.duelScoreLabel}>{t("duel.friend")}</Text>
              {otherResult ? (
                <Text style={styles.duelScoreValue}>{otherResult.correct}/{otherResult.total}</Text>
              ) : (
                <Text style={styles.duelScoreValue}>—</Text>
              )}
            </View>
          </View>
          {!otherResult && (
            <>
              <Text style={styles.duelWaitingText}>{t("duel.waiting")}</Text>
              <Pressable testID="duel-share" onPress={onShare} style={styles.duelShareBtn}>
                <Ionicons name="share-outline" size={18} color={colors.onBrand} />
                <Text style={styles.duelShareText}>{t("duel.share")}</Text>
              </Pressable>
            </>
          )}
        </ScrollView>
        <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
          <Pressable testID="duel-back" onPress={() => router.back()} style={styles.backLink}>
            <Text style={styles.backLinkText}>{t("practice.back")}</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  const question = duel.questions[step];
  const progress = (step / duel.questions.length) * 100;

  const submit = async (finalCorrect: number) => {
    setSubmitting(true);
    try {
      const res = await apiRequest<{
        duel_id: string;
        creator_user_id: string;
        creator_result: DuelResult | null;
        opponent_user_id: string | null;
        opponent_result: DuelResult | null;
      }>(`/duels/${id}/complete`, {
        method: "POST",
        body: { correct: finalCorrect, total: duel.questions.length },
      });
      setDuel((d) => (d ? {
        ...d,
        creator_result: res.creator_result,
        opponent_user_id: res.opponent_user_id,
        opponent_result: res.opponent_result,
      } : d));
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {} finally {
      setSubmitting(false);
    }
  };

  const next = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    if (!checked) {
      if (selected === null) return;
      const isCorrect = selected === question.answer;
      setChecked(true);
      if (isCorrect) {
        setCorrect((c) => c + 1);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
      return;
    }
    const finalCorrect = correct;
    setChecked(false);
    setSelected(null);
    if (step + 1 >= duel.questions.length) {
      await submit(finalCorrect);
    } else {
      setStep(step + 1);
    }
  };

  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.sm }]}>
      <View style={styles.topBar}>
        <Pressable testID="duel-close" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="close" size={28} color={colors.muted} />
        </Pressable>
        <View style={styles.progressBg}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <View style={styles.tierTag}>
          <Text style={styles.tierTagText}>{t(`tier.${question.tier}` as any)}</Text>
        </View>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.body} showsVerticalScrollIndicator={false}>
        <Text style={styles.tag}>
          {t("practice.q")} {step + 1} {t("practice.of")} {duel.questions.length}
        </Text>
        <Text style={styles.question}>{question.q}</Text>
        <View style={{ gap: spacing.md, marginTop: spacing.lg }}>
          {question.options.map((opt, i) => {
            const isSel = selected === i;
            const isAnswer = i === question.answer;
            let border = colors.border;
            let bg = colors.surfaceSecondary;
            if (checked) {
              if (isAnswer) { border = colors.brand; bg = "#0C2E22"; }
              else if (isSel) { border = colors.error; bg = "#2E0C0C"; }
            } else if (isSel) { border = colors.brand; }
            return (
              <Pressable
                key={i}
                testID={`duel-option-${i}`}
                disabled={checked}
                onPress={() => { Haptics.selectionAsync(); setSelected(i); }}
                style={[styles.option, { borderColor: border, backgroundColor: bg }]}
              >
                <Text style={styles.optionText}>{opt}</Text>
                {checked && isAnswer && <Ionicons name="checkmark-circle" size={22} color={colors.brand} />}
                {checked && isSel && !isAnswer && <Ionicons name="close-circle" size={22} color={colors.error} />}
              </Pressable>
            );
          })}
        </View>
        {checked && (
          <View style={[styles.explainBox, { borderColor: selected === question.answer ? colors.brand : colors.error }]}>
            <Text style={styles.explainTitle}>
              {selected === question.answer ? t("practice.correct") : t("practice.notQuite")}
            </Text>
            <Text style={styles.explainText}>{question.explain}</Text>
          </View>
        )}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <PrimaryButton
          testID="duel-action-button"
          label={checked ? t("practice.continue") : t("practice.check")}
          onPress={next}
          loading={submitting}
          disabled={!checked && selected === null}
          variant={checked && selected !== question.answer ? "amber" : "brand"}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  topBar: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md },
  progressBg: { flex: 1, height: 12, borderRadius: radius.pill, backgroundColor: colors.surfaceTertiary, overflow: "hidden" },
  progressFill: { height: "100%", backgroundColor: colors.brand, borderRadius: radius.pill },
  tierTag: { backgroundColor: colors.surfaceSecondary, paddingHorizontal: spacing.md, paddingVertical: 4, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border },
  tierTagText: { fontFamily: fonts.bodySemi, fontSize: 11, color: colors.amber, letterSpacing: 0.5 },
  body: { padding: spacing.xl, paddingBottom: spacing.xxxl },
  tag: { fontFamily: fonts.displayMed, fontSize: 13, color: colors.muted, letterSpacing: 1.5, marginBottom: spacing.md },
  question: { fontFamily: fonts.display, fontSize: 26, color: colors.onSurface, lineHeight: 30 },
  option: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: spacing.lg, borderRadius: radius.md, borderWidth: 2, minHeight: 58 },
  optionText: { fontFamily: fonts.bodyMed, fontSize: 16, color: colors.onSurface, flex: 1, paddingRight: spacing.sm },
  explainBox: { marginTop: spacing.xl, padding: spacing.lg, borderRadius: radius.md, borderWidth: 1, backgroundColor: colors.surfaceSecondary },
  explainTitle: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface, marginBottom: 4 },
  explainText: { fontFamily: fonts.body, fontSize: 14, color: colors.onSurfaceSecondary, lineHeight: 21 },
  footer: { paddingHorizontal: spacing.lg, paddingTop: spacing.md, borderTopWidth: 1, borderTopColor: colors.border, backgroundColor: colors.surface },
  resultScroll: { padding: spacing.xl, alignItems: "center", paddingTop: spacing.xxxl },
  resultTitle: { fontFamily: fonts.display, fontSize: 34, color: colors.onSurface, marginTop: spacing.lg },
  backLink: { alignItems: "center", paddingVertical: spacing.md, marginTop: spacing.xs },
  backLinkText: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.muted },
  emptyText: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, textAlign: "center", marginTop: spacing.lg },
  duelScoreRow: { flexDirection: "row", gap: spacing.md, marginTop: spacing.xl, width: "100%" },
  duelScoreCard: { flex: 1, alignItems: "center", backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, paddingVertical: spacing.xl, gap: 4 },
  duelScoreLabel: { fontFamily: fonts.displayMed, fontSize: 11, color: colors.muted, letterSpacing: 1 },
  duelScoreValue: { fontFamily: fonts.display, fontSize: 26, color: colors.onSurface },
  duelWaitingText: { fontFamily: fonts.body, fontSize: 13, color: colors.muted, marginTop: spacing.lg, textAlign: "center" },
  duelShareBtn: { flexDirection: "row", alignItems: "center", gap: spacing.sm, backgroundColor: colors.brand, borderRadius: radius.pill, paddingVertical: spacing.md, paddingHorizontal: spacing.xl, marginTop: spacing.lg },
  duelShareText: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onBrand },
});
