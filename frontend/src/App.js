import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Moon, Sparkles, BookOpen, TrendingUp, Loader2, Plus, Trash2, X, MessageCircle, Send, User, Bot } from 'lucide-react';
import { format } from 'date-fns';
import './index.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const EMOTIONS = [
  'Happy', 'Sad', 'Anxious', 'Peaceful', 'Confused', 
  'Excited', 'Scared', 'Calm', 'Angry', 'Hopeful'
];

function App() {
  const [activeTab, setActiveTab] = useState('new');
  
  const getUserId = () => {
    let userId = localStorage.getItem('dreamUserId');
    if (!userId) {
      userId = 'user_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('dreamUserId', userId);
    }
    return userId;
  };
  
  const [userId] = useState(getUserId());
  const [dreams, setDreams] = useState([]);
  const [selectedDream, setSelectedDream] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    emotions: []
  });

  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (activeTab === 'journal') {
      loadDreams();
    } else if (activeTab === 'patterns') {
      loadPatterns();
    }
  }, [activeTab]);

  const loadDreams = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/dreams/${userId}`);
      setDreams(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dreams');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadPatterns = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/dreams/${userId}/patterns`);
      setPatterns(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load patterns');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.description) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post(`${API_URL}/dreams`, {
        user_id: userId,
        title: formData.title,
        description: formData.description,
        emotions: formData.emotions
      });

      setSelectedDream(response.data);
      setFormData({ title: '', description: '', emotions: [] });
      setActiveTab('result');
    } catch (err) {
      setError('Failed to analyze dream. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleEmotion = (emotion) => {
    setFormData(prev => ({
      ...prev,
      emotions: prev.emotions.includes(emotion)
        ? prev.emotions.filter(e => e !== emotion)
        : [...prev.emotions, emotion]
    }));
  };

  const deleteDream = async (dreamId) => {
    if (!window.confirm('Are you sure you want to delete this dream?')) return;
    
    try {
      await axios.delete(`${API_URL}/dreams/${dreamId}`);
      loadDreams();
    } catch (err) {
      setError('Failed to delete dream');
      console.error(err);
    }
  };

  const loadChatHistory = async (dreamId) => {
    try {
      const response = await axios.get(`${API_URL}/dreams/${dreamId}/chat`);
      setChatMessages(response.data);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedDream) return;

    const userMessage = chatInput;
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await axios.post(`${API_URL}/dreams/${selectedDream.id}/chat`, {
        dream_id: selectedDream.id,
        message: userMessage
      });

      await loadChatHistory(selectedDream.id);
      
      setTimeout(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setError('Failed to send message');
      console.error(err);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  useEffect(() => {
    if (showChat && selectedDream) {
      loadChatHistory(selectedDream.id);
    }
  }, [showChat, selectedDream]);

  return (
    <div className="app-container">
      <header className="header">
        <h1><Moon size={48} style={{ display: 'inline', marginRight: '1rem' }} />Dream Interpreter</h1>
        <p>Unlock the symbolic meaning of your dreams</p>
      </header>

      <main className="main-content">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'new' ? 'active' : ''}`}
            onClick={() => setActiveTab('new')}
          >
            <Plus size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
            New Dream
          </button>
          <button 
            className={`tab ${activeTab === 'journal' ? 'active' : ''}`}
            onClick={() => setActiveTab('journal')}
          >
            <BookOpen size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
            Dream Journal
          </button>
          <button 
            className={`tab ${activeTab === 'patterns' ? 'active' : ''}`}
            onClick={() => setActiveTab('patterns')}
          >
            <TrendingUp size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
            Patterns
          </button>
        </div>

        {error && (
          <div className="error">
            <span>{error}</span>
            <button className="error-close" onClick={() => setError(null)}>
              <X size={20} />
            </button>
          </div>
        )}

        {activeTab === 'new' && (
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={24} />
              Record Your Dream
            </h2>
            
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label>Dream Title *</label>
                <input
                  type="text"
                  placeholder="Give your dream a title..."
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="input-group">
                <label>Dream Description *</label>
                <textarea
                  placeholder="Describe your dream in as much detail as you can remember..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="input-group">
                <label>How did you feel? (Select all that apply)</label>
                <div className="emotion-tags">
                  {EMOTIONS.map(emotion => (
                    <button
                      key={emotion}
                      type="button"
                      className={`emotion-tag ${formData.emotions.includes(emotion) ? 'selected' : ''}`}
                      onClick={() => toggleEmotion(emotion)}
                      disabled={loading}
                    >
                      {emotion}
                    </button>
                  ))}
                </div>
              </div>

              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 size={20} className="loading-spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles size={20} />
                    Analyze Dream
                  </>
                )}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'result' && selectedDream && (
          <div className="card">
            <h2>{selectedDream.title}</h2>
            <p className="date">{format(new Date(selectedDream.created_at), 'PPpp')}</p>
            
            <div style={{ marginTop: '1rem' }}>
              <strong>Your Dream:</strong>
              <p style={{ marginTop: '0.5rem', lineHeight: '1.6' }}>{selectedDream.description}</p>
            </div>

            {selectedDream.emotions && selectedDream.emotions.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <strong>Emotions:</strong>
                <div className="emotion-tags" style={{ marginTop: '0.5rem' }}>
                  {selectedDream.emotions.map(emotion => (
                    <span key={emotion} className="emotion-tag selected">{emotion}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="interpretation-section">
              <h2><Sparkles size={24} />Interpretation</h2>
              <div className="interpretation-text">{selectedDream.interpretation}</div>
            </div>

            {selectedDream.symbols && selectedDream.symbols.length > 0 && (
              <div className="interpretation-section">
                <h2>Key Symbols</h2>
                <div className="symbols-grid">
                  {selectedDream.symbols.map((symbol, idx) => (
                    <div key={idx} className="symbol-card">
                      <h4>{symbol.symbol}</h4>
                      <p>{symbol.meaning}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="chat-section">
              {!showChat ? (
                <button 
                  className="chat-toggle-btn"
                  onClick={() => setShowChat(true)}
                >
                  <MessageCircle size={20} />
                  Ask Follow-up Questions
                </button>
              ) : (
                <>
                  <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <MessageCircle size={24} />
                    Chat About Your Dream
                  </h2>
                  
                  <div className="chat-container">
                    {chatMessages.length === 0 ? (
                      <div className="chat-empty">
                        <MessageCircle size={48} style={{ opacity: 0.3 }} />
                        <p>Ask me anything about your dream! I can help you explore deeper meanings, clarify symbols, or discuss specific aspects.</p>
                      </div>
                    ) : (
                      <div className="chat-messages">
                        {chatMessages.map((msg) => (
                          <div key={msg.id} className={`chat-message ${msg.role}`}>
                            <div className="chat-avatar">
                              {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                            </div>
                            <div className="chat-bubble">
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        <div ref={chatEndRef} />
                      </div>
                    )}
                    
                    <div className="chat-input-container">
                      <input
                        type="text"
                        className="chat-input"
                        placeholder="Ask a question about your dream..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyPress={handleChatKeyPress}
                        disabled={chatLoading}
                      />
                      <button 
                        className="chat-send-btn"
                        onClick={sendChatMessage}
                        disabled={chatLoading || !chatInput.trim()}
                      >
                        {chatLoading ? (
                          <Loader2 size={20} className="loading-spinner" />
                        ) : (
                          <Send size={20} />
                        )}
                      </button>
                    </div>
                  </div>
                  
                  <button 
                    className="btn btn-secondary"
                    style={{ marginTop: '1rem' }}
                    onClick={() => setShowChat(false)}
                  >
                    Hide Chat
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {activeTab === 'journal' && (
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BookOpen size={24} />
              Your Dream Journal
            </h2>
            
            {loading ? (
              <div className="loading">
                <Loader2 size={40} className="loading-spinner" />
                <p>Loading dreams...</p>
              </div>
            ) : dreams.length === 0 ? (
              <div className="empty-state">
                <Moon size={64} />
                <p>No dreams recorded yet. Start by recording your first dream!</p>
              </div>
            ) : (
              <div className="dream-list">
                {dreams.map(dream => (
                  <div 
                    key={dream.id} 
                    className="dream-item"
                    onClick={() => {
                      setSelectedDream(dream);
                      setActiveTab('result');
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <h3>{dream.title}</h3>
                        <p className="date">{format(new Date(dream.created_at), 'PPP')}</p>
                        <p className="preview">{dream.description.substring(0, 150)}...</p>
                      </div>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '0.5rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteDream(dream.id);
                        }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'patterns' && (
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp size={24} />
              Dream Patterns Analysis
            </h2>
            
            {loading ? (
              <div className="loading">
                <Loader2 size={40} className="loading-spinner" />
                <p>Analyzing patterns...</p>
              </div>
            ) : patterns && patterns.pattern_analysis ? (
              <div className="pattern-analysis">
                {patterns.pattern_analysis}
              </div>
            ) : (
              <div className="empty-state">
                <TrendingUp size={64} />
                <p>{patterns?.message || 'Record more dreams to see patterns and insights.'}</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
