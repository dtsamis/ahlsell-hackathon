// FloorCAD YOLOv8n Interactive Frontend Application

const CATEGORY_COLORS = {
  // Doors & Openings: Cyan / Sky
  single_door: "#06b6d4",
  double_door: "#06b6d4",
  sliding_door: "#0ea5e9",
  opening_symbol: "#38bdf8",
  // Windows: Sky Blue
  window: "#0284c7",
  bay_window: "#0369a1",
  blind_window: "#0284c7",
  // Vertical circulation & transport: Emerald
  elevator: "#10b981",
  escalator: "#059669",
  stair: "#34d399",
  railing: "#6ee7b7",
  parking: "#047857",
  // Furniture: Violet / Purple
  bed: "#a855f7",
  bedside_cupboard: "#c084fc",
  chair: "#9333ea",
  sofa: "#7e22ce",
  table: "#c026d3",
  wardrobe: "#d946ef",
  tv_cabinet: "#a21caf",
  half_height_cabinet: "#86198f",
  high_cabinet: "#701a75",
  // Sanitary: Rose
  bath: "#f43f5e",
  bath_tub: "#e11d48",
  toilet: "#fb7185",
  squat_toilet: "#f43f5e",
  urinal: "#be123c",
  sink: "#fda4af",
  washing_machine: "#e11d48",
  // Kitchen: Amber
  gas_stove: "#f59e0b",
  refrigerator: "#d97706",
  // Structure: Orange
  wall: "#ea580c",
};
const DEFAULT_COLOR = "#f97316";

const state = {
  currentFile: null,
  currentImage: null,
  currentImageSrc: null,
  lastPrediction: null,
  classes: {},
  selectedClasses: new Set(),
  imgsz: 1024,
  viewMode: "interactive", // 'interactive' | 'sideBySide' | 'raw'
  scale: 1.0,
  panX: 0,
  panY: 0,
  isDragging: false,
  dragStartX: 0,
  dragStartY: 0,
  hoveredDetId: null,
  selectedDetId: null,
  showLabels: true,
  showScores: true,
  isDrawerCollapsed: false,
};

// DOM Elements
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const samplesList = document.getElementById("samplesList");
const confSlider = document.getElementById("confSlider");
const confValue = document.getElementById("confValue");
const iouSlider = document.getElementById("iouSlider");
const iouValue = document.getElementById("iouValue");
const detectBtn = document.getElementById("detectBtn");
const classListContainer = document.getElementById("classListContainer");
const classSearchInput = document.getElementById("classSearchInput");
const selectAllClasses = document.getElementById("selectAllClasses");
const clearAllClasses = document.getElementById("clearAllClasses");
const selectedClassCount = document.getElementById("selectedClassCount");
const deviceBadge = document.getElementById("deviceBadge");

const emptyState = document.getElementById("emptyState");
const loadingOverlay = document.getElementById("loadingOverlay");
const elapsedTimer = document.getElementById("elapsedTimer");
const canvasContainer = document.getElementById("canvasContainer");
const mainCanvas = document.getElementById("mainCanvas");
const ctx = mainCanvas.getContext("2d");
const detectionTooltip = document.getElementById("detectionTooltip");
const tooltipClass = document.getElementById("tooltipClass");
const tooltipConf = document.getElementById("tooltipConf");
const tooltipBbox = document.getElementById("tooltipBbox");

const splitViewContainer = document.getElementById("splitViewContainer");
const splitOriginalImg = document.getElementById("splitOriginalImg");
const splitAnnotatedImg = document.getElementById("splitAnnotatedImg");
const rawViewContainer = document.getElementById("rawViewContainer");
const rawAnnotatedImg = document.getElementById("rawAnnotatedImg");

const viewInteractiveBtn = document.getElementById("viewInteractiveBtn");
const viewSideBySideBtn = document.getElementById("viewSideBySideBtn");
const viewRawAnnotatedBtn = document.getElementById("viewRawAnnotatedBtn");

