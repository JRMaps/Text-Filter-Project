import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, Image, StatusBar, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';

const RegisterScreen = () => {

  //Blueprint for form data
  interface FormData {
  emailOrNumber: string;
  backupEmail: string;
  backupNumber: string;
  username: string;
  password: string;
  confirmPassword: string;
  }

  //useState used to store form data
  const [formData, setFormData] = useState<FormData>({
    emailOrNumber: '',
    backupEmail: '',
    backupNumber: '',
    username: '',
    password: '',
    confirmPassword: '',
  });
  
  const router = useRouter();

  //Login Handler pero NOT YET CONNECTED sa BACKEND
  
  const handleRegister = async () => {
    // Check all required fields
    if (!formData.emailOrNumber || !formData.username || !formData.password || !formData.confirmPassword) {
      Alert.alert('Error', 'All required fields must be filled');
      return;
    }

    // Validate email or phone number
    const isEmail = formData.emailOrNumber.includes('@');
    const isValidEmail = isEmail && formData.emailOrNumber.includes('.') && formData.emailOrNumber.length > 5;
    const isValidPhone = !isEmail && formData.emailOrNumber.length == 11;
    
    if (!isValidEmail && !isValidPhone) {
      Alert.alert('Error', 'Invalid email or phone number');
      return;
    }

    // Check if passwords match
    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    // Check password length
    if (formData.password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    // Validate backup email if provided
    if (formData.backupEmail && !formData.backupEmail.includes('@')) {
      Alert.alert('Error', 'Invalid backup email');
      return;
    }

    // Validate backup number if provided
    if (formData.backupNumber && formData.backupNumber.length < 11) {
      Alert.alert('Error', 'Invalid backup phone number');
      return;
    }

    Alert.alert('Success', 'Register Successful');
    // Send to backend / Firebase / mock API
};

    return (
      <SafeAreaView style = {styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
        {/* Header Section */}
        <View>
          <Image source={require('../assets/images/FILTalk Header Logo.png')} accessibilityLabel="FILTalk" style={styles.headerLogo} /> 
        </View>
        {/*Register Section */}
        <Text style={styles.loginText}>Register</Text>
        
        <View style={styles.formSection}>

          <Text style={styles.labelText}>Email or Number</Text>
          <TextInput
            style={styles.inputField}
            value={formData.emailOrNumber}
            onChangeText={(text) => setFormData({ ...formData, emailOrNumber: text })} //text is passed as parameter papunta sa setFormData, which updates only the emailOrNumber field in the formData state
            placeholder="Email or Number"
            placeholderTextColor="#9E9E9E"
            keyboardType="email-address"
          />
          
          <Text style={styles.labelText}>Backup Email (optional)</Text>
          <TextInput
            style={styles.inputField}
            value={formData.backupEmail}
            onChangeText={(text) => setFormData({ ...formData, backupEmail: text })}
            placeholder="Backup Email"
            placeholderTextColor="#9E9E9E"
            keyboardType="email-address"
          />

          <Text style={styles.labelText}>Backup Phone Number (optional)</Text>
          <TextInput
            style={styles.inputField}
            value={formData.backupNumber}
            onChangeText={(text) => setFormData({ ...formData, backupNumber: text })}
            placeholder="Backup Phone Number"
            placeholderTextColor="#9E9E9E"
            keyboardType="phone-pad"
          />

          <Text style={styles.labelText}>Username</Text>
          <TextInput
            style={styles.inputField}
            value={formData.username}
            onChangeText={(text) => setFormData({ ...formData, username: text })} 
            placeholder="Username"
            placeholderTextColor="#9E9E9E"
          />

          <Text style={styles.labelText}>Password</Text>
          <TextInput
            style={styles.inputField}
            value={formData.password}
            onChangeText={(text) => setFormData({ ...formData, password: text })}
            placeholder="Password"
            placeholderTextColor="#9E9E9E"
            secureTextEntry
          />

          <Text style={styles.labelText}>Confirm Password</Text>
          <TextInput
            style={styles.inputField}
            value={formData.confirmPassword}
            onChangeText={(text) => setFormData({ ...formData, confirmPassword: text })}
            placeholder="Confirm Password"
            placeholderTextColor="#9E9E9E"
            secureTextEntry
          />
          
        </View>
        {/*Buttons Section */}
        <View>
          <TouchableOpacity style={[styles.buttonBase, styles.registerButton]} onPress={handleRegister}>
            <Text style={styles.buttonText}>Register</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.buttonBase, styles.cancelButton]} onPress={() => router.push('./')}>
            <Text style={styles.buttonText}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.loginAcc} onPress={() => router.push('./loginScreen')}>
            Already have an account?
          </Text>
        </View>
      </SafeAreaView>
    ); 
}

const styles = StyleSheet.create({
  headerLogo: {
    color: '#000000',
    width: 400,
    height: 160,
    resizeMode: 'contain',
    alignSelf: 'flex-start',
    marginTop:-30,
    marginBottom: -20,
  },
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingTop: 0,
  },
  formSection: {
    width: '100%',
    paddingHorizontal: 20,
    alignItems: 'flex-start',
  },
  inputField: {
    width: '100%',
    height: 42,
    borderWidth: 1,
    borderColor: '#C5C5C5',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 5,
    backgroundColor: '#fff',
  },
  loginText: {
    fontSize: 25,
    fontWeight: '900',
    textAlign: 'center',
    marginBottom: 20,
  },
  labelText: {
    color: '#545454',
    fontSize: 15,
    fontWeight: '900',
    textAlign: 'left',
    alignSelf: 'flex-start',
    marginBottom: 5,
  },
  buttonBase: {
    width: 250,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10,
    borderRadius: 8,
  },
  registerButton: {
    backgroundColor: '#0039a9',
    marginVertical: 8,
    marginTop: 20,
  },
  cancelButton: {
    backgroundColor: '#cd1127',
    marginVertical: 8,
    marginBottom: 30,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '900',
  },
  loginAcc: {
    fontSize: 15,
    fontWeight: '900',
    color: '#0039a9',
    alignSelf: 'center',
    marginBottom: 100,
    textDecorationLine: 'underline', 
  },
});

export default RegisterScreen;