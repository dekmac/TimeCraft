import React from 'react';
import { Line } from 'react-chartjs-2';
import type { InjectionPoint, AnomalyInfo } from '../types/api';
import type { TimeHorizonOption } from '../types/timeHorizon';

interface MiniTimeSeriesChartProps {
  data: number[];
  tagName: string;
  timeHorizon: TimeHorizonOption;
  selectedInjectionPoint?: InjectionPoint;
  anomalies?: AnomalyInfo[];
  onPointClick?: (index: number) => void;
  isInteractive?: boolean;
}

export const MiniTimeSeriesChart: React.FC<MiniTimeSeriesChartProps> = ({ 
  data, 
  tagName, 
  timeHorizon,
  selectedInjectionPoint,
  anomalies = [],
  onPointClick,
  isInteractive = false
}) => {
  // Generate proper time-based labels that correspond to actual time periods
  const getTimeLabels = () => {
    const totalPoints = data.length;
    
    // For daily patterns, start at midnight (00:00) of today for realistic time alignment
    // This ensures temperature peaks at afternoon, occupancy patterns align correctly, etc.
    let startTime: Date;
    if (timeHorizon.config.unit === 'hours' && timeHorizon.config.period === 24) {
      // For 24-hour daily patterns, start at midnight
      const now = new Date();
      startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
    } else if (timeHorizon.config.unit === 'days' && timeHorizon.config.period <= 7) {
      // For weekly patterns, start at midnight
      const now = new Date();
      startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
    } else {
      // For longer periods, use current time (but still calculate backwards)
      startTime = new Date();
    }
    
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
        return day;
      };
    } else if (timeHorizon.id === '30days_3hour') {
      // 30 days, 240 points = 3-hour intervals
      intervalMs = 3 * 60 * 60 * 1000; // 3 hours in milliseconds
      formatTime = (date: Date) => {
        const day = date.getDate();
        const month = date.getMonth() + 1;
        return `${month}/${day}`;
      };
    } else if (timeHorizon.config.granularity === 'minute') {
      // For minute-based intervals
      const minuteInterval = timeHorizon.config.period * 60 / totalPoints;
      intervalMs = minuteInterval * 60 * 1000;
      formatTime = (date: Date) => date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    } else {
      // For hour-based intervals
      const hourInterval = timeHorizon.config.period / totalPoints;
      if (timeHorizon.config.unit === 'days') {
        intervalMs = hourInterval * 24 * 60 * 60 * 1000;
        formatTime = (date: Date) => date.toLocaleDateString('en-US', { weekday: 'short' });
      } else {
        intervalMs = hourInterval * 60 * 60 * 1000;
        formatTime = (date: Date) => date.toLocaleTimeString('en-US', { 
          hour: '2-digit',
          hour12: false 
        });
      }
    }
    
    // Calculate actual start time (forward from midnight for daily patterns)
    // For daily patterns (24 hours or ≤7 days), startTime is already set to midnight
    // For longer periods, we calculate backwards from current time
    if (timeHorizon.config.unit !== 'hours' || timeHorizon.config.period !== 24) {
      if (timeHorizon.config.unit !== 'days' || timeHorizon.config.period > 7) {
        // For longer periods, calculate backwards from current time
        const totalTimeMs = (totalPoints - 1) * intervalMs;
        startTime = new Date(startTime.getTime() - totalTimeMs);
      }
    }
    
    // For mini charts, show fewer labels to avoid crowding
    const maxLabels = 5;
    const labelEvery = Math.max(1, Math.ceil(totalPoints / maxLabels));
    
    return Array.from({ length: totalPoints }, (_, i) => {
      const timestamp = new Date(startTime.getTime() + (i * intervalMs));
      
      // Only show labels at regular intervals or for first/last points
      if (i % labelEvery === 0 || i === 0 || i === totalPoints - 1) {
        return formatTime(timestamp);
      }
      return '';
    });
  };

  const chartData = {
    labels: getTimeLabels(),
    datasets: [{
      label: `${tagName} (${timeHorizon.config.label})`,
      data: data,
      borderColor: selectedInjectionPoint ? 'rgb(34, 197, 94)' : 'rgb(59, 130, 246)', // green if point selected, blue otherwise
      backgroundColor: selectedInjectionPoint ? 'rgba(34, 197, 94, 0.1)' : 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      pointRadius: selectedInjectionPoint ? data.map((_, i) => i === selectedInjectionPoint.index ? 4 : 0) : 0,
      pointHoverRadius: isInteractive ? 4 : 3,
      pointBackgroundColor: selectedInjectionPoint ? data.map((_, i) => i === selectedInjectionPoint.index ? 'rgb(34, 197, 94)' : 'transparent') : 'transparent',
      pointBorderColor: selectedInjectionPoint ? data.map((_, i) => i === selectedInjectionPoint.index ? 'rgb(34, 197, 94)' : 'transparent') : 'transparent',
      borderWidth: 1.5,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: `${tagName} - ${timeHorizon.config.label}`,
        font: {
          size: 12
        },
        padding: {
          bottom: 10
        }
      },
      tooltip: {
        enabled: isInteractive,
        callbacks: {
          title: (context: any) => {
            const index = context[0]?.dataIndex;
            if (index !== undefined) {
              // Calculate actual timestamp for tooltip
              const totalPoints = data.length;
              
              // Use same midnight logic as the main chart
              let startTime: Date;
              if (timeHorizon.config.unit === 'hours' && timeHorizon.config.period === 24) {
                // For 24-hour daily patterns, start at midnight
                const now = new Date();
                startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
              } else if (timeHorizon.config.unit === 'days' && timeHorizon.config.period <= 7) {
                // For weekly patterns, start at midnight
                const now = new Date();
                startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
              } else {
                // For longer periods, use current time and calculate backwards
                startTime = new Date();
              }
              
              let intervalMs: number;
              if (timeHorizon.id === '24hours_5min') {
                intervalMs = 5 * 60 * 1000;
              } else if (timeHorizon.id === '7days_1hour') {
                intervalMs = 60 * 60 * 1000;
              } else if (timeHorizon.id === '30days_3hour') {
                intervalMs = 3 * 60 * 60 * 1000;
              } else {
                intervalMs = 60 * 60 * 1000; // default 1 hour
              }
              
              // For longer periods, calculate backwards from current time
              if (timeHorizon.config.unit !== 'hours' || timeHorizon.config.period !== 24) {
                if (timeHorizon.config.unit !== 'days' || timeHorizon.config.period > 7) {
                  const totalTimeMs = (totalPoints - 1) * intervalMs;
                  startTime = new Date(startTime.getTime() - totalTimeMs);
                }
              }
              
              const pointTime = new Date(startTime.getTime() + (index * intervalMs));
              
              return pointTime.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
              });
            }
            return '';
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false,
        },
        ticks: {
          display: false,
        },
        title: {
          display: true,
          text: `Time Horizon: ${timeHorizon.config.label}`,
          font: {
            size: 11,
            weight: 'bold' as const
          },
          color: '#4B5563',
          padding: {
            top: 8
          }
        }
      },
      y: {
        display: false,
        beginAtZero: false,
      },
    },
    elements: {
      point: {
        radius: 0,
      },
    },
    interaction: {
      intersect: false,
    },
  };

  if (!data || data.length === 0) {
    return (
      <div className="h-28 bg-gray-100 rounded flex items-center justify-center">
        <span className="text-xs text-gray-500">No data</span>
      </div>
    );
  }

  const handleChartClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!isInteractive || !onPointClick) return;
    
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const width = rect.width;
    const pointIndex = Math.round((x / width) * (data.length - 1));
    
    if (pointIndex >= 0 && pointIndex < data.length) {
      onPointClick(pointIndex);
    }
  };

  return (
    <div 
      className={`h-28 w-full ${isInteractive ? 'cursor-pointer' : ''}`}
      onClick={handleChartClick}
      title={isInteractive ? 'Click to select injection point' : ''}
    >
      <Line data={chartData} options={chartOptions} />
    </div>
  );
};
