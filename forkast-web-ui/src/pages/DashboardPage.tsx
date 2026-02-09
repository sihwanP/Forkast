import { useState, useEffect } from 'react';
import { 
  BarChart2, 
  TrendingUp, 
  Play,
  Check,
  Rocket,
  Package,
  Users
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { formatCurrency } from '../utils/format';
import { SALES_DATA_7_DAYS } from '../data/sales.mock';

export const DashboardPage = () => {
  const [currentRevenue] = useState(1250000); // 1,250,000
  const [targetRevenue] = useState(1000000);  // 1,000,000
  const [performanceRatio] = useState(125.0);
  const [activeVideo, setActiveVideo] = useState<string | null>(null);
  
  // Strategy Modals State
  const [activeStrategy, setActiveStrategy] = useState<number | null>(null);

  const strategies = [
    {
       id: 0,
       title: "긴급 타임 세일",
       icon: Rocket,
       color: "blue",
       desc: "오후 2시~4시 15% 할인 적용하여 방문율 극대화",
       score: 92,
       fullDesc: "유동 인구가 많은 오후 2시~4시 시간대에 할인을 적용하여 방문율과 객단가를 동시에 극대화하세요."
    },
    {
       id: 1,
       title: "재고 최적화",
       icon: Package,
       color: "indigo",
       desc: "인기 품목 선제적 발주로 품절 방지",
       score: 85,
       fullDesc: "주말 대비 수요가 높을 것으로 예상되는 주요 원재료와 인기 품목의 재고를 선제적으로 확보하세요."
    },
    {
       id: 2,
       title: "인력 효율화",
       icon: Users,
       color: "emerald",
       desc: "피크타임 파트타임 배치로 서비스 품질 유지",
       score: 88,
       fullDesc: "매출 집중 시간대에 숙련된 인력을 재배치하여 서비스 속도와 만족도를 최상으로 유지하세요."
    }
  ];

  useEffect(() => {
    // Add simple animation or fetch logic here if needed
  }, []);

  return (
    <div className='animate-fade-in text-slate-100 font-sans'>
      
      {/* 2. Hero Section (Replicated from dashboard.html) */}
      <section className="relative overflow-hidden flex items-end pb-20 min-h-screen">
        {/* Background Video */}
        <div className="absolute top-0 left-0 w-full h-full z-[-1]">
             <video className="w-full h-full object-cover" autoPlay muted loop playsInline>
                <source src="/videos/hero.mp4" type="video/mp4" />
             </video>
             <div className="absolute inset-0 bg-gray-900/40"></div>
        </div>
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent z-0"></div>

        <div className="relative z-10 max-w-7xl mx-auto w-full px-6 flex flex-col lg:flex-row items-end gap-12">
            <div className="flex-1 text-left lg:mb-10">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6 backdrop-blur-sm">
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                    <span className="text-sm font-black text-blue-400 uppercase tracking-wider">Forkast AI Analytics Engine</span>
                </div>
                <h1 className="font-black mb-6 text-white tracking-tight leading-[1.15]">
                    <span className="text-6xl lg:text-7xl block">지능형 매출</span>
                    <span className="text-6xl lg:text-7xl block bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 text-transparent bg-clip-text">예측 분석 플랫폼</span>
                </h1>
                <p className="text-lg text-slate-300 max-w-lg font-medium leading-relaxed">
                    AI 기반 실시간 POS 데이터 분석으로 매출 트렌드를 예측하고,<br/>데이터 기반의 전략적 의사결정을 지원합니다.
                </p>
            </div>

            {/* Performance Status Widget */}
            <div className="w-full lg:w-[480px] flex-none">
                <div className="p-8 rounded-[2.5rem] border border-white/10 transition-all bg-gradient-to-br from-emerald-500/10 to-transparent border-emerald-500/30 text-emerald-500 backdrop-blur-md">
                    <div className="flex justify-between items-start mb-5">
                        <span className="text-sm font-black uppercase tracking-[0.15em] opacity-60 whitespace-nowrap text-white">실시간 시스템 상태</span>
                        <div className="flex items-center gap-4 px-4 py-2 rounded-md bg-white/5 border border-white/10">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            <span className="text-sm font-black tracking-wide uppercase whitespace-nowrap text-white">데이터 실시간 수신 중</span>
                        </div>
                    </div>
                    
                    <h2 className="text-4xl font-black mb-2 text-emerald-400">흑자 달성</h2>
                    <p className="text-lg font-medium opacity-80 mb-6 text-white">
                        목표 매출 대비 <span className="font-black text-emerald-400">{performanceRatio}%</span> 달성 중
                    </p>
                    
                    <div className="w-full h-3 bg-black/20 rounded-full overflow-hidden mb-4">
                        <div className="h-full bg-emerald-500 transition-all duration-1000" style={{ width: `${performanceRatio}%`, maxWidth: '100%' }}></div>
                    </div>
                    
                    <div className="flex justify-between text-base font-bold opacity-60 text-white">
                        <span>현재 {formatCurrency(currentRevenue)}</span>
                        <span>목표 {formatCurrency(targetRevenue)}</span>
                    </div>
                </div>
            </div>
        </div>
      </section>

      {/* 3. Service Explanation Video */}
      <section className="py-20 bg-gray-800">
        <div className="max-w-7xl mx-auto w-full flex flex-col md:flex-row items-center gap-16 px-6">
            <div className="w-full md:w-1/2">
                <div 
                  onClick={() => setActiveVideo("/videos/service.mp4")}
                  className="aspect-video bg-gray-700 rounded-xl overflow-hidden shadow-2xl flex items-center justify-center relative group cursor-pointer hover:ring-4 ring-blue-500/50 transition"
                >
                    <video className="w-full h-full object-cover pointer-events-none" muted loop playsInline>
                        <source src="/videos/service.mp4" type="video/mp4" />
                    </video>
                    <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 flex items-center justify-center transition">
                        <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:scale-110 transition border border-white/30">
                            <Play className="text-white fill-white ml-2" size={32} />
                        </div>
                    </div>
                </div>
            </div>
            <div className="w-full md:w-1/2 text-left">
                <div className="inline-block py-2 px-4 rounded-lg bg-blue-500/10 text-blue-400 text-base font-black uppercase tracking-widest mb-6 border border-blue-500/20">데이터 전략 엔진</div>
                <h2 className="text-4xl lg:text-6xl font-black mb-8 leading-[1.2] tracking-tighter text-white">AI가 설계하는<br/><span className="text-blue-500">초개인화</span> 비즈니스 로직</h2>
                <p className="text-lg text-slate-400 font-light leading-relaxed">Forkast의 AI는 단순한 통계 그 이상입니다. 실시간 시장 변동성과 매장의 고유 특성을 결합하여 오직 당신만을 위한 최적의 경영 전략을 실시간으로 도출합니다.</p>
            </div>
        </div>
      </section>

      {/* 4. Promo Video */}
      <section className="py-20 bg-gray-900">
          <div className="max-w-7xl mx-auto w-full text-center px-6">
              <h2 className="text-4xl font-bold mb-12 text-white">성공하는 사장님들의 비밀</h2>
              <div 
                onClick={() => setActiveVideo("/videos/promo.mp4")}
                className="aspect-video bg-gray-800 rounded-xl overflow-hidden shadow-2xl mx-auto max-w-5xl flex items-center justify-center relative cursor-pointer group hover:ring-4 ring-blue-500/50 transition"
              >
                  <video className="w-full h-full object-cover pointer-events-none" muted loop playsInline>
                      <source src="/videos/promo.mp4" type="video/mp4" />
                  </video>
                  <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 flex items-center justify-center transition">
                      <div className="w-24 h-24 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:scale-110 transition border border-white/30">
                           <Play className="text-white fill-white ml-2" size={40} />
                      </div>
                  </div>
              </div>
          </div>
      </section>

      {/* 5. AI Sales Analysis (Visual Replication) */}
      <section className="py-20 bg-gray-800">
          <div className="max-w-7xl mx-auto w-full px-6">
              <h2 className="text-4xl font-bold mb-12 text-center text-white">실시간 매출 분석 및 흐름 예측</h2>
              
              <div className="mb-5 flex justify-between items-end border-b border-gray-700 pb-5">
                  <div>
                      <h3 className="text-3xl font-black text-white tracking-tight">실시간 인텔리전스 분석</h3>
                      <p className="text-slate-300 mt-4 text-base font-medium">데이터 스트림을 통한 AI 매출 가설 검증 및 인사이트 추출</p>
                  </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16 items-stretch">
                  <div className="flex flex-col gap-6 h-full">
                       {/* Sales Chart */}
                       <div className="p-1 rounded-3xl bg-gradient-to-br from-white/10 to-transparent relative shadow-2xl overflow-hidden group">
                           <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-600/10 rounded-full blur-3xl group-hover:bg-blue-600/20 transition-all duration-700"></div>
                           <div className="bg-gray-900/80 backdrop-blur-xl rounded-[1.4rem] p-6 h-[400px] flex flex-col relative text-center border border-white/5">
                               <div className="flex items-center justify-between mb-4 px-2">
                                  <h3 className="text-base font-bold text-blue-400 uppercase tracking-widest flex items-center gap-2">
                                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></span>
                                      실시간 매출 흐름
                                  </h3>
                                  <span className="text-base text-gray-300 font-medium">오늘 00:00 - 현재</span>
                               </div>
                               <ResponsiveContainer width="100%" height="100%">
                                  <AreaChart data={SALES_DATA_7_DAYS}>
                                    <defs>
                                      <linearGradient id="colorRevenue2" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                      </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} vertical={false} />
                                    <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickFormatter={(val) => val.slice(5)} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#9ca3af" fontSize={12} tickFormatter={(val) => `${val / 10000}만`} tickLine={false} axisLine={false} />
                                    <Tooltip 
                                      contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                                      itemStyle={{ color: '#fff' }}
                                      formatter={(value: any) => [formatCurrency(value), '매출']}
                                    />
                                    <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue2)" />
                                  </AreaChart>
                                </ResponsiveContainer>
                           </div>
                       </div>
                  </div>

                  {/* AI Analysis Report */}
                  <div className="flex flex-col h-full">
                      <div className="p-8 rounded-3xl border border-blue-500/20 bg-blue-900/10 relative overflow-hidden shadow-2xl h-full backdrop-blur-sm">
                          <div className="flex items-center gap-4 mb-8">
                              <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-500/40 shrink-0">
                                   <BarChart2 size={24} />
                              </div>
                              <div>
                                  <h3 className="text-2xl font-black text-white">AI 지능형 비교 분석 리포트</h3>
                                  <div className="mt-1 flex items-center gap-3 flex-wrap">
                                      <span className="px-3 py-1 bg-white/10 text-blue-300 text-xs font-bold rounded border border-blue-500/20">Forkast Neural Engine v2.4</span>
                                      <span className="text-xs text-blue-100/40 font-medium">실시간 데이터 스트림 분석 중</span>
                                  </div>
                              </div>
                          </div>

                          {/* Grid */}
                          <div className="grid grid-cols-2 gap-4 mb-8 relative">
                              <div className="p-5 bg-gradient-to-br from-white/10 to-transparent rounded-2xl border border-white/10 text-center relative overflow-hidden group">
                                  <p className="text-sm font-bold text-blue-200 uppercase mb-2">실시간 매출 (Today)</p>
                                  <p className="text-3xl font-black text-white tracking-tight">{formatCurrency(currentRevenue)}</p>
                              </div>
                              <div className="p-5 bg-gradient-to-br from-white/5 to-transparent rounded-2xl border border-white/5 text-center relative overflow-hidden group">
                                  <p className="text-sm font-bold text-gray-400 uppercase mb-2">전주 동기 (Past)</p>
                                  <p className="text-3xl font-black text-gray-300 tracking-tight">{formatCurrency(1000000)}</p>
                              </div>
                              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-14 h-14 bg-gray-900 rounded-full border-4 border-gray-800 flex items-center justify-center shadow-xl z-10">
                                  <span className="text-emerald-400 font-black text-sm">+25%</span>
                              </div>
                          </div>

                          <div className="space-y-6">
                              <div className="bg-blue-950/30 rounded-2xl p-6 border border-blue-500/10">
                                  <h4 className="text-xs font-black text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></span> 종합 진단
                                  </h4>
                                  <p className="text-xl font-bold text-white mb-3 leading-snug">현재 매장이 [흑자/양호] 상태를 유지하고 있습니다.</p>
                                  <p className="text-sm text-blue-100/70 font-medium leading-relaxed">지난주 동기 대비 매출이 250,000원 (상승) 했습니다.</p>
                              </div>

                              <div>
                                  <h4 className="text-xs font-black text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                                     <TrendingUp size={14} /> 주요 원인 분석
                                  </h4>
                                  <p className="text-gray-300 text-sm leading-relaxed pl-4 border-l-2 border-indigo-500/30 italic">단골 고객의 객단가가 전주 대비 12% 상승하며 전체 실적을 견인했습니다.</p>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </section>

      {/* 9. Strategy Section */}
      <section className="py-24 bg-gray-900 relative overflow-hidden">
         <div className="relative max-w-7xl mx-auto px-6">
            <h2 className="text-4xl font-extrabold mb-16 text-center text-white tracking-tight">
                최적 운영 전략 제안 <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent px-2">(AI)</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
               {strategies.map((st) => (
                 <div 
                    key={st.id} 
                    onClick={() => setActiveStrategy(st.id)}
                    className="group relative bg-gray-800 rounded-2xl p-8 shadow-md hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 border border-gray-700 overflow-hidden cursor-pointer"
                 >
                     <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-${st.color}-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity`}></div>
                     <div className="h-16 w-16 bg-gray-700 rounded-2xl mb-6 flex items-center justify-center text-3xl group-hover:scale-110 transition-transform duration-300 shadow-inner text-white">
                        <st.icon size={32} />
                     </div>
                     <h3 className={`text-2xl font-bold mb-4 text-white group-hover:text-${st.color}-400 transition-colors`}>{st.title}</h3>
                     <p className="leading-relaxed font-bold text-sm mb-4 text-gray-400">{st.desc}</p>
                     <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                           <div className={`h-full bg-${st.color}-500`} style={{ width: `${st.score}%` }}></div>
                        </div>
                        <span className={`text-xs font-black text-${st.color}-400`}>{st.score}점</span>
                     </div>
                 </div>
               ))}
            </div>
         </div>
      </section>

      {/* Footer */}
      <footer className="mt-20 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-sm py-12 px-6 lg:px-12">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8 text-white">
            <div className="md:col-span-2">
                <div className="flex items-center gap-2 mb-4">
                    <span className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">Forkast AI</span>
                </div>
                <p className="text-gray-400 mb-4 max-w-sm">
                    AI 기반 데일리 매출 예측 및 매장 관리 솔루션.<br/>
                    데이터로 증명하는 성공, 포카스트와 함께하세요.
                </p>
                <div className="flex gap-4">
                   {['🐦', '📘', '📸'].map(icon => (
                     <a key={icon} href="#" className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-gray-400 hover:bg-blue-600 hover:text-white transition">{icon}</a>
                   ))}
                </div>
            </div>
            {/* Links Omitted for Brevity in this Mock */}
        </div>
      </footer>

      {/* Video Modal */}
      {activeVideo && (
        <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/90 animate-in fade-in duration-200">
           <div className="absolute inset-0" onClick={() => setActiveVideo(null)}></div>
           <div className="relative w-full max-w-5xl aspect-video bg-black rounded-xl overflow-hidden shadow-2xl z-10">
               <button onClick={() => setActiveVideo(null)} className="absolute top-4 right-4 text-white text-3xl z-50 hover:text-red-500 transition">&times;</button>
               <video className="w-full h-full" controls autoPlay>
                   <source src={activeVideo} type="video/mp4" />
               </video>
           </div>
        </div>
      )}

      {/* Strategy Modal */}
      {activeStrategy !== null && (
        <div className="fixed inset-0 z-[300] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="absolute inset-0" onClick={() => setActiveStrategy(null)}></div>
            <div className="relative bg-white border border-slate-200 p-10 rounded-3xl max-w-2xl w-full mx-4 shadow-2xl animate-in zoom-in duration-300">
                 <button onClick={() => setActiveStrategy(null)} className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 text-2xl font-bold">&times;</button>
                 
                 {/* Icon */}
                 <div className={`h-20 w-20 bg-${strategies[activeStrategy].color}-50 rounded-2xl mb-8 flex items-center justify-center text-slate-800`}>
                    {(() => {
                        const Icon = strategies[activeStrategy].icon;
                        return <Icon size={48} className={`text-${strategies[activeStrategy].color}-600`} />;
                    })()}
                 </div>

                 <h3 className="text-3xl font-black mb-6 text-slate-900">{strategies[activeStrategy].title}</h3>
                 <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100 mb-8">
                     <p className="leading-relaxed font-bold text-lg text-slate-700">{strategies[activeStrategy].fullDesc}</p>
                 </div>
                 <button onClick={() => setActiveStrategy(null)} className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition shadow-lg flex items-center justify-center gap-2">
                    <Check size={20} /> 확인
                 </button>
            </div>
        </div>
      )}

    </div>
  );
};
