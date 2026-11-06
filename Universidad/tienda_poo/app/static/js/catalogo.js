// US03 (catálogo + loading + error/reintentar) y US04 (filtro por categoría).
(() => {
  "use strict";
  const raiz = document.getElementById("catalogo");
  const urls = {
    productos: raiz.dataset.urlProductos,
    categorias: raiz.dataset.urlCategorias,
    detalle: raiz.dataset.urlDetalle,   // termina en /0 -> se reemplaza por el id
    login: raiz.dataset.urlLogin,
  };
  const el = {
    filtros: document.getElementById("filtros"),
    grilla: document.getElementById("grilla"),
    carga: document.getElementById("estado-carga"),
    error: document.getElementById("estado-error"),
    vacio: document.getElementById("estado-vacio"),
    reintentar: document.getElementById("btn-reintentar"),
  };
  const dinero = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
  const TAMANO_LOTE = 8;

  let categoriaActiva = null;   // null = "Ver todos"
  let controlador = null;       // AbortController de la petición en curso
  let versionRender = 0;        // invalida renders por lotes obsoletos

  function mostrar(estado) {
    el.carga.hidden = estado !== "cargando";
    el.error.hidden = estado !== "error";
    el.vacio.hidden = estado !== "vacio";
  }

  async function pedirJSON(url, signal) {
    const resp = await fetch(url, { signal, headers: { Accept: "application/json" } });
    if (resp.status === 401) { window.location.href = urls.login; throw new Error("401"); }
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  function crearTarjeta(p) {
    const a = document.createElement("a");
    a.className = "tarjeta";
    a.href = urls.detalle.replace(/0$/, String(p.id));

    const caja = document.createElement("div");
    caja.className = "tarjeta-imagen";
    const img = new Image();
    img.loading = "lazy";      // descarga en segundo plano, sin congelar la UI
    img.decoding = "async";
    img.alt = p.title;
    img.src = p.image;
    caja.appendChild(img);

    const cuerpo = document.createElement("div");
    cuerpo.className = "tarjeta-cuerpo";
    const titulo = document.createElement("h2");
    titulo.className = "tarjeta-titulo";
    titulo.textContent = p.title;
    const precio = document.createElement("p");
    precio.className = "precio";
    precio.textContent = dinero.format(p.price);
    cuerpo.append(titulo, precio);

    a.append(caja, cuerpo);
    return a;
  }

  // Render por lotes: no se insertan todos los nodos de golpe.
  function renderizarPorLotes(productos) {
    const version = ++versionRender;
    let i = 0;
    const siguienteLote = () => {
      if (version !== versionRender) return;
      const fragmento = document.createDocumentFragment();
      for (const p of productos.slice(i, i + TAMANO_LOTE)) fragmento.appendChild(crearTarjeta(p));
      el.grilla.appendChild(fragmento);
      i += TAMANO_LOTE;
      if (i < productos.length) requestAnimationFrame(siguienteLote);
    };
    siguienteLote();
  }

  async function cargarProductos(categoria) {
    if (controlador) controlador.abort();          // descarta la petición anterior
    controlador = new AbortController();
    const { signal } = controlador;

    versionRender++;
    el.grilla.replaceChildren();                   // limpia datos previos antes de pedir los nuevos
    mostrar("cargando");
    try {
      const url = categoria
        ? `${urls.productos}?categoria=${encodeURIComponent(categoria)}`
        : urls.productos;
      const productos = await pedirJSON(url, signal);
      if (signal.aborted) return;
      if (productos.length === 0) { mostrar("vacio"); return; }
      mostrar("ok");
      renderizarPorLotes(productos);
    } catch (e) {
      if (e.name === "AbortError") return;
      mostrar("error");
    }
  }

  function seleccionarCategoria(categoria) {
    // Pulsar el chip activo (o "Ver todos") quita el filtro.
    categoriaActiva = categoria === categoriaActiva ? null : categoria;
    pintarChips();
    cargarProductos(categoriaActiva);
  }

  let categorias = [];
  function pintarChips() {
    el.filtros.replaceChildren();
    const crear = (texto, valor) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "chip";
      b.textContent = texto;
      b.setAttribute("aria-pressed", String(valor === categoriaActiva));
      b.addEventListener("click", () => (valor === null ? quitarFiltro() : seleccionarCategoria(valor)));
      return b;
    };
    el.filtros.appendChild(crear("Ver todos", null));
    for (const c of categorias) el.filtros.appendChild(crear(c, c));
  }

  function quitarFiltro() {
    categoriaActiva = null;
    pintarChips();
    cargarProductos(null);
  }

  async function cargarCategorias() {
    try {
      categorias = await pedirJSON(urls.categorias);
    } catch {
      categorias = [];     // el catálogo sigue usable aunque fallen las categorías
    }
    pintarChips();
  }

  el.reintentar.addEventListener("click", () => cargarProductos(categoriaActiva));
  cargarCategorias();
  cargarProductos(null);
})();
