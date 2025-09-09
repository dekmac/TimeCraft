import React from 'react';
import './utils/chartSetup';
import { useTimeCraft } from './hooks/useTimeCraft';
import { Header } from './components/Header';
import { InputForm } from './components/InputForm';
import { ErrorDisplay } from './components/ErrorDisplay';
import { TagsDisplay } from './components/TagsDisplay';
import { TimeSeriesChart } from './components/TimeSeriesChart';

const TimeCraftApp: React.FC = () => {
  const {
    description,
    setDescription,
    dataLength,
    setDataLength,
    isLoading,
    tags,
    timeSeriesData,
    error,
    generateTimeSeries
  } = useTimeCraft();

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-6xl mx-auto">
        <Header />
        
        <InputForm
          description={description}
          setDescription={setDescription}
          dataLength={dataLength}
          setDataLength={setDataLength}
          isLoading={isLoading}
          onGenerate={generateTimeSeries}
        />

        <ErrorDisplay error={error} />
        
        <TagsDisplay tags={tags} />

        {timeSeriesData.length > 0 && (
          <TimeSeriesChart timeSeriesData={timeSeriesData} dataLength={dataLength} />
        )}
      </div>
    </div>
  );
};

export default TimeCraftApp;
