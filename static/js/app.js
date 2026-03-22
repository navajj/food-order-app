/* ── CSRF Helper ── */
function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

/* ── Cart Management (localStorage) ── */
function getCart() {
  try { return JSON.parse(localStorage.getItem('cart')) || null; } catch { return null; }
}

function saveCart(cart) {
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartBadge();
}

function addToCart(restaurantId, itemId, name, price) {
  let cart = getCart();
  if (cart && cart.restaurantId !== restaurantId) {
    if (!confirm('Your cart has items from another restaurant. Clear cart and add this item?')) return;
    cart = null;
  }
  if (!cart) cart = { restaurantId: restaurantId, items: {} };
  const key = String(itemId);
  if (cart.items[key]) {
    cart.items[key].quantity++;
  } else {
    cart.items[key] = { name, price: parseFloat(price), quantity: 1 };
  }
  saveCart(cart);
}

function removeFromCart(itemId) {
  const cart = getCart();
  if (!cart) return;
  delete cart.items[String(itemId)];
  if (Object.keys(cart.items).length === 0) { localStorage.removeItem('cart'); updateCartBadge(); return; }
  saveCart(cart);
}

function updateQuantity(itemId, qty) {
  const cart = getCart();
  if (!cart) return;
  const key = String(itemId);
  if (qty <= 0) { removeFromCart(itemId); return; }
  if (cart.items[key]) cart.items[key].quantity = qty;
  saveCart(cart);
}

function clearCart() {
  localStorage.removeItem('cart');
  updateCartBadge();
}

function getCartTotal() {
  const cart = getCart();
  if (!cart) return 0;
  return Object.values(cart.items).reduce((s, i) => s + i.price * i.quantity, 0);
}

function getCartCount() {
  const cart = getCart();
  if (!cart) return 0;
  return Object.values(cart.items).reduce((s, i) => s + i.quantity, 0);
}

function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  if (!badge) return;
  const count = getCartCount();
  if (count > 0) {
    badge.textContent = count;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

/* ── Render Cart Page ── */
function renderCart() {
  const cart = getCart();
  const emptyEl = document.getElementById('cart-empty');
  const contentEl = document.getElementById('cart-content');
  if (!cart || Object.keys(cart.items).length === 0) {
    emptyEl && emptyEl.classList.remove('hidden');
    contentEl && contentEl.classList.add('hidden');
    return;
  }
  emptyEl && emptyEl.classList.add('hidden');
  contentEl && contentEl.classList.remove('hidden');

  const tbody = document.getElementById('cart-table-body');
  tbody.innerHTML = '';
  let total = 0;
  for (const [id, item] of Object.entries(cart.items)) {
    const sub = item.price * item.quantity;
    total += sub;
    tbody.innerHTML += `
      <tr class="border-t">
        <td class="px-6 py-4 text-gray-800">${item.name}</td>
        <td class="px-6 py-4 text-gray-600">$${item.price.toFixed(2)}</td>
        <td class="px-6 py-4">
          <div class="flex items-center gap-2">
            <button onclick="updateQuantity('${id}', ${item.quantity - 1}); renderCart();" class="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 transition text-gray-700 font-bold">-</button>
            <span class="w-8 text-center">${item.quantity}</span>
            <button onclick="updateQuantity('${id}', ${item.quantity + 1}); renderCart();" class="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 transition text-gray-700 font-bold">+</button>
          </div>
        </td>
        <td class="px-6 py-4 text-gray-800 font-medium">$${sub.toFixed(2)}</td>
        <td class="px-6 py-4">
          <button onclick="removeFromCart('${id}'); renderCart();" class="text-red-500 hover:text-red-700 transition text-sm">Remove</button>
        </td>
      </tr>`;
  }
  document.getElementById('cart-total').textContent = total.toFixed(2);
}

/* ── Render Checkout Page ── */
function renderCheckout() {
  const cart = getCart();
  const container = document.getElementById('checkout-items');
  if (!cart || Object.keys(cart.items).length === 0) {
    container.innerHTML = '<p class="text-gray-500">Your cart is empty.</p>';
    return;
  }
  let html = '', total = 0;
  for (const item of Object.values(cart.items)) {
    const sub = item.price * item.quantity;
    total += sub;
    html += `<div class="flex justify-between py-2 text-sm text-gray-700">
      <span>${item.quantity}x ${item.name}</span><span>$${sub.toFixed(2)}</span>
    </div>`;
  }
  container.innerHTML = html;
  document.getElementById('checkout-total').textContent = total.toFixed(2);
}

/* ── Place Order ── */
async function placeOrder() {
  const cart = getCart();
  if (!cart) return;
  const errEl = document.getElementById('checkout-error');
  errEl.classList.add('hidden');

  const items = Object.entries(cart.items).map(([id, i]) => ({
    menu_item_id: parseInt(id),
    quantity: i.quantity,
  }));

  try {
    const resp = await fetch('/api/orders/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
      body: JSON.stringify({
        restaurant_id: cart.restaurantId,
        items: items,
        notes: document.getElementById('order-notes').value || '',
      }),
    });
    if (!resp.ok) {
      const data = await resp.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to place order.');
    }
    const order = await resp.json();
    clearCart();
    window.location.href = '/orders/' + order.id + '/tracking/';
  } catch (e) {
    errEl.textContent = e.message;
    errEl.classList.remove('hidden');
  }
}

