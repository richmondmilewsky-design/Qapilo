import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { Text, StyleSheet, Modal, Pressable } from "react-native";
import { getLocales } from "expo-localization";
import { Ionicons } from "@expo/vector-icons";
import { storage } from "@/src/utils/storage";
import { setApiLang } from "@/src/api/client";
import { TRANSLATIONS, LANGUAGES, Lang } from "@/src/i18n/translations";
import { colors, fonts, radius, spacing } from "@/src/theme/theme";

const STORAGE_KEY = "tq_lang";

type I18nCtx = {
  locale: Lang;
  setLocale: (l: Lang) => void;
  t: (key: string) => string;
  openPicker: () => void;
};

const Ctx = createContext<I18nCtx>({} as I18nCtx);
export const useI18n = () => useContext(Ctx);

function detectLang(): Lang {
  try {
    const code = getLocales()?.[0]?.languageCode?.toLowerCase();
    if (code === "de" || code === "es") return code;
  } catch {}
  return "en";
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Lang>("en");
  const [pickerOpen, setPickerOpen] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const saved = (await storage.getItem(STORAGE_KEY, "")) as string;
      const initial: Lang = saved === "en" || saved === "de" || saved === "es" ? (saved as Lang) : detectLang();
      setApiLang(initial);
      setLocaleState(initial);
      setReady(true);
    })();
  }, []);

  const setLocale = useCallback((l: Lang) => {
    setApiLang(l);
    setLocaleState(l);
    storage.setItem(STORAGE_KEY, l);
    setPickerOpen(false);
  }, []);

  const t = useCallback(
    (key: string) => TRANSLATIONS[locale][key] ?? TRANSLATIONS.en[key] ?? key,
    [locale]
  );

  const openPicker = useCallback(() => setPickerOpen(true), []);

  if (!ready) return null;

  return (
    <Ctx.Provider value={{ locale, setLocale, t, openPicker }}>
      {children}
      <Modal visible={pickerOpen} transparent animationType="fade" onRequestClose={() => setPickerOpen(false)}>
        <Pressable style={styles.backdrop} onPress={() => setPickerOpen(false)}>
          <Pressable style={styles.sheet} testID="language-picker">
            <Text style={styles.sheetTitle}>{t("lang.title")}</Text>
            {LANGUAGES.map((l) => {
              const active = l.code === locale;
              return (
                <Pressable
                  key={l.code}
                  testID={`lang-option-${l.code}`}
                  onPress={() => setLocale(l.code)}
                  style={[styles.row, active && styles.rowActive]}
                >
                  <Text style={styles.flag}>{l.flag}</Text>
                  <Text style={[styles.label, active && styles.labelActive]}>{l.label}</Text>
                  {active && <Ionicons name="checkmark-circle" size={22} color={colors.brand} />}
                </Pressable>
              );
            })}
          </Pressable>
        </Pressable>
      </Modal>
    </Ctx.Provider>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.75)", justifyContent: "flex-end" },
  sheet: {
    backgroundColor: colors.elevated,
    borderTopLeftRadius: radius.lg,
    borderTopRightRadius: radius.lg,
    padding: spacing.lg,
    paddingBottom: spacing.xxxl,
    borderTopWidth: 1,
    borderColor: colors.border,
  },
  sheetTitle: { fontFamily: fonts.display, fontSize: 22, color: colors.onSurface, marginBottom: spacing.lg },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    padding: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.elevatedSecondary,
    marginBottom: spacing.sm,
  },
  rowActive: { borderColor: colors.brand, backgroundColor: "#0C2018" },
  flag: { fontSize: 24 },
  label: { flex: 1, fontFamily: fonts.bodyMed, fontSize: 16, color: colors.onSurface },
  labelActive: { color: colors.brand },
});
