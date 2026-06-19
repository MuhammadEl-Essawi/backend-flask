import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Car, 
  CalendarCheck, 
  CreditCard, 
  UserCheck, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  Menu,
  X
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { name: 'Users', icon: Users, path: '/users' },
    { name: 'Cars', icon: Car, path: '/cars' },
    { name: 'Bookings', icon: CalendarCheck, path: '/bookings' },
    { name: 'Payments', icon: CreditCard, path: '/payments' },
    { name: 'Requests', icon: UserCheck, path: '/requests' },
  ];

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);
  const toggleMobile = () => setIsMobileOpen(!isMobileOpen);

  return (
    <>
      {/* Mobile Menu Button */}
      <button 
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-secondary rounded-lg text-text"
        onClick={toggleMobile}
      >
        {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay for mobile */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed top-0 left-0 h-full z-40 bg-primary border-r border-secondary transition-all duration-300
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        ${isCollapsed ? 'w-20' : 'w-64'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className="flex items-center justify-between p-6">
            {!isCollapsed && (
              <span className="text-2xl font-bold text-cta font-fira tracking-tighter">
                RENTLY<span className="text-text font-sans text-xs ml-1 font-normal opacity-50 uppercase tracking-widest">Admin</span>
              </span>
            )}
            <button 
              className="hidden lg:block p-1 hover:bg-secondary rounded-lg transition-colors"
              onClick={toggleSidebar}
            >
              {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            </button>
          </div>

          {/* Nav Items */}
          <nav className="flex-1 px-4 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center p-3 rounded-xl transition-all duration-200 group
                  ${isActive ? 'bg-cta text-white shadow-lg shadow-cta/20' : 'text-muted hover:bg-secondary hover:text-text'}
                `}
                onClick={() => setIsMobileOpen(false)}
              >
                <item.icon size={22} className={isCollapsed ? 'mx-auto' : 'mr-3'} />
                {!isCollapsed && <span className="font-medium">{item.name}</span>}
              </NavLink>
            ))}
          </nav>

          {/* Logout Button */}
          <div className="p-4 border-t border-secondary">
            <button 
              onClick={logout}
              className={`
                flex items-center w-full p-3 text-muted hover:bg-status-red/10 hover:text-status-red rounded-xl transition-all duration-200
                ${isCollapsed ? 'justify-center' : ''}
              `}
            >
              <LogOut size={22} className={isCollapsed ? '' : 'mr-3'} />
              {!isCollapsed && <span className="font-medium">Logout</span>}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
