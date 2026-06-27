const screens = {
  launch: document.querySelector("#launchScreen"),
  region: document.querySelector("#regionScreen"),
  question: document.querySelector("#questionScreen"),
  safety: document.querySelector("#safetyScreen"),
  result: document.querySelector("#resultScreen"),
  evidence: document.querySelector("#evidenceScreen"),
  settings: document.querySelector("#settingsScreen"),
  review: document.querySelector("#reviewScreen"),
};

const els = {
  headerContext: document.querySelector("#headerContext"),
  backIconButton: document.querySelector("#backIconButton"),
  menuButton: document.querySelector("#menuButton"),
  menuPanel: document.querySelector("#menuPanel"),
  startButton: document.querySelector("#startButton"),
  launchEmergencyButton: document.querySelector("#launchEmergencyButton"),
  confirmRegionButton: document.querySelector("#confirmRegionButton"),
  regionEmergencyButton: document.querySelector("#regionEmergencyButton"),
  localeSelect: document.querySelector("#localeSelect"),
  progressText: document.querySelector("#progressText"),
  progressDots: document.querySelector("#progressDots"),
  questionCategory: document.querySelector("#questionCategory"),
  questionStatus: document.querySelector("#questionStatus"),
  questionArt: document.querySelector("#questionArt"),
  questionTitle: document.querySelector("#questionTitle"),
  questionHelp: document.querySelector("#questionHelp"),
  answerList: document.querySelector("#answerList"),
  questionBackButton: document.querySelector("#questionBackButton"),
  questionEmergencyButton: document.querySelector("#questionEmergencyButton"),
  safetyReason: document.querySelector("#safetyReason"),
  safetyAnswers: document.querySelector("#safetyAnswers"),
  safetyBackButton: document.querySelector("#safetyBackButton"),
  safetyEmergencyButton: document.querySelector("#safetyEmergencyButton"),
  priorityBanner: document.querySelector("#priorityBanner"),
  priorityBadge: document.querySelector("#priorityBadge"),
  priorityLabel: document.querySelector("#priorityLabel"),
  resultTitle: document.querySelector("#resultTitle"),
  routeBlock: document.querySelector("#routeBlock"),
  reasonList: document.querySelector("#reasonList"),
  answerMemoList: document.querySelector("#answerMemoList"),
  resultReviewButton: document.querySelector("#resultReviewButton"),
  resultEvidenceButton: document.querySelector("#resultEvidenceButton"),
  resultRestartButton: document.querySelector("#resultRestartButton"),
  sourceCards: document.querySelector("#sourceCards"),
  rawOutput: document.querySelector("#rawOutput"),
  evidenceBackButton: document.querySelector("#evidenceBackButton"),
  settingsApplyButton: document.querySelector("#settingsApplyButton"),
  settingsRestartButton: document.querySelector("#settingsRestartButton"),
  settingsBackButton: document.querySelector("#settingsBackButton"),
  reviewList: document.querySelector("#reviewList"),
  reviewResultButton: document.querySelector("#reviewResultButton"),
  reviewRestartButton: document.querySelector("#reviewRestartButton"),
  menuEmergencyButton: document.querySelector("#menuEmergencyButton"),
  menuReviewButton: document.querySelector("#menuReviewButton"),
  menuSettingsButton: document.querySelector("#menuSettingsButton"),
  menuRestartButton: document.querySelector("#menuRestartButton"),
};

const state = {
  currentScreen: "launch",
  previousScreen: null,
  locale: "JP-13",
  selected: {},
  skipped: new Set(),
  history: [],
  questionIndex: 0,
  result: null,
  emergencyMode: false,
};

const cardCopy = {
  fever: "発熱・熱っぽさ",
  cough: "咳・痰",
  dyspnea: "息苦しさ",
  chest_pain: "胸の痛み",
  blood: "血が混じる",
  duration: "続いている期間",
  worsening: "悪化している",
};

