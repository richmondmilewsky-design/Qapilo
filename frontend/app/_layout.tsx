import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { useEffect } from "react";
import { LogBox, Platform } from "react-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { KeyboardProvider } from "react-native-keyboard-controller";
import { StatusBar } from "expo-status-bar";
import { useFonts } from "expo-font";

import { useIconFonts } from "@/src/hooks/use-icon-fonts";
import { AuthProvider } from "@/src/context/AuthContext";
import { I18nProvider } from "@/src/i18n/I18nContext";
import { colors } from "@/src/theme/theme";

// Web only: the dev server does not apply app/+html.tsx, so we ensure the
// viewport opts into the safe-area (viewport-fit=cover) and inject the dynamic
// viewport-height + bottom-tab safe-area CSS here. Runs at import time (before
// safe-area measurement) and is idempotent.
if (Platform.OS === "web" && typeof document !== "undefined") {
  const vp = document.querySelector('meta[name="viewport"]');
  if (vp) {
    const c = vp.getAttribute("content") || "";
    if (!/viewport-fit\s*=\s*cover/.test(c)) {
      vp.setAttribute("content", c ? `${c}, viewport-fit=cover` : "width=device-width, initial-scale=1, viewport-fit=cover");
    }
  }
  if (document.head && !document.getElementById("qapilo-safe-area-css")) {
    const s = document.createElement("style");
    s.id = "qapilo-safe-area-css";
    s.textContent = `
      /* Dynamic viewport height so Safari's collapsing address bar never cuts
         off the bottom (dvh where supported, -webkit-fill-available fallback). */
      html, body { height: 100vh; height: -webkit-fill-available; }
      @supports (height: 100dvh) { html, body { height: 100dvh; } }
      /* Bottom tab bar clears the iOS home indicator on Safari/Chrome. */
      @supports (padding: max(0px, env(safe-area-inset-bottom))) {
        [role="tablist"] {
          box-sizing: border-box !important;
          height: calc(52px + max(10px, env(safe-area-inset-bottom))) !important;
          min-height: calc(52px + max(10px, env(safe-area-inset-bottom))) !important;
          padding-bottom: max(10px, env(safe-area-inset-bottom)) !important;
        }
      }
    `;
    document.head.appendChild(s);
  }
}

LogBox.ignoreAllLogs(true);
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [iconsLoaded, iconsError] = useIconFonts();
  const [appFontsLoaded, appFontsError] = useFonts({
    "Sora-SemiBold": require("../assets/fonts/Sora-SemiBold.ttf"),
    "Sora-Bold": require("../assets/fonts/Sora-Bold.ttf"),
    "Sora-ExtraBold": require("../assets/fonts/Sora-ExtraBold.ttf"),
    "Inter-Regular": require("../assets/fonts/Inter-Regular.ttf"),
    "Inter-Medium": require("../assets/fonts/Inter-Medium.ttf"),
    "Inter-SemiBold": require("../assets/fonts/Inter-SemiBold.ttf"),
    "Inter-Bold": require("../assets/fonts/Inter-Bold.ttf"),
  });

  const ready = (iconsLoaded || iconsError) && (appFontsLoaded || appFontsError);

  useEffect(() => {
    if (ready) SplashScreen.hideAsync();
  }, [ready]);

  if (!ready) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1, backgroundColor: colors.surface }}>
      <KeyboardProvider>
      <SafeAreaProvider>
        <I18nProvider>
          <AuthProvider>
            <StatusBar style="light" />
            <Stack
              screenOptions={{
                headerShown: false,
                contentStyle: { backgroundColor: colors.surface },
                animation: "slide_from_right",
              }}
            >
              <Stack.Screen name="lesson/[id]" options={{ animation: "slide_from_bottom" }} />
              <Stack.Screen name="paywall" options={{ animation: "slide_from_bottom", presentation: "modal" }} />
            </Stack>
          </AuthProvider>
        </I18nProvider>
      </SafeAreaProvider>
      </KeyboardProvider>
    </GestureHandlerRootView>
  );
}
