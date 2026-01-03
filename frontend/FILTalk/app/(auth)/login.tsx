import { useRouter, Href } from "expo-router";
import React, { useState } from "react";
import {
  Alert,
  Image,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const LoginScreen = () => {
  const [emailOrNumber, setEmailOrNumber] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleLogin = async () => {
    if (!emailOrNumber.includes("@") && emailOrNumber.length < 10) {
      Alert.alert("Error", "Invalid email or phone number");
      return;
    } else if (!emailOrNumber || !password) {
      Alert.alert("Error", "All fields are required");
      return;
    }

    // Implement actual authentication with backend
    Alert.alert("Success", "Login Successful", [
      { text: "OK", onPress: () => router.replace("/(tabs)" as Href) },
    ]);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

      {/* Header Section */}
      <View>
        <Image
          source={require("@/assets/images/FILTalk Header Logo.png")}
          accessibilityLabel="FILTalk"
          style={styles.headerLogo}
        />
      </View>

      {/* Login Section */}
      <Text style={styles.loginText}>Login</Text>

      <View style={styles.formSection}>
        <Text style={styles.labelText}>Email or Number</Text>
        <TextInput
          style={styles.inputField}
          value={emailOrNumber}
          onChangeText={setEmailOrNumber}
          placeholder="Email or Number"
          placeholderTextColor="#9E9E9E"
          keyboardType="email-address"
        />
        <Text style={styles.labelText}>Password</Text>
        <TextInput
          style={styles.inputField}
          value={password}
          onChangeText={setPassword}
          placeholder="Password"
          placeholderTextColor="#9E9E9E"
          secureTextEntry
        />
        <Text
          style={styles.forgotPass}
          onPress={() => console.log("Forgot password pressed")}
        >
          Forgot Password?
        </Text>
      </View>

      {/* Buttons Section */}
      <View>
        <TouchableOpacity
          style={[styles.buttonBase, styles.loginButton]}
          onPress={handleLogin}
        >
          <Text style={styles.buttonText}>Login</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.buttonBase, styles.cancelButton]}
          onPress={() => router.back()}
        >
          <Text style={styles.buttonText}>Cancel</Text>
        </TouchableOpacity>
        <Text
          style={styles.createAcc}
          onPress={() => router.push("./register")}
        >
          Create Account
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  headerLogo: {
    color: "#000000",
    width: 400,
    height: 160,
    resizeMode: "contain",
    alignSelf: "flex-start",
    marginTop: -30,
    marginBottom: 0,
  },
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
    justifyContent: "flex-start",
    alignItems: "center",
    paddingTop: 0,
  },
  formSection: {
    width: "100%",
    paddingHorizontal: 20,
    alignItems: "flex-start",
  },
  inputField: {
    width: "100%",
    height: 44,
    borderWidth: 1,
    borderColor: "#C5C5C5",
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 20,
    backgroundColor: "#fff",
  },
  loginText: {
    fontSize: 25,
    fontWeight: "900",
    textAlign: "center",
    marginBottom: 20,
  },
  labelText: {
    color: "#545454",
    fontSize: 15,
    fontWeight: "900",
    textAlign: "left",
    alignSelf: "flex-start",
    marginBottom: 15,
  },
  forgotPass: {
    fontSize: 12,
    fontWeight: "900",
    color: "#0039a9",
    textAlign: "left",
    alignSelf: "flex-start",
    marginBottom: 50,
    textDecorationLine: "underline",
  },
  buttonBase: {
    width: 250,
    height: 50,
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
    borderRadius: 8,
  },
  loginButton: {
    backgroundColor: "#0039a9",
    marginVertical: 8,
  },
  cancelButton: {
    backgroundColor: "#cd1127",
    marginVertical: 8,
    marginBottom: 80,
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "900",
  },
  createAcc: {
    fontSize: 15,
    fontWeight: "900",
    color: "#0039a9",
    alignSelf: "center",
    marginBottom: 100,
    textDecorationLine: "underline",
  },
});

export default LoginScreen;
