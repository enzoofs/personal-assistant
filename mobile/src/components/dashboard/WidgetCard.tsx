import React from 'react';
import { StyleSheet, Text, View, ViewStyle } from 'react-native';
import { useTheme } from '../../context/ThemeContext';
import { fontSize, spacing } from '../../theme';

interface Props {
  title: string;
  icon?: string;
  children: React.ReactNode;
  style?: ViewStyle;
  headerRight?: React.ReactNode;
}

export function WidgetCard({ title, icon, children, style, headerRight }: Props) {
  const { colors } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: colors.surface, borderColor: colors.border }, style]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>
          {icon} {title}
        </Text>
        {headerRight}
      </View>
      <View style={styles.content}>{children}</View>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  title: {
    fontSize: fontSize.md,
    fontWeight: '600',
  },
  content: {
    padding: spacing.md,
  },
});
