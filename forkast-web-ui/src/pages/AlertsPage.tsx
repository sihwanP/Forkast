import { useState } from 'react';
import { Bell, CheckCircle, AlertTriangle, Info, AlertOctagon } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { useAppStore } from '../store/useAppStore';

export const AlertsPage = () => {
  const { alerts, markAlertRead, markAllAlertsRead } = useAppStore();
  const [filter, setFilter] = useState<'all' | 'unread' | 'danger'>('all');

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'unread') return !alert.read;
    if (filter === 'danger') return alert.type === 'danger';
    return true;
  });

  const getIcon = (type: string) => {
    switch (type) {
      case 'danger': return <AlertOctagon size={24} className="text-red-400" />;
      case 'warn': return <AlertTriangle size={24} className="text-orange-400" />;
      case 'info': return <Info size={24} className="text-blue-400" />;
      default: return <Bell size={24} className="text-slate-400" />;
    }
  };

  return (
    <div className='animate-fade-in'>
      <PageHeader 
        title="알림 센터" 
        description="매장 운영에 필요한 주요 알림을 확인하세요."
        action={
          <button 
            onClick={markAllAlertsRead}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition text-sm"
          >
            <CheckCircle size={16} /> 모두 읽음으로 표시
          </button>
        }
      />

      <div className="flex gap-4 mb-6 border-b border-slate-700 pb-4">
        <button 
          onClick={() => setFilter('all')}
          className={`text-sm font-bold pb-2 border-b-2 transition ${filter === 'all' ? 'text-white border-blue-500' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
        >
          전체
        </button>
        <button 
          onClick={() => setFilter('unread')}
          className={`text-sm font-bold pb-2 border-b-2 transition ${filter === 'unread' ? 'text-white border-blue-500' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
        >
          미확인
        </button>
        <button 
          onClick={() => setFilter('danger')}
          className={`text-sm font-bold pb-2 border-b-2 transition ${filter === 'danger' ? 'text-white border-blue-500' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
        >
          긴급
        </button>
      </div>

      <div className="space-y-4">
        {filteredAlerts.length > 0 ? filteredAlerts.map(alert => (
          <div 
            key={alert.id}
            onClick={() => markAlertRead(alert.id)}
            className={`p-6 rounded-xl border transition cursor-pointer hover:bg-slate-800 ${
              alert.read 
                ? 'bg-slate-900 border-slate-800 opacity-60' 
                : 'bg-slate-800/50 border-slate-700 shadow-lg'
            }`}
          >
            <div className="flex gap-4">
              <div className={`p-3 rounded-xl h-fit ${
                alert.type === 'danger' ? 'bg-red-500/10' : 
                alert.type === 'warn' ? 'bg-orange-500/10' : 'bg-blue-500/10'
              }`}>
                {getIcon(alert.type)}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-1">
                  <h4 className={`font-bold ${alert.read ? 'text-slate-400' : 'text-white'}`}>{alert.title}</h4>
                  <span className="text-xs text-slate-500">{new Date(alert.createdAt).toLocaleDateString()}</span>
                </div>
                <p className="text-slate-400 text-sm mb-3">{alert.message}</p>
                {alert.link && (
                  <span className="text-xs text-blue-400 font-bold hover:underline">바로가기 →</span>
                )}
              </div>
            </div>
          </div>
        )) : (
          <div className="text-center py-20 text-slate-500">
            <Bell size={48} className="mx-auto mb-4 opacity-20" />
            <p>표시할 알림이 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
};
