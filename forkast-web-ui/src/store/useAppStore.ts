import { create } from 'zustand';

interface UserSettings {
  goalRevenue: number;
  openTime: string;
  closeTime: string;
}

interface Alert {
  id: string;
  type: 'danger' | 'warn' | 'info';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
  link?: string;
}

interface AppState {
  isAuth: boolean;
  userSettings: UserSettings;
  alerts: Alert[];
  
  login: () => void;
  logout: () => void;
  updateSettings: (settings: Partial<UserSettings>) => void;
  markAlertRead: (id: string) => void;
  markAllAlertsRead: () => void;
  addAlert: (alert: Omit<Alert, 'id' | 'read' | 'createdAt'>) => void;
}

export const useAppStore = create<AppState>((set) => ({
  isAuth: true, // Default to true for dev ease, usually false
  
  userSettings: {
    goalRevenue: 30000000,
    openTime: '09:00',
    closeTime: '22:00',
  },
  
  alerts: [
    {
      id: '1',
      type: 'danger',
      title: '오늘 매출 급감',
      message: '현재 매출이 목표 대비 15% 부족합니다. 프로모션을 고려하세요.',
      read: false,
      createdAt: new Date().toISOString(),
      link: '/analytics'
    },
    {
      id: '2',
      type: 'warn',
      title: '재고 소진 임박',
      message: '\'치즈볼\' 재고가 5개 남았습니다.',
      read: false,
      createdAt: new Date().toISOString(),
      link: '/menu-performance'
    },
    {
      id: '3',
      type: 'info',
      title: '비 오는 날 마케팅',
      message: '내일 비 예보가 있습니다. 배달 팁 할인을 설정해보세요.',
      read: true,
      createdAt: new Date().toISOString(),
      link: '/forecast'
    }
  ],

  login: () => set({ isAuth: true }),
  logout: () => set({ isAuth: false }),
  
  updateSettings: (newSettings) => set((state) => ({
    userSettings: { ...state.userSettings, ...newSettings }
  })),
  
  markAlertRead: (id) => set((state) => ({
    alerts: state.alerts.map(a => a.id === id ? { ...a, read: true } : a)
  })),

  markAllAlertsRead: () => set((state) => ({
    alerts: state.alerts.map(a => ({ ...a, read: true }))
  })),
  
  addAlert: (alert) => set((state) => ({
    alerts: [
      {
        ...alert,
        id: Math.random().toString(36).substr(2, 9),
        read: false,
        createdAt: new Date().toISOString()
      },
      ...state.alerts
    ]
  }))
}));
