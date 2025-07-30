async function generarClave() {
  const nombre = document.getElementById("nombreInput").value.trim();
  const gmail = document.getElementById("gmailInput").value.trim();
  const phone = document.getElementById("phoneInput").value.trim();

  if (!nombre || !gmail || !phone) {
    alert("Por favor completa todos los campos.");
    return;
  }

  const res = await fetch("/generate_key", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: nombre, gmail: gmail, phone: phone }),
  });
  const data = await res.json();
  if (data.success) {
    document.getElementById("mensaje").innerText = `Clave generada: ${data.key}`;
    document.getElementById("nombreInput").value = "";
    document.getElementById("gmailInput").value = "";
    document.getElementById("phoneInput").value = "";
    cargarClaves();
  } else {
    alert("Error al generar la clave.");
  }
}

function crearMensajeWhatsapp(name, key, uses) {
  const texto = `Hola ${name}, bienvenido. Tu clave es: ${key} y tienes ${uses} usos disponibles.`;
  return encodeURIComponent(texto);
}
function crearMensajeMail(name, key, uses) {
  return `Hola ${name},%0A%0ABienvenido.%0ATu clave es: ${key}%0ATienes ${uses} usos disponibles.%0A%0ASaludos.`;
}

async function cargarClaves() {
  const res = await fetch("/get_keys");
  const claves = await res.json();
  const tabla = document.getElementById("tablaClaves");
  tabla.innerHTML = "";

  claves.forEach(item => {
    const activatedEmoji = item.activated ? '✅' : '❌';

    const mailLink = `mailto:${item.gmail}?subject=Clave&body=${crearMensajeMail(item.name,item.key,item.uses)}`;
    const waLink   = `https://wa.me/${item.phone.replace(/\D/g,'')}?text=${crearMensajeWhatsapp(item.name,item.key,item.uses)}`;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="p-3 border-b">${item.name}</td>
      <td class="p-3 border-b">${item.gmail}</td>
      <td class="p-3 border-b">${item.phone}</td>
      <td class="p-3 border-b">${item.key}</td>
      <td class="p-3 border-b text-center">${activatedEmoji}</td>
      <td class="p-3 border-b text-center uses-cell" data-key="${item.key}">
        <button onclick="modificarUsos('${item.key}', ${item.uses - 1})" class="text-red-600 font-bold">➖</button>
        <span class="mx-2">${item.uses}</span>
        <button onclick="modificarUsos('${item.key}', ${item.uses + 1})" class="text-green-600 font-bold">➕</button>
      </td>
      <td class="p-3 border-b text-center space-x-2">
        <a href="${mailLink}" target="_blank">
          <img
            src="/images/GmailLogo.png"
            alt="Gmail"
            class="inline w-6 h-6 align-middle"
            onerror="this.onerror=null;this.src='/static/images/GmailLogo.png';"
          />
        </a>
        <a href="${waLink}" target="_blank">
          <img
            src="/images/WhatsApp.png"
            alt="WhatsApp"
            class="inline w-8 h-8 align-middle"
            onerror="this.onerror=null;this.src='/static/images/WhatsApp.png';"
          />
        </a>
      </td>
    `;
    tabla.appendChild(row);
  });

  document.querySelectorAll('.uses-cell').forEach(td => {
    td.ondblclick = () => editarUsosInline(td);
  });
}

function editarUsosInline(td) {
  const key = td.dataset.key;
  const original = td.innerText.trim().replace(/➖|➕/g, '').trim();

  td.innerHTML = `
    <input type="number" min="0" value="${original}" class="editable-input" style="width:4rem;text-align:center;background:transparent;border:none;">
    <button class="confirm-btn">✔️</button>
    <button class="cancel-btn">❌</button>
  `;
  const inp = td.querySelector('input');
  const btnOk = td.querySelector('.confirm-btn');
  const btnCancel = td.querySelector('.cancel-btn');

  inp.focus();

  btnOk.onclick = async () => {
    let val = parseInt(inp.value, 10);
    if (isNaN(val) || val < 0) val = 0;
    await fetch('/update_uses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, uses: val })
    });
    td.innerHTML = `
      <button onclick="modificarUsos('${key}', ${val - 1})" class="text-red-600 font-bold">➖</button>
      <span class="mx-2">${val}</span>
      <button onclick="modificarUsos('${key}', ${val + 1})" class="text-green-600 font-bold">➕</button>
    `;
    td.ondblclick = () => editarUsosInline(td);
  };

  btnCancel.onclick = () => {
    td.innerHTML = `
      <button onclick="modificarUsos('${key}', ${original - 1})" class="text-red-600 font-bold">➖</button>
      <span class="mx-2">${original}</span>
      <button onclick="modificarUsos('${key}', ${original + 1})" class="text-green-600 font-bold">➕</button>
    `;
    td.ondblclick = () => editarUsosInline(td);
  };
}

async function modificarUsos(key, usos) {
  if (usos < 0) usos = 0;
  await fetch("/update_uses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key: key, uses: usos }),
  });
  cargarClaves();
}

document.addEventListener('DOMContentLoaded', cargarClaves);
