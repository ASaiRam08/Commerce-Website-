// main.js
const API = "/";
let products = [];
let cart = {}; // {product_id: qty}

function currency(v){ return Number(v).toFixed(2); }

async function fetchProducts(){
  const res = await fetch(API + "api/products");
  products = await res.json();
  renderProducts();
}

function renderProducts(){
  const container = document.getElementById("products");
  container.innerHTML = "";
  products.forEach(p=>{
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h3>${p.name}</h3>
      <p>${p.description || ""}</p>
      <div class="price">₹${currency(p.price)}</div>
      <div style="margin-top:8px">
        <span>Stock: ${p.available_qty}</span>
      </div>
      <div style="margin-top:10px">
        <input type="number" min="1" value="1" id="qty-${p.product_id}" style="width:60px" />
        <button class="btn" onclick="addToCart(${p.product_id})">Add to cart</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function addToCart(pid){
  const qtyInput = document.getElementById(`qty-${pid}`);
  const qty = Math.max(1, parseInt(qtyInput.value || 1));
  const prod = products.find(x=>x.product_id===pid);
  if(!prod) return alert("Product not found");
  if(qty > prod.available_qty) return alert("Not enough stock");
  cart[pid] = (cart[pid] || 0) + qty;
  renderCart();
}

function renderCart(){
  const el = document.getElementById("cart-items");
  el.innerHTML = "";
  let total = 0;
  for(const pid in cart){
    const qty = cart[pid];
    const p = products.find(x=>x.product_id==pid);
    if(!p) continue;
    const line = document.createElement("div");
    line.className = "cart-item";
    const lineTotal = p.price * qty;
    total += lineTotal;
    line.innerHTML = `<div>${p.name} × ${qty}</div><div>₹${currency(lineTotal)}</div>`;
    el.appendChild(line);
  }
  document.getElementById("cart-total").innerText = currency(total);
}

document.getElementById("checkout-btn").addEventListener("click", async ()=>{
  const items = Object.entries(cart).map(([product_id,quantity])=>({product_id:parseInt(product_id),quantity}));
  if(items.length===0) return alert("Cart is empty");
  document.getElementById("checkout-result").innerText = "Processing...";

  try {
    const res = await fetch(API + "api/checkout", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({items})
    });
    const j = await res.json();
    if(!res.ok) {
      document.getElementById("checkout-result").innerText = "Error: " + (j.error || res.statusText);
    } else {
      document.getElementById("checkout-result").innerText = `Order placed. ID: ${j.order_id} • Total: ₹${j.total}`;
      cart = {};
      await fetchProducts(); // refresh stock
      renderCart();
    }
  } catch (err) {
    document.getElementById("checkout-result").innerText = "Network error";
  }
});

window.onload = fetchProducts;
