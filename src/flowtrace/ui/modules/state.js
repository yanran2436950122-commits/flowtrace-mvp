// 模块：界面状态。把可变页面状态、布局缓存和监视项缓存隔离。
const POSITION_STORAGE_KEY = "flowtrace.nodePositions.v1";
const WATCH_STORAGE_KEY = "flowtrace.watchItems.v1";
const WATCH_OPEN_STORAGE_KEY = "flowtrace.watchOpenItems.v1";
const ONBOARDING_STATUS_STORAGE_KEY = "flowtrace.onboardingStatuses.v1";
const ONBOARDING_STATUSES = new Set(["pending", "done", "ignored"]);

export function createState() {
  return {
    activeRunId: null,
    activeView: "layers",
    latestLayerFlow: null,
    latestDataflow: null,
    nodePositions: loadNodePositions(),
    watchItems: loadWatchItems(),
    watchOpenItems: loadWatchOpenItems(),
    watchScrollItems: {},
    watchFrozenItems: {},
    watchSnapshotItems: {},
    onboardingStatuses: loadOnboardingStatuses(),
  };
}

export function persistNodePositions(state) {
  writeStorage(POSITION_STORAGE_KEY, state.nodePositions);
}

export function persistWatchItems(state) {
  writeStorage(WATCH_STORAGE_KEY, state.watchItems);
}

export function persistWatchOpenItems(state) {
  writeStorage(WATCH_OPEN_STORAGE_KEY, state.watchOpenItems);
}

export function addWatchItem(state, item) {
  if (!item?.type || !item?.id) {
    return false;
  }
  const exists = state.watchItems.some((candidate) => candidate.type === item.type && candidate.id === item.id);
  if (exists) {
    return false;
  }
  state.watchItems.push(item);
  persistWatchItems(state);
  return true;
}

export function removeWatchItem(state, item) {
  state.watchItems = state.watchItems.filter((candidate) => !(candidate.type === item.type && candidate.id === item.id));
  delete state.watchOpenItems[watchItemKey(item)];
  delete state.watchScrollItems[watchItemKey(item)];
  delete state.watchFrozenItems[watchItemKey(item)];
  delete state.watchSnapshotItems[watchItemKey(item)];
  persistWatchItems(state);
  persistWatchOpenItems(state);
}

export function isWatchItemOpen(state, item) {
  return Boolean(state.watchOpenItems[watchItemKey(item)]);
}

// 监视项的展开状态独立于监视列表，避免实时刷新重建 DOM 时丢失用户操作。
export function setWatchItemOpen(state, item, isOpen) {
  const key = watchItemKey(item);
  if (isOpen) {
    state.watchOpenItems[key] = true;
  } else {
    delete state.watchOpenItems[key];
  }
  persistWatchOpenItems(state);
}

export function getWatchItemScroll(state, item) {
  return state.watchScrollItems[watchItemKey(item)] || { left: 0, top: 0 };
}

// 快照滚动位置只保存在当前会话内，避免实时刷新重建 DOM 时把阅读位置拉回顶部。
export function setWatchItemScroll(state, item, scrollPosition) {
  state.watchScrollItems[watchItemKey(item)] = {
    left: Math.max(0, Math.round(scrollPosition?.left || 0)),
    top: Math.max(0, Math.round(scrollPosition?.top || 0)),
  };
}

export function isWatchItemFrozen(state, item) {
  return Boolean(state.watchFrozenItems[watchItemKey(item)]);
}

export function getWatchItemSnapshot(state, item) {
  return state.watchSnapshotItems[watchItemKey(item)] || null;
}

// 快照锁定只冻结当前会话中的一帧数据；取消锁定后继续跟随实时刷新。
export function setWatchItemFrozen(state, item, isFrozen, snapshot) {
  const key = watchItemKey(item);
  if (isFrozen) {
    state.watchFrozenItems[key] = true;
    state.watchSnapshotItems[key] = cloneSnapshot(snapshot);
  } else {
    delete state.watchFrozenItems[key];
    delete state.watchSnapshotItems[key];
  }
}

export function getOnboardingSuggestionStatus(state, suggestion) {
  const status = state.onboardingStatuses[onboardingSuggestionKey(suggestion)] || "pending";
  return normalizeOnboardingStatus(status);
}

export function setOnboardingSuggestionStatus(state, suggestion, status) {
  const key = onboardingSuggestionKey(suggestion);
  const normalizedStatus = normalizeOnboardingStatus(status);
  if (normalizedStatus === "pending") {
    delete state.onboardingStatuses[key];
  } else {
    state.onboardingStatuses[key] = normalizedStatus;
  }
  persistOnboardingStatuses(state);
}

export function persistOnboardingStatuses(state) {
  writeStorage(ONBOARDING_STATUS_STORAGE_KEY, state.onboardingStatuses);
}

function loadNodePositions() {
  return readStorage(POSITION_STORAGE_KEY, {
    layers: {},
    dataflow: {},
  });
}

function loadWatchItems() {
  return readStorage(WATCH_STORAGE_KEY, []);
}

function loadWatchOpenItems() {
  return readStorage(WATCH_OPEN_STORAGE_KEY, {});
}

function loadOnboardingStatuses() {
  return readStorage(ONBOARDING_STATUS_STORAGE_KEY, {});
}

function watchItemKey(item) {
  return `${item?.type || "unknown"}:${item?.id || "unknown"}`;
}

function onboardingSuggestionKey(suggestion) {
  return suggestion?.id || `${suggestion?.kind || "unknown"}:${suggestion?.target || "unknown"}`;
}

function normalizeOnboardingStatus(status) {
  return ONBOARDING_STATUSES.has(status) ? status : "pending";
}

function cloneSnapshot(snapshot) {
  if (!snapshot) {
    return null;
  }
  try {
    return JSON.parse(JSON.stringify(snapshot));
  } catch {
    return snapshot;
  }
}

function readStorage(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) {
      return fallback;
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(fallback)) {
      return Array.isArray(parsed) ? parsed : fallback;
    }
    return { ...fallback, ...parsed };
  } catch {
    return fallback;
  }
}

function writeStorage(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // localStorage 不可用时，当前内存会话仍然生效。
  }
}
