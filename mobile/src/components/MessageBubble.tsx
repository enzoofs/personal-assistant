import React, { useEffect, useRef, useState } from 'react';
import { Animated, Modal, Pressable, StyleSheet, Text } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import Markdown from 'react-native-markdown-display';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme';
import { Message } from '../types';
import { ActionCard } from './ActionCard';
import { Haptic } from '../utils/haptics';

interface Props {
  message: Message;
  onSaveAsNote?: (text: string) => void;
  onToast?: (message: string) => void;
}

export function MessageBubble({ message, onSaveAsNote, onToast }: Props) {
  // Animation values
  const opacity = useRef(new Animated.Value(0)).current;
  const translateX = useRef(new Animated.Value(message.isUser ? 30 : -30)).current;
  const translateY = useRef(new Animated.Value(10)).current;
  const scale = useRef(new Animated.Value(0.92)).current;

  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    // Spring-based entrance animation for a more natural, bouncy feel
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 250,
        useNativeDriver: true,
      }),
      Animated.spring(translateX, {
        toValue: 0,
        friction: 8,
        tension: 80,
        useNativeDriver: true,
      }),
      Animated.spring(translateY, {
        toValue: 0,
        friction: 8,
        tension: 80,
        useNativeDriver: true,
      }),
      Animated.spring(scale, {
        toValue: 1,
        friction: 6,
        tension: 100,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleLongPress = () => {
    if (message.text) {
      Haptic.medium();
      setMenuVisible(true);
    }
  };

  const handleCopy = async () => {
    Haptic.light();
    await Clipboard.setStringAsync(message.text);
    setMenuVisible(false);
    onToast?.('Texto copiado');
  };

  const handleSaveAsNote = () => {
    Haptic.success();
    setMenuVisible(false);
    onSaveAsNote?.(message.text);
  };

  return (
    <>
      <Animated.View
        style={[
          styles.container,
          message.isUser ? styles.user : styles.bot,
          {
            opacity,
            transform: [
              { translateX },
              { translateY },
              { scale },
            ],
          },
        ]}
      >
        <Pressable
          onLongPress={handleLongPress}
          delayLongPress={400}
          style={({ pressed }) => [
            styles.bubble,
            message.isUser ? styles.userBubble : styles.botBubble,
            pressed && styles.bubblePressed,
          ]}
        >
          {message.isUser ? (
            <Text style={[styles.text, styles.userText]} selectable>{message.text}</Text>
          ) : (
            <Markdown style={markdownStyles}>{message.text}</Markdown>
          )}
          {message.intent && !message.isUser && (
            <Text style={styles.intent}>{message.intent}</Text>
          )}
        </Pressable>
        {message.actions?.map((action, i) => (
          <ActionCard key={i} action={action} />
        ))}
      </Animated.View>

      {/* Context Menu Modal */}
      <Modal
        visible={menuVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setMenuVisible(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setMenuVisible(false)}>
          <Animated.View style={styles.menuContainer}>
            <Pressable
              style={({ pressed }) => [styles.menuItem, pressed && styles.menuItemPressed]}
              onPress={handleCopy}
            >
              <Ionicons name="copy-outline" size={20} color={colors.text} />
              <Text style={styles.menuText}>Copiar</Text>
            </Pressable>
            {!message.isUser && onSaveAsNote && (
              <Pressable
                style={({ pressed }) => [
                  styles.menuItem,
                  styles.menuItemLast,
                  pressed && styles.menuItemPressed,
                ]}
                onPress={handleSaveAsNote}
              >
                <Ionicons name="document-text-outline" size={20} color={colors.text} />
                <Text style={styles.menuText}>Salvar como nota</Text>
              </Pressable>
            )}
          </Animated.View>
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing.xs,
    paddingHorizontal: spacing.md,
  },
  user: {
    alignItems: 'flex-end',
  },
  bot: {
    alignItems: 'flex-start',
  },
  bubble: {
    maxWidth: '85%',
    padding: spacing.md,
    borderRadius: 16,
  },
  bubblePressed: {
    opacity: 0.85,
  },
  userBubble: {
    backgroundColor: colors.accent,
    borderBottomRightRadius: 4,
    // Subtle glow effect
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  botBubble: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
    // Subtle shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  text: {
    color: colors.text,
    fontSize: fontSize.md,
    lineHeight: 22,
  },
  userText: {
    color: '#FFFFFF',
  },
  intent: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: spacing.xs,
    fontStyle: 'italic',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuContainer: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    minWidth: 220,
    overflow: 'hidden',
    // Menu shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  menuItemLast: {
    borderBottomWidth: 0,
  },
  menuItemPressed: {
    backgroundColor: colors.surfaceLight,
  },
  menuText: {
    color: colors.text,
    fontSize: fontSize.md,
  },
});

const markdownStyles = StyleSheet.create({
  body: { color: colors.text, fontSize: fontSize.md, lineHeight: 22 },
  strong: { color: colors.text, fontWeight: '700' },
  em: { color: colors.text, fontStyle: 'italic' },
  link: { color: colors.accent },
  bullet_list: { marginVertical: spacing.xs },
  ordered_list: { marginVertical: spacing.xs },
  list_item: { color: colors.text, fontSize: fontSize.md },
  code_inline: { backgroundColor: colors.surfaceLight, color: colors.accent, borderRadius: 4, paddingHorizontal: 4 },
  fence: { backgroundColor: colors.surfaceLight, borderRadius: 8, padding: spacing.sm },
  code_block: { color: colors.text, fontSize: fontSize.sm },
  heading1: { color: colors.text, fontSize: fontSize.xl, fontWeight: '700', marginVertical: spacing.xs },
  heading2: { color: colors.text, fontSize: fontSize.lg, fontWeight: '700', marginVertical: spacing.xs },
  paragraph: { marginVertical: 2 },
});
