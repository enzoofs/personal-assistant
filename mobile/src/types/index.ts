export interface ActionResult {
  type: string;
  details: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  intent: string;
  actions: ActionResult[];
  error: string | null;
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  intent?: string;
  actions?: ActionResult[];
  error?: string | null;
}
