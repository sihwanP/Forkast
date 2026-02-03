import { useNavigate } from 'react-router-dom';
import { 
  BarChart2, 
  ShoppingBag, 
  CreditCard, 
  TrendingUp, 
  ArrowRight 
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { formatCurrency, formatNumber } from '../utils/format';
import { SALES_DATA_7_DAYS } from '../data/sales.mock';
import { MENU_PERFORMANCE } from '../data/menu.mock';
import { useAppStore } from '../store/useAppStore';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const alerts = useAppStore(state => state.alerts);
  const unreadAlerts = alerts.filter(a => !a.read).slice(0, 3);
  const topMenu = [...MENU_PERFORMANCE].sort((a, b) => b.revenue - a.revenue).slice(0, 3);

  // Derive Mock KPI
  const todayRevenue = 1250000;

  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="대시보드" 
        description="오늘의 매장 현황을 한눈에 확인하세요."
        action={
          <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-bold text-sm transition">
            리포트 다운로드
          </button>
        }
      />

      {/* KPI Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          label="오늘 총 매출" 
          value={formatCurrency(todayRevenue)} 
          trend={{ value: '8.7%', direction: 'up', label: '전일 대비' }}
          icon={BarChart2}
          color="blue"
        />
        <StatCard 
          label="총 주문 수" 
          value="45건" 
          trend={{ value: '12%', direction: 'up', label: '지난주 동요일 대비' }}
          icon={ShoppingBag}
          color="green"
        />
        <StatCard 
          label="객단가" 
          value={formatCurrency(27800)} 
          trend={{ value: '1.2%', direction: 'down', label: '평균 대비' }}
          icon={CreditCard}
          color="purple"
        />
        <StatCard 
          label="오늘 성장률" 
          value="+8.7%" 
          trend={{ value: '양호', direction: 'flat', label: '목표 달성 중' }}
          icon={TrendingUp}
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart */}
        <div className="lg:col-span-2">
          <ChartCard title="최근 7일 매출 추이" subtitle="지난주 대비 평균 15% 상승했습니다.">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={SALES_DATA_7_DAYS}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickFormatter={(val) => val.slice(5)} />
                <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `${val / 10000}만`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                  formatter={(value: any) => [formatCurrency(value), '매출']}
                />
                <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Sidebar Widgets (Top Menu & Alerts) */}
        <div className="space-y-8">
          {/* Top Menu */}
          <div className="p-6 rounded-2xl border border-slate-700 bg-slate-800/50">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-white">🔥 인기 메뉴 TOP 3</h3>
              <button 
                onClick={() => navigate('/menu-performance')}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                더보기
              </button>
            </div>
            <div className="space-y-4">
              {topMenu.map((menu, idx) => (
                <div key={menu.id} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center font-bold text-slate-300">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-bold text-slate-200">{menu.name}</p>
                    <p className="text-xs text-slate-400">{formatNumber(menu.salesCount)}개 판매</p>
                  </div>
                  <div className="text-sm font-bold text-slate-300">
                    {formatCurrency(menu.revenue)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="p-6 rounded-2xl border border-slate-700 bg-slate-800/50">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-white">🔔 최근 알림</h3>
              <button 
                onClick={() => navigate('/alerts')}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                전체보기
              </button>
            </div>
            {unreadAlerts.length > 0 ? (
              <div className="space-y-3">
                {unreadAlerts.map((alert) => (
                  <div 
                    key={alert.id} 
                    onClick={() => navigate(alert.link || '/alerts')}
                    className="p-3 rounded-lg bg-slate-700/30 border border-slate-700 hover:bg-slate-700/50 cursor-pointer transition"
                  >
                    <div className="flex items-start justify-between">
                      <span className={`text-xs font-bold px-1.5 py-0.5 rounded uppercase ${
                        alert.type === 'danger' ? 'bg-red-500/20 text-red-400' :
                        alert.type === 'warn' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {alert.type}
                      </span>
                      <span className="text-[10px] text-slate-500">방금 전</span>
                    </div>
                    <p className="text-sm font-bold text-slate-200 mt-1">{alert.title}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm text-center py-4">새로운 알림이 없습니다.</p>
            )}
          </div>
        </div>
      </div>
      
      {/* Next Action */}
      <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
           <div className="p-2 bg-blue-500 rounded-lg text-white">
             <TrendingUp size={20} />
           </div>
           <div>
             <h4 className="font-bold text-blue-100">AI 매니저의 제안</h4>
             <p className="text-sm text-blue-200">내일 저녁 시간대 비 예보가 있습니다. 배달 전용 쿠폰을 발행하여 매출을 방어하세요.</p>
           </div>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-bold text-sm transition">
          액션 실행하기 <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
};
