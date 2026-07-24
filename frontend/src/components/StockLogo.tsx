import React, { useState } from "react";
import { View, Text, StyleSheet } from "react-native";
import { Image } from "expo-image";
import { colors, fonts } from "@/src/theme/theme";

// Deterministic accent color per symbol so the fallback looks intentional.
const PALETTE = ["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#EF4444"];

function colorFor(symbol: string) {
  let sum = 0;
  for (let i = 0; i < symbol.length; i++) sum += symbol.charCodeAt(i);
  return PALETTE[sum % PALETTE.length];
}

type Props = {
  uri?: string;
  symbol: string;
  size: number;
  borderRadius: number;
};

export default function StockLogo({ uri, symbol, size, borderRadius }: Props) {
  const [failed, setFailed] = useState(false);
  const style = { width: size, height: size, borderRadius };

  if (!uri || failed) {
    return (
      <View style={[styles.fallback, style, { backgroundColor: colorFor(symbol) }]}>
        <Text style={[styles.initials, { fontSize: size * 0.4 }]}>
          {symbol.slice(0, 2)}
        </Text>
      </View>
    );
  }

  return (
    <Image
      source={{ uri }}
      style={[style, { backgroundColor: "#FFFFFF" }]}
      contentFit="contain"
      transition={200}
      onError={() => setFailed(true)}
    />
  );
}

const styles = StyleSheet.create({
  fallback: { alignItems: "center", justifyContent: "center" },
  initials: { color: "#FFFFFF", fontFamily: fonts.display, letterSpacing: 0.5 },
});
