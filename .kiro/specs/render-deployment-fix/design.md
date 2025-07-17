# Design Document

## Overview

The deployment fix involves creating proper configuration files for Render, modifying the Flask app to handle dynamic port assignment, and ensuring the React build process works correctly in the deployment environment. The solution addresses the "Error connecting to server" issue by properly configuring the backend-frontend communication for production deployment.

## Architecture

### Deployment Flow
```
1. Render receives code push
2. Build script installs Python dependencies
3. Build script installs Node.js dependencies  
4. Build script builds React frontend
5. Start script launches Flask app with correct port
6. Flask serves both API endpoints and React static files
```

### Environment Configuration
- **Development**: Flask runs on localhost:5050, React dev server on localhost:3000
- **Production**: Flask runs on Render's dynamic port, serves built React files

## Components and Interfaces

### 1. Render Configuration Files

#### Build Script (`build.sh`)
- Installs Python dependencies via pip
- Installs Node.js dependencies via npm
- Builds React production bundle
- Ensures model files are accessible

#### Start Script (`start.sh`) 
- Sets environment variables
- Starts Flask app with production settings
- Uses Render's PORT environment variable

### 2. Flask Application Modifications

#### Port Configuration
```python
port = int(os.environ.get("PORT", 5050))
app.run(host="0.0.0.0", port=port)
```

#### Environment Detection
```python
is_production = os.environ.get("RENDER") is not None
```

#### CORS Configuration
- Allow requests from deployed domain
- Handle preflight requests properly

### 3. React Frontend Modifications

#### API Base URL Configuration
```javascript
const baseURL = process.env.NODE_ENV === "production" 
  ? "" // Same origin for production
  : "http://localhost:5050"; // Local development
```

#### Build Optimization
- Ensure build artifacts are properly generated
- Configure static file serving paths

## Data Models

No changes to existing data models are required. The User model and ML model interfaces remain unchanged.

## Error Handling

### Deployment Errors
- Build script failures: Log detailed error messages
- Missing dependencies: Clear error reporting
- Model loading failures: Graceful fallback with error messages

### Runtime Errors  
- Port binding issues: Fallback to default port with logging
- CORS errors: Detailed logging of blocked requests
- API connection errors: User-friendly error messages in frontend

### Frontend Error Handling
- Network connectivity issues: Display "Error connecting to server" with retry options
- Authentication failures: Redirect to login with clear messages
- API response errors: Show specific error messages from backend

## Testing Strategy

### Local Testing
1. Test build script locally to ensure it completes successfully
2. Test Flask app startup with PORT environment variable
3. Verify React build generates correct static files
4. Test API endpoints with production-like configuration

### Deployment Testing
1. Deploy to Render and verify build logs
2. Test all API endpoints through deployed URL
3. Verify frontend loads and connects to backend
4. Test complete user flow: login → symptom input → prediction
5. Test error scenarios and error message display

### Verification Steps
1. Check Render deployment logs for errors
2. Verify Flask app starts and binds to correct port
3. Test API endpoints directly via curl/Postman
4. Test frontend functionality through browser
5. Monitor for CORS or connection errors in browser console

## Implementation Notes

### File Structure After Implementation
```
├── build.sh              # New: Render build script
├── start.sh              # New: Render start script  
├── app.py                # Modified: Port configuration
├── frontend/
│   └── src/
│       └── Chatbot.js    # Modified: API URL configuration
└── requirements.txt      # Verify all dependencies listed
```

### Key Configuration Changes
1. **Dynamic Port Binding**: Flask app reads PORT from environment
2. **Build Automation**: Automated React build during deployment
3. **Static File Serving**: Proper configuration for serving React build
4. **Environment Detection**: Different behavior for dev vs production
5. **CORS Configuration**: Allow requests from deployed domain

### Render Platform Specifics
- Uses `build.sh` for build commands
- Uses `start.sh` for start commands  
- Provides PORT environment variable
- Expects apps to bind to 0.0.0.0
- Serves on HTTPS in production