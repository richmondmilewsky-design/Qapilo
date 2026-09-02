import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useAuth, User } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { PrimaryButton, Loading } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

type PQuestion = { q: string; options: string[]; answer: number; explain: string; tier: number };
type QuizResponse = { questions: PQuestion[] };
type CompleteResponse = { user: User };

export default function PlacementQuizScreen() {
  const router = useRouter();
  const { experience } = useLocalSearchParams<{ experience?: string }>();
  const insets = useSafeAreaInsets();
  const { setUser } = useAuth();
  const { t, locale } = useI18n();

  const [questions, setQuestions] = useState<PQuestion[] | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    setQuestions(null);
    setLoadError(false);
    setStep(0);
    setSelected(null);
    setChecked(false);
    setCorrect(0);
    setDone(false);
    try {
      const path = experience
        ? `/auth/placement-quiz?experience=${experience}`
        : "/auth/placement-quiz";
      const data = await apiRequest<QuizResponse>(path);
      setQuestions(data.questions || []);
    } catch {
      setLoadError(true);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locale]);

  const continueToApp = () => {
    router.replace("/(tabs)");
  };

  // Onboarding must never be blocked: a failed fetch or an empty quiz pool
  // always leads to a way forward into the app.
  if (loadError || (questions && questions.length === 0)) {
    return (
      <View
        style={[
          styles.root,
          styles.fallbackWrap,
          { paddingTop: insets.top + spacing.xxxl, paddingBottom: insets.bottom + spacing.xl },
        ]}
      >
        <MaterialCommunityIcons name="compass-outline" size={72} color={colors.brand} />
        <Text style={styles.fallbackTitle}>{t("placement.errorTitle")}</Text>
        <Text style={styles.fallbackSub}>{t("placement.errorSubtitle")}</Text>
        <PrimaryButton
          testID="placement-continue"
          label={t("placement.errorContinue")}
          onPress={continueToApp}
          style={{ marginTop: spacing.xl, alignSelf: "stretch" }}
        />
      </View>
    );
  }

  if (!questions) return <Loading testID="placement-loading" />;

  if (done) {
    return (
      <View style={[styles.root, { paddingTop: insets.top }]}>
        <ScrollView contentContainerStyle={styles.resultScroll}>
          <MaterialCommunityIcons name="check-circle" size={90} color={colors.brand} />
          <Text style={styles.resultTitle}>{t("placement.doneTitle")}</Text>
          <Text style={styles.resultSub}>{t("placement.doneSubtitle")}</Text>
        </ScrollView>
        <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
          <PrimaryButton
            testID="placement-continue"
            label={t("placement.continueToApp")}
            onPress={continueToApp}
          />
        </View>
      </View>
    );
  }

  const question = questions[step];
  const progress = (step / questions.length) * 100;

  const submit = async (finalCorrect: number) => {
    setSubmitting(true);
    try {
      const res = await apiRequest<CompleteResponse>("/auth/placement-quiz/complete", {
        method: "POST",
        body: { correct: finalCorrect, total: questions.length },
      });
      setUser(res.user);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {
      // Never block onboarding if the submission fails — the user still
      // continues into the app with their existing progress untouched.
    } finally {
      setSubmitting(false);
      setDone(true);
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
    if (step + 1 >= questions.length) {
      await submit(finalCorrect);
    } else {
      setStep(step + 1);
    }
  };

  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.sm }]}>
      <View style={styles.topBar}>
        <View style={styles.progressBg}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <View style={styles.tierTag}>
          <Text style={styles.tierTagText}>{t(`tier.${question.tier}` as any)}</Text>
        </View>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.body} showsVerticalScrollIndicator={false}>
        <Text style={styles.tag}>
          {t("placement.q")} {step + 1} {t("placement.of")} {questions.length}
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
                testID={`placement-option-${i}`}
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
              {selected === question.answer ? t("placement.correct") : t("placement.notQuite")}
            </Text>
            <Text style={styles.explainText}>{question.explain}</Text>
          </View>
        )}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <PrimaryButton
          testID="placement-action-button"
          label={checked ? t("placement.continue") : t("placement.check")}
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
  resultTitle: { fontFamily: fonts.display, fontSize: 34, color: colors.onSurface, marginTop: spacing.lg, textAlign: "center" },
  resultSub: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, marginTop: spacing.xs, marginBottom: spacing.xl, textAlign: "center", paddingHorizontal: spacing.lg },
  fallbackWrap: { alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.xl },
  fallbackTitle: { fontFamily: fonts.display, fontSize: 24, color: colors.onSurface, marginTop: spacing.lg, textAlign: "center" },
  fallbackSub: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, marginTop: spacing.sm, textAlign: "center", lineHeight: 21 },
});
