export interface TimeSeriesData {
    name: string;
    data: number[];
    timestamps?: string[];
}

export interface GeneratedTag {
    tag: string;
    description: string;
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
