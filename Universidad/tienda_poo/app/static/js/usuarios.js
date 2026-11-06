// US11: directorio de usuarios (solo lectura) con loading, error/reintentar, búsqueda y detalle.
(() => {
  "use strict";
  const raiz = document.getElementById("usuarios");
  const urls = { api: raiz.dataset.urlApi, login: raiz.dataset.urlLogin };
  const el = {
    buscar: document.getElementById("buscar"),
    contador: document.getElementById("contador"),
    carga: document.getElementById("estado-carga"),
    error: document.getElementById("estado-error"),
    vacio: document.getElementById("estado-vacio"),
    tabla: document.getElementById("tabla-contenedor"),
    cuerpo: document.getElementById("cuerpo"),
    reintentar: document.getElementById("btn-reintentar"),
  };

  let usuarios = [];
  let controlador = null;

  function mostrar(estado) {
    el.carga.hidden = estado !== "cargando";
    el.error.hidden = estado !== "error";
    el.vacio.hidden = estado !== "vacio";
    el.tabla.hidden = estado !== "ok";
  }

  const dato = (valor) => (valor && String(valor).trim() ? valor : "—");

  function celda(texto) {
    const td = document.createElement("td");
    td.textContent = dato(texto);
    return td;
  }

  function filaDetalle(u) {
    const tr = document.createElement("tr");
    tr.className = "fila-detalle";
    tr.hidden = true;
    const td = document.createElement("td");
    td.colSpan = 4;
    const d = u.direccion || {};
    const coordenadas = d.lat || d.lng ? `${d.lat || "—"}, ${d.lng || "—"}` : "No disponible";
    const lineas = [
      ["Calle", d.calle, true],
      ["Ciudad", d.ciudad, true],
      ["Código postal", d.codigo_postal, false],
      ["Coordenadas", coordenadas, false],
    ];
    const dl = document.createElement("dl");
    dl.className = "direccion";
    for (const [k, v, capitalizar] of lineas) {
      const dt = document.createElement("dt");
      dt.textContent = k;
      const dd = document.createElement("dd");
      if (capitalizar) dd.className = "cap";    // la API devuelve calle/ciudad en minúsculas
      dd.textContent = dato(v);
      dl.append(dt, dd);
    }
    td.appendChild(dl);
    tr.appendChild(td);
    return tr;
  }

  function filaUsuario(u) {
    const tr = document.createElement("tr");
    tr.className = "fila-usuario";
    tr.tabIndex = 0;
    tr.setAttribute("aria-expanded", "false");
    tr.append(celda(u.nombre_completo), celda(u.email), celda(u.telefono), celda(u.username));
    const detalle = filaDetalle(u);
    const alternar = () => {
      detalle.hidden = !detalle.hidden;
      tr.setAttribute("aria-expanded", String(!detalle.hidden));
      tr.classList.toggle("abierta", !detalle.hidden);
    };
    tr.addEventListener("click", alternar);
    tr.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); alternar(); }
    });
    return [tr, detalle];
  }

  function normalizar(t) {
    return String(t || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function pintar() {
    const q = normalizar(el.buscar.value.trim());
    const visibles = q
      ? usuarios.filter((u) =>
          normalizar([u.nombre_completo, u.email, u.telefono, u.username].join(" ")).includes(q))
      : usuarios;
    el.cuerpo.replaceChildren();
    const fragmento = document.createDocumentFragment();
    for (const u of visibles) fragmento.append(...filaUsuario(u));
    el.cuerpo.appendChild(fragmento);
    el.contador.textContent = `${visibles.length} de ${usuarios.length} usuarios`;
    mostrar(visibles.length === 0 ? "vacio" : "ok");
  }

  async function cargar() {
    if (controlador) controlador.abort();
    controlador = new AbortController();
    const { signal } = controlador;

    usuarios = [];
    el.cuerpo.replaceChildren();     // limpia datos previos antes de pedir los nuevos
    el.buscar.disabled = true;
    el.contador.textContent = "";
    mostrar("cargando");
    try {
      const resp = await fetch(urls.api, { signal, headers: { Accept: "application/json" } });
      if (resp.status === 401) { window.location.href = urls.login; return; }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const datos = await resp.json();
      if (!Array.isArray(datos)) throw new Error("Respuesta inválida");
      usuarios = datos;
      el.buscar.disabled = false;
      pintar();
    } catch (e) {
      if (e.name === "AbortError") return;
      mostrar("error");
    }
  }

  el.buscar.addEventListener("input", pintar);
  el.reintentar.addEventListener("click", cargar);
  cargar();
})();
