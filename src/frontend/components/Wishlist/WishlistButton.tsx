import { useState, useCallback } from 'react';
import styled from 'styled-components';

interface WishlistButtonProps {
  productId: string;
  productName: string;
}

const Button = styled.button<{ $active: boolean }>`
  background: ${({ $active }) => ($active ? '#e74c3c' : '#f0f0f0')};
  color: ${({ $active }) => ($active ? '#fff' : '#333')};
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    opacity: 0.8;
  }
`;

const WishlistButton = ({ productId, productName }: WishlistButtonProps) => {
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const toggleWishlist = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/wishlist', {
        method: isInWishlist ? 'DELETE' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId }),
      });

      if (!response.ok) {
        throw new Error(`Wishlist API error: ${response.status}`);
      }

      setIsInWishlist(!isInWishlist);
    } catch (error) {
      console.error('Failed to update wishlist:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isInWishlist, productId]);

  const shareWishlist = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(
        `${window.location.origin}/wishlist/shared?items=${productId}`
      );
      alert('Wishlist link copied!');
    } catch (error) {
      console.error('Failed to copy wishlist link:', error);
    }
  }, [productId]);

  return (
    <div>
      <Button $active={isInWishlist} onClick={toggleWishlist} disabled={isLoading}>
        {isLoading ? 'Updating...' : isInWishlist ? '❤️ In Wishlist' : '🤍 Add to Wishlist'}
      </Button>
      {isInWishlist && (
        <Button $active={false} onClick={shareWishlist} style={{ marginLeft: 8 }}>
          Share
        </Button>
      )}
    </div>
  );
};

export default WishlistButton;
