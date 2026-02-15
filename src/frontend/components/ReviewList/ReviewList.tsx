// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect, useCallback } from 'react';

interface Review {
  id: string;
  rating: number;
  title: string;
  body: string;
  author: string;
  createdAt: string;
  helpful: number;
}

interface ReviewListProps {
  productId: string;
}

type SortOption = 'newest' | 'highest' | 'lowest' | 'most_helpful';

const ReviewList = ({ productId }: ReviewListProps) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [filterRating, setFilterRating] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchReviews = useCallback(async (pageNum: number, reset = false) => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(pageNum),
        sort: sortBy,
        ...(filterRating ? { rating: String(filterRating) } : {}),
      });

      const response = await fetch(
        `/api/products/${productId}/reviews?${params}`
      );
      const data = await response.json();

      setReviews(prev => reset ? data.reviews : [...prev, ...data.reviews]);
      setHasMore(data.hasMore);
    } catch (error) {
      console.error('Failed to load reviews:', error);
    } finally {
      setIsLoading(false);
    }
  }, [productId, sortBy, filterRating]);

  useEffect(() => {
    setPage(1);
    fetchReviews(1, true);
  }, [fetchReviews]);

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchReviews(nextPage);
  };

  const handleSortChange = (newSort: SortOption) => {
    setSortBy(newSort);
  };

  const handleFilterChange = (rating: number | null) => {
    setFilterRating(rating);
  };

  const handleHelpful = async (reviewId: string) => {
    try {
      await fetch(`/api/reviews/${reviewId}/helpful`, { method: 'POST' });
      setReviews(prev =>
        prev.map(r =>
          r.id === reviewId ? { ...r, helpful: r.helpful + 1 } : r
        )
      );
    } catch (error) {
      console.error('Failed to mark review as helpful:', error);
    }
  };

  const handleReport = async (reviewId: string) => {
    if (!confirm('Are you sure you want to report this review?')) return;

    try {
      await fetch(`/api/reviews/${reviewId}/report`, { method: 'POST' });
      alert('Review has been reported. Thank you.');
    } catch (error) {
      console.error('Failed to report review:', error);
    }
  };

  const averageRating = reviews.length > 0
    ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
    : 0;

  return (
    <div className="review-list">
      <div className="review-summary">
        <h3>Customer Reviews</h3>
        <div className="average-rating">
          <span className="rating-number">{averageRating.toFixed(1)}</span>
          <span className="rating-stars">
            {'★'.repeat(Math.round(averageRating))}
            {'☆'.repeat(5 - Math.round(averageRating))}
          </span>
          <span className="review-count">({reviews.length} reviews)</span>
        </div>
      </div>

      <div className="review-controls">
        <div className="review-sort">
          <label>Sort by:</label>
          <select
            value={sortBy}
            onChange={e => handleSortChange(e.target.value as SortOption)}
          >
            <option value="newest">Newest</option>
            <option value="highest">Highest Rated</option>
            <option value="lowest">Lowest Rated</option>
            <option value="most_helpful">Most Helpful</option>
          </select>
        </div>

        <div className="review-filter">
          <label>Filter:</label>
          <div className="filter-buttons">
            <button
              className={filterRating === null ? 'active' : ''}
              onClick={() => handleFilterChange(null)}
            >
              All
            </button>
            {[5, 4, 3, 2, 1].map(star => (
              <button
                key={star}
                className={filterRating === star ? 'active' : ''}
                onClick={() => handleFilterChange(star)}
              >
                {star}★
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading && reviews.length === 0 ? (
        <div className="reviews-loading">Loading reviews...</div>
      ) : reviews.length === 0 ? (
        <div className="reviews-empty">
          <p>No reviews yet. Be the first to share your experience!</p>
        </div>
      ) : (
        <>
          <ul className="reviews">
            {reviews.map(review => (
              <li key={review.id} className="review-item">
                <div className="review-header">
                  <span className="review-stars">
                    {'★'.repeat(review.rating)}
                    {'☆'.repeat(5 - review.rating)}
                  </span>
                  <span className="review-title">{review.title}</span>
                </div>
                <p className="review-author">
                  By {review.author} on{' '}
                  {new Date(review.createdAt).toLocaleDateString()}
                </p>
                <p className="review-body">{review.body}</p>
                <div className="review-actions">
                  <button onClick={() => handleHelpful(review.id)}>
                    Helpful ({review.helpful})
                  </button>
                  <button
                    className="report-btn"
                    onClick={() => handleReport(review.id)}
                  >
                    Report
                  </button>
                </div>
              </li>
            ))}
          </ul>

          {hasMore && (
            <button
              className="load-more-btn"
              onClick={handleLoadMore}
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : 'Load More Reviews'}
            </button>
          )}
        </>
      )}
    </div>
  );
};

export default ReviewList;
