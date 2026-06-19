import React, { useEffect, useState } from 'react';
import { Plus, Check, X, Eye, Edit2, Trash2 } from 'lucide-react';
import api from '../api/axios';
import type { Car } from '../types';
import Table from '../components/Table';

const CarsPage: React.FC = () => {
  const [cars, setCars] = useState<Car[]>([]);
  const [carStats, setCarStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchData = async (pageNum: number) => {
    setLoading(true);
    try {
      const [carsRes, statsRes] = await Promise.all([
        api.get(`/car?page=${pageNum}`),
        api.get('/car/statistics')
      ]);
      setCars(carsRes.data.items);
      setTotalPages(carsRes.data.totalPages);
      setCarStats(statsRes.data);
    } catch (err) {
      console.error('Error fetching cars data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page);
  }, [page]);

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await api.patch(`/car/${id}/status`, { status });
      fetchData(page);
    } catch (err) {
      console.error('Error updating car status:', err);
    }
  };

  const columns = [
    { 
      header: 'Car', 
      accessor: (car: Car) => (
        <div>
          <p className="font-bold">{car.brand} {car.model}</p>
          <p className="text-xs text-muted">{car.year} • {car.locationCity}</p>
        </div>
      )
    },
    { 
      header: 'Daily Price', 
      accessor: (car: Car) => <span className="font-medium">${car.pricePerDay}</span>
    },
    { 
      header: 'Status', 
      accessor: (car: Car) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold capitalize
          ${car.status === 'available' ? 'bg-status-green/10 text-status-green' : 
            car.status === 'rented' ? 'bg-blue-500/10 text-blue-500' : 
            'bg-status-red/10 text-status-red'}`}>
          {car.status}
        </span>
      )
    },
    {
      header: 'Quick Actions',
      accessor: (car: Car) => (
        <div className="flex space-x-2">
          {car.status === 'pending' && (
            <>
              <button 
                onClick={() => handleStatusChange(car.id, 'available')}
                className="p-1.5 bg-status-green/10 text-status-green rounded-lg hover:bg-status-green/20 transition-colors"
                title="Approve"
              >
                <Check size={18} />
              </button>
              <button 
                onClick={() => handleStatusChange(car.id, 'rejected')}
                className="p-1.5 bg-status-red/10 text-status-red rounded-lg hover:bg-status-red/20 transition-colors"
                title="Reject"
              >
                <X size={18} />
              </button>
            </>
          )}
          <button className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted hover:text-text">
            <Eye size={18} />
          </button>
          <button className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted hover:text-text">
            <Edit2 size={18} />
          </button>
          <button className="p-1.5 hover:bg-status-red/10 rounded-lg transition-colors text-status-red">
            <Trash2 size={18} />
          </button>
        </div>
      ),
      className: 'text-right'
    }
  ];

  const statsCards = [
    { label: 'Available', value: carStats?.available || 0, color: 'text-status-green' },
    { label: 'Rented', value: carStats?.rented || 0, color: 'text-blue-500' },
    { label: 'In Maintenance', value: carStats?.maintenance || 0, color: 'text-status-yellow' },
    { label: 'Pending Approval', value: carStats?.pending || 0, color: 'text-purple-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Fleet Management</h1>
          <p className="text-muted">Control your inventory and car statuses.</p>
        </div>
        <button className="bg-cta hover:bg-cta/90 text-white px-4 py-2 rounded-xl font-bold flex items-center transition-all duration-200">
          <Plus size={20} className="mr-2" /> Add New Car
        </button>
      </div>

      {/* Mini Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statsCards.map((stat, i) => (
          <div key={i} className="bg-primary p-4 rounded-xl border border-secondary">
            <p className="text-xs font-medium text-muted uppercase tracking-wider">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <Table 
        columns={columns} 
        data={cars} 
        loading={loading}
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
};

export default CarsPage;
