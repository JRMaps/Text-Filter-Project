import { useRouter, Href } from "expo-router";
import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Keyboard,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  TouchableWithoutFeedback,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Fonts } from "@/constants/theme";
import { authApi } from "@/services/api";

const LoginScreen = () => {
  const [emailOrNumber, setEmailOrNumber] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    if (!emailOrNumber.includes("@") && emailOrNumber.length < 10) {
      Alert.alert("Error", "Invalid email or phone number");
      return;
    } else if (!emailOrNumber || !password) {
      Alert.alert("Error", "All fields are required");
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Re-enable backend API call when ready
      // Determine if input is email or phone number
      // const isEmail = emailOrNumber.includes("@");
      // const loginData = isEmail
      //   ? { email: emailOrNumber, password }
      //   : { phone_number: emailOrNumber, password };
      // await authApi.login(loginData);

      // Temporary: Skip API call for UI testing
      await new Promise((resolve) => setTimeout(resolve, 500)); // Fake delay

      // Navigate immediately after successful login
      router.replace("/(tabs)/messages" as Href);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Login failed";
      Alert.alert("Error", message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <View style={styles.scrollContent}>
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
            <TouchableOpacity
              onPress={() => router.push("../passwordRecovery")}
            >
              <Text style={styles.forgotPass}>Forgot Password?</Text>
            </TouchableOpacity>
          </View>

          {/* Buttons Section */}
          <View>
            <TouchableOpacity
              style={[styles.buttonBase, styles.loginButton]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Login</Text>
              )}
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
        </View>
      </TouchableWithoutFeedback>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  headerLogo: {
    color: "#000000",
    width: 350,
    height: 160,
    resizeMode: "contain",
    alignSelf: "flex-start",
    marginTop: -30,
    marginBottom: 35,
  },
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  scrollContent: {
    flexGrow: 1,
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
    fontFamily: Fonts.regular,
    fontSize: 18,
  },
  loginText: {
    fontSize: 35,
    fontWeight: "900",
    textAlign: "center",
    marginTop: -40,
    marginBottom: 70,
    fontFamily: Fonts.regular,
  },
  labelText: {
    color: "#545454",
    fontSize: 21,
    fontWeight: "900",
    textAlign: "left",
    alignSelf: "flex-start",
    marginBottom: 15,
    fontFamily: Fonts.regular,
  },
  forgotPass: {
    fontSize: 16,
    fontWeight: "900",
    color: "#0039a9",
    textAlign: "left",
    alignSelf: "flex-start",
    marginBottom: 50,
    textDecorationLine: "underline",
    fontFamily: Fonts.regular,
  },
  buttonBase: {
    width: 180,
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
    fontSize: 28,
    fontWeight: "900",
    fontFamily: Fonts.regular,
  },
  createAcc: {
    fontSize: 20,
    fontWeight: "900",
    color: "#0039a9",
    alignSelf: "center",
    marginBottom: 100,
    marginLeft: 5,
    textDecorationLine: "underline",
    fontFamily: Fonts.regular,
  },
});

export default LoginScreen;
