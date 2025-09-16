export interface TimeSeriesData {
    name: string;
    data: number[];
    timestamps?: string[];
}

export interface GeneratedTag {
    tag: string;
    description: string;
}

export type TagProgressStatus = 'pending' | 'generating-tag' | 'tag-complete' | 'generating-timeseries' | 'complete' | 'error';

export interface TagProgress extends GeneratedTag {
    status: TagProgressStatus;
    error?: string;
    timeSeriesData?: TimeSeriesData;
    anomalies?: AnomalyInfo[];
    selectedInjectionPoint?: InjectionPoint;
}

export interface GenerateTagsRequest {
  Text: string;
  timeHorizon?: {
    period: number;
    unit: 'minutes' | 'hours' | 'days' | 'weeks';
    granularity: 'minute' | 'hour' | 'day';
    totalPoints: number;
  };
}

export interface GenerateTagsResponse {
  success: boolean;
  tags: GeneratedTag[];
  message?: string;
}

export interface GenerateTimeSeriesRequest {
    tag: string;
    scenario: string;
    timeHorizon?: {
        period: number;
        unit: 'minutes' | 'hours' | 'days' | 'weeks';
        granularity: 'minute' | 'hour' | 'day';
        totalPoints: number;
        batchSize?: number;
        batchIndex?: number;
    };
}

export interface RegenerateTimeSeriesRequest {
    tag: string;
    scenario: string;
    instructions?: string;
    sequenceLength?: number;
    tagIndex?: number;
    timeHorizon?: {
        period: number;
        unit: 'minutes' | 'hours' | 'days' | 'weeks';
        granularity: 'minute' | 'hour' | 'day';
        totalPoints: number;
        batchSize?: number;
        batchIndex?: number;
    };
}

export interface GenerateTimeSeriesResponse {
    success: boolean;
    tagName: string;
    timeSeries: number[];
    timestamps: string[];
    message?: string;
}

export interface GenerateAnomalyRequest {
    tagName: string;
    tagDescription: string;
    existingTimeSeries: number[];
    injectionStartIndex: number;
    injectionEndIndex: number;
    anomalyType: string;
    anomalyDescription: string;
    severity: number;
}

export interface GenerateAnomalyResponse {
    success: boolean;
    message: string;
    tagName: string;
    modifiedTimeSeries: number[];
    timestamps: string[];
    anomalyStartIndex: number;
    anomalyEndIndex: number;
    anomalyType: string;
}

export interface AnomalyInfo {
    startIndex: number;
    endIndex: number;
    type: string;
    description: string;
    severity: number;
}

export interface InjectionPoint {
    index: number;
    selected: boolean;
}

// Publishing types
export interface EventHubConfig {
    eventHubName: string;
    namespaceName: string;
    connectionString?: string;
    useManagedIdentity: boolean;
    partitionKey?: string;
    additionalProperties?: Record<string, string>;
}

export interface OpcUaSettings {
    namespaceUri: string;
    namespaceIndex: number;
    useDataSetWriterId: boolean;
    publishingInterval: number;
    enableDeltaFrames: boolean;
    applicationName: string;
    applicationUri: string;
    customProperties?: Record<string, string>;
}

export interface DatasetTag {
    tagName: string;
    description: string;
    timeSeriesData: TimeSeriesDataPoint[];
    dataType: string;
    unit?: string;
    metadata?: Record<string, string>;
}

export interface TimeSeriesDataPoint {
    time?: string;
    value: number;
}

export interface PublishDatasetRequest {
    datasetName: string;
    description: string;
    originalPrompt?: string;
    tags: DatasetTag[];
    eventHubConfig: EventHubConfig;
    opcUaSettings: OpcUaSettings;
    metadata?: Record<string, string>;
}

export interface PublishTimeSeriesRequest {
    datasetName: string;
    description: string;
    timeSeriesData: TimeSeriesDataPoint[];
    eventHubConfig: EventHubConfig;
    metadata?: Record<string, string>;
}

export interface PublishTimeSeriesResponse {
    publishId: string;
    message: string;
    status: PublishingStatus;
    createdAt: string;
}

export type PublishingStatus = 'Pending' | 'InProgress' | 'Completed' | 'Failed' | 'Retrying';

export type PublishingMode = 'Batch' | 'Loop' | 'RealTimeStream';

export interface StreamConfiguration {
    mode: PublishingMode;
    streamIntervalMs: number;
    streamSpeed: number;
    loopCycles?: number | null;
    loopPauseMs: number;
    isActive: boolean;
    currentCycle: number;
    streamStartTime?: string;
    reIngestionCount: number;
    currentStreamPosition: number;
    streamPointsSent: number;
    pausedAt?: string;
    totalStreamTime: string; // TimeSpan as string
}

export interface UpdateModeRequest {
    mode: PublishingMode;
    streamConfig?: StreamConfiguration;
}

export interface PublishedDataset {
    id: string;
    datasetName: string;
    description: string;
    originalPrompt?: string;
    scenarioParameters?: string;
    status: PublishingStatus;
    createdAt: string;
    publishedAt?: string;
    eventHubName: string;
    namespaceName: string;
    totalDataPoints: number;
    publishedDataPoints: number;
    totalTags: number;
    publishedTags: number;
    errorMessage?: string;
    retryCount: number;
    progressPercentage: number;
    streamConfig?: StreamConfiguration;
}

export interface DatasetContent {
    id: string;
    datasetName: string;
    description: string;
    originalPrompt?: string;
    scenarioParameters?: string;
    tags: DatasetTag[];
    status: PublishingStatus;
    createdAt: string;
    publishedAt?: string;
    totalTags: number;
    totalDataPoints: number;
}

export interface PublishingStatusInfo {
    id: string;
    status: string;
    progressPercentage: number;
    publishedDataPoints: number;
    totalDataPoints: number;
    errorMessage?: string;
    retryCount: number;
    createdAt: string;
    publishedAt?: string;
}
