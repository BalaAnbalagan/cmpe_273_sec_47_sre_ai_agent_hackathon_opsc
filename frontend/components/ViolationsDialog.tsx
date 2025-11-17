'use client';

import { useState, useEffect } from 'react';

interface ViolationImage {
  image_id: string;
  site_id: string;
  description: string;
  url: string;
  thumbnail_url: string;
  timestamp: string;
  violation_type: string;
}

interface ViolationsDialogProps {
  isOpen: boolean;
  onClose: () => void;
  apiUrl: string;
}

export default function ViolationsDialog({ isOpen, onClose, apiUrl }: ViolationsDialogProps) {
  const [loading, setLoading] = useState(false);
  const [violations, setViolations] = useState<ViolationImage[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [selectedImage, setSelectedImage] = useState<ViolationImage | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchViolations();
    }
  }, [isOpen]);

  const fetchViolations = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/sre/images/safety-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_images: 20 })
      });

      if (response.ok) {
        const data = await response.json();
        setViolations(data.violation_images || []);
        setAnalysis(data.analysis);
      }
    } catch (error) {
      console.error('Error fetching violations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-6xl max-h-[90vh] bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-red-500/30 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-900/50 to-orange-900/50 px-6 py-4 border-b border-red-500/30">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <span className="text-3xl">⚠️</span>
                Safety Compliance Violations
              </h2>
              <p className="text-red-300 text-sm mt-1">AI-Detected Safety Issues Across Sites</p>
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
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-100px)]">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-red-500 border-t-transparent"></div>
                <p className="text-red-300 mt-4">Analyzing safety violations...</p>
              </div>
            </div>
          ) : (
            <>
              {/* Analysis Summary */}
              {analysis && (
                <div className="bg-slate-900/50 rounded-lg p-4 mb-6 border border-red-500/20">
                  <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                    <span>📊</span> AI Analysis Summary
                  </h3>
                  <p className="text-slate-300 text-sm whitespace-pre-wrap">{analysis}</p>
                </div>
              )}

              {/* Violations Grid */}
              {violations.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {violations.map((violation, index) => (
                    <div
                      key={index}
                      onClick={() => setSelectedImage(violation)}
                      className="group relative bg-slate-900/50 rounded-lg overflow-hidden border border-red-500/20 hover:border-red-500/50 transition-all cursor-pointer hover:scale-105"
                    >
                      {/* Image */}
                      <div className="aspect-video bg-slate-800 relative overflow-hidden">
                        <img
                          src={violation.thumbnail_url}
                          alt={violation.description}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                        />
                        <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                          Violation
                        </div>
                      </div>

                      {/* Details */}
                      <div className="p-3">
                        <div className="text-red-400 text-xs font-semibold mb-1">{violation.site_id}</div>
                        <div className="text-white text-sm font-medium mb-2 line-clamp-2">
                          {violation.description}
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400">{violation.timestamp}</span>
                          <span className="text-red-400">View Details →</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">✅</div>
                  <div className="text-white text-xl font-semibold mb-2">No Violations Detected</div>
                  <div className="text-slate-400">All sites are currently in compliance</div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Stats */}
        <div className="bg-slate-900/80 px-6 py-3 border-t border-red-500/20 flex items-center justify-between">
          <div className="text-sm text-slate-300">
            Total Violations: <span className="text-red-400 font-bold">{violations.length}</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 text-red-300 rounded-lg transition-colors text-sm font-medium"
          >
            Close
          </button>
        </div>
      </div>

      {/* Image Detail Modal */}
      {selectedImage && (
        <div
          className="absolute inset-0 flex items-center justify-center p-4 bg-black/90"
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
                <div>
                  <span className="text-slate-400">Type:</span>{' '}
                  <span className="text-red-400">{selectedImage.violation_type}</span>
                </div>
                <div>
                  <span className="text-slate-400">Detected:</span>{' '}
                  <span className="text-white">{selectedImage.timestamp}</span>
                </div>
                <div>
                  <span className="text-slate-400">ID:</span>{' '}
                  <span className="text-slate-300 font-mono text-xs">{selectedImage.image_id}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
