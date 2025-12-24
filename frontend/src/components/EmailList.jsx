import React from 'react';
import { Mail, Clock, AlertTriangle, FileText } from 'lucide-react';

export default function EmailList({ emails, selectedEmail, onSelectEmail, onFilterChange, filters }) {
  const getImportanceColor = (importance) => {
    switch (importance) {
      case 'high': return 'text-red-500 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-gray-500 bg-gray-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      professionnel: 'text-blue-600 bg-blue-50',
      personnel: 'text-green-600 bg-green-50',
      newsletter: 'text-purple-600 bg-purple-50',
      notification: 'text-gray-600 bg-gray-50',
      urgent: 'text-red-600 bg-red-50',
      commercial: 'text-orange-600 bg-orange-50',
      administratif: 'text-indigo-600 bg-indigo-50',
    };
    return colors[category] || 'text-gray-600 bg-gray-50';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = diffMs / (1000 * 60 * 60);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${Math.floor(diffHours)}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <div className="flex-1 overflow-y-auto border-r">
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Inbox</h2>
        <div className="flex flex-wrap gap-2">
          <select
            value={filters.status || 'all'}
            onChange={(e) => onFilterChange('status', e.target.value === 'all' ? null : e.target.value)}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="all">All Status</option>
            <option value="unread">Unread</option>
            <option value="read">Read</option>
          </select>
          <select
            value={filters.importance || 'all'}
            onChange={(e) => onFilterChange('importance', e.target.value === 'all' ? null : e.target.value)}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="all">All Priority</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={filters.category || 'all'}
            onChange={(e) => onFilterChange('category', e.target.value === 'all' ? null : e.target.value)}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="all">All Categories</option>
            <option value="professionnel">Professionnel</option>
            <option value="personnel">Personnel</option>
            <option value="newsletter">Newsletter</option>
            <option value="notification">Notification</option>
            <option value="urgent">Urgent</option>
            <option value="commercial">Commercial</option>
          </select>
        </div>
      </div>

      <div className="divide-y">
        {emails.map((email) => (
          <div
            key={email.id}
            onClick={() => onSelectEmail(email)}
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
              selectedEmail?.id === email.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
            } ${email.status === 'unread' ? 'font-medium' : ''}`}
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm truncate">{email.from_addr}</p>
                <p className="text-sm font-medium truncate">{email.subject || '(no subject)'}</p>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500 shrink-0">
                <Clock className="w-3 h-3" />
                {formatDate(email.date)}
              </div>
            </div>

            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
              {email.ai_summary || email.body_text?.substring(0, 150) || ''}
            </p>

            <div className="flex items-center gap-2 flex-wrap">
              {email.importance && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${getImportanceColor(email.importance)}`}>
                  {email.importance}
                </span>
              )}
              {email.category && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${getCategoryColor(email.category)}`}>
                  {email.category}
                </span>
              )}
              {email.has_attachments && (
                <FileText className="w-4 h-4 text-gray-400" />
              )}
            </div>
          </div>
        ))}
      </div>

      {emails.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-gray-500">
          <Mail className="w-12 h-12 mb-2" />
          <p>No emails found</p>
          <p className="text-sm">Click "Sync" to fetch your emails</p>
        </div>
      )}
    </div>
  );
}
