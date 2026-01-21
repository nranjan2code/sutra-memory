import { NavLink } from 'react-router-dom';
import { MessageSquare, BookOpen, BarChart3, Settings, Brain } from 'lucide-react';
import { useUIStore } from '../store';
import { clsx } from 'clsx';

const navigation = [
  { name: 'Chat', to: '/chat', icon: MessageSquare },
  { name: 'Knowledge', to: '/knowledge', icon: BookOpen },
  { name: 'Analytics', to: '/analytics', icon: BarChart3 },
  { name: 'Settings', to: '/settings', icon: Settings },
];

export function Sidebar() {
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);

  if (!sidebarOpen) return null;

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-dark-700">
        <Brain className="w-8 h-8 text-primary-500 mr-3" />
        <div>
          <h1 className="text-xl font-bold text-white">Sutra</h1>
          <p className="text-xs text-dark-400">Desktop Edition</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all',
                isActive
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/50'
                  : 'text-dark-300 hover:text-white hover:bg-dark-800'
              )
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-dark-700">
        <div className="flex items-center justify-between text-xs text-dark-400">
          <span>Version 1.0.0</span>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span>Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
