import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  FlatList,
  Image,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme';
import { useChat } from '../hooks/useChat';
import { useAudio } from '../hooks/useAudio';
import { checkHealth } from '../api/atlas';
import { MessageBubble } from '../components/MessageBubble';
import { MicButton } from '../components/MicButton';
import { ChatInput } from '../components/ChatInput';
import { Toast } from '../components/Toast';
import { TypingIndicator } from '../components/TypingIndicator';
import { QuickReplies } from '../components/QuickReplies';
import { Message } from '../types';

const ACTION_LABELS: Record<string, string> = {
  save_note: 'Nota salva',
  create_event: 'Evento criado',
  delete_event: 'Evento deletado',
  edit_event: 'Evento atualizado',
  log_habit: 'Hábito registrado',
  search: 'Pesquisa realizada',
  read_email: 'Emails carregados',
  send_email: 'Email enviado',
  send_email_pending: 'Email pronto para envio',
  confirm_send_email: 'Email confirmado',
  trash_email: 'Email movido para lixeira',
  briefing: 'Briefing gerado',
  shopping_add: 'Adicionado à lista',
  shopping_list: 'Lista de compras',
  shopping_complete: 'Item comprado',
};

export function HomeScreen() {
  const { messages, loading, send, sendAudio } = useChat();
  const [toast, setToast] = useState<string | null>(null);
  const { recording, playing, startRecording, stopRecording, playBase64Audio } = useAudio();
  const [connected, setConnected] = useState<boolean | null>(null);
  const [connError, setConnError] = useState<string | null>(null);
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const flatListRef = useRef<FlatList<Message>>(null);

  // Skip health checks while loading to avoid false offline status
  useEffect(() => {
    const check = () => {
      if (loading) return;
      checkHealth().then(r => { setConnected(r.ok); setConnError(r.error || null); });
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, [loading]);

  // Show toast when bot message has actions
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (last && !last.isUser && last.actions?.length) {
      const label = ACTION_LABELS[last.actions[0].type] || last.actions[0].type;
      setToast(label);
    }
  }, [messages.length]);

  useEffect(() => {
    if (messages.length > 0 || loading) {
      setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
    }
  }, [messages.length, loading]);

  useEffect(() => {
    const showEvent = Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow';
    const hideEvent = Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide';

    const showSub = Keyboard.addListener(showEvent, () => {
      setKeyboardVisible(true);
      setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 150);
    });

    const hideSub = Keyboard.addListener(hideEvent, () => {
      setKeyboardVisible(false);
    });

    return () => {
      showSub.remove();
      hideSub.remove();
    };
  }, []);

  const handleMicPress = async () => {
    if (recording) {
      const uri = await stopRecording();
      if (uri) {
        const result = await sendAudio(uri);
        if (result?.audio_base64) {
          await playBase64Audio(result.audio_base64);
        }
      }
    } else {
      await startRecording();
    }
  };

  const handleSaveAsNote = useCallback((text: string) => {
    send(`Salve isso como nota: ${text}`);
    setToast('Salvando como nota...');
  }, [send]);

  const handleShowToast = useCallback((msg: string) => {
    setToast(msg);
  }, []);

  // Get last bot message intent for contextual quick replies
  const lastBotMessage = [...messages].reverse().find(m => !m.isUser);
  const lastIntent = lastBotMessage?.intent || lastBotMessage?.actions?.[0]?.type;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.titleRow}>
            <Image source={require('../assets/logo.png')} style={styles.logo} />
            <Text style={styles.title}>ATLAS</Text>
          </View>
          <View style={styles.statusRow}>
            <View style={[styles.dot, connected ? styles.dotOn : styles.dotOff]} />
            <Text style={styles.statusText}>
              {connected === null ? 'Conectando...' : connected ? 'Online' : `Offline`}
            </Text>
          </View>
          {connError && <Text style={styles.connError} numberOfLines={2}>{connError}</Text>}
        </View>

        {/* Messages */}
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={item => item.id}
          renderItem={({ item }) => (
            <MessageBubble
              message={item}
              onSaveAsNote={handleSaveAsNote}
              onToast={handleShowToast}
            />
          )}
          contentContainerStyle={styles.messageList}
          keyboardShouldPersistTaps="handled"
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={styles.emptyTitle}>ATLAS</Text>
              <Text style={styles.emptySubtitle}>Seu assistente pessoal</Text>
              <Text style={styles.emptyHint}>Tente perguntar:</Text>
              <View style={styles.suggestions}>
                {[
                  { label: 'Briefing do dia', icon: 'sunny-outline' },
                  { label: 'Emails não lidos', icon: 'mail-outline' },
                  { label: 'Minha agenda', icon: 'calendar-outline' },
                  { label: 'Lista de compras', icon: 'cart-outline' },
                ].map((s) => (
                  <Pressable key={s.label} style={styles.suggestionChip} onPress={() => send(s.label)}>
                    <Ionicons name={s.icon as keyof typeof Ionicons.glyphMap} size={16} color={colors.accent} />
                    <Text style={styles.suggestionText}>{s.label}</Text>
                  </Pressable>
                ))}
              </View>
            </View>
          }
        />

        {/* Typing indicator */}
        {loading && <TypingIndicator />}

        {/* Mic Button — hidden when keyboard is open */}
        {!keyboardVisible && (
          <MicButton
            onPress={handleMicPress}
            disabled={loading || playing}
            recording={recording}
          />
        )}

        {/* Quick Replies — hidden when loading, recording, or keyboard visible */}
        <QuickReplies
          onSend={send}
          lastIntent={lastIntent}
          visible={!loading && !recording && !keyboardVisible && messages.length > 0}
        />

        {/* Text Input */}
        <ChatInput onSend={send} disabled={loading || recording} />
        <Toast message={toast || ''} visible={!!toast} onHide={() => setToast(null)} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  flex: {
    flex: 1,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 32) + spacing.sm : spacing.sm,
    paddingBottom: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  logo: {
    width: 44,
    height: 44,
    borderRadius: 8,
  },
  title: {
    color: colors.accent,
    fontSize: fontSize.xxl,
    fontWeight: '700',
    letterSpacing: 4,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: 2,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  dotOn: {
    backgroundColor: colors.success,
  },
  dotOff: {
    backgroundColor: colors.error,
  },
  statusText: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
  },
  connError: {
    color: colors.error,
    fontSize: fontSize.xs,
    marginTop: 2,
  },
  messageList: {
    flexGrow: 1,
    paddingVertical: spacing.sm,
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 120,
  },
  emptyTitle: {
    color: colors.accent,
    fontSize: 48,
    fontWeight: '700',
    letterSpacing: 8,
    opacity: 0.3,
  },
  emptySubtitle: {
    color: colors.textSecondary,
    fontSize: fontSize.lg,
    marginTop: spacing.sm,
  },
  emptyHint: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: spacing.xl,
    opacity: 0.7,
  },
  suggestions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: spacing.sm,
    marginTop: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  suggestionChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    // Shadow
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  suggestionText: {
    color: colors.text,
    fontSize: fontSize.sm,
    fontWeight: '500',
  },
});
