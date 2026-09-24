const form = document.querySelector("#matchingForm");
const questionInput = document.querySelector("#questionInput");
const knowledgeInput = document.querySelector("#knowledgeInput");
const thresholdInput = document.querySelector("#thresholdInput");
const thresholdValue = document.querySelector("#thresholdValue");
const questionCount = document.querySelector("#questionCount");
const matchButton = document.querySelector("#matchButton");
const errorMessage = document.querySelector("#errorMessage");
const resultsSummary = document.querySelector("#resultsSummary");
const emptyState = document.querySelector("#emptyState");
const resultsList = document.querySelector("#resultsList");
const rawJsonDetails = document.querySelector("#rawJsonDetails");
const rawJsonOutput = document.querySelector("#rawJsonOutput");

let latestResponse = null;

function readKnowledgePoints() {
  return knowledgeInput.value
    .split(/\r?\n/)
    .map((point) => point.trim())
    .filter(Boolean);
}

function setError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = !message;
}

function renderResults(response) {
  const rawResult = response?.raw_result;
  const answers = rawResult?.answers;
  const items = Array.isArray(response?.knowledge_points)
    ? response.knowledge_points
    : [];
  const threshold = Number(thresholdInput.value);
  let matchedCount = 0;
  let readableCount = 0;

  resultsList.replaceChildren();

  for (const item of items) {
    const answer = answers?.[item.key]?.noul;
    const isValidProbability =
      typeof answer === "number" &&
      Number.isFinite(answer) &&
      answer >= 0 &&
      answer <= 1;
    const probability = isValidProbability ? answer * 100 : null;
    const isMatched = isValidProbability && answer >= threshold / 100;

    if (isValidProbability) readableCount += 1;
    if (isMatched) matchedCount += 1;

    const row = document.createElement("li");
    const rowState = !isValidProbability
      ? "is-invalid"
      : isMatched
        ? "is-matched"
        : "is-unmatched";
    row.className = `result-row ${rowState}`;

    const marker = document.createElement("span");
    marker.className = "result-marker";
    marker.setAttribute("aria-hidden", "true");
    marker.textContent = isValidProbability ? (isMatched ? "✓" : "·") : "?";

    const topic = document.createElement("span");
    topic.className = "result-topic";
    topic.textContent = item.text ?? "未命名知识点";

    const status = document.createElement("span");
    status.className = "result-status";
    status.textContent = isValidProbability
      ? isMatched
        ? "匹配"
        : "不匹配"
      : "无法解析";

    const description = document.createElement("div");
    description.className = "result-description";
    description.append(topic, status);

    const percent = document.createElement("span");
    percent.className = "result-percent";
    percent.textContent = isValidProbability
      ? `${Math.round(probability)}%`
      : "—";

    const track = document.createElement("div");
    track.className = "probability-track";
    track.setAttribute("aria-hidden", "true");
    track.style.setProperty(
      "--probability",
      `${isValidProbability ? probability : 0}%`,
    );
    track.style.setProperty("--threshold", `${threshold}%`);

    const fill = document.createElement("span");
    fill.className = "probability-fill";
    track.append(fill);

    const meter = document.createElement("div");
    meter.className = "result-meter";
    meter.append(percent, track);

    row.append(marker, description, meter);
    resultsList.append(row);
  }

  emptyState.hidden = items.length > 0;
  resultsList.hidden = items.length === 0;
  rawJsonDetails.hidden = false;
  rawJsonOutput.textContent = JSON.stringify(rawResult, null, 2) ?? "null";

  if (items.length === 0) {
    resultsSummary.textContent = "没有可显示的知识点结果";
  } else if (readableCount === items.length) {
    resultsSummary.textContent = `${matchedCount} / ${readableCount} 个知识点达到阈值`;
  } else {
    resultsSummary.textContent = `${matchedCount} 个匹配 · ${items.length - readableCount} 项无法解析`;
  }
}

questionInput.addEventListener("input", () => {
  questionCount.textContent = `${questionInput.value.length} 个字符`;
});

thresholdInput.addEventListener("input", () => {
  thresholdValue.value = `${thresholdInput.value}%`;
  thresholdValue.textContent = `${thresholdInput.value}%`;
  if (latestResponse) renderResults(latestResponse);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError("");

  const question = questionInput.value.trim();
  const knowledgePoints = readKnowledgePoints();
  if (!question) {
    setError("请先输入考试题目内容。");
    questionInput.focus();
    return;
  }
  if (knowledgePoints.length === 0) {
    setError("请至少输入一个有效知识点，每行一个。");
    knowledgeInput.focus();
    return;
  }

  matchButton.disabled = true;
  matchButton.querySelector(".button-label").textContent = "正在匹配…";
  latestResponse = null;
  resultsList.replaceChildren();
  resultsList.hidden = true;
  emptyState.hidden = false;
  rawJsonDetails.hidden = true;
  rawJsonOutput.textContent = "";
  resultsSummary.textContent = "Laya 正在逐项判断";

  try {
    const response = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, knowledge_points: knowledgePoints }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "匹配失败，请检查输入后重试。");
    }

    latestResponse = payload;
    renderResults(latestResponse);
  } catch (error) {
    resultsSummary.textContent = "本次分析未完成";
    setError(error instanceof Error ? error.message : "连接失败，请稍后重试。");
  } finally {
    matchButton.disabled = false;
    matchButton.querySelector(".button-label").textContent = "开始匹配";
  }
});
