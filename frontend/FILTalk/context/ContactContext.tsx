import React, { createContext, useContext, useState, ReactNode } from 'react';

// Contact data interface
export interface ContactData {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar: string | null;
  status?: 'Online' | 'Offline';
  lastSeen?: string;
}

// Context type with contacts list management
interface ContactContextType {
  contacts: ContactData[];
  selectedContact: ContactData | null;
  setSelectedContact: (contact: ContactData | null) => void;
  updateContact: (contact: ContactData) => void;
  addContact: (contact: ContactData) => void;
  deleteContact: (id: string) => void;
}

const ContactContext = createContext<ContactContextType | undefined>(undefined);

export const ContactProvider = ({ children }: { children: ReactNode }) => {
  // Sample contacts data - will be replaced with backend data
  const [contacts, setContacts] = useState<ContactData[]>([
    { id: '1', name: 'Juan Dela Cruz', email: 'juan@gmail.com', phone: '09123456789', avatar: null, status: 'Online', lastSeen: 'Active now' },
    { id: '2', name: 'Maria Santos', email: 'maria@gmail.com', phone: '09234567890', avatar: null, status: 'Offline', lastSeen: 'Last seen 2h ago' },
    { id: '3', name: 'Pedro Garcia', email: 'pedro@gmail.com', phone: '09345678901', avatar: null, status: 'Online', lastSeen: 'Active now' },
    { id: '4', name: 'Ana Reyes', email: 'ana@gmail.com', phone: '09456789012', avatar: null, status: 'Offline', lastSeen: 'Last seen yesterday' },
    { id: '5', name: 'Carlos Mendoza', email: 'carlos@gmail.com', phone: '09567890123', avatar: null, status: 'Online', lastSeen: 'Active now' },
  ]);

  const [selectedContact, setSelectedContact] = useState<ContactData | null>(null);

  const updateContact = (updatedContact: ContactData) => {
    setContacts(prev => 
      prev.map(contact => 
        contact.id === updatedContact.id ? updatedContact : contact
      )
    );
    if (selectedContact?.id === updatedContact.id) {
      setSelectedContact(updatedContact);
    }
  };

  const addContact = (newContact: ContactData) => {
    setContacts(prev => [...prev, newContact]);
  };

  const deleteContact = (id: string) => {
    setContacts(prev => prev.filter(contact => contact.id !== id));
    if (selectedContact?.id === id) {
      setSelectedContact(null);
    }
  };

  return (
    <ContactContext.Provider value={{ 
      contacts, 
      selectedContact, 
      setSelectedContact, 
      updateContact, 
      addContact, 
      deleteContact 
    }}>
      {children}
    </ContactContext.Provider>
  );
};

export const useContact = () => {
  const context = useContext(ContactContext);
  if (!context) {
    throw new Error('useContact must be used within ContactProvider');
  }
  return context;
};
