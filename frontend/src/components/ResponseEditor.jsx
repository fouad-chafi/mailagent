import React, { useState } from 'react';
import { Send, Edit2, RotateCcw } from 'lucide-react';

export default function ResponseEditor({ responses, email, onSend, onImprove }) {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [isSending, setIsSending] = useState(false);

  const getToneLabel = (tone) => {
    const labels = {
      formal: 'Formal',
      casual: 'Casual',
      neutral: 'Neutral',
    };
    return labels[tone] || tone;
  };

  const getToneColor = (tone) => {
    const colors = {
      formal: 'border-blue-300 bg-blue-50',
      casual: 'border-green-300 bg-green-50',
      neutral: 'border-gray-300 bg-gray-50',
    };
    return colors[tone] || colors.neutral;
  };

  const handleSend = async (response) => {
    setIsSending(true);
    try {
      await onSend({
        to: email.from_addr,
        subject: `Re: ${email.subject}`,
        body: response.content,
        in_reply_to: email.id,
      });
    } finally {
      setIsSending(false);
    }
  };

  if (!responses || responses.length === 0) {
    return (
      <div className="p-6 text-center text-gray-500">
        <p>No responses generated yet</p>
      </div>
    );
  }

  return (
    <div className="p-6 border-t bg-gray-50">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
        Suggested Responses
      </h3>

      <div className="space-y-4">
        {responses.map((response, index) => (
          <div
            key={response.id || index}
            className={`border-2 rounded-lg p-4 transition-all ${getToneColor(response.tone)}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase">
                  {getToneLabel(response.tone)}
                </span>
                {response.sent && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                    Sent
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedIndex(selectedIndex === index ? null : index)}
                  className="p-1 hover:bg-white rounded transition-colors"
                  title="Edit"
                >
                  <Edit2 className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>

            <div className="mb-3">
              {selectedIndex === index ? (
                <textarea
                  value={response.content}
                  onChange={(e) => {
                    response.content = e.target.value;
                  }}
                  className="w-full p-3 border rounded-lg text-sm min-h-[150px] resize-y"
                />
              ) : (
                <p className="text-sm whitespace-pre-wrap">{response.content}</p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleSend(response)}
                disabled={isSending || response.sent}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
              >
                <Send className="w-4 h-4" />
                {isSending ? 'Sending...' : response.sent ? 'Sent' : 'Send'}
              </button>
              <button
                onClick={() => onImprove(response.content)}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors text-sm"
              >
                <RotateCcw className="w-4 h-4" />
                Improve
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