const valueCopy = {
  yes: "ある",
  no: "ない",
  unknown: "わからない",
  none: "ない",
  mild: "少しある",
  moderate: "はっきりある",
  severe: "かなり強い",
  pressure: "締めつけ・圧迫感",
  sputum: "痰に少し混じる",
  vomit: "吐いたものに混じる",
  heavy: "多い・止まらない",
  hours_0_24: "24時間以内",
  days_1_3: "1〜3日",
  days_4_plus: "4日以上",
  weeks: "数週間",
};

const ruleCopy = {
  "RF-P0-DYSPNEA-SEVERE": "強い息苦しさが選ばれています。",
  "RF-P0-CHEST-SEVERE": "胸の強い痛み、または圧迫感が選ばれています。",
  "RF-P0-BLOOD-HEAVY": "多い、または止まらない出血が選ばれています。",
  "RF-P1-DYSPNEA-MODERATE": "はっきりした息苦しさが選ばれています。",
  "RF-P1-TROUBLE-BREATHING-WITH-FEVER": "発熱と息苦しさ、悪化が重なっています。",
  "RF-P1-BLOOD-SPUTUM-VOMIT": "痰や吐いたものに血が混じる回答があります。",
  "RF-P2-MILD-DYSPNEA": "軽い息苦しさがあります。",
  "RF-P2-FEVER-COUGH-DURATION": "発熱または咳が4日以上続いています。",
  "RF-P2-FEVER-UNKNOWN-DURATION": "発熱の期間が不明です。",
  "RF-P2-UNKNOWN-SAFETY-CARDS": "安全確認の回答に不明があります。",
  "RF-P3-MILD-FEVER-COUGH": "現在の回答では高優先度の赤旗は確認されていません。",
  "RF-P3-NO-PRIMARY-SYMPTOM": "主要症状が確認されていません。",
};

const priorityCopy = {
  P0: {
    label: "緊急",
    title: "119 を優先してください",
  },
  P1: {
    label: "早めの相談",
    title: "早めに医療相談をしてください",
  },
  P2: {
    label: "追加確認",
    title: "追加確認または近いうちの相談を検討してください",
  },
  P3: {
    label: "観察",
    title: "変化を観察し、悪化条件を確認してください",
  },
};

