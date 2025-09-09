import React from 'react';
import { Line } from 'react-chartjs-2';
import type { TimeSeriesData } from '../types/api';

interface TimeSeriesChartProps {
  timeSeriesData: TimeSeriesData[];
  dataLength: number;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ 
  timeSeriesData, 
  dataLength 
}) => {
  const chartData = {
    labels: timeSeriesData[0]?.timestamps || Array.from({ length: dataLength }, (_, i) => i.toString()),
    datasets: timeSeriesData.map((series, index) => ({
      label: series.name,
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
        text: 'Time Series Overview - All Sensors',
      },
    },
    scales: {
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
