import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [stats, setStats] = useState([]);
  const [bestTime, setBestTime] = useState(''); // Correct: setBestTime for bestTime
  const [bestDay, setBestDay] = useState('');   // Correct: setBestDay for bestDay
  const [topPost, setTopPost] = useState(null);
  const [engagementTrend, setEngagementTrend] = useState([]);
  const [predictedLikes, setPredictedLikes] = useState(null);
  const [predictHour, setPredictHour] = useState('');
  const [predictDay, setPredictDay] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/stats');
      setStats(response.data.stats);
      setBestTime(response.data.bestTime);
      setBestDay(response.data.bestDay); // Correct: Use setBestDay
      setTopPost(response.data.topPost);
      setEngagementTrend(response.data.engagementTrend);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const predictLikes = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/predict', {
        hour: predictHour,
        day: predictDay
      });
      setPredictedLikes(response.data.predictedLikes);
    } catch (error) {
      console.error('Error predicting likes:', error);
      setPredictedLikes(null);
    }
  };

  return (
    <div className="App">
      <h1>Instagram AI Manager</h1>
      <button onClick={fetchStats}>Refresh Data</button>
      <div>
        <h3>Predict Likes for a Future Post</h3>
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