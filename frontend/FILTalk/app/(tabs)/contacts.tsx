import React from "react";
import { useRouter, Href } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  FlatList,
  TouchableOpacity,
  Image,
} from "react-native";
import { useContact, ContactData } from "@/context/ContactContext";
import { Fonts } from "@/constants/theme";

const ContactsScreen = () => {
  const router = useRouter();
  const { contacts, setSelectedContact } = useContact();

  const handleContactPress = (contact: ContactData) => {
    setSelectedContact(contact);
    router.push("/contactProfile" as Href);
  };

  const renderContact = ({ item }: { item: ContactData }) => (
    <TouchableOpacity
      style={styles.contactItem}
      activeOpacity={0.7}
      onPress={() => handleContactPress(item)}
    >
      <View style={styles.avatar}>
        {item.avatar ? (
          <Image source={{ uri: item.avatar }} style={styles.avatarImageFull} />
        ) : (
          <Image
            source={require("@/assets/images/account.png")}
            style={styles.avatarImage}
          />
        )}
      </View>
      <View style={styles.contactInfo}>
        <Text style={styles.contactName}>{item.name}</Text>
        <Text
          style={[
            styles.contactStatus,
            item.status === "Online" && styles.onlineStatus,
          ]}
        >
          {item.lastSeen}
        </Text>
      </View>
      {item.status === "Online" && <View style={styles.onlineIndicator} />}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Contacts</Text>
        <TouchableOpacity style={styles.addButton}>
          <Text style={styles.addButtonText}>+</Text>
        </TouchableOpacity>
      </View>

      {/* Contacts List */}
      <FlatList
        data={contacts}
        renderItem={renderContact}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
      />
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
    fontFamily: Fonts.regular,
  },
  addButton: {
    backgroundColor: "#f6ca15",
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  addButtonText: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#000",
    marginTop: -2,
    fontFamily: Fonts.regular,
  },
  listContainer: {
    paddingHorizontal: 20,
  },
  contactItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 10,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: "#E8E8E8",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  avatarImage: {
    width: 30,
    height: 30,
    tintColor: "#666",
  },
  avatarImageFull: {
    width: "100%",
    height: "100%",
    borderRadius: 25,
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#000",
    marginBottom: 2,
    fontFamily: Fonts.regular,
  },
  contactStatus: {
    fontSize: 13,
    color: "#999",
    fontFamily: Fonts.regular,
  },
  onlineStatus: {
    color: "#4CAF50",
  },
  onlineIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: "#4CAF50",
  },
});

export default ContactsScreen;
