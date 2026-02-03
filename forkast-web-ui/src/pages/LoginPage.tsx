import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { Lock } from 'lucide-react';

export const LoginPage = () => {
  const login = useAppStore((state) => state.login);
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    login();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white/5 backdrop-blur-xl p-8 rounded-2xl border border-white/10 shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-2">
            Forkast AI
          </h1>
          <p className="text-slate-400">사장님, 오늘도 대박 나세요! 🚀</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">아이디</label>
            <input 
              type="text" 
              defaultValue="admin"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            />
          </div>
          <div>
             <label className="block text-sm font-medium text-slate-300 mb-2">비밀번호</label>
            <div className="relative">
              <input 
                type="password" 
                defaultValue="1234"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
              <Lock size={18} className="absolute right-4 top-3.5 text-slate-500" />
            </div>
          </div>
          
          <button 
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-lg transition shadow-lg shadow-blue-500/30"
          >
            로그인하기
          </button>
        </form>
        
        <p className="text-center text-xs text-slate-600 mt-6">
          &copy; 2024 Forkast AI Solutions. All rights reserved.
        </p>
      </div>
    </div>
  );
};
