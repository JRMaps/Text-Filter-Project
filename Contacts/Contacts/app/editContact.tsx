import React, { useState, useEffect } from 'react';
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
  TextInput,
  Alert,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useContact } from './ContactContext';

const EditContactScreen = () => {
  const router = useRouter();
  const { contactData: sharedContactData, updateContact } = useContact();
  
  const [contactData, setContactData] = useState(sharedContactData);

  useEffect(() => {
    setContactData(sharedContactData);
  }, [sharedContactData]);

  const pickImage = async () => {
    // Request permission
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (permissionResult.granted === false) {
      Alert.alert('Permission Required', 'Permission to access camera roll is required!');
      return;
    }

    // Launch image picker
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: 'images',
      allowsEditing: true,
      aspect: [1, 1],
      quality: 1,
    });

    if (!result.canceled) {
      setContactData({ ...contactData, avatar: result.assets[0].uri });
    }
  };

  const handleSave = () => {
    updateContact(contactData);
    console.log('Saving contact:', contactData);
    router.back();
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
      
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Image source={require('../assets/images/returnButton (1).png')} style={styles.backIcon} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Edit Contact</Text>
          <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveButtonText}>Save</Text>
          </TouchableOpacity>
        </View>

        {/* Profile Picture Section */}
        <View style={styles.profilePictureSection}>
          <TouchableOpacity style={styles.avatarContainer} onPress={pickImage}>
            <View style={styles.avatar}>
              {contactData.avatar ? (
                <Image source={{ uri: contactData.avatar }} style={styles.avatarImage} />
              ) : (
                <View style={styles.avatarIcon}>
                  <View style={styles.avatarHead} />
                  <View style={styles.avatarBody} />
                </View>
              )}
            </View>
            <View style={styles.editIconContainer}>
              <Text style={styles.editIconText}>📷</Text>
            </View>
          </TouchableOpacity>
          <Text style={styles.changePhotoText}>Tap to change photo</Text>
        </View>

        {/* Form Fields */}
        <View style={styles.formSection}>
          <View style={styles.formGroup}>
            <Text style={styles.label}>Name</Text>
            <TextInput
              style={styles.input}
              value={contactData.name}
              onChangeText={(text) => setContactData({ ...contactData, name: text })}
              placeholder="Enter name"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Mobile Number</Text>
            <TextInput
              style={styles.input}
              value={contactData.phone}
              onChangeText={(text) => setContactData({ ...contactData, phone: text })}
              placeholder="Enter phone number"
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Email</Text>
            <TextInput
              style={styles.input}
              value={contactData.email}
              onChangeText={(text) => setContactData({ ...contactData, email: text })}
              placeholder="Enter email"
              keyboardType="email-address"
              autoCapitalize="none"
            />
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
  headerTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#000',
  },
  saveButton: {
    backgroundColor: '#f6ca15',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0039a9',
  },
  profilePictureSection: {
    alignItems: 'center',
    paddingVertical: 30,
  },
  avatarContainer: {
    position: 'relative',
  },
  avatar: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  avatarImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  avatarIcon: {
    width: 100,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarHead: {
    width: 35,
    height: 35,
    borderRadius: 17.5,
    backgroundColor: '#FFF',
    marginBottom: 3,
  },
  avatarBody: {
    width: 60,
    height: 40,
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    backgroundColor: '#FFF',
  },
  editIconContainer: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#f6ca15',
    justifyContent: 'center',
    alignItems: 'center',
  },
  editIconText: {
    fontSize: 18,
  },
  changePhotoText: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
  },
  formSection: {
    paddingHorizontal: 20,
  },
  formGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '900',
    color: '#000',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#FFF',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#000',
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
});

export default EditContactScreen;
