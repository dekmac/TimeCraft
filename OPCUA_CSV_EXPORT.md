# OPC UA Delta Frames CSV Export

This feature allows you to download CSV files containing OPC UA delta frames with relative timestamps from published datasets.

## API Endpoints

### GET Export (Query Parameters)
```
GET /api/publishing/datasets/{id}/export-csv
```

**Query Parameters:**
- `useRelativeTimestamps` (bool, default: true) - Use relative timestamps from reference time
- `startTime` (DateTime, optional) - Filter data from this time
- `endTime` (DateTime, optional) - Filter data until this time  
- `referenceTime` (DateTime, optional) - Reference time for relative timestamps (defaults to current UTC time)
- `tagFilter` (string[], optional) - Filter specific tag names

**Example:**
```
GET /api/publishing/datasets/abc123/export-csv?useRelativeTimestamps=true&tagFilter=Temperature&tagFilter=Pressure
```

### POST Export (JSON Body)
```
POST /api/publishing/datasets/{id}/export-csv
```

**Request Body:**
```json
{
  "useRelativeTimestamps": true,
  "startTime": "2024-01-01T00:00:00Z",
  "endTime": "2024-01-01T23:59:59Z",
  "referenceTime": "2024-01-01T12:00:00Z",
  "tagFilter": ["Temperature", "Pressure"]
}
```

## CSV Format

### With Relative Timestamps (default)
```csv
RelativeTimeSeconds,OriginalTimestamp,TagName,NodeId,DisplayName,Value,DataType,StatusCode,SequenceNumber,DataSetWriterId
-3600.000,2024-01-01 11:00:00.000,Temperature,ns=2;s=Temperature,Temperature,23.5,Double,0,1,MyDataset_Temperature
-3300.000,2024-01-01 11:05:00.000,Temperature,ns=2;s=Temperature,Temperature,24.1,Double,0,2,MyDataset_Temperature
```

### With Absolute Timestamps
```csv
Timestamp,TagName,NodeId,DisplayName,Value,DataType,StatusCode,SequenceNumber,DataSetWriterId
2024-01-01 11:00:00.000,Temperature,ns=2;s=Temperature,Temperature,23.5,Double,0,1,MyDataset_Temperature
2024-01-01 11:05:00.000,Temperature,ns=2;s=Temperature,Temperature,24.1,Double,0,2,MyDataset_Temperature
```

## Features

- **Relative Timestamps**: Shows time differences in seconds from a reference point (useful for analysis)
- **Time Filtering**: Export only data within specific time ranges
- **Tag Filtering**: Export only specific tags from the dataset
- **OPC UA Format**: Includes all standard OPC UA delta frame fields
- **Automatic Filename**: Generated with dataset name and timestamp

## Usage Examples

### Download all data with relative timestamps
```bash
curl -O -J "http://localhost:5000/api/publishing/datasets/abc123/export-csv"
```

### Download specific tags for a time range
```bash
curl -O -J "http://localhost:5000/api/publishing/datasets/abc123/export-csv?startTime=2024-01-01T10:00:00Z&endTime=2024-01-01T14:00:00Z&tagFilter=Temperature&tagFilter=Pressure"
```

### Download with custom reference time
```bash
curl -X POST "http://localhost:5000/api/publishing/datasets/abc123/export-csv" \
  -H "Content-Type: application/json" \
  -d '{"useRelativeTimestamps": true, "referenceTime": "2024-01-01T12:00:00Z"}' \
  --output deltaframes.csv
```

## Notes

- Data points are generated with 5-minute intervals by default
- Relative timestamps are calculated as seconds difference from reference time
- Negative relative timestamps indicate data points before the reference time
- StatusCode 0 indicates "Good" data quality in OPC UA
- All CSV values are properly escaped for special characters