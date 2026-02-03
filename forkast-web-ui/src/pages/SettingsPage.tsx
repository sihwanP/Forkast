import { useState } from 'react';
import { Save, RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { useAppStore } from '../store/useAppStore';
import { formatNumber } from '../utils/format';

export const SettingsPage = () => {
  const { userSettings, updateSettings } = useAppStore();
  const [goal, setGoal] = useState(userSettings.goalRevenue.toString());
  const [openTime, setOpenTime] = useState(userSettings.openTime);
  const [closeTime, setCloseTime] = useState(userSettings.closeTime);

  const handleSave = () => {
    updateSettings({
      goalRevenue: parseInt(goal, 10),
      openTime,
      closeTime
    });
    alert('설정이 저장되었습니다.');
  };

  const handleReset = () => {
    if (confirm('모든 데이터를 초기화하시겠습니까? (Mock Data Reset)')) {
      alert('데이터가 초기화되었습니다.');
      window.location.reload();
    }
  };

  return (
    <div className='animate-fade-in'>
      <PageHeader title="설정" description="매장 운영 목표와 앱 환경을 설정합니다." />

      <div className="max-w-2xl space-y-8">
        {/* Goal Settings */}
        <section className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
          <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
            목표 매출 설정
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-slate-400 text-sm font-bold mb-2">이번 달 목표 매출 (원)</label>
              <div className="flex items-center gap-4">
                <input 
                  type="number"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white w-full focus:outline-none focus:border-blue-500 transition"
                />
                <span className="text-slate-500 font-bold whitespace-nowrap">
                  현재 설정: {formatNumber(userSettings.goalRevenue)}원
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Operating Hours */}
        <section className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
          <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <span className="w-1 h-6 bg-green-500 rounded-full"></span>
            영업 시간 설정
          </h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-slate-400 text-sm font-bold mb-2">오픈 시간</label>
              <input 
                type="time"
                value={openTime}
                onChange={(e) => setOpenTime(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white w-full focus:outline-none focus:border-green-500 transition"
              />
            </div>
            <div>
              <label className="block text-slate-400 text-sm font-bold mb-2">마감 시간</label>
              <input 
                type="time"
                value={closeTime}
                onChange={(e) => setCloseTime(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white w-full focus:outline-none focus:border-green-500 transition"
              />
            </div>
          </div>
        </section>

        {/* Notifications */}
        <section className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
          <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <span className="w-1 h-6 bg-purple-500 rounded-full"></span>
            알림 조건
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-700/50 transition cursor-pointer">
               <div>
                 <h4 className="font-bold text-white text-sm">매출 급감 알림</h4>
                 <p className="text-slate-400 text-xs">목표 대비 10% 이상 부족 시 알림</p>
               </div>
               <div className="w-12 h-6 bg-blue-600 rounded-full relative"><div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-md"></div></div>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-700/50 transition cursor-pointer">
               <div>
                 <h4 className="font-bold text-white text-sm">재고 부족 알림</h4>
                 <p className="text-slate-400 text-xs">AI가 예측한 소진 시점 3시간 전 알림</p>
               </div>
               <div className="w-12 h-6 bg-blue-600 rounded-full relative"><div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-md"></div></div>
            </div>
          </div>
        </section>

        {/* Actions */}
        <div className="flex gap-4 pt-4">
          <button 
            onClick={handleSave}
            className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition"
          >
            <Save size={20} /> 설정 저장하기
          </button>
          <button 
             onClick={handleReset}
             className="px-6 border border-red-500/50 text-red-400 hover:bg-red-500/10 rounded-xl font-bold flex items-center justify-center gap-2 transition"
            >
            <RefreshCw size={20} /> 초기화
          </button>
        </div>
      </div>
    </div>
  );
};
