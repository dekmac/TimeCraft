import React from 'react';
import { Line } from 'react-chartjs-2';
import type { InjectionPoint, AnomalyInfo } from '../types/api';

interface MiniTimeSeriesChartProps {
  data: number[];
  tagName: string;
  dataLength: number;
  selectedInjectionPoint?: InjectionPoint;
  anomalies?: AnomalyInfo[];
  onPointClick?: (index: number) => void;
  isInteractive?: boolean;
}

export const MiniTimeSeriesChart: React.FC<MiniTimeSeriesChartProps> = ({ 
  data, 
  tagName, 
  dataLength,
  selectedInjectionPoint,
  anomalies = [],
  onPointClick,
  isInteractive = false
}) => {
  const chartData = {
    labels: Array.from({ length: dataLength }, (_, i) => i.toString()),
    datasets: [{
      label: tagName,
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
        display: false,
      },
      tooltip: {
        enabled: isInteractive,
      }
    },
    scales: {
      x: {
        display: false,
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
      <div className="h-20 bg-gray-100 rounded flex items-center justify-center">
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
      className={`h-20 w-full ${isInteractive ? 'cursor-pointer' : ''}`}
      onClick={handleChartClick}
      title={isInteractive ? 'Click to select injection point' : ''}
    >
      <Line data={chartData} options={chartOptions} />
    </div>
  );
};
