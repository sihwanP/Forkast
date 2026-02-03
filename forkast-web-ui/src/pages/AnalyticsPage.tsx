import { useState } from 'react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Bar, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid,
  Legend 
} from 'recharts';
import { Download, Calendar } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { DataTable, type Column } from '../components/DataTable';
import { ChartCard } from '../components/ChartCard';
import { formatCurrency } from '../utils/format';
import { SALES_DATA_7_DAYS, type DailySales } from '../data/sales.mock';

export const AnalyticsPage = () => {
  const [period, setPeriod] = useState('7d');

  const columns: Column<DailySales>[] = [
    { header: '날짜', accessor: 'date' as keyof DailySales, className: 'font-mono' },
    { header: '매출', accessor: (item: DailySales) => formatCurrency(item.revenue), className: 'text-right font-bold' },
    { header: '주문수', accessor: (item: DailySales) => `${item.orders}건`, className: 'text-right' },
    { header: '객단가', accessor: (item: DailySales) => formatCurrency(item.revenue / item.orders), className: 'text-right text-slate-400' },
  ];

  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="상세 매출 분석" 
        description="기간별 매출 동향과 세부 지표를 분석합니다."
        action={
          <div className="flex gap-2">
            <div className="flex bg-slate-800 rounded-lg p-1 border border-slate-700">
               {['7d', '30d', 'Month'].map(p => (
                 <button
                   key={p}
                   onClick={() => setPeriod(p)}
                   className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
                     period === p ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                   }`}
                 >
                   {p === '7d' ? '최근 7일' : p === '30d' ? '30일' : '이번달'}
                 </button>
               ))}
            </div>
            <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-4 py-2 rounded-lg font-bold text-sm transition">
              <Download size={16} /> CSV
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-3 h-96">
          <ChartCard title="매출 및 주문 추이">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={SALES_DATA_7_DAYS}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickFormatter={(val) => val.slice(5)} />
                <YAxis yAxisId="left" stroke="#3b82f6" fontSize={12} tickFormatter={(val) => `${val / 10000}만`} />
                <YAxis yAxisId="right" orientation="right" stroke="#22c55e" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                  formatter={(value: any, name: any) => [
                    name === 'revenue' ? formatCurrency(value) : `${value}건`,
                    name === 'revenue' ? '매출' : '주문수'
                  ]}
                />
                <Legend />
                <Bar yAxisId="left" dataKey="revenue" name="매출" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                <Line yAxisId="right" type="monotone" dataKey="orders" name="주문수" stroke="#22c55e" strokeWidth={3} dot={{ r: 4 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-bold text-white">상세 데이터</h3>
        <DataTable 
          data={SALES_DATA_7_DAYS}
          columns={columns}
          keyField="date"
        />
      </div>

       {/* Next Action */}
       <div className="mt-8 p-4 rounded-xl border border-slate-700 bg-slate-800/50 flex items-center gap-4">
         <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
            <Calendar size={20} />
         </div>
         <p className="text-slate-300 text-sm">
           <span className="font-bold text-white">Insight:</span> 이번주 금요일 매출이 평소보다 20% 높을 것으로 예상됩니다. 재고를 미리 확보하세요.
         </p>
      </div>
    </div>
  );
};
