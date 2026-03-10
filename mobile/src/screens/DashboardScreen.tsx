import React from 'react';
import {
  ActivityIndicator,
  Platform,
  Pressable,
  RefreshControl,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../context/ThemeContext';
import { useDashboardContext } from '../context/DashboardContext';
import { fontSize, spacing } from '../theme';
import { InsightsWidget, AgendaWidget, HabitsWidget, WidgetCard } from '../components/dashboard';
import { Insight } from '../types';

function VaultWidget() {
  const { colors } = useTheme();
  const { data } = useDashboardContext();
  const vault = data?.vault;

  if (!vault || vault.total_notes === 0) {
    return (
      <WidgetCard title="VAULT" icon="📝">
        <Text style={[styles.emptyText, { color: colors.textSecondary }]}>Vault vazio</Text>
      </WidgetCard>
    );
  }

  return (
    <WidgetCard title="VAULT" icon="📝">
      <View style={styles.statsRow}>
        <View style={[styles.statCard, { backgroundColor: colors.surfaceLight }]}>
          <Text style={[styles.statNumber, { color: colors.accent }]}>{vault.total_notes}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Notas</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: colors.surfaceLight }]}>
          <Text style={[styles.statNumber, { color: colors.accent }]}>{vault.notes_today}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Hoje</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: colors.surfaceLight }]}>
          <Text style={[styles.statNumber, { color: colors.accent }]}>{vault.orphan_notes}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Órfãs</Text>
        </View>
      </View>
      {vault.top_topics && vault.top_topics.length > 0 && (
        <View style={styles.topicsRow}>
          {vault.top_topics.slice(0, 5).map(([topic, count]) => (
            <View key={topic} style={[styles.topicChip, { backgroundColor: colors.surfaceLight }]}>
              <Text style={[styles.topicText, { color: colors.accent }]}>
                {topic} ({count})
              </Text>
            </View>
          ))}
        </View>
      )}
    </WidgetCard>
  );
}

function EmailsWidget() {
  const { colors } = useTheme();
  const { data, dismissAllAlerts } = useDashboardContext();

  const emails = data?.emails || [];
  const alerts = data?.email_alerts || [];

  return (
    <>
      {alerts.length > 0 && (
        <WidgetCard title="ATENÇÃO" icon="🚨">
          {alerts.map((alert, i) => (
            <View key={i} style={styles.alertRow}>
              <Text style={[styles.alertCategory, { color: colors.error }]}>{alert.category}</Text>
              <View style={{ flex: 1 }}>
                <Text style={[styles.alertSummary, { color: colors.text }]}>{alert.summary}</Text>
                <Text style={[styles.alertFrom, { color: colors.textSecondary }]} numberOfLines={1}>
                  {alert.from}
                </Text>
              </View>
            </View>
          ))}
          <Pressable
            style={[styles.dismissButton, { borderColor: colors.border }]}
            onPress={dismissAllAlerts}
          >
            <Text style={[styles.dismissText, { color: colors.textSecondary }]}>Dispensar alertas</Text>
          </Pressable>
        </WidgetCard>
      )}

      <WidgetCard title="EMAILS" icon="✉️">
        {emails.length > 0 ? (
          emails.map(email => (
            <View key={email.id} style={[styles.emailRow, { borderBottomColor: colors.border }]}>
              <Text style={[styles.emailFrom, { color: colors.accent }]} numberOfLines={1}>
                {email.from}
              </Text>
              <Text style={[styles.emailSubject, { color: colors.text }]} numberOfLines={1}>
                {email.subject}
              </Text>
            </View>
          ))
        ) : (
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>Nenhum email não lido</Text>
        )}
      </WidgetCard>
    </>
  );
}

function MemoriesWidget() {
  const { colors } = useTheme();
  const { data } = useDashboardContext();
  const memories = data?.memories || [];

  if (memories.length === 0) {
    return null;
  }

  return (
    <WidgetCard title="MEMÓRIAS" icon="🧠">
      {memories.slice(0, 5).map((mem, i) => (
        <View key={i} style={styles.memoryRow}>
          <Text style={[styles.memoryCategory, { color: colors.accent, backgroundColor: colors.surfaceLight }]}>
            {mem.category}
          </Text>
          <Text style={[styles.memoryContent, { color: colors.text }]} numberOfLines={2}>
            {mem.content}
          </Text>
        </View>
      ))}
    </WidgetCard>
  );
}

