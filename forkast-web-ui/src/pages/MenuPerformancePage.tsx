import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { DataTable, type Column } from '../components/DataTable';
import { ChartCard } from '../components/ChartCard';
import { formatCurrency, formatNumber } from '../utils/format';
import { MENU_PERFORMANCE, type MenuData } from '../data/menu.mock';

export const MenuPerformancePage = () => {
  const sortedMenu = [...MENU_PERFORMANCE].sort((a, b) => b.revenue - a.revenue);
  const bestMenu = sortedMenu[0];
  const worstMenu = sortedMenu[sortedMenu.length - 1];

  const columns: Column<MenuData>[] = [
    { header: '메뉴명', accessor: 'name' as keyof MenuData, className: 'font-bold text-white' },
    { header: '카테고리', accessor: 'category' as keyof MenuData, className: 'text-slate-400' },
    { header: '가격', accessor: (item: MenuData) => formatCurrency(item.price), className: 'text-right' },
    { header: '판매수', accessor: (item: MenuData) => `${formatNumber(item.salesCount)}개`, className: 'text-right' },
    { header: '매출', accessor: (item: MenuData) => formatCurrency(item.revenue), className: 'text-right font-bold text-blue-400' },
    { 
      header: '트렌드', 
      accessor: (item: MenuData) => (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold ${
          item.trend === 'up' ? 'text-green-400 bg-green-500/10' :
          item.trend === 'down' ? 'text-red-400 bg-red-500/10' : 'text-slate-400 bg-slate-500/10'
        }`}>
          {item.trend === 'up' ? <ArrowUpRight size={14} /> : 
           item.trend === 'down' ? <ArrowDownRight size={14} /> : <Minus size={14} />}
          {item.trend === 'up' ? '상승' : item.trend === 'down' ? '하락' : '유지'}
        </span>
      ), 
      className: 'text-center' 
    },
  ];

  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="메뉴 성과 분석" 
        description="어떤 메뉴가 효자 상품인지, 개선이 필요한지 파악하세요."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10 text-6xl">🍗</div>
          <p className="text-orange-400 text-xs font-bold uppercase mb-2">BEST SELLER</p>
          <h3 className="text-2xl font-bold text-white mb-2">{bestMenu.name}</h3>
          <p className="text-slate-400 text-sm">총 매출의 <span className="text-white font-bold">42%</span> 차지</p>
          <div className="mt-4 w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
             <div className="bg-orange-500 h-full" style={{ width: '42%' }}></div>
          </div>
        </div>
        
        <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10 text-6xl">📉</div>
           <p className="text-red-400 text-xs font-bold uppercase mb-2">WORST PERFORMER</p>
          <h3 className="text-2xl font-bold text-white mb-2">{worstMenu.name}</h3>
          <p className="text-slate-400 text-sm">전월 대비 주문수 <span className="text-white font-bold">15% 감소</span></p>
           <div className="mt-4 w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
             <div className="bg-red-500 h-full" style={{ width: '15%' }}></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <ChartCard title="메뉴별 매출 비교">
             <ResponsiveContainer width="100%" height={350}>
              <BarChart data={sortedMenu} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `${val / 10000}만`} />
                <YAxis dataKey="name" type="category" stroke="#e2e8f0" fontSize={12} width={80} />
                <Tooltip 
                  cursor={{ fill: '#334155', opacity: 0.2 }}
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                  formatter={(value: any) => formatCurrency(value)}
                />
                <Bar dataKey="revenue" radius={[0, 4, 4, 0]} barSize={20}>
                  {sortedMenu.map((entry, index) => (
                    <Cell key={entry.id} fill={index === 0 ? '#f97316' : '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div>
          <h3 className="text-lg font-bold text-white mb-4">전체 메뉴 리스트</h3>
           <DataTable 
            data={sortedMenu} 
            columns={columns.filter(c => c.header !== '카테고리')} 
            keyField="id" 
          />
        </div>
      </div>
    </div>
  );
};
