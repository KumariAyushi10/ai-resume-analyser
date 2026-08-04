const dropzone = document.getElementById("dropzone");
const dropzoneInner = document.getElementById("dropzoneInner");
const fileInput = document.getElementById("resumeFile");
const fileChip = document.getElementById("fileChip");
const fileNameEl = document.getElementById("fileName");
const removeFileBtn = document.getElementById("removeFile");
const form = document.getElementById("analyzeForm");
const errorMsg = document.getElementById("errorMsg");
const scanButton = document.getElementById("scanButton");
const uploadCard = document.getElementById("uploadCard");
const loadingPanel = document.getElementById("loadingPanel");
const results = document.getElementById("results");
const resetButton = document.getElementById("resetButton");

const LOADING_MESSAGES = [
  "Scanning document…",
  "Parsing sections…",
  "Extracting skills…",
  "Comparing keywords…",
  "Calculating score…",
];



dropzone.addEventListener("click", (e) => {
  if (e.target !== removeFileBtn) fileInput.click();
});

dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") fileInput.click();
});
dropzone.tabIndex = 0;

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) showFile(fileInput.files[0]);
});

["dragover", "dragenter"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
dropzone.addEventListener("drop", (e) => {
  const dropped = e.dataTransfer.files;
  if (dropped.length) {
    fileInput.files = dropped;
    showFile(dropped[0]);
  }
});

function showFile(file) {
  fileNameEl.textContent = file.name;
  dropzoneInner.hidden = true;
  fileChip.hidden = false;
}

removeFileBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  fileInput.value = "";
  dropzoneInner.hidden = false;
  fileChip.hidden = true;
});



form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorMsg.hidden = true;

  if (!fileInput.files.length) {
    showError("Please select a resume file first.");
    return;
  }

  const formData = new FormData();
  formData.append("resume", fileInput.files[0]);
  formData.append("job_description", document.getElementById("jobDescription").value);
  const useLlmEl = document.getElementById("useLlm");
  formData.append("use_llm", useLlmEl && useLlmEl.checked ? "true" : "false");

  scanButton.disabled = true;
  uploadCard.hidden = true;
  loadingPanel.hidden = false;
  cycleLoadingMessages();

  try {
    const response = await fetch("/analyze", { method: "POST", body: formData });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Something went wrong.");
    }

    renderResults(data);
    loadingPanel.hidden = true;
    results.hidden = false;
  } catch (err) {
    loadingPanel.hidden = true;
    uploadCard.hidden = false;
    showError(err.message);
  } finally {
    scanButton.disabled = false;
  }
});

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.hidden = false;
}

function cycleLoadingMessages() {
  const el = document.getElementById("loadingText");
  let i = 0;
  el.textContent = LOADING_MESSAGES[0];
  const interval = setInterval(() => {
    if (loadingPanel.hidden) { clearInterval(interval); return; }
    i = (i + 1) % LOADING_MESSAGES.length;
    el.textContent = LOADING_MESSAGES[i];
  }, 700);
}



function renderResults(data) {
  renderGauge(data.total_score);
  renderBreakdown(data.score_breakdown, data.has_job_description);
  renderSkills(data);
  renderSuggestions(data.suggestions, data.llm_suggestions);
}

function renderGauge(score) {
  const circumference = 2 * Math.PI * 86;
  const fill = document.getElementById("gaugeFill");
  const number = document.getElementById("gaugeNumber");
  const label = document.getElementById("gaugeLabel");

  const offset = circumference - (score / 100) * circumference;

  let color = "#F2B705"; 
  let verdict = "Room to improve";
  if (score >= 80) { color = "#4C9A6A"; verdict = "Strong ATS match"; }
  else if (score >= 60) { color = "#F2B705"; verdict = "Decent, needs polish"; }
  else { color = "#D6674F"; verdict = "Needs work"; }

  requestAnimationFrame(() => {
    fill.style.stroke = color;
    fill.style.strokeDashoffset = offset;
  });

  animateNumber(number, 0, Math.round(score), 1100);
  label.textContent = `ATS Compatibility Score — ${verdict}`;
}

