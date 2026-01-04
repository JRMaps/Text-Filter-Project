import { Tabs } from 'expo-router';
import React from 'react';
import { Image, StyleSheet } from 'react-native';

import { HapticTab } from '@/components/haptic-tab';
import { useColorScheme } from '@/hooks/use-color-scheme';

// FILTalk brand colors
const FILTalkColors = {
  primary: '#f6ca15', // Yellow accent
  inactive: '#666',
  background: '#F5F5F5',
};

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: FILTalkColors.primary,
        tabBarInactiveTintColor: FILTalkColors.inactive,
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 0,
          elevation: 8,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.1,
          shadowRadius: 8,
          height: 65,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
      }}>
      <Tabs.Screen
        name="contacts"
        options={{
          title: 'Contacts',
          tabBarIcon: ({ color }) => (
            <Image 
              source={require('@/assets/images/contacts.png')} 
              style={[styles.tabIcon, { tintColor: color }]} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="messages"
        options={{
          title: 'Messages',
          tabBarIcon: ({ color }) => (
            <Image 
              source={require('@/assets/images/messages.png')} 
              style={[styles.tabIcon, { tintColor: color }]} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="account"
        options={{
          title: 'Account',
          tabBarIcon: ({ color }) => (
            <Image 
              source={require('@/assets/images/account.png')} 
              style={[styles.tabIcon, { tintColor: color }]} 
            />
          ),
        }}
      />
      {/* Hide the splash screen from tab bar */}
      <Tabs.Screen
        name="index"
        options={{
          href: null,
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabIcon: {
    width: 24,
    height: 24,
    resizeMode: 'contain',
  },
});
