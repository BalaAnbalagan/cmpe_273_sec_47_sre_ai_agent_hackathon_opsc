'use client';

import { useEffect, useState } from 'react';
import ViolationsDialog from '@/components/ViolationsDialog';

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

  const API_AZ1 = 'https://sre-backend-az1.azurewebsites.net';
  const API_AZ2 = 'https://sre-backend-az2.azurewebsites.net';

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const activeAPI = activeZone === 'az1' ? API_AZ1 : API_AZ2;

        // Fetch from active zone only
        const [statusRes, versionRes, cohereRes] = await Promise.all([
          fetch(`${activeAPI}/sre/status`).then(r => r.ok ? r.json() : null),
          fetch(`${activeAPI}/sre/deployment-version`).then(r => r.ok ? r.json() : null),
          fetch(`${activeAPI}/sre/images/cohere-status`).then(r => r.ok ? r.json() : null),
        ]);

        // Update the active zone's data
        if (activeZone === 'az1') {
          setAz1Status(statusRes);
          setAz1Version(versionRes);
        } else {
          setAz2Status(statusRes);
          setAz2Version(versionRes);
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
                  <ServiceCard name="Azure Key Vault" status={currentStatus.azure_services.key_vault} icon="🔐" />
                  <ServiceCard name="Redis Cache" status={currentStatus.azure_services.redis_cache} icon="⚡" />
                  <ServiceCard name="Cosmos DB" status={currentStatus.azure_services.cosmos_db} icon="🗄️" />
                  <ServiceCard name="Cohere AI" status={currentStatus.azure_services.cohere_api} icon="🤖" />
                  <ServiceCard name="MQTT Broker" status={currentStatus.azure_services.mqtt_broker} icon="📡" />
                  <ServiceCard name="RabbitMQ" status={currentStatus.azure_services.rabbitmq_broker} icon="🐰" />
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

            {/* Capabilities */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-6">Platform Capabilities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <CapabilityCard
                  title="Natural Language Search"
                  description="Query site images using plain English queries"
                  example="'turbine sites with workers without hard hats'"
                />
                <button
                  onClick={() => setShowViolationsDialog(true)}
                  className="w-full text-left"
                >
                  <CapabilityCard
                    title="Safety Compliance Analysis"
                    description="AI-powered safety violation detection and scoring"
                    example="Real-time compliance monitoring - CLICK TO VIEW VIOLATIONS"
                  />
                </button>
                <CapabilityCard
                  title="RAG-Based Chat"
                  description="Contextual Q&A about operational data"
                  example="'What safety issues were reported this week?'"
                />
                <CapabilityCard
                  title="Log Diagnostics"
                  description="Intelligent log analysis and anomaly detection"
                  example="Identify top error-generating IP addresses"
                />
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

function ServiceCard({ name, status, icon }: { name: string; status: string; icon: string }) {
  const isOnline = status.includes('✅') || status.includes('connected') || status.includes('configured') || status.includes('available');

  return (
    <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700 hover:border-blue-500/50 transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
      </div>
      <div className="text-white font-medium mb-1">{name}</div>
      <div className={`text-xs ${isOnline ? 'text-green-400' : 'text-red-400'}`}>
        {isOnline ? 'Connected' : 'Offline'}
      </div>
    </div>
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
