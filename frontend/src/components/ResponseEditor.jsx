import React, { useState } from 'react';
import { Send, Edit2, RotateCcw, Loader2, Sparkles, Check, Wand2 } from 'lucide-react';

export default function ResponseEditor({ responses, email, onSend, onImprove, generating }) {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [editedContents, setEditedContents] = useState({});

  const getToneLabel = (tone) => {
    const labels = {
      formal: 'Formal',
      casual: 'Casual',
      neutral: 'Neutral',
    };
    return labels[tone] || tone;
  };

  const getToneStyle = (tone) => {
    const styles = {
      formal: {
        border: 'border-accent-blue/40',
        bg: 'bg-accent-blue/5',
        accent: 'text-accent-blue',
        badge: 'bg-accent-blue/20 text-accent-blue border-accent-blue/40',
      },
      casual: {
        border: 'border-accent-green/40',
        bg: 'bg-accent-green/5',
        accent: 'text-accent-green',
        badge: 'bg-accent-green/20 text-accent-green border-accent-green/40',
      },
      neutral: {
        border: 'border-dark-600',
        bg: 'bg-dark-800',
        accent: 'text-gray-400',
        badge: 'bg-dark-700 text-gray-400 border-dark-600',
      },
    };
    return styles[tone] || styles.neutral;
  };

  const getContent = (response, index) => {
    return editedContents[index] !== undefined ? editedContents[index] : response.content;
  };

  const handleContentChange = (index, newContent) => {
    setEditedContents(prev => ({
      ...prev,
      [index]: newContent
    }));
  };

  const handleSend = async (response, index) => {
    setIsSending(true);
    try {
      await onSend({
        to: email.from_addr,
        subject: `Re: ${email.subject}`,
        body: getContent(response, index),
        in_reply_to: email.id,
      });
    } finally {
      setIsSending(false);
    }
  };

  if (!responses || responses.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-dark-900 p-6">
        {generating ? (
          <div className="flex flex-col items-center gap-3 text-gray-400">
            <div className="relative">
              <Loader2 className="w-8 h-8 animate-spin text-accent-blue" />
              <Sparkles className="w-4 h-4 text-accent-blue absolute -top-1 -right-1" />
            </div>
            <p className="text-sm font-medium">Generating AI responses...</p>
            <p className="text-xs text-gray-600">This may take a moment</p>
          </div>
        ) : (
          <div className="text-center">
            <div className="w-16 h-16 bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Wand2 className="w-8 h-8 text-dark-700" />
            </div>
            <p className="text-gray-400 font-medium">No responses generated yet</p>
            <p className="text-xs text-gray-600 mt-1">Click "Generate AI Responses" to create drafts</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-dark-900 overflow-hidden">
      {/* Fixed Header */}
      <div className="flex-shrink-0 bg-dark-800 border-b border-dark-700 px-6 py-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-accent-blue" />
          <h3 className="text-sm font-semibold text-white uppercase tracking-wide">
            AI-Generated Responses
          </h3>
          <span className="px-2 py-0.5 bg-accent-blue/20 text-accent-blue text-xs font-medium rounded-full">
            {responses.length}
          </span>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4">
          {responses.map((response, index) => {
            const currentContent = getContent(response, index);
            const toneStyle = getToneStyle(response.tone);

            return (
              <div
                key={response.id || index}
                className={`border-2 rounded-xl p-4 transition-all duration-200 ${toneStyle.border} ${toneStyle.bg}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-semibold uppercase px-2.5 py-1 rounded-lg border ${toneStyle.badge}`}>
                      {getToneLabel(response.tone)}
                    </span>
                    {response.sent && (
                      <span className="flex items-center gap-1 text-xs bg-accent-green/20 text-accent-green px-2.5 py-1 rounded-lg border border-accent-green/40">
                        <Check className="w-3 h-3" />
                        Sent
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setSelectedIndex(selectedIndex === index ? null : index)}
                      className={`p-2 rounded-lg transition-all ${
                        selectedIndex === index
                          ? 'bg-accent-blue text-white'
                          : 'hover:bg-dark-700 text-gray-400'
                      }`}
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  {selectedIndex === index ? (
                    <textarea
                      value={currentContent}
                      onChange={(e) => handleContentChange(index, e.target.value)}
                      className="w-full p-4 bg-dark-900 border border-dark-700 rounded-lg text-sm text-gray-200 min-h-[180px] resize-y focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent placeholder-gray-600"
                      placeholder="Type your response here..."
                    />
                  ) : (
                    <div className="p-4 bg-dark-900/50 rounded-lg text-sm text-gray-300 whitespace-pre-wrap leading-relaxed max-h-[200px] overflow-y-auto">
                      {currentContent}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSend(response, index)}
                    disabled={isSending || response.sent}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 text-sm ${
                      isSending || response.sent
                        ? 'bg-dark-700 text-gray-500 cursor-not-allowed'
                        : 'bg-accent-blue hover:bg-accent-blueHover text-white shadow-glow'
                    }`}
                  >
                    <Send className="w-4 h-4" />
                    {isSending ? 'Sending...' : response.sent ? 'Sent' : 'Send Response'}
                  </button>
                  <button
                    onClick={() => onImprove(currentContent)}
                    disabled={isSending}
                    className="flex items-center gap-2 px-4 py-2.5 bg-dark-700 hover:bg-dark-600 text-gray-300 rounded-lg font-medium transition-all duration-200 text-sm border border-dark-600 disabled:opacity-50"
                  >
                    <Wand2 className="w-4 h-4" />
                    Improve with AI
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
