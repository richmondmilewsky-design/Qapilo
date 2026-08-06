import { useEffect } from "react";
import { View } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "@/src/context/AuthContext";
import { storage } from "@/src/utils/storage";
import { Loading } from "@/src/components/ui";
import { colors } from "@/src/theme/theme";
import { ONBOARDING_KEY } from "./onboarding";

export default function Index() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    (async () => {
      if (user && !user.accepted_terms) return router.replace("/agreement");
      if (user && !user.experience_level) return router.replace("/experience");
      if (user) return router.replace("/(tabs)");
      const onboarded = await storage.getItem<boolean>(ONBOARDING_KEY, false);
      router.replace(onboarded ? "/auth" : "/onboarding");
    })();
  }, [user, loading, router]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Loading testID="app-loading" />
    </View>
  );
}
