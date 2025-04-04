import React from 'react';

function Dashboard({ stats = [], bestTime = '', bestDay = '', topPost = null, engagementTrend = [] }) {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="stats">
        <h3>Stats</h3>
        {stats.length > 0 ? (
          <ul>
            {stats.map((stat, index) => (
              <li key={index}>
                {stat.name}: {stat.value}
              </li>
            ))}
          </ul>
        ) : (
          <p>No stats available.</p>
        )}
      </div>
      <div className="best-time">
        <h3>Best Time to Post</h3>
        <p>Hour: {bestTime || 'N/A'}</p>
      </div>
      <div className="best-day">
        <h3>Best Day to Post</h3>
        <p>Day: {bestDay || 'N/A'}</p>
      </div>
      <div className="top-post">
        <h3>Top Post</h3>
        {topPost ? (
          <div>
            <p>Post ID: {topPost.id}</p>
            <p>Likes: {topPost.likes}</p>
            <p>Timestamp: {topPost.timestamp}</p>
          </div>
        ) : (
          <p>No top post available.</p>
        )}
      </div>
      <div className="engagement-trend">
        <h3>Engagement Trend</h3>
        {engagementTrend.length > 0 ? (
          <ul>
            {engagementTrend.map((trend, index) => (
              <li key={index}>
                {trend.timestamp}: {trend.likes_count} likes
              </li>
            ))}
          </ul>
        ) : (
          <p>No engagement trend available.</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;