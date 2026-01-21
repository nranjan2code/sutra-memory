# Sutra Desktop Edition - Web Client

World-class web interface for Sutra Desktop Edition.

## Features

- 🎨 **Modern UI**: Beautiful dark theme with smooth animations
- 💬 **Chat Interface**: Natural language interaction with `/learn` commands
- 📚 **Knowledge Browser**: Visual grid to browse, search, and manage concepts
- 📊 **Analytics Dashboard**: Real-time performance metrics
- ⚡ **Fast & Responsive**: Built with React, Vite, and TailwindCSS
- 🔄 **Real-time Updates**: Automatic stats refresh and live queries

## Tech Stack

- **React 18** - Modern UI library
- **TypeScript** - Type safety
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS
- **Framer Motion** - Smooth animations
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

The web client is containerized with nginx for optimal performance:

```bash
# Build Docker image
docker build -t sutra-desktop-web .

# Run container
docker run -p 3000:80 sutra-desktop-web
```

## Environment Variables

- `VITE_API_URL` - API backend URL (default: `/api`)

## Project Structure

```
src/
├── api/           # API client and types
├── components/    # Reusable UI components
├── pages/         # Page components
├── store/         # State management
├── App.tsx        # Main app component
├── main.tsx       # Entry point
└── index.css      # Global styles
```

## Pages

- **Chat** - Conversational interface with `/learn` commands
- **Knowledge** - Browse and manage all concepts
- **Analytics** - Real-time performance dashboard
- **Settings** - App preferences and information

## Commands

In the chat interface:

- **Ask questions**: `What is machine learning?`
- **Teach concepts**: `/learn The Earth orbits the Sun`

## License

Part of Sutra AI Desktop Edition