const zoomInBtn = document.getElementById("zoomInBtn");
const zoomOutBtn = document.getElementById("zoomOutBtn");
const resetViewBtn = document.getElementById("resetViewBtn");
const zoomLevel = document.getElementById("zoomLevel");
const toggleLabelsCheckbox = document.getElementById("toggleLabelsCheckbox");
const toggleConfCheckbox = document.getElementById("toggleConfCheckbox");

const exportDropdownBtn = document.getElementById("exportDropdownBtn");
const exportMenu = document.getElementById("exportMenu");
const exportImageBtn = document.getElementById("exportImageBtn");
const exportJsonBtn = document.getElementById("exportJsonBtn");
const exportCsvBtn = document.getElementById("exportCsvBtn");

const statTotal = document.getElementById("statTotal");
const statClasses = document.getElementById("statClasses");
const statLatency = document.getElementById("statLatency");
const statResolution = document.getElementById("statResolution");
const classBreakdownContainer = document.getElementById("classBreakdownContainer");
const detectionsTableBody = document.getElementById("detectionsTableBody");
const toggleDrawerBtn = document.getElementById("toggleDrawerBtn");
const drawerBody = document.getElementById("drawerBody");
const drawerToggleIcon = document.getElementById("drawerToggleIcon");
const drawerToggleText = document.getElementById("drawerToggleText");

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await checkHealthAndInfo();
  await loadSamples();
});

async function checkHealthAndInfo() {
  try {
    const [healthRes, classesRes] = await Promise.all([
      fetch("/api/health").then((r) => r.json()),
      fetch("/api/classes").then((r) => r.json()),
    ]);

    deviceBadge.innerHTML = `<i class="fa-solid fa-microchip mr-1"></i>${healthRes.device || "Ready"}`;
    state.classes = classesRes.classes || {};

    // Select all classes by default
    state.selectedClasses = new Set(Object.keys(state.classes).map(Number));
    renderClassCheckboxes();
  } catch (err) {
    console.error("Health check error:", err);
    deviceBadge.innerHTML = `<i class="fa-solid fa-circle-exclamation text-amber-400 mr-1"></i>Offline`;
  }
}

function renderClassCheckboxes(filterText = "") {
  classListContainer.innerHTML = "";
  const filter = filterText.toLowerCase().trim();

  const entries = Object.entries(state.classes);
  let visibleCount = 0;

  entries.forEach(([idStr, name]) => {
    const id = Number(idStr);
    if (filter && !name.toLowerCase().includes(filter)) return;
    visibleCount++;

    const isChecked = state.selectedClasses.has(id);
    const color = CATEGORY_COLORS[name] || DEFAULT_COLOR;

    const row = document.createElement("label");
    row.className = "flex items-center space-x-2 py-1 px-1.5 rounded hover:bg-slate-800/60 cursor-pointer";
    row.innerHTML = `
      <input type="checkbox" data-class-id="${id}" ${isChecked ? "checked" : ""} class="accent-cyan-500 rounded" />
      <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background-color: ${color}"></span>
      <span class="text-slate-300 font-mono text-[11px] truncate flex-1">${name}</span>
      <span class="text-slate-600 text-[10px] font-mono">#${id}</span>
    `;

    row.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) {
        state.selectedClasses.add(id);
      } else {
        state.selectedClasses.delete(id);
      }
      updateSelectedClassCount();
    });

    classListContainer.appendChild(row);
  });

  if (visibleCount === 0) {
    classListContainer.innerHTML = `<div class="text-center text-slate-500 py-3">No matching symbols</div>`;
  }
  updateSelectedClassCount();
}

function updateSelectedClassCount() {
  selectedClassCount.textContent = state.selectedClasses.size;
}

