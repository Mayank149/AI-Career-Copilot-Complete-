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
    resumeUploaded: false,
    resumeFilename: 'resume.pdf',
    provider: 'local',
    threadId: localStorage.getItem('ai_copilot_thread_id') || generateThreadId(),
    selectedModalFile: null,
    isAnalyzing: false,
    isAsking: false,
    isUploading: false
  };

  function detectDefaultApiUrl() {
    if (window.location.protocol.startsWith('http')) {
      return window.location.origin;
    }
    return 'http://127.0.0.1:8000';
  }

  function generateThreadId() {
    const newId = 'thread_' + Math.random().toString(36).substring(2, 11);
    localStorage.setItem('ai_copilot_thread_id', newId);
    return newId;
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
    providerToggleBtn: document.getElementById('provider-toggle-btn'),
    
    // Resume Navigation & Banner Elements
    changeResumeNavBtn: document.getElementById('change-resume-nav-btn'),
    navResumeLabel: document.getElementById('nav-resume-label'),
    changeResumeFormBtn: document.getElementById('change-resume-form-btn'),
    activeResumeBanner: document.getElementById('active-resume-banner'),
    activeResumeName: document.getElementById('active-resume-name'),
    activeResumeDesc: document.getElementById('active-resume-desc'),

    // Resume Modal Elements
    resumeModal: document.getElementById('resume-modal'),
    closeResumeModalBtn: document.getElementById('close-resume-modal-btn'),
    cancelResumeModalBtn: document.getElementById('cancel-resume-modal-btn'),
    modalResumeForm: document.getElementById('modal-resume-form'),
    modalDropzone: document.getElementById('modal-dropzone'),
    modalResumeInput: document.getElementById('modal-resume-input'),
    modalFileBadge: document.getElementById('modal-file-badge'),
    modalFileName: document.getElementById('modal-file-name'),
    modalFileSize: document.getElementById('modal-file-size'),
    modalRemoveFileBtn: document.getElementById('modal-remove-file-btn'),
    uploadResumeSubmitBtn: document.getElementById('upload-resume-submit-btn'),
    uploadBtnText: document.getElementById('upload-btn-text'),
    uploadBtnSpinner: document.getElementById('upload-btn-spinner'),
    
    // ATS Form Elements
    atsForm: document.getElementById('ats-form'),
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
    setupProviderToggle();
    setupResumeModal();
    setupPresets();
    setupFormSubmission();
    setupChat();
    setupSettingsModal();

    DOM.apiUrlInput.value = state.apiUrl;
    checkApiHealth();
    checkResumeStatus();
    checkProviderStatus();

    setInterval(checkApiHealth, 25000);
  }

  async function checkApiHealth() {
    DOM.statusPing.className = 'status-ping connecting';
    DOM.statusText.textContent = 'Checking API...';

    try {
      let res = await fetch(`${state.apiUrl}/api/health`).catch(() => null);
      if (!res || !res.ok) {
        res = await fetch(`${state.apiUrl}/`).catch(() => null);
      }

      if (res && res.ok) {
        DOM.statusPing.className = 'status-ping';
        DOM.statusText.textContent = `Connected (${getCleanHost(state.apiUrl)})`;
      } else {
        DOM.statusPing.className = 'status-ping offline';
        DOM.statusText.textContent = 'API Offline';
      }
    } catch (err) {
      DOM.statusPing.className = 'status-ping offline';
      DOM.statusText.textContent = 'API Offline';
    }
  }

  async function checkResumeStatus() {
    try {
      const res = await fetch(`${state.apiUrl}/copilot/resume-status`).catch(() => null);
      if (res && res.ok) {
        const data = await res.json();
        if (data.uploaded) {
          state.resumeUploaded = true;
          state.resumeFilename = data.filename || 'resume.pdf';
          updateResumeUI();
          return;
        }
      }
      // If no resume uploaded, prompt modal
      state.resumeUploaded = false;
      updateResumeUI();
      openResumeModal();
    } catch (e) {
      console.warn("Could not fetch resume status:", e);
    }
  }

  async function checkProviderStatus() {
    try {
      const res = await fetch(`${state.apiUrl}/copilot/provider`).catch(() => null);
      if (res && res.ok) {
        const data = await res.json();
        state.provider = data.provider || 'local';
        updateProviderPillUI();
      }
    } catch (e) {
      console.warn("Could not fetch provider status:", e);
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
  // 3. Provider Selector Pill (Local vs Cloud)
  // ==========================================
  function setupProviderToggle() {
    DOM.providerToggleBtn.addEventListener('click', async () => {
      const targetProvider = state.provider === 'local' ? 'cloud' : 'local';
      showToast(`Switching LLM Provider to ${targetProvider.toUpperCase()}...`, 'info');

      try {
        const res = await fetch(`${state.apiUrl}/copilot/provider`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider: targetProvider })
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Failed to switch LLM provider');
        }

        const data = await res.json();
        state.provider = data.provider;
        updateProviderPillUI();
        showToast(`Provider active: ${state.provider === 'cloud' ? 'Cloud (Groq API)' : 'Local (Qwen 7B)'}`, 'success');

      } catch (err) {
        console.error(err);
        showToast(err.message || 'Error switching provider', 'error');
      }
    });
  }

  function updateProviderPillUI() {
    const isCloud = state.provider === 'cloud';
    DOM.providerToggleBtn.className = `provider-pill ${isCloud ? 'cloud' : 'local'}`;
    DOM.providerToggleBtn.innerHTML = isCloud 
      ? '☁️ Cloud (Groq API)'
      : '⚡ Local (Qwen 7B)';
  }

  // ==========================================
  // 4. Resume Upload Modal & State Management
  // ==========================================
  function setupResumeModal() {
    DOM.changeResumeNavBtn.addEventListener('click', openResumeModal);
    DOM.changeResumeFormBtn.addEventListener('click', openResumeModal);
    DOM.closeResumeModalBtn.addEventListener('click', closeResumeModal);
    DOM.cancelResumeModalBtn.addEventListener('click', closeResumeModal);

    DOM.resumeModal.addEventListener('click', (e) => {
      if (e.target === DOM.resumeModal && state.resumeUploaded) {
        closeResumeModal();
      }
    });

    // Dropzone Handlers inside Modal
    const dropzone = DOM.modalDropzone;
    const input = DOM.modalResumeInput;

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
        handleModalFileSelection(files[0]);
      }
    });

    input.addEventListener('change', () => {
      if (input.files && input.files.length > 0) {
        handleModalFileSelection(input.files[0]);
      }
    });

    DOM.modalRemoveFileBtn.addEventListener('click', () => {
      state.selectedModalFile = null;
      DOM.modalResumeInput.value = '';
      DOM.modalFileBadge.classList.remove('active');
      DOM.modalDropzone.style.display = 'block';
    });

    // Modal Form Submission
    DOM.modalResumeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!state.selectedModalFile) {
        showToast('Please select a PDF resume file to upload.', 'error');
        return;
      }

      setModalUploading(true);

      try {
        const formData = new FormData();
        formData.append('file', state.selectedModalFile);

        showToast('Uploading resume & initializing vector index...', 'info');

        const uploadRes = await fetch(`${state.apiUrl}/upload`, {
          method: 'POST',
          body: formData
        });

        if (!uploadRes.ok) {
          const errData = await uploadRes.json().catch(() => ({}));
          throw new Error(errData.detail || `Upload failed (${uploadRes.status})`);
        }

        const uploadData = await uploadRes.json();
        state.resumeUploaded = true;
        state.resumeFilename = uploadData.filename || state.selectedModalFile.name;
        state.selectedModalFile = null;

        updateResumeUI();
        closeResumeModal();
        showToast('Resume uploaded and processed successfully!', 'success');

      } catch (err) {
        console.error(err);
        showToast(err.message || 'Error uploading resume PDF', 'error');
      } finally {
        setModalUploading(false);
      }
    });
  }

  function openResumeModal() {
    DOM.resumeModal.classList.add('active');
  }

  function closeResumeModal() {
    if (!state.resumeUploaded && !state.selectedModalFile) {
      showToast('Please upload a resume PDF to proceed.', 'error');
      return;
    }
    DOM.resumeModal.classList.remove('active');
  }

  function handleModalFileSelection(file) {
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Please select a valid PDF file.', 'error');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      showToast('File size exceeds 10MB limit.', 'error');
      return;
    }

    state.selectedModalFile = file;
    DOM.modalFileName.textContent = file.name;
    DOM.modalFileSize.textContent = formatBytes(file.size);
    DOM.modalFileBadge.classList.add('active');
    DOM.modalDropzone.style.display = 'none';
  }

  function updateResumeUI() {
    if (state.resumeUploaded) {
      DOM.navResumeLabel.textContent = 'Change Resume';
      DOM.activeResumeName.textContent = state.resumeFilename;
      DOM.activeResumeDesc.textContent = 'Active & indexed for ATS Studio and AI Copilot';
      DOM.activeResumeBanner.className = 'active-resume-card';
    } else {
      DOM.navResumeLabel.textContent = 'Upload Resume';
      DOM.activeResumeName.textContent = 'No resume uploaded';
      DOM.activeResumeDesc.textContent = 'Click "Upload Resume" to get started';
      DOM.activeResumeBanner.className = 'active-resume-card missing';
    }
  }

  function setModalUploading(isUploading) {
    state.isUploading = isUploading;
    DOM.uploadResumeSubmitBtn.disabled = isUploading;
    if (isUploading) {
      DOM.uploadBtnText.textContent = 'Processing PDF...';
      DOM.uploadBtnSpinner.style.display = 'block';
    } else {
      DOM.uploadBtnText.textContent = 'Upload & Save Resume';
      DOM.uploadBtnSpinner.style.display = 'none';
    }
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
  // 5. Navigation & Tabs
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
  // 6. Presets & Sample Fillers
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
  // 7. ATS Analysis Form Submission
  // ==========================================
  function setupFormSubmission() {
    DOM.atsForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!state.resumeUploaded) {
        showToast('Please upload your resume first!', 'error');
        openResumeModal();
        return;
      }

      const jobDescription = DOM.jobDescInput.value.trim();
      if (!jobDescription) {
        showToast('Please enter a target job description.', 'error');
        return;
      }

      setAnalyzeLoading(true);

      try {
        showToast('Running ATS match evaluation...', 'info');
        let reviewRes = await fetch(`${state.apiUrl}/ats`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_description: jobDescription })
        }).catch(() => null);

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

  function renderAnalysisResults(data) {
    DOM.resultsEmpty.style.display = 'none';
    DOM.resultsContent.style.display = 'block';
    if (DOM.exportBtn) DOM.exportBtn.style.display = 'inline-flex';

    DOM.analysisSubtitle.textContent = `Analyzed at ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    const overallScore = Math.min(100, Math.max(0, data.overall_score || 0));
    DOM.overallScoreVal.textContent = overallScore;
    updateGauge(DOM.overallFill, overallScore);

    const keywordScore = Math.min(100, Math.max(0, data.keyword_match || 0));
    DOM.keywordScoreVal.textContent = keywordScore;
    updateGauge(DOM.keywordFill, keywordScore);

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

    renderListItems(DOM.strengthsContainer, data.strengths || [], 'strength', `
      <svg class="item-icon strength" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
    `);

    renderListItems(DOM.weaknessesContainer, data.weaknesses || [], 'weakness', `
      <svg class="item-icon weakness" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    `);

    renderSuggestionsItems(DOM.suggestionsContainer, data.suggestions || []);
  }

  function updateGauge(circleEl, score) {
    const circumference = 314;
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
  // 8. Copilot Q&A Chat Handler (Memory Enabled)
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
      state.threadId = generateThreadId();
      DOM.chatMessages.innerHTML = `
        <div class="message-row assistant">
          <div class="message-avatar">AI</div>
          <div>
            <div class="message-bubble">
              Started a new conversation session! Feel free to ask another question about your resume.
            </div>
            <span class="message-time">Just now</span>
          </div>
        </div>
      `;
      showToast('Started new conversation thread', 'info');
    });
  }

  async function sendChatQuestion(question) {
    if (state.isAsking) return;

    if (!state.resumeUploaded) {
      showToast('Please upload a resume PDF first!', 'error');
      openResumeModal();
      return;
    }

    appendChatMessage('user', question);
    DOM.chatInput.value = '';

    const loadingId = 'loading-' + Date.now();
    appendLoadingMessage(loadingId);
    state.isAsking = true;
    DOM.chatSendBtn.disabled = true;

    try {
      const res = await fetch(`${state.apiUrl}/copilot/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: question,
          thread_id: state.threadId
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Chat request failed (${res.status})`);
      }

      const data = await res.json();
      removeLoadingMessage(loadingId);
      appendChatMessage('assistant', data.message || 'No response returned.', data);

    } catch (err) {
      console.error(err);
      removeLoadingMessage(loadingId);
      appendChatMessage('assistant', `⚠️ Error processing response: ${err.message}`);
      showToast('Error getting chat response', 'error');
    } finally {
      state.isAsking = false;
      DOM.chatSendBtn.disabled = false;
    }
  }

  function appendChatMessage(role, text, payload = null) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;
    const avatarText = role === 'assistant' ? 'AI' : 'You';
    const formattedText = formatMarkdown(text);
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let extraHtml = '';
    if (payload && payload.type === 'resume_edit_proposal') {
      const orig = escapeHtml(payload.target_original || '');
      const prop = escapeHtml(payload.proposed_diff || '');
      const expl = escapeHtml(payload.explanation || '');

      extraHtml = `
        <div class="diff-card">
          <div class="diff-card-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            <span>Proposed Resume Edit</span>
          </div>
          <div class="diff-block original">
            <div class="diff-block-label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Earlier Version
            </div>
            <div>${orig}</div>
          </div>
          <div class="diff-block proposed">
            <div class="diff-block-label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Proposed Version
            </div>
            <div>${prop}</div>
          </div>
          ${expl ? `<div class="diff-explanation">💡 ${expl}</div>` : ''}
          <div class="diff-actions">
            <button class="btn-diff-approve" onclick="window.handleResumeAction('approve')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Approve & Apply
            </button>
            <button class="btn-diff-reject" onclick="window.promptResumeAdjustment()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Request Adjustment
            </button>
            <button class="btn-diff-cancel" onclick="window.handleResumeAction('cancel')">
              Cancel
            </button>
          </div>
        </div>
      `;
    } else if (payload && (payload.download_url || payload.can_revert)) {
      extraHtml = `
        <div class="resume-action-card">
          <div class="resume-action-buttons">
            ${payload.download_url ? `
              <a href="${state.apiUrl}${payload.download_url}" class="btn-download-resume" download="AI_Career_Copilot_Resume.pdf">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                Download Updated Resume PDF
              </a>
            ` : ''}
            ${payload.can_revert ? `
              <button class="btn-revert-resume" onclick="window.handleResumeRevert()">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                Revert to Original Resume
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }

    row.innerHTML = `
      <div class="message-avatar">${avatarText}</div>
      <div>
        <div class="message-bubble">
          ${formattedText}
          ${extraHtml}
        </div>
        <span class="message-time">${timeStr}</span>
      </div>
    `;

    DOM.chatMessages.appendChild(row);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
  }

  window.handleResumeAction = async function(action, feedback = null) {
    if (state.isAsking) return;
    state.isAsking = true;
    const loadingId = 'loading-' + Date.now();
    appendLoadingMessage(loadingId);

    try {
      const res = await fetch(`${state.apiUrl}/copilot/resume/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: state.threadId,
          action: action,
          feedback: feedback
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Action failed');
      }

      const data = await res.json();
      removeLoadingMessage(loadingId);
      appendChatMessage('assistant', data.message || 'Updated.', data);

      if (data.status === 'completed') {
        showToast('Resume updated and re-indexed!', 'success');
        checkResumeStatus();
      }
    } catch (err) {
      removeLoadingMessage(loadingId);
      showToast(err.message, 'error');
      appendChatMessage('assistant', `⚠️ Error processing action: ${err.message}`);
    } finally {
      state.isAsking = false;
    }
  };

  window.promptResumeAdjustment = function() {
    const feedback = prompt("What adjustments would you like to make to the proposed text?");
    if (feedback !== null && feedback.trim()) {
      window.handleResumeAction('reject', feedback.trim());
    }
  };

  window.handleResumeRevert = async function() {
    if (!confirm("Are you sure you want to revert to your original resume? All recent changes will be undone.")) return;
    if (state.isAsking) return;
    state.isAsking = true;
    const loadingId = 'loading-' + Date.now();
    appendLoadingMessage(loadingId);

    try {
      const res = await fetch(`${state.apiUrl}/copilot/resume/revert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: state.threadId })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to revert resume');
      }

      const data = await res.json();
      removeLoadingMessage(loadingId);
      appendChatMessage('assistant', '↩️ ' + (data.message || 'Reverted to original resume.'));
      showToast('Original resume restored!', 'success');
      checkResumeStatus();
    } catch (err) {
      removeLoadingMessage(loadingId);
      showToast(err.message, 'error');
      appendChatMessage('assistant', `⚠️ Error reverting resume: ${err.message}`);
    } finally {
      state.isAsking = false;
    }
  };

  function appendLoadingMessage(id) {
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    row.id = id;
    row.innerHTML = `
      <div class="message-avatar">AI</div>
      <div>
        <div class="message-bubble" style="display: flex; align-items: center; gap: 8px;">
          <div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>
          <span>Processing with memory agent...</span>
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
    if (!text) return '';
    let html = escapeHtml(text);
    
    // Convert markdown headers (### Header, ## Header, # Header) to styled headings without hashtags
    html = html.replace(/^(?:#{1,6})\s*(.*?)$/gm, '<strong style="display:block; font-size: 1.05em; margin-top: 12px; margin-bottom: 4px; color: var(--primary-light);">$1</strong>');
    
    // Convert bold text **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert italic text *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert inline code `text`
    html = html.replace(/`(.*?)`/g, '<code style="font-family: var(--font-mono); background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">$1</code>');
    
    // Replace horizontal rules ---
    html = html.replace(/^---$/gm, '<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 12px 0;" />');

    // Convert bullet points (- item or * item)
    html = html.replace(/^[•\-\*]\s+(.*?)$/gm, '• $1');

    // Convert line breaks
    html = html.replace(/\n/g, '<br/>');
    
    // Clean up duplicate line breaks
    html = html.replace(/(<br\/>){3,}/g, '<br/><br/>');
    
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
        state.apiUrl = newUrl.replace(/\/$/, '');
        localStorage.setItem('ai_career_api_url', state.apiUrl);
        showToast('Saved API Base URL', 'success');
        checkApiHealth();
      }
      DOM.settingsModal.classList.remove('active');
    });
  }

  function exportReport() {
    const overallScore = DOM.overallScoreVal.textContent;
    const keywordScore = DOM.keywordScoreVal.textContent;
    
    const reportText = `================================================
AI CAREER COPILOT - ATS ANALYSIS REPORT
Date: ${new Date().toLocaleString()}
================================================

OVERALL ATS SCORE: ${overallScore}/100
KEYWORD MATCH:    ${keywordScore}/100

================================================`;

    navigator.clipboard.writeText(reportText);
    showToast('ATS Report summary copied to clipboard!', 'success');
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
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary-light)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="18"/></svg>';
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
