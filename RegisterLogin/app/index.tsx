import React, { useState } from 'react';
import { Image, Text, View, StyleSheet, TouchableOpacity, ScrollView, StatusBar } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';

const LoginRegisterScreen = () => {

    return (
      <SafeAreaView style = {styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

        {/* Main Logo Section */}
        <View> 
          <Image source={require('../assets/images/FILTalkMainLogo.png')} accessibilityLabel="FILTalk" style={styles.mainLogo} /> 
        </View>

        {/*Buttons Section */}
        <View  >
          <TouchableOpacity style={styles.loginButton} onPress={() => console.log('Login Pressed')}>
            <Text style={styles.buttonText}>Login</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.registerButton} onPress={() => console.log('Register Pressed')}>
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
    justifyContent: 'center',
    marginBottom: -50,
  },
  loginButton: {
    backgroundColor: '#0039a9',
    width: 250,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10,
    marginVertical: 8,
    marginHorizontal: 15,
    borderRadius: 8,
  },
  registerButton: {
    backgroundColor: '#cd1127',
    width: 250,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 8,
    marginHorizontal: 10,
    margin: 15,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontFamily: 'Bernoru',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default LoginRegisterScreen;