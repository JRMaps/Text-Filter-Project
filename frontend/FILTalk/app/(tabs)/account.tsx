import React, { useState } from "react";
import { useRouter, Href } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  ScrollView,
  Image,
} from "react-native";

const AccountScreen = () => {
  const router = useRouter();

  // User profile state - will be populated by backend API
  const [userProfile] = useState({
    name: "Lorem ipsum dolor",
    email: "lorem@gmail.com",
    phone: "09231734621",
  });

  const settingsMenuItems = [
    {
      id: "settings",
      icon: require("@/assets/images/settings.png"),
      label: "Settings",
    },
  ];

  const menuItems = [
    {
      id: "language",
      icon: require("@/assets/images/language.png"),
      label: "Language",
    },
    { id: "theme", icon: require("@/assets/images/theme.png"), label: "Theme" },
    {
      id: "notifs",
      icon: require("@/assets/images/notifs.png"),
      label: "Notifications and Sounds",
    },
    {
      id: "privacy",
      icon: require("@/assets/images/privacy.png"),
      label: "Privacy",
    },
  ];

  const handleLogout = () => {
    // Clear auth state and navigate to login
    router.replace("/(auth)" as Href);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Account</Text>
          <TouchableOpacity
            style={styles.editButton}
            onPress={() => router.push("/edit" as Href)}
          >
            <Text style={styles.editButtonText}>Edit</Text>
          </TouchableOpacity>
        </View>

        {/* Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.avatar}>
            <View style={styles.avatarIcon}>
              <View style={styles.avatarHead} />
              <View style={styles.avatarBody} />
            </View>
          </View>
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{userProfile.name}</Text>
            <Text style={styles.profileEmail}>{userProfile.email}</Text>
            <Text style={styles.profilePhone}>{userProfile.phone}</Text>
          </View>
        </View>

        {/* Settings Card */}
        <View style={styles.settingsCard}>
          {settingsMenuItems.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={styles.menuItem}
              activeOpacity={0.7}
            >
              <Image source={item.icon} style={styles.menuIcon} />
              <Text style={styles.menuLabel}>{item.label}</Text>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Menu Items Card */}
        <View style={styles.menuCard}>
          {menuItems.map((item, index) => (
            <TouchableOpacity
              key={item.id}
              style={[
                styles.menuItem,
                index < menuItems.length - 1 && styles.menuItemBorder,
              ]}
              activeOpacity={0.7}
            >
              <Image
                source={item.icon}
                style={
                  item.label === "Privacy"
                    ? styles.menuIconLarge
                    : styles.menuIcon
                }
              />
              <Text style={styles.menuLabel}>{item.label}</Text>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>

        {/* Spacer for bottom */}
        <View style={styles.bottomSpacer} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 15,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#f6ca15",
  },
  editButton: {
    backgroundColor: "#f6ca15",
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
  },
  editButtonText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#000",
  },
  profileSection: {
    flexDirection: "row",
    paddingHorizontal: 20,
    paddingVertical: 20,
    alignItems: "center",
  },
  avatar: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "#000",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 15,
  },
  avatarIcon: {
    width: 80,
    height: 80,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarHead: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: "#FFF",
    marginBottom: 2,
  },
  avatarBody: {
    width: 48,
    height: 32,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    backgroundColor: "#FFF",
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#000",
    marginBottom: 4,
  },
  profileEmail: {
    fontSize: 14,
    color: "#999",
    marginBottom: 2,
  },
  profilePhone: {
    fontSize: 14,
    color: "#999",
  },
  settingsCard: {
    backgroundColor: "#eeeded",
    marginHorizontal: 20,
    borderRadius: 12,
    marginBottom: 15,
  },
  menuCard: {
    backgroundColor: "#eeeded",
    marginHorizontal: 20,
    borderRadius: 12,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 16,
    paddingHorizontal: 16,
  },
  menuItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: "#D0D0D0",
  },
  menuIcon: {
    width: 20,
    height: 20,
    marginRight: 12,
    resizeMode: "contain",
  },
  menuIconLarge: {
    width: 28,
    height: 28,
    marginRight: 12,
    resizeMode: "contain",
  },
  menuLabel: {
    flex: 1,
    fontSize: 16,
    fontWeight: "500",
    color: "#000",
  },
  chevron: {
    fontSize: 28,
    color: "#666",
    fontWeight: "300",
  },
  logoutButton: {
    backgroundColor: "#cd1127",
    marginHorizontal: 20,
    marginTop: 20,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  logoutButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  bottomSpacer: {
    height: 40,
  },
});

export default AccountScreen;
