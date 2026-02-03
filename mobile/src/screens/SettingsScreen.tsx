import React, { useState } from 'react';
import {
  Platform,
  Pressable,
  ScrollView,
  StatusBar,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useSettings } from '../context/SettingsContext';
import { fontSize, spacing } from '../theme';

export function SettingsScreen() {
  const { theme, colors, toggleTheme } = useTheme();
  const { serverUrl, apiKey, setServerUrl, setApiKey } = useSettings();
  const [urlDraft, setUrlDraft] = useState(serverUrl);
  const [keyDraft, setKeyDraft] = useState(apiKey);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setServerUrl(urlDraft.replace(/\/$/, ''));
    setApiKey(keyDraft);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const styles = makeStyles(colors);

  return (
    <View style={styles.container}>
      <StatusBar
        barStyle={theme === 'dark' ? 'light-content' : 'dark-content'}
        backgroundColor={colors.background}
      />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Configurações</Text>
      </View>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        {/* Theme */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Aparência</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Modo Escuro</Text>
            <Switch
              value={theme === 'dark'}
              onValueChange={toggleTheme}
              trackColor={{ false: colors.border, true: colors.accent }}
              thumbColor="#fff"
            />
          </View>
        </View>

        {/* Server */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Servidor</Text>
          <Text style={styles.label}>URL do Servidor</Text>
          <TextInput
            style={styles.input}
            value={urlDraft}
            onChangeText={setUrlDraft}
            placeholder="http://..."
            placeholderTextColor={colors.textSecondary}
            autoCapitalize="none"
            autoCorrect={false}
          />
          <Text style={[styles.label, { marginTop: spacing.sm }]}>API Key</Text>
          <TextInput
            style={styles.input}
            value={keyDraft}
            onChangeText={setKeyDraft}
            placeholder="sua-api-key"
            placeholderTextColor={colors.textSecondary}
            autoCapitalize="none"
            autoCorrect={false}
            secureTextEntry
          />
          <Pressable style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveText}>{saved ? 'Salvo!' : 'Salvar'}</Text>
          </Pressable>
        </View>
      </ScrollView>
    </View>
  );
}

const makeStyles = (colors: any) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingHorizontal: spacing.lg,
      paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 32) + spacing.sm : spacing.sm,
      paddingBottom: spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    headerTitle: {
      color: colors.text,
      fontSize: fontSize.xxl,
      fontWeight: '700',
    },
    scroll: { flex: 1 },
    scrollContent: { padding: spacing.md, paddingBottom: spacing.xxl },
    section: {
      backgroundColor: colors.surface,
      borderRadius: 12,
      padding: spacing.md,
      marginBottom: spacing.md,
      borderWidth: 1,
      borderColor: colors.border,
    },
    sectionTitle: {
      color: colors.text,
      fontSize: fontSize.lg,
      fontWeight: '600',
      marginBottom: spacing.sm,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    label: {
      color: colors.textSecondary,
      fontSize: fontSize.md,
    },
    input: {
      backgroundColor: colors.surfaceLight,
      color: colors.text,
      borderRadius: 8,
      paddingHorizontal: spacing.sm,
      paddingVertical: spacing.sm,
      fontSize: fontSize.md,
      marginTop: spacing.xs,
      borderWidth: 1,
      borderColor: colors.border,
    },
    saveButton: {
      backgroundColor: colors.accent,
      borderRadius: 8,
      paddingVertical: spacing.sm,
      alignItems: 'center',
      marginTop: spacing.md,
    },
    saveText: {
      color: '#FFFFFF',
      fontSize: fontSize.md,
      fontWeight: '600',
    },
  });
