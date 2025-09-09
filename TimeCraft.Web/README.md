# TimeCraft .NET React Frontend

This directory contains a modern .NET 8 + React + TypeScript frontend for TimeCraft, providing a better development experience compared to the legacy Python HTTP server approach.

## Features

- **Modern Development Stack**: .NET 8 + React 18 + TypeScript + Vite
- **Hot Reload**: Instant feedback during development
- **API Proxy**: Seamless integration with Python FastAPI backend
- **Beautiful UI**: Tailwind CSS with glassmorphism design
- **Chart Visualization**: Chart.js integration for time series display
- **Type Safety**: Full TypeScript support

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│  .NET React App │◄──►│   API Proxy      │◄──►│ Python FastAPI  │
│  (Port 5173)    │    │   (/api/*)       │    │ (Port 8080)     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Development Setup

### 1. Prerequisites
- .NET 8 SDK
- Node.js 18+
- Python 3.11+

### 2. Install Dependencies

```bash
# .NET dependencies (already done)
dotnet restore

# React dependencies
cd ClientApp
npm install
```

### 3. Run in Development

**Option A: VS Code F5 (Recommended)**

1. Open VS Code in the root TimeCraft directory
2. Press F5 and select "TimeCraft Full Stack (.NET React)"
3. This will start both the Python API server and .NET React app
4. .NET automatically starts and manages the Vite dev server

**Option B: Manual Start**

Terminal 1 - Python API:
```bash
# From TimeCraft root directory
python api_server.py
```

Terminal 2 - .NET React App:
```bash
# From TimeCraft.Web directory  
dotnet run
# This automatically starts Vite dev server
```

### 4. Access the Application

- **Frontend**: http://localhost:5173 (Vite dev server)
- **API**: http://localhost:8080 (Python FastAPI)
- **.NET App**: https://localhost:7154 (Production build)

## Project Structure

```
TimeCraft.Web/
├── TimeCraft.Web/               # .NET Web Application
│   ├── Program.cs              # ASP.NET Core configuration
│   ├── TimeCraft.Web.csproj    # .NET project file
│   └── ClientApp/              # React TypeScript App
│       ├── src/
│       │   ├── TimeCraftApp.tsx # Main TimeCraft component
│       │   ├── App.tsx         # React app entry
│       │   └── index.css       # Tailwind CSS styles
│       ├── vite.config.ts      # Vite configuration
│       ├── tailwind.config.js  # Tailwind CSS config
│       └── package.json        # React dependencies
└── README.md                   # This file
```

## Key Components

### TimeCraftApp.tsx
The main React component that provides:
- Scenario input form
- Time series generation
- Chart visualization
- Error handling
- Loading states

### Vite Configuration
- API proxy to Python FastAPI server
- Hot reload configuration
- TypeScript support

### .NET Configuration
- SPA hosting with proxy to Vite dev server
- CORS configuration for API access
- Production build support

## API Integration

The frontend communicates with the Python API through:

1. **Development**: Vite proxy (`/api/*` → `http://localhost:8080/*`)
2. **Production**: .NET proxy (configurable)

### API Endpoints Used:
- `POST /api/generate-tags` - Generate semantic tags
- `POST /api/generate-timeseries-for-tag` - Generate time series data
- `POST /api/refine-prompt` - Refine prompts (if implemented)

## Benefits Over Legacy HTML Approach

1. **Developer Experience**
   - Hot reload and instant feedback
   - TypeScript for type safety
   - Modern debugging tools
   - Component-based architecture

2. **Production Ready**
   - Optimized builds
   - Code splitting
   - Tree shaking
   - Modern browser features

3. **Maintainability**
   - Structured codebase
   - Reusable components
   - Clear separation of concerns
   - Modern development patterns

4. **Performance**
   - Fast development server
   - Optimized production builds
   - Efficient asset loading
   - Better caching strategies

## Production Deployment

1. Build the React app:
   ```bash
   cd ClientApp
   npm run build
   ```

2. Publish the .NET app:
   ```bash
   dotnet publish -c Release
   ```

3. The published app will include the built React frontend and can be deployed as a single unit.

## Troubleshooting

### Port Conflicts
- React Dev Server: 44445
- Python API: 8080
- .NET App: 5173 (dev), 7154 (https)

### API Connection Issues
1. Ensure Python API server is running on port 8080
2. Check CORS configuration in Program.cs
3. Verify proxy configuration in vite.config.ts

### Build Issues
1. Ensure all dependencies are installed
2. Check .NET and Node.js versions
3. Clear node_modules and reinstall if needed
