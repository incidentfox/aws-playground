// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useState, useCallback } from 'react';
import Button from '../Button';

interface WishlistItem {
  productId: string;
  name: string;
  picture: string;
  addedAt: Date;
}

const STORAGE_KEY = 'wishlist_items';

const Wishlist = () => {
  const [items, setItems] = useState<WishlistItem[]>(() => {
    if (typeof window === 'undefined') return [];
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  });
  const [isOpen, setIsOpen] = useState(false);

  const addToWishlist = useCallback((product: { id: string; name: string; picture: string }) => {
    setItems(prev => {
      if (prev.find(item => item.productId === product.id)) {
        return prev;
      }
      const updated = [...prev, {
        productId: product.id,
        name: product.name,
        picture: product.picture,
        addedAt: new Date(),
      }];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const removeFromWishlist = useCallback((productId: string) => {
    setItems(prev => {
      const updated = prev.filter(item => item.productId !== productId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const clearWishlist = useCallback(() => {
    setItems([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const moveToCart = useCallback(async (productId: string) => {
    try {
      const response = await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId, quantity: 1 }),
      });
      if (response.ok) {
        removeFromWishlist(productId);
      }
    } catch (error) {
      console.error('Failed to move item to cart:', error);
    }
  }, [removeFromWishlist]);

  const shareWishlist = async () => {
    const wishlistUrl = `${window.location.origin}/wishlist?items=${items.map(i => i.productId).join(',')}`;
    try {
      await navigator.clipboard.writeText(wishlistUrl);
      alert('Wishlist link copied!');
    } catch {
      console.error('Failed to copy wishlist link');
    }
  };

  return (
    <>
      <button
        className="wishlist-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        ♥ ({items.length})
      </button>

      {isOpen && (
        <div className="wishlist-panel">
          <div className="wishlist-header">
            <h3>My Wishlist</h3>
            {items.length > 0 && (
              <div className="wishlist-header-actions">
                <button onClick={shareWishlist}>Share</button>
                <button onClick={clearWishlist}>Clear All</button>
              </div>
            )}
          </div>

          {items.length === 0 ? (
            <p className="wishlist-empty">Your wishlist is empty</p>
          ) : (
            <ul className="wishlist-items">
              {items.map(item => (
                <li key={item.productId} className="wishlist-item">
                  <img src={item.picture} alt={item.name} />
                  <div className="wishlist-item-info">
                    <span>{item.name}</span>
                    <div className="wishlist-item-actions">
                      <Button onClick={() => moveToCart(item.productId)}>
                        Add to Cart
                      </Button>
                      <button onClick={() => removeFromWishlist(item.productId)}>
                        Remove
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </>
  );
};

export { Wishlist, type WishlistItem };
export default Wishlist;
