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