async function loadSamples() {
  try {
    const res = await fetch("/api/samples");
    const data = await res.json();
    samplesList.innerHTML = "";

    if (!data.samples || data.samples.length === 0) {
      samplesList.innerHTML = `<div class="col-span-2 text-xs text-slate-500">No demo samples available</div>`;
      return;
    }

    data.samples.forEach((sample) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sample-card text-left p-2 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-cyan-500/80 transition flex items-center space-x-2";
      btn.innerHTML = `
        <div class="w-7 h-7 rounded bg-slate-800 flex items-center justify-center text-cyan-400 text-xs">
          <i class="fa-solid fa-map"></i>
        </div>
        <div class="truncate flex-1">
          <div class="text-xs font-medium text-slate-200 truncate">${sample.name}</div>
          <div class="text-[10px] text-slate-500">Click to run</div>
        </div>
      `;
      btn.addEventListener("click", () => loadSampleByUrl(sample.url, sample.filename));
      samplesList.appendChild(btn);
    });
  } catch (err) {
    console.error("Error loading samples:", err);
  }
}

async function loadSampleByUrl(url, filename) {
  try {
    showLoading(true);
    const res = await fetch(url);
    const blob = await res.blob();
    const file = new File([blob], filename, { type: blob.type });
    handleImageFile(file, true);
  } catch (err) {
    alert("Failed to load sample image: " + err.message);
    showLoading(false);
  }
}

function setupEventListeners() {
  // Drag & Drop
  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleImageFile(e.target.files[0]);
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("border-cyan-500", "bg-cyan-950/20");
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("border-cyan-500", "bg-cyan-950/20");
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-cyan-500", "bg-cyan-950/20");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageFile(e.dataTransfer.files[0]);
    }
  });

  // Slider inputs
  confSlider.addEventListener("input", (e) => {
    confValue.textContent = Number(e.target.value).toFixed(2);
  });
  iouSlider.addEventListener("input", (e) => {
    iouValue.textContent = Number(e.target.value).toFixed(2);
  });

  // Image size selector buttons
  document.querySelectorAll(".imgsz-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".imgsz-btn").forEach((b) => {
        b.classList.remove("border-cyan-500", "bg-cyan-950/60", "text-cyan-300", "font-bold");
        b.classList.add("border-slate-700", "bg-slate-800", "text-slate-300");
      });
      btn.classList.add("border-cyan-500", "bg-cyan-950/60", "text-cyan-300", "font-bold");
      btn.classList.remove("border-slate-700", "bg-slate-800", "text-slate-300");
      state.imgsz = parseInt(btn.dataset.size, 10);
    });
  });

  // Class filtering search
  classSearchInput.addEventListener("input", (e) => {
    renderClassCheckboxes(e.target.value);
  });

  selectAllClasses.addEventListener("click", () => {
    state.selectedClasses = new Set(Object.keys(state.classes).map(Number));
    renderClassCheckboxes(classSearchInput.value);
  });

  clearAllClasses.addEventListener("click", () => {
    state.selectedClasses.clear();
    renderClassCheckboxes(classSearchInput.value);
  });

  // Detect action button
  detectBtn.addEventListener("click", () => {
    if (state.currentFile) {
      runDetection();
    } else {
      alert("Please upload a CAD floor plan image first or select one of the demo samples.");
    }
  });

  // View mode switcher
  viewInteractiveBtn.addEventListener("click", () => setViewMode("interactive"));
  viewSideBySideBtn.addEventListener("click", () => setViewMode("sideBySide"));
  viewRawAnnotatedBtn.addEventListener("click", () => setViewMode("raw"));

  // Zoom and pan controls
  zoomInBtn.addEventListener("click", () => adjustZoom(1.25));
  zoomOutBtn.addEventListener("click", () => adjustZoom(0.8));
  resetViewBtn.addEventListener("click", () => resetZoom());

  toggleLabelsCheckbox.addEventListener("change", (e) => {
    state.showLabels = e.target.checked;
    drawCanvas();
  });

  toggleConfCheckbox.addEventListener("change", (e) => {
    state.showScores = e.target.checked;
    drawCanvas();
  });

  // Drawer Toggle
  toggleDrawerBtn.addEventListener("click", () => {
    state.isDrawerCollapsed = !state.isDrawerCollapsed;
    if (state.isDrawerCollapsed) {
      drawerBody.classList.add("hidden");
      drawerToggleIcon.classList.replace("fa-chevron-down", "fa-chevron-up");
      drawerToggleText.textContent = "Expand Details";
    } else {
      drawerBody.classList.remove("hidden");
      drawerToggleIcon.classList.replace("fa-chevron-up", "fa-chevron-down");
      drawerToggleText.textContent = "Collapse Details";
    }
  });

  // Export menu
  exportDropdownBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    exportMenu.classList.toggle("hidden");
  });
  document.addEventListener("click", () => exportMenu.classList.add("hidden"));

  exportImageBtn.addEventListener("click", exportAnnotatedImage);
  exportJsonBtn.addEventListener("click", exportDetectionsJson);
  exportCsvBtn.addEventListener("click", exportDetectionsCsv);

  // Canvas Mouse Pan & Zoom
  setupCanvasInteractions();
}

