import React, { useEffect, useState } from 'react';
import { DollarSign, PieChart, TrendingUp, Download } from 'lucide-react';
import api from '../api/axios';

const PaymentsPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/payment/statistics');
        setStats(response.data);
      } catch (err) {
        console.error('Error fetching payment stats:', err);
      }
    };
    fetchStats();
  }, []);

  const statCards = [
    { label: 'Total Revenue', value: `$${stats?.totalRevenue?.toLocaleString() || 0}`, icon: DollarSign, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Total Profit', value: `$${stats?.totalProfit?.toLocaleString() || 0}`, icon: TrendingUp, color: 'text-cta', bg: 'bg-cta/10' },
    { label: 'Avg. Transaction', value: `$${stats?.avgTransaction?.toLocaleString() || 0}`, icon: PieChart, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Payments</h1>
          <p className="text-muted">Financial overview and revenue breakdown.</p>
        </div>
        <button className="bg-secondary hover:bg-accent text-text px-4 py-2 rounded-xl font-bold flex items-center transition-all duration-200">
          <Download size={20} className="mr-2" /> Export Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statCards.map((card, i) => (
          <div key={i} className="bg-primary p-6 rounded-2xl border border-secondary shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted">{card.label}</p>
                <h3 className="text-3xl font-bold mt-2">{card.value}</h3>
              </div>
              <div className={`${card.bg} ${card.color} p-4 rounded-2xl`}>
                <card.icon size={28} />
              </div>
            </div>
            <div className="mt-4 text-xs text-muted flex items-center">
              <TrendingUp size={14} className="mr-1 text-cta" />
              <span className="text-cta font-medium mr-1">+8%</span> than last period
            </div>
          </div>
        ))}
      </div>

      {/* Placeholder for Recent Transactions */}
      <div className="bg-primary p-6 rounded-2xl border border-secondary">
        <h3 className="text-lg font-bold mb-6">Recent Transactions</h3>
        <div className="flex flex-col items-center justify-center py-12 text-muted">
          <DollarSign size={48} className="opacity-20 mb-4" />
          <p>Transaction history integration coming soon.</p>
        </div>
      </div>
    </div>
  );
};

export default PaymentsPage;
