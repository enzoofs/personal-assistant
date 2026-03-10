import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../context/ThemeContext';
import { useDashboardContext } from '../../context/DashboardContext';
import { fontSize, spacing } from '../../theme';
import { Insight } from '../../types';
import { Haptic } from '../../utils/haptics';

interface Props {
  onAction?: (insight: Insight, action: { intent: string; parameters: Record<string, unknown> }) => void;
}

export function InsightsWidget({ onAction }: Props) {
  const { colors } = useTheme();
  const { insights, dismissInsight } = useDashboardContext();

  const activeInsights = insights.filter(i => !i.dismissed);

  if (activeInsights.length === 0) {
    return null;
  }

  const handleDismiss = (id: string) => {
    Haptic.lightImpact();
    dismissInsight(id);
  };

  const handleAction = (insight: Insight, action: { intent: string; parameters: Record<string, unknown> }) => {
    Haptic.mediumImpact();
    onAction?.(insight, action);
    dismissInsight(insight.id);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return colors.error;
      case 'normal':
        return colors.warning;
      default:
        return colors.accent;
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.surfaceLight, borderColor: colors.border }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.warning }]}>
          <Ionicons name="bulb" size={16} /> INSIGHTS
        </Text>
      </View>
      {activeInsights.map(insight => (
        <View key={insight.id} style={[styles.insightCard, { borderLeftColor: getPriorityColor(insight.priority) }]}>
          <View style={styles.insightContent}>
            <Text style={[styles.insightTitle, { color: colors.text }]}>{insight.title}</Text>
            <Text style={[styles.insightMessage, { color: colors.textSecondary }]}>{insight.message}</Text>
          </View>
          <View style={styles.actions}>
            {insight.actions?.map((action, idx) => (
              <Pressable
                key={idx}
                style={[styles.actionButton, { backgroundColor: colors.accent }]}
                onPress={() => handleAction(insight, action)}
              >
                <Text style={[styles.actionText, { color: colors.text }]}>{action.label}</Text>
              </Pressable>
            ))}
            <Pressable style={styles.dismissButton} onPress={() => handleDismiss(insight.id)}>
              <Ionicons name="close" size={18} color={colors.textSecondary} />
            </Pressable>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: spacing.md,
    overflow: 'hidden',
  },
  header: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  title: {
    fontSize: fontSize.sm,
    fontWeight: '700',
    letterSpacing: 1,
  },
  insightCard: {
    borderLeftWidth: 3,
    marginHorizontal: spacing.sm,
    marginBottom: spacing.sm,
    paddingLeft: spacing.sm,
    paddingVertical: spacing.xs,
  },
  insightContent: {
    marginBottom: spacing.xs,
  },
  insightTitle: {
    fontSize: fontSize.md,
    fontWeight: '600',
  },
  insightMessage: {
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  actionButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 16,
  },
  actionText: {
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  dismissButton: {
    padding: spacing.xs,
  },
});
