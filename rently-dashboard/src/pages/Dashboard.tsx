import React, { useEffect, useState } from 'react';
import { 
  Users, 
  Car, 
  CalendarCheck, 
  TrendingUp,
  ArrowUpRight
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import api from '../api/axios';
import type { DashboardStats, WeeklyRevenue, BookingsByMonth } from '../types/index';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [weeklyRevenue, setWeeklyRevenue] = useState<WeeklyRevenue[]>([]);
  const [bookingsByMonth, setBookingsByMonth] = useState<BookingsByMonth[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsRes, revenueRes, monthRes] = await Promise.all([
          api.get('/dashboard/stats'),
          api.get('/dashboard/weekly-revenue'),
          api.get('/dashboard/bookings-by-month')
        ]);
        setStats(statsRes.data);
        setWeeklyRevenue(revenueRes.data);
        setBookingsByMonth(monthRes.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cta"></div>
      </div>
    );
  }

  const cards = [
    { title: 'Total Users', value: stats?.totalUsers || 0, icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { title: 'Active Fleet', value: stats?.totalCars || 0, icon: Car, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { title: 'Total Bookings', value: stats?.totalBookings || 0, icon: CalendarCheck, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { title: 'Total Revenue', value: `$${(stats?.totalRevenue || 0).toLocaleString()}`, icon: TrendingUp, color: 'text-cta', bg: 'bg-cta/10' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Overview</h1>
        <p className="text-muted">Welcome back to Rently Admin.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, i) => (
          <div key={i} className="bg-primary p-6 rounded-2xl border border-secondary shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-muted">{card.title}</p>
                <h3 className="text-2xl font-bold mt-2">{card.value}</h3>
              </div>
              <div className={`${card.bg} ${card.color} p-3 rounded-xl`}>
                <card.icon size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-cta flex items-center font-medium">
                <ArrowUpRight size={16} className="mr-1" /> 12%
              </span>
              <span className="text-muted ml-2">vs last month</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Weekly Revenue Line Chart */}
        <div className="bg-primary p-6 rounded-2xl border border-secondary shadow-sm">
          <h3 className="text-lg font-bold mb-6">Weekly Revenue Trend</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weeklyRevenue}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1E293B" />
                <XAxis 
                  dataKey="date" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94A3B8', fontSize: 12 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94A3B8', fontSize: 12 }}
                  tickFormatter={(val) => `$${val}`}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '12px' }}
                  itemStyle={{ color: '#F8FAFC' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#22C55E" 
                  strokeWidth={3} 
                  dot={{ r: 4, fill: '#22C55E', strokeWidth: 2, stroke: '#0F172A' }}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Bookings Bar Chart */}
        <div className="bg-primary p-6 rounded-2xl border border-secondary shadow-sm">
          <h3 className="text-lg font-bold mb-6">Bookings by Month</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bookingsByMonth}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1E293B" />
                <XAxis 
                  dataKey="month" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94A3B8', fontSize: 12 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94A3B8', fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '12px' }}
                  cursor={{ fill: '#1E293B', opacity: 0.4 }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {bookingsByMonth.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={index === bookingsByMonth.length - 1 ? '#22C55E' : '#334155'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
