import React, { useEffect, useState } from 'react';
import { UserPlus, Edit2, Trash2, Eye } from 'lucide-react';
import api from '../api/axios';
import type { User } from '../types';
import Table from '../components/Table';

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchUsers = async (pageNum: number) => {
    setLoading(true);
    try {
      const response = await api.get(`/user?page=${pageNum}`);
      setUsers(response.data.items);
      setTotalPages(response.data.totalPages);
    } catch (err) {
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers(page);
  }, [page]);

  const columns = [
    { 
      header: 'Name', 
      accessor: (u: User) => (
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center mr-3 font-bold text-xs">
            {u.firstName[0]}{u.lastName[0]}
          </div>
          <span className="font-medium">{u.firstName} {u.lastName}</span>
        </div>
      )
    },
    { header: 'Email', accessor: 'email' as keyof User },
    { header: 'Phone', accessor: 'phone' as keyof User },
    { 
      header: 'Role', 
      accessor: (u: User) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold capitalize
          ${u.role === 'admin' ? 'bg-purple-500/10 text-purple-500' : 'bg-blue-500/10 text-blue-500'}`}>
          {u.role}
        </span>
      )
    },
    { 
      header: 'Status', 
      accessor: (u: User) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold capitalize
          ${u.approvalStatus === 'Approved' ? 'bg-status-green/10 text-status-green' : 
            u.approvalStatus === 'Pending' ? 'bg-status-yellow/10 text-status-yellow' : 
            'bg-status-red/10 text-status-red'}`}>
          {u.approvalStatus}
        </span>
      )
    },
    {
      header: 'Actions',
      accessor: () => (
        <div className="flex space-x-2">
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Users</h1>
          <p className="text-muted">Manage platform users and roles.</p>
        </div>
        <button className="bg-cta hover:bg-cta/90 text-white px-4 py-2 rounded-xl font-bold flex items-center transition-all duration-200">
          <UserPlus size={20} className="mr-2" /> Add User
        </button>
      </div>

      <Table 
        columns={columns} 
        data={users} 
        loading={loading}
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
};

export default UsersPage;
