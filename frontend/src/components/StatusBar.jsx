import React from 'react';
import { Mail, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function StatusBar({ status, stats }) {
  const getStatusIcon = () => {
    if (status.status === 'ok') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status.status === 'degraded') return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  return (
    <div className="bg-white border-b px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Mail className="w-5 h-5 text-blue-500" />
          <h1 className="text-xl font-semibold">MailAgent</h1>
        </div>
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className="text-sm text-gray-600">
            {status.status === 'ok' ? 'All systems operational' : status.error || 'System degraded'}
          </span>
        </div>
      </div>
      {stats && (
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>{stats.total_emails || 0} total emails</span>
          <span>{stats.unread_emails || 0} unread</span>
          <span>{stats.high_importance || 0} high priority</span>
          {status.model && <span className="text-gray-500">Model: {status.model}</span>}
        </div>
      )}
    </div>
  );
}
