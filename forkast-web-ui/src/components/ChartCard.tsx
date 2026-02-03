import React from 'react';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}

export const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, action }) => {
  return (
    <div className="p-6 rounded-2xl border border-slate-700 bg-slate-800/50 backdrop-blur-sm h-full flex flex-col">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-white">{title}</h3>
          {subtitle && <p className="text-slate-400 text-sm mt-1">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className="flex-1 w-full min-h-[300px]">
        {children}
      </div>
    </div>
  );
};
