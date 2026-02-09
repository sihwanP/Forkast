import { useState, useEffect } from 'react';

// --- Sub Components (Moved to top for clarity or separate files in real app) ---

const KpiCard = ({ title, value, unit, color, icon }: any) => {
    const colorClasses: any = {
        red: "border-l-red-500 text-red-600 bg-red-50",
        blue: "border-l-blue-500 text-blue-600 bg-blue-50",
        indigo: "border-l-indigo-500 text-indigo-600 bg-indigo-50",
        emerald: "border-l-emerald-500 text-emerald-600 bg-emerald-50",
    };
    
    return (
        <div className={`bg-white p-6 border border-slate-200 border-l-8 rounded-2xl shadow-sm hover:-translate-y-1 transition-transform ${colorClasses[color].split(' ')[0]}`}>
            <div className="text-slate-400 text-xs font-black uppercase tracking-widest mb-4">{title}</div>
            <div className="flex items-end justify-between">
                <div className="text-4xl font-black text-slate-900 leading-none">
                    {value.toLocaleString()} <span className="text-lg font-bold text-slate-400 ml-1">{unit}</span>
                </div>
                <div className={`p-3 rounded-2xl shadow-inner ${colorClasses[color].split(' ').slice(1).join(' ')}`}>
                    <i className={`fa-solid ${icon} text-2xl`}></i>
                </div>
            </div>
        </div>
    );
};

const SectionTitle = ({ icon, title, color }: any) => (
    <div className={`flex items-center gap-3 mb-5 ${color}`}>
        <i className={`fa-solid ${icon} text-2xl`}></i>
        <span className="text-2xl font-black">{title}</span>
    </div>
);

