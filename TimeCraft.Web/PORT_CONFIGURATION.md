# TimeCraft Port Configuration

## Fixed Port Mapping

After resolving the port mismatch issues, here's the corrected configuration:

### Development Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **Vite Dev Server** | 44445 | HTTPS | React frontend development server |
| **.NET Application** | 7154 | HTTPS | .NET backend (production proxy) |
| **.NET Application** | 5173 | HTTP | .NET backend (fallback) |
| **Python FastAPI** | 8080 | HTTP | TimeCraft API server |

### Configuration Files Updated

#### 1. `vite.config.ts`
```typescript
server: {
    port: 44445,  // Changed from 7252 to match .NET proxy expectation
    // HTTPS is handled by mkcert plugin
    proxy: {
        '/api': {
            target: 'http://localhost:8080',  // Python API
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/api/, '')
        }
    }
}
```

#### 2. `launchSettings.json`
```json
"applicationUrl": "https://localhost:7154;http://localhost:5173"
```

#### 3. `Program.cs`
```csharp
spa.UseProxyToSpaDevelopmentServer("https://localhost:44445");  // Changed to HTTPS
```

## How It Works

### Development Flow
1. **VS Code F5**: Starts both Python API (port 8080) and .NET app (port 7154)
2. **.NET App**: Automatically starts and manages Vite dev server (port 44445)
3. **.NET SPA Proxy**: Handles all proxying to Vite dev server
4. **Vite Dev Server**: Serves React app with hot reload (automatically managed)
5. **API Calls**: Vite proxies `/api/*` calls to Python server (port 8080)

### Request Flow Diagram
```
Browser → .NET App (7154) → Vite Dev Server (44445) → Python API (8080)
         (HTTPS)            (HTTPS)                   (HTTP)
```

### Access Points

During development:
- **Primary URL**: https://localhost:7154 (through .NET proxy)
- **Direct Vite URL**: https://localhost:44445 (direct access, bypasses .NET)
- **API Direct**: http://localhost:8080 (for API testing)

## Previous Issues Fixed

### Issue 1: Port Mismatch
- **Problem**: .NET expected Vite on port 44445, but Vite was running on 7252
- **Solution**: Changed Vite port to 44445 in `vite.config.ts`

### Issue 2: HTTP/HTTPS Mismatch
- **Problem**: .NET was proxying to HTTP, but mkcert enables HTTPS
- **Solution**: Updated .NET proxy URL to use HTTPS

### Issue 3: Port Conflicts
- **Problem**: .NET and Vite both trying to use port 7252
- **Solution**: Separated ports - .NET on 7154, Vite on 44445

## Debugging Tips

### Check if services are running:
```powershell
# Check .NET app
netstat -an | findstr :7154

# Check Vite dev server
netstat -an | findstr :44445

# Check Python API
netstat -an | findstr :8080
```

### VS Code Launch Configuration
Use the "TimeCraft Full Stack (.NET React)" configuration which:
1. Starts Python API server on port 8080
2. Starts .NET app which proxies to Vite on port 44445
3. Vite serves React app with hot reload and API proxy

### Common Issues

#### "Cannot connect to Vite dev server"
- Ensure Vite is running on port 44445
- Check that mkcert certificates are installed
- Verify no firewall blocking HTTPS on 44445

#### "API calls failing with 404"
- Confirm Python API is running on port 8080
- Check Vite proxy configuration in `vite.config.ts`
- Verify API endpoints in React code use `/api/` prefix

#### "SSL certificate issues"
- Run `mkcert -install` to install root CA
- Restart browsers after certificate installation
- Check that vite-plugin-mkcert is in vite.config.ts

## Production Notes

In production, the React app will be built and served directly by the .NET application:
- No Vite dev server needed
- Static files served from `ClientApp/dist`
- API calls go directly to Python server
- Single deployment unit including both frontend and backend proxy
