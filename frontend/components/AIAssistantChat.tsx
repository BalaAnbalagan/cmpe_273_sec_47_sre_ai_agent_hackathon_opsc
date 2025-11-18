'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  images?: ViolationImage[];
  citations?: Citation[];
  metadata?: any;
}

interface ViolationImage {
  image_id: string;
  site_id: string;
  description: string;
  url: string;
  thumbnail_url: string;
  timestamp: string;
  violation_type?: string;
  similarity_score?: number;
}

interface Citation {
  document_id: string;
  text: string;
}

interface AIAssistantChatProps {
  isOpen: boolean;
  onClose: () => void;
  apiUrl: string;
}

export default function AIAssistantChat({ isOpen, onClose, apiUrl }: AIAssistantChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: "👋 Hello! I'm your AI Site Reliability Assistant. I can help you with:\n\n🔍 **Image Search** - Find site images using natural language\n💬 **Safety Analysis** - Analyze compliance violations\n📊 **RAG Chat** - Ask questions about your site data with AI-powered answers\n📋 **Log Analysis** - Query logs and error patterns\n\nWhat would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<ViolationImage | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const detectQueryIntent = (query: string): 'safety_analysis' | 'image_search' | 'rag_chat' | 'general' => {
    const lowerQuery = query.toLowerCase();

    // Safety analysis patterns
    if (lowerQuery.includes('violation') || lowerQuery.includes('safety') ||
        lowerQuery.includes('compliance') || lowerQuery.includes('hard hat') ||
        lowerQuery.includes('ppe') || lowerQuery.includes('hazard')) {
      return 'safety_analysis';
    }

    // Image search patterns
    if (lowerQuery.includes('find images') || lowerQuery.includes('show images') ||
        lowerQuery.includes('search images') || lowerQuery.includes('pictures of')) {
      return 'image_search';
    }

    // RAG chat patterns (questions)
    if (lowerQuery.includes('what') || lowerQuery.includes('how') ||
        lowerQuery.includes('why') || lowerQuery.includes('describe') ||
        lowerQuery.includes('explain') || lowerQuery.includes('tell me')) {
      return 'rag_chat';
    }

    return 'general';
  };

  const handleSafetyAnalysis = async (query: string) => {
    try {
      const response = await fetch(`${apiUrl}/sre/images/safety-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          custom_query: query,
          max_images: 12
        })
      });

      if (response.ok) {
        const data = await response.json();

        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: data.analysis || 'Safety analysis completed.',
          timestamp: new Date(),
          images: data.violation_images || [],
          metadata: {
            type: 'safety_analysis',
            images_analyzed: data.images_analyzed,
            rag_mode: data.rag_mode,
            query_used: data.query_used
          }
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Safety analysis failed');
      }
    } catch (error) {
      console.error('Safety analysis error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Sorry, I encountered an error analyzing safety compliance. Please try again.',
        timestamp: new Date()
      }]);
    }
  };

  const handleImageSearch = async (query: string) => {
    try {
      const response = await fetch(`${apiUrl}/sre/images/search-nl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          top_k: 10
        })
      });

      if (response.ok) {
        const data = await response.json();

        // Convert search results to ViolationImage format
        const images: ViolationImage[] = data.results.map((result: any) => ({
          image_id: result.image_id,
          site_id: result.metadata?.site_id || 'UNKNOWN',
          description: result.metadata?.description || 'No description',
          url: result.metadata?.url || '',
          thumbnail_url: result.metadata?.thumbnail_url || result.metadata?.url || '',
          timestamp: result.metadata?.timestamp || new Date().toISOString(),
          similarity_score: result.score
        }));

        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `🔍 Found ${data.count} images matching "${data.query}"`,
          timestamp: new Date(),
          images: images,
          metadata: {
            type: 'image_search',
            query: data.query,
            count: data.count
          }
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Image search failed');
      }
    } catch (error) {
      console.error('Image search error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Sorry, image search failed. Please try again.',
        timestamp: new Date()
      }]);
    }
  };

  const handleRAGChat = async (query: string) => {
    try {
      const response = await fetch(`${apiUrl}/sre/images/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          max_results: 10
        })
      });

      if (response.ok) {
        const data = await response.json();

        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: data.answer,
          timestamp: new Date(),
          citations: data.citations || [],
          metadata: {
            type: 'rag_chat',
            context_images: data.context_images
          }
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('RAG chat failed');
      }
    } catch (error) {
      console.error('RAG chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Sorry, I couldn\'t process your question. Please try again.',
        timestamp: new Date()
      }]);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const intent = detectQueryIntent(input);

      if (intent === 'safety_analysis') {
        await handleSafetyAnalysis(input);
      } else if (intent === 'image_search') {
        await handleImageSearch(input);
      } else if (intent === 'rag_chat') {
        await handleRAGChat(input);
      } else {
        // Default to RAG chat for general queries
        await handleRAGChat(input);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-6xl h-[90vh] bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-blue-500/30 shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 px-6 py-4 border-b border-blue-500/30 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <span className="text-3xl">🤖</span>
                AI Site Reliability Assistant
              </h2>
              <p className="text-blue-300 text-sm mt-1">Natural Language · RAG-Powered · Multi-Modal</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-3xl leading-none transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700/50 text-slate-100 border border-slate-600'
                }`}
              >
                {/* Message content */}
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </div>

                {/* Images grid */}
                {message.images && message.images.length > 0 && (
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3">
                    {message.images.map((image, idx) => (
                      <div
                        key={idx}
                        onClick={() => setSelectedImage(image)}
                        className="group relative bg-slate-800 rounded-lg overflow-hidden border border-slate-600 hover:border-blue-500/50 transition-all cursor-pointer hover:scale-105"
                      >
                        <div className="aspect-video relative overflow-hidden">
                          <img
                            src={image.thumbnail_url}
                            alt={image.description}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                          />
                          {image.similarity_score && (
                            <div className="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">
                              {(image.similarity_score * 100).toFixed(0)}%
                            </div>
                          )}
                        </div>
                        <div className="p-2">
                          <div className="text-blue-400 text-xs font-semibold">{image.site_id}</div>
                          <div className="text-white text-xs line-clamp-2 mt-1">
                            {image.description}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Citations */}
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <div className="text-xs text-slate-400 font-semibold">📚 Citations:</div>
                    {message.citations.map((citation, idx) => (
                      <div key={idx} className="text-xs bg-slate-800/50 rounded p-2 border-l-2 border-blue-500">
                        {citation.text}
                      </div>
                    ))}
                  </div>
                )}

                {/* Metadata */}
                {message.metadata && (
                  <div className="mt-3 text-xs text-slate-400 flex items-center gap-3">
                    {message.metadata.type === 'safety_analysis' && (
                      <>
                        <span>⚠️ Safety Analysis</span>
                        <span>·</span>
                        <span>{message.metadata.images_analyzed} images</span>
                        {message.metadata.rag_mode && (
                          <>
                            <span>·</span>
                            <span>🧠 BP RAG</span>
                          </>
                        )}
                      </>
                    )}
                    {message.metadata.type === 'image_search' && (
                      <>
                        <span>🔍 Image Search</span>
                        <span>·</span>
                        <span>{message.metadata.count} results</span>
                      </>
                    )}
                    {message.metadata.type === 'rag_chat' && (
                      <>
                        <span>💬 RAG Chat</span>
                        <span>·</span>
                        <span>{message.metadata.context_images} context images</span>
                      </>
                    )}
                  </div>
                )}

                <div className="text-xs text-slate-500 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                <div className="flex items-center gap-2">
                  <div className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                  <span className="text-slate-300 text-sm">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-slate-900/80 px-6 py-4 border-t border-slate-700 flex-shrink-0">
          <div className="flex gap-3 items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything... (e.g., 'Find safety violations', 'What are the hard hat requirements?', 'Show turbine images')"
              className="flex-1 px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500/50 resize-none"
              rows={2}
              disabled={loading}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-300 rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed h-[58px]"
            >
              Send
            </button>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            💡 Try: "Find workers without hard hats" · "What safety violations exist?" · "Show turbine site images"
          </div>
        </div>
      </div>

      {/* Image Detail Modal */}
      {selectedImage && (
        <div
          className="absolute inset-0 flex items-center justify-center p-4 bg-black/90 z-10"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl w-full" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-12 right-0 text-white/70 hover:text-white text-4xl"
            >
              ×
            </button>
            <img
              src={selectedImage.url}
              alt={selectedImage.description}
              className="w-full rounded-lg shadow-2xl"
            />
            <div className="mt-4 bg-slate-800 rounded-lg p-4">
              <div className="text-white font-semibold text-lg mb-2">{selectedImage.description}</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">Site:</span>{' '}
                  <span className="text-white">{selectedImage.site_id}</span>
                </div>
                {selectedImage.violation_type && (
                  <div>
                    <span className="text-slate-400">Type:</span>{' '}
                    <span className="text-red-400">{selectedImage.violation_type}</span>
                  </div>
                )}
                <div>
                  <span className="text-slate-400">Detected:</span>{' '}
                  <span className="text-white">{selectedImage.timestamp}</span>
                </div>
                <div>
                  <span className="text-slate-400">ID:</span>{' '}
                  <span className="text-slate-300 font-mono text-xs">{selectedImage.image_id}</span>
                </div>
                {selectedImage.similarity_score && (
                  <div>
                    <span className="text-slate-400">Relevance:</span>{' '}
                    <span className="text-blue-400">{(selectedImage.similarity_score * 100).toFixed(1)}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
