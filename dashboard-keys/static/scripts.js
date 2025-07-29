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
    document.getElementById(
      "mensaje"
    ).innerText = `Clave generada: ${data.key}`;
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

  claves.forEach((item) => {
    const activatedText = item.activated ? "Sí" : "No";
    const mailLink = `mailto:${
      item.gmail
    }?subject=Clave%20de%20software&body=${crearMensajeMail(
      item.name,
      item.key,
      item.uses
    )}`;
    const phoneNum = item.phone.replace(/\D/g, ""); // Quitar cualquier caracter no numérico
    const waLink = `https://wa.me/${phoneNum}?text=${crearMensajeWhatsapp(
      item.name,
      item.key,
      item.uses
    )}`;

    tabla.innerHTML += `
            <tr>
              <td class="p-3 border-b">${item.name}</td>
              <td class="p-3 border-b">${item.gmail}</td>
              <td class="p-3 border-b">${item.phone}</td>
              <td class="p-3 border-b">${item.key}</td>
              <td class="p-3 border-b text-center">${item.uses}</td>
              <td class="p-3 border-b text-center">${activatedText}</td>
              <td class="p-3 border-b text-center space-x-2">
                <button onclick="modificarUsos('${item.key}', ${
      item.uses + 1
    })" class="text-green-600 font-bold">➕</button>
                <button onclick="modificarUsos('${item.key}', ${
      item.uses - 1
    })" class="text-red-600 font-bold">➖</button>
                <a href="${mailLink}" target="_blank" class="text-blue-600 underline">🔵</a>
                <a href="${waLink}" target="_blank" class="text-green-600 underline">🟢</a>
              </td>
            </tr>
        `;
  });
}

async function modificarUsos(clave, usos) {
  if (usos < 0) usos = 0;

  await fetch("/update_uses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key: clave, uses: usos }),
  });

  cargarClaves();
}

document.addEventListener("DOMContentLoaded", cargarClaves);
