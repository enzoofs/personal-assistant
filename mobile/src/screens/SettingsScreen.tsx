import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
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
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';
import { useSettings } from '../context/SettingsContext';
import { fetchSettings, updateSettings, ResponseMode } from '../api/atlas';
import { fontSize, spacing } from '../theme';
import { Haptic } from '../utils/haptics';

const RESPONSE_MODES: { value: ResponseMode; label: string; description: string; icon: string }[] = [
  { value: 'text', label: 'Apenas Texto', description: 'Sem áudio nas respostas', icon: 'text' },
  { value: 'audio', label: 'Áudio (Gratuito)', description: 'Edge TTS - voz sintética', icon: 'volume-medium' },
  { value: 'audio_premium', label: 'Áudio Premium', description: 'ElevenLabs - voz natural', icon: 'volume-high' },
];

export function SettingsScreen() {
  const { theme, colors, toggleTheme } = useTheme();
  const { serverUrl, apiKey, setServerUrl, setApiKey } = useSettings();
  const [urlDraft, setUrlDraft] = useState(serverUrl);
  const [keyDraft, setKeyDraft] = useState(apiKey);
  const [saved, setSaved] = useState(false);

  // Response mode state
  const [responseMode, setResponseMode] = useState<ResponseMode>('text');
  const [loadingMode, setLoadingMode] = useState(true);
  const [savingMode, setSavingMode] = useState(false);

  // Fetch current response mode on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const settings = await fetchSettings();
        setResponseMode(settings.response_mode);
      } catch (e) {
        console.error('Failed to fetch settings:', e);
      } finally {
        setLoadingMode(false);
      }
    };
    loadSettings();
  }, []);

  const handleSave = () => {
    setServerUrl(urlDraft.replace(/\/$/, ''));
    setApiKey(keyDraft);
    setSaved(true);
    Haptic.success();
    setTimeout(() => setSaved(false), 2000);
  };

  const handleResponseModeChange = async (mode: ResponseMode) => {
    if (mode === responseMode) return;

    Haptic.selection();
    setSavingMode(true);
    try {
      await updateSettings({ response_mode: mode });
      setResponseMode(mode);
      Haptic.success();
    } catch (e) {
      console.error('Failed to update response mode:', e);
      Haptic.error();
    } finally {
      setSavingMode(false);
    }
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

        {/* Response Mode */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Modo de Resposta</Text>
            {(loadingMode || savingMode) && (
              <ActivityIndicator size="small" color={colors.accent} />
            )}
          </View>
          <Text style={styles.sectionDescription}>
            Escolha como o ATLAS responde às suas mensagens
          </Text>
          {RESPONSE_MODES.map((mode) => (
            <Pressable
              key={mode.value}
              style={[
                styles.modeOption,
                responseMode === mode.value && styles.modeOptionSelected,
              ]}
              onPress={() => handleResponseModeChange(mode.value)}
              disabled={loadingMode || savingMode}
            >
              <View style={styles.modeIconContainer}>
                <Ionicons
                  name={mode.icon as any}
                  size={24}
                  color={responseMode === mode.value ? colors.accent : colors.textSecondary}
                />
              </View>
              <View style={styles.modeTextContainer}>
                <Text
                  style={[
                    styles.modeLabel,
                    responseMode === mode.value && { color: colors.accent },
                  ]}
                >
                  {mode.label}
                </Text>
                <Text style={styles.modeDescription}>{mode.description}</Text>
              </View>
              {responseMode === mode.value && (
                <Ionicons name="checkmark-circle" size={24} color={colors.accent} />
              )}
            </Pressable>
          ))}
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
    sectionHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    sectionTitle: {
      color: colors.text,
      fontSize: fontSize.lg,
      fontWeight: '600',
      marginBottom: spacing.xs,
    },
    sectionDescription: {
      color: colors.textSecondary,
      fontSize: fontSize.sm,
      marginBottom: spacing.md,
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
    modeOption: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: spacing.md,
      borderRadius: 8,
      marginBottom: spacing.sm,
      backgroundColor: colors.surfaceLight,
      borderWidth: 1,
      borderColor: colors.border,
    },
    modeOptionSelected: {
      borderColor: colors.accent,
      backgroundColor: `${colors.accent}15`,
    },
    modeIconContainer: {
      width: 40,
      alignItems: 'center',
    },
    modeTextContainer: {
      flex: 1,
      marginLeft: spacing.sm,
    },
    modeLabel: {
      color: colors.text,
      fontSize: fontSize.md,
      fontWeight: '600',
    },
    modeDescription: {
      color: colors.textSecondary,
      fontSize: fontSize.sm,
      marginTop: 2,
    },
  });
