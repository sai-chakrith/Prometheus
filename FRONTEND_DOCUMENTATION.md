# 🎨 Prometheus Frontend - Complete Documentation

> **For:** Developers, Reviewers, and Anyone Learning the Codebase
> **Last Updated:** January 2026

---

## 📖 Table of Contents

1. [What is This Project?](#-what-is-this-project)
2. [How Does it Work? (Simple Explanation)](#-how-does-it-work-simple-explanation)
3. [Visual Flow Charts](#-visual-flow-charts)
4. [Project Structure](#-project-structure)
5. [Component Deep Dive](#-component-deep-dive)
6. [State Management](#-state-management)
7. [Styling System](#-styling-system)
8. [API Integration](#-api-integration)
9. [Voice Input System](#-voice-input-system)
10. [Theme System](#-theme-system)
11. [Multilingual Support](#-multilingual-support)
12. [Data Flow Examples](#-data-flow-examples)
13. [Common Questions](#-common-questions)

---

## 🌟 What is This Project?

### In Simple Terms

Prometheus is like a **smart assistant** that knows everything about Indian startup funding. You can:

- **Ask questions** in 8 different languages (Hindi, Tamil, Telugu, etc.)
- **Speak your questions** using voice input
- **Get intelligent answers** backed by real data
- **View analytics** about funding trends

### Think of it Like This

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   You: "Which startups in Bangalore got the most funding?"  │
│                                                             │
│   Prometheus: "Here are the top funded startups:            │
│   1. Swiggy - ₹250 crores                                  │
│   2. Flipkart - ₹200 crores                                │
│   ..."                                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

It's like Google, but specifically for Indian startup funding data!

---

## 🧠 How Does it Work? (Simple Explanation)

### The Big Picture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         YOUR BROWSER                                  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     FRONTEND (React)                           │  │
│  │                                                                │  │
│  │  What you see:                                                 │  │
│  │  • Login page                                                  │  │
│  │  • Chat interface                                              │  │
│  │  • Voice button                                                │  │
│  │  • Analytics dashboard                                         │  │
│  └───────────────────────────┬────────────────────────────────────┘  │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                               │ HTTP Requests
                               │ (Like sending a letter)
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         SERVER                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     BACKEND (Python)                           │  │
│  │                                                                │  │
│  │  What it does:                                                 │  │
│  │  • Understands your question                                   │  │
│  │  • Searches the database                                       │  │
│  │  • Uses AI to generate answer                                  │  │
│  │  • Sends response back                                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step: What Happens When You Ask a Question?

```
Step 1: YOU TYPE A QUESTION
        ↓
        "Top 10 fintech startups"
        ↓
Step 2: FRONTEND SENDS IT TO BACKEND
        ↓
        POST /api/rag {query: "Top 10 fintech startups", lang: "en"}
        ↓
Step 3: BACKEND PROCESSES IT
        ↓
        • Converts question to numbers (embeddings)
        • Searches database for similar data
        • Builds a prompt for AI
        • AI generates human-readable answer
        ↓
Step 4: BACKEND SENDS RESPONSE
        ↓
        {answer: "Here are the top 10 fintech startups..."}
        ↓
Step 5: FRONTEND SHOWS THE ANSWER
        ↓
        You see the response in a chat bubble!
```

---

## 📊 Visual Flow Charts

### 1. Application Startup Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     APP STARTS                                   │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Check localStorage     │
                    │  for saved login token  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │ Token EXISTS  │         │ Token MISSING │
           │               │         │               │
           │ → Load user   │         │ → Show Login  │
           │ → Show chat   │         │   page        │
           └───────────────┘         └───────────────┘
```

### 2. Login/Signup Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     LOGIN PAGE                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │   [Login]  [Signup]   ← Tab selector                    │    │
│  │                                                         │    │
│  │   Username: [___________]                               │    │
│  │   Password: [___________]                               │    │
│  │                                                         │    │
│  │   [Submit Button]                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Send to Backend        │
                    │  POST /api/login        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │   SUCCESS     │         │    FAILED     │
           │               │         │               │
           │ • Save token  │         │ • Show error  │
           │ • Go to chat  │         │ • Stay here   │
           └───────────────┘         └───────────────┘
```

### 3. Chat Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        CHAT PAGE                                 │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    MESSAGE AREA                            │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 🤖 AI: Welcome! How can I help you?                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 👤 You: Top startups in Bangalore            ──────┐│  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 🤖 AI: Here are the top startups...                │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  [Type your question...        ]  [🎤]  [➤]              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

        │                          │           │
        │                          │           │
        ▼                          ▼           ▼
   Type text               Click mic      Click send
        │                     │                │
        │                     ▼                │
        │          ┌──────────────────┐        │
        │          │ Start listening  │        │
        │          │ (voice to text)  │        │
        │          └────────┬─────────┘        │
        │                   │                  │
        └───────────────────┼──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Send to Backend  │
                  │ POST /api/rag    │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Show AI Response │
                  └──────────────────┘
```

### 4. Voice Input Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE INPUT SYSTEM                            │
└─────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │ Click 🎤     │
     │ (Mic Button) │
     └──────┬───────┘
            │
            ▼
     ┌──────────────────────────────────────┐
     │ Browser asks: "Allow microphone?"    │
     └──────────────┬───────────────────────┘
                    │
       ┌────────────┴────────────┐
       │                         │
       ▼                         ▼
┌─────────────┐          ┌─────────────┐
│  ALLOWED    │          │   DENIED    │
└──────┬──────┘          └──────┬──────┘
       │                        │
       ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐
│ Start Recording     │  │ Show Error:         │
│                     │  │ "Permission denied" │
│ 🎤 Button turns RED │  └─────────────────────┘
│ and PULSES          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ User speaks:        │
│ "Show me funding    │
│  in Mumbai"         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Speech converted    │
│ to text:            │
│ "Show me funding    │
│  in Mumbai"         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Text appears in     │
│ input box           │
└─────────────────────┘
```

### 5. Theme Toggle Flow

```
                         THEME SYSTEM
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
    ┌───────────────┐                   ┌───────────────┐
    │  DARK MODE    │    Click ☀️/🌙    │  LIGHT MODE   │
    │               │◄────────────────►│               │
    │ • Dark bg     │                   │ • Light bg    │
    │ • White text  │                   │ • Dark text   │
    │ • Glass cards │                   │ • Solid cards │
    └───────────────┘                   └───────────────┘

    Visual Comparison:

    DARK MODE                          LIGHT MODE
    ┌────────────────────┐             ┌────────────────────┐
    │████████████████████│             │░░░░░░░░░░░░░░░░░░░░│
    │██ ░░░░░░░░░░░░░ ██│             │░░ ████████████ ░░░░│
    │██ ░░  TEXT  ░░░ ██│             │░░ ░░  TEXT  ░░ ░░░░│
    │██ ░░░░░░░░░░░░░ ██│             │░░ ████████████ ░░░░│
    │████████████████████│             │░░░░░░░░░░░░░░░░░░░░│
    └────────────────────┘             └────────────────────┘
```

### 6. Page Navigation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         HEADER                                   │
│  [Logo] [User] [Language ▼] [🔄] [☀️] [Logout]                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TAB NAVIGATION                              │
│                                                                  │
│        [💬 Chat]      [📜 History]      [📊 Insights]           │
│            │               │                  │                  │
└────────────┼───────────────┼──────────────────┼──────────────────┘
             │               │                  │
             ▼               ▼                  ▼
      ┌──────────┐    ┌──────────┐      ┌──────────┐
      │   CHAT   │    │ HISTORY  │      │ INSIGHTS │
      │          │    │          │      │          │
      │ • Talk   │    │ • Past   │      │ • Stats  │
      │   to AI  │    │   chats  │      │ • Trends │
      │ • Voice  │    │ • Search │      │ • Policy │
      │   input  │    │ • Filter │      │   info   │
      └──────────┘    └──────────┘      └──────────┘
```

---

## 📁 Project Structure

### Folder Organization (What Each File Does)

```
prometheus-ui/frontend/
│
├── 📄 index.html              ← The single HTML page (React fills this)
├── 📄 package.json            ← List of all packages/libraries used
├── 📄 vite.config.js          ← Build tool settings
├── 📄 tailwind.config.js      ← CSS styling settings
│
└── 📁 src/                    ← ALL THE CODE LIVES HERE
    │
    ├── 📄 main.jsx            ← ENTRY POINT (app starts here)
    │   └── Loads PrometheusApp
    │
    ├── 📄 index.css           ← Global CSS styles
    │
    ├── 📄 api.js              ← Talks to the backend server
    │   └── Sets up: base URL, caching, etc.
    │
    ├── 📄 PrometheusApp.jsx   ← MAIN APP (589 lines)
    │   └── Contains: Header, Tabs, Chat, everything!
    │
    ├── 📄 Auth.jsx            ← Login & Signup page (320 lines)
    │   └── Contains: Login form, Signup form
    │
    ├── 📄 Insights.jsx        ← Analytics dashboard (313 lines)
    │   └── Contains: Investors, Trends, Policy tabs
    │
    ├── 📄 ChatHistoryOptimized.jsx  ← Past conversations
    │   └── Contains: Search, filters, chat list
    │
    ├── 📄 translations.js     ← Text in different languages
    │   └── Contains: UI text for en, hi, ta, te, etc.
    │
    ├── 📁 components/         ← Reusable UI pieces
    │   ├── 📁 chat/
    │   │   ├── ChatInput.jsx  ← Input box + buttons
    │   │   └── MessageList.jsx← Chat bubbles
    │   └── 📁 layout/
    │       └── Header.jsx     ← Top navigation bar
    │
    ├── 📁 hooks/              ← Custom React hooks
    │   ├── index.js           ← Exports all hooks
    │   └── useSpeechRecognition.js  ← Voice input logic
    │
    └── 📁 constants/          ← Fixed values
        └── languages.js       ← Language codes & names
```

### File Size & Complexity

| File | Lines | Complexity | What It Does |
|------|-------|------------|--------------|
| `PrometheusApp.jsx` | 589 | High | Main app, all features |
| `Auth.jsx` | 320 | Medium | Login/signup |
| `Insights.jsx` | 313 | Medium | Analytics |
| `useSpeechRecognition.js` | 220 | Medium | Voice input |
| `ChatHistoryOptimized.jsx` | ~200 | Medium | Past chats |
| `languages.js` | 60 | Low | Language config |
| `api.js` | 30 | Low | API setup |

---

## 🧩 Component Deep Dive

### What is a Component?

Think of components like **LEGO blocks**. Each block does one thing, and you combine them to build something bigger.

```
COMPONENT = A reusable piece of UI

Example:
┌─────────────────────────────────┐
│          BUTTON                  │  ← This is a component
│  ┌───────────────────────────┐  │
│  │        Click Me           │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘

You can use the same button in many places!
```

### Component Hierarchy (Parent → Child)

```
PrometheusApp (PARENT - controls everything)
│
├── Auth (shown when NOT logged in)
│   ├── Left Panel
│   │   ├── Logo
│   │   ├── Title
│   │   └── Features List
│   └── Right Panel
│       ├── Tab Switcher (Login/Signup)
│       └── Form
│           ├── Input Fields
│           └── Submit Button
│
└── Main App (shown when logged in)
    ├── Header
    │   ├── Logo
    │   ├── Username Display
    │   ├── Language Dropdown
    │   ├── Reset Button
    │   ├── Theme Toggle
    │   └── Logout Button
    │
    ├── Tab Navigation
    │   ├── Chat Tab
    │   ├── History Tab
    │   └── Insights Tab
    │
    └── Content (changes based on active tab)
        │
        ├── [If Chat Tab]
        │   ├── Welcome Screen OR Messages
        │   └── Input Area
        │       ├── Text Input
        │       ├── Mic Button
        │       └── Send Button
        │
        ├── [If History Tab]
        │   └── ChatHistoryOptimized
        │
        └── [If Insights Tab]
            └── Insights
                ├── Investors Tab
                ├── Trends Tab
                └── Policy Tab
```

---

## 🗄️ State Management

### What is State?

**State = Data that can change**

Think of it like variables that React watches. When they change, the screen updates automatically!

```javascript
// Example: A counter
const [count, setCount] = useState(0);

// count = current value (starts at 0)
// setCount = function to change it

// When you click a button:
setCount(count + 1);  // count becomes 1, screen updates!
```

### All State Variables in PrometheusApp

| Variable | What It Stores | Example Values |
|----------|----------------|----------------|
| `messages` | Chat history | `[{role: 'user', content: 'Hi'}, ...]` |
| `input` | What user is typing | `"Top startups in..."` |
| `isRecording` | Is mic on? | `true` / `false` |
| `language` | Selected language | `'en'`, `'hi'`, `'ta'` |
| `theme` | Light or dark mode | `'dark'` / `'light'` |
| `activeTab` | Which tab is open | `'chat'`, `'history'`, `'insights'` |
| `isLoading` | Is AI thinking? | `true` / `false` |
| `authToken` | Login proof | `'eyJhbGciOiJIUzI1...'` |
| `username` | Who's logged in | `'john_doe'` |

### State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         STATE                                    │
│                                                                  │
│  messages: []  →  [{user msg}]  →  [{user}, {ai}]               │
│       ↑              ↑                    ↑                      │
│       │              │                    │                      │
│   Initial      User sends          AI responds                   │
│                                                                  │
│  isLoading: false → true → false                                │
│       ↑              ↑        ↑                                  │
│       │              │        │                                  │
│   Initial     Waiting    Done                                    │
│                                                                  │
│  theme: 'dark' ←──────────────→ 'light'                         │
│                    Toggle                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Styling System

### TailwindCSS Explained

Instead of writing CSS files, we write classes directly in HTML/JSX:

```jsx
// Traditional CSS way:
// styles.css: .button { background: blue; padding: 10px; }
// component: <button className="button">

// TailwindCSS way:
<button className="bg-blue-500 p-4 rounded-lg hover:bg-blue-600">
```

### Common Classes Used

| Class | What It Does | Visual |
|-------|--------------|--------|
| `bg-blue-500` | Blue background | 🟦 |
| `text-white` | White text | ⬜ text |
| `p-4` | Padding all sides | ░░content░░ |
| `rounded-lg` | Rounded corners | ╭──╮ |
| `flex` | Horizontal layout | ▢ ▢ ▢ |
| `grid` | Grid layout | ▢▢▢ |
| `hover:` | On mouse hover | Changes on hover |
| `dark:` | In dark mode | Different in dark |

### Theme Classes

```
DARK MODE                              LIGHT MODE
─────────────────────────────────────────────────────────────

Background:
bg-slate-900                           bg-gray-50
(Very dark blue-gray)                  (Very light gray)

Cards:
bg-white/5                             bg-white/80
(5% white = nearly transparent)        (80% white = mostly solid)

Text:
text-white                             text-gray-900
(White)                                (Almost black)

Borders:
border-white/10                        border-gray-200
(10% white = subtle)                   (Light gray)
```

### Glass Effect (Glassmorphism)

```
┌─────────────────────────────────────┐
│                                     │
│  backdrop-blur-xl                   │  ← Blurs what's behind
│  bg-white/5                         │  ← Slightly white
│  border border-white/10             │  ← Subtle border
│                                     │
│  Result: Frosted glass look! 🧊     │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔌 API Integration

### How Frontend Talks to Backend

```
FRONTEND                              BACKEND
────────                              ───────

   ┌──────────────┐                   ┌──────────────┐
   │  api.post()  │ ────────────────► │  /api/rag    │
   └──────────────┘    HTTP POST      └──────────────┘
                       JSON data
```

### API Client Setup (api.js)

```javascript
import axios from 'axios';

// Create an API client
const api = axios.create({
  baseURL: 'http://localhost:8000',  // Backend URL
  headers: {
    'Content-Type': 'application/json'  // We send JSON
  }
});

// Usage:
// api.post('/api/rag', { query: 'Hello', lang: 'en' })
// api.get('/api/history')
```

### All API Calls Made by Frontend

| Action | Method | Endpoint | Data Sent | Data Received |
|--------|--------|----------|-----------|---------------|
| Login | POST | `/api/login` | username, password | token, username |
| Signup | POST | `/api/signup` | username, email, password | token, username |
| Ask Question | POST | `/api/rag` | query, language | answer, sources |
| Get History | GET | `/api/chat-history` | - | array of chats |
| Save Chat | POST | `/api/save-chat` | query, response, lang | success |
| Get Insights | GET | `/api/insights` | - | analytics data |

### Request/Response Example

```
REQUEST (what frontend sends):
────────────────────────────────
POST http://localhost:8000/api/rag
Headers:
  Content-Type: application/json
  Authorization: Bearer eyJhbGc...
Body:
  {
    "query": "Top 10 fintech startups",
    "language": "en"
  }

RESPONSE (what backend returns):
────────────────────────────────
Status: 200 OK
Body:
  {
    "answer": "Here are the top 10 fintech startups:\n1. Paytm...",
    "sources": [...],
    "language": "en"
  }
```

---

## 🎤 Voice Input System

### How Voice Input Works

```
┌────────────────────────────────────────────────────────────────┐
│                    WEB SPEECH API                               │
│                                                                 │
│  Built into Chrome/Edge browsers (not available in all!)        │
│                                                                 │
│  1. Browser captures audio from microphone                      │
│  2. Sends to Google's servers for processing                    │
│  3. Returns recognized text                                     │
│                                                                 │
│  ⚠️ Requires:                                                   │
│     • Chrome or Edge browser                                    │
│     • Internet connection (uses Google servers)                 │
│     • Microphone permission                                     │
└────────────────────────────────────────────────────────────────┘
```

### Language Support

| Language | Code Sent to API | Example Recognition |
|----------|------------------|---------------------|
| English | `en-US` | "top startups" |
| Hindi | `hi-IN` | "टॉप स्टार्टअप्स" |
| Tamil | `ta-IN` | "முதல் நிறுவனங்கள்" |
| Telugu | `te-IN` | "టాప్ స్టార్టప్స్" |
| Kannada | `kn-IN` | "ಟಾಪ್ ಸ್ಟಾರ್ಟ್‌ಅಪ್ಸ್" |
| Marathi | `mr-IN` | "टॉप स्टार्टअप्स" |
| Gujarati | `gu-IN` | "ટોપ સ્ટાર્ટઅપ્સ" |
| Bengali | `bn-IN` | "টপ স্টার্টআপস" |

### Error Handling

| Error | What Happened | What User Sees |
|-------|---------------|----------------|
| `no-speech` | User didn't speak | (silently restarts) |
| `audio-capture` | No mic found | "No microphone found" |
| `not-allowed` | Permission denied | "Click 🔒 to allow" |
| `network` | No internet | "Requires internet" |

---

## 🌓 Theme System

### How Theme Toggle Works

```javascript
// State
const [theme, setTheme] = useState('dark');

// Toggle function
onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}

// Dynamic classes based on theme
const cardClass = theme === 'dark'
  ? 'bg-white/5 text-white'      // Dark mode styles
  : 'bg-white text-gray-900';    // Light mode styles
```

### All Theme-Aware Variables

```javascript
// These change based on theme:

const glassCard = theme === 'dark' 
  ? 'bg-white/5 backdrop-blur-xl border border-white/10' 
  : 'bg-white/80 backdrop-blur-xl border border-gray-200 shadow-lg';

const textMain = theme === 'dark' ? 'text-white' : 'text-gray-900';

const textMuted = theme === 'dark' ? 'text-gray-400' : 'text-gray-600';

const textSubtle = theme === 'dark' ? 'text-gray-300' : 'text-gray-700';

const inputBg = theme === 'dark' 
  ? 'bg-transparent text-white placeholder-gray-400' 
  : 'bg-transparent text-gray-900 placeholder-gray-500';

const menuHover = theme === 'dark' 
  ? 'hover:bg-cyan-500/20' 
  : 'hover:bg-cyan-100';
```

### Components That Support Theming

| Component | Theme Support | Passed Via |
|-----------|---------------|------------|
| PrometheusApp | ✅ Full | Internal state |
| Header | ✅ Full | Props from parent |
| Chat Messages | ✅ Full | Dynamic classes |
| Insights | ✅ Full | `theme` prop |
| Auth | ⚠️ Dark only | Hardcoded |
| ChatHistory | ⚠️ Partial | Needs update |

---

## 🌍 Multilingual Support

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTILINGUAL FLOW                             │
│                                                                  │
│  1. User selects language (e.g., Hindi)                         │
│                                                                  │
│  2. UI text changes to Hindi:                                   │
│     • "Chat" → "चैट"                                            │
│     • "History" → "इतिहास"                                       │
│     • Placeholder → "अपना सवाल लिखें..."                         │
│                                                                  │
│  3. Voice input uses Hindi speech recognition (hi-IN)           │
│                                                                  │
│  4. Query sent with lang='hi'                                   │
│                                                                  │
│  5. Backend responds in Hindi                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Translation Files Structure

```javascript
// translations.js
export const translations = {
  en: {
    appName: 'Prometheus',
    chat: 'Chat',
    history: 'History',
    insights: 'Insights',
    placeholder: 'Type your question...',
    // ... more
  },
  hi: {
    appName: 'प्रोमेथियस',
    chat: 'चैट',
    history: 'इतिहास',
    insights: 'अंतर्दृष्टि',
    placeholder: 'अपना सवाल लिखें...',
    // ... more
  },
  // ... other languages
};

// Usage:
const t = translations[language];  // Get current language
<h1>{t.appName}</h1>               // Shows "Prometheus" or "प्रोमेथियस"
```

---

## 📊 Data Flow Examples

### Example 1: User Asks a Question

```
TIME    ACTION                              STATE CHANGES
────    ──────                              ─────────────

0ms     User types "Top startups"           input: "Top startups"

1s      User clicks Send button             
        ↓
        handleSend() called
        ↓
        1. Add user message                 messages: [..., {role:'user', content:'Top startups'}]
        2. Set loading                      isLoading: true
        3. Call API                         (waiting...)

2s      API responds
        ↓
        1. Add AI message                   messages: [..., {role:'assistant', content:'Here are...'}]
        2. Clear loading                    isLoading: false
        3. Clear input                      input: ""
```

### Example 2: User Changes Language

```
TIME    ACTION                              STATE CHANGES
────    ──────                              ─────────────

0ms     User clicks language dropdown       showLanguageMenu: true

500ms   User clicks "Hindi"                 
        ↓
        1. Set language                     language: 'hi'
        2. Close dropdown                   showLanguageMenu: false
        3. (Automatic) UI text changes      t = translations['hi']
        4. (Automatic) Speech lang changes  recognition.lang = 'hi-IN'
```

### Example 3: Theme Toggle

```
TIME    ACTION                              STATE CHANGES
────    ──────                              ─────────────

0ms     Current theme: dark                 theme: 'dark'
        User clicks sun icon ☀️
        ↓
        setTheme('light')                   theme: 'light'
        ↓
        (Automatic) All components re-render with light colors
```

---

## ❓ Common Questions

### Q: Why doesn't voice work in Brave browser?
**A:** Brave blocks Google's speech recognition servers for privacy. Use Chrome or Edge instead.

### Q: How do I add a new language?
**A:** 
1. Add to `LANGUAGES` array in `constants/languages.js`
2. Add speech code to `SPEECH_LANG_MAP`
3. Add translations to `translations.js`
4. Add welcome message to `WELCOME_MESSAGES`

### Q: How do I change the API URL for production?
**A:** Update `baseURL` in `api.js` or use environment variable `VITE_API_URL`.

### Q: Why is the page blank after login?
**A:** Usually means the backend isn't running. Check if `http://localhost:8000/health` responds.

### Q: How do I add a new tab?
**A:**
1. Add tab button in `PrometheusApp.jsx` (Tab Navigation section)
2. Add new component for tab content
3. Add conditional render in Content Area

### Q: How do I change colors?
**A:** 
- For specific element: Change TailwindCSS classes directly
- For theme colors: Update the theme variables (`glassCard`, `textMain`, etc.)
- For global colors: Update `tailwind.config.js`

### Q: What happens if the API call fails?
**A:** The `catch` block shows an error message to the user. Check Network tab in DevTools for details.

---

## 📝 Quick Reference

### File → Purpose

| File | One-Line Purpose |
|------|------------------|
| `main.jsx` | Starts the React app |
| `api.js` | Configures API calls |
| `PrometheusApp.jsx` | Main app with all features |
| `Auth.jsx` | Login and signup |
| `Insights.jsx` | Analytics dashboard |
| `useSpeechRecognition.js` | Voice input logic |
| `languages.js` | Language configuration |
| `translations.js` | UI text in 8 languages |

### State → What It Controls

| State | Controls |
|-------|----------|
| `messages` | Chat bubble display |
| `isLoading` | Loading spinner |
| `theme` | Dark/light colors |
| `language` | UI text + speech |
| `activeTab` | Which page shows |
| `authToken` | Login status |

### Component → Where It Appears

| Component | Location |
|-----------|----------|
| Auth | Full page (logged out) |
| Header | Top of main app |
| TabButton | Below header |
| Chat | Main content (chat tab) |
| Insights | Main content (insights tab) |
| ChatHistory | Main content (history tab) |

---

## 🎯 Summary

This frontend is built with:

1. **React** - Component-based UI
2. **Vite** - Fast development
3. **TailwindCSS** - Utility-first styling
4. **Framer Motion** - Smooth animations
5. **React Query** - Smart data fetching
6. **Web Speech API** - Voice input

Key features:

- 🌓 Dark/Light theme toggle
- 🌍 8 language support
- 🎤 Voice input
- 💬 Real-time chat
- 📊 Analytics dashboard
- 🔐 JWT authentication

---

*This documentation should answer most questions about the frontend. For backend details, see the backend documentation.*
