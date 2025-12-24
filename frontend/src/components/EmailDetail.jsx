import React, { useState } from 'react';
import { User, Clock, FileText, RefreshCw } from 'lucide-react';

export default function EmailDetail({ email, onGenerateResponses }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
  };

  const getImportanceBadge = (importance) => {
    const colors = {
      high: 'bg-red-100 text-red-700',
      medium: 'bg-yellow-100 text-yellow-700',
      low: 'bg-gray-100 text-gray-700',
    };
    return colors[importance] || colors.low;
  };

  const getCategoryBadge = (category) => {
    const colors = {
      professionnel: 'bg-blue-100 text-blue-700',
      personnel: 'bg-green-100 text-green-700',
      newsletter: 'bg-purple-100 text-purple-700',
      notification: 'bg-gray-100 text-gray-700',
      urgent: 'bg-red-100 text-red-700',
      commercial: 'bg-orange-100 text-orange-700',
      administratif: 'bg-indigo-100 text-indigo-700',
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  if (!email) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <p>Select an email to view details</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-6 border-b bg-gray-50">
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-xl font-semibold">{email.subject || '(no subject)'}</h2>
          <button
            onClick={() => onGenerateResponses && onGenerateResponses(email)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Generate Responses
          </button>
        </div>

        <div className="flex items-center gap-2 mb-4">
          {email.importance && (
            <span className={`text-xs px-2 py-1 rounded-full ${getImportanceBadge(email.importance)}`}>
              {email.importance} priority
            </span>
          )}
          {email.category && (
            <span className={`text-xs px-2 py-1 rounded-full ${getCategoryBadge(email.category)}`}>
              {email.category}
            </span>
          )}
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4" />
            <span className="font-medium">{email.from_addr}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span>{formatDate(email.date)}</span>
          </div>
          {email.has_attachments && (
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              <span>Has attachments</span>
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        {email.ai_summary && (
          <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
            <h3 className="text-sm font-semibold text-blue-700 mb-2">AI Summary</h3>
            <p className="text-sm text-blue-900">{email.ai_summary}</p>
          </div>
        )}

        <div className="prose max-w-none">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
            {email.body_text || '(no content)'}
          </pre>
        </div>
      </div>
    </div>
  );
}
