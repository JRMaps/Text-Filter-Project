import React, { useState, useRef } from "react";
import { useRouter, useLocalSearchParams } from "expo-router";
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
  KeyboardAvoidingView,
  Platform,
  Keyboard,
} from "react-native";
import { Fonts } from "@/constants/theme";

interface Message {
  id: string;
  text: string;
  isSent: boolean;
  timestamp: string;
}

// Sample chat messages - will be replaced with backend data
const sampleChatMessages: Message[] = [
  { id: "1", text: "Hey! How are you?", isSent: true, timestamp: "12:00 PM" },
  { id: "2", text: "I'm good, thanks!", isSent: false, timestamp: "12:01 PM" },
  { id: "3", text: "What about you?", isSent: false, timestamp: "12:01 PM" },
  {
    id: "4",
    text: "I'm doing great! Just finished my project.",
    isSent: true,
    timestamp: "12:05 PM",
  },
  { id: "5", text: "That's awesome!", isSent: false, timestamp: "12:06 PM" },
  {
    id: "6",
    text: "We should celebrate!",
    isSent: false,
    timestamp: "12:06 PM",
  },
  {
    id: "7",
    text: "Yeah, let's grab some food later",
    isSent: true,
    timestamp: "12:10 PM",
  },
  { id: "8", text: "Sounds good to me!", isSent: true, timestamp: "12:10 PM" },
];

const ChatScreen = () => {
  const router = useRouter();
  const params = useLocalSearchParams();
  const { name, status } = params;

  const [messages, setMessages] = useState<Message[]>(sampleChatMessages);
  const [inputText, setInputText] = useState("");
  const flatListRef = useRef<FlatList>(null);

  const handleSend = () => {
    if (inputText.trim()) {
      const newMessage: Message = {
        id: Date.now().toString(),
        text: inputText.trim(),
        isSent: true,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages([...messages, newMessage]);
      setInputText("");
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View
      style={[
        styles.messageBubbleContainer,
        item.isSent ? styles.sentContainer : styles.receivedContainer,
      ]}
    >
      <View
        style={[
          styles.messageBubble,
          item.isSent ? styles.sentBubble : styles.receivedBubble,
        ]}
      >
        <Text
          style={[
            styles.messageText,
            item.isSent ? styles.sentText : styles.receivedText,
          ]}
        >
          {item.text}
        </Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={["top", "bottom"]}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Text style={styles.backArrow}>‹</Text>
        </TouchableOpacity>

        <View style={styles.headerInfo}>
          <Text style={styles.headerName}>{name || "Contact"}</Text>
          <View style={styles.statusContainer}>
            <View style={styles.onlineDot} />
            <Text style={styles.headerStatus}>Seen Message recently</Text>
          </View>
        </View>

        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.headerButton}>
            <Image
              source={require("@/assets/images/phoneIcon.png")}
              style={styles.headerIcon}
            />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton}>
            <Image
              source={require("@/assets/images/videoIcon.png")}
              style={styles.headerIcon}
            />
          </TouchableOpacity>
          <TouchableOpacity style={styles.moreButton}>
            <Image
              source={require("@/assets/images/moreIcon.png")}
              style={styles.moreIcon}
            />
          </TouchableOpacity>
        </View>
      </View>

      {/* Chat Messages */}
      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messagesList}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({ animated: false })
          }
        />

        {/* Input Area */}
        <View style={styles.inputContainer}>
          <TouchableOpacity style={styles.addButton}>
            <Text style={styles.addButtonText}>+</Text>
          </TouchableOpacity>

          <View style={styles.inputWrapper}>
            <TextInput
              style={styles.textInput}
              placeholder="Message..."
              placeholderTextColor="#999"
              value={inputText}
              onChangeText={setInputText}
              multiline
              onSubmitEditing={handleSend}
            />
            <View style={styles.inputActions}>
              <TouchableOpacity style={styles.inputAction}>
                <Image
                  source={require("@/assets/images/emojiicon.png")}
                  style={styles.inputActionIcon}
                />
              </TouchableOpacity>
              <TouchableOpacity style={styles.inputAction}>
                <Image
                  source={require("@/assets/images/imageicon.png")}
                  style={styles.inputActionIcon}
                />
              </TouchableOpacity>
            </View>
          </View>

          <TouchableOpacity style={styles.micButton} onPress={handleSend}>
            <Image
              source={require("@/assets/images/micicon.png")}
              style={styles.micIcon}
            />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
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
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 5,
    backgroundColor: "#F5F5F5",
    borderBottomWidth: 1,
    borderBottomColor: "#E0E0E0",
  },
  backButton: {
    padding: 5,
  },
  backArrow: {
    fontSize: 36,
    color: "#000",
    fontWeight: "300",
  },
  headerInfo: {
    flex: 1,
    marginLeft: 5,
  },
  headerName: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#000",
    fontFamily: Fonts.regular,
  },
  statusContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#4CD964",
    marginRight: 5,
  },
  headerStatus: {
    fontSize: 12,
    color: "#4CD964",
    fontFamily: Fonts.regular,
  },
  headerActions: {
    flexDirection: "row",
    alignItems: "center",
  },
  headerButton: {
    padding: 8,
  },
  headerIcon: {
    width: 24,
    height: 24,
    tintColor: "#0039a9",
    resizeMode: "contain",
  },
  moreButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: "#0039a9",
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 5,
  },
  moreIcon: {
    width: 16,
    height: 16,
    tintColor: "#0039a9",
    resizeMode: "contain",
  },
  chatContainer: {
    flex: 1,
  },
  messagesList: {
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  messageBubbleContainer: {
    marginVertical: 3,
  },
  sentContainer: {
    alignItems: "flex-end",
  },
  receivedContainer: {
    alignItems: "flex-start",
  },
  messageBubble: {
    maxWidth: "75%",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  sentBubble: {
    backgroundColor: "#0039a9",
    borderBottomRightRadius: 5,
  },
  receivedBubble: {
    backgroundColor: "#E8E8E8",
    borderBottomLeftRadius: 5,
  },
  messageText: {
    fontSize: 16,
    fontFamily: Fonts.regular,
  },
  sentText: {
    color: "#fff",
  },
  receivedText: {
    color: "#000",
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 8,
    backgroundColor: "#F5F5F5",
    borderTopWidth: 1,
    borderTopColor: "#E0E0E0",
  },
  addButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "#cd1127",
    justifyContent: "center",
    alignItems: "center",
  },
  addButtonText: {
    fontSize: 24,
    color: "#fff",
    fontWeight: "300",
    marginTop: -2,
  },
  inputWrapper: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 25,
    marginHorizontal: 10,
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: "#333",
    maxHeight: 100,
    fontFamily: Fonts.regular,
  },
  inputActions: {
    flexDirection: "row",
    alignItems: "center",
  },
  inputAction: {
    marginLeft: 8,
  },
  inputActionIcon: {
    width: 24,
    height: 24,
    resizeMode: "contain",
  },
  micButton: {
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
  },
  micIcon: {
    width: 40,
    height: 40,
    resizeMode: "contain",
  },
});

export default ChatScreen;
