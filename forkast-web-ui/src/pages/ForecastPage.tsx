import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  ReferenceLine 
} from 'recharts';
import { BrainCircuit, Sparkles } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { ChartCard } from '../components/ChartCard';
import { StatCard } from '../components/StatCard';
import { formatCurrency } from '../utils/format';

const PREDICTION_DATA = [
  { date: '오늘', actual: 1250000, predicted: 1200000 },
  { date: '내일', actual: null, predicted: 1350000 }, // Future
  { date: '모레', actual: null, predicted: 1100000 },
  { date: '3일후', actual: null, predicted: 1450000 },
  { date: '4일후', actual: null, predicted: 1600000 },
  { date: '5일후', actual: null, predicted: 1900000 }, // Weekend
  { date: '6일후', actual: null, predicted: 1850000 },
];

export const ForecastPage = () => {
  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="AI 매출 예측" 
        description="Forkast AI가 분석한 향후 매출 예측 리포트입니다."
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard 
          label="내일 예상 매출" 
          value={formatCurrency(1350000)}
          trend={{ value: '+8%', direction: 'up', label: '오늘 대비' }}
          icon={Sparkles}
          color="purple"
        />
         <StatCard 
          label="이번 주 예상 총 매출" 
          value={formatCurrency(9850000)}
          trend={{ value: '목표 달성 유력', direction: 'flat' }}
          icon={BrainCircuit}
          color="blue"
        />
        <div className="p-6 rounded-2xl border border-blue-500/30 bg-blue-900/20 flex flex-col justify-center">
           <h3 className="text-blue-400 font-bold mb-2">AI 모델 신뢰도</h3>
           <div className="flex items-end gap-2">
             <span className="text-4xl font-black text-white">94.3%</span>
           </div>
           <div className="w-full bg-slate-700 h-2 rounded-full mt-3 overflow-hidden">
             <div className="bg-blue-500 h-full" style={{ width: '94.3%' }}></div>
           </div>
           <p className="text-xs text-slate-400 mt-2">최근 30일 예측 정확도 기준</p>
        </div>
      </div>

      <div className="mb-8 h-96">
        <ChartCard title="향후 7일 매출 예측">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={PREDICTION_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `${val / 10000}만`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                formatter={(value: any) => formatCurrency(value)}
              />
              <ReferenceLine x="오늘" stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'top', value: '오늘', fill: '#ef4444', fontSize: 12 }} />
              <Line type="monotone" dataKey="actual" name="실제 매출" stroke="#94a3b8" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="predicted" name="AI 예측" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* AI Explanation Box */}
      <div className="p-6 rounded-2xl border border-purple-500/30 bg-slate-800/50">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <BrainCircuit size={20} className="text-purple-400" />
          예측 근거 분석
        </h3>
        <ul className="space-y-3 text-slate-300">
          <li className="flex gap-2">
            <span className="text-purple-400 font-bold">•</span>
            내일(수요일)은 통상적인 주중 매출 패턴을 따르며, 날씨가 맑아 내방 고객이 5% 증가할 것으로 예상됩니다.
          </li>
          <li className="flex gap-2">
            <span className="text-purple-400 font-bold">•</span>
            금요일 저녁에는 인근 지역 행사로 인해 배달 주문이 급증할 가능성이 높습니다 (작년 데이터 기반).
          </li>
        </ul>
      </div>
    </div>
  );
};
