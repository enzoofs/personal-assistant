import React, { useEffect, useRef } from 'react';
import { Animated, Pressable, ScrollView, StyleSheet, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme';
import { Haptic } from '../utils/haptics';

interface QuickReply {
  label: string;
  message: string;
  icon: keyof typeof Ionicons.glyphMap;
}

// Default suggestions
const DEFAULT_REPLIES: QuickReply[] = [
  { label: 'Briefing', message: 'Meu briefing do dia', icon: 'sunny-outline' },
  { label: 'Emails', message: 'Emails não lidos', icon: 'mail-outline' },
  { label: 'Agenda', message: 'Minha agenda de hoje', icon: 'calendar-outline' },
  { label: 'Compras', message: 'Lista de compras', icon: 'cart-outline' },
];

// Contextual suggestions based on last intent
const CONTEXTUAL_REPLIES: Record<string, QuickReply[]> = {
  briefing: [
    { label: 'Mais detalhes', message: 'Me conta mais sobre os eventos de hoje', icon: 'expand-outline' },
    { label: 'Criar evento', message: 'Criar um evento para hoje', icon: 'add-circle-outline' },
    { label: 'Emails', message: 'Mostrar emails não lidos', icon: 'mail-outline' },
  ],
  read_email: [
    { label: 'Responder', message: 'Quero responder esse email', icon: 'arrow-undo-outline' },
    { label: 'Arquivar', message: 'Arquivar esses emails', icon: 'archive-outline' },
    { label: 'Mais emails', message: 'Mostrar mais emails', icon: 'mail-unread-outline' },
  ],
  create_event: [
    { label: 'Ver agenda', message: 'Mostrar minha agenda', icon: 'calendar-outline' },
    { label: 'Novo evento', message: 'Criar outro evento', icon: 'add-circle-outline' },
    { label: 'Editar', message: 'Editar esse evento', icon: 'create-outline' },
  ],
  shopping_add: [
    { label: 'Ver lista', message: 'Mostrar lista de compras', icon: 'list-outline' },
    { label: 'Adicionar mais', message: 'Adicionar mais itens', icon: 'add-outline' },
    { label: 'Limpar comprados', message: 'Limpar itens comprados', icon: 'checkmark-done-outline' },
  ],
  shopping_list: [
    { label: 'Adicionar item', message: 'Adicionar item na lista', icon: 'add-outline' },
    { label: 'Limpar comprados', message: 'Limpar itens já comprados', icon: 'checkmark-done-outline' },
  ],
  search: [
    { label: 'Mais resultados', message: 'Buscar mais sobre isso', icon: 'search-outline' },
    { label: 'Salvar nota', message: 'Salvar isso como nota', icon: 'document-text-outline' },
  ],
  save_note: [
    { label: 'Ver notas', message: 'Mostrar minhas notas recentes', icon: 'documents-outline' },
    { label: 'Nova nota', message: 'Criar outra nota', icon: 'add-circle-outline' },
  ],
  log_habit: [
    { label: 'Ver hábitos', message: 'Mostrar meus hábitos de hoje', icon: 'fitness-outline' },
    { label: 'Registrar outro', message: 'Registrar outro hábito', icon: 'add-outline' },
  ],
};

interface Props {
  onSend: (message: string) => void;
  lastIntent?: string;
  visible?: boolean;
}

export function QuickReplies({ onSend, lastIntent, visible = true }: Props) {
  // Get appropriate suggestions
  const replies = lastIntent && CONTEXTUAL_REPLIES[lastIntent]
    ? CONTEXTUAL_REPLIES[lastIntent]
    : DEFAULT_REPLIES;

  // Animation values for each chip
  const animations = useRef(replies.map(() => ({
    opacity: new Animated.Value(0),
    translateY: new Animated.Value(20),
    scale: new Animated.Value(0.8),
  }))).current;

  // Container animation
  const containerOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      // Fade in container
      Animated.timing(containerOpacity, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }).start();

      // Stagger chip animations
      animations.forEach((anim, index) => {
        Animated.parallel([
          Animated.timing(anim.opacity, {
            toValue: 1,
            duration: 300,
            delay: index * 50,
            useNativeDriver: true,
          }),
          Animated.spring(anim.translateY, {
            toValue: 0,
            friction: 8,
            tension: 100,
            delay: index * 50,
            useNativeDriver: true,
          }),
          Animated.spring(anim.scale, {
            toValue: 1,
            friction: 6,
            tension: 100,
            delay: index * 50,
            useNativeDriver: true,
          }),
        ]).start();
      });
    } else {
      containerOpacity.setValue(0);
      animations.forEach(anim => {
        anim.opacity.setValue(0);
        anim.translateY.setValue(20);
        anim.scale.setValue(0.8);
      });
    }
  }, [visible, lastIntent]);

  if (!visible) return null;

  return (
    <Animated.View style={[styles.container, { opacity: containerOpacity }]}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {replies.map((reply, index) => {
          const anim = animations[index] || animations[0];
          return (
            <Animated.View
              key={`${reply.label}-${index}`}
              style={{
                opacity: anim.opacity,
                transform: [
                  { translateY: anim.translateY },
                  { scale: anim.scale },
                ],
              }}
            >
              <Pressable
                style={({ pressed }) => [
                  styles.chip,
                  pressed && styles.chipPressed,
                ]}
                onPress={() => {
                  Haptic.light();
                  onSend(reply.message);
                }}
              >
                <Ionicons
                  name={reply.icon}
                  size={16}
                  color={colors.accent}
                  style={styles.icon}
                />
                <Text style={styles.label}>{reply.label}</Text>
              </Pressable>
            </Animated.View>
          );
        })}
      </ScrollView>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: spacing.xs,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.background,
  },
  scrollContent: {
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    // Shadow
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  chipPressed: {
    backgroundColor: colors.surfaceLight,
    transform: [{ scale: 0.95 }],
  },
  icon: {
    marginRight: spacing.xs,
  },
  label: {
    color: colors.text,
    fontSize: fontSize.sm,
    fontWeight: '500',
  },
});
