// 模块：图画布视口。负责 Ctrl + 滚轮缩放、按钮缩放和缩放坐标换算。
const MIN_SCALE = 0.45;
const MAX_SCALE = 2.2;
const ZOOM_STEP = 1.12;

export function mountZoomableSurface(container, surface, options = {}) {
  const contentWidth = options.width || Number.parseFloat(surface.style.width) || surface.offsetWidth || 1200;
  const contentHeight = options.height || Number.parseFloat(surface.style.height) || surface.offsetHeight || 720;
  const visibleSize = measureVisibleSize(container);
  const width = Math.max(contentWidth, visibleSize.width);
  const height = Math.max(contentHeight, visibleSize.height);
  const storageKey = options.storageKey || null;
  let scale = readScale(storageKey);

  surface.style.width = `${width}px`;
  surface.style.height = `${height}px`;

  const world = document.createElement("div");
  world.className = "graph-world";
  world.appendChild(surface);

  const controls = renderZoomControls();
  container.appendChild(controls.root);
  container.appendChild(world);

  const applyScale = () => {
    scale = clamp(scale, MIN_SCALE, MAX_SCALE);
    surface.style.transform = `scale(${scale})`;
    world.style.width = `${Math.ceil(width * scale)}px`;
    world.style.height = `${Math.ceil(height * scale)}px`;
    controls.value.textContent = `${Math.round(scale * 100)}%`;
    writeScale(storageKey, scale);
  };

  const zoomAt = (nextScale, clientX, clientY) => {
    const rect = container.getBoundingClientRect();
    const localX = clientX - rect.left;
    const localY = clientY - rect.top;
    const worldX = (container.scrollLeft + localX) / scale;
    const worldY = (container.scrollTop + localY) / scale;
    scale = clamp(nextScale, MIN_SCALE, MAX_SCALE);
    applyScale();
    container.scrollLeft = worldX * scale - localX;
    container.scrollTop = worldY * scale - localY;
  };

  const zoomFromCenter = (nextScale) => {
    const rect = container.getBoundingClientRect();
    zoomAt(nextScale, rect.left + rect.width / 2, rect.top + rect.height / 2);
  };

  container.addEventListener("wheel", (event) => {
    if (!event.ctrlKey) {
      return;
    }
    event.preventDefault();
    const direction = event.deltaY > 0 ? 1 / ZOOM_STEP : ZOOM_STEP;
    zoomAt(scale * direction, event.clientX, event.clientY);
  }, { passive: false });

  installDragPan(container);

  controls.zoomOut.addEventListener("click", () => zoomFromCenter(scale / ZOOM_STEP));
  controls.zoomIn.addEventListener("click", () => zoomFromCenter(scale * ZOOM_STEP));
  controls.reset.addEventListener("click", () => zoomFromCenter(1));
  controls.fit.addEventListener("click", () => {
    const fitScale = Math.min(
      MAX_SCALE,
      Math.max(MIN_SCALE, Math.min(container.clientWidth / width, container.clientHeight / height) * 0.96),
    );
    zoomFromCenter(fitScale);
  });

  applyScale();

  return {
    getScale: () => scale,
    setScale: (nextScale) => zoomFromCenter(nextScale),
    world,
  };
}

function measureVisibleSize(container) {
  const rect = container.getBoundingClientRect();
  return {
    width: Math.max(1, Math.floor(rect.width || container.clientWidth || 0)),
    height: Math.max(1, Math.floor(rect.height || container.clientHeight || 0)),
  };
}

function renderZoomControls() {
  const root = document.createElement("div");
  root.className = "graph-zoom-controls";
  root.innerHTML = `
    <button type="button" data-zoom="out" title="缩小">-</button>
    <button type="button" data-zoom="reset" title="重置缩放"><span data-zoom-value>100%</span></button>
    <button type="button" data-zoom="in" title="放大">+</button>
    <button type="button" data-zoom="fit" title="适应视图">适应</button>
  `;
  return {
    root,
    value: root.querySelector("[data-zoom-value]"),
    zoomOut: root.querySelector('[data-zoom="out"]'),
    reset: root.querySelector('[data-zoom="reset"]'),
    zoomIn: root.querySelector('[data-zoom="in"]'),
    fit: root.querySelector('[data-zoom="fit"]'),
  };
}

function installDragPan(container) {
  let panning = null;

  container.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || isInteractiveTarget(event.target)) {
      return;
    }
    panning = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      scrollLeft: container.scrollLeft,
      scrollTop: container.scrollTop,
    };
    container.classList.add("is-panning");
    container.setPointerCapture(event.pointerId);
    event.preventDefault();
  });

  container.addEventListener("pointermove", (event) => {
    if (!panning || panning.pointerId !== event.pointerId) {
      return;
    }
    container.scrollLeft = panning.scrollLeft - (event.clientX - panning.startX);
    container.scrollTop = panning.scrollTop - (event.clientY - panning.startY);
  });

  const stopPanning = (event) => {
    if (!panning || panning.pointerId !== event.pointerId) {
      return;
    }
    panning = null;
    container.classList.remove("is-panning");
  };
  container.addEventListener("pointerup", stopPanning);
  container.addEventListener("pointercancel", stopPanning);
  container.addEventListener("lostpointercapture", () => {
    panning = null;
    container.classList.remove("is-panning");
  });
}

function isInteractiveTarget(target) {
  return Boolean(target?.closest?.([
    "button",
    "a",
    "input",
    "textarea",
    "select",
    "summary",
    ".flow-edge-hit",
    ".layer-inspector",
    ".graph-zoom-controls",
  ].join(",")));
}

function readScale(storageKey) {
  if (!storageKey) {
    return 1;
  }
  try {
    const value = Number.parseFloat(window.localStorage.getItem(storageKey) || "1");
    return Number.isFinite(value) ? clamp(value, MIN_SCALE, MAX_SCALE) : 1;
  } catch {
    return 1;
  }
}

function writeScale(storageKey, scale) {
  if (!storageKey) {
    return;
  }
  try {
    window.localStorage.setItem(storageKey, String(round(scale)));
  } catch {
    // localStorage 不可用时，当前会话缩放仍然生效。
  }
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function round(value) {
  return Number.parseFloat(value.toFixed(3));
}
