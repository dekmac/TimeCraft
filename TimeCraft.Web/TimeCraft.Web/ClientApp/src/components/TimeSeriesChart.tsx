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
        text: 'Generated Time Series Data',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  return (
    <div className="glass-effect p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Generated Time Series</h3>
      <div className="chart-container">
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};
