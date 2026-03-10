import React, { useEffect } from 'react';
import { NavigationContainer, DarkTheme, DefaultTheme } from '@react-navigation/native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { AppNavigator } from './src/navigation/AppNavigator';
import { ThemeProvider, useTheme } from './src/context/ThemeContext';
import { SettingsProvider, useSettings } from './src/context/SettingsContext';
import { DashboardProvider } from './src/context/DashboardContext';
import { configureApi } from './src/api/atlas';

function AppInner() {
  const { theme, colors } = useTheme();
  const { serverUrl, apiKey } = useSettings();

  useEffect(() => {
    configureApi(serverUrl, apiKey);
  }, [serverUrl, apiKey]);

  const navTheme = {
    ...(theme === 'dark' ? DarkTheme : DefaultTheme),
    colors: {
      ...(theme === 'dark' ? DarkTheme.colors : DefaultTheme.colors),
      background: colors.background,
      card: colors.surface,
      border: colors.border,
      primary: colors.accent,
      text: colors.text,
    },
  };

  return (
    <NavigationContainer theme={navTheme}>
      <AppNavigator />
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <ThemeProvider>
        <SettingsProvider>
          <DashboardProvider>
            <AppInner />
          </DashboardProvider>
        </SettingsProvider>
      </ThemeProvider>
    </GestureHandlerRootView>
  );
}