function animateNumber(el, from, to, duration) {
  const start = performance.now();
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function renderBreakdown(breakdown, hasJD) {
  const container = document.getElementById("breakdownList");
  container.innerHTML = "";

  const labels = {
    keywords_and_skills: hasJD ? "Keyword & Skill Match" : "Skill Richness",
    formatting_and_structure: "Formatting & Structure",
    contact_completeness: "Contact Completeness",
    impact_and_achievements: "Impact & Achievements",
  };

  Object.entries(breakdown).forEach(([key, val]) => {
    const row = document.createElement("div");
    row.className = "breakdown-row";
    row.innerHTML = `
      <div class="breakdown-row-top">
        <span class="label">${labels[key] || key}</span>
        <span class="value">${val.score} / ${val.max}</span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:0%"></div></div>
    `;
    container.appendChild(row);
    const pct = (val.score / val.max) * 100;
    const barFill = row.querySelector(".bar-fill");
    requestAnimationFrame(() => { barFill.style.width = pct + "%"; });
  });
}

function renderSkills(data) {
  const matchedTitle = document.getElementById("matchedTitle");
  const matchedChips = document.getElementById("matchedChips");
  const missingPanel = document.getElementById("missingPanel");
  const missingChips = document.getElementById("missingChips");

  matchedChips.innerHTML = "";
  missingChips.innerHTML = "";

  const kw = data.score_breakdown.keywords_and_skills;

  if (data.has_job_description) {
    matchedTitle.textContent = "Matched Skills";
    missingPanel.hidden = false;

    const matched = kw.matched || [];
    const missing = kw.missing || [];

    if (matched.length === 0) {
      matchedChips.innerHTML = `<p class="empty-note">No overlapping skills found.</p>`;
    } else {
      matched.forEach((s) => matchedChips.appendChild(makeChip(s, "matched")));
    }

    if (missing.length === 0) {
      missingChips.innerHTML = `<p class="empty-note">No gaps found - great coverage!</p>`;
    } else {
      missing.forEach((s) => missingChips.appendChild(makeChip(s, "missing")));
    }
  } else {
    matchedTitle.textContent = "Skills Found In Your Resume";
    missingPanel.hidden = true;

    const found = data.resume_skills || [];
    if (found.length === 0) {
      matchedChips.innerHTML = `<p class="empty-note">No recognized skills found. Consider adding a Skills section.</p>`;
    } else {
      found.forEach((s) => matchedChips.appendChild(makeChip(s, "matched")));
    }
  }
}

function makeChip(text, type) {
  const chip = document.createElement("span");
  chip.className = `chip ${type}`;
  chip.textContent = text;
  return chip;
}

function renderSuggestions(suggestions, llmSuggestions) {
  const list = document.getElementById("suggestionsList");
  list.innerHTML = "";
  (suggestions || []).forEach((tip) => {
    const li = document.createElement("li");
    li.textContent = tip;
    list.appendChild(li);
  });

  const llmBlock = document.getElementById("llmBlock");
  const llmList = document.getElementById("llmSuggestionsList");
  llmList.innerHTML = "";

  if (llmSuggestions && llmSuggestions.length) {
    llmBlock.hidden = false;
    llmSuggestions.forEach((tip) => {
      const li = document.createElement("li");
      li.textContent = tip;
      llmList.appendChild(li);
    });
  } else {
    llmBlock.hidden = true;
  }
}



resetButton.addEventListener("click", () => {
  form.reset();
  fileInput.value = "";
  dropzoneInner.hidden = false;
  fileChip.hidden = true;
  results.hidden = true;
  uploadCard.hidden = false;
  errorMsg.hidden = true;
  window.scrollTo({ top: 0, behavior: "smooth" });
});
