import { Clock } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { HEATMAP_DATA, TIME_LABELS, DAY_LABELS } from '../data/insights.mock';

export const InsightsPage = () => {
  const getHeatmapColor = (value: number) => {
    switch (value) {
      case 0: return 'bg-slate-800/50';
      case 1: return 'bg-emerald-900/40 text-emerald-700';
      case 2: return 'bg-emerald-600/60 text-emerald-100';
      case 3: return 'bg-emerald-400 text-white shadow-lg shadow-emerald-500/30 font-bold';
      default: return 'bg-slate-800';
    }
  };

  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="시간/요일 인사이트" 
        description="매장이 가장 붐비는 시간과 한산한 시간을 시각적으로 확인하세요."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-700 bg-slate-800/50 overflow-x-auto">
          <h3 className="font-bold text-white mb-6 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            주간 혼잡도 히트맵
          </h3>
          
          <div className="min-w-[600px]">
            {/* Header Row */}
            <div className="grid grid-cols-13 gap-1 mb-2">
               <div className="col-span-1 text-slate-500 text-xs text-center font-bold"></div>
               {TIME_LABELS.map(time => (
                 <div key={time} className="col-span-1 text-slate-500 text-xs text-center">{time}시</div>
               ))}
            </div>

            {/* Data Rows */}
            {HEATMAP_DATA.map((row, dayIdx) => (
              <div key={dayIdx} className="grid grid-cols-13 gap-1 mb-1 items-center">
                 <div className="col-span-1 text-slate-400 text-xs font-bold text-center">{DAY_LABELS[dayIdx]}</div>
                 {row.map((val, hourIdx) => (
                   <div 
                     key={hourIdx} 
                     className={`col-span-1 aspect-square rounded-md flex items-center justify-center text-[10px] transition hover:scale-110 cursor-default ${getHeatmapColor(val)}`}
                     title={`${DAY_LABELS[dayIdx]}요일 ${TIME_LABELS[hourIdx]}시: 혼잡도 ${val}`}
                   >
                     {val === 3 && 'MAX'}
                   </div>
                 ))}
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex items-center gap-4 text-xs text-slate-400 justify-end">
             <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-slate-800/50 border border-slate-700"></div> 한산</div>
             <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-emerald-900/40"></div> 보통</div>
             <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-emerald-600/60"></div> 붐빔</div>
             <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-emerald-400"></div> 매우 붐빔</div>
          </div>
        </div>

        <div className="space-y-6">
           {/* Peak Time Card */}
           <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-900/50 to-slate-900 border border-emerald-500/30">
             <h3 className="font-bold text-emerald-400 text-sm uppercase mb-4">🏆 이번주 피크 타임</h3>
             <div className="text-3xl font-black text-white mb-1">금요일 19시</div>
             <p className="text-slate-400 text-sm">평소보다 주문이 <span className="text-white font-bold">2.5배</span> 많습니다.</p>
           </div>
           
           {/* Action Card */}
           <div className="p-6 rounded-2xl bg-slate-800 border border-slate-700">
             <div className="flex items-start gap-3">
               <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
                 <Clock size={20} />
               </div>
               <div>
                  <h3 className="font-bold text-white text-sm mb-1">브레이크 타임 추천</h3>
                  <p className="text-slate-400 text-xs leading-relaxed">
                    평일 <span className="text-white">15:00 ~ 17:00</span> 시간대는 주문이 가장 적습니다. 
                    재료 준비 및 휴식 시간으로 활용하세요.
                  </p>
               </div>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
};
