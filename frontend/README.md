# Startup Funding Intelligence - React Frontend

This is the React.js frontend for the Startup Funding Intelligence application.

## Features

- **Professional UI** - Clean, modern design without emojis
- **Right-Side Menu** - Slide-in menu bar from the right
- **Voice Input** - Microphone button for voice queries (placeholder)
- **Responsive Design** - Works on desktop and mobile
- **Real-time Status** - API connection status indicator
- **Example Queries** - Quick-start query buttons
- **Multilingual Support** - English and Hindi

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open in your browser at `http://localhost:3000`

### Backend Setup

Make sure the FastAPI backend is running:

```bash
cd ..
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js / Header.css
│   │   ├── SearchBar.js / SearchBar.css
│   │   ├── ExampleQueries.js / ExampleQueries.css
│   │   ├── Results.js / Results.css
│   │   ├── Sidebar.js / Sidebar.css
│   │   └── StatusBar.js / StatusBar.css
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

## Design Features

- **Gradient Elements** - Purple to violet gradients (#667eea to #764ba2)
- **Clean Typography** - Inter font family
- **Smooth Animations** - Hover effects and transitions
- **Card-based Layout** - Modern card design for sections
- **Professional Color Scheme** - Consistent purple theme
- **Right-Side Navigation** - Hamburger menu slides from right

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Runs tests
- `npm eject` - Ejects from Create React App (irreversible)

## Technologies Used

- React.js
- Axios for API calls
- React Icons
- CSS3 with modern features
- Inter font from Google Fonts
