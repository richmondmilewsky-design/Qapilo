import React, { useCallback, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  Pressable,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { apiRequest } from "@/src/api/client";
import { useI18n } from "@/src/i18n/I18nContext";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

type Msg = { role: "user" | "assistant"; content: string };


export default function TutorScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t, locale } = useI18n();
  const listRef = useRef<FlatList>(null);
  const SUGGESTIONS = [t("tutor.ex1"), t("tutor.ex2"), t("tutor.ex3"), t("tutor.ex4")];

  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [isPro, setIsPro] = useState(true);

  const load = useCallback(async () => {
    try {
      const [hist, status] = await Promise.all([
        apiRequest<{ messages: Msg[] }>("/tutor/history"),
        apiRequest<{ is_pro: boolean; remaining: number | null }>("/tutor/status"),
      ]);
      setMessages(hist.messages.map((m) => ({ role: m.role, content: m.content })));
      setIsPro(status.is_pro);
      setRemaining(status.remaining);
    } catch {}
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const scrollToEnd = () => setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 80);

  const send = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || sending) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setInput("");
    setMessages((m) => [...m, { role: "user", content: msg }]);
    setSending(true);
    scrollToEnd();
    try {
      const res = await apiRequest<{ reply: string; remaining: number | null }>("/tutor/chat", {
        method: "POST",
        body: { message: msg, lang: locale },
      });
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      setRemaining(res.remaining);
      scrollToEnd();
    } catch (e: any) {
      const limitHit = String(e.message || "").toLowerCase().includes("upgrade");
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: limitHit
            ? "⚡ You've used your free AI Tutor messages for today. Upgrade to Pro for unlimited chat!"
            : "Sorry, I couldn't answer that right now. Please try again.",
        },
      ]);
      if (limitHit) setRemaining(0);
      scrollToEnd();
    } finally {
      setSending(false);
    }
  };

  const limitReached = !isPro && remaining !== null && remaining <= 0;

  return (
    <View style={[styles.root, { paddingTop: insets.top + spacing.sm }]}>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={styles.botBadge}>
            <MaterialCommunityIcons name="robot-happy" size={20} color={colors.onBrand} />
          </View>
          <View>
            <Text style={styles.title}>{t("tutor.title")}</Text>
            <Text style={styles.subtitle}>
              {isPro ? t("tutor.unlimited") : `${t("tutor.free")} · ${remaining ?? 0} ${t("tutor.left")}`}
            </Text>
          </View>
        </View>
        {!isPro && (
          <Pressable testID="tutor-upgrade-pill" onPress={() => router.push("/paywall")} style={styles.proPill}>
            <MaterialCommunityIcons name="crown" size={14} color={colors.onAmber} />
            <Text style={styles.proPillText}>{t("tutor.goPro")}</Text>
          </Pressable>
        )}
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        keyboardVerticalOffset={insets.bottom + 64}
      >
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(_, i) => String(i)}
          contentContainerStyle={{ padding: spacing.lg, paddingBottom: spacing.lg, flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={scrollToEnd}
          ListEmptyComponent={
            <View style={styles.empty}>
              <View style={styles.emptyBadge}>
                <MaterialCommunityIcons name="robot-happy" size={40} color={colors.brand} />
              </View>
              <Text style={styles.emptyTitle}>{t("tutor.askAnything")}</Text>
              <Text style={styles.emptyText}>{t("tutor.intro")}</Text>
              <View style={{ gap: spacing.sm, marginTop: spacing.lg, width: "100%" }}>
                {SUGGESTIONS.map((s) => (
                  <Pressable
                    key={s}
                    testID={`suggestion-${s.slice(0, 8)}`}
                    onPress={() => send(s)}
                    style={styles.suggestion}
                  >
                    <Text style={styles.suggestionText}>{s}</Text>
                    <Ionicons name="arrow-forward" size={16} color={colors.muted} />
                  </Pressable>
                ))}
              </View>
            </View>
          }
          renderItem={({ item }) => (
            <View
              testID={`chat-msg-${item.role}`}
              style={[styles.bubbleRow, item.role === "user" ? styles.rowRight : styles.rowLeft]}
            >
              <View style={[styles.bubble, item.role === "user" ? styles.userBubble : styles.botBubble]}>
                <Text style={[styles.bubbleText, item.role === "user" && { color: colors.onBrand }]}>
                  {item.content}
                </Text>
              </View>
            </View>
          )}
          ListFooterComponent={
            sending ? (
              <View style={[styles.bubbleRow, styles.rowLeft]}>
                <View style={[styles.bubble, styles.botBubble]}>
                  <ActivityIndicator color={colors.brand} />
                </View>
              </View>
            ) : null
          }
        />

        {limitReached ? (
          <Pressable
            testID="tutor-limit-cta"
            onPress={() => router.push("/paywall")}
            style={[styles.limitBar, { paddingBottom: insets.bottom + spacing.md }]}
          >
            <MaterialCommunityIcons name="crown" size={20} color={colors.onAmber} />
            <Text style={styles.limitText}>{t("tutor.limit")}</Text>
          </Pressable>
        ) : (
          <View style={[styles.inputBar, { paddingBottom: insets.bottom + spacing.sm }]}>
            <TextInput
              testID="chat-input"
              placeholder={t("tutor.placeholder")}
              placeholderTextColor={colors.muted}
              value={input}
              onChangeText={setInput}
              style={styles.input}
              multiline
              onSubmitEditing={() => send()}
            />
            <Pressable
              testID="chat-send-button"
              onPress={() => send()}
              disabled={!input.trim() || sending}
              style={[styles.sendBtn, { opacity: !input.trim() || sending ? 0.5 : 1 }]}
            >
              <Ionicons name="arrow-up" size={22} color={colors.onBrand} />
            </Pressable>
          </View>
        )}
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerLeft: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  botBadge: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  title: { fontFamily: fonts.display, fontSize: 20, color: colors.onSurface },
  subtitle: { fontFamily: fonts.body, fontSize: 12, color: colors.muted },
  proPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: colors.amber,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: radius.pill,
  },
  proPillText: { fontFamily: fonts.bodySemi, fontSize: 12, color: colors.onAmber },
  empty: { flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.md },
  emptyBadge: {
    width: 80,
    height: 80,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceSecondary,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.lg,
  },
  emptyTitle: { fontFamily: fonts.display, fontSize: 24, color: colors.onSurface, textAlign: "center" },
  emptyText: { fontFamily: fonts.body, fontSize: 14, color: colors.muted, textAlign: "center", marginTop: 4 },
  suggestion: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  suggestionText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurfaceSecondary, flex: 1 },
  bubbleRow: { marginBottom: spacing.md, flexDirection: "row" },
  rowRight: { justifyContent: "flex-end" },
  rowLeft: { justifyContent: "flex-start" },
  bubble: { maxWidth: "84%", padding: spacing.md, borderRadius: radius.lg },
  userBubble: { backgroundColor: colors.brand, borderBottomRightRadius: radius.sm },
  botBubble: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderBottomLeftRadius: radius.sm,
  },
  bubbleText: { fontFamily: fonts.body, fontSize: 15, color: colors.onSurface, lineHeight: 22 },
  inputBar: {
    flexDirection: "row",
    alignItems: "flex-end",
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surface,
  },
  input: {
    flex: 1,
    maxHeight: 120,
    minHeight: 48,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.lg,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.md,
    color: colors.onSurface,
    fontFamily: fonts.body,
    fontSize: 15,
  },
  sendBtn: {
    width: 48,
    height: 48,
    borderRadius: radius.pill,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
  },
  limitBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.amber,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
  },
  limitText: { flex: 1, fontFamily: fonts.bodySemi, fontSize: 13, color: colors.onAmber },
});
