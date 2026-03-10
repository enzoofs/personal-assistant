import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../context/ThemeContext';
import { useDashboardContext } from '../../context/DashboardContext';
import { fontSize, spacing } from '../../theme';
import { WidgetCard } from './WidgetCard';
import { Haptic } from '../../utils/haptics';

interface Props {
  onAddEvent?: () => void;
}

export function AgendaWidget({ onAddEvent }: Props) {
  const { colors } = useTheme();
  const { data } = useDashboardContext();

  const events = data?.events || [];

  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateStr;
    }
  };

  const handleAddEvent = () => {
    Haptic.lightImpact();
    onAddEvent?.();
  };

  const addButton = (
    <Pressable onPress={handleAddEvent} style={styles.addButton}>
      <Ionicons name="add-circle" size={24} color={colors.accent} />
    </Pressable>
  );

  return (
    <WidgetCard title="HOJE" icon="📅" headerRight={addButton}>
      {events.length === 0 ? (
        <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
          Nenhum evento agendado
        </Text>
      ) : (
        <View style={styles.eventList}>
          {events.map((event, idx) => (
            <View key={event.id || idx} style={styles.eventItem}>
              <Text style={[styles.eventTime, { color: colors.accent }]}>
                {formatTime(event.start)}
              </Text>
              <Text style={[styles.eventSummary, { color: colors.text }]} numberOfLines={1}>
                {event.summary}
              </Text>
            </View>
          ))}
        </View>
      )}
    </WidgetCard>
  );
}

const styles = StyleSheet.create({
  addButton: {
    padding: spacing.xs,
  },
  emptyText: {
    fontSize: fontSize.sm,
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: spacing.sm,
  },
  eventList: {
    gap: spacing.sm,
  },
  eventItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  eventTime: {
    fontSize: fontSize.sm,
    fontWeight: '600',
    minWidth: 50,
  },
  eventSummary: {
    fontSize: fontSize.md,
    flex: 1,
  },
});
