import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { PageHeader } from '../components/PageHeader';
import { ChartCard } from '../components/ChartCard';
import { DataTable, type Column } from '../components/DataTable';
import { formatCurrency, formatNumber } from '../utils/format';
import { DELIVERY_DATA, type DeliveryPlatformData } from '../data/delivery.mock';

export const DeliveryPage = () => {
  const columns: Column<DeliveryPlatformData>[] = [
    { header: '플랫폼', accessor: 'name' as keyof DeliveryPlatformData, className: 'font-bold' },
    { header: '주문수', accessor: (item: DeliveryPlatformData) => formatNumber(item.orders), className: 'text-right' },
    { header: '수수료율', accessor: (item: DeliveryPlatformData) => `${item.feeRate}%`, className: 'text-right text-slate-400' },
    { header: '순매출', accessor: (item: DeliveryPlatformData) => formatCurrency(item.revenue), className: 'text-right font-bold text-blue-400' },
  ];

  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="배달 분석" 
        description="플랫폼별 매출 비중과 수수료 효율을 분석합니다."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="h-80">
          <ChartCard title="플랫폼별 매출 비중">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={DELIVERY_DATA}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="revenue"
                >
                  {DELIVERY_DATA.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} stroke="none" />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                  formatter={(value: any) => formatCurrency(value)}
                />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div className="h-80">
          <ChartCard title="주문 건수 비교">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={DELIVERY_DATA} layout="vertical" margin={{ left: 20 }}>
                 <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} horizontal={false} />
                 <XAxis type="number" stroke="#94a3b8" fontSize={12} />
                 <YAxis dataKey="name" type="category" stroke="#e2e8f0" fontSize={12} width={80} />
                 <Tooltip 
                   cursor={{ fill: '#334155', opacity: 0.2 }}
                   contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                   formatter={(value: any) => [value, '주문수']}
                 />
                 <Bar dataKey="orders" name="주문수" radius={[0, 4, 4, 0]} barSize={30}>
                    {DELIVERY_DATA.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                 </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </div>

      <h3 className="text-xl font-bold text-white mb-4">상세 수익 분석</h3>
      <DataTable 
        data={DELIVERY_DATA}
        columns={columns}
        keyField="name"
      />
    </div>
  );
};
