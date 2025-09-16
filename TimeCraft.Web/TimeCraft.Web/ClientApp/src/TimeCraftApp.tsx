import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import './utils/chartSetup';
import { useTimeCraft } from './hooks/useTimeCraft';
import { Header } from './components/Header';
import { InputForm } from './components/InputForm';
import { ErrorDisplay } from './components/ErrorDisplay';
import { TagsDisplay } from './components/TagsDisplay';
import { PublishedDatasets } from './components/PublishedDatasets';

type AppView = 'main' | 'published';

interface TimeCraftAppProps {
  defaultView?: AppView;
}

export const TimeCraftApp: React.FC<TimeCraftAppProps> = ({ defaultView = 'main' }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [currentView, setCurrentView] = useState<AppView>(defaultView);
  const lastLoadedDatasetId = useRef<string | null>(null);
  
  const {
    description,
    setDescription,
    timeHorizon,
    setTimeHorizon,
    isLoading,
    loadingDataset,
    tags,
    tagProgress,
    error,
    generateTimeSeries,
    clearAll,
    retryTag,
    updateTagTimeSeriesData,
    loadDataset
  } = useTimeCraft();

  // Handle route changes and dataset loading
  useEffect(() => {
    // Set view based on current path
    if (location.pathname.startsWith('/datasets')) {
      setCurrentView('published');
    } else if (location.pathname === '/generate') {
      setCurrentView('main');
    }
  }, [location.pathname]);

  // Separate effect for dataset loading to prevent infinite loops
  useEffect(() => {
    // Handle query parameters for dataset loading
    const searchParams = new URLSearchParams(location.search);
    const datasetId = searchParams.get('datasetId') || id;
    
    // Only load if we have a dataset ID and it's different from the last loaded one
    if (datasetId && datasetId !== lastLoadedDatasetId.current) {
      console.log('Loading dataset with ID:', datasetId);
      lastLoadedDatasetId.current = datasetId;
      loadDataset(datasetId);
    }
    
    // Clear the last loaded ID if no dataset ID is present
    if (!datasetId) {
      lastLoadedDatasetId.current = null;
    }
  }, [location.pathname, location.search, id, loadDataset]);

  const handleViewChange = (view: AppView) => {
    setCurrentView(view);
    if (view === 'main') {
      navigate('/generate');
    } else {
      navigate('/datasets');
    }
  };

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-6xl mx-auto">
        <Header />
        
        {/* Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => handleViewChange('main')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                currentView === 'main'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              Generate Time Series
            </button>
            <button
              onClick={() => handleViewChange('published')}
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
            {loadingDataset && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  <span className="text-blue-700">Loading dataset...</span>
                </div>
              </div>
            )}

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
              originalScenario={description}
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
