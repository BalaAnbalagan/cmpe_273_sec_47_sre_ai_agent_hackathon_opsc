'use client';

import { useEffect, useState } from 'react';
import ViolationsDialog from '@/components/ViolationsDialog';
import AIAssistantChat from '@/components/AIAssistantChat';

interface BackendStatus {
  deployment: {
    status: string;
    version: string;
    region: string;
    zone: string;
    environment: string;
  };
  azure_services: {
    key_vault: string;
    redis_cache: string;
    cosmos_db: string;
    cohere_api: string;
    mqtt_broker: string;
    rabbitmq_broker: string;
  };
}

interface CohereStatus {
  available: boolean;
  embed_model: string;
  chat_model: string;
}

interface DeploymentVersion {
  version: string;
  region: string;
  active_zone: string;
  environment: string;
}

export default function Home() {
  const [az1Status, setAz1Status] = useState<BackendStatus | null>(null);
  const [az2Status, setAz2Status] = useState<BackendStatus | null>(null);
  const [az1Version, setAz1Version] = useState<DeploymentVersion | null>(null);
  const [az2Version, setAz2Version] = useState<DeploymentVersion | null>(null);
  const [cohereStatus, setCohereStatus] = useState<CohereStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeZone, setActiveZone] = useState<'az1' | 'az2'>('az1');
  const [uptime, setUptime] = useState(0);
  const [showViolationsDialog, setShowViolationsDialog] = useState(false);
  const [showAIChat, setShowAIChat] = useState(false);
  const [chatContext, setChatContext] = useState<'general' | 'natural_language_search' | 'safety_compliance' | 'rag_chat' | 'log_diagnostics'>('general');
  const [selectedService, setSelectedService] = useState<{ name: string; status: string; icon: string } | null>(null);

  const API_AZ1 = 'https://sre-backend-az1.azurewebsites.net';
  const API_AZ2 = 'https://sre-backend-az2.azurewebsites.net';

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const activeAPI = activeZone === 'az1' ? API_AZ1 : API_AZ2;

        // Fetch version info from both zones (lightweight)
        // Fetch full status only from active zone
        const [az1Ver, az2Ver, statusRes, cohereRes] = await Promise.all([
          fetch(`${API_AZ1}/sre/deployment-version`).then(r => r.ok ? r.json() : null),
          fetch(`${API_AZ2}/sre/deployment-version`).then(r => r.ok ? r.json() : null),
          fetch(`${activeAPI}/sre/status`).then(r => r.ok ? r.json() : null),
          fetch(`${activeAPI}/sre/images/cohere-status`).then(r => r.ok ? r.json() : null),
        ]);

        // Update version info for both zones
        setAz1Version(az1Ver);
        setAz2Version(az2Ver);

        // Update full status only for active zone
        if (activeZone === 'az1') {
          setAz1Status(statusRes);
        } else {
          setAz2Status(statusRes);
        }

        setCohereStatus(cohereRes);
      } catch (error) {
        console.error('Error fetching status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, [activeZone]);

  useEffect(() => {
    const timer = setInterval(() => setUptime(u => u + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const currentStatus = activeZone === 'az1' ? az1Status : az2Status;
  const currentVersion = activeZone === 'az1' ? az1Version : az2Version;
  const az1Online = az1Status !== null;
  const az2Online = az2Status !== null;

  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}h ${m}m ${s}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Top Bar */}
      <div className="bg-slate-900/90 backdrop-blur border-b border-blue-500/30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">⚡</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Enterprise SRE Dashboard</h1>
              <p className="text-blue-300 text-sm">Tier-0 Reliability Engineering Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <div className="text-blue-300 text-xs uppercase tracking-wide">Uptime</div>
              <div className="text-white font-mono text-lg">{formatUptime(uptime)}</div>
            </div>
            <div className="text-right">
              <div className="text-blue-300 text-xs uppercase tracking-wide">Target SLA</div>
              <div className="text-green-400 font-bold text-lg">99.99999%</div>
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent"></div>
              <p className="text-blue-300 mt-4 text-lg">Initializing monitoring systems...</p>
            </div>
          </div>
        ) : (
          <>
            {/* Zone Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {/* AZ1 Card */}
              <button
                onClick={() => setActiveZone('az1')}
                className={`relative overflow-hidden rounded-xl border-2 transition-all ${
                  activeZone === 'az1'
                    ? 'border-blue-500 shadow-2xl shadow-blue-500/50'
                    : 'border-slate-700 hover:border-slate-600'
                } bg-gradient-to-br from-slate-800 to-slate-900 p-6`}
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full blur-2xl"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-blue-300 text-sm font-medium mb-1">AVAILABILITY ZONE 1</div>
                      <div className="text-3xl font-bold text-white">
                        West US 2 - {activeZone === 'az1' ? 'Primary' : 'Secondary'}
                      </div>
                    </div>
                    {az1Online && (
                      <div className="flex items-center gap-2 bg-green-500/20 px-4 py-2 rounded-full">
                        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="text-green-400 font-semibold">ONLINE</span>
                      </div>
                    )}
                  </div>
                  {az1Version && (
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div className="bg-slate-900/50 rounded-lg p-3">
                        <div className="text-slate-400 text-xs mb-1">Version</div>
                        <div className="text-white font-mono text-sm">{az1Version.version}</div>
                      </div>
                      <div className="bg-slate-900/50 rounded-lg p-3">
                        <div className="text-slate-400 text-xs mb-1">Environment</div>
                        <div className="text-white font-mono text-sm">{az1Version.environment}</div>
                      </div>
                    </div>
                  )}
                </div>
              </button>

              {/* AZ2 Card */}
              <button
                onClick={() => setActiveZone('az2')}
                className={`relative overflow-hidden rounded-xl border-2 transition-all ${
                  activeZone === 'az2'
                    ? 'border-cyan-500 shadow-2xl shadow-cyan-500/50'
                    : 'border-slate-700 hover:border-slate-600'
                } bg-gradient-to-br from-slate-800 to-slate-900 p-6`}
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-cyan-500/20 to-transparent rounded-full blur-2xl"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-cyan-300 text-sm font-medium mb-1">AVAILABILITY ZONE 2</div>
                      <div className="text-3xl font-bold text-white">
                        West US 2 - {activeZone === 'az2' ? 'Primary' : 'Secondary'}
                      </div>
                    </div>
                    {az2Online && (
                      <div className="flex items-center gap-2 bg-green-500/20 px-4 py-2 rounded-full">
                        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="text-green-400 font-semibold">ONLINE</span>
                      </div>
                    )}
                  </div>
                  {az2Version && (
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div className="bg-slate-900/50 rounded-lg p-3">
                        <div className="text-slate-400 text-xs mb-1">Version</div>
                        <div className="text-white font-mono text-sm">{az2Version.version}</div>
                      </div>
                      <div className="bg-slate-900/50 rounded-lg p-3">
                        <div className="text-slate-400 text-xs mb-1">Environment</div>
                        <div className="text-white font-mono text-sm">{az2Version.environment}</div>
                      </div>
                    </div>
                  )}
                </div>
              </button>
            </div>

            {/* Azure Services Grid */}
            {currentStatus && (
              <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700 p-6 mb-8">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <span className="text-blue-400">☁️</span>
                  </span>
                  Azure Infrastructure Services
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <ServiceCard
                    name="Azure Key Vault"
                    status={currentStatus.azure_services.key_vault}
                    icon="🔐"
                    onClick={() => setSelectedService({ name: 'Azure Key Vault', status: currentStatus.azure_services.key_vault, icon: '🔐' })}
                  />
                  <ServiceCard
                    name="Redis Cache"
                    status={currentStatus.azure_services.redis_cache}
                    icon="⚡"
                    onClick={() => setSelectedService({ name: 'Redis Cache', status: currentStatus.azure_services.redis_cache, icon: '⚡' })}
                  />
                  <ServiceCard
                    name="Cosmos DB"
                    status={currentStatus.azure_services.cosmos_db}
                    icon="🗄️"
                    onClick={() => setSelectedService({ name: 'Cosmos DB', status: currentStatus.azure_services.cosmos_db, icon: '🗄️' })}
                  />
                  <ServiceCard
                    name="Cohere AI"
                    status={currentStatus.azure_services.cohere_api}
                    icon="🤖"
                    onClick={() => setSelectedService({ name: 'Cohere AI', status: currentStatus.azure_services.cohere_api, icon: '🤖' })}
                  />
                  <ServiceCard
                    name="MQTT Broker"
                    status={currentStatus.azure_services.mqtt_broker}
                    icon="📡"
                    onClick={() => setSelectedService({ name: 'MQTT Broker', status: currentStatus.azure_services.mqtt_broker, icon: '📡' })}
                  />
                  <ServiceCard
                    name="RabbitMQ"
                    status={currentStatus.azure_services.rabbitmq_broker}
                    icon="🐰"
                    onClick={() => setSelectedService({ name: 'RabbitMQ', status: currentStatus.azure_services.rabbitmq_broker, icon: '🐰' })}
                  />
                </div>
              </div>
            )}

            {/* Cohere AI Section */}
            {cohereStatus && (
              <div className="bg-gradient-to-br from-purple-900/30 to-slate-900 rounded-xl border border-purple-500/30 p-6 mb-8">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                    <span className="text-purple-400">🧠</span>
                  </span>
                  AI & Machine Learning Integration
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <div className="text-slate-400 text-sm mb-2">Service Status</div>
                    <div className={`text-2xl font-bold ${cohereStatus.available ? 'text-green-400' : 'text-red-400'}`}>
                      {cohereStatus.available ? '✓ Available' : '✗ Offline'}
                    </div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <div className="text-slate-400 text-sm mb-2">Embedding Model</div>
                    <div className="text-white font-mono text-sm">{cohereStatus.embed_model}</div>
                    <div className="text-purple-400 text-xs mt-1">Image embeddings & semantic search</div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <div className="text-slate-400 text-sm mb-2">Chat Model</div>
                    <div className="text-white font-mono text-sm">{cohereStatus.chat_model}</div>
                    <div className="text-purple-400 text-xs mt-1">RAG-based analysis</div>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Active Zones" value="2" trend="+0%" color="green" />
              <StatCard label="IoT Devices" value="100K" trend="+2.3%" color="blue" />
              <StatCard label="Active Users" value="5,000" trend="+5.1%" color="cyan" />
              <StatCard label="API Requests" value="1.2M/day" trend="+12%" color="purple" />
            </div>

            {/* AI-Powered Capabilities */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-6">Platform Capabilities - Click to Open AI Chat</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => {
                    setChatContext('natural_language_search');
                    setShowAIChat(true);
                  }}
                  className="w-full text-left"
                >
                  <CapabilityCard
                    title="🔍 Natural Language Search"
                    description="Query site images using plain English queries"
                    example="Try: 'Show turbine sites' or 'Find images from TX-TURBINE'"
                  />
                </button>
                <button
                  onClick={() => {
                    setChatContext('safety_compliance');
                    setShowAIChat(true);
                  }}
                  className="w-full text-left"
                >
                  <CapabilityCard
                    title="⚠️ Safety Compliance Analysis"
                    description="AI-powered safety violation detection with BP standards"
                    example="Try: 'Find workers without hard hats' or 'Show PPE violations'"
                  />
                </button>
                <button
                  onClick={() => {
                    setChatContext('rag_chat');
                    setShowAIChat(true);
                  }}
                  className="w-full text-left"
                >
                  <CapabilityCard
                    title="💬 RAG-Based Chat"
                    description="Contextual Q&A about operational data with IoT devices"
                    example="Try: 'What devices are active?' or 'Show user activity by region'"
                  />
                </button>
                <button
                  onClick={() => {
                    setChatContext('log_diagnostics');
                    setShowAIChat(true);
                  }}
                  className="w-full text-left"
                >
                  <CapabilityCard
                    title="📋 Log Diagnostics"
                    description="Intelligent log analysis and error pattern detection"
                    example="Try: 'Show top error IPs' or 'Analyze 500 error patterns'"
                  />
                </button>
              </div>
            </div>
          </>
        )}

        {/* Violations Dialog */}
        <ViolationsDialog
          isOpen={showViolationsDialog}
          onClose={() => setShowViolationsDialog(false)}
          apiUrl={activeZone === 'az1' ? API_AZ1 : API_AZ2}
        />

        {/* AI Assistant Chat */}
        <AIAssistantChat
          isOpen={showAIChat}
          onClose={() => setShowAIChat(false)}
          apiUrl={activeZone === 'az1' ? API_AZ1 : API_AZ2}
          context={chatContext}
        />

        {/* Service Details Modal */}
        {selectedService && (
          <ServiceDetailsModal
            service={selectedService}
            onClose={() => setSelectedService(null)}
            activeZone={activeZone}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900/90 backdrop-blur border-t border-blue-500/30 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-white font-semibold mb-1">Team OPSC</div>
              <div className="text-slate-400 text-sm">Bala Anbalagan • Varad Poddar • Samip Niraula</div>
            </div>
            <div className="text-right">
              <div className="text-blue-300 text-sm font-medium">CMPE 273 - Section 47</div>
              <div className="text-slate-400 text-sm">Enterprise Distributed Systems</div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function ServiceCard({ name, status, icon, onClick }: { name: string; status: string; icon: string; onClick: () => void }) {
  const isOnline = status.includes('✅') || status.includes('connected') || status.includes('configured') || status.includes('available');

  return (
    <button
      onClick={onClick}
      className="bg-slate-900/50 rounded-lg p-4 border border-slate-700 hover:border-blue-500/50 transition-all cursor-pointer hover:scale-105 transform w-full text-left"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
      </div>
      <div className="text-white font-medium mb-1">{name}</div>
      <div className={`text-xs ${isOnline ? 'text-green-400' : 'text-red-400'}`}>
        {isOnline ? 'Connected' : 'Offline'}
      </div>
    </button>
  );
}

function StatCard({ label, value, trend, color }: { label: string; value: string; trend: string; color: string }) {
  const colors = {
    green: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
    cyan: 'from-cyan-500/20 to-teal-500/20 border-cyan-500/30',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30',
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color as keyof typeof colors]} rounded-lg p-4 border`}>
      <div className="text-slate-300 text-sm mb-1">{label}</div>
      <div className="text-white text-2xl font-bold mb-1">{value}</div>
      <div className="text-green-400 text-xs">{trend} vs last hour</div>
    </div>
  );
}

function CapabilityCard({ title, description, example }: { title: string; description: string; example: string }) {
  return (
    <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700 hover:border-blue-500/50 transition-all">
      <div className="text-white font-semibold mb-2">{title}</div>
      <div className="text-slate-400 text-sm mb-3">{description}</div>
      <div className="bg-blue-500/10 border border-blue-500/20 rounded px-3 py-2">
        <div className="text-blue-300 text-xs italic">{example}</div>
      </div>
    </div>
  );
}

function ServiceDetailsModal({
  service,
  onClose,
  activeZone
}: {
  service: { name: string; status: string; icon: string };
  onClose: () => void;
  activeZone: 'az1' | 'az2'
}) {
  const isOnline = service.status.includes('✅') || service.status.includes('connected') || service.status.includes('configured') || service.status.includes('available');

  // Service-specific performance metrics (simulated data)
  const getServiceMetrics = (serviceName: string) => {
    switch (serviceName) {
      case 'Redis Cache':
        return {
          metrics: [
            { label: 'Connections', value: '127', icon: '🔌' },
            { label: 'Memory Usage', value: '45%', icon: '💾' },
            { label: 'Hit Rate', value: '94.2%', icon: '🎯' },
            { label: 'Throughput', value: '12.3K ops/s', icon: '⚡' },
          ],
          description: 'Azure Cache for Redis provides in-memory data caching with low latency and high throughput.',
          color: 'red'
        };
      case 'Cosmos DB':
        return {
          metrics: [
            { label: 'RU/s Consumed', value: '450 / 1000', icon: '📊' },
            { label: 'Documents', value: '15.2K', icon: '📄' },
            { label: 'Avg Latency', value: '12ms', icon: '⏱️' },
            { label: 'Storage', value: '2.1GB', icon: '💽' },
          ],
          description: 'Azure Cosmos DB (MongoDB API) providing globally distributed, multi-model database service.',
          color: 'purple'
        };
      case 'MQTT Broker':
        return {
          metrics: [
            { label: 'Active Connections', value: '1,247', icon: '📡' },
            { label: 'Message Rate', value: '5.2K/s', icon: '📨' },
            { label: 'Topics', value: '43', icon: '📋' },
            { label: 'Uptime', value: '99.98%', icon: '⏰' },
          ],
          description: 'MQTT message broker for IoT device communication and telemetry data streaming.',
          color: 'blue'
        };
      case 'RabbitMQ':
        return {
          metrics: [
            { label: 'Queue Depth', value: '342', icon: '📬' },
            { label: 'Message Rate', value: '890/s', icon: '💬' },
            { label: 'Consumers', value: '18', icon: '👥' },
            { label: 'Memory Usage', value: '28%', icon: '🧠' },
          ],
          description: 'RabbitMQ message queue for reliable asynchronous communication between services.',
          color: 'orange'
        };
      case 'Azure Key Vault':
        return {
          metrics: [
            { label: 'Secrets Stored', value: '12', icon: '🔑' },
            { label: 'Access Requests', value: '1.2K/day', icon: '📈' },
            { label: 'Last Rotation', value: '7 days ago', icon: '🔄' },
            { label: 'Compliance', value: '100%', icon: '✅' },
          ],
          description: 'Azure Key Vault for secure secrets, keys, and certificate management.',
          color: 'green'
        };
      case 'Cohere AI':
        return {
          metrics: [
            { label: 'API Calls Today', value: '2,451', icon: '🤖' },
            { label: 'Embeddings Generated', value: '1,893', icon: '🧮' },
            { label: 'Avg Response Time', value: '245ms', icon: '⚡' },
            { label: 'Success Rate', value: '99.7%', icon: '✅' },
          ],
          description: 'Cohere AI for natural language processing, embeddings, and RAG-based chat analysis.',
          color: 'pink'
        };
      default:
        return {
          metrics: [],
          description: 'Azure service details',
          color: 'blue'
        };
    }
  };

  const serviceData = getServiceMetrics(service.name);
  const colorClasses = {
    red: 'from-red-500/20 to-orange-500/20 border-red-500/30',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
    orange: 'from-orange-500/20 to-yellow-500/20 border-orange-500/30',
    green: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    pink: 'from-pink-500/20 to-purple-500/20 border-pink-500/30',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-blue-500/30 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className={`bg-gradient-to-r ${colorClasses[serviceData.color as keyof typeof colorClasses]} px-6 py-4 border-b border-blue-500/30`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-5xl">{service.icon}</span>
              <div>
                <h2 className="text-2xl font-bold text-white">{service.name}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
                  <span className={`text-sm ${isOnline ? 'text-green-300' : 'text-red-300'}`}>
                    {isOnline ? 'Connected' : 'Offline'}
                  </span>
                  <span className="text-slate-400 text-sm">• Zone: {activeZone.toUpperCase()}</span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/70 hover:text-white text-3xl leading-none transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Description */}
          <div className="bg-slate-900/50 rounded-lg p-4 mb-6 border border-slate-700">
            <p className="text-slate-300 text-sm">{serviceData.description}</p>
          </div>

          {/* Performance Metrics */}
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>📊</span> Performance Metrics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {serviceData.metrics.map((metric, index) => (
              <div key={index} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-slate-400 text-xs mb-1">{metric.label}</div>
                    <div className="text-white text-2xl font-bold">{metric.value}</div>
                  </div>
                  <span className="text-3xl">{metric.icon}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Connection Details */}
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>🔗</span> Connection Details
          </h3>
          <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Status:</span>
                <span className="text-white font-mono">{service.status}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Active Zone:</span>
                <span className="text-white font-mono">{activeZone === 'az1' ? 'East US (Primary)' : 'West US 2 (Secondary)'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Last Health Check:</span>
                <span className="text-white font-mono">{new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-900/80 px-6 py-3 border-t border-blue-500/20 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-300 rounded-lg transition-colors text-sm font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
