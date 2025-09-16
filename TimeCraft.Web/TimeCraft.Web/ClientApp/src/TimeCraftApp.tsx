import React, { useState } from 'react';
import './utils/chartSetup';
import { useTimeCraft } from './hooks/useTimeCraft';
import { Header } from './components/Header';
import { InputForm } from './components/InputForm';
import { ErrorDisplay } from './components/ErrorDisplay';
import { TagsDisplay } from './components/TagsDisplay';
import { PublishedDatasets } from './components/PublishedDatasets';

type AppView = 'main' | 'published';

export const TimeCraftApp: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>('main');
  
  const {
    description,
    setDescription,
    timeHorizon,
    setTimeHorizon,
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
        
        {/* Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setCurrentView('main')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                currentView === 'main'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              Generate Time Series
            </button>
            <button
              onClick={() => setCurrentView('published')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                currentView === 'published'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              Published Datasets
            </button>
          </nav>
        </div>

        {/* Main View */}
        {currentView === 'main' && (
          <>
            <InputForm
              description={description}
              setDescription={setDescription}
              timeHorizon={timeHorizon}
              setTimeHorizon={setTimeHorizon}
              isLoading={isLoading}
              onGenerate={generateTimeSeries}
              onClearAll={clearAll}
              hasExistingData={tags.length > 0}
            />

            <ErrorDisplay error={error} />
            
            <TagsDisplay 
              tags={tags} 
              tagProgress={tagProgress} 
              timeHorizon={timeHorizon}
              onRetryTag={retryTag}
              onUpdateTagData={updateTagTimeSeriesData}
            />
          </>
        )}

        {/* Published Datasets View */}
        {currentView === 'published' && <PublishedDatasets />}
      </div>
    </div>
  );
};

export default TimeCraftApp;