const questions = [
  {
    id: "fever",
    cardId: "fever",
    category: "症状",
    title: "熱っぽさや発熱はありますか？",
    help: "体温がわからない場合も、熱っぽさがあれば「ある」を選べます。",
    art: "thermometer",
    optional: true,
    answers: [
      { label: "ある", hint: "熱っぽい・発熱がある", value: "yes", tone: "primary" },
      { label: "ない", hint: "発熱はなさそう", value: "no" },
      { label: "わからない", hint: "測れていない・判断できない", value: "unknown", tone: "unknown" },
    ],
  },
  {
    id: "cough",
    cardId: "cough",
    category: "症状",
    title: "咳や痰はありますか？",
    help: "乾いた咳、痰がからむ咳のどちらでも、気になる場合は「ある」を選びます。",
    art: "cough",
    optional: true,
    answers: [
      { label: "ある", hint: "咳・痰がある", value: "yes", tone: "primary" },
      { label: "ない", hint: "咳はない", value: "no" },
      { label: "わからない", hint: "判断できない", value: "unknown", tone: "unknown" },
    ],
  },
  {
    id: "dyspnea",
    cardId: "dyspnea",
    category: "安全確認",
    title: "息苦しさはどの程度ですか？",
    help: "強い息苦しさは緊急確認に直結します。迷う場合は「わからない」を選んでください。",
    art: "lungs",
    requiredSafety: true,
    answers: [
      { label: "かなり強い", hint: "会話や移動がつらい", value: "severe", tone: "danger" },
      { label: "はっきりある", hint: "普通より明らかにつらい", value: "moderate", tone: "primary" },
      { label: "少しある", hint: "軽いが気になる", value: "mild" },
      { label: "ない", hint: "息苦しさはない", value: "none" },
      { label: "わからない", hint: "判断できない", value: "unknown", tone: "unknown", safetyInterrupt: true },
    ],
  },
  {
    id: "chest_pain",
    cardId: "chest_pain",
    category: "安全確認",
    title: "胸の強い痛みや圧迫感はありますか？",
    help: "強い痛み、締めつけ、圧迫感がある場合は安全側に扱います。",
    art: "chest",
    requiredSafety: true,
    answers: [
      { label: "締めつけ・圧迫感", hint: "強い違和感を含む", value: "pressure", tone: "danger" },
      { label: "強い痛み", hint: "かなりつらい", value: "severe", tone: "danger" },
      { label: "はっきり痛い", hint: "中程度の痛み", value: "moderate", tone: "primary" },
      { label: "ない", hint: "胸の痛みはない", value: "no" },
      { label: "わからない", hint: "判断できない", value: "unknown", tone: "unknown", safetyInterrupt: true },
    ],
  },
  {
    id: "blood",
    cardId: "blood",
    category: "安全確認",
    title: "咳・痰・吐いたものに血が混じりますか？",
    help: "量が多い、止まらない場合は緊急側に扱います。",
    art: "blood",
    requiredSafety: true,
    answers: [
      { label: "多い・止まらない", hint: "量が多い", value: "heavy", tone: "danger" },
      { label: "痰に少し混じる", hint: "血痰がある", value: "sputum", tone: "primary" },
      { label: "ない", hint: "血は混じらない", value: "none" },
      { label: "わからない", hint: "判断できない", value: "unknown", tone: "unknown", safetyInterrupt: true },
    ],
  },
  {
    id: "duration",
    cardId: "duration",
    category: "状況",
    title: "症状はどのくらい続いていますか？",
    help: "発熱や咳がある場合、期間は次の行動の目安になります。",
    art: "calendar",
    optional: true,
    answers: [
      { label: "24時間以内", hint: "今日から", value: "hours_0_24" },
      { label: "1〜3日", hint: "数日以内", value: "days_1_3" },
      { label: "4日以上", hint: "長く続く", value: "days_4_plus", tone: "primary" },
      { label: "わからない", hint: "期間が不明", value: "unknown", tone: "unknown" },
    ],
  },
  {
    id: "worsening",
    cardId: "worsening",
    category: "変化",
    title: "時間とともに悪化していますか？",
    help: "急な悪化や、昨日より明らかにつらい場合は「悪化している」を選びます。",
    art: "trend",
    optional: true,
    answers: [
      { label: "悪化している", hint: "明らかにつらくなった", value: "yes", tone: "primary" },
      { label: "悪化していない", hint: "大きな変化はない", value: "no" },
      { label: "わからない", hint: "判断できない", value: "unknown", tone: "unknown" },
    ],
  },
];

