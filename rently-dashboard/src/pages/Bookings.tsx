import React, { useEffect, useState } from 'react';
import { RefreshCcw, Check, X, Eye } from 'lucide-react';
import api from '../api/axios';
import type { Booking } from '../types';
import Table from '../components/Table';

const BookingsPage: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [refundLoading, setRefundLoading] = useState(false);

  const fetchData = async (pageNum: number) => {
    setLoading(true);
    try {
      const [bookingsRes, statsRes] = await Promise.all([
        api.get(`/booking?page=${pageNum}`),
        api.get('/booking/statistics')
      ]);
      setBookings(bookingsRes.data.items);
      setTotalPages(bookingsRes.data.totalPages);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Error fetching bookings data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page);
  }, [page]);

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await api.patch(`/booking/${id}/status`, { status });
      fetchData(page);
    } catch (err) {
      console.error('Error updating booking status:', err);
    }
  };

  const handleRefundAll = async () => {
    if (!window.confirm('Are you sure you want to refund all refundable bookings?')) return;
    setRefundLoading(true);
    try {
      const res = await api.post('/booking/refund-all');
      alert(`Successfully refunded ${res.data.count} bookings.`);
      fetchData(page);
    } catch (err) {
      console.error('Error refunding bookings:', err);
    } finally {
      setRefundLoading(false);
    }
  };

  const columns = [
    { 
      header: 'Booking ID', 
      accessor: (b: Booking) => <span className="font-fira text-xs">#{b.id.toString().padStart(6, '0')}</span>
    },
    { 
      header: 'Car', 
      accessor: (b: Booking) => <span>{b.car ? `${b.car.brand} ${b.car.model}` : `Car ID: ${b.carId}`}</span>
    },
    { 
      header: 'Period', 
      accessor: (b: Booking) => (
        <div className="text-xs">
          <p>{new Date(b.startDate).toLocaleDateString()}</p>
          <p className="text-muted">to {new Date(b.endDate).toLocaleDateString()}</p>
        </div>
      )
    },
    { 
      header: 'Total', 
      accessor: (b: Booking) => <span className="font-bold">${b.totalPrice}</span>
    },
    { 
      header: 'Status', 
      accessor: (b: Booking) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold capitalize
          ${b.status === 'confirmed' || b.status === 'completed' ? 'bg-status-green/10 text-status-green' : 
            b.status === 'pending' ? 'bg-status-yellow/10 text-status-yellow' : 
            'bg-status-red/10 text-status-red'}`}>
          {b.status}
        </span>
      )
    },
    {
      header: 'Actions',
      accessor: (b: Booking) => (
        <div className="flex space-x-2">
          {b.status === 'pending' && (
            <>
              <button 
                onClick={() => handleStatusChange(b.id, 'confirmed')}
                className="p-1.5 bg-status-green/10 text-status-green rounded-lg hover:bg-status-green/20 transition-colors"
              >
                <Check size={18} />
              </button>
              <button 
                onClick={() => handleStatusChange(b.id, 'cancelled')}
                className="p-1.5 bg-status-red/10 text-status-red rounded-lg hover:bg-status-red/20 transition-colors"
              >
                <X size={18} />
              </button>
            </>
          )}
          <button className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted hover:text-text">
            <Eye size={18} />
          </button>
        </div>
      ),
      className: 'text-right'
    }
  ];

  const statCards = [
    { label: 'Active Trips', value: stats?.activeTrips || 0, color: 'text-emerald-500' },
    { label: 'Pickups Today', value: stats?.pickupsToday || 0, color: 'text-blue-500' },
    { label: 'Pending Bookings', value: stats?.pendingBookings || 0, color: 'text-status-yellow' },
    { label: 'Cancelled', value: stats?.cancelledBookings || 0, color: 'text-status-red' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Bookings</h1>
          <p className="text-muted">Manage rental reservations and status updates.</p>
        </div>
        <button 
          onClick={handleRefundAll}
          disabled={refundLoading}
          className="bg-secondary hover:bg-accent text-text px-4 py-2 rounded-xl font-bold flex items-center transition-all duration-200 disabled:opacity-50"
        >
          <RefreshCcw size={20} className={`mr-2 ${refundLoading ? 'animate-spin' : ''}`} /> Refund All
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <div key={i} className="bg-primary p-4 rounded-xl border border-secondary">
            <p className="text-xs font-medium text-muted uppercase tracking-wider">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <Table 
        columns={columns} 
        data={bookings} 
        loading={loading}
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
};

export default BookingsPage;
