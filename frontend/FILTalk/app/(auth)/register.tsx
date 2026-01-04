import { useRouter } from "expo-router";
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
  ScrollView,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const RegisterScreen = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const router = useRouter();

  const handleRegister = async () => {
    if (!name || !email || !phone || !password || !confirmPassword) {
      Alert.alert("Error", "All fields are required");
      return;
    }

    if (!email.includes("@")) {
      Alert.alert("Error", "Please enter a valid email address");
      return;
    }

    if (phone.length < 10) {
      Alert.alert("Error", "Please enter a valid phone number");
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert("Error", "Passwords do not match");
      return;
    }

    if (password.length < 6) {
      Alert.alert("Error", "Password must be at least 6 characters");
      return;
    }

    // TODO: Implement actual registration with backend
    Alert.alert("Success", "Registration Successful! Please login.", [
      { text: "OK", onPress: () => router.replace("./login") },
    ]);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Header Section */}
        <View>
          <Image
            source={require("@/assets/images/FILTalk Header Logo.png")}
            accessibilityLabel="FILTalk"
            style={styles.headerLogo}
          />
        </View>

        {/* Register Section */}
        <Text style={styles.registerText}>Create Account</Text>

        <View style={styles.formSection}>
          <Text style={styles.labelText}>Full Name</Text>
          <TextInput
            style={styles.inputField}
            value={name}
            onChangeText={setName}
            placeholder="Enter your full name"
            placeholderTextColor="#9E9E9E"
          />

          <Text style={styles.labelText}>Email</Text>
          <TextInput
            style={styles.inputField}
            value={email}
            onChangeText={setEmail}
            placeholder="Enter your email"
            placeholderTextColor="#9E9E9E"
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <Text style={styles.labelText}>Phone Number</Text>
          <TextInput
            style={styles.inputField}
            value={phone}
            onChangeText={setPhone}
            placeholder="Enter your phone number"
            placeholderTextColor="#9E9E9E"
            keyboardType="phone-pad"
          />

          <Text style={styles.labelText}>Password</Text>
          <TextInput
            style={styles.inputField}
            value={password}
            onChangeText={setPassword}
            placeholder="Enter password"
            placeholderTextColor="#9E9E9E"
            secureTextEntry
          />

          <Text style={styles.labelText}>Confirm Password</Text>
          <TextInput
            style={styles.inputField}
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder="Confirm your password"
            placeholderTextColor="#9E9E9E"
            secureTextEntry
          />
        </View>

        {/* Buttons Section */}
        <View style={styles.buttonSection}>
          <TouchableOpacity
            style={[styles.buttonBase, styles.registerButton]}
            onPress={handleRegister}
          >
            <Text style={styles.buttonText}>Register</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.buttonBase, styles.cancelButton]}
            onPress={() => router.back()}
          >
            <Text style={styles.buttonText}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.loginLink} onPress={() => router.push("./login")}>
            Already have an account? Login
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  headerLogo: {
    color: "#000000",
    width: 400,
    height: 140,
    resizeMode: "contain",
    alignSelf: "center",
    marginTop: -20,
    marginBottom: 0,
  },
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  scrollContent: {
    alignItems: "center",
    paddingBottom: 40,
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
    marginBottom: 15,
    backgroundColor: "#fff",
  },
  registerText: {
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
    marginBottom: 8,
  },
  buttonSection: {
    alignItems: "center",
    marginTop: 20,
  },
  buttonBase: {
    width: 250,
    height: 50,
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
    borderRadius: 8,
  },
  registerButton: {
    backgroundColor: "#0039a9",
    marginVertical: 8,
  },
  cancelButton: {
    backgroundColor: "#cd1127",
    marginVertical: 8,
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "900",
  },
  loginLink: {
    fontSize: 15,
    fontWeight: "900",
    color: "#0039a9",
    alignSelf: "center",
    marginTop: 20,
    textDecorationLine: "underline",
  },
});

export default RegisterScreen;