const CardContainer = ({ color, title, icon, table, children }: any) => {
     const colorMap: any = {
        blue: "border-t-blue-500",
        emerald: "border-t-emerald-500",
        rose: "border-t-rose-500",
        amber: "border-t-amber-500",
     };
     
     const bgMap: any = {
        blue: "bg-blue-100 text-blue-600",
        emerald: "bg-emerald-100 text-emerald-600",
        rose: "bg-rose-100 text-rose-600",
        amber: "bg-amber-100 text-amber-600",
     };

     return (
        <div className={`bg-white border border-slate-200 rounded-2xl shadow-lg overflow-hidden flex flex-col border-t-4 ${colorMap[color]}`}>
            <div className="p-6 border-b border-slate-100 flex justify-between items-start bg-slate-50/50">
                 <div className="flex items-center gap-4">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-sm ${bgMap[color]}`}>
                        <i className={`fa-solid ${icon} text-2xl`}></i>
                    </div>
                    <div>
                        <h3 className="font-black text-slate-800 text-2xl tracking-tight">{title}</h3>
                        <div className="mt-2">
                             <span className="px-3 py-1 bg-slate-900 text-white text-xs font-black rounded-lg shadow-sm">
                                BASE: {table}
                             </span>
                        </div>
                    </div>
                </div>
            </div>
            <div className="flex-1 overflow-x-auto p-2">
                {children}
            </div>
        </div>
     );
}

const StatusBadge = ({ status }: { status: string }) => {
    if (status === 'LOW') return <span className="px-3 py-1 bg-rose-100 text-rose-700 font-black rounded-full text-sm">부족</span>;
    if (status === 'OVER') return <span className="px-3 py-1 bg-amber-100 text-amber-700 font-black rounded-full text-sm">과다</span>;
    return <span className="px-3 py-1 bg-emerald-100 text-emerald-700 font-black rounded-full text-sm">안정</span>;
};


export const SuperAdminPage = () => {
    // Dynamic Mock Data (Simulating Live Updates)
    const [lowStockCount, setLowStockCount] = useState(3);
    const [pendingOrdersCount, setPendingOrdersCount] = useState(12);
    const [activeMembers, setActiveMembers] = useState(48);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [dbStatus] = useState("우수"); // Keeping for UI completeness, ignoring lint

    const [pendingOrders, setPendingOrders] = useState([
        { id: 101, branch: "강남본점", item: "치즈토핑 (2kg)", qty: 5, status: "PENDING" },
        { id: 102, branch: "서초점", item: "프리미엄 도우", qty: 10, status: "PENDING" },
        { id: 103, branch: "역삼점", item: "올리브오일", qty: 2, status: "PENDING" },
    ]);

    const [inventoryItems, setInventoryItems] = useState([
        { id: "M-001", name: "모짜렐라 치즈", stock: 120, optimal: 500, status: "LOW" },
        { id: "M-002", name: "토마토 소스", stock: 850, optimal: 800, status: "GOOD" },
        { id: "M-003", name: "피클", stock: 2000, optimal: 1000, status: "OVER" },
        { id: "M-004", name: "페퍼로니", stock: 50, optimal: 300, status: "LOW" },
    ]);

    // Using unused variables to avoid build error (or implementing display)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [purchaseOrders] = useState([
        { id: "PO-3001", item: "밀가루 (20kg)", qty: 50, status: "APPROVED" },
        { id: "PO-3002", item: "콜라 시럽", qty: 10, status: "APPROVED" },
    ]);
    
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [deliveries] = useState([
        { dest: "송파점", item: "치킨박스", driver: "김철수", status: "DELIVERED" },
        { dest: "잠실점", item: "양념소스", driver: "이영희", status: "IN_TRANSIT" },
    ]);

    // Effect: Simulate Live Data Updates
    useEffect(() => {
        const interval = setInterval(() => {
            // Randomly update KPI numbers
            setPendingOrdersCount(prev => prev + (Math.random() > 0.7 ? 1 : 0));
            setLowStockCount(prev => Math.max(0, prev + (Math.random() > 0.8 ? (Math.random() > 0.5 ? 1 : -1) : 0)));
            setActiveMembers(48 + Math.floor(Math.random() * 2)); // 48 or 49

            // Randomly update stock
            setInventoryItems(prev => prev.map(item => {
                if (Math.random() > 0.7) {
                    const change = Math.floor(Math.random() * 5) - 2; // -2 to +2
                    const newStock = Math.max(0, item.stock + change);
                    let newStatus = item.status;
                    if (newStock < item.optimal * 0.3) newStatus = "LOW";
                    else if (newStock > item.optimal * 1.5) newStatus = "OVER";
                    else newStatus = "GOOD";
                    
                    return { ...item, stock: newStock, status: newStatus };
                }
                return item;
            }));

            // Occasionally add a new order
            if (Math.random() > 0.95) {
                const newId = Math.floor(Math.random() * 1000) + 200;
                setPendingOrders(prev => [
                    { id: newId, branch: "신규지점", item: "추가주문", qty: Math.floor(Math.random() * 10) + 1, status: "PENDING" },
                    ...prev.slice(0, 4) // Keep list short
                ]);
            }

        }, 3000); // Update every 3 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen py-5 px-6 max-w-[1920px] mx-auto bg-slate-50 text-slate-800">
            {/* Top Bar */}
            <div className="flex flex-col md:flex-row justify-between items-center mb-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm gap-4">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-4 px-4 py-2 bg-slate-900 text-white rounded-xl shadow-lg">
                        <span className="text-xl">🛡️</span>
                        <div>
                            <div className="text-sm text-slate-400 font-bold uppercase leading-none mb-1">시스템 권한</div>
                            <div className="text-lg font-black tracking-tight">최고 권한 (총괄 관리)</div>
                        </div>
                    </div>
                    
                    {/* DB Status */}
                    <div className="flex items-center gap-4 px-5 py-2 bg-emerald-50 border border-emerald-100 rounded-xl hidden sm:flex">
                        <div className="relative flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                        </div>
                        <div>
                            <div className="text-sm text-emerald-600 font-bold leading-none mb-1">Oracle DB 가동 상태</div>
                            <div className="text-base font-black text-emerald-700">실시간 정상 연결 (가동 중)</div>
                        </div>
                    </div>
                </div>
                
                <div className="flex items-center gap-6 select-none">
                    <div className="px-6 border-r border-slate-100 text-right hidden sm:block">
                        <div className="text-sm text-slate-400 font-bold uppercase mb-1">현재 접속 계정</div>
                        <div className="text-lg font-black text-blue-600">마스터 관리자</div>
                    </div>
                    <button className="flex items-center gap-3 px-5 py-3 bg-red-50 text-red-500 rounded-xl hover:bg-red-500 hover:text-white transition-all shadow-sm group">
                        <span className="font-bold text-base">로그아웃</span>
                        <i className="fa-solid fa-power-off text-xl"></i>
                    </button>
                </div>
            </div>

            {/* Header */}
            <section className="animate-fade-in mb-5">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-5 border-b border-gray-200 pb-6 mb-5 mt-5">
                    <div>
                        <h1 className="text-3xl font-black text-slate-900 flex items-center gap-4">
                            <span className="p-4 bg-blue-600 rounded-2xl text-white shadow-lg">📡</span>
                            SCM 통합 관제 시스템
                        </h1>
                        <p className="text-slate-400 mt-4 text-xl font-medium">전체 가맹점 물류 흐름 및 재고 현황 실시간 감시 (Live Demo)</p>
                    </div>
                     <div className="flex gap-4">
                        <div className="bg-white px-6 py-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
                            <div className="w-10 h-10 flex items-center justify-center bg-blue-50 text-blue-600 rounded-full">
                                <i className="fa-solid fa-sync fa-spin"></i>
                            </div>
                            <div>
                                <div className="text-sm text-slate-400 font-bold leading-none mb-1">데이터 동기화</div>
                                <div className="text-base font-black text-slate-700">실시간 수신 중...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* KPIs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                <KpiCard title="재고 부족 품목 통합" value={lowStockCount} unit="품목" color="red" icon="fa-triangle-exclamation" />
                <KpiCard title="전체 미처리 수주" value={pendingOrdersCount} unit="주문" color="blue" icon="fa-clock-rotate-left" />
                <KpiCard title="총 활성 가맹점" value={activeMembers} unit="지점" color="indigo" icon="fa-city" />
                <KpiCard title="Oracle DB 연동 품질" value={dbStatus} unit="동기화" color="emerald" icon="fa-database" />
            </div>

            {/* 1. Incoming Flow */}
            <section className="mb-8">
                <SectionTitle icon="fa-arrow-right-to-bracket" title="유입 물류 관리" color="text-blue-600" />
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    {/* Orders Table */}
                    <CardContainer color="blue" title="가맹점 수주 관리" icon="fa-file-invoice-dollar" table="PLATFORM_UI_ORDER">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-slate-50 border-b-2 border-slate-100">
                                <tr>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">주문처</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">품목</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm text-center">수량</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm text-center">상태</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pendingOrders.map((order) => (
                                    <tr key={order.id} className="border-b border-slate-50 hover:bg-blue-50/50 transition">
                                        <td className="p-4 font-black text-slate-800">{order.branch}</td>
                                        <td className="p-4 text-slate-600">{order.item}</td>
                                        <td className="p-4 text-center font-bold">{order.qty}개</td>
                                        <td className="p-4 text-center">
                                            <div className="flex items-center justify-center gap-2">
                                                <span className="px-3 py-1 bg-amber-100 text-amber-700 font-black rounded-full text-sm">접수대기</span>
                                                <button className="bg-blue-600 text-white px-3 py-1 rounded-lg font-bold hover:bg-blue-700 text-sm shadow-sm group-hover:scale-105 transition-transform">승인</button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </CardContainer>

                    {/* Stock Table */}
                    <CardContainer color="emerald" title="재고 현황" icon="fa-warehouse" table="PLATFORM_UI_INVENTORY">
                         <table className="w-full text-left border-collapse">
                            <thead className="bg-slate-50 border-b-2 border-slate-100">
                                <tr>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">자재명</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm text-center">현재고</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm text-center">상태</th>
                                </tr>
                            </thead>
                            <tbody>
                                {inventoryItems.map((item) => (
                                    <tr key={item.id} className="border-b border-slate-50 hover:bg-emerald-50/30 transition">
                                        <td className="p-4">
                                            <div className="font-black text-slate-800">{item.name}</div>
                                            <div className="text-xs text-slate-400">{item.id}</div>
                                        </td>
                                        <td className="p-4 text-center font-bold bg-slate-100 rounded-lg">{item.stock.toLocaleString()}</td>
                                        <td className="p-4 text-center">
                                            <StatusBadge status={item.status} />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </CardContainer>
                </div>
            </section>
             
            
             {/* 2. Outgoing Flow  (Using the unused variables now to satisfy functionality requests) */}
            <section className="mb-10">
                <SectionTitle icon="fa-arrow-right-from-bracket" title="유출 물류 관리 (Mock)" color="text-rose-600" />
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    {/* Delivery */}
                    <CardContainer color="rose" title="배송 현황" icon="fa-truck-fast" table="PLATFORM_UI_DELIVERY">
                        <table className="w-full text-left border-collapse">
                             <thead className="bg-slate-50 border-b-2 border-slate-100">
                                <tr>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">도착지점</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">품목</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm text-center">기사님</th>
                                </tr>
                            </thead>
                            <tbody>
                                {deliveries.map((d, i) => (
                                    <tr key={i} className="border-b border-slate-50 hover:bg-rose-50/50 transition">
                                        <td className="p-4 font-black text-slate-800">{d.dest}</td>
                                        <td className="p-4 text-slate-600">{d.item}</td>
                                        <td className="p-4 text-center font-bold text-slate-700">{d.driver}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </CardContainer>
                    
                    {/* Purchase Order */}
                     <CardContainer color="amber" title="발주 관리" icon="fa-cart-shopping" table="PLATFORM_UI_PURCHASE">
                        <table className="w-full text-left border-collapse">
                             <thead className="bg-slate-50 border-b-2 border-slate-100">
                                <tr>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">발주번호</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm">품목</th>
                                    <th className="p-4 text-slate-500 font-bold uppercase text-sm text-center">상태</th>
                                </tr>
                            </thead>
                            <tbody>
                                {purchaseOrders.map((p, i) => (
                                    <tr key={i} className="border-b border-slate-50 hover:bg-amber-50/50 transition">
                                        <td className="p-4 font-black text-slate-800">{p.id}</td>
                                        <td className="p-4 text-slate-600">{p.item} ({p.qty}ea)</td>
                                        <td className="p-4 text-center font-bold text-emerald-600">{p.status}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </CardContainer>
                </div>
            </section>
        </div>
    );
};
