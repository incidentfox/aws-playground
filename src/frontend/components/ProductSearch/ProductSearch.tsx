// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';

interface SearchResult {
  id: string;
  name: string;
  picture: string;
  categories: string[];
}

const ProductSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const debounceRef = useRef<NodeJS.Timeout>();
  const { push } = useRouter();

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`/api/products/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        setResults(data.products || []);
        setIsOpen(true);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const handleSelect = (product: SearchResult) => {
    setQuery('');
    setIsOpen(false);
    push(`/product/${product.id}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      handleSelect(results[selectedIndex]);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
  };

  return (
    <div className="product-search">
      <div className="search-input-wrapper">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder="Search products..."
          className="search-input"
        />
        {query && (
          <button className="search-clear" onClick={handleClear}>x</button>
        )}
        {isLoading && <span className="search-spinner" />}
      </div>

      {isOpen && results.length > 0 && (
        <ul className="search-results">
          {results.map((product, index) => (
            <li
              key={product.id}
              className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => handleSelect(product)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <img src={product.picture} alt={product.name} />
              <div>
                <span className="result-name">{product.name}</span>
                <span className="result-category">
                  {product.categories.join(', ')}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      {isOpen && results.length === 0 && query.length >= 2 && !isLoading && (
        <div className="search-no-results">
          No products found for "{query}"
        </div>
      )}
    </div>
  );
};

export default ProductSearch;
