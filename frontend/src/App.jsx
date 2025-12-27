import React, { useState, useEffect } from 'react';
import { RefreshCw, Download, Loader2 } from 'lucide-react';
import StatusBar from './components/StatusBar';
import EmailList from './components/EmailList';
import EmailDetail from './components/EmailDetail';
import ResponseEditor from './components/ResponseEditor';
import { apiService } from './services/api';

function App() {
  const [status, setStatus] = useState({ status: 'loading' });
  const [stats, setStats] = useState(null);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    loadStatus();
    loadStats();
    loadEmails();
  }, []);

  useEffect(() => {
    loadEmails();
  }, [filters]);

  const loadStatus = async () => {
    try {
      const data = await apiService.getStatus();
      setStatus(data);
    } catch (error) {
      setStatus({ status: 'error', error: error.message });
    }
  };

  const loadStats = async () => {
    try {
      const data = await apiService.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadEmails = async () => {
    setLoading(true);
    try {
      const data = await apiService.listEmails(filters);
      setEmails(data.emails || []);
    } catch (error) {
      console.error('Failed to load emails:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await apiService.syncEmails(50, true);
      await loadEmails();
      await loadStats();
    } catch (error) {
      console.error('Sync failed:', error);
      alert('Sync failed: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  const handleHistoricalSync = async () => {
    const days = prompt('Sync how many days back?', '30');
    if (days && !isNaN(days)) {
      try {
        await apiService.syncHistorical(parseInt(days));
        alert('Historical sync started in background');
      } catch (error) {
        alert('Failed to start historical sync: ' + error.message);
      }
    }
  };

  const handleSelectEmail = async (email) => {
    setSelectedEmail(email);
    setResponses([]);
    try {
      const data = await apiService.getResponses(email.id);
      setResponses(data.responses || []);
    } catch (error) {
      console.error('Failed to load responses:', error);
    }
  };

  const handleGenerateResponses = async (email) => {
    setGenerating(true);
    try {
      const data = await apiService.getResponses(email.id);
      setResponses(data.responses || []);
    } catch (error) {
      console.error('Failed to generate responses:', error);
      alert('Failed to generate responses: ' + error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleSendResponse = async (data) => {
    try {
      await apiService.sendEmail(selectedEmail.id, data);
      alert('Email sent successfully');
      await loadEmails();
      await loadStats();
      setSelectedEmail(null);
      setResponses([]);
    } catch (error) {
      console.error('Failed to send email:', error);
      alert('Failed to send email: ' + error.message);
    }
  };

  const handleImproveResponse = async (draft) => {
    const feedback = prompt('What would you like to improve?');
    if (feedback) {
      try {
        const data = await apiService.improveResponse(selectedEmail.id, draft, feedback);
        setResponses([{ content: data.improved, tone: 'improved' }]);
      } catch (error) {
        console.error('Failed to improve response:', error);
        alert('Failed to improve response: ' + error.message);
      }
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="h-screen flex flex-col">
      <StatusBar status={status} stats={stats} />

      <div className="px-6 py-3 border-b bg-white flex items-center gap-4">
        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          {syncing ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Sync
        </button>
        <button
          onClick={handleHistoricalSync}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Download className="w-4 h-4" />
          Historical Sync
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <EmailList
          emails={emails}
          selectedEmail={selectedEmail}
          onSelectEmail={handleSelectEmail}
          onFilterChange={handleFilterChange}
          filters={filters}
        />

        <div className="flex-1 flex flex-col">
          <EmailDetail
            email={selectedEmail}
            onGenerateResponses={handleGenerateResponses}
            generating={generating}
          />
          {selectedEmail && (
            <ResponseEditor
              responses={responses}
              email={selectedEmail}
              onSend={handleSendResponse}
              onImprove={handleImproveResponse}
              generating={generating}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
