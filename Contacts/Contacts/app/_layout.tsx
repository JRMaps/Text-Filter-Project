import { Stack } from "expo-router";
import { ContactProvider } from "./ContactContext";

export default function RootLayout() {
  return (
    <ContactProvider>
      <Stack>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="editContact" options={{ headerShown: false }} />
      </Stack>
    </ContactProvider>
  );
}
