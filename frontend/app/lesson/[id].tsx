import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ScrollView,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useAuth } from "@/src/context/AuthContext";
import { PrimaryButton, Loading } from "@/src/components/ui";
import { colors, fonts, radius, spacing, BADGE_ICONS } from "@/src/theme/theme";

type Card = { heading: string; body: string };
type Question = { q: string; options: string[]; answer: number; explain: string };
type LessonData = {
  id: string;
  title: string;
  unit_title: string;
  unit_color: string;
  xp: number;
  cards: Card[];
  questions: Question[];
};
type Badge = { id: string; name: string; desc: string; icon: string };
type Result = {
  earned_xp: number;
  first_time: boolean;
  perfect: boolean;
  new_badges: Badge[];
  user: any;
};

export default function LessonScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { setUser } = useAuth();

  const [lesson, setLesson] = useState<LessonData | null>(null);
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [result, setResult] = useState<Result | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiRequest<LessonData>(`/lessons/${id}`);
        setLesson(data);
      } catch {
        router.back();
      }
    })();
  }, [id]);

  if (!lesson) return <Loading testID="lesson-loading" />;

  const totalSteps = lesson.cards.length + lesson.questions.length;
  const inCards = step < lesson.cards.length;
  const qIndex = step - lesson.cards.length;
  const question = !inCards ? lesson.questions[qIndex] : null;
  const progress = (step / totalSteps) * 100;

  const submitLesson = async (finalCorrect: number) => {
    setSubmitting(true);
    try {
      const res = await apiRequest<Result>(`/lessons/${lesson.id}/complete`, {
        method: "POST",
        body: { correct: finalCorrect, total: lesson.questions.length },
      });
      setUser(res.user);
      setResult(res);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {
    } finally {
      setSubmitting(false);
    }
  };

  const next = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    if (inCards) {
      setStep(step + 1);
      return;
    }
    // question phase
    if (!checked) {
      if (selected === null) return;
      const isCorrect = selected === question!.answer;
      setChecked(true);
      if (isCorrect) {
        setCorrectCount((c) => c + 1);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
      return;
    }
    // continue after feedback
    const finalCorrect = correctCount;
    setChecked(false);
    setSelected(null);
    if (qIndex + 1 >= lesson.questions.length) {
      await submitLesson(finalCorrect);
    } else {
      setStep(step + 1);
    }
  };

  // ---------- Result screen ----------
  if (result) {
    return (
      <View style={[styles.root, { paddingTop: insets.top }]}>
        <ScrollView contentContainerStyle={styles.resultScroll}>
          <View style={styles.resultBadge}>
            <MaterialCommunityIcons
              name={result.perfect ? "star-circle" : "check-circle"}
              size={90}
              color={result.perfect ? colors.amber : colors.brand}
            />
          </View>
          <Text style={styles.resultTitle}>
            {result.perfect ? "Perfect!" : "Lesson Complete!"}
          </Text>
          <Text style={styles.resultSub}>
            You got {correctCount}/{lesson.questions.length} correct
          </Text>

          <View style={styles.rewardRow}>
            <View style={styles.rewardCard}>
              <MaterialCommunityIcons name="flash" size={26} color={colors.brand} />
              <Text style={styles.rewardValue}>+{result.earned_xp}</Text>
              <Text style={styles.rewardLabel}>XP EARNED</Text>
            </View>
            <View style={styles.rewardCard}>
              <MaterialCommunityIcons name="fire" size={26} color={colors.amber} />
              <Text style={styles.rewardValue}>{result.user.streak}</Text>
              <Text style={styles.rewardLabel}>DAY STREAK</Text>
            </View>
          </View>

          {result.new_badges.length > 0 && (
            <View style={styles.badgeUnlock}>
              <Text style={styles.badgeUnlockTitle}>NEW BADGE UNLOCKED</Text>
              {result.new_badges.map((b) => (
                <View key={b.id} style={styles.badgeRow} testID={`unlocked-badge-${b.id}`}>
                  <View style={styles.badgeIcon}>
                    <MaterialCommunityIcons
                      name={(BADGE_ICONS[b.icon] || "medal") as any}
                      size={24}
                      color={colors.amber}
                    />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.badgeName}>{b.name}</Text>
                    <Text style={styles.badgeDesc}>{b.desc}</Text>
                  </View>
                </View>
              ))}
            </View>
          )}
        </ScrollView>
        <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
          <PrimaryButton
            testID="result-continue-button"
            label="Continue"
            onPress={() => router.back()}
          />
        </View>
      </View>
    );
  }

  // ---------- Lesson flow ----------
  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.sm }]}>
      {/* Top bar */}
      <View style={styles.topBar}>
        <Pressable testID="lesson-close-button" onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="close" size={28} color={colors.muted} />
        </Pressable>
        <View style={styles.progressBg}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <View style={styles.xpTag}>
          <MaterialCommunityIcons name="flash" size={14} color={colors.brand} />
          <Text style={styles.xpTagText}>{lesson.xp}</Text>
        </View>
      </View>

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={styles.body}
        showsVerticalScrollIndicator={false}
      >
        {inCards ? (
          <View testID="lesson-card">
            <Text style={[styles.tag, { color: lesson.unit_color }]}>{lesson.unit_title.toUpperCase()}</Text>
            <Text style={styles.cardHeading}>{lesson.cards[step].heading}</Text>
            <Text style={styles.cardBody}>{lesson.cards[step].body}</Text>
          </View>
        ) : (
          <View testID="lesson-question">
            <Text style={styles.tag}>QUESTION {qIndex + 1} OF {lesson.questions.length}</Text>
            <Text style={styles.question}>{question!.q}</Text>
            <View style={{ gap: spacing.md, marginTop: spacing.lg }}>
              {question!.options.map((opt, i) => {
                const isSel = selected === i;
                const isAnswer = i === question!.answer;
                let border = colors.border;
                let bg = colors.surfaceSecondary;
                if (checked) {
                  if (isAnswer) {
                    border = colors.brand;
                    bg = "#0C2E22";
                  } else if (isSel) {
                    border = colors.error;
                    bg = "#2E0C0C";
                  }
                } else if (isSel) {
                  border = colors.brand;
                }
                return (
                  <Pressable
                    key={i}
                    testID={`answer-option-${i}`}
                    disabled={checked}
                    onPress={() => {
                      Haptics.selectionAsync();
                      setSelected(i);
                    }}
                    style={[styles.option, { borderColor: border, backgroundColor: bg }]}
                  >
                    <Text style={styles.optionText}>{opt}</Text>
                    {checked && isAnswer && (
                      <Ionicons name="checkmark-circle" size={22} color={colors.brand} />
                    )}
                    {checked && isSel && !isAnswer && (
                      <Ionicons name="close-circle" size={22} color={colors.error} />
                    )}
                  </Pressable>
                );
              })}
            </View>

            {checked && (
              <View
                style={[
                  styles.explainBox,
                  { borderColor: selected === question!.answer ? colors.brand : colors.error },
                ]}
                testID="answer-explanation"
              >
                <Text style={styles.explainTitle}>
                  {selected === question!.answer ? "Correct!" : "Not quite"}
                </Text>
                <Text style={styles.explainText}>{question!.explain}</Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <PrimaryButton
          testID="lesson-action-button"
          label={inCards ? "Continue" : checked ? "Continue" : "Check"}
          onPress={next}
          loading={submitting}
          disabled={!inCards && !checked && selected === null}
          variant={checked && selected !== question?.answer ? "amber" : "brand"}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
  },
  progressBg: {
    flex: 1,
    height: 12,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceTertiary,
    overflow: "hidden",
  },
  progressFill: { height: "100%", backgroundColor: colors.brand, borderRadius: radius.pill },
  xpTag: { flexDirection: "row", alignItems: "center", gap: 3 },
  xpTagText: { fontFamily: fonts.display, fontSize: 16, color: colors.onSurface },
  body: { padding: spacing.xl, paddingBottom: spacing.xxxl },
  tag: { fontFamily: fonts.displayMed, fontSize: 13, color: colors.muted, letterSpacing: 1.5, marginBottom: spacing.md },
  cardHeading: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface, marginBottom: spacing.lg, lineHeight: 34 },
  cardBody: { fontFamily: fonts.body, fontSize: 17, color: colors.onSurfaceSecondary, lineHeight: 27 },
  question: { fontFamily: fonts.display, fontSize: 26, color: colors.onSurface, lineHeight: 30 },
  option: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 2,
    minHeight: 58,
  },
  optionText: { fontFamily: fonts.bodyMed, fontSize: 16, color: colors.onSurface, flex: 1, paddingRight: spacing.sm },
  explainBox: {
    marginTop: spacing.xl,
    padding: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 1,
    backgroundColor: colors.surfaceSecondary,
  },
  explainTitle: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface, marginBottom: 4 },
  explainText: { fontFamily: fonts.body, fontSize: 14, color: colors.onSurfaceSecondary, lineHeight: 21 },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surface,
  },
  // Result
  resultScroll: { padding: spacing.xl, alignItems: "center", paddingTop: spacing.xxxl },
  resultBadge: { marginBottom: spacing.lg },
  resultTitle: { fontFamily: fonts.display, fontSize: 36, color: colors.onSurface },
  resultSub: { fontFamily: fonts.body, fontSize: 15, color: colors.muted, marginTop: spacing.xs, marginBottom: spacing.xl },
  rewardRow: { flexDirection: "row", gap: spacing.md, width: "100%" },
  rewardCard: {
    flex: 1,
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.xl,
    gap: 4,
  },
  rewardValue: { fontFamily: fonts.display, fontSize: 30, color: colors.onSurface },
  rewardLabel: { fontFamily: fonts.displayMed, fontSize: 11, color: colors.muted, letterSpacing: 1 },
  badgeUnlock: { width: "100%", marginTop: spacing.xl },
  badgeUnlockTitle: { fontFamily: fonts.displayMed, fontSize: 13, color: colors.amber, letterSpacing: 1.5, marginBottom: spacing.md, textAlign: "center" },
  badgeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  badgeIcon: {
    width: 44,
    height: 44,
    borderRadius: radius.pill,
    backgroundColor: "#2E2410",
    alignItems: "center",
    justifyContent: "center",
  },
  badgeName: { fontFamily: fonts.bodySemi, fontSize: 15, color: colors.onSurface },
  badgeDesc: { fontFamily: fonts.body, fontSize: 13, color: colors.muted },
});
