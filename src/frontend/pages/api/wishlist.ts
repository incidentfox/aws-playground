import type { NextApiRequest, NextApiResponse } from 'next';

interface WishlistItem {
  productId: string;
  addedAt: string;
}

// In-memory store (would be a database in production)
const wishlists = new Map<string, WishlistItem[]>();

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const userId = req.headers['x-user-id'] as string || 'anonymous';

  if (req.method === 'GET') {
    const items = wishlists.get(userId) || [];
    return res.status(200).json({ items });
  }

  if (req.method === 'POST') {
    const { productId } = req.body;

    if (!productId) {
      return res.status(400).json({ error: 'productId is required' });
    }

    const items = wishlists.get(userId) || [];
    const exists = items.find(item => item.productId === productId);

    if (exists) {
      return res.status(409).json({ error: 'Already in wishlist' });
    }

    items.push({ productId, addedAt: new Date().toISOString() });
    wishlists.set(userId, items);

    return res.status(201).json({ success: true, itemCount: items.length });
  }

  if (req.method === 'DELETE') {
    const { productId } = req.body;

    if (!productId) {
      return res.status(400).json({ error: 'productId is required' });
    }

    const items = wishlists.get(userId) || [];
    const filtered = items.filter(item => item.productId !== productId);
    wishlists.set(userId, filtered);

    return res.status(200).json({ success: true, itemCount: filtered.length });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}

