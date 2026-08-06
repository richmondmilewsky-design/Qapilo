import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  Platform,
  Pressable,
  Image,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import * as AppleAuthentication from "expo-apple-authentication";
import { useAuth } from "@/src/context/AuthContext";
import { useI18n } from "@/src/i18n/I18nContext";
import { LanguageButton } from "@/src/components/LanguageButton";
import { PrimaryButton } from "@/src/components/ui";
import { storage } from "@/src/utils/storage";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

function passwordScore(p: string): number {
  let s = 0;
  if (p.length >= 8) s++;
  if (/[a-z]/.test(p) && /[A-Z]/.test(p)) s++;
  if (/\d/.test(p)) s++;
  if (/[^A-Za-z0-9]/.test(p)) s++;
  return s;
}

export default function AuthScreen() {
  const { login, signup, loginWithGoogle, loginWithApple } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { t } = useI18n();

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [gLoading, setGLoading] = useState(false);
  const [appleAvailable, setAppleAvailable] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");

  const emailRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);

  useEffect(() => {
    if (Platform.OS !== "ios") return;
    AppleAuthentication.isAvailableAsync()
      .then(setAppleAvailable)
      .catch(() => setAppleAvailable(false));
  }, []);

  const submit = async () => {
    setError("");
    setLoading(true);
    try {
      await storage.setItem("tq_remember", remember);
      const u =
        mode === "signup"
          ? await signup(email.trim(), password, name.trim() || "Investor")
          : await login(email.trim(), password);
      await storage.setItem("qapilo_welcome", `${mode}::${u.name}`);
      router.replace("/");
    } catch (e: any) {
      setError(e.message || t("auth.failed"));
    } finally {
      setLoading(false);
    }
  };

  const google = async () => {
    setError("");
    setGLoading(true);
    try {
      await storage.setItem("tq_remember", remember);
      await loginWithGoogle();
      router.replace("/");
    } catch (e: any) {
      setError(e.message || t("auth.googleFailed"));
    } finally {
      setGLoading(false);
    }
  };

  const apple = async () => {
    setError("");
    try {
      await storage.setItem("tq_remember", remember);
      await loginWithApple();
      router.replace("/");
    } catch (e: any) {
      // User cancelled the native sheet — not an error worth surfacing.
      if (e?.code === "ERR_REQUEST_CANCELED" || e?.code === "ERR_CANCELED") return;
      setError(e.message || t("auth.appleFailed"));
    }
  };

  return (
    <View style={styles.root}>
      <LinearGradient
        colors={["#163b2c", "#0f2820", colors.surface]}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />
      <KeyboardAwareScrollView
        style={{ flex: 1 }}
        contentContainerStyle={[
          styles.scroll,
          { paddingTop: insets.top + spacing.xxl, paddingBottom: insets.bottom + spacing.xl },
        ]}
        keyboardShouldPersistTaps="handled"
        keyboardDismissMode="on-drag"
        showsVerticalScrollIndicator={false}
        bottomOffset={24}
      >
            <View style={styles.langTop}>
              <LanguageButton />
            </View>
            <View style={styles.logoWrap}>
              <Image
                source={require("../assets/images/qapilo-logo.png")}
                style={styles.logoImg}
                resizeMode="cover"
              />
              <Text style={styles.brand}>QAPILO</Text>
              <Text style={styles.tagline}>{t("auth.tagline")}</Text>
            </View>

            <Text style={styles.h1} testID="auth-heading">
              {mode === "login" ? t("auth.welcomeBack") : t("auth.createAccount")}
            </Text>

            <Pressable
              testID="google-login-button"
              onPress={google}
              disabled={gLoading}
              style={({ pressed }) => [styles.socialBtn, { opacity: pressed ? 0.85 : 1 }]}
            >
              <Ionicons name="logo-google" size={20} color={colors.onSurface} style={styles.socialIcon} />
              <Text style={styles.socialText}>
                {gLoading ? "…" : t("auth.google")}
              </Text>
            </Pressable>

            {Platform.OS === "ios" && appleAvailable && (
              <Pressable
                testID="apple-login-button"
                onPress={apple}
                style={({ pressed }) => [styles.socialBtn, styles.socialBtnSpacing, { opacity: pressed ? 0.85 : 1 }]}
              >
                <Ionicons name="logo-apple" size={22} color={colors.onSurface} style={styles.socialIcon} />
                <Text style={styles.socialText}>{t("auth.apple")}</Text>
              </Pressable>
            )}

            <View style={styles.divider}>
              <View style={styles.line} />
              <Text style={styles.dividerText}>{t("auth.or")}</Text>
              <View style={styles.line} />
            </View>

            {mode === "signup" && (
              <TextInput
                testID="name-input"
                placeholder={t("auth.name")}
                placeholderTextColor={colors.muted}
                value={name}
                onChangeText={setName}
                style={styles.input}
                autoCapitalize="words"
                returnKeyType="next"
                blurOnSubmit={false}
                onSubmitEditing={() => emailRef.current?.focus()}
              />
            )}
            <TextInput
              ref={emailRef}
              testID="email-input"
              placeholder={t("auth.email")}
              placeholderTextColor={colors.muted}
              value={email}
              onChangeText={setEmail}
              style={styles.input}
              autoCapitalize="none"
              keyboardType="email-address"
              autoCorrect={false}
              returnKeyType="next"
              blurOnSubmit={false}
              onSubmitEditing={() => passwordRef.current?.focus()}
            />
            <View style={styles.passwordWrap}>
              <TextInput
                ref={passwordRef}
                testID="password-input"
                placeholder={t("auth.password")}
                placeholderTextColor={colors.muted}
                value={password}
                onChangeText={setPassword}
                style={[styles.input, { marginBottom: 0, paddingRight: 52 }]}
                secureTextEntry={!showPassword}
                returnKeyType="go"
                onSubmitEditing={submit}
              />
              <Pressable
                testID="toggle-password"
                onPress={() => setShowPassword((v) => !v)}
                style={styles.eyeBtn}
                hitSlop={8}
              >
                <Ionicons
                  name={showPassword ? "eye-off-outline" : "eye-outline"}
                  size={22}
                  color={colors.muted}
                />
              </Pressable>
            </View>

            {mode === "signup" && password.length > 0 && (() => {
              const score = passwordScore(password);
              const level = score <= 2 ? "weak" : score === 3 ? "medium" : "strong";
              const barColor =
                level === "weak" ? colors.error : level === "medium" ? colors.amber : colors.brand;
              const filled = level === "weak" ? 1 : level === "medium" ? 2 : 3;
              const label =
                level === "weak" ? t("auth.pwWeak") : level === "medium" ? t("auth.pwMedium") : t("auth.pwStrong");
              return (
                <View style={styles.strengthWrap} testID="password-strength">
                  <View style={styles.strengthBars}>
                    {[0, 1, 2].map((i) => (
                      <View
                        key={i}
                        style={[
                          styles.strengthSeg,
                          { backgroundColor: i < filled ? barColor : colors.surfaceTertiary },
                        ]}
                      />
                    ))}
                  </View>
                  <Text style={[styles.strengthLabel, { color: barColor }]}>{label}</Text>
                </View>
              );
            })()}

            {error ? (
              <Text testID="auth-error" style={styles.error}>
                {error}
              </Text>
            ) : null}

            <Pressable
              testID="remember-toggle"
              onPress={() => setRemember((v) => !v)}
              style={styles.rememberRow}
              hitSlop={6}
            >
              <View style={[styles.checkbox, remember && styles.checkboxChecked]}>
                {remember && <Ionicons name="checkmark" size={14} color={colors.onBrand} />}
              </View>
              <Text style={styles.rememberText}>{t("auth.remember")}</Text>
            </Pressable>

            <PrimaryButton
              testID="auth-submit-button"
              label={mode === "login" ? t("auth.login") : t("auth.signup")}
              onPress={submit}
              loading={loading}
              style={{ marginTop: spacing.md }}
            />

            {mode === "login" && (
              <Pressable
                testID="forgot-password-link"
                onPress={() => router.push("/forgot-password")}
                style={{ alignSelf: "center", marginTop: spacing.md }}
              >
                <Text style={styles.toggleLink}>{t("auth.forgotLink")}</Text>
              </Pressable>
            )}

            <Pressable
              testID="toggle-auth-mode"
              onPress={() => {
                setError("");
                setMode(mode === "login" ? "signup" : "login");
              }}
              style={styles.toggle}
            >
              <Text style={styles.toggleText}>
                {mode === "login" ? t("auth.newHere") : t("auth.haveAccount")}
                <Text style={styles.toggleLink}>
                  {mode === "login" ? t("auth.createOne") : t("auth.loginLink")}
                </Text>
              </Text>
            </Pressable>

            <Text style={styles.terms}>
              {t("auth.terms")}
              <Text
                testID="auth-disclaimer-link"
                style={styles.toggleLink}
                onPress={() => router.push("/disclaimer")}
              >
                {t("auth.termsLink")}
              </Text>
              {t("auth.termsEnd")}
            </Text>
        </KeyboardAwareScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  scroll: { paddingHorizontal: spacing.xl },
  logoWrap: { alignItems: "center", marginBottom: spacing.xxl },
  langTop: { alignItems: "flex-end", marginBottom: spacing.sm },
  logoImg: {
    width: 84,
    height: 84,
    borderRadius: radius.lg,
    marginBottom: spacing.md,
  },
  brand: { fontFamily: fonts.display, fontSize: 34, color: colors.onSurface, letterSpacing: 1 },
  tagline: {
    fontFamily: fonts.body,
    fontSize: 14,
    color: colors.muted,
    textAlign: "center",
    marginTop: spacing.xs,
    maxWidth: 260,
  },
  h1: { fontFamily: fonts.display, fontSize: 28, color: colors.onSurface, marginBottom: spacing.lg },
  socialBtn: {
    height: 54,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  socialBtnSpacing: { marginTop: spacing.md },
  socialIcon: { position: "absolute", left: spacing.lg },
  socialText: { fontFamily: fonts.bodySemi, fontSize: 16, color: colors.onSurface },
  divider: { flexDirection: "row", alignItems: "center", marginVertical: spacing.lg, gap: spacing.md },
  line: { flex: 1, height: 1, backgroundColor: colors.border },
  dividerText: { fontFamily: fonts.body, color: colors.muted, fontSize: 13 },
  input: {
    height: 54,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.lg,
    color: colors.onSurface,
    fontFamily: fonts.body,
    fontSize: 15,
    marginBottom: spacing.md,
  },
  passwordWrap: { position: "relative", marginBottom: spacing.md },
  eyeBtn: {
    position: "absolute",
    right: spacing.md,
    top: 0,
    bottom: 0,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.xs,
  },
  strengthWrap: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginTop: -spacing.xs,
    marginBottom: spacing.md,
  },
  strengthBars: { flexDirection: "row", gap: 6, flex: 1 },
  strengthSeg: { flex: 1, height: 5, borderRadius: radius.pill },
  strengthLabel: { fontFamily: fonts.bodySemi, fontSize: 12, minWidth: 56, textAlign: "right" },
  rememberRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginTop: spacing.sm,
    alignSelf: "flex-start",
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: radius.sm,
    borderWidth: 1.5,
    borderColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
    alignItems: "center",
    justifyContent: "center",
  },
  checkboxChecked: { backgroundColor: colors.brand, borderColor: colors.brand },
  rememberText: { fontFamily: fonts.bodyMed, fontSize: 14, color: colors.onSurfaceSecondary },
  error: { color: colors.error, fontFamily: fonts.bodyMed, fontSize: 13, marginBottom: spacing.sm },
  toggle: { marginTop: spacing.xl, alignItems: "center" },
  toggleText: { fontFamily: fonts.body, color: colors.muted, fontSize: 14 },
  toggleLink: { fontFamily: fonts.bodySemi, color: colors.brand },
  terms: {
    fontFamily: fonts.body,
    fontSize: 12,
    color: colors.muted,
    textAlign: "center",
    marginTop: spacing.lg,
    lineHeight: 18,
  },
});
