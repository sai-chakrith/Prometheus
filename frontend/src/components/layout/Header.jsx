/**
 * App header component
 */

import { Flame, Globe } from 'lucide-react';
import { LANGUAGES } from '../../constants/languages';

export function Header({ selectedLang, onLangChange }) {
  return (
    <header className="bg-gray-800/50 backdrop-blur border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg">
            <Flame className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
              PROMETHEUS
            </h1>
            <p className="text-xs text-gray-400">Multilingual Startup Funding RAG</p>
          </div>
        </div>

        {/* Language Selector */}
        <LanguageSelector 
          selectedLang={selectedLang} 
          onLangChange={onLangChange} 
        />
      </div>
    </header>
  );
}

export function LanguageSelector({ selectedLang, onLangChange }) {
  return (
    <div className="flex items-center gap-3">
      <Globe className="w-5 h-5 text-gray-400" />
      <select
        value={selectedLang}
        onChange={(e) => onLangChange(e.target.value)}
        className="bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default Header;
