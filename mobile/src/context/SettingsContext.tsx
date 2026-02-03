import React, { createContext, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

interface SettingsContextType {
  serverUrl: string;
  apiKey: string;
  setServerUrl: (url: string) => void;
  setApiKey: (key: string) => void;
}

const DEFAULTS = {
  serverUrl: 'http://137.131.252.201:8000',
  apiKey: 'dev-key',
};

const SettingsContext = createContext<SettingsContextType>({
  ...DEFAULTS,
  setServerUrl: () => {},
  setApiKey: () => {},
});

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [serverUrl, _setServerUrl] = useState(DEFAULTS.serverUrl);
  const [apiKey, _setApiKey] = useState(DEFAULTS.apiKey);

  useEffect(() => {
    const loadSettings = async () => {
      const [url, key] = await Promise.all([
        AsyncStorage.getItem('serverUrl'),
        SecureStore.getItemAsync('apiKey'),
      ]);
      if (url) _setServerUrl(url);
      if (key) _setApiKey(key);
    };
    loadSettings();
  }, []);

  const setServerUrl = (url: string) => {
    _setServerUrl(url);
    AsyncStorage.setItem('serverUrl', url);
  };

  const setApiKey = async (key: string) => {
    _setApiKey(key);
    await SecureStore.setItemAsync('apiKey', key);
  };

  return (
    <SettingsContext.Provider value={{ serverUrl, apiKey, setServerUrl, setApiKey }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  return useContext(SettingsContext);
}
