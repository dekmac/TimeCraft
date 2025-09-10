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
  text: string;
}

export interface GenerateTagsResponse {
  success: boolean;
  tags: GeneratedTag[];
  message?: string;
}

export interface GenerateTimeSeriesRequest {
    tag: string;
    scenario: string;
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
