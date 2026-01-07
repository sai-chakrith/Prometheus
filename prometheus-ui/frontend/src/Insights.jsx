/**
 * PROMETHEUS - Insights Dashboard
 * Investor Details, Funding Trends, and Policy Support
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Users, FileText, Search, DollarSign, MapPin } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function Insights({ theme = 'dark' }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('investors');

  // Theme-aware classes
  const cardBg = theme === 'dark' 
    ? 'bg-gray-800/50 border-gray-700' 
    : 'bg-white/80 border-gray-200 shadow-md';
  const cardBgHover = theme === 'dark' 
    ? 'bg-gray-700/30 hover:bg-gray-700/50' 
    : 'bg-gray-100/50 hover:bg-gray-200/70';
  const textMain = theme === 'dark' ? 'text-white' : 'text-gray-900';
  const textMuted = theme === 'dark' ? 'text-gray-400' : 'text-gray-600';
  const textSubtle = theme === 'dark' ? 'text-gray-500' : 'text-gray-500';
  const tabInactive = theme === 'dark' 
    ? 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50' 
    : 'bg-gray-200/70 text-gray-700 hover:bg-gray-300/70';
  const barBg = theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300';

  // Fetch insights data
  const { data: insights, isLoading } = useQuery({
    queryKey: ['insights'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/insights`);
      if (!response.ok) throw new Error('Failed to fetch insights');
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className={textMuted}>Loading insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 overflow-hidden">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
          Startup Insights
        </h2>
        <p className={textMuted}>Investor details, funding trends, and policy support</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('investors')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'investors'
              ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
              : tabInactive
          }`}
        >
          <Users className="w-5 h-5" />
          Investors
        </button>
        <button
          onClick={() => setActiveTab('trends')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'trends'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
              : tabInactive
          }`}
        >
          <TrendingUp className="w-5 h-5" />
          Trends
        </button>
        <button
          onClick={() => setActiveTab('policy')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'policy'
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
              : tabInactive
          }`}
        >
          <FileText className="w-5 h-5" />
          Policy Support
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'investors' && <InvestorDetails data={insights} theme={theme} cardBg={cardBg} cardBgHover={cardBgHover} textMain={textMain} textMuted={textMuted} textSubtle={textSubtle} />}
        {activeTab === 'trends' && <FundingTrends data={insights} theme={theme} cardBg={cardBg} cardBgHover={cardBgHover} textMain={textMain} textMuted={textMuted} textSubtle={textSubtle} barBg={barBg} />}
        {activeTab === 'policy' && <PolicySupport data={insights} theme={theme} cardBg={cardBg} cardBgHover={cardBgHover} textMain={textMain} textMuted={textMuted} textSubtle={textSubtle} />}
      </div>
    </div>
  );
}

function InvestorDetails({ data, theme, cardBg, cardBgHover, textMain, textMuted, textSubtle }) {
  const sectors = data?.data?.sectors?.top || [];
  const cities = data?.data?.cities?.top || [];
  const overview = data?.data?.overview || {};
  
  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`bg-gradient-to-br ${theme === 'dark' ? 'from-blue-500/20 to-cyan-500/20' : 'from-blue-100 to-cyan-100'} backdrop-blur rounded-xl p-6 border ${theme === 'dark' ? 'border-blue-500/30' : 'border-blue-300'}`}>
          <div className={`text-sm ${textMuted} mb-1`}>Total Funding</div>
          <div className={`text-3xl font-bold ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`}>{overview.totalFunding || 'N/A'}</div>
          <div className={`text-xs ${textSubtle} mt-1`}>{overview.timeRange || '2015-2017'}</div>
        </div>
        <div className={`bg-gradient-to-br ${theme === 'dark' ? 'from-purple-500/20 to-pink-500/20' : 'from-purple-100 to-pink-100'} backdrop-blur rounded-xl p-6 border ${theme === 'dark' ? 'border-purple-500/30' : 'border-purple-300'}`}>
          <div className={`text-sm ${textMuted} mb-1`}>Total Deals</div>
          <div className={`text-3xl font-bold ${theme === 'dark' ? 'text-purple-400' : 'text-purple-600'}`}>{overview.totalDeals?.toLocaleString() || 'N/A'}</div>
          <div className={`text-xs ${textSubtle} mt-1`}>Funding rounds</div>
        </div>
        <div className={`bg-gradient-to-br ${theme === 'dark' ? 'from-green-500/20 to-emerald-500/20' : 'from-green-100 to-emerald-100'} backdrop-blur rounded-xl p-6 border ${theme === 'dark' ? 'border-green-500/30' : 'border-green-300'}`}>
          <div className={`text-sm ${textMuted} mb-1`}>Avg Deal Size</div>
          <div className={`text-3xl font-bold ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`}>{overview.avgDealSize || 'N/A'}</div>
          <div className={`text-xs ${textSubtle} mt-1`}>Per funding round</div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Sectors */}
        <div className={`${cardBg} backdrop-blur rounded-xl p-6 border`}>
          <h3 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${textMain}`}>
            <DollarSign className={`w-5 h-5 ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`} />
            Top Funded Sectors
          </h3>
          <div className="space-y-3">
            {sectors.length > 0 ? (
              sectors.map((sector, idx) => (
                <InvestorCard key={idx} name={sector.name} deals={sector.deals} amount={sector.amount} theme={theme} cardBgHover={cardBgHover} textMain={textMain} textMuted={textMuted} />
              ))
            ) : (
              <p className={textSubtle}>No sector data available</p>
            )}
          </div>
        </div>

        {/* Top Cities */}
        <div className={`${cardBg} backdrop-blur rounded-xl p-6 border`}>
          <h3 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${textMain}`}>
            <MapPin className={`w-5 h-5 ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`} />
            Top Funded Cities
          </h3>
          <div className="space-y-3">
            {cities.length > 0 ? (
              cities.map((city, idx) => (
                <InvestorCard key={idx} name={city.name} deals={city.deals} amount={city.amount} theme={theme} cardBgHover={cardBgHover} textMain={textMain} textMuted={textMuted} />
              ))
            ) : (
              <p className={textSubtle}>No city data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function FundingTrends({ data, theme, cardBg, cardBgHover, textMain, textMuted, textSubtle, barBg }) {
  const trends = data?.data?.trends?.yearly || [];
  
  return (
    <div className="grid grid-cols-1 gap-6">
      {/* Year-wise Funding */}
      <div className={`${cardBg} backdrop-blur rounded-xl p-6 border`}>
        <h3 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${textMain}`}>
          <TrendingUp className={`w-5 h-5 ${theme === 'dark' ? 'text-purple-400' : 'text-purple-600'}`} />
          Year-wise Funding Trends (2015-2017)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {trends.length > 0 ? (
            trends.map((trend, idx) => (
              <TrendCard 
                key={idx} 
                year={trend.year} 
                amount={trend.amount} 
                change={trend.change}
                deals={trend.deals}
                theme={theme}
                cardBgHover={cardBgHover}
                textMuted={textMuted}
                textSubtle={textSubtle}
              />
            ))
          ) : (
            <p className={textSubtle}>No trend data available</p>
          )}
        </div>
      </div>

      {/* Additional Info */}
      <div className={`${cardBg} backdrop-blur rounded-xl p-6 border`}>
        <h3 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${textMain}`}>
          <MapPin className={`w-5 h-5 ${theme === 'dark' ? 'text-pink-400' : 'text-pink-600'}`} />
          Dataset Information
        </h3>
        <div className={`space-y-3 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
          <p>📊 <span className="font-semibold">Data Source:</span> Indian Startup Funding Dataset (2015-2017)</p>
          <p>🏢 <span className="font-semibold">Coverage:</span> {data?.data?.overview?.totalDeals || '5,302'} funding rounds across India</p>
          <p>🌍 <span className="font-semibold">Major Cities:</span> Bangalore, Mumbai, Delhi NCR, Gurgaon, Hyderabad</p>
          <p>💡 <span className="font-semibold">Key Sectors:</span> Technology, E-commerce, Fintech, Healthcare, Education</p>
        </div>
      </div>
    </div>
  );
}

function PolicySupport({ data, theme, cardBg, cardBgHover, textMain, textMuted, textSubtle }) {
  const policies = data?.data?.policy?.initiatives || [];
  
  return (
    <div className="space-y-6">
      {/* Government Initiatives */}
      <div className={`${cardBg} backdrop-blur rounded-xl p-6 border`}>
        <h3 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${textMain}`}>
          <FileText className={`w-5 h-5 ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`} />
          Government Initiatives (2015-2017 Period)
        </h3>
        <div className="space-y-4">
          {policies.length > 0 ? (
            policies.map((policy, idx) => (
              <PolicyCard
                key={idx}
                title={policy.name}
                description={getDescription(policy.name)}
                status={policy.status}
                theme={theme}
                cardBgHover={cardBgHover}
                textMain={textMain}
                textMuted={textMuted}
              />
            ))
          ) : (
            <p className={textSubtle}>No policy data available</p>
          )}
        </div>
      </div>
    </div>
  );
}

function getDescription(policyName) {
  const descriptions = {
    'Startup India (Launched 2016)': 'Tax exemptions for 3 years, easier compliance, and faster patent examination',
    'Digital India Initiative': 'Focus on digital infrastructure and technology adoption across sectors',
    'Make in India': 'Encouraging manufacturing and production startups with incentives'
  };
  return descriptions[policyName] || 'Government initiative to support startup ecosystem';
}

// Helper Components
function InvestorCard({ name, deals, amount, theme, cardBgHover, textMain, textMuted }) {
  return (
    <div className={`${cardBgHover} rounded-lg p-3 transition-all`}>
      <p className={`font-medium text-sm ${textMain}`}>{name}</p>
      <div className="flex items-center justify-between mt-1">
        <span className={`text-xs ${textMuted}`}>{deals} deals</span>
        <span className={`text-sm font-semibold ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`}>{amount}</span>
      </div>
    </div>
  );
}

function CategoryBar({ label, percentage, color, theme, textMain, barBg }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>{label}</span>
        <span className={`text-sm font-semibold ${textMain}`}>{percentage}%</span>
      </div>
      <div className={`w-full ${barBg} rounded-full h-2`}>
        <div className={`${color} h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}

function TrendCard({ year, amount, change, deals, theme, cardBgHover, textMuted, textSubtle }) {
  const isPositive = change && change !== '—' && change.startsWith('+');
  const isNegative = change && change !== '—' && change.startsWith('-');
  
  return (
    <div className={`${cardBgHover} rounded-lg p-4 text-center`}>
      <p className={`text-2xl font-bold ${theme === 'dark' ? 'text-purple-400' : 'text-purple-600'}`}>{amount}</p>
      <p className={`text-sm ${textMuted} mt-1`}>{year}</p>
      {deals && <p className={`text-xs ${textSubtle} mt-1`}>{deals} deals</p>}
      <p className={`text-xs mt-2 font-semibold ${
        isPositive ? (theme === 'dark' ? 'text-green-400' : 'text-green-600') : 
        isNegative ? (theme === 'dark' ? 'text-red-400' : 'text-red-600') : 
        textMuted
      }`}>
        {change}
      </p>
    </div>
  );
}

function SectorCard({ sector, amount, deals, theme, cardBgHover, textMain, textMuted }) {
  return (
    <div className={`${cardBgHover} rounded-lg p-4`}>
      <p className={`font-semibold text-lg ${textMain}`}>{sector}</p>
      <p className={`text-2xl font-bold ${theme === 'dark' ? 'text-pink-400' : 'text-pink-600'} mt-2`}>{amount}</p>
      <p className={`text-xs ${textMuted} mt-1`}>{deals} deals</p>
    </div>
  );
}

function PolicyCard({ title, description, status, theme, cardBgHover, textMain, textMuted }) {
  return (
    <div className={`${cardBgHover} rounded-lg p-4`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className={`font-semibold ${textMain}`}>{title}</h4>
          <p className={`text-sm ${textMuted} mt-1`}>{description}</p>
        </div>
        <span className={`ml-3 px-3 py-1 ${theme === 'dark' ? 'bg-green-500/20 text-green-400' : 'bg-green-100 text-green-700'} text-xs rounded-full`}>
          {status}
        </span>
      </div>
    </div>
  );
}
