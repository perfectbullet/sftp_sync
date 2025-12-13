# SFTP Sync Web UI

Modern web management interface for SFTP Sync, built with Vue 3 and Vite.

## Features

- 📝 Visual configuration editor
- 📊 Real-time sync status monitoring
- 💾 Configuration management (save/load/delete)
- 🔌 Connection testing
- 🎨 Clean and responsive UI

## Development

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

The dev server will run at `http://localhost:5173` with API proxy to `http://localhost:8000`.

## Build

Build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory and are automatically served by the FastAPI backend.

## Environment Variables

Create a `.env` file for development:

```
VITE_API_URL=http://localhost:8000
```

For production, the API is served from the same origin as the frontend.

## Project Structure

```
web-ui/
├── src/
│   ├── components/
│   │   ├── SyncConfig.vue      # Main sync configuration form
│   │   ├── SyncStatus.vue      # Sync task status display
│   │   └── ConfigManager.vue   # Saved config management
│   ├── api.js                   # API client
│   ├── App.vue                  # Main app component
│   ├── main.js                  # App entry point
│   └── style.css                # Global styles
├── public/                      # Static assets
├── dist/                        # Build output (served by backend)
└── vite.config.js              # Vite configuration
```

## Tech Stack

- Vue 3 - Progressive JavaScript framework
- Vite - Next generation frontend tooling
- Axios - HTTP client for API requests
