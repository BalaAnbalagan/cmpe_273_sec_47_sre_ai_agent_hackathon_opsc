/**
 * API Client for SRE Backend
 * Handles communication with Azure-deployed FastAPI backend
 * Supports multi-zone failover (AZ1 <-> AZ2)
 */

const API_URL_AZ1 = process.env.NEXT_PUBLIC_API_URL_AZ1 || 'https://sre-backend-az1.azurewebsites.net';
const API_URL_AZ2 = process.env.NEXT_PUBLIC_API_URL_AZ2 || 'https://sre-backend-az2.azurewebsites.net';

export type Zone = 'az1' | 'az2';

export interface BackendStatus {
  status: string;
  deployment: {
    version: string;
    zone: string;
    region: string;
  };
  azure_services: {
    redis: string;
    cosmos_db: string;
    key_vault: string;
    cohere_ai: string;
  };
  timestamp: string;
}

export interface DeploymentVersion {
  version: string;
  region: string;
  active_zone: string;
  environment: string;
}

export interface CohereStatus {
  available: boolean;
  model_embed: string;
  model_chat: string;
  message?: string;
}

export interface SearchResult {
  image_id: string;
  site_id: string;
  similarity_score: number;
  description: string;
  timestamp: string;
}

export interface SafetyAnalysis {
  overall_safety_score: number;
  findings: string[];
  recommendations: string[];
  analyzed_images: number;
  timestamp: string;
}

export interface ChatResponse {
  answer: string;
  sources: Array<{
    image_id: string;
    site_id: string;
    relevance_score: number;
  }>;
  timestamp: string;
}

class APIClient {
  private activeZone: Zone = 'az1';

  getBaseURL(zone?: Zone): string {
    const targetZone = zone || this.activeZone;
    return targetZone === 'az1' ? API_URL_AZ1 : API_URL_AZ2;
  }

  switchZone(zone: Zone) {
    this.activeZone = zone;
  }

  getActiveZone(): Zone {
    return this.activeZone;
  }

  async fetchWithFallback<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      const response = await fetch(this.getBaseURL() + endpoint, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
      }

      return await response.json();
    } catch (error) {
      // Failover to other zone
      const fallbackZone: Zone = this.activeZone === 'az1' ? 'az2' : 'az1';
      console.warn('Failing over from ' + this.activeZone + ' to ' + fallbackZone);

      const response = await fetch(this.getBaseURL(fallbackZone) + endpoint, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
      }

      // Update active zone on successful fallback
      this.activeZone = fallbackZone;
      return await response.json();
    }
  }

  // System Status APIs
  async getStatus(zone?: Zone): Promise<BackendStatus> {
    const url = zone ? this.getBaseURL(zone) : this.getBaseURL();
    const response = await fetch(url + '/sre/status');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return await response.json();
  }

  async getDeploymentVersion(zone?: Zone): Promise<DeploymentVersion> {
    const url = zone ? this.getBaseURL(zone) : this.getBaseURL();
    const response = await fetch(url + '/sre/deployment-version');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return await response.json();
  }

  async getCohereStatus(): Promise<CohereStatus> {
    return this.fetchWithFallback('/sre/images/cohere-status');
  }

  // AI-Powered APIs
  async searchNaturalLanguage(
    query: string,
    topK: number = 5
  ): Promise<{ results: SearchResult[] }> {
    return this.fetchWithFallback('/sre/images/search-nl', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  }

  async analyzeSafety(maxImages: number = 20): Promise<SafetyAnalysis> {
    return this.fetchWithFallback('/sre/images/safety-analysis', {
      method: 'POST',
      body: JSON.stringify({ max_images: maxImages }),
    });
  }

  async chatWithImages(
    query: string,
    maxResults: number = 10
  ): Promise<ChatResponse> {
    return this.fetchWithFallback('/sre/images/chat', {
      method: 'POST',
      body: JSON.stringify({ query, max_results: maxResults }),
    });
  }

  // Log Analysis APIs
  async getTopIPs(
    statusCode: string = '400',
    topN: number = 10
  ): Promise<{ top_ips: Array<{ ip: string; count: number }> }> {
    return this.fetchWithFallback('/sre/top-ips', {
      method: 'POST',
      body: JSON.stringify({ status_code: statusCode, top_n: topN }),
    });
  }
}

// Export singleton instance
export const api = new APIClient();
