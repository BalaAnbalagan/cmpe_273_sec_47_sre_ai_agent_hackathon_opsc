'use client';

import { useEffect, useState } from 'react';

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

export default function Home() {
  const [az1Status, setAz1Status] = useState<BackendStatus | null>(null);
  const [az2Status, setAz2Status] = useState<BackendStatus | null>(null);
  const [cohereStatus, setCohereStatus] = useState<CohereStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeZone, setActiveZone] = useState<'az1' | 'az2'>('az1');

  const API_AZ1 = 'https://sre-backend-az1.azurewebsites.net';
  const API_AZ2 = 'https://sre-backend-az2.azurewebsites.net';

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [az1Res, az2Res, cohereRes] = await Promise.all([
          fetch(`${API_AZ1}/sre/status`).then(r => r.ok ? r.json() : null),
          fetch(`${API_AZ2}/sre/status`).then(r => r.ok ? r.json() : null),
          fetch(`${API_AZ1}/sre/images/cohere-status`).then(r => r.ok ? r.json() : null),
        ]);

        setAz1Status(az1Res);
        setAz2Status(az2Res);
        setCohereStatus(cohereRes);
      } catch (error) {
        console.error('Error fetching status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const currentAPI = activeZone === 'az1' ? API_AZ1 : API_AZ2;
  const currentStatus = activeZone === 'az1' ? az1Status : az2Status;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-800/50 border-b border-gray-700 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-white">SRE AI Agent Dashboard</h1>
          <p className="text-gray-400 mt-1">Team OPSC - CMPE273 Hackathon</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Zone Selector */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Active Availability Zone</h2>
          <div className="flex gap-4">
            <button
              onClick={() => setActiveZone('az1')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeZone === 'az1'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Zone 1 (Primary)
              {az1Status && <span className="ml-2 text-green-400">● Online</span>}
            </button>
            <button
              onClick={() => setActiveZone('az2')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeZone === 'az2'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Zone 2 (Secondary)
              {az2Status && <span className="ml-2 text-green-400">● Online</span>}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="text-gray-400 mt-4">Loading backend status...</p>
          </div>
        ) : (
          <>
            {/* Deployment Info */}
            {currentStatus && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                <StatCard title="Status" value={currentStatus.deployment.status} color="green" />
                <StatCard title="Version" value={currentStatus.deployment.version} />
                <StatCard title="Region" value={currentStatus.deployment.region} />
                <StatCard title="Zone" value={currentStatus.deployment.zone} />
                <StatCard title="Environment" value={currentStatus.deployment.environment} />
              </div>
            )}

            {/* Azure Services Status */}
            {currentStatus && (
              <div className="bg-gray-800/50 rounded-lg p-6 mb-6 border border-gray-700">
                <h2 className="text-xl font-semibold text-white mb-4">Azure Services</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <ServiceStatus
                    name="Key Vault"
                    status={currentStatus.azure_services.key_vault}
                  />
                  <ServiceStatus
                    name="Redis Cache"
                    status={currentStatus.azure_services.redis_cache}
                  />
                  <ServiceStatus
                    name="Cosmos DB"
                    status={currentStatus.azure_services.cosmos_db}
                  />
                  <ServiceStatus
                    name="Cohere API"
                    status={currentStatus.azure_services.cohere_api}
                  />
                  <ServiceStatus
                    name="MQTT Broker"
                    status={currentStatus.azure_services.mqtt_broker}
                  />
                  <ServiceStatus
                    name="RabbitMQ Broker"
                    status={currentStatus.azure_services.rabbitmq_broker}
                  />
                </div>
              </div>
            )}

            {/* Cohere AI Status */}
            {cohereStatus && (
              <div className="bg-gray-800/50 rounded-lg p-6 mb-6 border border-gray-700">
                <h2 className="text-xl font-semibold text-white mb-4">Cohere AI Integration</h2>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Status:</span>
                    <span className={`font-medium ${cohereStatus.available ? 'text-green-400' : 'text-red-400'}`}>
                      {cohereStatus.available ? '✓ Available' : '✗ Unavailable'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Embedding Model:</span>
                    <span className="text-blue-400 font-mono text-sm">{cohereStatus.embed_model}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Chat Model:</span>
                    <span className="text-blue-400 font-mono text-sm">{cohereStatus.chat_model}</span>
                  </div>
                </div>
              </div>
            )}

            {/* API Endpoints */}
            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
              <h2 className="text-xl font-semibold text-white mb-4">Available API Endpoints</h2>
              <div className="space-y-2">
                <EndpointLink url={`${currentAPI}/sre/status`} method="GET" desc="System Status" />
                <EndpointLink url={`${currentAPI}/sre/deployment-version`} method="GET" desc="Deployment Version" />
                <EndpointLink url={`${currentAPI}/sre/images/cohere-status`} method="GET" desc="Cohere AI Status" />
                <EndpointLink url={`${currentAPI}/sre/telemetry`} method="POST" desc="IoT Telemetry" />
                <EndpointLink url={`${currentAPI}/sre/user-metric`} method="POST" desc="User Metrics" />
                <EndpointLink url={`${currentAPI}/sre/search-images`} method="POST" desc="Image Search" />
                <EndpointLink url={`${currentAPI}/sre/top-ips`} method="POST" desc="Log Analysis" />
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800/50 border-t border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-400">
          <p>Team OPSC | Bala Anbalagan, Varad Poddar, Samip Niraula</p>
          <p className="text-sm mt-1">CMPE273 Section 47 - SRE AI Agent Hackathon</p>
        </div>
      </footer>
    </div>
  );
}

function StatCard({ title, value, color = 'blue' }: { title: string; value: string; color?: string }) {
  const colorClasses = {
    green: 'text-green-400',
    blue: 'text-blue-400',
  };

  return (
    <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
      <div className="text-gray-400 text-sm mb-1">{title}</div>
      <div className={`text-xl font-semibold ${colorClasses[color as keyof typeof colorClasses] || 'text-gray-200'}`}>
        {value}
      </div>
    </div>
  );
}

function ServiceStatus({ name, status }: { name: string; status: string }) {
  const isOnline = status.includes('✅') || status.includes('connected') || status.includes('configured') || status.includes('available');

  return (
    <div className="bg-gray-700/30 rounded p-3 border border-gray-600">
      <div className="flex items-center justify-between">
        <span className="text-gray-300">{name}</span>
        <span className={`text-sm ${isOnline ? 'text-green-400' : 'text-gray-400'}`}>
          {status}
        </span>
      </div>
    </div>
  );
}

function EndpointLink({ url, method, desc }: { url: string; method: string; desc: string }) {
  return (
    <div className="flex items-center gap-3 py-2 px-3 bg-gray-700/30 rounded border border-gray-600 hover:border-blue-500 transition-colors">
      <span className={`px-2 py-1 rounded text-xs font-mono ${
        method === 'GET' ? 'bg-green-600' : 'bg-blue-600'
      }`}>
        {method}
      </span>
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-400 hover:text-blue-300 font-mono text-sm flex-1 truncate"
      >
        {url}
      </a>
      <span className="text-gray-400 text-sm">{desc}</span>
    </div>
  );
}
