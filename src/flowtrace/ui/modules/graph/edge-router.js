// 模块：图边路由。根据节点相对位置动态选择出入口，并生成避让式折线路径。
const DEFAULT_EXIT = 46;
const CORNER_RADIUS = 14;
const STRAIGHT_TOLERANCE = 28;

export function routeDirectedEdge(sourceRect, targetRect, laneOffset = 0) {
  if (sourceRect.id === targetRect.id) {
    return selfLoopPath(sourceRect, laneOffset);
  }

  const sourceCenter = center(sourceRect);
  const targetCenter = center(targetRect);
  const dx = targetCenter.x - sourceCenter.x;
  const dy = targetCenter.y - sourceCenter.y;
  const axis = Math.abs(dx) >= Math.abs(dy) ? "x" : "y";
  const sourceSide = axis === "x" ? (dx >= 0 ? "right" : "left") : (dy >= 0 ? "bottom" : "top");
  const targetSide = oppositeSide(sourceSide);
  const source = portPoint(sourceRect, sourceSide, laneOffset);
  const target = portPoint(targetRect, targetSide, laneOffset);
  if (shouldUseStraightLine(laneOffset, source, target)) {
    return straightPath(source, target);
  }
  const points = axis === "x"
    ? horizontalRoute(source, target, sourceSide, targetSide, laneOffset)
    : verticalRoute(source, target, sourceSide, targetSide, laneOffset);

  return roundedPath(points);
}

export function buildEdgeLanes(edges, gap = 22) {
  const groups = new Map();
  for (const edge of edges) {
    const key = [edge.from, edge.to].sort().join("<->");
    groups.set(key, [...(groups.get(key) || []), edge]);
  }

  const lanes = new Map();
  for (const group of groups.values()) {
    group.forEach((edge, index) => {
      const centeredIndex = index - (group.length - 1) / 2;
      lanes.set(edge, centeredIndex * gap);
    });
  }
  return lanes;
}

function shouldUseStraightLine(_laneOffset, source, target) {
  const distance = Math.hypot(target.x - source.x, target.y - source.y);
  const alignedX = Math.abs(source.x - target.x) <= STRAIGHT_TOLERANCE;
  const alignedY = Math.abs(source.y - target.y) <= STRAIGHT_TOLERANCE;
  return distance > 4 && (alignedX || alignedY);
}

function straightPath(source, target) {
  return `M ${round(source.x)} ${round(source.y)} L ${round(target.x)} ${round(target.y)}`;
}

function horizontalRoute(source, target, sourceSide, targetSide, laneOffset) {
  const sourceDirection = sideVector(sourceSide);
  const targetDirection = sideVector(targetSide);
  const lead = DEFAULT_EXIT + Math.abs(laneOffset);
  const sourceExit = {
    x: source.x + sourceDirection.x * lead,
    y: source.y + sourceDirection.y * lead,
  };
  const targetEntry = {
    x: target.x + targetDirection.x * lead,
    y: target.y + targetDirection.y * lead,
  };
  const midX = (sourceExit.x + targetEntry.x) / 2;
  return [
    source,
    sourceExit,
    { x: midX, y: sourceExit.y },
    { x: midX, y: targetEntry.y },
    targetEntry,
    target,
  ];
}

function verticalRoute(source, target, sourceSide, targetSide, laneOffset) {
  const sourceDirection = sideVector(sourceSide);
  const targetDirection = sideVector(targetSide);
  const lead = DEFAULT_EXIT + Math.abs(laneOffset);
  const sourceExit = {
    x: source.x + sourceDirection.x * lead,
    y: source.y + sourceDirection.y * lead,
  };
  const targetEntry = {
    x: target.x + targetDirection.x * lead,
    y: target.y + targetDirection.y * lead,
  };
  const midY = (sourceExit.y + targetEntry.y) / 2;
  return [
    source,
    sourceExit,
    { x: sourceExit.x, y: midY },
    { x: targetEntry.x, y: midY },
    targetEntry,
    target,
  ];
}

