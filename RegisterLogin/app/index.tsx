import { useRouter } from 'expo-router';
import React from 'react';
import { Image, StatusBar, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';

const LoginRegisterScreen = () => {
    const router = useRouter();

    return (
      <SafeAreaView style = {styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

        {/* Main Logo Section */}
        <View> 
          <Image source={require('../assets/images/FILTalkMainLogo.png')} accessibilityLabel="FILTalk" style={styles.mainLogo} /> 
        </View>

        {/*Buttons Section */}
        <View>
          <TouchableOpacity style={[styles.buttonBase, styles.loginButton]} onPress={() => router.push('./loginScreen')}>
            <Text style={styles.buttonText}>Login</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.buttonBase, styles.registerButton]} onPress={() => console.log('Register Pressed')}>
            <Text style={styles.buttonText}>Register</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    ); 
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingTop: 100,
  },
  mainLogo: {
    width: 400,
    height: 400,
    resizeMode: 'contain',
    alignSelf: 'center',
    marginBottom: -50,
  },
  buttonBase: {
    width: 250,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10,
    borderRadius: 8,
  },
  loginButton: {
    backgroundColor: '#0039a9',
    marginVertical: 8,
  },
  registerButton: {
    backgroundColor: '#cd1127',
    marginVertical: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '900',
  },
});

export default LoginRegisterScreen;