import axios, { type AxiosInstance } from 'axios';
import type { 
  GenerateTagsRequest, 
  GenerateTagsResponse, 
  GenerateTimeSeriesRequest, 
  GenerateTimeSeriesResponse,
  GenerateAnomalyRequest,
  GenerateAnomalyResponse,
  PublishTimeSeriesRequest,
  PublishTimeSeriesResponse,
  PublishDatasetRequest,
  PublishedDataset,
  PublishingStatusInfo,
  UpdateModeRequest,
  PublishingMode
} from '../types/api';

class TimeCraftApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 180000, // 3 minutes to accommodate reflection operations
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token when available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    // TODO: Implement actual token retrieval logic
    // For now, return null as auth is not implemented
    return null;
  }

  async generateTags(request: GenerateTagsRequest): Promise<GenerateTagsResponse> {
    console.log('Generating tags with request:', request);
    const response = await this.api.post<GenerateTagsResponse>('/timecraft/generate-tags', request);
    return response.data;
  }

  async generateTimeSeries(request: GenerateTimeSeriesRequest): Promise<GenerateTimeSeriesResponse> {
    const response = await this.api.post<GenerateTimeSeriesResponse>('/timecraft/generate-timeseries', request);
    return response.data;
  }

  async generateAnomaly(request: GenerateAnomalyRequest): Promise<GenerateAnomalyResponse> {
    console.log('Generating anomaly with request:', request);
    const response = await this.api.post<GenerateAnomalyResponse>('/timecraft/generate-anomaly', request);
    return response.data;
  }

  async publishDataset(request: PublishDatasetRequest): Promise<PublishTimeSeriesResponse> {
    console.log('Publishing dataset with request:', request);
    const response = await this.api.post<PublishTimeSeriesResponse>('/timecraft/publish-dataset', request);
    return response.data;
  }

  async publishTimeSeries(request: PublishTimeSeriesRequest): Promise<PublishTimeSeriesResponse> {
    console.log('Publishing time series with request:', request);
    const response = await this.api.post<PublishTimeSeriesResponse>('/timecraft/publish-timeseries', request);
    return response.data;
  }

  async getPublishedDatasets(): Promise<PublishedDataset[]> {
    const response = await this.api.get<PublishedDataset[]>('/publishing/datasets');
    return response.data;
  }

  async getPublishedDataset(id: string): Promise<PublishedDataset> {
    const response = await this.api.get<PublishedDataset>(`/publishing/datasets/${id}`);
    return response.data;
  }

  async getPublishingStatus(id: string): Promise<PublishingStatusInfo> {
    const response = await this.api.get<PublishingStatusInfo>(`/publishing/datasets/${id}/status`);
    return response.data;
  }

  async forceRetryDataset(id: string): Promise<{ message: string; datasetId: string }> {
    const response = await this.api.post<{ message: string; datasetId: string }>(`/publishing/datasets/${id}/force-retry`);
    return response.data;
  }

  async downloadDatasetCsv(id: string, filename: string): Promise<void> {
    const response = await this.api.get(`/publishing/datasets/${id}/download-csv`, {
      responseType: 'blob'
    });
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  // New Publishing Mode APIs
  async reIngestDataset(id: string): Promise<{ message: string; datasetId: string }> {
    const response = await this.api.post<{ message: string; datasetId: string }>(`/publishing/datasets/${id}/re-ingest`);
    return response.data;
  }

  async updatePublishingMode(id: string, request: UpdateModeRequest): Promise<{ message: string; datasetId: string; mode: PublishingMode }> {
    console.log('Updating publishing mode:', { id, request });
    const response = await this.api.put<{ message: string; datasetId: string; mode: PublishingMode }>(`/publishing/datasets/${id}/mode`, request);
    return response.data;
  }

  async stopStreaming(id: string): Promise<{ message: string; datasetId: string }> {
    const response = await this.api.post<{ message: string; datasetId: string }>(`/publishing/datasets/${id}/stop`);
    return response.data;
  }

  async startStreaming(id: string): Promise<{ message: string; datasetId: string }> {
    const response = await this.api.post<{ message: string; datasetId: string }>(`/publishing/datasets/${id}/start`);
    return response.data;
  }

  async pauseStreaming(id: string): Promise<{ message: string; datasetId: string }> {
    const response = await this.api.post<{ message: string; datasetId: string }>(`/publishing/datasets/${id}/pause`);
    return response.data;
  }

  async updateStreamingProgress(id: string, pointsSent: number, currentPosition: number): Promise<{ message: string }> {
    const response = await this.api.post<{ message: string }>(`/publishing/datasets/${id}/update-progress`, {
      pointsSent,
      currentPosition
    });
    return response.data;
  }

  async updateStreamingStats(id: string, isActive: boolean, cycleCount?: number): Promise<{ message: string }> {
    const response = await this.api.post<{ message: string }>(`/publishing/datasets/${id}/update-stats`, {
      isActive,
      cycleCount
    });
    return response.data;
  }
}

export const timeCraftApi = new TimeCraftApiService();
