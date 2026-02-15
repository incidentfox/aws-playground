import React, { useState } from 'react';

interface FeedbackWidgetProps {
  productId: string;
  userId: string;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ productId, userId }) => {
  const [rating, setRating] = useState<number>(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId, userId, rating, comment }),
    });

    if (response.ok) {
      setSubmitted(true);
    }
  };

  const handleRatingClick = (value: number) => {
    setRating(value);
  };

  if (submitted) {
    return <div className="feedback-thanks">Thank you for your feedback!</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="feedback-widget">
      <h3>Rate this product</h3>
      <div className="rating-stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => handleRatingClick(star)}
            className={star <= rating ? 'active' : ''}
          >
            ★
          </button>
        ))}
      </div>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Tell us what you think..."
        rows={3}
      />
      <button type="submit" disabled={rating === 0}>
        Submit Feedback
      </button>
    </form>
  );
};
// v2
