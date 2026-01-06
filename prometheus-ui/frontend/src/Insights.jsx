/**
 * PROMETHEUS - Insights Dashboard
 * Investor Details, Funding Trends, and Policy Support
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Users, FileText, Search, DollarSign, MapPin } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function Insights() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('investors');

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
          <p className="text-gray-400">Loading insights...</p>
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
        <p className="text-gray-400">Investor details, funding trends, and policy support</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('investors')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'investors'
              ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
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
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
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
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
          }`}
        >
          <FileText className="w-5 h-5" />
          Policy Support
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'investors' && <InvestorDetails data={insights} />}
        {activeTab === 'trends' && <FundingTrends data={insights} />}
        {activeTab === 'policy' && <PolicySupport data={insights} />}
      </div>
    </div>
  );
}

function InvestorDetails({ data }) {
  const sectors = data?.data?.sectors?.top || [];
  const cities = data?.data?.cities?.top || [];
  const overview = data?.data?.overview || {};
  
  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur rounded-xl p-6 border border-blue-500/30">
          <div className="text-sm text-gray-400 mb-1">Total Funding</div>
          <div className="text-3xl font-bold text-blue-400">{overview.totalFunding || 'N/A'}</div>
          <div className="text-xs text-gray-500 mt-1">{overview.timeRange || '2015-2017'}</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur rounded-xl p-6 border border-purple-500/30">
          <div className="text-sm text-gray-400 mb-1">Total Deals</div>
          <div className="text-3xl font-bold text-purple-400">{overview.totalDeals?.toLocaleString() || 'N/A'}</div>
          <div className="text-xs text-gray-500 mt-1">Funding rounds</div>
        </div>
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur rounded-xl p-6 border border-green-500/30">
          <div className="text-sm text-gray-400 mb-1">Avg Deal Size</div>
          <div className="text-3xl font-bold text-green-400">{overview.avgDealSize || 'N/A'}</div>
          <div className="text-xs text-gray-500 mt-1">Per funding round</div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Sectors */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-400" />
            Top Funded Sectors
          </h3>
          <div className="space-y-3">
            {sectors.length > 0 ? (
              sectors.map((sector, idx) => (
                <InvestorCard key={idx} name={sector.name} deals={sector.deals} amount={sector.amount} />
              ))
            ) : (
              <p className="text-gray-500">No sector data available</p>
            )}
          </div>
        </div>

        {/* Top Cities */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-400" />
            Top Funded Cities
          </h3>
          <div className="space-y-3">
            {cities.length > 0 ? (
              cities.map((city, idx) => (
                <InvestorCard key={idx} name={city.name} deals={city.deals} amount={city.amount} />
              ))
            ) : (
              <p className="text-gray-500">No city data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function FundingTrends({ data }) {
  const trends = data?.data?.trends?.yearly || [];
  
  return (
    <div className="grid grid-cols-1 gap-6">
      {/* Year-wise Funding */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-400" />
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
              />
            ))
          ) : (
            <p className="text-gray-500">No trend data available</p>
          )}
        </div>
      </div>

      {/* Additional Info */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-pink-400" />
          Dataset Information
        </h3>
        <div className="space-y-3 text-gray-300">
          <p>📊 <span className="font-semibold">Data Source:</span> Indian Startup Funding Dataset (2015-2017)</p>
          <p>🏢 <span className="font-semibold">Coverage:</span> {data?.data?.overview?.totalDeals || '5,302'} funding rounds across India</p>
          <p>🌍 <span className="font-semibold">Major Cities:</span> Bangalore, Mumbai, Delhi NCR, Gurgaon, Hyderabad</p>
          <p>💡 <span className="font-semibold">Key Sectors:</span> Technology, E-commerce, Fintech, Healthcare, Education</p>
        </div>
      </div>
    </div>
  );
}

function PolicySupport({ data }) {
  const policies = data?.data?.policy?.initiatives || [];
  
  return (
    <div className="space-y-6">
      {/* Government Initiatives */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-green-400" />
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
              />
            ))
          ) : (
            <p className="text-gray-500">No policy data available</p>
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
function InvestorCard({ name, deals, amount }) {
  return (
    <div className="bg-gray-700/30 rounded-lg p-3 hover:bg-gray-700/50 transition-all">
      <p className="font-medium text-sm">{name}</p>
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs text-gray-400">{deals} deals</span>
        <span className="text-sm font-semibold text-green-400">{amount}</span>
      </div>
    </div>
  );
}

function CategoryBar({ label, percentage, color }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-300">{label}</span>
        <span className="text-sm font-semibold">{percentage}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}

function TrendCard({ year, amount, change, deals }) {
  const isPositive = change && change !== '—' && change.startsWith('+');
  const isNegative = change && change !== '—' && change.startsWith('-');
  
  return (
    <div className="bg-gray-700/30 rounded-lg p-4 text-center">
      <p className="text-2xl font-bold text-purple-400">{amount}</p>
      <p className="text-sm text-gray-400 mt-1">{year}</p>
      {deals && <p className="text-xs text-gray-500 mt-1">{deals} deals</p>}
      <p className={`text-xs mt-2 font-semibold ${
        isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-gray-400'
      }`}>
        {change}
      </p>
    </div>
  );
}

function SectorCard({ sector, amount, deals }) {
  return (
    <div className="bg-gray-700/30 rounded-lg p-4">
      <p className="font-semibold text-lg">{sector}</p>
      <p className="text-2xl font-bold text-pink-400 mt-2">{amount}</p>
      <p className="text-xs text-gray-400 mt-1">{deals} deals</p>
    </div>
  );
}

function PolicyCard({ title, description, status }) {
  return (
    <div className="bg-gray-700/30 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold">{title}</h4>
          <p className="text-sm text-gray-400 mt-1">{description}</p>
        </div>
        <span className="ml-3 px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
          {status}
        </span>
      </div>
    </div>
  );
}
