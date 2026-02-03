import { useCallback, useEffect, useState } from 'react';
import { DashboardData, fetchDashboard, getApiConfig } from '../api/atlas';

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchDashboard();
      setData(result);
    } catch (e: any) {
      const { baseUrl } = getApiConfig();
      const msg = e.message || 'Erro desconhecido';
      setError(`${baseUrl}\n${msg}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 60000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { data, loading, error, refresh };
}