function handleImageFile(file, autoRun = true) {
  state.currentFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    state.currentImageSrc = e.target.result;
    const img = new Image();
    img.onload = () => {
      state.currentImage = img;
      emptyState.classList.add("hidden");
      canvasContainer.classList.remove("hidden");

      statResolution.textContent = `${img.naturalWidth} x ${img.naturalHeight} px`;
      splitOriginalImg.src = state.currentImageSrc;

      resetZoom();
      if (autoRun) {
        runDetection();
      } else {
        drawCanvas();
      }
    };
    img.src = state.currentImageSrc;
  };
  reader.readAsDataURL(file);
}

async function runDetection() {
  if (!state.currentFile) return;

  showLoading(true);
  const formData = new FormData();
  formData.append("file", state.currentFile);
  formData.append("conf", confSlider.value);
  formData.append("iou", iouSlider.value);
  formData.append("imgsz", state.imgsz);

  // Class filtering
  if (state.selectedClasses.size > 0 && state.selectedClasses.size < Object.keys(state.classes).length) {
    formData.append("classes", Array.from(state.selectedClasses).join(","));
  }
  formData.append("return_annotated", "true");

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Detection failed");
    }

    const data = await res.json();
    state.lastPrediction = data;

    renderResults(data);
    drawCanvas();
  } catch (err) {
    alert("Inference Error: " + err.message);
  } finally {
    showLoading(false);
  }
}

