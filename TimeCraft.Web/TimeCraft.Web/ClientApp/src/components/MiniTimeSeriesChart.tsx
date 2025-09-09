import React from 'react';
import { Line } from 'react-chartjs-2';

interface MiniTimeSeriesChartProps {
  data: number[];
  tagName: string;
  dataLength: number;
}

export const MiniTimeSeriesChart: React.FC<MiniTimeSeriesChartProps> = ({ 
  data, 
  tagName, 
  dataLength 
}) => {
  const chartData = {
    labels: Array.from({ length: dataLength }, (_, i) => i.toString()),
    datasets: [{
      label: tagName,
      data: data,
      borderColor: 'rgb(59, 130, 246)', // blue-500
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 3,
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

  return (
    <div className="h-20 w-full">
      <Line data={chartData} options={chartOptions} />
    </div>
  );
};
