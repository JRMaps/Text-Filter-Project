import { Tabs } from "expo-router";
import React from "react";
import { Image, StyleSheet, View } from "react-native";

import { HapticTab } from "@/components/haptic-tab";
import { useColorScheme } from "@/hooks/use-color-scheme";
import { Fonts } from "@/constants/theme";

const TabColors = {
  contacts: "#cd1127", // Red
  messages: "#0039a9", // Blue
  account: "#f6ca15", // Yellow
  inactive: "#666",
};

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <View style={styles.container}>
      <Tabs
        screenOptions={{
          tabBarInactiveTintColor: TabColors.inactive,
          headerShown: false,
          tabBarButton: HapticTab,
          tabBarStyle: {
            backgroundColor: "#fff",
            elevation: 8,

            shadowOffset: { width: 0, height: 0 },
            shadowOpacity: 0.25,
            shadowRadius: 10,
            height: 80,
            paddingBottom: 10,
            paddingTop: 12,
            marginHorizontal: 70,
            marginBottom: 35,
            borderRadius: 40,
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            justifyContent: "center",
            alignItems: "center",
          },
          tabBarLabelStyle: {
            fontSize: 14,
            marginTop: 8,
            fontWeight: "500",
            fontFamily: Fonts.regular,
          },
          tabBarItemStyle: {
            justifyContent: "center",
            alignItems: "center",
          },
        }}
      >
        <Tabs.Screen
          name="contacts"
          options={{
            title: "Contacts",
            tabBarActiveTintColor: TabColors.contacts,
            tabBarIcon: ({ focused }) => (
              <Image
                source={
                  focused
                    ? require("@/assets/images/contactsred.png")
                    : require("@/assets/images/contacts.png")
                }
                style={styles.tabIcon}
              />
            ),
          }}
        />
        <Tabs.Screen
          name="messages"
          options={{
            title: "Messages",
            tabBarActiveTintColor: TabColors.messages,
            tabBarIcon: ({ focused }) => (
              <Image
                source={
                  focused
                    ? require("@/assets/images/messagesblue.png")
                    : require("@/assets/images/messages.png")
                }
                style={styles.tabIcon}
              />
            ),
          }}
        />
        <Tabs.Screen
          name="account"
          options={{
            title: "Account",
            tabBarActiveTintColor: TabColors.account,
            tabBarIcon: ({ focused }) => (
              <Image
                source={
                  focused
                    ? require("@/assets/images/accountyellow.png")
                    : require("@/assets/images/account.png")
                }
                style={styles.tabIcon}
              />
            ),
          }}
        />
        {/* Hide the splash screen from tab bar */}
        <Tabs.Screen
          name="index"
          options={{
            href: null,
          }}
        />
      </Tabs>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  tabIcon: {
    width: 36,
    height: 36,
    resizeMode: "contain",
  },
});