function renderResults(data) {
  // Stats
  statTotal.textContent = data.summary.total_detections;
  statClasses.textContent = Object.keys(data.summary.class_counts).length;
  statLatency.textContent = `${data.summary.inference_time_ms} ms`;
  statResolution.textContent = `${data.image_dimensions.width} x ${data.image_dimensions.height} px`;

  // Annotated image updates
  if (data.annotated_image_base64) {
    splitAnnotatedImg.src = data.annotated_image_base64;
    rawAnnotatedImg.src = data.annotated_image_base64;
  }

  // Symbol counts breakdown chips
  classBreakdownContainer.innerHTML = "";
  const counts = Object.entries(data.summary.class_counts).sort((a, b) => b[1] - a[1]);

  if (counts.length === 0) {
    classBreakdownContainer.innerHTML = `<span class="text-xs text-slate-500">No symbols detected at current confidence threshold.</span>`;
  } else {
    counts.forEach(([cname, count]) => {
      const color = CATEGORY_COLORS[cname] || DEFAULT_COLOR;
      const chip = document.createElement("span");
      chip.className = "inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-mono font-medium border";
      chip.style.backgroundColor = `${color}20`;
      chip.style.borderColor = `${color}80`;
      chip.style.color = "#ffffff";
      chip.innerHTML = `
        <span class="w-2 h-2 rounded-full" style="background-color: ${color}"></span>
        <span>${cname}:</span>
        <span class="font-bold">${count}</span>
      `;
      classBreakdownContainer.appendChild(chip);
    });
  }

  // Detections table
  detectionsTableBody.innerHTML = "";
  if (!data.detections || data.detections.length === 0) {
    detectionsTableBody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500">No symbols detected</td></tr>`;
    return;
  }

  data.detections.forEach((det) => {
    const color = CATEGORY_COLORS[det.class_name] || DEFAULT_COLOR;
    const tr = document.createElement("tr");
    tr.className = "table-detection-row hover:bg-slate-800/60";
    tr.dataset.detId = det.id;

    tr.innerHTML = `
      <td class="py-1.5 px-2 text-slate-500">${det.id}</td>
      <td class="py-1.5 px-2">
        <span class="inline-flex items-center space-x-1.5">
          <span class="w-2 h-2 rounded-full" style="background-color: ${color}"></span>
          <span class="text-slate-200 font-semibold">${det.class_name}</span>
        </span>
      </td>
      <td class="py-1.5 px-2">
        <div class="flex items-center space-x-2">
          <div class="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div class="h-full bg-cyan-400 rounded-full" style="width: ${det.confidence * 100}%"></div>
          </div>
          <span class="text-cyan-400 text-[11px]">${(det.confidence * 100).toFixed(1)}%</span>
        </div>
      </td>
      <td class="py-1.5 px-2 text-slate-400 text-[11px]">
        [${det.bbox.x1}, ${det.bbox.y1}, ${det.bbox.x2}, ${det.bbox.y2}] (${det.bbox.width}x${det.bbox.height})
      </td>
      <td class="py-1.5 px-2">
        <button type="button" class="px-2 py-0.5 rounded text-[10px] bg-slate-800 hover:bg-cyan-950 text-cyan-400 border border-slate-700 hover:border-cyan-500">
          Spotlight
        </button>
      </td>
    `;

    // Row hover & click handlers
    tr.addEventListener("mouseenter", () => {
      state.hoveredDetId = det.id;
      drawCanvas();
    });
    tr.addEventListener("mouseleave", () => {
      state.hoveredDetId = null;
      drawCanvas();
    });
    tr.addEventListener("click", () => {
      spotlightDetection(det);
    });

    detectionsTableBody.appendChild(tr);
  });
}

function spotlightDetection(det) {
  state.selectedDetId = det.id;
  // Center canvas on detection
  const canvasW = mainCanvas.width;
  const canvasH = mainCanvas.height;
  const targetX = (det.bbox.x1 + det.bbox.width / 2);
  const targetY = (det.bbox.y1 + det.bbox.height / 2);

  state.scale = Math.max(state.scale, 2.0);
  state.panX = (canvasW / 2) - (targetX * state.scale);
  state.panY = (canvasH / 2) - (targetY * state.scale);

  applyCanvasTransform();
  drawCanvas();

  // Highlight corresponding row
  document.querySelectorAll(".table-detection-row").forEach((r) => {
    if (r.dataset.detId == det.id) {
      r.classList.add("selected");
      r.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      r.classList.remove("selected");
    }
  });
}

function setViewMode(mode) {
  state.viewMode = mode;
  [viewInteractiveBtn, viewSideBySideBtn, viewRawAnnotatedBtn].forEach((btn) => btn.classList.remove("active"));

  canvasContainer.classList.add("hidden");
  splitViewContainer.classList.add("hidden");
  rawViewContainer.classList.add("hidden");

  if (mode === "interactive") {
    viewInteractiveBtn.classList.add("active");
    if (state.currentImage) canvasContainer.classList.remove("hidden");
  } else if (mode === "sideBySide") {
    viewSideBySideBtn.classList.add("active");
    splitViewContainer.classList.remove("hidden");
  } else if (mode === "raw") {
    viewRawAnnotatedBtn.classList.add("active");
    rawViewContainer.classList.remove("hidden");
  }
}

