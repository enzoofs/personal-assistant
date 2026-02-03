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
import { colors, fontSize, spacing } from '../theme';
import { dismissEmailAlerts } from '../api/atlas';
import { useDashboard } from '../hooks/useDashboard';

function Section({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{icon}  {title}</Text>
      {children}
    </View>
  );
}

function formatTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoString;
  }
}

export function DashboardScreen() {
  const { data, loading, error, refresh } = useDashboard();

  if (loading && !data) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  if (error && !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard</Text>
        <Text style={styles.headerDate}>{data?.date}</Text>
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={refresh} tintColor={colors.accent} />
        }
      >
        {/* Important Email Alerts */}
        {data?.email_alerts && data.email_alerts.length > 0 && (
          <Section title="Atenção" icon="🚨">
            {data.email_alerts.map((alert, i) => (
              <View key={i} style={styles.alertRow}>
                <Text style={styles.alertCategory}>{alert.category}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.alertSummary}>{alert.summary}</Text>
                  <Text style={styles.alertFrom} numberOfLines={1}>{alert.from}</Text>
                </View>
              </View>
            ))}
            <Pressable
              style={styles.dismissButton}
              onPress={() => { dismissEmailAlerts().then(refresh); }}
            >
              <Text style={styles.dismissText}>Dispensar alertas</Text>
            </Pressable>
          </Section>
        )}

        {/* Events */}
        <Section title="Agenda de Hoje" icon="📅">
          {data?.events && data.events.length > 0 ? (
            data.events.map((event) => (
              <View key={event.id} style={styles.row}>
                <Text style={styles.rowTime}>{formatTime(event.start)}</Text>
                <Text style={styles.rowText}>{event.summary}</Text>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>Nenhum evento hoje</Text>
          )}
        </Section>

        {/* Habits */}
        <Section title="Hábitos" icon="💪">
          {data?.habits && data.habits.length > 0 ? (
            data.habits.map((habit, i) => (
              <View key={i} style={styles.row}>
                <Text style={styles.rowLabel}>{habit.type}</Text>
                <Text style={styles.rowValue}>
                  {habit.value} {habit.unit}
                </Text>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>Nenhum hábito registrado hoje</Text>
          )}
        </Section>

        {/* Vault */}
        <Section title="Vault" icon="📝">
          {data?.vault && data.vault.total_notes > 0 ? (
            <>
              <View style={styles.statsRow}>
                <View style={styles.statCard}>
                  <Text style={styles.statNumber}>{data.vault.total_notes}</Text>
                  <Text style={styles.statLabel}>Notas</Text>
                </View>
                <View style={styles.statCard}>
                  <Text style={styles.statNumber}>{data.vault.notes_today}</Text>
                  <Text style={styles.statLabel}>Hoje</Text>
                </View>
                <View style={styles.statCard}>
                  <Text style={styles.statNumber}>{data.vault.total_links}</Text>
                  <Text style={styles.statLabel}>Links</Text>
                </View>
              </View>
              {data.vault.top_topics && data.vault.top_topics.length > 0 && (
                <View style={styles.topicsRow}>
                  {data.vault.top_topics.slice(0, 5).map(([topic, count]) => (
                    <View key={topic} style={styles.topicChip}>
                      <Text style={styles.topicText}>{topic} ({count})</Text>
                    </View>
                  ))}
                </View>
              )}
            </>
          ) : (
            <Text style={styles.emptyText}>Vault vazio</Text>
          )}
        </Section>

        {/* Emails */}
        <Section title="Emails Não Lidos" icon="✉️">
          {data?.emails && data.emails.length > 0 ? (
            data.emails.map((email) => (
              <View key={email.id} style={styles.emailRow}>
                <Text style={styles.emailFrom} numberOfLines={1}>{email.from}</Text>
                <Text style={styles.emailSubject} numberOfLines={1}>{email.subject}</Text>
                <Text style={styles.emailSnippet} numberOfLines={2}>{email.snippet}</Text>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>Nenhum email não lido</Text>
          )}
        </Section>

        {/* Memories */}
        <Section title="Memórias" icon="🧠">
          {data?.memories && data.memories.length > 0 ? (
            data.memories.map((mem, i) => (
              <View key={i} style={styles.memoryRow}>
                <Text style={styles.memoryCategory}>{mem.category}</Text>
                <Text style={styles.memoryContent} numberOfLines={2}>{mem.content}</Text>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>Nenhuma memória ainda</Text>
          )}
        </Section>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centered: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
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
  headerDate: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.md,
    paddingBottom: spacing.xxl,
  },
  section: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sectionTitle: {
    color: colors.text,
    fontSize: fontSize.lg,
    fontWeight: '600',
    marginBottom: spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.xs,
    gap: spacing.sm,
  },
  rowTime: {
    color: colors.accent,
    fontSize: fontSize.md,
    fontWeight: '600',
    minWidth: 50,
  },
  rowText: {
    color: colors.text,
    fontSize: fontSize.md,
    flex: 1,
  },
  rowLabel: {
    color: colors.textSecondary,
    fontSize: fontSize.md,
    flex: 1,
  },
  rowValue: {
    color: colors.text,
    fontSize: fontSize.md,
    fontWeight: '600',
  },
  emptyText: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    fontStyle: 'italic',
  },
  errorText: {
    color: colors.error,
    fontSize: fontSize.md,
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.surfaceLight,
    borderRadius: 8,
    padding: spacing.sm,
    alignItems: 'center',
  },
  statNumber: {
    color: colors.accent,
    fontSize: fontSize.xl,
    fontWeight: '700',
  },
  statLabel: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  topicsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  topicChip: {
    backgroundColor: colors.surfaceLight,
    borderRadius: 12,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  topicText: {
    color: colors.accent,
    fontSize: fontSize.sm,
  },
  alertRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: spacing.xs,
    gap: spacing.sm,
  },
  alertCategory: {
    color: '#FF6B6B',
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
    color: colors.text,
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  alertFrom: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  dismissButton: {
    marginTop: spacing.sm,
    paddingVertical: spacing.xs,
    alignItems: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  dismissText: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
  },
  emailRow: {
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  emailFrom: {
    color: colors.accent,
    fontSize: fontSize.sm,
    fontWeight: '600',
  },
  emailSubject: {
    color: colors.text,
    fontSize: fontSize.md,
    marginTop: 2,
  },
  emailSnippet: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  memoryRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: spacing.xs,
    gap: spacing.sm,
  },
  memoryCategory: {
    color: colors.accent,
    fontSize: fontSize.sm,
    fontWeight: '600',
    backgroundColor: colors.surfaceLight,
    borderRadius: 8,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    overflow: 'hidden',
    minWidth: 60,
    textAlign: 'center',
  },
  memoryContent: {
    color: colors.text,
    fontSize: fontSize.sm,
    flex: 1,
  },
});
