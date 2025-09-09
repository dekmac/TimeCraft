---
applyTo: '**'
---


# TimeCraft Development Guidelines

## 🚀 Golden Rules

These are **non-negotiable** coding standards that must be followed in this project.

### 1. One Class/Interface/Struct Per File 🏗️
- **NEVER** put multiple classes, interfaces, or structs in a single file
- File name **MUST** match the class/interface/struct name exactly
- Example: `GenerateTagsRequest.cs` contains only `GenerateTagsRequest` class

### 2. File-Scoped Namespaces 📦
- Use file-scoped namespaces: `namespace TimeCraft.Web.Models;`
- **NOT** block-scoped: `namespace TimeCraft.Web.Models { }`

### 3. Defensive Programming 🛡️
- Always use null checks, guard clauses, and early returns
- Validate inputs at API boundaries
- Use nullable reference types (`string?` not `string`)
- Handle exceptions gracefully with proper logging

### 4. Keep Files Under 200 Lines 📏
- **All class files should be no longer than ~200 lines**
- If a file exceeds 200 lines, it's time to refactor
- Extract methods, split responsibilities, break into smaller classes
- Exception: Configuration files are exempt

## 🏛️ Architecture Principles

### Dependency Injection
- Use constructor injection for all dependencies
- Register services in `Program.cs`
- Prefer interfaces over concrete types

### Configuration
- Use strongly-typed `Settings` classes with `IOptions<T>`
- **NEVER** inject `IConfiguration` directly
- Support layered configuration (appsettings.json → appsettings.Development.json → environment variables)
- Suffix all config classes with `Settings` (e.g., `PythonApiSettings`)

### Organization by Feature
- Organize code by **feature**, then **type**, then **category**
- Example: `src/Features/TimeSeries/Services/TimeSeriesService.cs`
- Not: `src/Services/TimeSeriesService.cs`

## 🧪 Testing Standards

### Test Naming
- Use `Given_When_Then` syntax for test method names
- Example: `Given_ValidScenario_When_GeneratingTags_Then_ReturnsExpectedTags()`

### Test Location
- Place tests in `/tests/<platform>/<project>/` structure
- Keep tests near code but excluded from build/deployment
- Example: `/tests/unit/TimeCraft.Web.Tests/`

## 🎨 Code Style

### C# Specific
- Use `nameof()` over string literals
- Fix **ALL** warnings or document why they're ignored
- Use modern C# features (records, pattern matching, etc.)
- Prefer expression-bodied members when appropriate
- **All class files should be no longer than ~200 lines**
- When a class exceeds 200 lines, refactor by:
  - Extracting methods into smaller methods
  - Breaking the class into multiple classes
  - Moving responsibilities to separate services or utilities

### React/TypeScript
- Use **functional components** with hooks only
- No class components (ever)
- Use `useState`, `useEffect`, `useMemo`, `useCallback` appropriately
- Extract common logic into custom hooks

#### Component Architecture
- **Break down all pages and components** into components, hooks, and services for maintainability
- Components should be focused and single-purpose
- Extract business logic into custom hooks
- Move data access and API calls to services

#### HTTP Communication
- **Use Axios for all HTTP calls** with interceptors for authentication
- Configure Axios interceptors to automatically add auth headers
- Centralize API configuration and error handling
- Example interceptor setup:
  ```typescript
  axios.interceptors.request.use((config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  ```

### CSS Guidelines
- **Tailwind CSS only** - no custom stylesheets unless absolutely required
- Group classes by function: layout → spacing → color → state
- Use utility classes for all styling

## 📁 Project Structure

```
TimeCraft.Web/
├── Controllers/           # API controllers (one per file)
├── Models/               # Data models (one per file)
├── Services/             # Business logic services
│   ├── Interfaces/       # Service interfaces
│   └── Implementations/  # Service implementations
├── Settings/             # Configuration classes
├── Extensions/           # Extension methods
└── ClientApp/            # React frontend
    ├── src/
    │   ├── components/   # Reusable React components
    │   ├── hooks/        # Custom React hooks
    │   ├── types/        # TypeScript type definitions
    │   └── utils/        # Utility functions
    └── public/           # Static assets
```

## 🔐 Security Guidelines

### API Design
- All API calls should go through .NET controllers (no direct Python API access)
- Validate all inputs at controller level
- Use proper HTTP status codes
- Log security events

### Error Handling
- Never expose internal errors to clients
- Use generic error messages for security
- Log detailed errors server-side only

## 🚀 Development Workflow

### Before Making Changes
1. Create feature branch from `main`
2. Check that changes are architectural - if so, create ADR
3. Create plan with numbered phases and tasks
4. Show plan before starting work

### During Development
- Follow the one-class-per-file rule **religiously**
- Run `dotnet build` frequently to catch issues early
- Test changes incrementally
- Keep commits small and focused

### After Changes
- Create `CodeTour` to walk through updates
- Update documentation if needed
- Test full integration before PR
- Follow conventional commit format with model attribution

## 🧰 Tools and Commands

### Useful Commands
```bash
# Build the entire solution
dotnet build

# Run with hot reload
dotnet run

# Add new package
dotnet add package PackageName

# Check for warnings
dotnet build --verbosity normal
```

### VS Code Integration
- Use provided launch configurations
- "TimeCraft Full Stack (.NET React)" for development
- Both Python API and .NET app start automatically

## ❌ Common Violations to Avoid

### File Organization
- ❌ Multiple classes in one file
- ❌ Inconsistent file naming
- ❌ Deep nesting of logic/structures

### Architecture
- ❌ Injecting `IConfiguration` directly
- ❌ Not using dependency injection
- ❌ Exposing internal APIs directly

### Code Quality
- ❌ Ignoring compiler warnings
- ❌ Missing null checks
- ❌ Files over 200 lines
- ❌ Class components in React

## 🎯 Quality Gates

Before any PR:
- [ ] All files follow one-class-per-file rule
- [ ] No compiler warnings
- [ ] All new code has appropriate tests
- [ ] Files are under 200 lines
- [ ] Proper error handling implemented
- [ ] Configuration follows Settings pattern
- [ ] API routes through .NET (no direct Python access)

## 📚 Additional Resources

- [.NET Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [React Hooks Best Practices](https://react.dev/reference/react)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

**Remember: These guidelines ensure code quality, maintainability, and team productivity. They are not suggestions - they are requirements.**
