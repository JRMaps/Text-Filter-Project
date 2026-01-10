import { useRouter, Href } from "expo-router";
import React, { useState } from "react";
import {
  Alert,
  Image,
  Keyboard,
  ScrollView,
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

const RecoveryScreen = () => {
  const [selectedTab, setSelectedTab] = useState<"email" | "mobile">("email");
  const [emailInput, setEmailInput] = useState("");
  const [mobileInput, setMobileInput] = useState("");
  const router = useRouter();

  const handleEnter = async () => {
    if (selectedTab === "email") {
      if (!emailInput || !emailInput.includes("@")) {
        Alert.alert("Error", "Please enter a valid email address");
        return;
      }
      // email
      Alert.alert("Success", "Recovery link sent to your email");
      router.push("/passwordCode");
    } else {
      if (!mobileInput || mobileInput.length < 10) {
        Alert.alert("Error", "Please enter a valid mobile number");
        return;
      }
      // mobile
      Alert.alert("Success", "Recovery link sent to your mobile");
      router.push("/passwordCode");
    }
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <SafeAreaView style={styles.container}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

          {/* Title */}
          <Text style={styles.titleText}>Password Recovery</Text>

          {/* Tab Toggle */}
          <View style={styles.tabContainer}>
            <TouchableOpacity
              style={[
                styles.tabButton,
                selectedTab === "email" && styles.tabButtonActive,
              ]}
              onPress={() => setSelectedTab("email")}
            >
              <Text
                style={[
                  styles.tabText,
                  selectedTab === "email" && styles.tabTextActive,
                ]}
              >
                Email
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.tabButton,
                selectedTab === "mobile" && styles.tabButtonActive,
              ]}
              onPress={() => setSelectedTab("mobile")}
            >
              <Text
                style={[
                  styles.tabText,
                  selectedTab === "mobile" && styles.tabTextActive,
                ]}
              >
                Mobile No.
              </Text>
            </TouchableOpacity>
          </View>

          {/* Instruction Text */}
          <Text style={styles.instructionText}>
            {selectedTab === "email"
              ? "Please ENTER your email address below."
              : "Please ENTER your mobile number below."}
          </Text>

          {/* Input Section */}
          <View style={styles.formSection}>
            <Text style={styles.labelText}>
              {selectedTab === "email" ? "Email Address" : "Mobile Number"}
            </Text>
            <TextInput
              style={styles.inputField}
              value={selectedTab === "email" ? emailInput : mobileInput}
              onChangeText={
                selectedTab === "email" ? setEmailInput : setMobileInput
              }
              placeholder=""
              placeholderTextColor="#9E9E9E"
              keyboardType={selectedTab === "email" ? "email-address" : "phone-pad"}
            />
          </View>

          {/* Buttons Section */}
          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={[styles.buttonBase, styles.enterButton]}
              onPress={handleEnter}
            >
              <Text style={styles.buttonText}>Enter</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.buttonBase, styles.cancelButton]}
              onPress={handleCancel}
            >
              <Text style={styles.buttonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
  },
  scrollContent: {
    flexGrow: 1,
    alignItems: "center",
    paddingTop: 60,
    paddingHorizontal: 30,
  },
  titleText: {
    fontSize: 32,
    fontWeight: "900",
    textAlign: "center",
    marginBottom: 40,
    fontFamily: Fonts.regular,
    color: "#000000",
  },
  tabContainer: {
    flexDirection: "row",
    backgroundColor: "#E8E8E8",
    borderRadius: 25,
    padding: 4,
    marginBottom: 30,
    width: "80%",
  },
  tabButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    alignItems: "center",
  },
  tabButtonActive: {
    backgroundColor: "#FFC107",
  },
  tabText: {
    fontSize: 16,
    fontWeight: "700",
    color: "#666666",
    fontFamily: Fonts.regular,
  },
  tabTextActive: {
    color: "#000000",
  },
  instructionText: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 30,
    fontFamily: Fonts.regular,
    color: "#333333",
  },
  formSection: {
    width: "100%",
    alignItems: "flex-start",
    marginBottom: 40,
  },
  labelText: {
    color: "#333333",
    fontSize: 16,
    fontWeight: "700",
    textAlign: "left",
    alignSelf: "flex-start",
    marginBottom: 10,
    fontFamily: Fonts.regular,
  },
  inputField: {
    width: "100%",
    height: 50,
    borderWidth: 1,
    borderColor: "#C5C5C5",
    borderRadius: 8,
    paddingHorizontal: 15,
    backgroundColor: "#FFFFFF",
    fontFamily: Fonts.regular,
    fontSize: 16,
  },
  buttonContainer: {
    width: "100%",
    alignItems: "center",
  },
  buttonBase: {
    width: "70%",
    height: 50,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 8,
    marginVertical: 8,
  },
  enterButton: {
    backgroundColor: "#0039a9",
  },
  cancelButton: {
    backgroundColor: "#cd1127",
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 22,
    fontWeight: "900",
    fontFamily: Fonts.regular,
  },
});

export default RecoveryScreen;