import { Platform } from "react-native";

export const colors = {
  surface: "#09090B",
  onSurface: "#FAFAFA",
  surfaceSecondary: "#18181B",
  onSurfaceSecondary: "#E4E4E7",
  surfaceTertiary: "#27272A",
  onSurfaceTertiary: "#D4D4D8",
  brand: "#10B981",
  onBrand: "#022C22",
  brandDark: "#047857",
  amber: "#F59E0B",
  onAmber: "#451A03",
  error: "#EF4444",
  muted: "#71717A",
  border: "#27272A",
  borderStrong: "#3F3F46",
};

export const fonts = {
  display: "BarlowCondensed-SemiBold",
  displayMed: "BarlowCondensed-Medium",
  displayReg: "BarlowCondensed-Regular",
  body: "Manrope-Regular",
  bodyMed: "Manrope-Medium",
  bodySemi: "Manrope-SemiBold",
};

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
export const radius = { sm: 6, md: 12, lg: 20, pill: 999 };

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
