import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Pressable,
  Keyboard,
  TouchableWithoutFeedback,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MaterialCommunityIcons, Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useAuth } from "@/src/context/AuthContext";
import { PrimaryButton } from "@/src/components/ui";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

export default function AuthScreen() {
  const { login, signup, loginWithGoogle } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [gLoading, setGLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    setLoading(true);
    try {
      if (mode === "signup") await signup(email.trim(), password, name.trim() || "Investor");
      else await login(email.trim(), password);
      router.replace("/(tabs)");
    } catch (e: any) {
      setError(e.message || "Failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const google = async () => {
    setError("");
    setGLoading(true);
    try {
      await loginWithGoogle();
      router.replace("/(tabs)");
    } catch (e: any) {
      setError(e.message || "Google sign-in failed.");
    } finally {
      setGLoading(false);
    }
  };

  return (
    <View style={styles.root}>
      <LinearGradient
        colors={["#052E20", colors.surface, colors.surface]}
        style={StyleSheet.absoluteFill}
      />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
          <ScrollView
            contentContainerStyle={[
              styles.scroll,
              { paddingTop: insets.top + spacing.xxl, paddingBottom: insets.bottom + spacing.xl },
            ]}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.logoWrap}>
              <View style={styles.logoBadge}>
                <MaterialCommunityIcons name="chart-line-variant" size={34} color={colors.onBrand} />
              </View>
              <Text style={styles.brand}>TRADEQUEST</Text>
              <Text style={styles.tagline}>Master the stock market, one lesson at a time.</Text>
            </View>

            <Text style={styles.h1} testID="auth-heading">
              {mode === "login" ? "Welcome back" : "Create your account"}
            </Text>

            <Pressable
              testID="google-login-button"
              onPress={google}
              disabled={gLoading}
              style={({ pressed }) => [styles.googleBtn, { opacity: pressed ? 0.85 : 1 }]}
            >
              <Ionicons name="logo-google" size={20} color={colors.onSurface} />
              <Text style={styles.googleText}>
                {gLoading ? "Connecting…" : "Continue with Google"}
              </Text>
            </Pressable>

            <View style={styles.divider}>
              <View style={styles.line} />
              <Text style={styles.dividerText}>or</Text>
              <View style={styles.line} />
            </View>

            {mode === "signup" && (
              <TextInput
                testID="name-input"
                placeholder="Name"
                placeholderTextColor={colors.muted}
                value={name}
                onChangeText={setName}
                style={styles.input}
                autoCapitalize="words"
              />
            )}
            <TextInput
              testID="email-input"
              placeholder="Email"
              placeholderTextColor={colors.muted}
              value={email}
              onChangeText={setEmail}
              style={styles.input}
              autoCapitalize="none"
              keyboardType="email-address"
              autoCorrect={false}
            />
            <TextInput
              testID="password-input"
              placeholder="Password"
              placeholderTextColor={colors.muted}
              value={password}
              onChangeText={setPassword}
              style={styles.input}
              secureTextEntry
            />

            {error ? (
              <Text testID="auth-error" style={styles.error}>
                {error}
              </Text>
            ) : null}

            <PrimaryButton
              testID="auth-submit-button"
              label={mode === "login" ? "Log In" : "Sign Up"}
              onPress={submit}
              loading={loading}
              style={{ marginTop: spacing.md }}
            />

            <Pressable
              testID="toggle-auth-mode"
              onPress={() => {
                setError("");
                setMode(mode === "login" ? "signup" : "login");
              }}
              style={styles.toggle}
            >
              <Text style={styles.toggleText}>
                {mode === "login" ? "New here? " : "Already have an account? "}
                <Text style={styles.toggleLink}>
                  {mode === "login" ? "Create an account" : "Log in"}
                </Text>
              </Text>
            </Pressable>
          </ScrollView>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  scroll: { paddingHorizontal: spacing.xl },
  logoWrap: { alignItems: "center", marginBottom: spacing.xxl },
  logoBadge: {
    width: 72,
    height: 72,
    borderRadius: radius.lg,
    backgroundColor: colors.brand,
    alignItems: "center",
    justifyContent: "center",
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
  googleBtn: {
    height: 54,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
  googleText: { fontFamily: fonts.bodySemi, fontSize: 16, color: colors.onSurface },
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
  error: { color: colors.error, fontFamily: fonts.bodyMed, fontSize: 13, marginBottom: spacing.sm },
  toggle: { marginTop: spacing.xl, alignItems: "center" },
  toggleText: { fontFamily: fonts.body, color: colors.muted, fontSize: 14 },
  toggleLink: { fontFamily: fonts.bodySemi, color: colors.brand },
});
