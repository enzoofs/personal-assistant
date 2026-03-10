import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { DashboardData, fetchDashboard, getApiConfig, sendChat } from '../api/atlas';
import { Insight } from '../types';

const CACHE_KEY = 'dashboard_cache';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos
const REFRESH_INTERVAL = 60 * 1000; // 60 segundos

interface CachedData {
  data: DashboardData;
  timestamp: number;
}

interface DashboardContextType {
  data: DashboardData | null;
  insights: Insight[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  refresh: () => Promise<void>;
  logHabit: (habitType: string, value: string | number | boolean) => Promise<void>;
  dismissInsight: (id: string) => Promise<void>;
  dismissAllAlerts: () => Promise<void>;
}

const DashboardContext = createContext<DashboardContextType>({
  data: null,
  insights: [],
  loading: true,
  error: null,
  lastUpdated: null,
  refresh: async () => {},
  logHabit: async () => {},
  dismissInsight: async () => {},
  dismissAllAlerts: async () => {},
});

export function DashboardProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Carregar cache ao iniciar
  useEffect(() => {
    const loadCache = async () => {
      try {
        const cached = await AsyncStorage.getItem(CACHE_KEY);
        if (cached) {
          const { data: cachedData, timestamp }: CachedData = JSON.parse(cached);
          const age = Date.now() - timestamp;

          // Usa cache se tiver menos de 5 minutos
          if (age < CACHE_TTL) {
            setData(cachedData);
            setInsights((cachedData as any).insights || []);
            setLastUpdated(new Date(timestamp));
            setLoading(false);
          }
        }
      } catch {
        // Cache inválido, ignora
      }
    };
    loadCache();
  }, []);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await fetchDashboard();
      setData(result);
      setInsights((result as any).insights || []);
      setLastUpdated(new Date());

      // Salvar no cache
      const cacheData: CachedData = {
        data: result,
        timestamp: Date.now(),
      };
      await AsyncStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
    } catch (e: any) {
      const { baseUrl } = getApiConfig();
      const msg = e.message || 'Erro desconhecido';
      setError(`${baseUrl}\n${msg}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // Refresh periódico
  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [refresh]);

  const logHabit = useCallback(async (habitType: string, value: string | number | boolean) => {
    try {
      // Monta mensagem natural para o ATLAS
      let message: string;
      if (typeof value === 'boolean') {
        message = value ? `Registra que eu ${habitType} hoje` : `Registra que eu não ${habitType} hoje`;
      } else {
        message = `Registra ${habitType}: ${value}`;
      }

      await sendChat(message);
      // Refresh para atualizar os dados
      await refresh();
    } catch (e: any) {
      console.error('Erro ao logar hábito:', e);
      throw e;
    }
  }, [refresh]);

  const dismissInsight = useCallback(async (id: string) => {
    // Remove localmente
    setInsights(prev => prev.filter(i => i.id !== id));

    // TODO: Chamar API para persistir dismiss quando endpoint existir
    // await api.dismissInsight(id);
  }, []);

  const dismissAllAlerts = useCallback(async () => {
    try {
      const { default: api } = await import('../api/atlas');
      await api.dismissEmailAlerts();
      // Atualizar dados localmente
      if (data) {
        setData({ ...data, email_alerts: [] });
      }
    } catch (e: any) {
      console.error('Erro ao limpar alertas:', e);
    }
  }, [data]);

  return (
    <DashboardContext.Provider
      value={{
        data,
        insights,
        loading,
        error,
        lastUpdated,
        refresh,
        logHabit,
        dismissInsight,
        dismissAllAlerts,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboardContext() {
  return useContext(DashboardContext);
}