export function DashboardScreen() {
  const { colors } = useTheme();
  const { data, loading, error, refresh, lastUpdated } = useDashboardContext();
  const navigation = useNavigation<any>();

  const handleAddEvent = () => {
    // Navegar para o chat com mensagem pré-preenchida
    navigation.navigate('Chat', { prefill: 'Marca ' });
  };

  const handleInsightAction = (insight: Insight, action: { intent: string; parameters: Record<string, unknown> }) => {
    // Navegar para o chat para executar a ação
    if (action.intent === 'log_habit') {
      const habit = action.parameters.habit as string;
      navigation.navigate('Chat', { prefill: `Registra ${habit}` });
    }
  };

  if (loading && !data) {
    return (
      <View style={[styles.centered, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  if (error && !data) {
    return (
      <View style={[styles.centered, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
        <Pressable style={[styles.retryButton, { backgroundColor: colors.accent }]} onPress={refresh}>
          <Text style={[styles.retryText, { color: colors.text }]}>Tentar novamente</Text>
        </Pressable>
      </View>
    );
  }

  const formatLastUpdated = () => {
    if (!lastUpdated) return '';
    return lastUpdated.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <View>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Dashboard</Text>
          <Text style={[styles.headerDate, { color: colors.textSecondary }]}>{data?.date}</Text>
        </View>
        {lastUpdated && (
          <Text style={[styles.lastUpdated, { color: colors.textSecondary }]}>
            Atualizado {formatLastUpdated()}
          </Text>
        )}
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={refresh} tintColor={colors.accent} />
        }
      >
        {/* Insights proativos (novo!) */}
        <InsightsWidget onAction={handleInsightAction} />

        {/* Agenda do dia */}
        <AgendaWidget onAddEvent={handleAddEvent} />

        {/* Hábitos com quick-log */}
        <HabitsWidget />

        {/* Emails e alertas */}
        <EmailsWidget />

        {/* Vault stats */}
        <VaultWidget />

        {/* Memórias */}
        <MemoriesWidget />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    paddingHorizontal: spacing.lg,
    paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 32) + spacing.sm : spacing.sm,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
  },
  headerTitle: {
    fontSize: fontSize.xxl,
    fontWeight: '700',
  },
  headerDate: {
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  lastUpdated: {
    fontSize: fontSize.xs,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.md,
    paddingBottom: spacing.xxl,
  },
  emptyText: {
    fontSize: fontSize.sm,
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: spacing.sm,
  },
  errorText: {
    fontSize: fontSize.md,
    marginBottom: spacing.md,
  },
  retryButton: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  retryText: {
    fontSize: fontSize.md,
    fontWeight: '600',
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  statCard: {
    flex: 1,
    borderRadius: 8,
    padding: spacing.sm,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: fontSize.xl,
    fontWeight: '700',
  },
  statLabel: {
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  topicsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  topicChip: {
    borderRadius: 12,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  topicText: {
    fontSize: fontSize.sm,
  },
  alertRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: spacing.xs,
    gap: spacing.sm,
  },
  alertCategory: {
    fontSize: fontSize.sm,
    fontWeight: '600',
    backgroundColor: 'rgba(255,107,107,0.15)',
    borderRadius: 8,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    overflow: 'hidden',
    minWidth: 60,
    textAlign: 'center',
  },
  alertSummary: {
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  alertFrom: {
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  dismissButton: {
    marginTop: spacing.sm,
    paddingVertical: spacing.xs,
    alignItems: 'center',
    borderRadius: 8,
    borderWidth: 1,
  },
  dismissText: {
    fontSize: fontSize.sm,
  },
  emailRow: {
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
  },
  emailFrom: {
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  emailSubject: {
    fontSize: fontSize.md,
    marginTop: 2,
  },
  memoryRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: spacing.xs,
    gap: spacing.sm,
  },
  memoryCategory: {
    fontSize: fontSize.sm,
    fontWeight: '600',
    borderRadius: 8,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    overflow: 'hidden',
    minWidth: 60,
    textAlign: 'center',
  },
  memoryContent: {
    fontSize: fontSize.sm,
    flex: 1,
  },
});
