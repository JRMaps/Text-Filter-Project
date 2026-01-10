import { useRouter } from 'expo-router';
import React, { useRef, useState } from 'react';
import { Alert, StatusBar, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';
import { Fonts } from '@/constants/theme';

const CodeScreen = () => {

  const [codeDigits, setCodeDigits] = useState(Array(6).fill(''));
  const inputRefs = useRef<(TextInput | null)[]>([]);
  const router = useRouter();

  //Authentication Handler pero NOT YET CONNECTED sa BACKEND
  const handleAuth = async () => {
    const code = codeDigits.join('');
    if (code.length !== 6) {
      Alert.alert('Error', 'Please enter all 6 digits');
      return;
    }

    Alert.alert('Success', 'Authentication Successful'); // EDIT EDIT
    //Send to backend
    router.push('./');
};

    return (
      <SafeAreaView style = {styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />
        
        {/*Authentication Section */}
        <View>
            <Text style={styles.authText}>Password Recovery</Text>
            <Text style={styles.desc}>A verification code has been sent to your registered email. Please enter it below.</Text>
        </View>
        
        <View style={styles.authSection}>
          {Array.from({ length: 6 }).map((_, index) => (
            <TextInput
              key={index} //key prop for list rendering
              style={styles.inputField}
              value={codeDigits[index]}
              onChangeText={(text) => {
                const newDigits = [...codeDigits];
                newDigits[index] = text.slice(-1); //allow 1 digit
                setCodeDigits(newDigits);
                
                //auto focus next field if digit entered
                if (text.length > 0 && index < 5) {
                    (inputRefs.current[index + 1])?.focus();
                }
              }}

              onKeyPress={({ nativeEvent }) => {
                // Go back to previous field on backspace if current field is empty
                if (nativeEvent.key === 'Backspace' && !codeDigits[index] && index > 0) {
                  inputRefs.current[index - 1]?.focus();
                }
                
              }}
              ref={(num) => {inputRefs.current[index] = num;}} //reference to each input field HAPPENS BEFORE ANYTHING ELSE

              placeholder={String(" ")}
              //placeholderTextColor="#9E9E9E" - just in case you guys want to put a number as placeholder
              keyboardType="number-pad"
              maxLength={1}
            />
          ))}
        </View>
        
        {/*Buttons Section */}
        <View>
          <TouchableOpacity style={[styles.buttonBase, styles.enterButton]} onPress={handleAuth}>
            <Text style={styles.buttonText}>Enter</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.buttonBase, styles.cancelButton]} onPress={() => router.push('./')}>
            <Text style={styles.buttonText}>Cancel</Text>
          </TouchableOpacity>
          <View style={{flexDirection: 'row', justifyContent: 'center', marginTop: 10}}>
            <Text style={styles.codeText}>Didn't receive a code?</Text>
            <Text style={styles.resendText} onPress={() => Alert.alert('Resend code pressed')}>
                Resend Code
            </Text>
          </View>
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
    paddingTop: 0,
  },
  authText: {
    fontSize: 35,
    fontWeight: '900',
    textAlign: 'center',
    marginTop: 40,
    marginBottom: 20,
    fontFamily: Fonts.regular,
  },
    desc: {
    fontSize: 20,
    color: '#000000',
    textAlign: 'center',
    marginTop: 50,
    marginBottom: 30,
    paddingHorizontal: 20,
    fontFamily: Fonts.regular,
    },
  authSection: {
    width: '100%',
    paddingHorizontal: 10,
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 80,
  },
  inputField: {
    width: 50,
    height: 84,
    borderWidth: 1,
    borderColor: '#C5C5C5',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginRight: 10,
    marginBottom: 20,
    textAlign: 'center',
    fontSize: 24,
    fontWeight: '600',
    color: '#000000',
    backgroundColor: '#fff',
    fontFamily: Fonts.regular,
  },
  codeText: { 
    fontSize: 15,
    fontStyle: 'italic',
    color: '#000000',
    marginTop: 20,
    fontFamily: Fonts.regular,
  },
  resendText: {
    fontSize: 15,
    color: '#0039a9',
    marginLeft: 5,
    textDecorationLine: 'underline', 
    marginTop: 20,
    fontFamily: Fonts.regular,
  },
  buttonBase: {
    width: 250,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10,
    borderRadius: 8,
  },
  enterButton: {
    backgroundColor: '#0039a9',
    marginVertical: 8,
  },
  cancelButton: {
    backgroundColor: '#cd1127',
    marginVertical: 8,
    marginBottom: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 28,
    fontWeight: '900',
    fontFamily: Fonts.regular,
  },
});

export default CodeScreen;