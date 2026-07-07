// 模块：HTML 工具函数。集中处理转义、JSON 格式化和轻量语法高亮。
export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

export function formatJsonHtml(value) {
  const json = formatJson(value);
  const tokenPattern = /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g;
  let cursor = 0;
  let html = "";

  for (const match of json.matchAll(tokenPattern)) {
    html += escapeHtml(json.slice(cursor, match.index));
    const token = match[0];
    const quoted = match[1];
    const keySuffix = match[2] || "";

    if (quoted && keySuffix) {
      html += `<span class="json-key">${escapeHtml(quoted)}</span>${escapeHtml(keySuffix)}`;
    } else if (quoted) {
      html += `<span class="json-string">${escapeHtml(token)}</span>`;
    } else if (token === "true" || token === "false") {
      html += `<span class="json-bool">${token}</span>`;
    } else if (token === "null") {
      html += `<span class="json-null">${token}</span>`;
    } else {
      html += `<span class="json-number">${token}</span>`;
    }

    cursor = match.index + token.length;
  }

  html += escapeHtml(json.slice(cursor));
  return html;
}
