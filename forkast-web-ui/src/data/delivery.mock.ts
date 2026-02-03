export interface DeliveryPlatformData {
  name: string;
  revenue: number; // 순매출
  orders: number;
  feeRate: number; // 수수료율 (%)
  color: string;
}

export const DELIVERY_DATA: DeliveryPlatformData[] = [
  { name: '배달의민족', revenue: 4500000, orders: 180, feeRate: 6.8, color: '#2ac1bc' },
  { name: '쿠팡이츠', revenue: 1200000, orders: 45, feeRate: 9.8, color: '#00aaff' },
  { name: '요기요', revenue: 800000, orders: 32, feeRate: 12.5, color: '#fa0050' },
  { name: '홀/포장', revenue: 3500000, orders: 150, feeRate: 0, color: '#fbbf24' },
];
