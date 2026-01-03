import React from "react";
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
import { useContact } from "@/context/ContactContext";

const ContactProfileScreen = () => {
  const router = useRouter();
  const { selectedContact } = useContact();

  // If no contact is selected, go back
  if (!selectedContact) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No contact selected</Text>
          <TouchableOpacity
            style={styles.backButtonEmpty}
            onPress={() => router.back()}
          >
            <Text style={styles.backButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const profileItems = [
    { icon: require("@/assets/images/phoneIcon.png"), label: "Call" },
    { icon: require("@/assets/images/messageIcon.png"), label: "Messages" },
    { icon: require("@/assets/images/videoIcon.png"), label: "Video" },
    { icon: require("@/assets/images/emailIcon.png"), label: "Email" },
    { icon: require("@/assets/images/moreIcon.png"), label: "More" },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
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

        {/* Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.avatar}>
            {selectedContact.avatar ? (
              <Image
                source={{ uri: selectedContact.avatar }}
                style={styles.avatarImage}
              />
            ) : (
              <View style={styles.avatarIcon}>
                <View style={styles.avatarHead} />
                <View style={styles.avatarBody} />
              </View>
            )}
          </View>
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{selectedContact.name}</Text>
            {selectedContact.status && (
              <Text
                style={[
                  styles.statusText,
                  selectedContact.status === "Online" && styles.onlineStatus,
                ]}
              >
                {selectedContact.lastSeen || selectedContact.status}
              </Text>
            )}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          {profileItems.map((item, index) => (
            <TouchableOpacity key={index} style={styles.actionButton}>
              <View style={styles.actionIconContainer}>
                <Image source={item.icon} style={styles.actionIcon} />
                <Text style={styles.actionLabel}>{item.label}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Contact Details Card */}
        <View style={styles.detailsCard}>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Mobile Number</Text>
            <Text style={styles.detailValue}>{selectedContact.phone}</Text>
          </View>
          <View style={styles.detailDivider} />
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Email</Text>
            <Text style={styles.detailValue}>{selectedContact.email}</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  emptyState: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: 18,
    color: "#666",
    marginBottom: 20,
  },
  backButtonEmpty: {
    backgroundColor: "#f6ca15",
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#000",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 15,
  },
  backButton: {
    padding: 8,
  },
  backIcon: {
    width: 24,
    height: 24,
    resizeMode: "contain",
  },
  editButton: {
    backgroundColor: "#f6ca15",
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
  },
  editButtonText: {
    fontSize: 16,
    fontWeight: "900",
    color: "#0039a9",
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
    marginRight: 15,
    overflow: "hidden",
    marginBottom: 40,
  },
  avatarImage: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
  avatarIcon: {
    width: 200,
    height: 200,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarHead: {
    width: 76,
    height: 76,
    borderRadius: 56,
    backgroundColor: "#FFF",
    marginBottom: 2,
  },
  avatarBody: {
    width: 58,
    height: 52,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    backgroundColor: "#FFF",
  },
  profileInfo: {
    alignItems: "center",
  },
  profileName: {
    fontSize: 36,
    fontWeight: "900",
    color: "#000",
    textAlign: "center",
    marginBottom: 4,
  },
  statusText: {
    fontSize: 14,
    color: "#666",
  },
  onlineStatus: {
    color: "#4CAF50",
  },
  actionButtons: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingHorizontal: 20,
    paddingVertical: 20,
    marginBottom: 10,
  },
  actionButton: {
    alignItems: "center",
    flex: 1,
  },
  actionIconContainer: {
    width: 62,
    height: 62,
    borderRadius: 8,
    backgroundColor: "#E8E8E8",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 6,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  actionIcon: {
    width: 24,
    height: 24,
    resizeMode: "contain",
  },
  actionLabel: {
    fontSize: 12,
    color: "#000",
    fontWeight: "800",
  },
  detailsCard: {
    backgroundColor: "#FFF",
    marginHorizontal: 20,
    borderRadius: 12,
    paddingVertical: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  detailItem: {
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  detailDivider: {
    height: 1,
    backgroundColor: "#E8E8E8",
    marginHorizontal: 16,
  },
  detailLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#000",
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 15,
    color: "#666",
  },
});

export default ContactProfileScreen;
