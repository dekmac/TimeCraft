export interface TimeHorizonConfig {
  period: number;
  unit: 'minutes' | 'hours' | 'days' | 'weeks';
  granularity: 'minute' | 'hour' | 'day';
  label: string;
}

export interface TimeHorizonOption {
  id: string;
  label: string;
  config: TimeHorizonConfig;
  totalPoints: number;
  batchCount: number;
}

export const TIME_HORIZON_OPTIONS: TimeHorizonOption[] = [
  {
    id: '1hour_1min',
    label: '1 Hour (per minute)',
    config: { period: 1, unit: 'hours', granularity: 'minute', label: '1 Hour - Minute Intervals' },
    totalPoints: 60,
    batchCount: 1
  },
  {
    id: '6hours_5min',
    label: '6 Hours (per 5 minutes)',
    config: { period: 6, unit: 'hours', granularity: 'minute', label: '6 Hours - 5 Minute Intervals' },
    totalPoints: 72,
    batchCount: 1
  },
  {
    id: '24hours_5min',
    label: '24 Hours (per 5 minutes)',
    config: { period: 24, unit: 'hours', granularity: 'minute', label: '24 Hours - 5 Minute Intervals' },
    totalPoints: 288, // 24 hours * 12 (5-minute intervals per hour)
    batchCount: 1
  },
  {
    id: '48hours_1hour',
    label: '48 Hours (per hour)',
    config: { period: 48, unit: 'hours', granularity: 'hour', label: '48 Hours - Hourly' },
    totalPoints: 48,
    batchCount: 1
  },
  {
    id: '7days_1hour',
    label: '7 Days (per hour)',
    config: { period: 7, unit: 'days', granularity: 'hour', label: '7 Days - Hourly' },
    totalPoints: 168,
    batchCount: 1
  },
  {
    id: '7days_6hours',
    label: '7 Days (per 6 hours)',
    config: { period: 7, unit: 'days', granularity: 'hour', label: '7 Days - 6 Hour Intervals' },
    totalPoints: 28,
    batchCount: 1
  },
  {
    id: '30days_1day',
    label: '30 Days (per day)', 
    config: { period: 30, unit: 'days', granularity: 'day', label: '30 Days - Daily' },
    totalPoints: 30,
    batchCount: 1
  },
  {
    id: '30days_3hours',
    label: '30 Days (per 3 hours)',
    config: { period: 30, unit: 'days', granularity: 'hour', label: '30 Days - 3 Hour Intervals' },
    totalPoints: 240, // 30 days * 8 (3-hour intervals per day)
    batchCount: 1
  },
  {
    id: '90days_1day',
    label: '90 Days (per day)',
    config: { period: 90, unit: 'days', granularity: 'day', label: '90 Days - Daily' },
    totalPoints: 90,
    batchCount: 1
  },
  {
    id: '365days_1day',
    label: '1 Year (per day)',
    config: { period: 365, unit: 'days', granularity: 'day', label: '1 Year - Daily' },
    totalPoints: 365,
    batchCount: 1
  },
  {
    id: '365days_1hour',
    label: '1 Year (per hour) - Large Dataset',
    config: { period: 365, unit: 'days', granularity: 'hour', label: '1 Year - Hourly' },
    totalPoints: 8760,
    batchCount: 18 // 500 point batches
  }
];

export const getTimeHorizonById = (id: string): TimeHorizonOption | undefined => {
  return TIME_HORIZON_OPTIONS.find(option => option.id === id);
};

export const formatTimeHorizonLabel = (config: TimeHorizonConfig): string => {
  return config.label;
};

export const calculateTotalPoints = (config: TimeHorizonConfig): number => {
  const { period, unit, granularity } = config;
  
  // Special cases for specific configurations
  if (period === 24 && unit === 'hours' && granularity === 'minute') {
    // 24 hours with 5-minute intervals
    return 288; // 24 * 12 (5-minute intervals per hour)
  }
  
  if (period === 30 && unit === 'days' && granularity === 'hour') {
    // 30 days with 3-hour intervals  
    return 240; // 30 * 8 (3-hour intervals per day)
  }
  
  // Default calculation for other configurations
  let totalMinutes = 0;
  switch (unit) {
    case 'minutes':
      totalMinutes = period;
      break;
    case 'hours':
      totalMinutes = period * 60;
      break;
    case 'days':
      totalMinutes = period * 24 * 60;
      break;
    case 'weeks':
      totalMinutes = period * 7 * 24 * 60;
      break;
  }
  
  let intervalMinutes = 1;
  switch (granularity) {
    case 'minute':
      intervalMinutes = 1;
      break;
    case 'hour':
      intervalMinutes = 60;
      break;
    case 'day':
      intervalMinutes = 24 * 60;
      break;
  }
  
  return Math.ceil(totalMinutes / intervalMinutes);
};

export const generateTimestamps = (config: TimeHorizonConfig, startDate?: Date): string[] => {
  const start = startDate || new Date();
  const timestamps: string[] = [];
  const totalPoints = calculateTotalPoints(config);
  
  let intervalMs = 0;
  
  // Special cases for specific configurations
  if (config.period === 24 && config.unit === 'hours' && config.granularity === 'minute') {
    // 24 hours with 5-minute intervals
    intervalMs = 5 * 60 * 1000;
  } else if (config.period === 30 && config.unit === 'days' && config.granularity === 'hour') {
    // 30 days with 3-hour intervals
    intervalMs = 3 * 60 * 60 * 1000;
  } else {
    // Default intervals
    switch (config.granularity) {
      case 'minute':
        intervalMs = 60 * 1000;
        break;
      case 'hour':
        intervalMs = 60 * 60 * 1000;
        break;
      case 'day':
        intervalMs = 24 * 60 * 60 * 1000;
        break;
    }
  }
  
  for (let i = 0; i < totalPoints; i++) {
    const timestamp = new Date(start.getTime() + (i * intervalMs));
    timestamps.push(timestamp.toISOString());
  }
  
  return timestamps;
};