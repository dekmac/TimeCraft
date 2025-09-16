import React from 'react';
import { Line } from 'react-chartjs-2';
import type { TimeSeriesData } from '../types/api';
import type { TimeHorizonOption } from '../types/timeHorizon';

interface TimeSeriesChartProps {
  timeSeriesData: TimeSeriesData[];
  timeHorizon: TimeHorizonOption;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ 
  timeSeriesData, 
  timeHorizon 
}) => {
  // Generate proper time-based labels that correspond to actual time periods
  const getTimeLabels = (dataLength: number) => {
    const now = new Date();
    
    // Determine the interval between data points based on time horizon
    let intervalMs: number;
    let formatTime: (date: Date) => string;
    
    // Use timeHorizon.id to determine the specific time configuration
    if (timeHorizon.id === '24hours_5min') {
      // 24 hours, 288 points = 5-minute intervals
      intervalMs = 5 * 60 * 1000; // 5 minutes in milliseconds
      formatTime = (date: Date) => date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    } else if (timeHorizon.id === '7days_1hour') {
      // 7 days, 168 points = hourly intervals
      intervalMs = 60 * 60 * 1000; // 1 hour in milliseconds
      formatTime = (date: Date) => {
        const day = date.toLocaleDateString('en-US', { weekday: 'short' });
        const time = date.toLocaleTimeString('en-US', { 
          hour: '2-digit',
          hour12: false 
        });
        return `${day} ${time}:00`;
      };
    } else if (timeHorizon.id === '30days_3hour') {
      // 30 days, 240 points = 3-hour intervals
      intervalMs = 3 * 60 * 60 * 1000; // 3 hours in milliseconds
      formatTime = (date: Date) => {
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const time = date.toLocaleTimeString('en-US', { 
          hour: '2-digit',
          hour12: false 
        });
        return `${month}/${day} ${time}:00`;
      };
    } else if (timeHorizon.config.granularity === 'minute') {
      // For minute-based intervals
      const minuteInterval = timeHorizon.config.period * 60 / dataLength;
      intervalMs = minuteInterval * 60 * 1000;
      formatTime = (date: Date) => date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    } else if (timeHorizon.config.granularity === 'hour') {
      // For hour-based intervals
      const hourInterval = timeHorizon.config.period / dataLength;
      if (timeHorizon.config.unit === 'days') {
        intervalMs = hourInterval * 24 * 60 * 60 * 1000;
      } else {
        intervalMs = hourInterval * 60 * 60 * 1000;
      }
      formatTime = (date: Date) => {
        if (timeHorizon.config.unit === 'days') {
          const day = date.toLocaleDateString('en-US', { weekday: 'short' });
          const time = date.toLocaleTimeString('en-US', { 
            hour: '2-digit',
            hour12: false 
          });
          return `${day} ${time}:00`;
        } else {
          return date.toLocaleTimeString('en-US', { 
            hour: '2-digit',
            hour12: false 
          });
        }
      };
    } else {
      // Fallback for other time horizons
      intervalMs = 60 * 60 * 1000; // 1 hour default
      formatTime = (date: Date) => date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    }
    
    // Calculate start time (going backwards from now)
    const totalTimeMs = (dataLength - 1) * intervalMs;
    const startTime = new Date(now.getTime() - totalTimeMs);
    
    // For display purposes, show only every nth label to avoid crowding
    const maxLabels = 10;
    const labelEvery = Math.max(1, Math.ceil(dataLength / maxLabels));
    
    return Array.from({ length: dataLength }, (_, i) => {
      const timestamp = new Date(startTime.getTime() + (i * intervalMs));
      
      // Only show labels at regular intervals or for first/last points
      if (i % labelEvery === 0 || i === 0 || i === dataLength - 1) {
        return formatTime(timestamp);
      }
      return '';
    });
  };

  const chartData = {
    labels: timeSeriesData[0]?.timestamps || (timeSeriesData[0] ? getTimeLabels(timeSeriesData[0].data.length) : []),
    datasets: timeSeriesData.map((series, index) => ({
      label: `${series.name} (${timeHorizon.config.label})`,
      data: series.data,
      borderColor: `hsl(${index * 360 / timeSeriesData.length}, 70%, 50%)`,
      backgroundColor: `hsla(${index * 360 / timeSeriesData.length}, 70%, 50%, 0.2)`,
      tension: 0.4
    }))
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Time Series Overview - ${timeHorizon.config.label}`,
        font: {
          size: 16
        }
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: `Time Horizon: ${timeHorizon.config.label}`,
          font: {
            size: 12,
            weight: 'bold' as const
          },
          color: '#666'
        }
      },
      y: {
        beginAtZero: false,
      },
    },
  };

  return (
    <div className="chart-container">
      <Line data={chartData} options={chartOptions} />
    </div>
  );
};
