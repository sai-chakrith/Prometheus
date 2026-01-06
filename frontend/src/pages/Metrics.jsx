/**
 * Metrics Dashboard Component - Benchmark Results
 * Refactored for better code organization
 */

import { useState } from 'react';
import { BarChart3, TrendingUp, Zap, Loader2 } from 'lucide-react';
import { useEvalMetrics } from '../api';
import confetti from 'canvas-confetti';
import { cn } from '../utils';

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'mr', name: 'Marathi', flag: '🇮🇳' },
  { code: 'gu', name: 'Gujarati', flag: '🇮🇳' },
];

const formatPercent = (value) => `${(value * 100).toFixed(0)}%`;
const formatMs = (value) => `${value}ms`;

function getGrade(f1) {
  if (f1 >= 0.9) return { grade: 'A+', color: 'text-green-400' };
  if (f1 >= 0.85) return { grade: 'A', color: 'text-blue-400' };
  if (f1 >= 0.8) return { grade: 'B+', color: 'text-yellow-400' };
  return { grade: 'B', color: 'text-orange-400' };
}

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

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <MetricsHeader 
          isLoading={isLoading} 
          onRunBenchmark={handleRunBenchmark} 
        />

        {/* Metrics Display */}
        {showMetrics && data && (
          <MetricsContent data={data} />
        )}

        {/* Empty State */}
        {!showMetrics && <EmptyState />}
      </div>
    </div>
  );
}

function MetricsHeader({ isLoading, onRunBenchmark }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="w-7 h-7 text-blue-400" />
          Benchmark Dashboard
        </h2>
        <p className="text-gray-400 mt-1">Multilingual RAG Performance Metrics</p>
      </div>
      
      <button
        onClick={onRunBenchmark}
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
  );
}

function MetricsContent({ data }) {
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Summary Cards */}
      <SummaryCards data={data} />

      {/* Detailed Table */}
      <PerformanceTable data={data} />

      {/* Test Info */}
      <div className="flex items-center justify-between text-sm text-gray-400 px-2">
        <p>Total test queries: {data.test_queries}</p>
        <p>Last updated: {new Date(data.timestamp).toLocaleString()}</p>
      </div>
    </div>
  );
}

function SummaryCards({ data }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <MetricCard
        icon={TrendingUp}
        title="Recall@5"
        value={formatPercent(data.metrics.recall5.en)}
        subtitle="Average across languages"
        gradient="from-blue-500/20 to-blue-600/20"
        borderColor="border-blue-500/30"
        iconBg="bg-blue-500/30"
        iconColor="text-blue-400"
        valueColor="text-blue-400"
      />

      <MetricCard
        icon={BarChart3}
        title="Numeric F1"
        value={formatPercent(data.metrics.numeric_f1.en)}
        subtitle="Accuracy score"
        gradient="from-green-500/20 to-green-600/20"
        borderColor="border-green-500/30"
        iconBg="bg-green-500/30"
        iconColor="text-green-400"
        valueColor="text-green-400"
      />

      <MetricCard
        icon={Zap}
        title="Latency"
        value={formatMs(data.metrics.latency_ms.en)}
        subtitle="Response time"
        gradient="from-purple-500/20 to-purple-600/20"
        borderColor="border-purple-500/30"
        iconBg="bg-purple-500/30"
        iconColor="text-purple-400"
        valueColor="text-purple-400"
      />
    </div>
  );
}

function MetricCard({ 
  icon: Icon, 
  title, 
  value, 
  subtitle, 
  gradient, 
  borderColor, 
  iconBg, 
  iconColor, 
  valueColor 
}) {
  return (
    <div className={cn(
      "rounded-xl p-6 backdrop-blur border",
      `bg-gradient-to-br ${gradient} ${borderColor}`
    )}>
      <div className="flex items-center gap-3 mb-2">
        <div className={cn("p-2 rounded-lg", iconBg)}>
          <Icon className={cn("w-6 h-6", iconColor)} />
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      <p className={cn("text-3xl font-bold", valueColor)}>
        {value}
      </p>
      <p className="text-sm text-gray-400 mt-1">{subtitle}</p>
    </div>
  );
}

function PerformanceTable({ data }) {
  return (
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
            {LANGUAGES.map((lang) => {
              const recall = data.metrics.recall5[lang.code];
              const f1 = data.metrics.numeric_f1[lang.code];
              const latency = data.metrics.latency_ms[lang.code];
              const { grade, color } = getGrade(f1);
              
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
                    <span className={cn("text-lg font-bold", color)}>
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
  );
}

function EmptyState() {
  return (
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
  );
}
