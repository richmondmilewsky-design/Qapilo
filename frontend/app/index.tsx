import { useEffect } from "react";
import { View } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "@/src/context/AuthContext";
import { Loading } from "@/src/components/ui";
import { colors } from "@/src/theme/theme";

export default function Index() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (user && !user.accepted_terms) router.replace("/agreement");
    else if (user) router.replace("/(tabs)");
    else router.replace("/auth");
  }, [user, loading, router]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Loading testID="app-loading" />
    </View>
  );
}
