/**
 * App footer component
 */

export function Footer() {
  return (
    <footer className="bg-gray-800/50 backdrop-blur border-t border-gray-700 px-6 py-3">
      <div className="flex items-center justify-between text-xs text-gray-400">
        <p>5-Day Hackathon MVP • Voice-Enabled Multilingual RAG</p>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <span>Backend: 127.0.0.1:8000</span>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
