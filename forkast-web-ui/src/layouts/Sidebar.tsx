import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  TrendingUp, 
  BrainCircuit, 
  UtensilsCrossed, 
  Clock, 
  Truck, 
  Bell, 
  Settings,
  X 
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const MENU_ITEMS = [
  { path: '/dashboard', label: '대시보드', icon: LayoutDashboard },
  { path: '/analytics', label: '매출 분석', icon: TrendingUp },
  { path: '/forecast', label: '매출 예측 (AI)', icon: BrainCircuit },
  { path: '/menu-performance', label: '메뉴 성과', icon: UtensilsCrossed },
  { path: '/insights', label: '시간/요일 인사이트', icon: Clock },
  { path: '/delivery', label: '배달 분석', icon: Truck },
];

const SYSTEM_ITEMS = [
  { path: '/alerts', label: '알림 센터', icon: Bell, badge: 3 },
  { path: '/settings', label: '설정', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const sidebarClasses = `fixed inset-y-0 left-0 w-64 bg-slate-900 border-r border-slate-800 z-50 transform transition-transform duration-300 ease-in-out ${
    isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
  }`;

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside className={sidebarClasses}>
        <div className="p-6 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Forkast AI
          </div>
          <button onClick={onClose} className="lg:hidden text-slate-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        <nav className="px-4 space-y-2 mt-4 overflow-y-auto h-[calc(100vh-100px)]">
          {MENU_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => onClose()} // Close on mobile navigation
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium
                ${isActive 
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'}
              `}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}

          <div className="pt-4 pb-2 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
            시스템
          </div>

          {SYSTEM_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => onClose()}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium relative
                ${isActive 
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'}
              `}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
              {item.badge && (
                <span className="absolute right-4 bg-red-500 text-white text-[10px] px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};
