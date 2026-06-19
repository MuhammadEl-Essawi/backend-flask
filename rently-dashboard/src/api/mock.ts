import MockAdapter from 'axios-mock-adapter';
import api from './axios';

export const setupMocks = () => {
  const mock = new MockAdapter(api, { delayResponse: 500 });

  // Auth
  mock.onPost('/auth/login').reply(200, {
    token: 'mock-jwt-token',
    user: { id: 1, firstName: 'Admin', lastName: 'User', email: 'admin@rently.com', role: 'admin' }
  });

  // Dashboard Stats
  mock.onGet('/dashboard/stats').reply(200, {
    totalUsers: 1240,
    totalCars: 312,
    totalBookings: 856,
    totalRevenue: 42500
  });

  // Weekly Revenue
  mock.onGet('/dashboard/weekly-revenue').reply(200, [
    { date: 'Mon', revenue: 4500 },
    { date: 'Tue', revenue: 5200 },
    { date: 'Wed', revenue: 4800 },
    { date: 'Thu', revenue: 6100 },
    { date: 'Fri', revenue: 5900 },
    { date: 'Sat', revenue: 7200 },
    { date: 'Sun', revenue: 6800 },
  ]);

  // Bookings by Month
  mock.onGet('/dashboard/bookings-by-month').reply(200, [
    { month: 'Jan', count: 45 },
    { month: 'Feb', count: 52 },
    { month: 'Mar', count: 61 },
    { month: 'Apr', count: 58 },
    { month: 'May', count: 72 },
    { month: 'Jun', count: 85 },
  ]);

  // Users
  mock.onGet(/\/user.*/).reply(200, {
    items: [
      { id: 1, firstName: 'Ahmed', lastName: 'Ali', email: 'ahmed@example.com', phone: '01012345678', role: 'owner', approvalStatus: 'Approved' },
      { id: 2, firstName: 'Sara', lastName: 'Hassan', email: 'sara@example.com', phone: '01212345678', role: 'renter', approvalStatus: 'Pending' },
      { id: 3, firstName: 'John', lastName: 'Doe', email: 'john@example.com', phone: '01512345678', role: 'renter', approvalStatus: 'Approved' },
      { id: 4, firstName: 'Mona', lastName: 'Zaki', email: 'mona@example.com', phone: '01112345678', role: 'owner', approvalStatus: 'Rejected' },
    ],
    totalPages: 5
  });

  // Cars
  mock.onGet('/car/statistics').reply(200, {
    available: 240,
    rented: 45,
    maintenance: 12,
    pending: 15
  });

  mock.onGet(/\/car.*/).reply(200, {
    items: [
      { id: 1, brand: 'Tesla', model: 'Model 3', year: 2023, pricePerDay: 150, status: 'available', locationCity: 'Cairo' },
      { id: 2, brand: 'BMW', model: 'M4', year: 2022, pricePerDay: 200, status: 'rented', locationCity: 'Alexandria' },
      { id: 3, brand: 'Mercedes', model: 'C-Class', year: 2024, pricePerDay: 180, status: 'pending', locationCity: 'Giza' },
    ],
    totalPages: 3
  });

  // Bookings
  mock.onGet('/booking/statistics').reply(200, {
    activeTrips: 45,
    pickupsToday: 12,
    pendingBookings: 8,
    cancelledBookings: 3
  });

  mock.onGet(/\/booking.*/).reply(200, {
    items: [
      { id: 101, carId: 1, renterId: 2, startDate: '2026-05-01', endDate: '2026-05-05', totalPrice: 600, status: 'confirmed', car: { brand: 'Tesla', model: 'Model 3' } },
      { id: 102, carId: 2, renterId: 3, startDate: '2026-05-10', endDate: '2026-05-12', totalPrice: 400, status: 'pending', car: { brand: 'BMW', model: 'M4' } },
    ],
    totalPages: 2
  });

  // Payments
  mock.onGet('/payment/statistics').reply(200, {
    totalRevenue: 125000,
    totalProfit: 35000,
    avgTransaction: 450
  });

  // Requests
  mock.onGet('/request').reply(200, [
    { id: 1, type: 'User', entityId: 10, title: 'Identity Verification', description: 'User Ahmed Ali submitted a new national ID.', status: 'Pending', createdAt: new Date().toISOString() },
    { id: 2, type: 'Car', entityId: 5, title: 'New Car Listing', description: 'Tesla Model 3 verification required.', status: 'Pending', createdAt: new Date().toISOString() },
  ]);

  // Patch/Post fallbacks
  mock.onPatch(/\/car\/\d+\/status/).reply(200);
  mock.onPatch(/\/booking\/\d+\/status/).reply(200);
  mock.onPatch(/\/request\/\d+\/status/).reply(200);
  mock.onPost('/booking/refund-all').reply(200, { count: 3 });

  console.log('🚀 Mock API Layer Enabled');
};
