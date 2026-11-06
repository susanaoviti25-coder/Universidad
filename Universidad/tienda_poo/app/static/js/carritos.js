// US12: histórico global de carritos (solo lectura). Selecciona un carrito para ver sus artículos.
(() => {
  "use strict";
  const raiz = document.getElementById("carritos");
  const urls = { api: raiz.dataset.urlApi, login: raiz.dataset.urlLogin };
  const el = {
    carga: document.getElementById("estado-carga"),
    error: document.getElementById("estado-error"),
    vacio: document.getElementById("estado-vacio"),
    aviso: document.getElementById("aviso-catalogo"),
    lista: document.getElementById("lista"),
    reintentar: document.getElementById("btn-reintentar"),
  };
  let controlador = null;

  function mostrar(estado) {
    el.carga.hidden = estado !== "cargando";
    el.error.hidden = estado !== "error";
    el.vacio.hidden = estado !== "vacio";
    el.lista.hidden = estado !== "ok";
  }

  function tablaItems(items) {
    if (items.length === 0) {
      const p = document.createElement("p");
      p.className = "sin-items";
      p.textContent = "Este carrito no contiene artículos.";
      return p;
    }
    const tabla = document.createElement("table");
    tabla.className = "tabla tabla-items";
    const cab = document.createElement("thead");
    const trc = document.createElement("tr");
    for (const t of ["ID producto", "Producto", "Cantidad"]) {
      const th = document.createElement("th");
      th.scope = "col";
      th.textContent = t;
      trc.appendChild(th);
    }
    cab.appendChild(trc);
    const cuerpo = document.createElement("tbody");
    for (const i of items) {
      const tr = document.createElement("tr");
      const id = document.createElement("td");
      id.textContent = i.producto_id;
      const titulo = document.createElement("td");
      titulo.textContent = i.titulo || `Producto #${i.producto_id}`;   // sin catálogo: solo el ID
      const cant = document.createElement("td");
      cant.textContent = i.cantidad;
      tr.append(id, titulo, cant);
      cuerpo.appendChild(tr);
    }
    tabla.append(cab, cuerpo);
    return tabla;
  }

  function tarjetaCarrito(c) {
    const art = document.createElement("article");
    art.className = "carrito";

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "carrito-cabecera";
    boton.setAttribute("aria-expanded", "false");
    const campos = [
      ["Carrito", `#${c.id}`],
      ["Fecha de creación", c.fecha],
      ["ID usuario", c.usuario_id],
      ["Artículos", c.items.length],
    ];
    for (const [k, v] of campos) {
      const span = document.createElement("span");
      span.className = "campo";
      const etiqueta = document.createElement("small");
      etiqueta.textContent = k;
      const valor = document.createElement("strong");
      valor.textContent = v;
      span.append(etiqueta, valor);
      boton.appendChild(span);
    }

    const panel = document.createElement("div");
    panel.className = "carrito-detalle";
    panel.hidden = true;
    panel.appendChild(tablaItems(c.items));

    boton.addEventListener("click", () => {
      panel.hidden = !panel.hidden;
      boton.setAttribute("aria-expanded", String(!panel.hidden));
      art.classList.toggle("abierta", !panel.hidden);
    });
    art.append(boton, panel);
    return art;
  }

  async function cargar() {
    if (controlador) controlador.abort();
    controlador = new AbortController();
    const { signal } = controlador;

    el.lista.replaceChildren();      // limpia datos previos antes de pedir los nuevos
    el.aviso.hidden = true;
    mostrar("cargando");
    try {
      const resp = await fetch(urls.api, { signal, headers: { Accept: "application/json" } });
      if (resp.status === 401) { window.location.href = urls.login; return; }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const datos = await resp.json();
      if (!datos || !Array.isArray(datos.carritos)) throw new Error("Respuesta inválida");
      if (datos.carritos.length === 0) { mostrar("vacio"); return; }
      el.aviso.hidden = datos.catalogo_disponible !== false;
      const fragmento = document.createDocumentFragment();
      for (const c of datos.carritos) fragmento.appendChild(tarjetaCarrito(c));
      el.lista.appendChild(fragmento);
      mostrar("ok");
    } catch (e) {
      if (e.name === "AbortError") return;
      mostrar("error");
    }
  }

  el.reintentar.addEventListener("click", cargar);
  cargar();
})();
