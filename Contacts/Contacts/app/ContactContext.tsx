import React, { createContext, useContext, useState, ReactNode } from 'react';

// STEP 1: Define the shape of our contact data
// This interface describes what properties a contact has
interface ContactData {
  name: string;
  email: string;
  phone: string;
  avatar: string | null;  // Can be null (no image) or string (image URI)
}

// STEP 2: Define what the context provides
// This interface describes what functions/data we can access from the context
interface ContactContextType {
  contactData: ContactData;  // The current contact information
  updateContact: (data: ContactData) => void;  // Function to update the contact
}

// STEP 3: Create the context (initially undefined)
// Think of this as creating an empty "storage box" that will hold our contact data
const ContactContext = createContext<ContactContextType | undefined>(undefined);

// STEP 4: Create the Provider component
// This component wraps around our app and provides the contact data to all child components
export const ContactProvider = ({ children }: { children: ReactNode }) => {
  // Create state to hold the contact data - this is the "single source of truth"
  const [contactData, setContactData] = useState<ContactData>({
    name: 'Arthur Nery',
    email: 'lorem@gmail.com',
    phone: '09231734621',
    avatar: null,
  });

  // Function that other components can call to update the contact data
  // When this runs, it updates the state, which triggers re-renders in components using this data
  const updateContact = (data: ContactData) => {
    setContactData(data);
  };

  // Return the Provider component with the value it should share
  // Any component inside {children} can now access contactData and updateContact
  return (
    <ContactContext.Provider value={{ contactData, updateContact }}>
      {children}
    </ContactContext.Provider>
  );
};

// STEP 5: Create a custom hook for easy access
// Instead of using useContext(ContactContext) everywhere, we use useContact()
export const useContact = () => {
  // Get the context value (contactData and updateContact)
  const context = useContext(ContactContext);
  
  // Safety check: If someone tries to use useContact outside of ContactProvider, throw an error
  if (!context) {
    throw new Error('useContact must be used within ContactProvider');
  }
  
  // Return the context so components can use it
  // Example: const { contactData, updateContact } = useContact();
  return context;
};

/*
HOW IT ALL WORKS TOGETHER:

1. _layout.tsx wraps the app with <ContactProvider>
   This makes contact data available to ALL screens

2. index.tsx (Display Screen) uses:
   const { contactData } = useContact();
   - Reads the current contact data
   - Automatically updates when data changes

3. editContact.tsx (Edit Screen) uses:
   const { contactData, updateContact } = useContact();
   - Reads current contact data to pre-fill the form
   - Calls updateContact(newData) when Save is clicked
   - This updates the shared state
   - index.tsx automatically shows the new data!

ANALOGY:
Think of ContactContext like a shared notebook:
- ContactProvider is the notebook keeper
- contactData is what's written in the notebook
- updateContact is the function to write new data
- useContact is how you borrow the notebook to read or write
*/
