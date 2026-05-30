// RESTAURANT_SLUG must be injected in the template before this file loads
const cart = {};
let currentStep = 1; // 1=cart, 2=car details, 3=invoice

// ─── Cart state ───────────────────────────────────────────────────────────────

function addToCart(id, nameAr, nameEn, price, qty = 1) {
  if (cart[id]) {
    cart[id].qty += qty;
  } else {
    cart[id] = { id, nameAr, nameEn, price: parseFloat(price), qty };
  }
  updateCartBar();
  refreshAllCtrl();
  closeProductSheet();
}

function changeQty(id, delta) {
  if (!cart[id]) return;
  cart[id].qty += delta;
  if (cart[id].qty <= 0) delete cart[id];
  renderStep(currentStep);
  updateCartBar();
  refreshAllCtrl();
}

function cartTotal() {
  return Object.values(cart).reduce((s, i) => s + i.price * i.qty, 0);
}
function cartCount() {
  return Object.values(cart).reduce((s, i) => s + i.qty, 0);
}

// ─── Cart bar ─────────────────────────────────────────────────────────────────

function updateCartBar() {
  const count = cartCount();
  const bar = document.getElementById('cartBar');
  document.getElementById('cartCount').textContent = count;
  document.getElementById('cartTotal').textContent = cartTotal().toFixed(3) + ' ر.ع';
  bar.classList.toggle('visible', count > 0);
}

// ─── Inline add-ctrl (card quantity selector) ─────────────────────────────────

function ctrlAdd(ctrl) {
  const id = parseInt(ctrl.dataset.productId);
  addToCart(id, ctrl.dataset.nameAr, ctrl.dataset.nameEn, parseFloat(ctrl.dataset.price));
}

function ctrlIncrease(ctrl) {
  const id = parseInt(ctrl.dataset.productId);
  addToCart(id, ctrl.dataset.nameAr, ctrl.dataset.nameEn, parseFloat(ctrl.dataset.price));
}

function ctrlDecrease(ctrl) {
  const id = parseInt(ctrl.dataset.productId);
  if (cart[id]) {
    cart[id].qty -= 1;
    if (cart[id].qty <= 0) delete cart[id];
  }
  updateCartBar();
  refreshAllCtrl();
}

function renderCtrl(ctrl) {
  const id = parseInt(ctrl.dataset.productId);
  const qty = cart[id] ? cart[id].qty : 0;
  if (qty === 0) {
    ctrl.innerHTML = `<button class="add-btn" onclick="event.stopPropagation(); ctrlAdd(this.closest('.add-ctrl'))">+ أضف</button>`;
  } else {
    ctrl.innerHTML = `
      <div style="display:flex;align-items:center;gap:.4rem;justify-content:center;">
        <button class="qty-btn" onclick="event.stopPropagation(); ctrlDecrease(this.closest('.add-ctrl'))"
                style="width:32px;height:32px;font-size:1.1rem;">−</button>
        <span style="font-weight:800;font-size:1rem;min-width:22px;text-align:center;">${qty}</span>
        <button class="qty-btn" onclick="event.stopPropagation(); ctrlIncrease(this.closest('.add-ctrl'))"
                style="width:32px;height:32px;font-size:1.1rem;background:var(--primary);color:white;border-color:var(--primary);">+</button>
      </div>`;
  }
}

function refreshAllCtrl() {
  document.querySelectorAll('.add-ctrl').forEach(renderCtrl);
}

// ─── Product detail sheet ─────────────────────────────────────────────────────

