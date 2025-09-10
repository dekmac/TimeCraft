import axios, { type AxiosInstance } from 'axios';
import type { 
  GenerateTagsRequest, 
  GenerateTagsResponse, 
  GenerateTimeSeriesRequest, 
  GenerateTimeSeriesResponse 
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
}

export const timeCraftApi = new TimeCraftApiService();
