async function generarClave() {
    const nombre = document.getElementById('nombreInput').value;
    if (!nombre) return alert('Escribe un nombre');

    const res = await fetch('/generate_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nombre })
    });
    const data = await res.json();
    if (data.success) {
        document.getElementById('mensaje').innerText = `Clave generada: ${data.key}`;
        document.getElementById('nombreInput').value = '';
        cargarClaves();
    }
}

async function cargarClaves() {
    const res = await fetch('/get_keys');
    const claves = await res.json();
    const tabla = document.getElementById('tablaClaves');
    tabla.innerHTML = '';

    claves.forEach(item => {
        tabla.innerHTML += `
            <tr>
              <td class="p-2">${item.name}</td>
              <td class="p-2">${item.key}</td>
              <td class="p-2 text-center">${item.uses}</td>
              <td class="p-2">
                <button onclick="modificarUsos('${item.key}', ${item.uses + 1})" class="text-green-600">➕</button>
                <button onclick="modificarUsos('${item.key}', ${item.uses - 1})" class="text-red-600">➖</button>
              </td>
            </tr>
        `;
    });
}

async function modificarUsos(clave, usos) {
    if (usos < 0) usos = 0;
    await fetch('/update_uses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: clave, uses: usos })
    });
    cargarClaves();
}

document.addEventListener('DOMContentLoaded', cargarClaves);

