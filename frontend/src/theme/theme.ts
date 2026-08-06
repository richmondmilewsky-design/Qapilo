import { Platform } from "react-native";

export const colors = {
  surface: "#0a1210",
  onSurface: "#ffffff",
  surfaceSecondary: "rgba(255,255,255,0.05)",
  onSurfaceSecondary: "rgba(255,255,255,0.72)",
  surfaceTertiary: "rgba(255,255,255,0.08)",
  onSurfaceTertiary: "rgba(255,255,255,0.6)",
  elevated: "#14201b",
  elevatedSecondary: "#1d2d26",
  brand: "#22d99a",
  onBrand: "#06231a",
  brandDark: "#159168",
  amber: "#e79a2e",
  onAmber: "#2a1806",
  error: "#ef4444",
  muted: "rgba(255,255,255,0.5)",
  border: "rgba(255,255,255,0.09)",
  borderStrong: "rgba(255,255,255,0.16)",
};

// Reusable gradients + accent tokens for the Qapilo visual system.
export const gradients = {
  brand: ["#22d99a", "#159168"] as const,       // CTAs
  brandProgress: ["#159168", "#22d99a"] as const, // progress fill
  loginBg: ["#163b2c", "#0a1210"] as const,      // login radial-ish
};

export const shadows = {
  brand: {
    shadowColor: "#22d99a",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    elevation: 8,
  },
};

export const fonts = {
  display: "Sora-ExtraBold",
  displayMed: "Sora-Bold",
  displayReg: "Sora-SemiBold",
  body: "Inter-Regular",
  bodyMed: "Inter-Medium",
  bodySemi: "Inter-SemiBold",
  bodyBold: "Inter-Bold",
};

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
export const radius = { sm: 8, md: 12, lg: 16, xl: 20, pill: 999 };

// Lesson node icons -> MaterialCommunityIcons safe names
export const LESSON_ICONS: Record<string, string> = {
  "trending-up": "trending-up",
  bank: "bank",
  "chart-line": "chart-line",
  "swap-vertical": "swap-vertical",
  cash: "cash-multiple",
  shield: "shield-check",
  list: "format-list-bulleted",
  cursor: "cursor-default-click",
  "chart-bar": "chart-bar",
  receipt: "receipt",
  calculator: "calculator-variant",
  globe: "earth",
  grid: "view-grid",
  clock: "clock-outline",
  trophy: "trophy",
};

export const BADGE_ICONS: Record<string, string> = {
  flag: "flag-checkered",
  flame: "fire",
  star: "star",
  medal: "medal",
  trophy: "trophy",
  "trending-up": "trending-up",
  bolt: "flash",
};

export const fontShim = Platform.OS === "web" ? {} : {};