/* ── Order Tracking ── */
const STATUS_STEPS = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'DELIVERED'];
const STATUS_LABELS = { PENDING: 'Pending', CONFIRMED: 'Confirmed', PREPARING: 'Preparing', READY: 'Ready', DELIVERED: 'Delivered' };

function renderStatusStepper(status) {
  const container = document.getElementById('status-stepper');
  const cancelledBadge = document.getElementById('cancelled-badge');
  if (status === 'CANCELLED') {
    container.classList.add('hidden');
    cancelledBadge.classList.remove('hidden');
    return;
  }
  cancelledBadge.classList.add('hidden');
  container.classList.remove('hidden');

  const currentIdx = STATUS_STEPS.indexOf(status);
  let html = '';
  STATUS_STEPS.forEach((step, i) => {
    const done = i <= currentIdx;
    const color = done ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500';
    const lineColor = i <= currentIdx ? 'bg-indigo-600' : 'bg-gray-200';
    html += `<div class="flex-1 flex flex-col items-center">
      <div class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${color} transition">${i + 1}</div>
      <span class="mt-2 text-xs font-medium ${done ? 'text-indigo-600' : 'text-gray-400'}">${STATUS_LABELS[step]}</span>
    </div>`;
    if (i < STATUS_STEPS.length - 1) {
      html += `<div class="flex-1 h-1 self-center rounded ${lineColor} transition" style="margin-top:-1.25rem;"></div>`;
    }
  });
  container.innerHTML = html;
}

function pollOrderStatus(orderId) {
  setInterval(async () => {
    try {
      const resp = await fetch('/api/orders/' + orderId + '/');
      if (!resp.ok) return;
      const data = await resp.json();
      renderStatusStepper(data.status);
    } catch {}
  }, 5000);
}

/* ── Dashboard: Update Order Status ── */
async function updateOrderStatus(orderId) {
  const select = document.getElementById('status-select-' + orderId);
  const status = select.value;
  try {
    const resp = await fetch('/api/orders/' + orderId + '/status/', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
      body: JSON.stringify({ status }),
    });
    if (!resp.ok) throw new Error('Failed');
    const badge = document.getElementById('status-badge-' + orderId);
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-700',
      CONFIRMED: 'bg-blue-100 text-blue-700',
      PREPARING: 'bg-orange-100 text-orange-700',
      READY: 'bg-green-100 text-green-700',
      DELIVERED: 'bg-gray-100 text-gray-700',
      CANCELLED: 'bg-red-100 text-red-700',
    };
    badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-medium ' + (colors[status] || '');
    badge.textContent = STATUS_LABELS[status] || status;
  } catch {
    alert('Failed to update status.');
  }
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', updateCartBadge);
