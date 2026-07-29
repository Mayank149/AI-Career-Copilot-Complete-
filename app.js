/**
 * AI Career Copilot - Frontend Application Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // 1. Application State & API Config
  // ==========================================
  const state = {
    apiUrl: localStorage.getItem('ai_career_api_url') || detectDefaultApiUrl(),
    activeTab: 'tab-ats',
    uploadedFile: null,
    resumeUploaded: false,
    uploadDetails: null,
    lastAnalysis: null,
    isAnalyzing: false,
    isAsking: false
  };

  function detectDefaultApiUrl() {
    if (window.location.protocol.startsWith('http')) {
      return window.location.origin;
    }
    return 'http://127.0.0.1:8000';
  }

  // Preset Job Descriptions
  const JOB_PRESETS = {
    backend: `Senior Backend Engineer (Python / AI Services)
    
Key Responsibilities:
- Design, build, and maintain high-performance RESTful APIs using Python, FastAPI, and Pydantic.
- Architect RAG (Retrieval-Augmented Generation) pipelines, vector stores (ChromaDB, Pinecone), and LLM integrations.
- Manage database schemas, query optimizations, and caching strategies using PostgreSQL, Redis, and SQLAlchemy.
- Containerize services using Docker & Kubernetes for scalable deployment on cloud infrastructure (AWS/GCP).
- Implement robust CI/CD pipelines, unit testing with PyTest, and automated monitoring.

Requirements:
- 4+ years of backend engineering experience with Python.
- Strong knowledge of FastAPI, AsyncIO, and microservices architecture.
- Hands-on experience with LangChain, LlamaIndex, or custom LLM chains.
- Solid understanding of Git, Docker, Linux administration, and system design patterns.`,

    ml: `Machine Learning & AI Engineer (LLMs & RAG)
    
Key Responsibilities:
- Build and fine-tune machine learning and deep learning models for NLP and document parsing tasks.
- Construct semantic search engines using sentence-transformers, embeddings, and vector databases.
- Develop, evaluate, and optimize custom RAG chains and prompt engineering frameworks.
- Deploy models into production environments with latency optimization and monitoring.

Requirements:
- Strong background in Python, PyTorch, Hugging Face Transformers, and OpenAI/Ollama APIs.
- Experience with vector search libraries (ChromaDB, FAISS, Qdrant).
- Understanding of embeddings model architectures (e.g., all-MiniLM-L6-v2, BGE, E5).
- M.S. or B.S. in Computer Science, AI, Machine Learning, or related quantitative field.`,

    fullstack: `Full Stack Engineer (TypeScript, React & FastAPI)
    
Key Responsibilities:
- Lead end-to-end feature development across modern Web UI and backend AI services.
- Build sleek, accessible user interfaces using React, HTML5, CSS3, TypeScript, and state management.
- Connect frontend clients to FastAPI / Node.js backend endpoints via REST and WebSockets.
- Optimize frontend performance, web vitals, dynamic animations, and user experience.

Requirements:
- 3+ years experience with React / Next.js and modern JavaScript (ES6+).
- Proficiency with Python / FastAPI or Node.js backend APIs.
- Strong CSS proficiency (Flexbox, Grid, CSS Variables, Glassmorphism, animations).
- Experience with Git version control, RESTful APIs, and cloud deployments.`
  };

  // DOM Elements
  const DOM = {
    navTabs: document.querySelectorAll('.nav-tab'),
    viewPanels: document.querySelectorAll('.view-panel'),
    statusBadge: document.getElementById('status-badge'),
    statusPing: document.getElementById('status-ping'),
    statusText: document.getElementById('status-text'),
    
    // Form Elements
    atsForm: document.getElementById('ats-form'),
    dropzone: document.getElementById('dropzone'),
    resumeInput: document.getElementById('resume-input'),
    fileBadge: document.getElementById('file-badge'),
    fileName: document.getElementById('file-name'),
    fileSize: document.getElementById('file-size'),
    removeFileBtn: document.getElementById('remove-file-btn'),
    jobDescInput: document.getElementById('job-desc'),
    presetBtns: document.querySelectorAll('.preset-btn'),
    analyzeBtn: document.getElementById('analyze-btn'),
    btnText: document.getElementById('btn-text'),
    btnIcon: document.getElementById('btn-icon'),
    btnSpinner: document.getElementById('btn-spinner'),

    // Analysis Results Elements
    resultsEmpty: document.getElementById('results-empty'),
    resultsContent: document.getElementById('results-content'),
    analysisSubtitle: document.getElementById('analysis-subtitle'),
    overallScoreVal: document.getElementById('overall-score-val'),
    overallFill: document.getElementById('overall-fill'),
    keywordScoreVal: document.getElementById('keyword-score-val'),
    keywordFill: document.getElementById('keyword-fill'),
    missingTagsContainer: document.getElementById('missing-tags-container'),
    missingCountBadge: document.getElementById('missing-count-badge'),
    strengthsContainer: document.getElementById('strengths-container'),
    weaknessesContainer: document.getElementById('weaknesses-container'),
    suggestionsContainer: document.getElementById('suggestions-container'),
    exportBtn: document.getElementById('export-btn'),

    // Copilot Chat Elements
    chatForm: document.getElementById('chat-form'),
    chatInput: document.getElementById('chat-input'),
    chatSendBtn: document.getElementById('chat-send-btn'),
    chatMessages: document.getElementById('chat-messages'),
    chatSubtitle: document.getElementById('chat-subtitle'),
    promptChips: document.querySelectorAll('.prompt-chip'),
    clearChatBtn: document.getElementById('clear-chat-btn'),

    // Settings Modal
    settingsModal: document.getElementById('settings-modal'),
    openSettingsBtn: document.getElementById('open-settings-btn'),
    closeSettingsBtn: document.getElementById('close-settings-btn'),
    apiUrlInput: document.getElementById('api-url-input'),
    testApiBtn: document.getElementById('test-api-btn'),
    saveSettingsBtn: document.getElementById('save-settings-btn'),
    toastContainer: document.getElementById('toast-container')
  };

  // ==========================================
  // 2. Initialization & Health Check
  // ==========================================
  init();

  function init() {
    setupNavigation();
    setupDropzone();
    setupPresets();
    setupFormSubmission();
    setupChat();
    setupSettingsModal();

    DOM.apiUrlInput.value = state.apiUrl;
    checkApiHealth();

    // Periodically ping health
    setInterval(checkApiHealth, 25000);
  }

  async function checkApiHealth() {
    DOM.statusPing.className = 'status-ping connecting';
    DOM.statusText.textContent = 'Checking API...';

    try {
      // Try /api/health or fallback to /
      let res = await fetch(`${state.apiUrl}/api/health`).catch(() => null);
      if (!res || !res.ok) {
        res = await fetch(`${state.apiUrl}/`).catch(() => null);
      }

      if (res && res.ok) {
        DOM.statusPing.className = 'status-ping';
        DOM.statusText.textContent = `Connected (${getCleanHost(state.apiUrl)})`;
      } else {
        // Try fallback port 8001 if 8000 failed and we are on default
        if (state.apiUrl.includes(':8000')) {
          const altUrl = state.apiUrl.replace(':8000', ':8001');
          const altRes = await fetch(`${altUrl}/api/health`).catch(() => null);
          if (altRes && altRes.ok) {
            state.apiUrl = altUrl;
            localStorage.setItem('ai_career_api_url', altUrl);
            DOM.apiUrlInput.value = altUrl;
            DOM.statusPing.className = 'status-ping';
            DOM.statusText.textContent = `Connected (${getCleanHost(altUrl)})`;
            return;
          }
        }
        DOM.statusPing.className = 'status-ping offline';
        DOM.statusText.textContent = 'API Disconnected';
      }
    } catch (err) {
      DOM.statusPing.className = 'status-ping offline';
      DOM.statusText.textContent = 'API Offline';
    }
  }

  function getCleanHost(urlStr) {
    try {
      const u = new URL(urlStr);
      return u.port ? `${u.hostname}:${u.port}` : u.hostname;
    } catch (e) {
      return urlStr;
    }
  }

  // ==========================================
  // 3. Navigation & Tabs
  // ==========================================
  function setupNavigation() {
    DOM.navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetTab = tab.getAttribute('data-tab');
        DOM.navTabs.forEach(t => t.classList.remove('active'));
        DOM.viewPanels.forEach(p => p.classList.remove('active'));

        tab.classList.add('active');
        document.getElementById(targetTab).classList.add('active');
        state.activeTab = targetTab;
      });
    });
  }

  // ==========================================
  // 4. File Drag & Drop Handlers
  // ==========================================
  function setupDropzone() {
    const dropzone = DOM.dropzone;
    const input = DOM.resumeInput;

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFileSelection(files[0]);
      }
    });

    input.addEventListener('change', (e) => {
      if (input.files && input.files.length > 0) {
        handleFileSelection(input.files[0]);
      }
    });

    DOM.removeFileBtn.addEventListener('click', () => {
      state.uploadedFile = null;
      state.resumeUploaded = false;
      DOM.resumeInput.value = '';
      DOM.fileBadge.classList.remove('active');
      DOM.dropzone.style.display = 'block';
      showToast('Resume file removed', 'info');
    });
  }

  function handleFileSelection(file) {
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Please select a valid PDF file.', 'error');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      showToast('File size exceeds 10MB limit.', 'error');
      return;
    }

    state.uploadedFile = file;
    DOM.fileName.textContent = file.name;
    DOM.fileSize.textContent = formatBytes(file.size);
    DOM.fileBadge.classList.add('active');
    DOM.dropzone.style.display = 'none';
    showToast(`Loaded ${file.name}`, 'success');
  }

  function formatBytes(bytes, decimals = 1) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  // ==========================================
  // 5. Presets & Sample Fillers
  // ==========================================
  function setupPresets() {
    DOM.presetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const presetKey = btn.getAttribute('data-preset');
        if (JOB_PRESETS[presetKey]) {
          DOM.jobDescInput.value = JOB_PRESETS[presetKey];
          showToast(`Applied ${btn.textContent} sample JD`, 'info');
        }
      });
    });
  }

  // ==========================================
  // 6. ATS Analysis Form Submission
  // ==========================================
  function setupFormSubmission() {
    DOM.atsForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const jobDescription = DOM.jobDescInput.value.trim();
      if (!jobDescription) {
        showToast('Please enter a target job description.', 'error');
        return;
      }

      if (!state.uploadedFile && !state.resumeUploaded) {
        showToast('Please upload your resume PDF first.', 'error');
        return;
      }

      setAnalyzeLoading(true);

      try {
        // Step A: Upload Resume if a new file is selected
        if (state.uploadedFile) {
          showToast('Uploading resume & building vector store...', 'info');
          const formData = new FormData();
          formData.append('file', state.uploadedFile);

          const uploadRes = await fetch(`${state.apiUrl}/upload`, {
            method: 'POST',
            body: formData
          });

          if (!uploadRes.ok) {
            const errData = await uploadRes.json().catch(() => ({}));
            throw new Error(errData.detail || `Resume upload failed (${uploadRes.status})`);
          }

          const uploadJson = await uploadRes.json();
          state.uploadDetails = uploadJson;
          state.resumeUploaded = true;
          state.uploadedFile = null; // reset raw file so we don't upload repeatedly
          showToast(`Resume uploaded! (${uploadJson.num_pages || 1} pages parsed)`, 'success');
        }

        // Step B: Send ATS Analysis Request
        showToast('Running ATS match evaluation...', 'info');
        let reviewRes = await fetch(`${state.apiUrl}/ats`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_description: jobDescription })
        }).catch(() => null);

        // Fallback endpoint test: /review
        if (!reviewRes || !reviewRes.ok) {
          reviewRes = await fetch(`${state.apiUrl}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description: jobDescription })
          });
        }

        if (!reviewRes.ok) {
          const errData = await reviewRes.json().catch(() => ({}));
          throw new Error(errData.detail || `ATS analysis failed (${reviewRes.status})`);
        }

        const analysisData = await reviewRes.json();
        state.lastAnalysis = analysisData;
        renderAnalysisResults(analysisData);
        showToast('ATS Match Analysis Completed!', 'success');

      } catch (err) {
        console.error(err);
        showToast(err.message || 'Error executing ATS analysis', 'error');
      } finally {
        setAnalyzeLoading(false);
      }
    });

    if (DOM.exportBtn) {
      DOM.exportBtn.addEventListener('click', exportReport);
    }
  }

  function setAnalyzeLoading(isLoading) {
    state.isAnalyzing = isLoading;
    DOM.analyzeBtn.disabled = isLoading;
    if (isLoading) {
      DOM.btnText.textContent = 'Analyzing Resume & JD...';
      DOM.btnIcon.style.display = 'none';
      DOM.btnSpinner.style.display = 'block';
    } else {
      DOM.btnText.textContent = 'Run ATS Match Analysis';
      DOM.btnIcon.style.display = 'block';
      DOM.btnSpinner.style.display = 'none';
    }
  }

  // ==========================================
  // 7. Render ATS Results & Gauge Animations
  // ==========================================
  function renderAnalysisResults(data) {
    DOM.resultsEmpty.style.display = 'none';
    DOM.resultsContent.style.display = 'block';
    if (DOM.exportBtn) DOM.exportBtn.style.display = 'inline-flex';

    DOM.analysisSubtitle.textContent = `Analyzed at ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    // Overall Score
    const overallScore = Math.min(100, Math.max(0, data.overall_score || 0));
    DOM.overallScoreVal.textContent = overallScore;
    updateGauge(DOM.overallFill, overallScore);

    // Keyword Match
    const keywordScore = Math.min(100, Math.max(0, data.keyword_match || 0));
    DOM.keywordScoreVal.textContent = keywordScore;
    updateGauge(DOM.keywordFill, keywordScore);

    // Missing Keywords
    const missingKeywords = data.missing_keywords || [];
    DOM.missingCountBadge.textContent = `${missingKeywords.length} Missing`;
    DOM.missingTagsContainer.innerHTML = '';

    if (missingKeywords.length === 0) {
      DOM.missingTagsContainer.innerHTML = '<span class="form-hint" style="color: var(--accent-emerald);">All major required keywords appear present!</span>';
    } else {
      missingKeywords.forEach(kw => {
        const tag = document.createElement('span');
        tag.className = 'tag-missing';
        tag.innerHTML = `
          <span>${escapeHtml(kw)}</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-left: 2px; cursor: pointer;">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
        `;
        tag.title = 'Click to copy keyword';
        tag.addEventListener('click', () => {
          navigator.clipboard.writeText(kw);
          showToast(`Copied "${kw}" to clipboard`, 'info');
        });
        DOM.missingTagsContainer.appendChild(tag);
      });
    }

    // Strengths
    renderListItems(DOM.strengthsContainer, data.strengths || [], 'strength', `
      <svg class="item-icon strength" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
    `);

    // Weaknesses
    renderListItems(DOM.weaknessesContainer, data.weaknesses || [], 'weakness', `
      <svg class="item-icon weakness" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    `);

    // Suggestions
    renderSuggestionsItems(DOM.suggestionsContainer, data.suggestions || []);
  }

  function updateGauge(circleEl, score) {
    const circumference = 314; // 2 * pi * 50
    const offset = circumference - (score / 100) * circumference;
    circleEl.style.strokeDashoffset = offset;
  }

  function renderListItems(container, items, typeClass, iconSvg) {
    container.innerHTML = '';
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="form-hint">No items reported.</div>';
      return;
    }

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'list-item-card';
      card.innerHTML = `${iconSvg}<div>${escapeHtml(item)}</div>`;
      container.appendChild(card);
    });
  }

  function renderSuggestionsItems(container, items) {
    container.innerHTML = '';
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="form-hint">No suggestions generated.</div>';
      return;
    }

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'list-item-card';
      card.innerHTML = `
        <svg class="item-icon suggestion" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <div class="suggestion-content">
          <span>${escapeHtml(item)}</span>
          <button type="button" class="copy-tip-btn" title="Copy suggestion">Copy Tip</button>
        </div>
      `;

      const copyBtn = card.querySelector('.copy-tip-btn');
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(item);
        showToast('Suggestion copied to clipboard!', 'info');
      });

      container.appendChild(card);
    });
  }

  // ==========================================
  // 8. Copilot Q&A Chat Handler
  // ==========================================
  function setupChat() {
    DOM.chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = DOM.chatInput.value.trim();
      if (!question) return;

      sendChatQuestion(question);
    });

    DOM.promptChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const promptText = chip.getAttribute('data-prompt');
        if (promptText) {
          DOM.chatInput.value = promptText;
          sendChatQuestion(promptText);
        }
      });
    });

    DOM.clearChatBtn.addEventListener('click', () => {
      DOM.chatMessages.innerHTML = `
        <div class="message-row assistant">
          <div class="message-avatar">AI</div>
          <div>
            <div class="message-bubble">
              Chat history cleared! Feel free to ask another question about your uploaded resume.
            </div>
            <span class="message-time">Just now</span>
          </div>
        </div>
      `;
      showToast('Chat history cleared', 'info');
    });
  }

  async function sendChatQuestion(question) {
    if (state.isAsking) return;

    if (!state.resumeUploaded) {
      showToast('Please upload a resume PDF in the ATS Studio tab first!', 'error');
      // Prompt user to switch tab
      return;
    }

    // Append User Question Bubble
    appendChatMessage('user', question);
    DOM.chatInput.value = '';

    // Append Assistant Loading Bubble
    const loadingId = 'loading-' + Date.now();
    appendLoadingMessage(loadingId);
    state.isAsking = true;
    DOM.chatSendBtn.disabled = true;

    try {
      const res = await fetch(`${state.apiUrl}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Chat request failed (${res.status})`);
      }

      const data = await res.json();
      removeLoadingMessage(loadingId);
      appendChatMessage('assistant', data.answer || 'No response returned.');

    } catch (err) {
      console.error(err);
      removeLoadingMessage(loadingId);
      appendChatMessage('assistant', `⚠️ Sorry, I ran into an error answering your question: ${err.message}`);
      showToast('Error getting chat answer', 'error');
    } finally {
      state.isAsking = false;
      DOM.chatSendBtn.disabled = false;
    }
  }

  function appendChatMessage(role, text) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;
    const avatarText = role === 'assistant' ? 'AI' : 'You';
    const formattedText = formatMarkdown(text);
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    row.innerHTML = `
      <div class="message-avatar">${avatarText}</div>
      <div>
        <div class="message-bubble">${formattedText}</div>
        <span class="message-time">${timeStr}</span>
      </div>
    `;

    DOM.chatMessages.appendChild(row);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
  }

  function appendLoadingMessage(id) {
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    row.id = id;
    row.innerHTML = `
      <div class="message-avatar">AI</div>
      <div>
        <div class="message-bubble" style="display: flex; align-items: center; gap: 8px;">
          <div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>
          <span>Thinking & retrieving vector context...</span>
        </div>
      </div>
    `;
    DOM.chatMessages.appendChild(row);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
  }

  function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function formatMarkdown(text) {
    let html = escapeHtml(text);
    // Convert bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Convert inline code `text`
    html = html.replace(/`(.*?)`/g, '<code style="font-family: var(--font-mono); background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">$1</code>');
    // Convert bullet line breaks
    html = html.replace(/\n- /g, '<br/>• ');
    html = html.replace(/\n\d+\.\s/g, '<br/>1. ');
    html = html.replace(/\n/g, '<br/>');
    return html;
  }

  // ==========================================
  // 9. Settings Modal & Helpers
  // ==========================================
  function setupSettingsModal() {
    DOM.openSettingsBtn.addEventListener('click', () => {
      DOM.settingsModal.classList.add('active');
    });

    DOM.statusBadge.addEventListener('click', () => {
      DOM.settingsModal.classList.add('active');
    });

    DOM.closeSettingsBtn.addEventListener('click', () => {
      DOM.settingsModal.classList.remove('active');
    });

    DOM.settingsModal.addEventListener('click', (e) => {
      if (e.target === DOM.settingsModal) {
        DOM.settingsModal.classList.remove('active');
      }
    });

    DOM.testApiBtn.addEventListener('click', async () => {
      const testUrl = DOM.apiUrlInput.value.trim() || state.apiUrl;
      showToast('Testing API connection...', 'info');
      try {
        const res = await fetch(`${testUrl}/api/health`).catch(() => null) || await fetch(`${testUrl}/`).catch(() => null);
        if (res && res.ok) {
          showToast(`Successfully connected to ${testUrl}`, 'success');
        } else {
          showToast(`Failed to connect to ${testUrl}`, 'error');
        }
      } catch (err) {
        showToast(`Connection error: ${err.message}`, 'error');
      }
    });

    DOM.saveSettingsBtn.addEventListener('click', () => {
      const newUrl = DOM.apiUrlInput.value.trim();
      if (newUrl) {
        state.apiUrl = newUrl.replace(/\/$/, ''); // strip trailing slash
        localStorage.setItem('ai_career_api_url', state.apiUrl);
        showToast('Saved API Base URL', 'success');
        checkApiHealth();
      }
      DOM.settingsModal.classList.remove('active');
    });
  }

  function exportReport() {
    if (!state.lastAnalysis) return;

    const data = state.lastAnalysis;
    const reportText = `================================================
AI CAREER COPILOT - ATS ANALYSIS REPORT
Date: ${new Date().toLocaleString()}
================================================

OVERALL ATS SCORE: ${data.overall_score}/100
KEYWORD MATCH:    ${data.keyword_match}/100

MISSING KEYWORDS:
${(data.missing_keywords || []).map(k => ' - ' + k).join('\n') || ' None'}

KEY STRENGTHS:
${(data.strengths || []).map(s => ' - ' + s).join('\n') || ' None'}

WEAKNESSES / GAPS:
${(data.weaknesses || []).map(w => ' - ' + w).join('\n') || ' None'}

ACTIONABLE ATS SUGGESTIONS:
${(data.suggestions || []).map(s => ' - ' + s).join('\n') || ' None'}
================================================`;

    navigator.clipboard.writeText(reportText);
    showToast('Full ATS Report copied to clipboard!', 'success');
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
    } else if (type === 'error') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-rose)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
    } else {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary-light)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
    }

    toast.innerHTML = `${iconSvg}<span>${escapeHtml(message)}</span>`;
    DOM.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
