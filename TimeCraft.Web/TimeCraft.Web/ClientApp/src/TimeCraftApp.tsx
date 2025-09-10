import React from 'react';
import './utils/chartSetup';
import { useTimeCraft } from './hooks/useTimeCraft';
import { Header } from './components/Header';
import { InputForm } from './components/InputForm';
import { ErrorDisplay } from './components/ErrorDisplay';
import { TagsDisplay } from './components/TagsDisplay';

export const TimeCraftApp: React.FC = () => {
  const {
    description,
    setDescription,
    dataLength,
    setDataLength,
    isLoading,
    tags,
    tagProgress,
    error,
    generateTimeSeries,
    clearAll,
    retryTag,
    updateTagTimeSeriesData
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
          onClearAll={clearAll}
          hasExistingData={tags.length > 0}
        />

        <ErrorDisplay error={error} />
        
        <TagsDisplay 
          tags={tags} 
          tagProgress={tagProgress} 
          dataLength={dataLength}
          onRetryTag={retryTag}
          onUpdateTagData={updateTagTimeSeriesData}
        />
      </div>
    </div>
  );
};

export default TimeCraftApp;
