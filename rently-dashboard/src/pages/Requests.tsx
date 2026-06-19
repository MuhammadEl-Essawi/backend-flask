import React, { useEffect, useState } from 'react';
import { Check, X, FileText, User, Car } from 'lucide-react';
import api from '../api/axios';
import type { VerificationRequest } from '../types';
import Table from '../components/Table';

const RequestsPage: React.FC = () => {
  const [requests, setRequests] = useState<VerificationRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const response = await api.get('/request');
      setRequests(response.data);
    } catch (err) {
      console.error('Error fetching requests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAction = async (id: number, status: string) => {
    try {
      await api.patch(`/request/${id}/status`, { status });
      setRequests(requests.filter(r => r.id !== id));
    } catch (err) {
      console.error('Error updating request status:', err);
    }
  };

  const columns = [
    { 
      header: 'Type', 
      accessor: (r: VerificationRequest) => (
        <div className="flex items-center">
          {r.type === 'User' ? <User size={18} className="mr-2 text-blue-500" /> : <Car size={18} className="mr-2 text-emerald-500" />}
          <span className="font-medium">{r.type}</span>
        </div>
      )
    },
    { header: 'Title', accessor: 'title' as keyof VerificationRequest },
    { 
      header: 'Description', 
      accessor: (r: VerificationRequest) => <span className="text-muted line-clamp-1">{r.description}</span> 
    },
    { 
      header: 'Created', 
      accessor: (r: VerificationRequest) => <span className="text-xs">{new Date(r.createdAt).toLocaleString()}</span> 
    },
    {
      header: 'Actions',
      accessor: (r: VerificationRequest) => (
        <div className="flex space-x-2">
          <button 
            onClick={() => handleAction(r.id, 'Approved')}
            className="p-1.5 bg-status-green/10 text-status-green rounded-lg hover:bg-status-green/20 transition-colors"
          >
            <Check size={18} />
          </button>
          <button 
            onClick={() => handleAction(r.id, 'Rejected')}
            className="p-1.5 bg-status-red/10 text-status-red rounded-lg hover:bg-status-red/20 transition-colors"
          >
            <X size={18} />
          </button>
          <button className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted hover:text-text">
            <FileText size={18} />
          </button>
        </div>
      ),
      className: 'text-right'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Verification Requests</h1>
        <p className="text-muted">Review and approve pending user and car listings.</p>
      </div>

      <Table 
        columns={columns} 
        data={requests} 
        loading={loading}
      />
    </div>
  );
};

export default RequestsPage;