// Canvas Rendering
function drawCanvas() {
  if (!state.currentImage) return;

  const img = state.currentImage;
  mainCanvas.width = img.naturalWidth;
  mainCanvas.height = img.naturalHeight;

  ctx.clearRect(0, 0, mainCanvas.width, mainCanvas.height);
  ctx.drawImage(img, 0, 0);

  if (!state.lastPrediction || !state.lastPrediction.detections) return;

  const detections = state.lastPrediction.detections;

  detections.forEach((det) => {
    const isHovered = state.hoveredDetId === det.id;
    const isSelected = state.selectedDetId === det.id;
    const baseColor = CATEGORY_COLORS[det.class_name] || DEFAULT_COLOR;

    const x = det.bbox.x1;
    const y = det.bbox.y1;
    const w = det.bbox.width;
    const h = det.bbox.height;

    // Draw box fill if hovered/selected
    if (isHovered || isSelected) {
      ctx.fillStyle = `${baseColor}40`;
      ctx.fillRect(x, y, w, h);
    }

    // Draw bounding box
    ctx.lineWidth = isSelected ? 5 : (isHovered ? 4 : 2.5);
    ctx.strokeStyle = isSelected ? "#ffffff" : (isHovered ? "#38bdf8" : baseColor);
    ctx.strokeRect(x, y, w, h);

    // Optional corner brackets CAD style
    drawCADCorners(ctx, x, y, w, h, isHovered || isSelected ? "#38bdf8" : baseColor);

    // Draw label
    if (state.showLabels) {
      let label = det.class_name;
      if (state.showScores) {
        label += ` ${Math.round(det.confidence * 100)}%`;
      }

      ctx.font = "bold 13px ui-monospace, SFMono-Regular, monospace";
      const textMetrics = ctx.measureText(label);
      const textW = textMetrics.width;
      const textH = 14;

      const badgeY = Math.max(0, y - textH - 6);

      // Label background
      ctx.fillStyle = isSelected ? "#06b6d4" : baseColor;
      ctx.fillRect(x, badgeY, textW + 8, textH + 6);

      // Label text
      ctx.fillStyle = "#ffffff";
      ctx.fillText(label, x + 4, badgeY + textH);
    }
  });
}

function drawCADCorners(context, x, y, w, h, color) {
  const len = Math.min(10, w / 4, h / 4);
  context.lineWidth = 3;
  context.strokeStyle = color;

  // Top-left
  context.beginPath();
  context.moveTo(x, y + len);
  context.lineTo(x, y);
  context.lineTo(x + len, y);
  context.stroke();

  // Top-right
  context.beginPath();
  context.moveTo(x + w - len, y);
  context.lineTo(x + w, y);
  context.lineTo(x + w, y + len);
  context.stroke();

  // Bottom-left
  context.beginPath();
  context.moveTo(x, y + h - len);
  context.lineTo(x, y + h);
  context.lineTo(x + len, y + h);
  context.stroke();

  // Bottom-right
  context.beginPath();
  context.moveTo(x + w - len, y + h);
  context.lineTo(x + w, y + h);
  context.lineTo(x + w, y + h - len);
  context.stroke();
}

// Pan & Zoom
function setupCanvasInteractions() {
  const viewport = document.getElementById("viewportArea");

  viewport.addEventListener("wheel", (e) => {
    if (!state.currentImage || state.viewMode !== "interactive") return;
    e.preventDefault();

    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    adjustZoom(zoomFactor, e.clientX, e.clientY);
  }, { passive: false });

  canvasContainer.addEventListener("mousedown", (e) => {
    if (e.button === 0) { // left click
      state.isDragging = true;
      state.dragStartX = e.clientX - state.panX;
      state.dragStartY = e.clientY - state.panY;
    }
  });

  window.addEventListener("mousemove", (e) => {
    if (state.isDragging) {
      state.panX = e.clientX - state.dragStartX;
      state.panY = e.clientY - state.dragStartY;
      applyCanvasTransform();
    } else {
      handleCanvasHover(e);
    }
  });

  window.addEventListener("mouseup", () => {
    state.isDragging = false;
  });

  canvasContainer.addEventListener("click", (e) => {
    handleCanvasClick(e);
  });
}

