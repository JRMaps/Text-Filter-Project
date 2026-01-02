import { Stack } from "expo-router";

export default function RootLayout() {
  return <Stack>
    <Stack.Screen
      name="index"
      options={{ headerShown: false }}
    />
    <Stack.Screen
      name="loginScreen"
      options={{ 
        headerShown:false,
        title: '',
        headerBackVisible: false,
       }}
    />
  </Stack>;
}
