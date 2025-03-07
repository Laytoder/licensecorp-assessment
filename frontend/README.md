# Task Management System Frontend

This is the Next.js frontend for the Task Management System, providing a responsive UI for task management and real-time analytics.

## Features

- Modern React-based UI built with Next.js
- Real-time task updates and analytics visualization
- Responsive design for desktop and mobile
- Optimized for handling large volumes of tasks

## Local Setup

### Prerequisites

- Node.js 14+ and npm

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up environment variables (create a `.env.local` file in the frontend directory):

```
NEXT_PUBLIC_API_URL=http://localhost:8002
```

### Running the Frontend

Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### Building for Production

```bash
npm run build
npm run start
```

## Project Structure

- `components/` - Reusable UI components
- `pages/` - Next.js pages and routes
- `public/` - Static assets
- `styles/` - CSS and styling
- `utils/` - Utility functions and API clients

## Deployment

See the main [README.md](../README.md) for Docker deployment instructions.
