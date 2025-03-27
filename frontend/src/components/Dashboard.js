import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = ({ stats, bestTime }) => {
  const hourlyLikes = {};
  stats.forEach(post => {
    const hour = new Date(post.timestamp).getHours();
    hourlyLikes[hour] = (hourlyLikes[hour] || 0) + post.likes_count;
  });

  const chartData = {
    labels: Object.keys(hourlyLikes).map(h => `${h}:00`),
    datasets: [
      {
        label: 'Likes by Hour',
        data: Object.values(hourlyLikes),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { position: 'top' }, title: { display: true, text: 'Engagement by Hour' } },
  };

  return (
    <div>
      <h2>Best Posting Time: {bestTime || 'Loading...'}</h2>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Bar data={chartData} options={options} />
      </div>
      <h3>Recent Posts</h3>
      <ul>
        {stats.map(post => (
          <li key={post.id}>
            {new Date(post.timestamp).toLocaleString()} - Likes: {post.likes_count}, Comments: {post.comments_count}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;