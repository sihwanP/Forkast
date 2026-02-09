import { useNavigate } from 'react-router-dom';

export const AdminPage = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white p-6">
            <div className="max-w-md w-full bg-slate-800 rounded-2xl p-8 shadow-2xl border border-slate-700 text-center">
                <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30">
                    <i className="fa-solid fa-user-shield text-3xl"></i>
                </div>
                
                <h1 className="text-3xl font-black mb-2">관리자 포털</h1>
                <p className="text-slate-400 mb-8">접근하려는 관리자 권한을 선택해주세요.</p>
                
                <div className="space-y-4">
                    <button 
                        onClick={() => navigate('/super-admin')}
                        className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl font-bold text-lg hover:from-blue-500 hover:to-indigo-500 transition shadow-lg flex items-center justify-center gap-3"
                    >
                        <i className="fa-solid fa-gauge-high"></i>
                        통합 관제 콘솔 (권장)
                    </button>
                    
                    <a 
                        href={`http://${window.location.hostname}:8000/admin/`}
                        className="block w-full py-4 bg-slate-700 rounded-xl font-bold text-lg hover:bg-slate-600 transition shadow-lg text-slate-300 flex items-center justify-center gap-3"
                        target="_blank"
                        rel="noreferrer"
                    >
                        <i className="fa-brands fa-python"></i>
                        Django Admin (로컬)
                    </a>
                </div>
                
                <p className="mt-8 text-xs text-slate-500">
                    * Django Admin은 로컬 환경에서만 접속 가능합니다.
                    <br />
                    * 통합 관제 콘솔은 React 전용 UI입니다 (Mock Data).
                </p>
            </div>
        </div>
    );
};
