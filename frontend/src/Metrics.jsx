/**
 * Metrics Dashboard Component - Benchmark Results
 */

import { useState } from 'react';
import { BarChart3, TrendingUp, Zap, Loader2 } from 'lucide-react';
import { useEvalMetrics } from './api';
import confetti from 'canvas-confetti';
import { cn } from './utils';

export default function Metrics() {
  const [showMetrics, setShowMetrics] = useState(false);
  const { data, isLoading, refetch } = useEvalMetrics(showMetrics);

  const handleRunBenchmark = async () => {
    setShowMetrics(true);
    const result = await refetch();
    
    if (result.isSuccess) {
      // Celebration confetti!
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
    }
  };

  const formatPercent = (value) => `${(value * 100).toFixed(0)}%`;
  const formatMs = (value) => `${value}ms`;

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
    { code: 'mr', name: 'Marathi', flag: '🇮🇳' },
    { code: 'gu', name: 'Gujarati', flag: '🇮🇳' },
  ];

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-7 h-7 text-blue-400" />
              Benchmark Dashboard
            </h2>
            <p className="text-gray-400 mt-1">Multilingual RAG Performance Metrics</p>
          </div>
          
          <button
            onClick={handleRunBenchmark}
            disabled={isLoading}
            className={cn(
              "px-6 py-3 rounded-xl font-semibold transition-all shadow-lg",
              "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600",
              "text-white disabled:opacity-50 disabled:cursor-not-allowed",
              "flex items-center gap-2"
            )}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Run Benchmark
              </>
            )}
          </button>
        </div>

        {/* Metrics Display */}
        {showMetrics && data && (
          <div className="space-y-6 animate-fadeIn">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6 backdrop-blur">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-blue-500/30 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">Recall@5</h3>
                </div>
                <p className="text-3xl font-bold text-blue-400">
                  {formatPercent(data.metrics.recall5.en)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Average across languages</p>
              </div>

              <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6 backdrop-blur">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-green-500/30 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-green-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">Numeric F1</h3>
                </div>
                <p className="text-3xl font-bold text-green-400">
                  {formatPercent(data.metrics.numeric_f1.en)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Accuracy score</p>
              </div>

              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-xl p-6 backdrop-blur">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-purple-500/30 rounded-lg">
                    <Zap className="w-6 h-6 text-purple-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">Latency</h3>
                </div>
                <p className="text-3xl font-bold text-purple-400">
                  {formatMs(data.metrics.latency_ms.en)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Response time</p>
              </div>
            </div>

            {/* Detailed Table */}
            <div className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl overflow-hidden">
              <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 border-b border-gray-700">
                <h3 className="text-lg font-semibold text-white">Performance by Language</h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-800/70">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                        Language
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-gray-300 uppercase tracking-wider">
                        Recall@5
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-gray-300 uppercase tracking-wider">
                        Numeric F1
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-gray-300 uppercase tracking-wider">
                        Latency
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-gray-300 uppercase tracking-wider">
                        Grade
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {languages.map((lang) => {
                      const recall = data.metrics.recall5[lang.code];
                      const f1 = data.metrics.numeric_f1[lang.code];
                      const latency = data.metrics.latency_ms[lang.code];
                      const grade = f1 >= 0.9 ? 'A+' : f1 >= 0.85 ? 'A' : f1 >= 0.8 ? 'B+' : 'B';
                      const gradeColor = f1 >= 0.9 ? 'text-green-400' : f1 >= 0.85 ? 'text-blue-400' : 'text-yellow-400';
                      
                      return (
                        <tr key={lang.code} className="hover:bg-gray-700/30 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">{lang.flag}</span>
                              <span className="text-sm font-medium text-white">{lang.name}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-sm text-blue-400 font-semibold">
                              {formatPercent(recall)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-sm text-green-400 font-semibold">
                              {formatPercent(f1)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-sm text-purple-400 font-semibold">
                              {formatMs(latency)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className={cn("text-lg font-bold", gradeColor)}>
                              {grade}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Test Info */}
            <div className="flex items-center justify-between text-sm text-gray-400 px-2">
              <p>Total test queries: {data.test_queries}</p>
              <p>Last updated: {new Date(data.timestamp).toLocaleString()}</p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!showMetrics && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="p-6 bg-gray-800/30 rounded-full mb-6">
              <BarChart3 className="w-16 h-16 text-gray-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-400 mb-2">
              No Metrics Yet
            </h3>
            <p className="text-gray-500 mb-6">
              Click "Run Benchmark" to evaluate the RAG system performance
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
