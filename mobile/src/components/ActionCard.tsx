import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme';
import { ActionResult } from '../types';

interface ActionConfig {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  color: string;
}

const ACTION_CONFIG: Record<string, ActionConfig> = {
  save_note: { icon: 'document-text-outline', label: 'Nota salva', color: colors.accent },
  log_habit: { icon: 'fitness-outline', label: 'Hábito registrado', color: colors.warning },
  search: { icon: 'search-outline', label: 'Pesquisa', color: colors.accent },
  briefing: { icon: 'today-outline', label: 'Briefing', color: colors.accent },
  create_event: { icon: 'calendar-outline', label: 'Evento criado', color: colors.success },
  query_calendar: { icon: 'calendar-number-outline', label: 'Agenda', color: colors.accent },
  delete_event: { icon: 'trash-outline', label: 'Evento removido', color: colors.error },
};

const DEFAULT_CONFIG: ActionConfig = {
  icon: 'ellipsis-horizontal-outline',
  label: 'Ação',
  color: colors.accent,
};

interface Props {
  action: ActionResult;
}

export function ActionCard({ action }: Props) {
  const config = ACTION_CONFIG[action.type] || DEFAULT_CONFIG;
  const details = action.details;

  let detail = '';
  if (details.title) detail = String(details.title);
  else if (details.path) detail = String(details.path).split('/').pop() || '';
  else if (details.query) detail = `"${details.query}"`;
  else if (details.habit_type) detail = `${details.habit_type}: ${details.value} ${details.unit || ''}`.trim();
  else if (details.period) detail = String(details.period);
  else if (details.count !== undefined) detail = `${details.count} evento(s)`;

  return (
    <View style={[styles.card, { borderLeftColor: config.color }]}>
      <View style={[styles.iconContainer, { backgroundColor: config.color + '20' }]}>
        <Ionicons name={config.icon} size={20} color={config.color} />
      </View>
      <View style={styles.content}>
        <Text style={[styles.label, { color: config.color }]}>{config.label}</Text>
        {detail ? <Text style={styles.detail} numberOfLines={1}>{detail}</Text> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceLight,
    borderRadius: 10,
    borderLeftWidth: 3,
    padding: spacing.sm,
    paddingLeft: spacing.md,
    marginTop: spacing.xs,
    maxWidth: '85%',
    gap: spacing.sm,
  },
  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    flex: 1,
  },
  label: {
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  detail: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: 1,
  },
});