const icons = {
  thermometer: `<svg viewBox="0 0 220 160" role="img" aria-label="体温計"><path d="M106 30a17 17 0 0 1 34 0v62a38 38 0 1 1-34 0V30Z" fill="#e8f1ff" stroke="currentColor" stroke-width="7"/><path d="M123 49v66" stroke="#115bc8" stroke-width="9" stroke-linecap="round"/><circle cx="123" cy="122" r="18" fill="#115bc8"/><path d="M54 56c-13 16-20 34-20 55M171 58c12 14 18 31 18 52" fill="none" stroke="#9fc3ec" stroke-width="5" stroke-linecap="round"/></svg>`,
  cough: `<svg viewBox="0 0 220 160" role="img" aria-label="咳"><path d="M55 101c25-9 40-28 40-58 0-22 18-38 42-38 22 0 38 16 38 35" fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><path d="M125 82l36 12M126 103l42 2M126 62l30-23" stroke="#115bc8" stroke-width="7" stroke-linecap="round"/><path d="M47 112c22 13 54 13 78 2" fill="none" stroke="#9fc3ec" stroke-width="5" stroke-linecap="round"/></svg>`,
  lungs: `<svg viewBox="0 0 240 170" role="img" aria-label="肺"><path d="M120 20v50" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><path d="M120 62c-23-28-53-26-66 2-10 22-15 58-14 82 1 21 15 29 36 20 28-12 42-49 42-104Z" fill="#f8fbff" stroke="currentColor" stroke-width="6"/><path d="M120 62c23-28 53-26 66 2 10 22 15 58 14 82-1 21-15 29-36 20-28-12-42-49-42-104Z" fill="#f8fbff" stroke="currentColor" stroke-width="6"/><path d="M74 105c17-4 29-2 41 7M166 105c-17-4-29-2-41 7M68 133c20-9 34-9 48-3M172 133c-20-9-34-9-48-3" fill="none" stroke="#115bc8" stroke-width="4" stroke-linecap="round"/></svg>`,
  chest: `<svg viewBox="0 0 220 160" role="img" aria-label="胸"><path d="M73 35c-22 26-30 67-22 101M147 35c22 26 30 67 22 101" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><path d="M110 48v82" stroke="#9fc3ec" stroke-width="5" stroke-linecap="round"/><path d="m110 71 20 19-20 19-20-19Z" fill="#fff0ec" stroke="#c9382b" stroke-width="6"/></svg>`,
  blood: `<svg viewBox="0 0 220 160" role="img" aria-label="血"><path d="M111 16c34 42 51 70 51 94a51 51 0 1 1-102 0c0-24 18-53 51-94Z" fill="#fff0ec" stroke="currentColor" stroke-width="7"/><path d="M93 117c8 12 31 14 42-4" fill="none" stroke="#c9382b" stroke-width="7" stroke-linecap="round"/></svg>`,
  calendar: `<svg viewBox="0 0 220 160" role="img" aria-label="カレンダー"><rect x="38" y="28" width="144" height="110" rx="15" fill="#ffffff" stroke="currentColor" stroke-width="7"/><path d="M70 17v32M150 17v32M38 64h144" stroke="#115bc8" stroke-width="7" stroke-linecap="round"/><path d="M68 91h28M114 91h38M68 116h28M114 116h38" stroke="#9fc3ec" stroke-width="7" stroke-linecap="round"/></svg>`,
  trend: `<svg viewBox="0 0 220 160" role="img" aria-label="悪化"><path d="M38 132h145" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><path d="m50 112 42-43 33 25 50-62" fill="none" stroke="#115bc8" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/><path d="M151 32h24v24" fill="none" stroke="#115bc8" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  alert: `<svg viewBox="0 0 220 160" role="img" aria-label="注意"><path d="M110 16 24 145h172L110 16Z" fill="#fff0ec" stroke="currentColor" stroke-width="7" stroke-linejoin="round"/><path d="M110 58v45" stroke="#c9382b" stroke-width="11" stroke-linecap="round"/><circle cx="110" cy="124" r="8" fill="#c9382b"/></svg>`,
};

function showScreen(name, options = {}) {
  state.previousScreen = options.preservePrevious ? state.previousScreen : state.currentScreen;
  state.currentScreen = name;
  Object.entries(screens).forEach(([screenName, node]) => {
    node.hidden = screenName !== name;
  });
  els.headerContext.textContent = screenContext(name);
  els.backIconButton.disabled = name === "launch";
  closeMenu();
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
}

function screenContext(name) {
  const labels = {
    launch: "症状アクション案内",
    region: "地域確認",
    question: "質問",
    safety: "安全確認",
    result: "次の行動",
    evidence: "根拠",
    settings: "設定・ヘルプ",
    review: "回答確認",
  };
  return labels[name] || "Monshin Compass";
}

function closeMenu() {
  els.menuPanel.hidden = true;
  els.menuButton.setAttribute("aria-expanded", "false");
}

function currentQuestion() {
  return questions[state.questionIndex] || questions[0];
}

function selectedCards() {
  return Object.entries(state.selected).map(([card_id, value]) => ({ card_id, value }));
}

function goRegion() {
  showScreen("region");
}

function setLocale(locale) {
  state.locale = locale;
  document.querySelectorAll("[data-locale-choice]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.localeChoice === locale));
  });
  els.localeSelect.value = locale;
}

function startQuestions() {
  state.questionIndex = 0;
  state.history = [];
  showQuestion();
}

function showQuestion() {
  const question = currentQuestion();
  showScreen("question", { preservePrevious: true });
  els.progressDots.style.setProperty("--step-count", String(questions.length));
  els.progressText.textContent = `${state.questionIndex + 1} / ${questions.length}`;
  els.progressDots.replaceChildren(
    ...questions.map((_, index) => {
      const dot = document.createElement("span");
      if (index < state.questionIndex) dot.className = "done";
      if (index === state.questionIndex) dot.className = "active";
      return dot;
    }),
  );
  els.questionCategory.textContent = question.category;
  const currentValue = state.selected[question.cardId];
  els.questionStatus.textContent = currentValue ? valueCopy[currentValue] || currentValue : "未回答";
  els.questionArt.innerHTML = icons[question.art] || icons.alert;
  els.questionTitle.textContent = question.title;
  els.questionHelp.textContent = question.help;
  els.answerList.replaceChildren(...question.answers.map((answer) => answerButton(answer, () => chooseAnswer(question, answer))));
  els.questionBackButton.disabled = state.history.length === 0;
}

function answerButton(answer, handler) {
  const button = document.createElement("button");
  button.className = "answer-option";
  button.type = "button";
  button.dataset.tone = answer.tone || "normal";
  if (answer.value) {
    button.dataset.value = answer.value;
  }
  const label = document.createElement("strong");
  label.textContent = answer.label;
  const hint = document.createElement("span");
  hint.textContent = answer.hint || "";
  button.append(label, hint);
  button.addEventListener("click", handler);
  return button;
}

async function chooseAnswer(question, answer) {
  state.history.push({
    questionIndex: state.questionIndex,
    selected: { ...state.selected },
    skipped: [...state.skipped],
  });
  state.selected[question.cardId] = answer.value;
  state.skipped.delete(question.cardId);
  state.emergencyMode = false;

  if (answer.safetyInterrupt) {
    showSafetyConfirmation(question);
    return;
  }

  await evaluateAndMaybeStop();
}

function showSafetyConfirmation(question) {
  showScreen("safety");
  els.safetyReason.textContent = `${cardCopy[question.cardId]} が「わからない」です。低い優先度に見せる前に、緊急側の症状だけ確認します。`;
  const safetyOptions = [
    {
      label: "強い息苦しさがある",
      hint: "119 を優先する状態として扱う",
      tone: "danger",
      apply: () => {
        state.selected.dyspnea = "severe";
      },
    },
    {
      label: "胸の強い痛みや圧迫感がある",
      hint: "緊急確認として扱う",
      tone: "danger",
      apply: () => {
        state.selected.chest_pain = "pressure";
      },
    },
    {
      label: "そこまでは確認できない",
      hint: "不明のまま次へ進む",
      tone: "unknown",
      apply: () => {},
    },
  ];
  els.safetyAnswers.replaceChildren(
    ...safetyOptions.map((option) =>
      answerButton(option, async () => {
        option.apply();
        await evaluateAndMaybeStop();
      }),
    ),
  );
}

async function evaluateAndMaybeStop() {
  const result = await evaluate();
  if (result?.triage_priority === "P0" || result?.triage_priority === "P1") {
    renderResult(result);
    showScreen("result");
    return;
  }
  if (state.questionIndex < questions.length - 1) {
    state.questionIndex += 1;
    showQuestion();
    return;
  }
  renderResult(result);
  showScreen("result");
}

async function evaluate() {
  const selected = selectedCards();
  if (!selected.length) {
    state.result = null;
    return null;
  }
  const response = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ locale: state.locale, selected_cards: selected }),
  });
  const payload = await response.json();
  if (!payload.ok) {
    throw new Error(payload.error || "evaluation failed");
  }
  state.result = payload.result;
  return payload.result;
}

function renderResult(result) {
  const priority = result?.triage_priority || "P3";
  const copy = priorityCopy[priority] || priorityCopy.P3;
  els.priorityBanner.dataset.priority = priority;
  els.priorityBadge.textContent = priority;
  els.priorityLabel.textContent = copy.label;
  els.resultTitle.textContent = copy.title;
  els.routeBlock.textContent = routeText(result);
  els.reasonList.replaceChildren(...listItems(reasonTexts(result)));
  els.answerMemoList.replaceChildren(...listItems(answerMemoTexts()));
  renderEvidence(result);
}

function routeText(result) {
  if (state.emergencyMode) {
    return "強い症状がある場合は、地域の相談番号より先に 119 を優先してください。";
  }
  const route = result?.jp_emergency_route;
  if (!route) return "地域ルートはまだ確認できていません。";
  if (route.primary_action === "call_119_now") {
    return "119 を優先してください。#7119 などの相談ルートより先に、緊急対応を優先します。";
  }
  if (route.consultation_route?.show_7119_direct && route.consultation_route?.consultation_phone) {
    return `${route.jurisdiction_label_ja || "確認済み地域"}では ${route.consultation_route.consultation_phone} を相談先として表示できます。強い症状や急な悪化があれば 119 を優先してください。`;
  }
  return "地域が未確認のため、救急相談番号を直接表示しません。実施エリアを確認するか、地域の医療相談窓口を確認してください。強い症状があれば 119 を優先してください。";
}

function reasonTexts(result) {
  if (state.emergencyMode) return ["ユーザーが緊急確認を選択しました。"];
  const rules = result?.matched_rule_ids || [];
  if (!rules.length) return ["該当ルールはありません。現在の回答だけで安全とは断定しません。"];
  return rules.map((rule) => ruleCopy[rule] || rule);
}

function answerMemoTexts() {
  const selected = selectedCards().map(({ card_id, value }) => `${cardCopy[card_id] || card_id}: ${valueCopy[value] || value}`);
  const skipped = [...state.skipped].map((cardId) => `${cardCopy[cardId] || cardId}: スキップ`);
  return [...selected, ...skipped].length ? [...selected, ...skipped] : ["まだ回答はありません。"];
}

function listItems(items) {
  return items.map((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    return item;
  });
}

function renderEvidence(result) {
  const records = new Map();
  [...(result?.source_records || []), ...(result?.jp_emergency_route?.source_records || [])].forEach((record) => {
    if (record?.source_id) records.set(record.source_id, record);
  });
  els.sourceCards.replaceChildren(...[...records.values()].map(sourceCard));
  els.rawOutput.textContent = result ? JSON.stringify(result, null, 2) : "{}";
}

function sourceCard(record) {
  const article = document.createElement("article");
  article.className = "source-card";
  const title = document.createElement(record.url ? "a" : "strong");
  title.textContent = record.title || record.source_id;
  if (record.url) {
    title.href = record.url;
    title.target = "_blank";
    title.rel = "noopener noreferrer";
  }
  const publisher = document.createElement("small");
  publisher.textContent = `${record.publisher || "publisher unknown"} / retrieved=${record.retrieved_at || "unknown"} / raw_rag_ingest_allowed=${record.raw_rag_ingest_allowed}`;
  article.append(title, publisher);
  return article;
}

function showEmergencyResult() {
  state.emergencyMode = true;
  const result = {
    triage_priority: "P0",
    matched_rule_ids: [],
    selected_cards: selectedCards(),
    jp_emergency_route: {
      primary_action: "call_119_now",
      emergency_phone: "119",
      consultation_route: { show_7119_direct: false },
    },
    source_records: [],
  };
  state.result = result;
  renderResult(result);
  showScreen("result");
}

function goBack() {
  if (state.currentScreen === "question") {
    const previous = state.history.pop();
    if (!previous) return;
    state.questionIndex = previous.questionIndex;
    state.selected = { ...previous.selected };
    state.skipped = new Set(previous.skipped);
    showQuestion();
    return;
  }
  if (state.currentScreen === "region") {
    showScreen("launch");
    return;
  }
  if (state.currentScreen === "evidence" || state.currentScreen === "review") {
    showScreen("result");
    return;
  }
  if (state.currentScreen === "settings") {
    showScreen(state.previousScreen && state.previousScreen !== "settings" ? state.previousScreen : "question");
    return;
  }
  if (state.currentScreen === "safety") {
    showQuestion();
    return;
  }
}

function restart() {
  state.selected = {};
  state.skipped = new Set();
  state.history = [];
  state.questionIndex = 0;
  state.result = null;
  state.emergencyMode = false;
  showScreen("launch");
}

function renderReview() {
  const rows = questions.map((question, index) => {
    const row = document.createElement("div");
    row.className = "review-row";
    const content = document.createElement("div");
    const label = document.createElement("strong");
    label.textContent = cardCopy[question.cardId] || question.cardId;
    const value = document.createElement("p");
    value.textContent = state.selected[question.cardId]
      ? valueCopy[state.selected[question.cardId]] || state.selected[question.cardId]
      : state.skipped.has(question.cardId)
        ? "スキップ"
        : "未回答";
    value.style.margin = "4px 0 0";
    content.append(label, value);
    const edit = document.createElement("button");
    edit.type = "button";
    edit.textContent = "編集";
    edit.addEventListener("click", () => {
      state.questionIndex = index;
      showQuestion();
    });
    row.append(content, edit);
    return row;
  });
  els.reviewList.replaceChildren(...rows);
  showScreen("review");
}

function applySettings() {
  setLocale(els.localeSelect.value);
  if (state.result && selectedCards().length) {
    evaluate()
      .then((result) => {
        renderResult(result);
        showScreen("result");
      })
      .catch(showFatalError);
    return;
  }
  showScreen(state.previousScreen && state.previousScreen !== "settings" ? state.previousScreen : "region");
}

function showFatalError(error) {
  els.questionTitle.textContent = "読み込みに失敗しました";
  els.questionHelp.textContent = error.message;
  showScreen("question");
}

async function loadInitialData() {
  await fetch("/api/cards").then((response) => response.json());
  const preset = new URLSearchParams(window.location.search).get("demo");
  if (preset === "p0") {
    setLocale("JP-13");
    state.selected = { dyspnea: "severe" };
    const result = await evaluate();
    renderResult(result);
    showScreen("result");
    return;
  }
  if (preset === "p1") {
    setLocale("JP-13");
    state.selected = { fever: "yes", cough: "yes", dyspnea: "moderate" };
    const result = await evaluate();
    renderResult(result);
    showScreen("result");
    return;
  }
  if (preset === "jp-unconfirmed") {
    setLocale("JP");
    state.selected = { fever: "yes", cough: "yes", dyspnea: "moderate" };
    const result = await evaluate();
    renderResult(result);
    showScreen("result");
    return;
  }
  showScreen("launch");
}

document.querySelectorAll("[data-locale-choice]").forEach((button) => {
  button.addEventListener("click", () => setLocale(button.dataset.localeChoice));
});

els.menuButton.addEventListener("click", () => {
  const expanded = els.menuButton.getAttribute("aria-expanded") !== "true";
  els.menuButton.setAttribute("aria-expanded", String(expanded));
  els.menuPanel.hidden = !expanded;
});
els.backIconButton.addEventListener("click", goBack);
els.startButton.addEventListener("click", goRegion);
els.launchEmergencyButton.addEventListener("click", showEmergencyResult);
els.confirmRegionButton.addEventListener("click", startQuestions);
els.regionEmergencyButton.addEventListener("click", showEmergencyResult);
els.questionBackButton.addEventListener("click", goBack);
els.questionEmergencyButton.addEventListener("click", showEmergencyResult);
els.safetyBackButton.addEventListener("click", showQuestion);
els.safetyEmergencyButton.addEventListener("click", showEmergencyResult);
els.resultReviewButton.addEventListener("click", renderReview);
els.resultEvidenceButton.addEventListener("click", () => showScreen("evidence"));
els.resultRestartButton.addEventListener("click", restart);
els.evidenceBackButton.addEventListener("click", () => showScreen("result"));
els.settingsApplyButton.addEventListener("click", applySettings);
els.settingsRestartButton.addEventListener("click", restart);
els.settingsBackButton.addEventListener("click", goBack);
els.reviewResultButton.addEventListener("click", () => showScreen("result"));
els.reviewRestartButton.addEventListener("click", restart);
els.menuEmergencyButton.addEventListener("click", showEmergencyResult);
els.menuReviewButton.addEventListener("click", renderReview);
els.menuSettingsButton.addEventListener("click", () => showScreen("settings"));
els.menuRestartButton.addEventListener("click", restart);

loadInitialData().catch(showFatalError);
