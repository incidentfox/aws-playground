// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { useCart } from '../../providers/Cart.provider';
import { useCurrency } from '../../providers/Currency.provider';
import ProductPrice from '../ProductPrice';
import Button from '../Button';

interface QuickViewProps {
  productId: string;
  isOpen: boolean;
  onClose: () => void;
}

const QuickView = ({ productId, isOpen, onClose }: QuickViewProps) => {
  const [product, setProduct] = useState<any>(null);
  const [selectedQuantity, setSelectedQuantity] = useState(1);
  const [selectedSize, setSelectedSize] = useState('');
  const { addItem } = useCart();
  const { selectedCurrency } = useCurrency();

  useEffect(() => {
    if (isOpen && productId) {
      fetch(`/api/products/${productId}`)
        .then(res => res.json())
        .then(data => setProduct(data))
        .catch(err => console.error('Failed to load product:', err));
    }
  }, [isOpen, productId]);

  if (!isOpen || !product) return null;

  const handleAddToCart = () => {
    addItem({
      productId: product.id,
      quantity: selectedQuantity,
    });
    onClose();
  };

  const handleQuantityChange = (delta: number) => {
    setSelectedQuantity(prev => Math.max(1, Math.min(10, prev + delta)));
  };

  const handleSizeSelect = (size: string) => {
    setSelectedSize(size);
  };

  const handleShare = async () => {
    const shareUrl = `${window.location.origin}/product/${product.id}`;
    if (navigator.share) {
      await navigator.share({
        title: product.name,
        url: shareUrl,
      });
    } else {
      await navigator.clipboard.writeText(shareUrl);
    }
  };

  return (
    <div className="quickview-overlay" onClick={onClose}>
      <div className="quickview-modal" onClick={e => e.stopPropagation()}>
        <button className="quickview-close" onClick={onClose}>×</button>

        <div className="quickview-content">
          <div className="quickview-image">
            <img src={product.picture} alt={product.name} />
          </div>

          <div className="quickview-details">
            <h2>{product.name}</h2>
            <p className="quickview-description">{product.description}</p>

            <ProductPrice
              price={product.priceUsd}
              currency={selectedCurrency}
            />

            {product.categories && (
              <div className="quickview-categories">
                {product.categories.map((cat: string) => (
                  <span key={cat} className="category-tag">{cat}</span>
                ))}
              </div>
            )}

            {product.sizes && (
              <div className="quickview-sizes">
                <label>Size:</label>
                {product.sizes.map((size: string) => (
                  <button
                    key={size}
                    className={`size-btn ${selectedSize === size ? 'active' : ''}`}
                    onClick={() => handleSizeSelect(size)}
                  >
                    {size}
                  </button>
                ))}
              </div>
            )}

            <div className="quickview-quantity">
              <button onClick={() => handleQuantityChange(-1)}>-</button>
              <span>{selectedQuantity}</span>
              <button onClick={() => handleQuantityChange(1)}>+</button>
            </div>

            <div className="quickview-actions">
              <Button onClick={handleAddToCart}>Add to Cart</Button>
              <button className="share-btn" onClick={handleShare}>
                Share
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickView;
