import React from 'react';
import { User, Clock, FileText, RefreshCw, Loader2, Sparkles, Mail } from 'lucide-react';

export default function EmailDetail({ email, onGenerateResponses, generating }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
  };

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

  if (!email) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500 bg-dark-900">
        <div className="text-center">
          <Mail className="w-16 h-16 mx-auto mb-4 text-dark-700" />
          <p className="text-gray-400">Select an email to view details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-dark-900 overflow-hidden">
      {/* Fixed Header */}
      <div className="flex-shrink-0 bg-dark-800 border-b border-dark-700">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1 min-w-0">
              <h2 className="text-xl font-semibold text-white mb-3 leading-tight">
                {email.subject || '(no subject)'}
              </h2>

              <div className="flex items-center gap-2 flex-wrap">
                {email.importance && (
                  <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${getImportanceBadge(email.importance)}`}>
                    {email.importance}
                  </span>
                )}
                {email.category && (
                  <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${getCategoryBadge(email.category)}`}>
                    {email.category}
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={() => onGenerateResponses && onGenerateResponses(email)}
              disabled={generating}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 flex-shrink-0 ml-4 ${
                generating
                  ? 'bg-dark-700 text-gray-400 cursor-not-allowed'
                  : 'bg-accent-blue hover:bg-accent-blueHover text-white shadow-glow'
              }`}
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate AI Responses
                </>
              )}
            </button>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-accent-blue to-blue-600 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <span className="text-gray-300">{email.from_addr}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{formatDate(email.date)}</span>
            </div>
            {email.has_attachments && (
              <div className="flex items-center gap-2 px-2 py-1 bg-dark-700 rounded-lg">
                <FileText className="w-4 h-4 text-accent-blue" />
                <span>Has attachments</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          {email.ai_summary && (
            <div className="mb-6 p-4 bg-accent-blue/10 border border-accent-blue/30 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-accent-blue" />
                <h3 className="text-sm font-semibold text-accent-blue">AI Summary</h3>
              </div>
              <p className="text-sm text-gray-300 leading-relaxed">{email.ai_summary}</p>
            </div>
          )}

          <div className="prose prose-invert prose-sm max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-gray-300">
              {email.body_text || '(no content)'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
