import React, { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../context/ThemeContext';
import { useDashboardContext } from '../../context/DashboardContext';
import { fontSize, spacing } from '../../theme';
import { WidgetCard } from './WidgetCard';
import { Haptic } from '../../utils/haptics';

const HABIT_CONFIG: Record<string, { icon: string; label: string; unit?: string; type: 'boolean' | 'number' }> = {
  exercise: { icon: '🏃', label: 'Treino', type: 'boolean' },
  sleep: { icon: '😴', label: 'Sono', unit: 'h', type: 'number' },
  meditation: { icon: '🧘', label: 'Meditação', type: 'boolean' },
  water: { icon: '💧', label: 'Água', unit: 'L', type: 'number' },
};

interface HabitCardProps {
  type: string;
  value?: string | number | boolean;
  unit?: string;
  logged: boolean;
  onLog: (type: string, value: string | number | boolean) => Promise<void>;
}

function HabitCard({ type, value, unit, logged, onLog }: HabitCardProps) {
  const { colors } = useTheme();
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [showInput, setShowInput] = useState(false);

  const config = HABIT_CONFIG[type] || { icon: '📊', label: type, type: 'boolean' };

  const handleQuickLog = async (val: boolean | string | number) => {
    Haptic.mediumImpact();
    setLoading(true);
    try {
      await onLog(type, val);
      Haptic.success();
    } catch {
      Haptic.error();
    } finally {
      setLoading(false);
      setShowInput(false);
      setInputValue('');
    }
  };

  const handleSubmitNumber = () => {
    const num = parseFloat(inputValue);
    if (!isNaN(num) && num > 0) {
      handleQuickLog(num);
    }
  };

  return (
    <View style={[styles.habitCard, { backgroundColor: colors.surfaceLight, borderColor: colors.border }]}>
      <Text style={styles.habitIcon}>{config.icon}</Text>
      <Text style={[styles.habitLabel, { color: colors.text }]}>{config.label}</Text>

      {logged ? (
        <View style={styles.loggedValue}>
          <Text style={[styles.valueText, { color: colors.success }]}>
            {typeof value === 'boolean' ? '✓' : `${value}${unit || ''}`}
          </Text>
        </View>
      ) : loading ? (
        <ActivityIndicator size="small" color={colors.accent} />
      ) : config.type === 'boolean' ? (
        <View style={styles.booleanButtons}>
          <Pressable
            style={[styles.boolButton, { backgroundColor: colors.success }]}
            onPress={() => handleQuickLog(true)}
          >
            <Ionicons name="checkmark" size={16} color="#fff" />
          </Pressable>
          <Pressable
            style={[styles.boolButton, { backgroundColor: colors.error }]}
            onPress={() => handleQuickLog(false)}
          >
            <Ionicons name="close" size={16} color="#fff" />
          </Pressable>
        </View>
      ) : showInput ? (
        <View style={styles.inputRow}>
          <TextInput
            style={[styles.numberInput, { color: colors.text, borderColor: colors.border }]}
            value={inputValue}
            onChangeText={setInputValue}
            keyboardType="numeric"
            placeholder={unit || '0'}
            placeholderTextColor={colors.textSecondary}
            autoFocus
            onSubmitEditing={handleSubmitNumber}
          />
          <Pressable style={[styles.submitButton, { backgroundColor: colors.accent }]} onPress={handleSubmitNumber}>
            <Ionicons name="checkmark" size={14} color="#fff" />
          </Pressable>
        </View>
      ) : (
        <Pressable
          style={[styles.logButton, { borderColor: colors.accent }]}
          onPress={() => setShowInput(true)}
        >
          <Text style={[styles.logButtonText, { color: colors.accent }]}>Logar</Text>
        </Pressable>
      )}
    </View>
  );
}

export function HabitsWidget() {
  const { data, logHabit } = useDashboardContext();

  const habits = data?.habits || [];
  const loggedTypes = new Set(habits.map(h => h.type));

  // Hábitos para mostrar (logados + não logados)
  const habitsToShow = Object.keys(HABIT_CONFIG);

  return (
    <WidgetCard title="HÁBITOS" icon="🎯">
      <View style={styles.grid}>
        {habitsToShow.map(type => {
          const habit = habits.find(h => h.type === type);
          return (
            <HabitCard
              key={type}
              type={type}
              value={habit?.value}
              unit={habit?.unit}
              logged={loggedTypes.has(type)}
              onLog={logHabit}
            />
          );
        })}
      </View>
    </WidgetCard>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  habitCard: {
    width: '48%',
    borderRadius: 8,
    borderWidth: 1,
    padding: spacing.sm,
    alignItems: 'center',
    minHeight: 90,
    justifyContent: 'space-between',
  },
  habitIcon: {
    fontSize: 24,
  },
  habitLabel: {
    fontSize: fontSize.sm,
    fontWeight: '500',
    marginVertical: spacing.xs,
  },
  loggedValue: {
    paddingVertical: spacing.xs,
  },
  valueText: {
    fontSize: fontSize.lg,
    fontWeight: '700',
  },
  booleanButtons: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  boolButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    borderWidth: 1,
  },
  logButtonText: {
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  numberInput: {
    width: 50,
    height: 28,
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: spacing.xs,
    fontSize: fontSize.sm,
    textAlign: 'center',
  },
  submitButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
