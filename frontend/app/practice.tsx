import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton, Loading } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

type PQuestion = { q: string; options: string[]; answer: number; explain: string; tier: number };
type Session = { questions: PQuestion[]; reward_xp: number; tier: number; practice_level: number };
type Result = { earned_xp: number; perfect: boolean; new_badges: any[]; user: any };

export default function PracticeScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { setUser } = useAuth();
  const { t, locale } = useI18n();

  const [session, setSession] = useState<Session | null>(null);
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [result, setResult] = useState<Result | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const loadSession = async () => {
    setSession(null);
    setStep(0);
    setSelected(null);
    setChecked(false);
    setCorrect(0);
    setResult(null);
    try {
      const data = await apiRequest<Session>("/practice");
      setSession(data);
    } catch {
      router.back();
    }
  };

  useEffect(() => {
    loadSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locale]);

  if (!session) return <Loading testID="practice-loading" />;

  if (session.questions.length === 0) {
    return (
      <View style={[styles.root, { paddingTop: insets.top + spacing.xxxl, alignItems: "center" }]}>
        <Text style={styles.emptyText}>{t("practice.empty")}</Text>
        <PrimaryButton testID="practice-back" label={t("practice.back")} onPress={() => router.back()} style={{ marginTop: spacing.lg }} />
      </View>
    );
  }

  const question = session.questions[step];
  const progress = (step / session.questions.length) * 100;

  const submit = async (finalCorrect: number) => {
    setSubmitting(true);
    try {
      const res = await apiRequest<Result>("/practice/complete", {
        method: "POST",
        body: { correct: finalCorrect, total: session.questions.length, tier: session.tier },
      });
      setUser(res.user);
      setResult(res);
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
    if (step + 1 >= session.questions.length) {
      await submit(finalCorrect);
    } else {
      setStep(step + 1);
    }
  };

  if (result) {
    return (
      <View style={[styles.root, { paddingTop: insets.top }]}>
        <ScrollView contentContainerStyle={styles.resultScroll}>
          <MaterialCommunityIcons
            name={result.perfect ? "star-circle" : "check-circle"}
            size={90}
            color={result.perfect ? colors.amber : colors.brand}
          />
          <Text style={styles.resultTitle}>{t("practice.done")}</Text>
          <Text style={styles.resultSub}>
            {t("practice.gotCorrect")} {correct}/{session.questions.length}
          </Text>
          <View style={styles.rewardCard}>
            <MaterialCommunityIcons name="flash" size={26} color={colors.brand} />
            <Text style={styles.rewardValue}>+{result.earned_xp}</Text>
            <Text style={styles.rewardLabel}>XP</Text>
          </View>
        </ScrollView>
        <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
          <PrimaryButton testID="practice-again" label={t("practice.again")} onPress={loadSession} />
          <Pressable testID="practice-back" onPress={() => router.back()} style={styles.backLink}>
            <Text style={styles.backLinkText}>{t("practice.back")}</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.sm }]}>
      <View style={styles.topBar}>
        <Pressable testID="practice-close" onPress={() => router.back()} hitSlop={12}>
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
          {t("practice.q")} {step + 1} {t("practice.of")} {session.questions.length}
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
                testID={`practice-option-${i}`}
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
          testID="practice-action-button"
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
  resultSub: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, marginTop: spacing.xs, marginBottom: spacing.xl },
  rewardCard: { alignItems: "center", backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, paddingVertical: spacing.xl, paddingHorizontal: spacing.xxxl, gap: 4 },
  rewardValue: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface },
  rewardLabel: { fontFamily: fonts.displayMed, fontSize: 11, color: colors.muted, letterSpacing: 1 },
  backLink: { alignItems: "center", paddingVertical: spacing.md, marginTop: spacing.xs },
  backLinkText: { fontFamily: fonts.bodySemi, fontSize: 14, color: colors.muted },
  emptyText: { fontFamily: fonts.body, fontSize: 15, color: colors.muted },
});
