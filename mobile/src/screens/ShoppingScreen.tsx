import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList,
  Platform,
  Pressable,
  RefreshControl,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme';
import {
  fetchShoppingList,
  addShoppingItem,
  completeShoppingItem,
  deleteShoppingItem,
  ShoppingItem,
} from '../api/atlas';
import { Confetti } from '../components/Confetti';
import { Haptic } from '../utils/haptics';

const CATEGORIES = ['geral', 'mercado', 'farmácia', 'limpeza'];

export function ShoppingScreen() {
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [newItem, setNewItem] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('geral');
  const [error, setError] = useState<string | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  const loadItems = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchShoppingList();
      setItems(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao carregar lista');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadItems();
  };

  const handleAddItem = async () => {
    const trimmed = newItem.trim();
    if (!trimmed) return;

    try {
      const item = await addShoppingItem(trimmed, selectedCategory);
      setItems(prev => [{ ...item, completed: 0, created_at: new Date().toISOString(), completed_at: null } as ShoppingItem, ...prev]);
      setNewItem('');
      Haptic.success();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao adicionar item');
      Haptic.error();
    }
  };

  const handleToggleComplete = async (item: ShoppingItem) => {
    const newCompleted = !item.completed;
    try {
      await completeShoppingItem(item.id, newCompleted);
      setItems(prev =>
        prev.map(i =>
          i.id === item.id ? { ...i, completed: newCompleted ? 1 : 0 } : i
        )
      );

      // Trigger confetti and haptic when completing an item
      if (newCompleted) {
        Haptic.celebration();
        setShowConfetti(true);
      } else {
        Haptic.light();
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao atualizar item');
    }
  };

  const handleDelete = async (itemId: number) => {
    Haptic.medium();
    try {
      await deleteShoppingItem(itemId);
      setItems(prev => prev.filter(i => i.id !== itemId));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao deletar item');
      Haptic.error();
    }
  };

  const handleCategorySelect = (cat: string) => {
    if (cat !== selectedCategory) {
      Haptic.selection();
      setSelectedCategory(cat);
    }
  };

  // Group items by category
  const groupedItems = items.reduce((acc, item) => {
    const cat = item.category || 'geral';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, ShoppingItem[]>);

  const renderItem = ({ item }: { item: ShoppingItem }) => (
    <View style={styles.itemRow}>
      <Pressable
        style={styles.checkbox}
        onPress={() => handleToggleComplete(item)}
      >
        <Ionicons
          name={item.completed ? 'checkbox' : 'square-outline'}
          size={24}
          color={item.completed ? colors.success : colors.textSecondary}
        />
      </Pressable>
      <Text style={[styles.itemText, item.completed && styles.itemCompleted]}>
        {item.item}
        {item.quantity && <Text style={styles.quantity}> ({item.quantity})</Text>}
      </Text>
      <Pressable style={styles.deleteBtn} onPress={() => handleDelete(item.id)}>
        <Ionicons name="trash-outline" size={20} color={colors.error} />
      </Pressable>
    </View>
  );

  const renderCategory = (category: string) => {
    const categoryItems = groupedItems[category];
    if (!categoryItems || categoryItems.length === 0) return null;

    return (
      <View key={category} style={styles.categorySection}>
        <Text style={styles.categoryTitle}>{category.charAt(0).toUpperCase() + category.slice(1)}</Text>
        {categoryItems.map(item => (
          <View key={item.id}>{renderItem({ item })}</View>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />

      {/* Confetti celebration */}
      <Confetti
        active={showConfetti}
        onComplete={() => setShowConfetti(false)}
        originY={200}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Lista de Compras</Text>
        <Text style={styles.subtitle}>{items.filter(i => !i.completed).length} itens pendentes</Text>
      </View>

      {/* Add Item */}
      <View style={styles.addSection}>
        <View style={styles.categoryPicker}>
          {CATEGORIES.map(cat => (
            <Pressable
              key={cat}
              style={[styles.categoryChip, selectedCategory === cat && styles.categoryChipActive]}
              onPress={() => handleCategorySelect(cat)}
            >
              <Text style={[styles.categoryChipText, selectedCategory === cat && styles.categoryChipTextActive]}>
                {cat}
              </Text>
            </Pressable>
          ))}
        </View>
        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            value={newItem}
            onChangeText={setNewItem}
            placeholder="Adicionar item..."
            placeholderTextColor={colors.textSecondary}
            onSubmitEditing={handleAddItem}
            returnKeyType="done"
          />
          <Pressable
            style={[styles.addBtn, !newItem.trim() && styles.addBtnDisabled]}
            onPress={handleAddItem}
            disabled={!newItem.trim()}
          >
            <Ionicons name="add" size={24} color={newItem.trim() ? colors.text : colors.textSecondary} />
          </Pressable>
        </View>
      </View>

      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* List */}
      <FlatList
        data={Object.keys(groupedItems)}
        keyExtractor={item => item}
        renderItem={({ item: category }) => renderCategory(category)}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={colors.accent}
          />
        }
        ListEmptyComponent={
          !loading ? (
            <View style={styles.empty}>
              <Ionicons name="cart-outline" size={64} color={colors.textSecondary} />
              <Text style={styles.emptyText}>Lista vazia</Text>
              <Text style={styles.emptySubtext}>Diga "preciso comprar..." no chat</Text>
            </View>
          ) : null
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 32) + spacing.sm : spacing.sm,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    color: colors.text,
    fontSize: fontSize.xl,
    fontWeight: '700',
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: 2,
  },
  addSection: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  categoryPicker: {
    flexDirection: 'row',
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  categoryChip: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  categoryChipActive: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  categoryChipText: {
    color: colors.textSecondary,
    fontSize: fontSize.xs,
  },
  categoryChipTextActive: {
    color: colors.text,
    fontWeight: '600',
  },
  inputRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  input: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 12,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    color: colors.text,
    fontSize: fontSize.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  addBtn: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addBtnDisabled: {
    backgroundColor: colors.surface,
  },
  errorBanner: {
    backgroundColor: colors.error,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  errorText: {
    color: colors.text,
    fontSize: fontSize.sm,
  },
  list: {
    paddingVertical: spacing.sm,
  },
  categorySection: {
    paddingHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  categoryTitle: {
    color: colors.accent,
    fontSize: fontSize.sm,
    fontWeight: '600',
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginBottom: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
  checkbox: {
    marginRight: spacing.sm,
  },
  itemText: {
    flex: 1,
    color: colors.text,
    fontSize: fontSize.md,
  },
  itemCompleted: {
    textDecorationLine: 'line-through',
    color: colors.textSecondary,
  },
  quantity: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
  },
  deleteBtn: {
    padding: spacing.xs,
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    color: colors.textSecondary,
    fontSize: fontSize.lg,
    marginTop: spacing.md,
  },
  emptySubtext: {
    color: colors.textSecondary,
    fontSize: fontSize.sm,
    marginTop: spacing.xs,
  },
});
