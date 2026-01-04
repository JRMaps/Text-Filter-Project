import React from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  FlatList,
  TouchableOpacity,
  Image,
} from 'react-native';
import { Fonts } from '@/constants/theme';

// Sample messages data - will be replaced with backend data
const sampleMessages = [
  { 
    id: '1', 
    name: 'Juan Dela Cruz', 
    lastMessage: 'Kamusta ka na?', 
    time: '2:30 PM',
    unread: 2,
  },
  { 
    id: '2', 
    name: 'Maria Santos', 
    lastMessage: 'Sige, see you tomorrow!', 
    time: '1:15 PM',
    unread: 0,
  },
  { 
    id: '3', 
    name: 'Pedro Garcia', 
    lastMessage: 'Okay lang, salamat!', 
    time: '11:45 AM',
    unread: 5,
  },
  { 
    id: '4', 
    name: 'Ana Reyes', 
    lastMessage: 'Nagtext ka ba kanina?', 
    time: 'Yesterday',
    unread: 0,
  },
  { 
    id: '5', 
    name: 'Carlos Mendoza', 
    lastMessage: 'Ingat palagi!', 
    time: 'Yesterday',
    unread: 1,
  },
];

const MessagesScreen = () => {
  const renderMessage = ({ item }: { item: typeof sampleMessages[0] }) => (
    <TouchableOpacity style={styles.messageItem} activeOpacity={0.7}>
      <View style={styles.avatar}>
        <Image 
          source={require('@/assets/images/account.png')} 
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
            style={[styles.lastMessage, item.unread > 0 && styles.unreadMessage]} 
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
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Messages</Text>
        <TouchableOpacity style={styles.composeButton}>
          <Image 
            source={require('@/assets/images/messages.png')} 
            style={styles.composeIcon} 
          />
        </TouchableOpacity>
      </View>

      {/* Messages List */}
      <FlatList
        data={sampleMessages}
        renderItem={renderMessage}
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
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 15,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#f6ca15',
    fontFamily: Fonts.regular,
  },
  composeButton: {
    backgroundColor: '#f6ca15',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  composeIcon: {
    width: 22,
    height: 22,
    tintColor: '#000',
  },
  listContainer: {
    paddingHorizontal: 20,
  },
  messageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 10,
  },
  avatar: {
    width: 55,
    height: 55,
    borderRadius: 27.5,
    backgroundColor: '#E8E8E8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarImage: {
    width: 32,
    height: 32,
    tintColor: '#666',
  },
  messageInfo: {
    flex: 1,
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  messageName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    fontFamily: Fonts.regular,
  },
  messageTime: {
    fontSize: 12,
    color: '#999',
    fontFamily: Fonts.regular,
  },
  messagePreview: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  lastMessage: {
    fontSize: 14,
    color: '#666',
    flex: 1,
    marginRight: 10,
    fontFamily: Fonts.regular,
  },
  unreadMessage: {
    fontWeight: '600',
    color: '#000',
    fontFamily: Fonts.regular,
  },
  unreadBadge: {
    backgroundColor: '#f6ca15',
    minWidth: 22,
    height: 22,
    borderRadius: 11,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  unreadCount: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#000',
    fontFamily: Fonts.regular,
  },
});

export default MessagesScreen;
