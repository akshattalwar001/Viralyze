import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [stats, setStats] = useState([]);
  const [bestTime, setBestTime] = useState('');
  const [bestDay, setBestDay] = useState('');
  const [topPost, setTopPost] = useState(null);
  const [engagementTrend, setEngagementTrend] = useState([]);
  const [predictedLikes, setPredictedLikes] = useState(null);
  const [predictHour, setPredictHour] = useState('');
  const [predictDay, setPredictDay] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/stats');
      setStats(response.data.stats || []);
      setBestTime(response.data.bestTime || '');
      setBestDay(response.data.bestDay || '');
      setTopPost(response.data.topPost || null);
      setEngagementTrend(response.data.engagementTrend || []);
      setError(null);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setError('Failed to fetch stats. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const predictLikes = async () => {
    if (!predictHour || !predictDay) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/predict', {
        hour: predictHour,
        day: predictDay
      });
      setPredictedLikes(response.data.predictedLikes);
      setError(null);
    } catch (error) {
      console.error('Error predicting likes:', error);
      setPredictedLikes(null);
      setError('Failed to predict likes. Please check your inputs and ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="App">
        <h1>Instagram AI Manager</h1>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={fetchStats}>Retry</button>
      </div>
    );
  }

  return (
    <div className="App">
      <h1>Instagram AI Manager</h1>
      <button onClick={fetchStats}>Refresh Data</button>
      <div>
        <h3>Predict Likes for a Future Post</h3>
        {loading && <p>Loading...</p>}
        <label>
          Hour (0-23):
          <input
            type="number"
            min="0"
            max="23"
            value={predictHour}
            onChange={(e) => setPredictHour(e.target.value)}
          />
        </label>
        <label>
          Day of the Week:
          <select value={predictDay} onChange={(e) => setPredictDay(e.target.value)}>
            <option value="">Select a day</option>
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
            <option value="Thursday">Thursday</option>
            <option value="Friday">Friday</option>
            <option value="Saturday">Saturday</option>
            <option value="Sunday">Sunday</option>
          </select>
        </label>
        <button onClick={predictLikes}>Predict Likes</button>
        {predictedLikes !== null && (
          <p>Predicted Likes: {predictedLikes}</p>
        )}
      </div>
      <Dashboard
        stats={stats}
        bestTime={bestTime}
        bestDay={bestDay}
        topPost={topPost}
        engagementTrend={engagementTrend}
      />
    </div>
  );
}

export default App;