import { ChatResponse } from '../types';

// Configurable at runtime via Settings screen
let BASE_URL = 'http://137.131.252.201:8000';
let API_KEY = 'dev-key';

export function configureApi(serverUrl: string, apiKey: string) {
  BASE_URL = serverUrl;
  API_KEY = apiKey;
}

export async function sendChat(message: string): Promise<ChatResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000); // 2 min for LLM

  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({ message }),
    signal: controller.signal,
  });
  clearTimeout(timeout);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export interface StreamEvent {
  type: 'token' | 'done';
  content?: string;
  intent?: string;
  actions?: Array<{ type: string; result: unknown }>;
  error?: string | null;
}

export async function sendChatStream(
  message: string,
  onToken: (token: string) => void,
  onDone: (data: { intent: string; actions: Array<{ type: string; result: unknown }>; error: string | null }) => void,
): Promise<void> {
  // React Native doesn't support ReadableStream, so we fallback to regular chat endpoint
  // and simulate streaming by delivering the response at once
  const response = await sendChat(message);

  // Deliver the full response as tokens (simulated streaming)
  const text = response.response;
  const chunkSize = 10; // characters per "token"

  for (let i = 0; i < text.length; i += chunkSize) {
    const chunk = text.slice(i, Math.min(i + chunkSize, text.length));
    onToken(chunk);
    // Small delay to create streaming effect
    await new Promise(resolve => setTimeout(resolve, 20));
  }

  onDone({
    intent: response.intent || 'chat',
    actions: (response.actions || []).map(a => ({ type: a.type, result: a.details })),
    error: response.error || null,
  });
}

export interface VoiceResponse extends ChatResponse {
  transcript: string;
  audio_base64: string;
}

export async function sendVoice(uri: string): Promise<VoiceResponse> {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'audio.m4a',
    type: 'audio/m4a',
  } as unknown as Blob);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);

  const response = await fetch(`${BASE_URL}/voice`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
    },
    body: formData,
    signal: controller.signal,
  });
  clearTimeout(timeout);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export interface DashboardData {
  date: string;
  events: Array<{ id: string; summary: string; start: string }>;
  habits: Array<{ type: string; value: string; unit: string; category: string }>;
  vault: {
    total_notes: number;
    total_links: number;
    orphan_notes: number;
    notes_today: number;
    top_topics: Array<[string, number]>;
  };
  recent_messages: Array<{ role: string; content: string }>;
  emails: Array<{ id: string; subject: string; from: string; snippet: string }>;
  memories: Array<{ content: string; category: string }>;
  email_alerts: Array<{ from: string; subject: string; category: string; summary: string; timestamp: string }>;
}

export async function fetchDashboard(): Promise<DashboardData> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000); // 30s

  const response = await fetch(`${BASE_URL}/dashboard`, {
    headers: { 'X-API-Key': API_KEY },
    signal: controller.signal,
  });
  clearTimeout(timeout);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function dismissEmailAlerts(): Promise<void> {
  await fetch(`${BASE_URL}/email-alerts`, {
    method: 'DELETE',
    headers: { 'X-API-Key': API_KEY },
  });
}

export async function checkHealth(): Promise<{ ok: boolean; error?: string }> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000); // 15s timeout
    const response = await fetch(`${BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    return { ok: response.ok, error: response.ok ? undefined : `HTTP ${response.status}` };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { ok: false, error: `${BASE_URL} - ${msg}` };
  }
}

export function getApiConfig() {
  return { baseUrl: BASE_URL, apiKey: API_KEY };
}

// --- Shopping List API ---

export interface ShoppingItem {
  id: number;
  item: string;
  quantity: string | null;
  category: string;
  completed: number;
  created_at: string;
  completed_at: string | null;
}

export async function fetchShoppingList(): Promise<{ items: ShoppingItem[]; count: number }> {
  const response = await fetch(`${BASE_URL}/shopping`, {
    headers: { 'X-API-Key': API_KEY },
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

export async function addShoppingItem(item: string, category: string = 'geral'): Promise<ShoppingItem> {
  const response = await fetch(`${BASE_URL}/shopping`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({ item, category }),
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

export async function completeShoppingItem(itemId: number, completed: boolean = true): Promise<void> {
  const response = await fetch(`${BASE_URL}/shopping/${itemId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({ completed }),
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
}

export async function deleteShoppingItem(itemId: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/shopping/${itemId}`, {
    method: 'DELETE',
    headers: { 'X-API-Key': API_KEY },
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
}
