<script lang="ts">
  import { cart } from '../lib/cartStore.svelte';
  let promoInput = $state('');
  let promoMessage = $state('');

  function handleApplyPromo() {
    const res = cart.applyPromo(promoInput);
    promoMessage = res.message;
  }
</script>

<aside class="cart-drawer p-6 bg-slate-900 text-white rounded-xl shadow-2xl">
  <h2 class="text-xl font-bold mb-4">Shopping Cart ({cart.totalCount})</h2>
  <div class="space-y-3 mb-6">
    {#each cart.items as item}
      <div class="flex justify-between items-center border-b border-slate-800 pb-2">
        <span>{item.name} x {item.quantity}</span>
        <span>${(item.price * item.quantity).toFixed(2)}</span>
      </div>
    {/each}
  </div>
  <div class="border-t border-slate-800 pt-4 space-y-2">
    <div class="flex justify-between text-slate-400">Subtotal: <span>${cart.subtotal.toFixed(2)}</span></div>
    {#if cart.appliedPromo}
      <div class="flex justify-between text-emerald-400 font-semibold">Discount: <span>-${cart.discountAmount.toFixed(2)}</span></div>
    {/if}
    <div class="flex justify-between text-lg font-bold text-white">Total: <span>${cart.total.toFixed(2)}</span></div>
  </div>
</aside>
