import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axios.get(`${API_BASE_URL}/api/reviews`);
      setReviews(response.data);
    } catch (err) {
      setError('Failed to fetch reviews. Make sure the backend server is running on port 8000.');
      console.error('Error fetching reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="container">
      <div className="header">
        <div className="whatsapp-icon">📱</div>
        <h1>WhatsApp Review Collector</h1>
        <p>Product reviews collected via WhatsApp messages</p>
      </div>

      {error && (
        <div className="error">
          {error}
          <button className="retry-button" onClick={fetchReviews}>
            Retry
          </button>
        </div>
      )}

      <div className="reviews-table">
        {loading ? (
          <div className="loading">Loading reviews...</div>
        ) : reviews.length === 0 ? (
          <div className="empty-state">
            <h3>No reviews yet</h3>
            <p>Send a "Hi" to your WhatsApp Sandbox number to start collecting reviews!</p>
            <div style={{ fontSize: '4rem' }}>💬</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>User Name</th>
                <th>Product</th>
                <th>Review</th>
                <th>Timestamp</th>
                <th>Contact</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id}>
                  <td>
                    <strong>{review.user_name}</strong>
                  </td>
                  <td>{review.product_name}</td>
                  <td style={{ maxWidth: '300px' }}>{review.product_review}</td>
                  <td style={{ whiteSpace: 'nowrap' }}>{formatDate(review.created_at)}</td>
                  <td style={{ color: '#666', fontSize: '0.9em', fontFamily: 'monospace' }}>
                    {review.contact_number}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default App;