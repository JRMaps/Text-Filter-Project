import React from 'react';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  ScrollView,
  Image,
} from 'react-native';
import { useContact } from './ContactContext';

const ContactsAccScreen = () => {
  const router = useRouter();
  const { contactData } = useContact();
  const contactsProfileData = contactData;

  const profileItems = [
    { icon: require('../assets/images/phoneIcon.png'), label: 'Call' },
    { icon: require('../assets/images/messageIcon.png'), label: 'Messages' },
    { icon: require('../assets/images/videoIcon.png'), label: 'Video' },
    { icon: require('../assets/images/emailIcon.png'), label: 'Email' },
    { icon: require('../assets/images/moreIcon.png'), label: 'More' }, 
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
      
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          {/* Back Button na hindi pa connected sa CONTACTS paconnect nalanggzzz wala siya sakin e*/}
          <TouchableOpacity style={styles.backButton} onPress={() => console.log('Back pressed')}>
            <Image source={require('../assets/images/returnButton (1).png')} style={styles.backIcon} />
          </TouchableOpacity>

          <TouchableOpacity style={styles.editButton} onPress={() => router.push('/editContact')}>
            <Text style={styles.editButtonText}>Edit</Text>
          </TouchableOpacity>
        </View>

        {/* Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.avatar}>
            {contactsProfileData.avatar ? (
              <Image source={{ uri: contactsProfileData.avatar }} style={styles.avatarImage} />
            ) : (
              <View style={styles.avatarIcon}>
                <View style={styles.avatarHead} />
                <View style={styles.avatarBody} />
              </View>
            )}
          </View>
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{contactsProfileData.name}</Text>
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
            <Text style={styles.detailValue}>{contactsProfileData.phone}</Text>
          </View>
          <View style={styles.detailDivider} />
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Email</Text>
            <Text style={styles.detailValue}>{contactsProfileData.email}</Text>
          </View>
        </View>
      </ScrollView>
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
  backButton: {
    padding: 8,
  },
  backIcon: {
    width: 24,
    height: 24,
    resizeMode: 'contain',
  },
  editButton: {
    backgroundColor: '#f6ca15',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
  },
  editButtonText: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0039a9',
  },
  profileSection: {
    flexDirection: 'column',
    paddingHorizontal: 20,
    paddingVertical: 20,
    alignItems: 'center',
    marginBottom: -20,
  },
  avatar: {
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
    overflow: 'hidden',
    marginBottom: 40,
  },
  avatarImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  avatarIcon: {
    width: 200,
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarHead: {
    width: 76,
    height: 76,
    borderRadius: 56,
    backgroundColor: '#FFF',
    marginBottom: 2,
  },
  avatarBody: {
    width: 58,
    height: 52,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    backgroundColor: '#FFF',
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 48,
    fontWeight: '900',
    color: '#000',
    textAlign: 'center',
    marginBottom: 2,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    paddingVertical: 20,
    marginBottom: 10,
  },
  actionButton: {
    alignItems: 'center',
    flex: 1,
  },
  actionIconContainer: {
    width: 62,
    height: 62,
    borderRadius: 8,
    backgroundColor: '#E8E8E8',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  actionIcon: {
    width: 24,
    height: 24,
    resizeMode: 'contain',
  },
  actionLabel: {
    fontSize: 12,
    color: '#000',
    fontWeight: '800',
    
  },
  detailsCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    borderRadius: 12,
    paddingVertical: 8,
    shadowColor: '#000',
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
    backgroundColor: '#E8E8E8',
    marginHorizontal: 16,
  },
  detailLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 15,
    color: '#666',
  },
});

export default ContactsAccScreen;