import React from 'react';
import { Menu, LogOut } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  onMenuClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const logout = useAppStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    if (confirm('정말 업무를 종료하고 로그아웃 하시겠습니까?')) {
      logout();
      navigate('/login');
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 z-30 lg:pl-64 flex items-center justify-between px-6 transition-all">
      <div className="flex items-center gap-4">
        <button onClick={onMenuClick} className="lg:hidden text-slate-400 hover:text-white">
          <Menu size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-200 hidden md:block">
          오늘도 힘내세요, 사장님! 💪
        </h1>
      </div>

      <button
        onClick={handleLogout}
        className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition text-sm font-bold"
      >
        <LogOut size={16} />
        <span>업무 종료</span>
      </button>
    </header>
  );
};
