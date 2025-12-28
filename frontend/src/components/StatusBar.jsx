import React from 'react';
import { Mail, CheckCircle, XCircle, AlertCircle, Database, Cpu } from 'lucide-react';

export default function StatusBar({ status, stats }) {
  const getStatusIcon = () => {
    if (status.status === 'ok') return <CheckCircle className="w-4 h-4 text-accent-green" />;
    if (status.status === 'degraded') return <AlertCircle className="w-4 h-4 text-accent-yellow" />;
    return <XCircle className="w-4 h-4 text-accent-red" />;
  };

  const getStatusText = () => {
    if (status.status === 'ok') return 'All systems operational';
    if (status.status === 'loading') return 'Initializing...';
    return status.error || 'System degraded';
  };

  return (
    <div className="bg-dark-900 border-b border-dark-700 px-6 py-3 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-accent-blue to-blue-600 p-2 rounded-lg shadow-glow">
            <Mail className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">MailAgent</h1>
            <p className="text-xs text-gray-500">AI-Powered Email Assistant</p>
          </div>
        </div>

        <div className="h-8 w-px bg-dark-700" />

        <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-800 rounded-lg border border-dark-700">
          {getStatusIcon()}
          <span className="text-sm text-gray-300 font-medium">
            {getStatusText()}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium ${status.gmail_connected ? 'bg-dark-800 text-accent-green border border-accent-green/30' : 'bg-dark-800 text-accent-red border border-accent-red/30'}`}>
            <Mail className="w-3.5 h-3.5" />
            Gmail
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium ${status.llm_connected ? 'bg-dark-800 text-accent-green border border-accent-green/30' : 'bg-dark-800 text-accent-red border border-accent-red/30'}`}>
            <Cpu className="w-3.5 h-3.5" />
            LLM
          </div>
        </div>
      </div>

      {stats && (
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-800 rounded-lg border border-dark-700">
              <Database className="w-4 h-4 text-accent-blue" />
              <span className="text-gray-400">{stats.total_emails || 0}</span>
              <span className="text-gray-500">total</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-800 rounded-lg border border-dark-700">
              <Mail className="w-4 h-4 text-accent-blue" />
              <span className="text-accent-blue font-semibold">{stats.unread_emails || 0}</span>
              <span className="text-gray-500">unread</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-800 rounded-lg border border-accent-red/30">
              <AlertCircle className="w-4 h-4 text-accent-red" />
              <span className="text-accent-red font-semibold">{stats.high_importance || 0}</span>
              <span className="text-gray-500">urgent</span>
            </div>
          </div>
          {status.model && (
            <div className="px-3 py-1.5 bg-accent-purple/10 border border-accent-purple/30 rounded-lg">
              <span className="text-xs text-accent-purple font-medium">{status.model}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
