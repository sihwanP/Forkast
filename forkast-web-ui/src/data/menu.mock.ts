export interface MenuData {
  id: string;
  name: string;
  price: number;
  category: string;
  salesCount: number;
  revenue: number;
  trend: 'up' | 'down' | 'flat';
}

export const MENU_PERFORMANCE: MenuData[] = [
  { id: '1', name: '후라이드 치킨', price: 18000, category: '치킨', salesCount: 145, revenue: 2610000, trend: 'up' },
  { id: '2', name: '양념 치킨', price: 19000, category: '치킨', salesCount: 112, revenue: 2128000, trend: 'flat' },
  { id: '3', name: '간장 치킨', price: 19000, category: '치킨', salesCount: 89, revenue: 1691000, trend: 'up' },
  { id: '4', name: '치즈볼', price: 5000, category: '사이드', salesCount: 210, revenue: 1050000, trend: 'up' },
  { id: '5', name: '감자튀김', price: 4000, category: '사이드', salesCount: 45, revenue: 180000, trend: 'down' },
  { id: '6', name: '콜라 1.25L', price: 2000, category: '음료', salesCount: 150, revenue: 300000, trend: 'flat' },
  { id: '7', name: '마늘 치킨', price: 20000, category: '치킨', salesCount: 23, revenue: 460000, trend: 'down' },
];
