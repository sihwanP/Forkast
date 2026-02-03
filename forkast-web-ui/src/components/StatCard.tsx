import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'flat';
    label?: string;
  };
  icon?: React.ElementType;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const colorMap = {
  blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  green: 'text-green-400 bg-green-500/10 border-green-500/20',
  purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  orange: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  red: 'text-red-400 bg-red-500/10 border-red-500/20',
};

export const StatCard: React.FC<StatCardProps> = ({ label, value, trend, icon: Icon, color = 'blue' }) => {
  return (
    <div className={`p-6 rounded-2xl border bg-slate-800/50 backdrop-blur-sm ${colorMap[color].split(' ')[2]}`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">{label}</p>
          <h3 className="text-2xl font-black text-white">{value}</h3>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${colorMap[color]} `}>
            <Icon size={24} />
          </div>
        )}
      </div>
      
      {trend && (
        <div className="flex items-center gap-2 text-sm">
          <span className={`flex items-center gap-1 font-bold px-2 py-0.5 rounded text-xs ${
            trend.direction === 'up' ? 'text-green-400 bg-green-500/10' : 
            trend.direction === 'down' ? 'text-red-400 bg-red-500/10' : 'text-slate-400 bg-slate-500/10'
          }`}>
            {trend.direction === 'up' && <ArrowUpRight size={14} />}
            {trend.direction === 'down' && <ArrowDownRight size={14} />}
            {trend.direction === 'flat' && <Minus size={14} />}
            {trend.value}
          </span>
          {trend.label && <span className="text-slate-500 text-xs">{trend.label}</span>}
        </div>
      )}
    </div>
  );
};