function handleCanvasHover(e) {
  if (!state.currentImage || !state.lastPrediction || state.isDragging) return;

  const rect = mainCanvas.getBoundingClientRect();
  const mouseX = (e.clientX - rect.left) * (mainCanvas.width / rect.width);
  const mouseY = (e.clientY - rect.top) * (mainCanvas.height / rect.height);

  let found = null;
  const detections = state.lastPrediction.detections || [];

  for (let i = detections.length - 1; i >= 0; i--) {
    const d = detections[i];
    if (
      mouseX >= d.bbox.x1 &&
      mouseX <= d.bbox.x2 &&
      mouseY >= d.bbox.y1 &&
      mouseY <= d.bbox.y2
    ) {
      found = d;
      break;
    }
  }

  if (found) {
    state.hoveredDetId = found.id;
    tooltipClass.textContent = found.class_name;
    tooltipConf.textContent = `Confidence: ${(found.confidence * 100).toFixed(1)}%`;
    tooltipBbox.textContent = `BBox: [${found.bbox.x1}, ${found.bbox.y1}, ${found.bbox.width}x${found.bbox.height}]`;

    detectionTooltip.style.left = `${e.clientX + 15}px`;
    detectionTooltip.style.top = `${e.clientY + 15}px`;
    detectionTooltip.classList.remove("hidden");
  } else {
    state.hoveredDetId = null;
    detectionTooltip.classList.add("hidden");
  }
  drawCanvas();
}

function handleCanvasClick(e) {
  if (state.hoveredDetId) {
    const det = state.lastPrediction.detections.find((d) => d.id === state.hoveredDetId);
    if (det) spotlightDetection(det);
  }
}

function adjustZoom(factor, clientX, clientY) {
  const newScale = Math.min(Math.max(0.15, state.scale * factor), 10.0);
  state.scale = newScale;
  zoomLevel.textContent = `${Math.round(state.scale * 100)}%`;
  applyCanvasTransform();
}

function resetZoom() {
  state.scale = 1.0;
  state.panX = 0;
  state.panY = 0;
  zoomLevel.textContent = "100%";
  applyCanvasTransform();
}

function applyCanvasTransform() {
  canvasContainer.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
}

// Timer and loading spinner
let timerInterval = null;
let startTime = 0;

function showLoading(show) {
  if (show) {
    loadingOverlay.classList.remove("hidden");
    detectBtn.disabled = true;
    startTime = performance.now();
    timerInterval = setInterval(() => {
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(1);
      elapsedTimer.textContent = `${elapsed}s`;
    }, 100);
  } else {
    loadingOverlay.classList.add("hidden");
    detectBtn.disabled = false;
    clearInterval(timerInterval);
  }
}

// Exports
function exportAnnotatedImage() {
  if (state.lastPrediction && state.lastPrediction.annotated_image_base64) {
    const a = document.createElement("a");
    a.href = state.lastPrediction.annotated_image_base64;
    a.download = `floorcad-annotated-${Date.now()}.png`;
    a.click();
  } else if (state.currentImage) {
    const a = document.createElement("a");
    a.href = mainCanvas.toDataURL("image/png");
    a.download = `floorcad-canvas-${Date.now()}.png`;
    a.click();
  }
}

function exportDetectionsJson() {
  if (!state.lastPrediction) return;
  const jsonStr = JSON.stringify(state.lastPrediction, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `floorcad-detections-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function exportDetectionsCsv() {
  if (!state.lastPrediction || !state.lastPrediction.detections) return;
  const headers = ["ID", "Class_ID", "Class_Name", "Confidence", "X1", "Y1", "X2", "Y2", "Width", "Height"];
  const rows = state.lastPrediction.detections.map((d) => [
    d.id,
    d.class_id,
    `"${d.class_name}"`,
    d.confidence,
    d.bbox.x1,
    d.bbox.y1,
    d.bbox.x2,
    d.bbox.y2,
    d.bbox.width,
    d.bbox.height,
  ]);

  const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `floorcad-schedule-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
