// Svelte 5 Runes Cart Store for Webshop-Ecom
export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface PromoCode {
  code: string;
  discountPercentage: number;
}

class CartState {
  items = $state<CartItem[]>([]);
  appliedPromo = $state<PromoCode | null>(null);

  subtotal = $derived(this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0));
  discountAmount = $derived(this.appliedPromo ? (this.subtotal * this.appliedPromo.discountPercentage / 100) : 0);
  total = $derived(Math.max(0, this.subtotal - this.discountAmount));
  totalCount = $derived(this.items.reduce((sum, item) => sum + item.quantity, 0));

  addItem(item: Omit<CartItem, 'quantity'>) {
    const existing = this.items.find(i => i.id === item.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      this.items.push({ ...item, quantity: 1 });
    }
  }

  applyPromo(codeStr: string): { success: boolean; message: string } {
    const code = codeStr.trim().toUpperCase();
    if (code === 'SAVE20') {
      this.appliedPromo = { code: 'SAVE20', discountPercentage: 20 };
      return { success: true, message: '20% discount applied!' };
    }
    return { success: false, message: 'Invalid promo code' };
  }
}

export const cart = new CartState();
