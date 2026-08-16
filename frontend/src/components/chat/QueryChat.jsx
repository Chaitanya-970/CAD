'use client';

import { useRef, useState } from 'react';
import { Bot, Send } from 'lucide-react';
import { api } from '@/lib/api';
import styles from './chat.module.css';

const SUGGESTIONS = [
  'Which villages are at risk?',
  'Where are the most SOS signals coming from?',
  'Suggest a safe zone for 500 people near Majuli',
];

const COOLDOWN_MS = 3000;

export default function QueryChat() {
  const [messages, setMessages] = useState([]); // { role: 'user'|'ai', text, error }
  const [input, setInput] = useState('');
  const [cooling, setCooling] = useState(false);
  const timeoutRef = useRef(null);

  const send = async (question) => {
    const q = (question ?? input).trim();
    if (!q || cooling) return;

    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    setInput('');
    setCooling(true);
    timeoutRef.current = setTimeout(() => setCooling(false), COOLDOWN_MS);

    try {
      const res = await api.query(q);
      setMessages((prev) => [...prev, { role: 'ai', text: res.answer || 'No answer returned.' }]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', error: true, text: "I couldn't process that query. Try rephrasing." },
      ]);
    }
  };

  return (
    <div className={styles.chatPanel}>
      <div className={styles.chatHeader}>
        <Bot size={16} /> Ask AFIP
      </div>

      <div className={styles.chatMessages}>
        {messages.length === 0 && (
          <div className={styles.chatEmpty}>
            Ask a question about current flood risk, SOS activity, or safe zones.
            <div className={styles.suggestions}>
              {SUGGESTIONS.map((s) => (
                <button key={s} className={styles.suggestionBtn} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={styles.bubbleRow}>
            <div className={m.role === 'user' ? styles.bubbleUser : `${styles.bubbleAi} ${m.error ? styles.bubbleAiError : ''}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>

      <div className={styles.inputRow}>
        <input
          className={styles.input}
          placeholder="Type your question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
        />
        <button className={styles.sendBtn} onClick={() => send()} disabled={cooling || !input.trim()}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
