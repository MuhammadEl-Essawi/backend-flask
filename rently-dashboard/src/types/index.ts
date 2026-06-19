export interface User {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: string;
  approvalStatus: string;
}

export interface Car {
  id: number;
  brand: string;
  model: string;
  year: number;
  pricePerDay: number;
  status: string;
  ownerId: number;
  locationCity: string;
}

export interface Booking {
  id: number;
  carId: number;
  renterId: number;
  startDate: string;
  endDate: string;
  totalPrice: number;
  status: string;
  car?: Car;
}

export interface DashboardStats {
  totalUsers: number;
  totalCars: number;
  totalBookings: number;
  totalRevenue: number;
}

export interface WeeklyRevenue {
  date: string;
  revenue: number;
}

export interface BookingsByMonth {
  month: string;
  count: number;
}

export interface VerificationRequest {
  id: number;
  type: 'User' | 'Car';
  entityId: number;
  title: string;
  description: string;
  status: string;
  createdAt: string;
}
