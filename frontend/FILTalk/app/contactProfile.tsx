import React, { useEffect, useState } from "react";
import { useRouter, useLocalSearchParams, Href } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  ScrollView,
  Image,
  ActivityIndicator,
  Alert,
} from "react-native";
import { Fonts } from "@/constants/theme";
import api from "../services/api";

const ContactProfileScreen = () => {
  const router = useRouter();
  const params = useLocalSearchParams();

  // Get ID from navigation params
  const contactId = params.id ? Number(params.id) : null;
  const initialName = params.name as string;

  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // 1. Fetch Contact Details on Mount
  useEffect(() => {
    let isMounted = true;

    const fetchDetails = async () => {
      if (!contactId) {
        setLoading(false);
        return;
      }

      try {
        // FIXED: Uses api.users.getById (which we added to api.ts)
        const data = await api.users.getById(contactId);
        if (isMounted) {
          setProfile(data);
        }
      } catch (error) {
        console.error("Failed to load contact profile", error);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchDetails();

    return () => {
      isMounted = false;
    };
  }, [contactId]);

  // 2. Handle "Message" Button Press
  const handleMessage = async () => {
    if (!contactId) return;

    // FIX: Instead of calling a non-existent API, navigate with receiverId.
    // The backend will create the chat automatically when the first message is sent.
    router.push({
      pathname: "/chat",
      params: {
        name: profile?.username || initialName || "Chat",
        receiverId: contactId, // Passes the contact's ID to the ChatScreen
      },
    } as Href);
  };

  const profileItems = [
    {
      icon: require("@/assets/images/phoneIcon.png"),
      label: "Call",
      action: () => Alert.alert("Call", "Calling feature coming soon!"),
    },
    {
      icon: require("@/assets/images/messageIcon.png"),
      label: "Messages",
      action: handleMessage,
    },
    {
      icon: require("@/assets/images/videoIcon.png"),
      label: "Video",
      action: () => {},
    },
    {
      icon: require("@/assets/images/emailIcon.png"),
      label: "Email",
      action: () => {},
    },
    {
      icon: require("@/assets/images/moreIcon.png"),
      label: "More",
      action: () => {},
    },
  ];

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { justifyContent: "center" }]}>
        <ActivityIndicator size="large" color="#0039a9" />
      </SafeAreaView>
    );
  }

  const displayName = profile?.username || initialName || "Unknown";
  const displayPhone = profile?.phone_number || "No phone number";
  const displayEmail = profile?.email || "No email address";

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Image
              source={require("@/assets/images/returnButton.png")}
              style={styles.backIcon}
            />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.editButton}
            onPress={() => router.push("/editContact" as Href)}
          >
            <Text style={styles.editButtonText}>Edit</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.profileSection}>
          <View style={styles.avatar}>
            <Image
              source={require("@/assets/images/account.png")}
              style={styles.defaultAvatarIcon}
            />
          </View>
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{displayName}</Text>
            <Text
              style={[
                styles.statusText,
                profile?.active_status && styles.onlineStatus,
              ]}
            >
              {profile?.active_status ? "Online" : "Offline"}
            </Text>
          </View>
        </View>

        <View style={styles.actionButtons}>
          {profileItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.actionButton}
              onPress={item.action}
            >
              <View style={styles.actionIconContainer}>
                <Image source={item.icon} style={styles.actionIcon} />
                <Text style={styles.actionLabel}>{item.label}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.detailsCard}>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Mobile Number</Text>
            <Text style={styles.detailValue}>{displayPhone}</Text>
          </View>
          <View style={styles.detailDivider} />
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Email</Text>
            <Text style={styles.detailValue}>{displayEmail}</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F5" },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 15,
  },
  backButton: { padding: 8 },
  backIcon: { width: 28, height: 28, resizeMode: "contain" },
  editButton: {
    backgroundColor: "#f6ca15",
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
  },
  editButtonText: {
    fontSize: 24,
    fontWeight: "900",
    color: "#0039a9",
    fontFamily: Fonts.regular,
  },
  profileSection: {
    flexDirection: "column",
    paddingHorizontal: 20,
    paddingVertical: 20,
    alignItems: "center",
    marginBottom: -20,
  },
  avatar: {
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: "#000",
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden",
    marginTop: -10,
    marginBottom: 40,
  },
  defaultAvatarIcon: {
    width: 125,
    height: 125,
    resizeMode: "contain",
    tintColor: "#FFF",
  },
  profileInfo: { alignItems: "center" },
  profileName: {
    fontSize: 52,
    fontWeight: "900",
    color: "#000",
    textAlign: "center",
    marginBottom: 10,
    marginTop: -20,
    fontFamily: Fonts.regular,
  },
  statusText: {
    fontSize: 20,
    marginTop: -4,
    marginBottom: 10,
    color: "#666",
    fontFamily: Fonts.regular,
  },
  onlineStatus: { color: "#4CAF50" },
  actionButtons: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingHorizontal: 20,
    paddingVertical: 20,
    marginBottom: 10,
  },
  actionButton: { alignItems: "center", flex: 1 },
  actionIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 8,
    backgroundColor: "#E8E8E8",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 6,
  },
  actionIcon: { width: 32, height: 32, resizeMode: "contain" },
  actionLabel: {
    fontSize: 15,
    color: "#000",
    fontWeight: "800",
    fontFamily: Fonts.regular,
    marginTop: 8,
  },
  detailsCard: {
    backgroundColor: "#FFF",
    marginHorizontal: 20,
    borderRadius: 12,
    paddingVertical: 8,
  },
  detailItem: { paddingVertical: 12, paddingHorizontal: 16 },
  detailDivider: {
    height: 1,
    backgroundColor: "#E8E8E8",
    marginHorizontal: 16,
  },
  detailLabel: {
    fontSize: 20,
    fontWeight: "600",
    color: "#000",
    marginBottom: 4,
    fontFamily: Fonts.regular,
  },
  detailValue: { fontSize: 18, color: "#666", fontFamily: Fonts.regular },
});

export default ContactProfileScreen;
