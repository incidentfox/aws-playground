// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useState } from 'react';
import Button from '../Button';

interface CouponResult {
  valid: boolean;
  discount: number;
  message: string;
}

interface CouponCodeProps {
  onApply: (discount: number) => void;
}

const CouponCode = ({ onApply }: CouponCodeProps) => {
  const [code, setCode] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [result, setResult] = useState<CouponResult | null>(null);
  const [appliedCode, setAppliedCode] = useState<string | null>(null);

  const handleApply = async () => {
    if (!code.trim() || code === appliedCode) return;

    setIsValidating(true);
    setResult(null);

    try {
      const response = await fetch('/api/coupons/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code.trim().toUpperCase() }),
      });

      const data: CouponResult = await response.json();
      setResult(data);

      if (data.valid) {
        setAppliedCode(code.trim().toUpperCase());
        onApply(data.discount);
      }
    } catch (error) {
      setResult({
        valid: false,
        discount: 0,
        message: 'Failed to validate coupon. Please try again.',
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleRemove = () => {
    setAppliedCode(null);
    setCode('');
    setResult(null);
    onApply(0);
  };

  return (
    <div className="coupon-section">
      <h4>Have a coupon code?</h4>

      {appliedCode ? (
        <div className="coupon-applied">
          <span className="coupon-badge">
            {appliedCode} — {result?.discount}% off
          </span>
          <button onClick={handleRemove} className="coupon-remove">
            Remove
          </button>
        </div>
      ) : (
        <div className="coupon-input-group">
          <input
            type="text"
            value={code}
            onChange={e => setCode(e.target.value)}
            placeholder="Enter coupon code"
            disabled={isValidating}
            onKeyDown={e => e.key === 'Enter' && handleApply()}
          />
          <Button
            onClick={handleApply}
            disabled={isValidating || !code.trim()}
          >
            {isValidating ? 'Validating...' : 'Apply'}
          </Button>
        </div>
      )}

      {result && !result.valid && (
        <p className="coupon-error">{result.message}</p>
      )}
    </div>
  );
};

export default CouponCode;
