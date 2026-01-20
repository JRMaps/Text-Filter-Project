import React from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  FlatList,
  TouchableOpacity,
  Image,
  TextInput,
  ScrollView,
  Keyboard,
  TouchableWithoutFeedback,
} from "react-native";
import { Fonts } from "@/constants/theme";

// Sample online contacts data
const onlineContacts = [
  { id: "1", name: "Juan Dela Cruz" },
  { id: "2", name: "Pedro Garcia" },
  { id: "3", name: "Carlos Mendoza" },
  { id: "4", name: "Sia Antoriano" },
  { id: "5", name: "Celebes Dimautang" },
];

// Sample messages data - will be replaced with backend data
const sampleMessages = [
  {
    id: "1",
    name: "Juan Dela Cruz",
    lastMessage: "Kamusta ka na?",
    time: "2:30 PM",
    unread: 2,
  },
  {
    id: "2",
    name: "Maria Santos",
    lastMessage: "Sige, see you tomorrow!",
    time: "1:15 PM",
    unread: 0,
  },
  {
    id: "3",
    name: "Pedro Garcia",
    lastMessage: "Okay lang, salamat!",
    time: "11:45 AM",
    unread: 5,
  },
  {
    id: "4",
    name: "Ana Reyes",
    lastMessage: "Nagtext ka ba kanina?",
    time: "Yesterday",
    unread: 0,
  },
  {
    id: "5",
    name: "Carlos Mendoza",
    lastMessage: "Ingat palagi!",
    time: "Yesterday",
    unread: 1,
  },
];

const MessagesScreen = () => {
  const renderMessage = ({ item }: { item: (typeof sampleMessages)[0] }) => (
    <TouchableOpacity style={styles.messageItem} activeOpacity={0.7}>
      <View style={styles.avatar}>
        <Image
          source={require("@/assets/images/account.png")}
          style={styles.avatarImage}
        />
      </View>
      <View style={styles.messageInfo}>
        <View style={styles.messageHeader}>
          <Text style={styles.messageName}>{item.name}</Text>
          <Text style={styles.messageTime}>{item.time}</Text>
        </View>
        <View style={styles.messagePreview}>
          <Text
            style={[
              styles.lastMessage,
              item.unread > 0 && styles.unreadMessage,
            ]}
            numberOfLines={1}
          >
            {item.lastMessage}
          </Text>
          {item.unread > 0 && (
            <View style={styles.unreadBadge}>
              <Text style={styles.unreadCount}>{item.unread}</Text>
            </View>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

        {/* Header */}
        <View style={styles.header}>
          <Image
            source={require("@/assets/images/FILTalktext.png")}
            style={styles.headerLogo}
          />
          <TouchableOpacity style={styles.composeButton}>
            <Image
              source={require("@/assets/images/MessagesNewChatIcon.png")}
              style={styles.composeIcon}
            />
          </TouchableOpacity>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <View style={styles.searchBar}>
            <Image
              source={require("@/assets/images/Search.png")}
              style={styles.searchIcon}
            />
            <TextInput
              style={styles.searchInput}
              placeholder="Search Conversation or People"
              placeholderTextColor="#999"
            />
          </View>
        </View>

        {/* Online Contacts */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.onlineContactsContainer}
          contentContainerStyle={styles.onlineContactsContent}
        >
          {onlineContacts.map((contact) => (
            <TouchableOpacity key={contact.id} style={styles.onlineContact}>
              <View style={styles.onlineAvatarContainer}>
                <View style={styles.onlineAvatar}>
                  <Image
                    source={require("@/assets/images/account.png")}
                    style={styles.onlineAvatarImage}
                  />
                </View>
                <View style={styles.onlineIndicator} />
              </View>
              <Text style={styles.onlineContactName} numberOfLines={2}>
                {contact.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Messages List */}
        <FlatList
          data={sampleMessages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        />
      </SafeAreaView>
    </TouchableWithoutFeedback>
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
    paddingBottom: 10,
    marginLeft: 10,
  },
  headerLogo: {
    width: 130,
    height: 44,
    resizeMode: "contain",
  },
  searchContainer: {
    paddingHorizontal: 20,
    marginBottom: 15,
  },
  searchBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 25,
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  searchIcon: {
    width: 24,
    height: 24,
    tintColor: "#666",
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 22,
    color: "#333",
    fontFamily: Fonts.regular,
  },
  onlineContactsContainer: {
    maxHeight: 120,
    marginBottom: -20,
  },
  onlineContactsContent: {
    paddingHorizontal: 20,
    gap: 15,
  },
  onlineContact: {
    alignItems: "center",
    width: 70,
  },
  onlineAvatarContainer: {
    position: "relative",
    marginBottom: 5,
  },
  onlineAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "#000",
    justifyContent: "center",
    alignItems: "center",
  },
  onlineAvatarImage: {
    width: 30,
    height: 40,
    tintColor: "#fff",
  },
  onlineIndicator: {
    position: "absolute",
    bottom: 2,
    right: 2,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: "#4CD964",
    borderWidth: 2,
    borderColor: "#F5F5F5",
  },
  onlineContactName: {
    fontSize: 12,
    color: "#333",
    textAlign: "center",
    fontFamily: Fonts.regular,
  },
  composeButton: {
    justifyContent: "center",
    alignItems: "center",
  },
  composeIcon: {
    width: 40,
    height: 40,
    resizeMode: "contain",
  },
  listContainer: {
    paddingHorizontal: 20,
  },
  messageItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 10,
  },
  avatar: {
    width: 55,
    height: 55,
    borderRadius: 27.5,
    backgroundColor: "#E8E8E8",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  avatarImage: {
    width: 26,
    height: 34,
    tintColor: "#666",
  },
  messageInfo: {
    flex: 1,
  },
  messageHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  messageName: {
    fontSize: 22,
    fontWeight: "600",
    color: "#000",
    fontFamily: Fonts.regular,
  },
  messageTime: {
    fontSize: 18,
    color: "#999",
    fontFamily: Fonts.regular,
  },
  messagePreview: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  lastMessage: {
    fontSize: 16,
    color: "#666",
    flex: 1,
    marginRight: 10,
    fontFamily: Fonts.regular,
  },
  unreadMessage: {
    fontWeight: "600",
    color: "#000",
    fontFamily: Fonts.regular,
  },
  unreadBadge: {
    backgroundColor: "#f6ca15",
    minWidth: 22,
    height: 22,
    borderRadius: 11,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 6,
  },
  unreadCount: {
    fontSize: 12,
    fontWeight: "bold",
    color: "#000",
    fontFamily: Fonts.regular,
  },
});

export default MessagesScreen;
