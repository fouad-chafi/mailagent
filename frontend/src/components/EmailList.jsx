import React from 'react';
import { Mail, Clock, FileText, Search, Inbox } from 'lucide-react';

export default function EmailList({ emails, selectedEmail, onSelectEmail, onFilterChange, filters }) {
  const getImportanceBadge = (importance) => {
    const badges = {
      high: 'bg-accent-red/20 text-accent-red border-accent-red/40',
      medium: 'bg-accent-yellow/20 text-accent-yellow border-accent-yellow/40',
      low: 'bg-dark-700 text-gray-400 border-dark-600',
    };
    return badges[importance] || badges.low;
  };

  const getCategoryBadge = (category) => {
    const badges = {
      professionnel: 'bg-accent-blue/20 text-accent-blue border-accent-blue/40',
      personnel: 'bg-accent-green/20 text-accent-green border-accent-green/40',
      newsletter: 'bg-accent-purple/20 text-accent-purple border-accent-purple/40',
      notification: 'bg-dark-700 text-gray-400 border-dark-600',
      urgent: 'bg-accent-red/20 text-accent-red border-accent-red/40',
      commercial: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
      administratif: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40',
    };
    return badges[category] || 'bg-dark-700 text-gray-400 border-dark-600';
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
    <div className="h-full flex flex-col bg-dark-900">
      {/* Header */}
      <div className="flex-shrink-0 bg-dark-900 border-b border-dark-700">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Inbox className="w-5 h-5 text-accent-blue" />
              <h2 className="text-lg font-semibold text-white">Inbox</h2>
              <span className="px-2 py-0.5 bg-accent-blue/20 text-accent-blue text-xs font-medium rounded-full">
                {emails.length}
              </span>
            </div>
            <button className="p-2 hover:bg-dark-800 rounded-lg transition-colors">
              <Search className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-2 overflow-x-auto pb-1">
            <select
              value={filters.status || 'all'}
              onChange={(e) => onFilterChange('status', e.target.value === 'all' ? null : e.target.value)}
              className="input text-xs px-3 py-1.5 min-w-[100px]"
            >
              <option value="all">All Status</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
            </select>
            <select
              value={filters.importance || 'all'}
              onChange={(e) => onFilterChange('importance', e.target.value === 'all' ? null : e.target.value)}
              className="input text-xs px-3 py-1.5 min-w-[100px]"
            >
              <option value="all">All Priority</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <select
              value={filters.category || 'all'}
              onChange={(e) => onFilterChange('category', e.target.value === 'all' ? null : e.target.value)}
              className="input text-xs px-3 py-1.5 min-w-[120px]"
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
      </div>

      {/* Scrollable Email List */}
      <div className="flex-1 overflow-y-auto divide-y divide-dark-800">
        {emails.map((email) => (
          <div
            key={email.id}
            onClick={() => onSelectEmail(email)}
            className={`group cursor-pointer transition-all duration-200 ${
              selectedEmail?.id === email.id
                ? 'bg-accent-blue/10 border-l-2 border-accent-blue'
                : 'hover:bg-dark-800 border-l-2 border-transparent'
            }`}
          >
            <div className="p-4">
              <div className="flex items-start gap-3 mb-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className={`text-sm truncate ${email.status === 'unread' ? 'font-semibold text-white' : 'text-gray-300'}`}>
                      {email.from_addr}
                    </p>
                    {email.status === 'unread' && (
                      <span className="w-2 h-2 bg-accent-blue rounded-full flex-shrink-0" />
                    )}
                  </div>
                  <p className={`text-sm truncate ${email.status === 'unread' ? 'font-medium text-gray-200' : 'text-gray-400'}`}>
                    {email.subject || '(no subject)'}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-gray-500 flex-shrink-0">
                  <Clock className="w-3 h-3" />
                  <span>{formatDate(email.date)}</span>
                </div>
              </div>

              {email.ai_summary && (
                <p className="text-xs text-gray-500 line-clamp-2 mb-2 pl-1 border-l-2 border-dark-700">
                  {email.ai_summary}
                </p>
              )}

              <div className="flex items-center gap-2 flex-wrap">
                {email.importance && (
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${getImportanceBadge(email.importance)}`}>
                    {email.importance}
                  </span>
                )}
                {email.category && (
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${getCategoryBadge(email.category)}`}>
                    {email.category}
                  </span>
                )}
                {email.has_attachments && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <FileText className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {emails.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 px-4">
          <div className="bg-dark-800 p-4 rounded-full mb-4">
            <Mail className="w-12 h-12 text-gray-600" />
          </div>
          <p className="text-gray-400 font-medium">No emails found</p>
          <p className="text-sm text-gray-600 mt-1">Click "Sync" to fetch your emails</p>
        </div>
      )}
    </div>
  );
}
