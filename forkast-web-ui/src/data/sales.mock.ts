export interface DailySales {
  date: string;
  revenue: number;
  orders: number;
}

export const SALES_DATA_7_DAYS: DailySales[] = [
  { date: '2023-10-25', revenue: 1250000, orders: 45 },
  { date: '2023-10-26', revenue: 980000, orders: 38 },
  { date: '2023-10-27', revenue: 1450000, orders: 52 },
  { date: '2023-10-28', revenue: 1890000, orders: 75 },
  { date: '2023-10-29', revenue: 2100000, orders: 82 },
  { date: '2023-10-30', revenue: 850000, orders: 32 },
  { date: '2023-10-31', revenue: 1150000, orders: 41 },
];

export const HOURLY_SALES_TODAY = [
  { hour: '11:00', sales: 0 },
  { hour: '12:00', sales: 120000 },
  { hour: '13:00', sales: 250000 },
  { hour: '14:00', sales: 80000 },
  { hour: '15:00', sales: 45000 },
  { hour: '16:00', sales: 150000 },
  { hour: '17:00', sales: 320000 },
  { hour: '18:00', sales: 480000 },
  { hour: '19:00', sales: 650000 },
  { hour: '20:00', sales: 520000 },
  { hour: '21:00', sales: 280000 },
  { hour: '22:00', sales: 120000 },
];
