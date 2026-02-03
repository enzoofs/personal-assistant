import { useCallback, useRef, useState } from 'react';
import { sendChatStream, sendVoice, VoiceResponse } from '../api/atlas';
import { Message } from '../types';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const streamingMsgId = useRef<string | null>(null);

  const addUserMessage = (text: string): void => {
    const msg: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, msg]);
  };

  const addBotMessage = (text: string, intent?: string, actions?: Message['actions'], error?: string | null): void => {
    const msg: Message = {
      id: (Date.now() + 1).toString(),
      text,
      isUser: false,
      timestamp: new Date(),
      intent,
      actions,
      error,
    };
    setMessages(prev => [...prev, msg]);
  };

  const addErrorMessage = (err: unknown): void => {
    addBotMessage('Erro de conexão com o ATLAS.', undefined, undefined, String(err));
  };

  const send = useCallback(async (text: string) => {
    addUserMessage(text);
    setLoading(true);

    // Create placeholder message for streaming
    const botMsgId = (Date.now() + 1).toString();
    streamingMsgId.current = botMsgId;
    const botMsg: Message = {
      id: botMsgId,
      text: '',
      isUser: false,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, botMsg]);

    try {
      await sendChatStream(
        text,
        // On each token
        (token) => {
          setMessages(prev =>
            prev.map(m =>
              m.id === streamingMsgId.current ? { ...m, text: m.text + token } : m
            )
          );
        },
        // On done
        (data) => {
          setMessages(prev =>
            prev.map(m =>
              m.id === streamingMsgId.current
                ? { ...m, intent: data.intent, actions: data.actions, error: data.error }
                : m
            )
          );
          streamingMsgId.current = null;
        }
      );
    } catch (err) {
      // Replace streaming message with error
      setMessages(prev =>
        prev.map(m =>
          m.id === streamingMsgId.current
            ? { ...m, text: 'Erro de conexão com o ATLAS.', error: String(err) }
            : m
        )
      );
      streamingMsgId.current = null;
    } finally {
      setLoading(false);
    }
  }, []);

  const sendAudio = useCallback(async (uri: string): Promise<VoiceResponse | null> => {
    setLoading(true);
    try {
      const data = await sendVoice(uri);
      addUserMessage(data.transcript);
      addBotMessage(data.response, data.intent, data.actions, data.error);
      return data;
    } catch (err) {
      addErrorMessage(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, send, sendAudio };
}
