import React, { useState, useRef, useMemo, useCallback } from "react";
import { useRouter, Href } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  SectionList,
  SectionListData,
  TouchableOpacity,
  Image,
  TextInput,
  Keyboard,
  TouchableWithoutFeedback,
  PanResponder,
  GestureResponderEvent,
  LayoutChangeEvent,
} from "react-native";
import { useContact, ContactData } from "@/context/ContactContext";
import { Fonts } from "@/constants/theme";

type ContactSection = {
  title: string;
  data: ContactData[];
};

const ALPHABET = [
  "A",
  "B",
  "C",
  "D",
  "E",
  "F",
  "G",
  "H",
  "I",
  "J",
  "K",
  "L",
  "M",
  "N",
  "Ñ",
  "O",
  "P",
  "Q",
  "R",
  "S",
  "T",
  "U",
  "V",
  "W",
  "X",
  "Y",
  "Z",
];

const ContactsScreen = () => {
  const router = useRouter();
  const { contacts, setSelectedContact } = useContact();
  const [searchQuery, setSearchQuery] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeLetter, setActiveLetter] = useState<string | null>(null);
  const [showLetterIndicator, setShowLetterIndicator] = useState(false);
  const sectionListRef = useRef<SectionList<ContactData, ContactSection>>(null);
  const alphabetSidebarRef = useRef<View>(null);
  const sidebarLayout = useRef({ y: 0, height: 0 });

  const handleContactPress = (contact: ContactData) => {
    setSelectedContact(contact);
    router.push("/contactProfile" as Href);
  };

  // Filter contacts based on search query
  const filteredContacts = useMemo(() => {
    if (!searchQuery.trim()) return contacts;
    return contacts.filter((contact) =>
      contact.name.toLowerCase().includes(searchQuery.toLowerCase()),
    );
  }, [contacts, searchQuery]);

  // Group contacts by first letter
  const groupedContacts = useMemo(() => {
    const groups: { [key: string]: ContactData[] } = {};

    filteredContacts.forEach((contact) => {
      const firstLetter = contact.name.charAt(0).toUpperCase();
      if (!groups[firstLetter]) {
        groups[firstLetter] = [];
      }
      groups[firstLetter].push(contact);
    });

    // Sort contacts within each group
    Object.keys(groups).forEach((key) => {
      groups[key].sort((a, b) => a.name.localeCompare(b.name));
    });

    // Convert to SectionList format and sort by letter
    return Object.keys(groups)
      .sort((a, b) => a.localeCompare(b))
      .map((letter) => ({
        title: letter,
        data: groups[letter],
      }));
  }, [filteredContacts]);

  // Get available letters for the sidebar
  const availableLetters = useMemo(() => {
    return groupedContacts.map((section) => section.title);
  }, [groupedContacts]);

  const scrollToSection = useCallback(
    (letter: string) => {
      const sectionIndex = groupedContacts.findIndex(
        (section) => section.title === letter,
      );
      if (sectionIndex !== -1 && sectionListRef.current) {
        sectionListRef.current.scrollToLocation({
          sectionIndex,
          itemIndex: 0,
          animated: true,
          viewOffset: 0,
        });
      }
    },
    [groupedContacts],
  );

  const getLetterFromTouch = useCallback((pageY: number) => {
    const { y, height } = sidebarLayout.current;
    const relativeY = pageY - y;
    const letterHeight = height / ALPHABET.length;
    const index = Math.floor(relativeY / letterHeight);
    if (index >= 0 && index < ALPHABET.length) {
      return ALPHABET[index];
    }
    return null;
  }, []);

  const handleSidebarTouch = useCallback(
    (pageY: number) => {
      const letter = getLetterFromTouch(pageY);
      if (letter && letter !== activeLetter) {
        setActiveLetter(letter);
        if (availableLetters.includes(letter)) {
          scrollToSection(letter);
        }
      }
    },
    [getLetterFromTouch, activeLetter, availableLetters, scrollToSection],
  );

  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onMoveShouldSetPanResponder: () => true,
        onPanResponderGrant: (evt: GestureResponderEvent) => {
          setShowLetterIndicator(true);
          handleSidebarTouch(evt.nativeEvent.pageY);
        },
        onPanResponderMove: (evt: GestureResponderEvent) => {
          handleSidebarTouch(evt.nativeEvent.pageY);
        },
        onPanResponderRelease: () => {
          setShowLetterIndicator(false);
          setActiveLetter(null);
        },
        onPanResponderTerminate: () => {
          setShowLetterIndicator(false);
          setActiveLetter(null);
        },
      }),
    [handleSidebarTouch],
  );

  const onSidebarLayout = useCallback((event: LayoutChangeEvent) => {
    const { height } = event.nativeEvent.layout;
    alphabetSidebarRef.current?.measureInWindow((x, y) => {
      sidebarLayout.current = { y, height };
    });
  }, []);

  const renderContact = ({ item }: { item: ContactData }) => (
    <TouchableOpacity
      style={styles.contactItem}
      activeOpacity={0.7}
      onPress={() => handleContactPress(item)}
    >
      <View style={styles.avatar}>
        {item.avatar ? (
          <Image source={{ uri: item.avatar }} style={styles.avatarImageFull} />
        ) : (
          <Image
            source={require("@/assets/images/account.png")}
            style={styles.avatarImage}
          />
        )}
      </View>
      <View style={styles.contactInfo}>
        <Text style={styles.contactName}>{item.name}</Text>
        <Text
          style={[
            styles.contactStatus,
            item.status === "Online" && styles.onlineStatus,
          ]}
        >
          {item.lastSeen}
        </Text>
      </View>
      {item.status === "Online" && <View style={styles.onlineIndicator} />}
    </TouchableOpacity>
  );

  const renderSectionHeader = ({
    section,
  }: {
    section: SectionListData<ContactData, ContactSection>;
  }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{section.title}</Text>
    </View>
  );

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F5" />

        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Contacts</Text>
          <TouchableOpacity style={styles.addButton}>
            <Text style={styles.addButtonText}>Add New</Text>
          </TouchableOpacity>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <View style={styles.searchBar}>
            <Image
              source={require("@/assets/images/Search.png")}
              style={styles.searchIcon}
            />
            <TextInput
              style={styles.searchInput}
              placeholder="Search Contacts"
              placeholderTextColor="#999"
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>
        </View>

        {/* All Contacts Dropdown */}
        <TouchableOpacity
          style={styles.allContactsHeader}
          onPress={() => setShowDropdown(!showDropdown)}
        >
          <Text style={styles.allContactsText}>All Contacts</Text>
          <Text style={styles.dropdownArrow}>{showDropdown ? "▲" : "▼"}</Text>
        </TouchableOpacity>

        {/* Main Content Area */}
        <View style={styles.contentContainer}>
          {/* Contacts List */}
          <SectionList
            ref={sectionListRef}
            sections={groupedContacts}
            renderItem={renderContact}
            renderSectionHeader={renderSectionHeader}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContainer}
            showsVerticalScrollIndicator={false}
            stickySectionHeadersEnabled={false}
            keyboardShouldPersistTaps="handled"
          />

          {/* Letter Indicator Popup */}
          {showLetterIndicator && activeLetter && (
            <View style={styles.letterIndicator}>
              <Text style={styles.letterIndicatorText}>{activeLetter}</Text>
            </View>
          )}

          {/* Alphabet Sidebar */}
          <View
            ref={alphabetSidebarRef}
            style={styles.alphabetSidebar}
            onLayout={onSidebarLayout}
            {...panResponder.panHandlers}
          >
            {ALPHABET.map((letter) => (
              <View key={letter} style={styles.alphabetLetterContainer}>
                <Text
                  style={[
                    styles.alphabetLetter,
                    availableLetters.includes(letter) &&
                      styles.alphabetLetterActive,
                    activeLetter === letter && styles.alphabetLetterSelected,
                  ]}
                >
                  {letter}
                </Text>
              </View>
            ))}
          </View>
        </View>
      </SafeAreaView>
    </TouchableWithoutFeedback>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 15,
  },
  headerTitle: {
    fontSize: 44,
    fontWeight: "bold",
    color: "#f6ca15",
    fontFamily: Fonts.regular,
  },
  addButton: {
    backgroundColor: "#0039a9",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  addButtonText: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#fff",
    fontFamily: Fonts.regular,
  },
  searchContainer: {
    paddingHorizontal: 20,
    marginBottom: 15,
  },
  searchBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 25,
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  searchIcon: {
    width: 24,
    height: 24,
    tintColor: "#666",
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: "#333",
    fontFamily: Fonts.regular,
  },
  allContactsHeader: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  allContactsText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#000",
    fontFamily: Fonts.regular,
  },
  dropdownArrow: {
    fontSize: 12,
    color: "#000",
    marginLeft: 5,
  },
  contentContainer: {
    flex: 1,
    flexDirection: "row",
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingRight: 30,
    paddingBottom: 100,
  },
  sectionHeader: {
    backgroundColor: "#F0F0F0",
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 10,
    marginTop: 5,
  },
  sectionHeaderText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    fontFamily: Fonts.regular,
  },
  contactItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 10,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: "#E8E8E8",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  avatarImage: {
    width: 24,
    height: 32,
    tintColor: "#666",
  },
  avatarImageFull: {
    width: "100%",
    height: "100%",
    borderRadius: 25,
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 22,
    fontWeight: "600",
    color: "#000",
    marginBottom: 2,
    fontFamily: Fonts.regular,
  },
  contactStatus: {
    fontSize: 16,
    color: "#999",
    fontFamily: Fonts.regular,
  },
  onlineStatus: {
    color: "#4CAF50",
  },
  onlineIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: "#4CAF50",
  },
  alphabetSidebar: {
    position: "absolute",
    right: 5,
    top: 0,
    bottom: 100,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 10,
  },
  alphabetLetterContainer: {
    paddingVertical: 1,
    paddingHorizontal: 5,
  },
  alphabetLetter: {
    fontSize: 12,
    color: "#CCC",
    fontWeight: "500",
    fontFamily: Fonts.regular,
  },
  alphabetLetterActive: {
    color: "#666",
    fontWeight: "600",
  },
  alphabetLetterSelected: {
    color: "#0039a9",
    fontWeight: "bold",
  },
  letterIndicator: {
    position: "absolute",
    right: 40,
    top: "40%",
    width: 60,
    height: 60,
    borderRadius: 10,
    backgroundColor: "#0039a9",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 100,
  },
  letterIndicatorText: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#fff",
    fontFamily: Fonts.regular,
  },
});

export default ContactsScreen;
