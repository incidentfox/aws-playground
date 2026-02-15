// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';

interface RatingDistribution {
  [key: number]: number;
}

interface ReviewStatsProps {
  productId: string;
  onFilterClick?: (rating: number) => void;
}

const ReviewStats = ({ productId, onFilterClick }: ReviewStatsProps) => {
  const [stats, setStats] = useState<{
    total: number;
    average: number;
    distribution: RatingDistribution;
    recommended: number;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [compareProduct, setCompareProduct] = useState<string | null>(null);
  const [compareStats, setCompareStats] = useState<typeof stats>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`/api/products/${productId}/review-stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Failed to load review stats:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, [productId]);

  const handleCompare = async (otherProductId: string) => {
    setCompareProduct(otherProductId);
    try {
      const response = await fetch(`/api/products/${otherProductId}/review-stats`);
      const data = await response.json();
      setCompareStats(data);
    } catch (error) {
      console.error('Failed to load comparison stats:', error);
      setCompareStats(null);
    }
  };

  const handleExport = () => {
    if (!stats) return;
    const csv = [
      'Rating,Count,Percentage',
      ...Object.entries(stats.distribution).map(([rating, count]) =>
        `${rating},${count},${((count / stats.total) * 100).toFixed(1)}%`
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `review-stats-${productId}.csv`;
    a.click();
  };

  if (isLoading) return <div className="stats-loading">Loading stats...</div>;
  if (!stats) return null;

  const maxCount = Math.max(...Object.values(stats.distribution));

  return (
    <div className="review-stats">
      <div className="stats-overview">
        <div className="stats-score">
          <span className="big-number">{stats.average.toFixed(1)}</span>
          <span className="out-of">out of 5</span>
          <span className="total-reviews">{stats.total} reviews</span>
        </div>
        <div className="stats-recommendation">
          {stats.recommended}% of customers recommend this product
        </div>
      </div>

      <div className="rating-bars">
        {[5, 4, 3, 2, 1].map(rating => {
          const count = stats.distribution[rating] || 0;
          const percentage = stats.total > 0 ? (count / stats.total) * 100 : 0;

          return (
            <div
              key={rating}
              className="rating-bar-row"
              onClick={() => onFilterClick?.(rating)}
              role="button"
              tabIndex={0}
            >
              <span className="rating-label">{rating} ★</span>
              <div className="rating-bar-track">
                <div
                  className="rating-bar-fill"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <span className="rating-count">{count}</span>
            </div>
          );
        })}
      </div>

      <div className="stats-actions">
        <button className="export-btn" onClick={handleExport}>
          Export CSV
        </button>
        {!compareProduct && (
          <button
            className="compare-btn"
            onClick={() => handleCompare('similar-product-id')}
          >
            Compare with Similar
          </button>
        )}
      </div>

      {compareStats && (
        <div className="stats-comparison">
          <h4>Comparison</h4>
          <table>
            <thead>
              <tr>
                <th>Metric</th>
                <th>This Product</th>
                <th>Compared Product</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Average Rating</td>
                <td>{stats.average.toFixed(1)}</td>
                <td>{compareStats.average.toFixed(1)}</td>
              </tr>
              <tr>
                <td>Total Reviews</td>
                <td>{stats.total}</td>
                <td>{compareStats.total}</td>
              </tr>
              <tr>
                <td>Recommended</td>
                <td>{stats.recommended}%</td>
                <td>{compareStats.recommended}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ReviewStats;
