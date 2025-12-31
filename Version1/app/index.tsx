import React, { useState } from 'react';
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

const AccountScreen = () => {
  const router = useRouter();
  
  // User profile state - will be populated by backend API
  const [userProfile, setUserProfile] = useState({
    name: 'Lorem ipsum dolor', 
    email: 'lorem@gmail.com', 
    phone: '09231734621' 
  });


  const settingsMenuItems = [
    { icon: require('../assets/images/settings.png'), label: 'Settings' },
  ];

  const menuItems = [
    { icon: require('../assets/images/language.png'), label: 'Language' },
    { icon: require('../assets/images/theme.png'), label: 'Theme' },
    { icon: require('../assets/images/notifs.png'), label: 'Notifications and Sounds' },
    { icon: require('../assets/images/privacy.png'), label: 'Privacy' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
      
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Account</Text>
          <TouchableOpacity style={styles.editButton} onPress={() => router.push('/edit')}>
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

            {/* Placeholder - replace with REAL data */}
            <Text style={styles.profileName}>{userProfile.name}</Text>
            <Text style={styles.profileEmail}>{userProfile.email}</Text> 
            <Text style={styles.profilePhone}>{userProfile.phone}</Text>
          </View>
        </View>

        {/* Settings Card */}
        <View style={styles.settingsCard}>
          {settingsMenuItems.map((item, index) => (
            <TouchableOpacity 
              key={index} 
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
              key={index} 
              style={[
                styles.menuItem,
                index < menuItems.length - 1 && styles.menuItemBorder
              ]}
              activeOpacity={0.7}
            >
              <Image source={item.icon} style={item.label === 'Privacy' ? styles.menuIconLarge : styles.menuIcon} />
              <Text style={styles.menuLabel}>{item.label}</Text>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Spacer for bottom navigation */}
        <View style={styles.bottomSpacer} />
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <View style={styles.bottomNavContainer}>
          <TouchableOpacity style={styles.navItem} activeOpacity={0.7}>
            <View style={styles.navIconContainer}>
              <Image source={require('../assets/images/contacts.png')} style={styles.navIcon} />
            </View>
            <Text style={styles.navLabel}>Contacts</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.navItem} activeOpacity={0.7}>
            <View style={styles.navIconContainer}>
              <Image source={require('../assets/images/messages.png')} style={styles.navIcon} />
            </View>
            <Text style={styles.navLabel}>Messages</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.navItem} activeOpacity={0.7}>
            <View style={styles.navIconContainer}>
              <Image source={require('../assets/images/account.png')} style={styles.navIconLarge} />
            </View>
            <Text style={[styles.navLabel, styles.navLabelActive]}>Account</Text>
          </TouchableOpacity>
        </View>
      </View>
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
  },
  editButton: {
    backgroundColor: '#f6ca15',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
  },
  editButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  profileSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 20,
    alignItems: 'center',
  },
  avatar: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  avatarIcon: {
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarHead: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#FFF',
    marginBottom: 2,
  },
  avatarBody: {
    width: 48,
    height: 32,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    backgroundColor: '#FFF',
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 4,
  },
  profileEmail: {
    fontSize: 14,
    color: '#999',
    marginBottom: 2,
  },
  profilePhone: {
    fontSize: 14,
    color: '#999',
  },
  settingsCard: {
    backgroundColor: '#eeeded',
    marginHorizontal: 20,
    borderRadius: 12,
    marginBottom: 15,
  },
  menuCard: {
    backgroundColor: '#eeeded',
    marginHorizontal: 20,
    borderRadius: 12,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
  },
  menuItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#D0D0D0',
  },
  menuIcon: {
    width: 20,
    height: 20,
    marginRight: 12,
    resizeMode: 'contain',
  },
  menuIconLarge: {
    width: 28,
    height: 28,
    marginRight: 12,
    resizeMode: 'contain',
  },
  menuLabel: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
  },
  chevron: {
    fontSize: 28,
    color: '#666',
    fontWeight: '300',
  },
  bottomSpacer: {
    height: 100,
  },
  bottomNav: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingBottom: 20,
    paddingTop: 10,
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  bottomNavContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 30,
    paddingVertical: 12,
    paddingHorizontal: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
  navItem: {
    alignItems: 'center',
    marginHorizontal: 20,
  },
  navIconContainer: {
    marginBottom: 4,
  },
  navIcon: {
    width: 24,
    height: 24,
    resizeMode: 'contain',
  },
  navIconLarge: {
    width: 26,
    height: 26,
    resizeMode: 'contain',
  },
  navLabel: {
    fontSize: 12,
    color: '#666',
  },
  navLabelActive: {
    color: '#f6ca15',
    fontWeight: '600',
  },
});

export default AccountScreen;