function openProductSheet(id, nameAr, nameEn, price, imgSrc, descAr) {
  const sheet = document.getElementById('productSheet');
  let sheetQty = 1;

  const imgHtml = imgSrc
    ? `<img src="${imgSrc}" style="width:100%;height:200px;object-fit:cover;border-radius:12px 12px 0 0;">`
    : `<div style="width:100%;height:160px;display:flex;align-items:center;justify-content:center;font-size:4rem;background:var(--theme-bg-page,#f0faf9);border-radius:12px 12px 0 0;">🍽️</div>`;

  const inCart = cart[id] ? `<div style="font-size:.78rem;color:#22C55E;font-weight:700;margin-bottom:.25rem;">✓ في السلة (${cart[id].qty})</div>` : '';

  sheet.innerHTML = `
    <div class="product-sheet-inner" id="productSheetInner">
      <button class="modal-close" onclick="closeProductSheet()" style="position:absolute;top:.75rem;left:.75rem;z-index:10;">✕</button>
      ${imgHtml}
      <div style="padding:1.1rem 1.1rem 1.5rem;">
        ${inCart}
        <div style="font-size:1.15rem;font-weight:800;color:var(--theme-text-primary,#1a3a35);">${nameAr}</div>
        <div style="font-size:.82rem;color:#94A3B8;margin-bottom:.35rem;">${nameEn}</div>
        ${descAr ? `<div style="font-size:.83rem;color:var(--theme-text-secondary,#475569);line-height:1.6;margin-bottom:.6rem;">${descAr}</div>` : ''}
        <div style="font-size:1.4rem;font-weight:900;color:var(--primary);margin-bottom:1.1rem;">${parseFloat(price).toFixed(3)} ر.ع</div>

        <div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;">
          <div style="display:flex;align-items:center;gap:.6rem;background:var(--theme-bg-page,#f8fafc);border-radius:12px;padding:.4rem .6rem;border:2px solid var(--theme-border,#e2e8f0);">
            <button class="qty-btn" id="sheetMinus" onclick="sheetQtyChange(-1)">−</button>
            <span id="sheetQtyVal" style="font-weight:800;font-size:1.1rem;min-width:28px;text-align:center;">${sheetQty}</span>
            <button class="qty-btn" onclick="sheetQtyChange(1)">+</button>
          </div>
          <button onclick="addToCart(${id}, ${JSON.stringify(nameAr)}, ${JSON.stringify(nameEn)}, ${price}, window._sheetQty||1)"
                  style="flex:1;padding:.75rem;background:var(--primary);color:white;border:none;border-radius:12px;font-family:'Cairo',sans-serif;font-weight:800;font-size:1rem;cursor:pointer;">
            أضف للسلة &nbsp;<span id="sheetBtnTotal">${parseFloat(price).toFixed(3)} ر.ع</span>
          </button>
        </div>
      </div>
    </div>`;

  window._sheetQty = 1;
  window._sheetPrice = parseFloat(price);

  sheet.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function sheetQtyChange(delta) {
  window._sheetQty = Math.max(1, (window._sheetQty || 1) + delta);
  document.getElementById('sheetQtyVal').textContent = window._sheetQty;
  document.getElementById('sheetMinus').disabled = window._sheetQty <= 1;
  document.getElementById('sheetBtnTotal').textContent =
    (window._sheetPrice * window._sheetQty).toFixed(3) + ' ر.ع';
}

function closeProductSheet() {
  const sheet = document.getElementById('productSheet');
  sheet.classList.remove('open');
  document.body.style.overflow = '';
}

// ─── Order Modal (3 steps) ────────────────────────────────────────────────────

function openOrderModal() {
  currentStep = 1;
  renderStep(1);
  document.getElementById('orderModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeOrderModal() {
  document.getElementById('orderModal').classList.remove('open');
  document.body.style.overflow = '';
}

function goStep(n) {
  if (n === 2) {
    // validate cart not empty before moving to step 2
    if (cartCount() === 0) {
      showModalError('السلة فارغة، أضف منتجاً أولاً'); return;
    }
  }
  if (n === 3) {
    const plate = document.getElementById('carPlate')?.value.trim();
    const model = document.getElementById('carModel')?.value.trim();
    const color = document.getElementById('carColor')?.value.trim();
    if (!plate) { shakeInput('carPlate'); showModalError('يرجى إدخال رقم اللوحة'); return; }
    if (!model) { shakeInput('carModel'); showModalError('يرجى إدخال نوع السيارة'); return; }
    if (!color) { shakeInput('carColor'); showModalError('يرجى إدخال لون السيارة'); return; }
  }
  currentStep = n;
  renderStep(n);
}

function showModalError(msg) {
  const el = document.getElementById('modalError');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function shakeInput(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.borderColor = '#EF4444';
  el.focus();
  setTimeout(() => { el.style.borderColor = ''; }, 2000);
}

function renderStep(step) {
  const body = document.getElementById('modalBody');
  if (!body) return;

  if (step === 1) renderCartStep(body);
  else if (step === 2) renderCarStep(body);
  else if (step === 3) renderInvoiceStep(body);
}

// Step 1 — Cart review
function renderCartStep(body) {
  const items = Object.values(cart);
  const empty = items.length === 0;

  body.innerHTML = `
    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:1rem;">
      <span style="font-size:1.2rem;">🛒</span>
      <span style="font-size:1.1rem;font-weight:800;">طلبك</span>
      <span style="margin-right:auto;font-size:.78rem;color:#94A3B8;">الخطوة 1 من 3</span>
    </div>
    <div id="modalError" style="display:none;background:#FEE2E2;color:#991B1B;border-radius:8px;padding:.5rem .75rem;font-size:.82rem;font-weight:600;margin-bottom:.75rem;"></div>

    <div id="cartItemsList">
      ${empty ? '<div style="text-align:center;color:#94A3B8;padding:1.5rem;font-size:.9rem;">السلة فارغة</div>' :
        items.map(item => `
          <div class="cart-item-row">
            <div style="flex:1;">
              <div class="cart-item-name">${item.nameAr}</div>
              <div style="font-size:.75rem;color:#94A3B8;">${item.nameEn}</div>
            </div>
            <div style="display:flex;align-items:center;gap:.5rem;">
              <div class="qty-controls">
                <button class="qty-btn" onclick="changeQty(${item.id},-1)">−</button>
                <span style="font-weight:800;min-width:22px;text-align:center;">${item.qty}</span>
                <button class="qty-btn" onclick="changeQty(${item.id},1)">+</button>
              </div>
              <div class="cart-item-price" style="min-width:70px;text-align:left;">${(item.price * item.qty).toFixed(3)} ر.ع</div>
            </div>
          </div>`).join('')}
    </div>

    ${!empty ? `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:.75rem 0;border-top:2px solid var(--theme-border,#e2e8f0);margin-top:.5rem;">
      <span style="font-weight:700;">المجموع</span>
      <span style="font-weight:900;font-size:1.15rem;color:var(--primary);">${cartTotal().toFixed(3)} ر.ع</span>
    </div>
    <button class="submit-order-btn" onclick="goStep(2)" style="margin-top:.75rem;">
      التالي: بيانات السيارة ←
    </button>` : ''}`;
}

// Step 2 — Car details
function renderCarStep(body) {
  const saved = window._carData || {};
  body.innerHTML = `
    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:1rem;">
      <button onclick="goStep(1)" style="background:none;border:none;font-size:1.1rem;cursor:pointer;color:#94A3B8;">←</button>
      <span style="font-size:1.1rem;font-weight:800;">🚗 بيانات السيارة</span>
      <span style="margin-right:auto;font-size:.78rem;color:#94A3B8;">الخطوة 2 من 3</span>
    </div>
    <div id="modalError" style="display:none;background:#FEE2E2;color:#991B1B;border-radius:8px;padding:.5rem .75rem;font-size:.82rem;font-weight:600;margin-bottom:.75rem;"></div>

    <div class="form-group">
      <label class="form-label">رقم اللوحة <span style="color:#EF4444;">*</span></label>
      <input class="form-input" type="text" id="carPlate" value="${saved.plate||''}" placeholder="مثال: ABC 1234">
    </div>
    <div class="form-group">
      <label class="form-label">نوع السيارة <span style="color:#EF4444;">*</span></label>
      <input class="form-input" type="text" id="carModel" value="${saved.model||''}" placeholder="مثال: تويوتا كامري">
    </div>
    <div class="form-group">
      <label class="form-label">لون السيارة <span style="color:#EF4444;">*</span></label>
      <input class="form-input" type="text" id="carColor" value="${saved.color||''}" placeholder="مثال: أبيض">
    </div>
    <div class="form-group">
      <label class="form-label">ملاحظات (اختياري)</label>
      <textarea class="form-input" id="orderNotes" rows="2" placeholder="أي طلبات خاصة...">${saved.notes||''}</textarea>
    </div>
    <button class="submit-order-btn" onclick="saveCarAndPreview()">
      مراجعة الطلب ←
    </button>`;
}

function saveCarAndPreview() {
  const plate = document.getElementById('carPlate')?.value.trim();
  const model = document.getElementById('carModel')?.value.trim();
  const color = document.getElementById('carColor')?.value.trim();
  if (!plate) { shakeInput('carPlate'); showModalError('يرجى إدخال رقم اللوحة'); return; }
  if (!model) { shakeInput('carModel'); showModalError('يرجى إدخال نوع السيارة'); return; }
  if (!color) { shakeInput('carColor'); showModalError('يرجى إدخال لون السيارة'); return; }
  window._carData = {
    plate,
    model,
    color,
    notes: document.getElementById('orderNotes')?.value.trim() || '',
  };
  goStep(3);
}

// Step 3 — Invoice preview
function renderInvoiceStep(body) {
  const items = Object.values(cart);
  const car = window._carData || {};
  const total = cartTotal();

  body.innerHTML = `
    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:1rem;">
      <button onclick="goStep(2)" style="background:none;border:none;font-size:1.1rem;cursor:pointer;color:#94A3B8;">←</button>
      <span style="font-size:1.1rem;font-weight:800;">🧾 مراجعة الطلب</span>
      <span style="margin-right:auto;font-size:.78rem;color:#94A3B8;">الخطوة 3 من 3</span>
    </div>

    <!-- Invoice card -->
    <div style="border:2px solid var(--theme-border,#e2e8f0);border-radius:14px;overflow:hidden;margin-bottom:1rem;">

      <!-- Items -->
      <div style="padding:.85rem 1rem;">
        <div style="font-size:.75rem;font-weight:800;color:#94A3B8;text-transform:uppercase;letter-spacing:.04em;margin-bottom:.6rem;">الطلبات</div>
        ${items.map(item => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:.35rem 0;border-bottom:1px dashed var(--theme-border,#f1f5f9);">
            <div>
              <span style="font-weight:700;font-size:.9rem;">${item.nameAr}</span>
              <span style="color:#94A3B8;font-size:.8rem;"> × ${item.qty}</span>
            </div>
            <span style="font-weight:700;color:var(--primary);">${(item.price * item.qty).toFixed(3)} ر.ع</span>
          </div>`).join('')}
        <div style="display:flex;justify-content:space-between;align-items:center;padding:.6rem 0 0;margin-top:.25rem;">
          <span style="font-weight:800;font-size:.95rem;">الإجمالي</span>
          <span style="font-weight:900;font-size:1.4rem;color:var(--primary);">${total.toFixed(3)} ر.ع</span>
        </div>
      </div>

      <!-- Divider -->
      <div style="border-top:2px dashed var(--theme-border,#e2e8f0);"></div>

      <!-- Car info -->
      <div style="padding:.75rem 1rem;background:var(--theme-bg-page,#f8fafc);">
        <div style="font-size:.75rem;font-weight:800;color:#94A3B8;text-transform:uppercase;letter-spacing:.04em;margin-bottom:.5rem;">🚗 بيانات التوصيل</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.35rem;font-size:.85rem;">
          <div><span style="color:#94A3B8;">اللوحة: </span><strong>${car.plate}</strong></div>
          <div><span style="color:#94A3B8;">النوع: </span><strong>${car.model}</strong></div>
          <div><span style="color:#94A3B8;">اللون: </span><strong>${car.color}</strong></div>
        </div>
        ${car.notes ? `<div style="margin-top:.5rem;background:#FEF9C3;border-radius:6px;padding:.35rem .6rem;font-size:.8rem;">💬 ${car.notes}</div>` : ''}
      </div>
    </div>

    <button class="submit-order-btn" id="submitOrderBtn" onclick="submitOrder()"
            style="background:linear-gradient(135deg, var(--primary), var(--secondary));font-size:1.05rem;">
      ✅ تأكيد الطلب وإرساله
    </button>
    <p style="text-align:center;font-size:.75rem;color:#94A3B8;margin-top:.6rem;">سيتم توصيل طلبك إلى سيارتك في الباركن</p>`;
}

// ─── Submit ───────────────────────────────────────────────────────────────────

async function submitOrder() {
  const car = window._carData || {};
  const btn = document.getElementById('submitOrderBtn');
  btn.disabled = true;
  btn.textContent = 'جاري الإرسال...';

  try {
    const res = await fetch(`/r/${RESTAURANT_SLUG}/order/place`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        car_plate:    car.plate,
        car_model:    car.model || '',
        car_color:    car.color,
        notes:        car.notes || '',
        cart: Object.values(cart).map(i => ({ id: i.id, quantity: i.qty })),
      }),
    });
    const data = await res.json();
    if (data.success) {
      window.location.href = `/r/${RESTAURANT_SLUG}/order/confirm/${data.order_number}`;
    } else {
      btn.disabled = false;
      btn.textContent = '✅ تأكيد الطلب وإرساله';
      showModalError(data.message || 'حدث خطأ، حاول مرة أخرى');
    }
  } catch {
    btn.disabled = false;
    btn.textContent = '✅ تأكيد الطلب وإرساله';
    showModalError('خطأ في الاتصال، حاول مرة أخرى');
  }
}

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // close order modal on overlay click
  document.getElementById('orderModal')?.addEventListener('click', e => {
    if (e.target.id === 'orderModal') closeOrderModal();
  });
  // close product sheet on overlay click
  document.getElementById('productSheet')?.addEventListener('click', e => {
    if (e.target.id === 'productSheet') closeProductSheet();
  });
});