function selfLoopPath(rect, laneOffset) {
  const top = rect.y - 54 - Math.abs(laneOffset);
  const right = rect.x + rect.width + 78 + Math.abs(laneOffset);
  const start = { x: rect.x + rect.width, y: rect.y + rect.height * 0.38 + laneOffset };
  const end = { x: rect.x + rect.width * 0.56 + laneOffset, y: rect.y };
  return roundedPath([
    start,
    { x: right, y: start.y },
    { x: right, y: top },
    { x: end.x, y: top },
    end,
  ]);
}

function portPoint(rect, side, laneOffset) {
  if (side === "left") {
    return { x: rect.x, y: rect.y + rect.height / 2 + laneOffset };
  }
  if (side === "right") {
    return { x: rect.x + rect.width, y: rect.y + rect.height / 2 + laneOffset };
  }
  if (side === "top") {
    return { x: rect.x + rect.width / 2 + laneOffset, y: rect.y };
  }
  return { x: rect.x + rect.width / 2 + laneOffset, y: rect.y + rect.height };
}

function roundedPath(points) {
  const cleanPoints = removeCollinearPoints(removeDuplicatePoints(points));
  if (cleanPoints.length < 2) {
    return "";
  }

  let path = `M ${round(cleanPoints[0].x)} ${round(cleanPoints[0].y)}`;
  for (let index = 1; index < cleanPoints.length - 1; index += 1) {
    const previous = cleanPoints[index - 1];
    const current = cleanPoints[index];
    const next = cleanPoints[index + 1];
    const before = pointToward(current, previous, CORNER_RADIUS);
    const after = pointToward(current, next, CORNER_RADIUS);
    path += ` L ${round(before.x)} ${round(before.y)}`;
    path += ` Q ${round(current.x)} ${round(current.y)} ${round(after.x)} ${round(after.y)}`;
  }

  const last = cleanPoints[cleanPoints.length - 1];
  return `${path} L ${round(last.x)} ${round(last.y)}`;
}

function pointToward(from, to, distance) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const length = Math.hypot(dx, dy);
  if (length <= distance || length === 0) {
    return to;
  }
  return {
    x: from.x + (dx / length) * distance,
    y: from.y + (dy / length) * distance,
  };
}

function removeCollinearPoints(points) {
  if (points.length <= 2) {
    return points;
  }
  const result = [points[0]];
  for (let index = 1; index < points.length - 1; index += 1) {
    const previous = result[result.length - 1];
    const current = points[index];
    const next = points[index + 1];
    const sameX = nearlyEqual(previous.x, current.x) && nearlyEqual(current.x, next.x);
    const sameY = nearlyEqual(previous.y, current.y) && nearlyEqual(current.y, next.y);
    if (!sameX && !sameY) {
      result.push(current);
    }
  }
  result.push(points[points.length - 1]);
  return result;
}

function removeDuplicatePoints(points) {
  return points.filter((point, index) => {
    if (index === 0) {
      return true;
    }
    const previous = points[index - 1];
    return Math.abs(point.x - previous.x) > 0.1 || Math.abs(point.y - previous.y) > 0.1;
  });
}

function nearlyEqual(left, right) {
  return Math.abs(left - right) < 0.1;
}

function center(rect) {
  return {
    x: rect.x + rect.width / 2,
    y: rect.y + rect.height / 2,
  };
}

function sideVector(side) {
  if (side === "left") {
    return { x: -1, y: 0 };
  }
  if (side === "right") {
    return { x: 1, y: 0 };
  }
  if (side === "top") {
    return { x: 0, y: -1 };
  }
  return { x: 0, y: 1 };
}

function oppositeSide(side) {
  if (side === "left") {
    return "right";
  }
  if (side === "right") {
    return "left";
  }
  if (side === "top") {
    return "bottom";
  }
  return "top";
}

function round(value) {
  return Number.parseFloat(value.toFixed(2));
}
