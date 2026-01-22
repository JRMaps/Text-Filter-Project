import React, { useEffect, useState, useRef } from "react";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Image,
  ActivityIndicator,
  Alert,
  Keyboard,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import api, { getToken } from "../services/api";
import { Fonts } from "@/constants/theme";

interface Message {
  id: string | number;
  content: string;
  sender_id: number;
  created_at: string;
}

const ChatScreen = () => {
  const router = useRouter();
  const params = useLocalSearchParams();

  // 1. Get Params (Handles both existing chat ID and new chat receiverID)
  const [conversationId, setConversationId] = useState<number | null>(
    params.id ? Number(params.id) : null,
  );
  const receiverId = params.receiverId ? Number(params.receiverId) : null;
  const chatName = (params.name as string) || "Chat";

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  const flatListRef = useRef<FlatList>(null);
  const ws = useRef<WebSocket | null>(null);

  // 2. Initial Setup: Get User ID & Load Messages
  useEffect(() => {
    const init = async () => {
      try {
        const idStr = await AsyncStorage.getItem("user_id");
        if (idStr) setCurrentUserId(Number(idStr));

        // Only fetch history if we have a conversation ID (not for new chats)
        if (conversationId) {
          const data = await api.conversations.getConversation(conversationId);
          if (data && data.messages) {
            setMessages(data.messages);
          }
        }
      } catch (error) {
        console.error("Failed to load chat:", error);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [conversationId]);

  // 3. WebSocket Connection (For receiving messages in real-time)
  useEffect(() => {
    if (!conversationId || !currentUserId) return;

    let socket: WebSocket;
    const connectWS = async () => {
      const token = await getToken();
      if (!token) return;

      // Adjust IP if needed
      const wsUrl = `ws://192.168.254.201:8000/ws/${conversationId}?token=${token}`;
      socket = new WebSocket(wsUrl);

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "new_message" && data.message) {
            // Append incoming message to list
            setMessages((prev) => {
              if (prev.some((m) => m.id === data.message.id)) return prev;
              return [...prev, data.message];
            });
            // Auto-scroll to bottom
            setTimeout(() => flatListRef.current?.scrollToEnd(), 100);
          }
        } catch (e) {
          console.log("WS Error", e);
        }
      };

      ws.current = socket;
    };

    connectWS();
    return () => {
      if (socket) socket.close();
    };
  }, [conversationId, currentUserId]);

  // 4. The "Send" Logic - Strict & Reliable
  const handleSend = async () => {
    if (!inputText.trim()) return;

    const content = inputText.trim();
    setInputText(""); // Clear input first
    setSending(true); // Show loading spinner on button

    try {
      // Call Backend
      const newMessage = await api.messages.sendMessage(
        content,
        conversationId || undefined, // undefined if null
        receiverId || undefined, // undefined if null
      );

      // Backend Success: Add message to list immediately so you see it
      setMessages((prev) => [...prev, newMessage]);

      // Auto-scroll
      setTimeout(() => flatListRef.current?.scrollToEnd(), 100);

      // If this was a "New Chat", save the ID so future messages work
      if (!conversationId && newMessage.conversation_id) {
        setConversationId(newMessage.conversation_id);
      }
    } catch (error: any) {
      console.error("Send Error:", error);
      // Alert user if Moderation Blocked or Error occurred
      Alert.alert("Failed to Send", error.message || "Something went wrong");
      // Restore text so user doesn't lose it
      setInputText(content);
    } finally {
      setSending(false);
    }
  };

  const renderItem = ({ item }: { item: Message }) => {
    const isMe = item.sender_id === currentUserId;
    return (
      <View
        style={[
          styles.messageBubble,
          isMe ? styles.myMessage : styles.otherMessage,
        ]}
      >
        <Text
          style={[styles.messageText, isMe ? styles.myText : styles.otherText]}
        >
          {item.content}
        </Text>
        <Text
          style={[styles.timeText, isMe ? styles.myTime : styles.otherTime]}
        >
          {new Date(item.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backButton}
        >
          <Image
            source={require("@/assets/images/returnButton.png")}
            style={styles.backIcon}
          />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Image
            source={require("@/assets/images/account.png")}
            style={styles.headerAvatar}
          />
          <Text style={styles.headerTitle}>{chatName}</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      {/* Messages List */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => String(item.id)}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        onContentSizeChange={() =>
          flatListRef.current?.scrollToEnd({ animated: true })
        }
        ListEmptyComponent={
          !loading ? (
            <Text style={{ textAlign: "center", color: "#999", marginTop: 20 }}>
              No messages yet. Say hi!
            </Text>
          ) : null
        }
      />

      {/* Input Area */}
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        keyboardVerticalOffset={Platform.OS === "ios" ? 10 : 0}
      >
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="Type a message..."
            value={inputText}
            onChangeText={setInputText}
            multiline
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              !inputText.trim() && styles.sendButtonDisabled,
            ]}
            onPress={handleSend}
            disabled={!inputText.trim() || sending}
          >
            {sending ? (
              <ActivityIndicator size="small" color="#FFF" />
            ) : (
              <Image
                source={require("@/assets/images/sendIcon.png")}
                style={styles.sendIcon}
              />
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F5" },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 15,
    backgroundColor: "#FFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E0E0E0",
  },
  backButton: { padding: 5 },
  backIcon: { width: 24, height: 24, resizeMode: "contain" },
  headerTitleContainer: { flexDirection: "row", alignItems: "center" },
  headerAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 8,
    backgroundColor: "#CCC",
  },
  headerTitle: { fontSize: 18, fontWeight: "600", fontFamily: Fonts.regular },
  listContent: { padding: 15, paddingBottom: 20 },
  messageBubble: {
    maxWidth: "80%",
    padding: 12,
    borderRadius: 20,
    marginBottom: 10,
  },
  myMessage: {
    alignSelf: "flex-end",
    backgroundColor: "#0039a9",
    borderBottomRightRadius: 2,
  },
  otherMessage: {
    alignSelf: "flex-start",
    backgroundColor: "#FFF",
    borderBottomLeftRadius: 2,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  messageText: { fontSize: 16, fontFamily: Fonts.regular },
  myText: { color: "#FFF" },
  otherText: { color: "#000" },
  timeText: {
    fontSize: 10,
    marginTop: 4,
    alignSelf: "flex-end",
    fontFamily: Fonts.regular,
  },
  myTime: { color: "rgba(255,255,255,0.7)" },
  otherTime: { color: "#999" },
  inputContainer: {
    flexDirection: "row",
    padding: 10,
    backgroundColor: "#FFF",
    alignItems: "center",
    borderTopWidth: 1,
    borderTopColor: "#E0E0E0",
  },
  input: {
    flex: 1,
    backgroundColor: "#F0F0F0",
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    maxHeight: 100,
    fontSize: 16,
    fontFamily: Fonts.regular,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "#0039a9",
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 10,
  },
  sendButtonDisabled: { backgroundColor: "#CCC" },
  sendIcon: { width: 20, height: 20, tintColor: "#FFF", resizeMode: "contain" },
});

export default ChatScreen;
