import { useChatStore } from '../store';
import { Trash2 } from 'lucide-react';

export function SettingsPage() {
  const clearMessages = useChatStore((state) => state.clearMessages);
  const messageCount = useChatStore((state) => state.messages.length);

  return (
    <div className="p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Settings</h1>
          <p className="text-dark-400 mt-1">Manage your Sutra Desktop preferences</p>
        </div>

        <div className="bg-dark-800 border border-dark-700 rounded-lg divide-y divide-dark-700">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Chat History</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-dark-300">Clear all chat messages</p>
                <p className="text-sm text-dark-500 mt-1">
                  {messageCount} message{messageCount !== 1 ? 's' : ''} stored
                </p>
              </div>
              <button
                onClick={clearMessages}
                disabled={messageCount === 0}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Clear History
              </button>
            </div>
          </div>

          <div className="p-6">
            <h2 className="text-lg font-semibold text-white mb-4">About</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-dark-400">Version</span>
                <span className="text-white font-medium">1.0.0</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-dark-400">Edition</span>
                <span className="text-white font-medium">Desktop Edition</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-dark-400">API Endpoint</span>
                <span className="text-white font-mono text-xs">localhost:8000</span>
              </div>
            </div>
          </div>

          <div className="p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Resources</h2>
            <div className="space-y-2">
              <a
                href="https://github.com/sutra-ai/sutra"
                target="_blank"
                rel="noopener noreferrer"
                className="block text-primary-400 hover:text-primary-300 transition-colors"
              >
                Documentation →
              </a>
              <a
                href="https://github.com/sutra-ai/sutra/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="block text-primary-400 hover:text-primary-300 transition-colors"
              >
                Report an Issue →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
