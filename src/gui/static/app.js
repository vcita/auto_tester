/**
 * vcita Test Runner GUI - Frontend Application
 */

// ==================== State ====================

const state = {
    categories: [],
    selectedCategory: null,
    selectedTest: null,
    isRunning: false,
    eventSource: null
};

// ==================== DOM Elements ====================

const elements = {
    testTree: document.getElementById('test-tree'),
    testDetails: document.getElementById('test-details'),
    resultsLog: document.getElementById('results-log'),
    screenshotsList: document.getElementById('screenshots-list'),
    videosList: document.getElementById('videos-list'),
    healList: document.getElementById('heal-list'),
    btnRunSelected: document.getElementById('btn-run-selected'),
    btnRunAll: document.getElementById('btn-run-all'),
    btnRefresh: document.getElementById('btn-refresh'),
    statusIndicator: document.getElementById('status-indicator'),
    modal: document.getElementById('modal'),
    modalBody: document.getElementById('modal-body')
};

// ==================== API Functions ====================

async function fetchCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        state.categories = data.categories;
        return data.categories;
    } catch (error) {
        console.error('Failed to fetch categories:', error);
        return [];
    }
}

async function fetchTestDetails(category, testPath) {
    try {
        // Don't encode testPath as it may contain path separators that the server expects
        const url = `/api/test/${encodeURIComponent(category)}/${testPath}`;
        const response = await fetch(url);
        if (!response.ok) {
            console.error('Failed to fetch test details:', response.status, response.statusText);
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch test details:', error);
        return null;
    }
}

async function fetchScreenshots() {
    try {
        const response = await fetch('/api/screenshots');
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch screenshots:', error);
        return { screenshots: [] };
    }
}

async function fetchVideos() {
    try {
        const response = await fetch('/api/videos');
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch videos:', error);
        return { videos: [] };
    }
}

async function fetchHealRequests() {
    try {
        const response = await fetch('/api/heal-requests');
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch heal requests:', error);
        return { heal_requests: [] };
    }
}

async function fetchHealRequestContent(id) {
    try {
        const response = await fetch(`/api/heal-request/${id}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch heal request:', error);
        return null;
    }
}

async function runCategory(category) {
    try {
        const response = await fetch(`/api/run/category/${category}`, { method: 'POST' });
        return await response.json();
    } catch (error) {
        console.error('Failed to run category:', error);
        return null;
    }
}

async function runAllTests() {
    try {
        const response = await fetch('/api/run/all', { method: 'POST' });
        return await response.json();
    } catch (error) {
        console.error('Failed to run all tests:', error);
        return null;
    }
}

// ==================== SSE Connection ====================

function connectSSE() {
    // Close existing connection if any
    if (state.eventSource) {
        try {
            state.eventSource.close();
        } catch (e) {
            // Ignore close errors
        }
        state.eventSource = null;
    }

    try {
        state.eventSource = new EventSource('/api/events');

        state.eventSource.onopen = () => {
            console.log('SSE connected');
        };

        state.eventSource.onerror = (error) => {
            // Only reconnect if connection is fully closed
            if (state.eventSource && state.eventSource.readyState === EventSource.CLOSED) {
                console.log('SSE connection closed, will reconnect in 30s...');
                try {
                    state.eventSource.close();
                } catch (e) {}
                state.eventSource = null;
                // Reconnect after 30 seconds - SSE is only needed during test runs
                setTimeout(connectSSE, 30000);
            }
        };
    } catch (e) {
        console.error('Failed to create SSE connection:', e);
        // Don't retry immediately on error
        setTimeout(connectSSE, 30000);
    }

    state.eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data);
        updateRunningState(data.is_running);
    });

    state.eventSource.addEventListener('heartbeat', (event) => {
        // Keep-alive, do nothing
    });

    state.eventSource.addEventListener('run_starting', (event) => {
        const data = JSON.parse(event.data);
        updateRunningState(true);
        addLogEntry('info', `Starting tests: ${data.category || 'all'}`);
        clearResults();
    });

    state.eventSource.addEventListener('run_complete', (event) => {
        const data = JSON.parse(event.data);
        updateRunningState(false);
        addLogEntry('success', `Tests complete: ${data.passed} passed, ${data.failed} failed, ${data.skipped} skipped`);
        refreshArtifacts();
    });

    state.eventSource.addEventListener('run_error', (event) => {
        const data = JSON.parse(event.data);
        updateRunningState(false);
        addLogEntry('error', `Run error: ${data.error}`);
    });

    state.eventSource.addEventListener('category_started', (event) => {
        const data = JSON.parse(event.data);
        addLogEntry('info', `Category: ${data.category}`);
    });

    state.eventSource.addEventListener('category_completed', (event) => {
        const data = JSON.parse(event.data);
        addLogEntry('info', `Category ${data.category} completed`);
    });

    state.eventSource.addEventListener('test_started', (event) => {
        const data = JSON.parse(event.data);
        addLogEntry('info', `[${data.index}/${data.total}] ${data.test} (${data.test_type})`);
    });

    state.eventSource.addEventListener('test_completed', (event) => {
        const data = JSON.parse(event.data);
        const status = data.result?.status || 'unknown';
        const logType = status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warning';
        addLogEntry(logType, `  ${status.toUpperCase()}: ${data.test}`);
    });

    state.eventSource.addEventListener('test_failed', (event) => {
        const data = JSON.parse(event.data);
        addLogEntry('error', `  FAILED: ${data.test} - ${data.error}`);
    });

    state.eventSource.addEventListener('heal_request_created', (event) => {
        const data = JSON.parse(event.data);
        addLogEntry('warning', `  Heal request created: ${data.path}`);
        loadHealRequests();
    });

    state.eventSource.addEventListener('browser_starting', (event) => {
        addLogEntry('info', '  Browser starting...');
    });

    state.eventSource.addEventListener('browser_started', (event) => {
        addLogEntry('info', '  Browser ready');
    });

    state.eventSource.addEventListener('browser_closing', (event) => {
        addLogEntry('info', '  Browser closing...');
    });
}

// ==================== Rendering Functions ====================

function renderTestTree(categories) {
    if (!categories || categories.length === 0) {
        elements.testTree.innerHTML = '<div class="empty-state"><span class="icon">📁</span><p>No tests found</p></div>';
        return;
    }

    let html = '';
    
    for (const category of categories) {
        html += `
            <div class="tree-category" data-category="${category.id}">
                <div class="tree-header" onclick="toggleCategory('${category.id}')">
                    <span class="tree-toggle">▼</span>
                    <span class="tree-icon">📁</span>
                    <span class="tree-name">${category.name}</span>
                </div>
                <div class="tree-children" id="cat-${category.id}">
        `;
        
        // Add setup if exists
        if (category.has_setup) {
            html += `
                <div class="tree-item">
                    <div class="tree-header" onclick="selectTest('${category.id}', '_setup')">
                        <span class="tree-toggle"></span>
                        <span class="tree-icon">⚙️</span>
                        <span class="tree-name">_setup</span>
                    </div>
                </div>
            `;
        }
        
        // Add direct tests
        for (const test of category.tests) {
            const statusClass = test.status.toLowerCase();
            html += `
                <div class="tree-item">
                    <div class="tree-header" onclick="selectTest('${category.id}', '${test.id}')" data-test="${category.id}/${test.id}">
                        <span class="tree-toggle"></span>
                        <span class="tree-icon">🧪</span>
                        <span class="tree-name">${test.name}</span>
                        <span class="tree-status ${statusClass}">${test.status}</span>
                    </div>
                </div>
            `;
        }
        
        // Add subcategories
        for (const subcat of category.subcategories) {
            html += `
                <div class="tree-category" data-subcategory="${subcat.id}">
                    <div class="tree-header" onclick="toggleSubcategory('${category.id}', '${subcat.id}')">
                        <span class="tree-toggle">▼</span>
                        <span class="tree-icon">📂</span>
                        <span class="tree-name">${subcat.name}</span>
                    </div>
                    <div class="tree-children" id="subcat-${category.id}-${subcat.id}">
            `;
            
            for (const test of subcat.tests) {
                const statusClass = test.status.toLowerCase();
                html += `
                    <div class="tree-item">
                        <div class="tree-header" onclick="selectTest('${category.id}', '${subcat.id}/${test.id}')" data-test="${category.id}/${subcat.id}/${test.id}">
                            <span class="tree-toggle"></span>
                            <span class="tree-icon">🧪</span>
                            <span class="tree-name">${test.name}</span>
                            <span class="tree-status ${statusClass}">${test.status}</span>
                        </div>
                    </div>
                `;
            }
            
            html += '</div></div>';
        }
        
        // Add teardown if exists
        if (category.has_teardown) {
            html += `
                <div class="tree-item">
                    <div class="tree-header" onclick="selectTest('${category.id}', '_teardown')">
                        <span class="tree-toggle"></span>
                        <span class="tree-icon">🧹</span>
                        <span class="tree-name">_teardown</span>
                    </div>
                </div>
            `;
        }
        
        html += '</div></div>';
    }
    
    elements.testTree.innerHTML = html;
}

function renderTestDetails(details) {
    if (!details) {
        elements.testDetails.innerHTML = '<div class="placeholder"><p>Failed to load test details</p></div>';
        return;
    }

    const tabs = [];
    if (details.steps) tabs.push({ id: 'steps', name: 'Steps', content: details.steps });
    if (details.script) tabs.push({ id: 'script', name: 'Script', content: details.script });
    if (details.code) tabs.push({ id: 'code', name: 'Code', content: details.code });

    if (tabs.length === 0) {
        elements.testDetails.innerHTML = '<div class="placeholder"><p>No files found for this test</p></div>';
        return;
    }

    let html = '<div class="detail-tabs">';
    for (let i = 0; i < tabs.length; i++) {
        const active = i === 0 ? 'active' : '';
        html += `<button class="detail-tab ${active}" onclick="switchDetailTab('${tabs[i].id}')">${tabs[i].name}</button>`;
    }
    html += '</div>';

    for (let i = 0; i < tabs.length; i++) {
        // Use inline style for first tab to ensure visibility
        const style = i === 0 ? 'style="display: block;"' : 'style="display: none;"';
        const active = i === 0 ? 'active' : '';
        html += `<div class="detail-content ${active}" ${style} id="detail-${tabs[i].id}"><pre>${escapeHtml(tabs[i].content)}</pre></div>`;
    }

    elements.testDetails.innerHTML = html;
}

function renderScreenshots(screenshots) {
    if (!screenshots || screenshots.length === 0) {
        elements.screenshotsList.innerHTML = '<div class="empty-state"><span class="icon">📷</span><p>No screenshots</p></div>';
        return;
    }

    let html = '';
    for (const screenshot of screenshots) {
        const date = new Date(screenshot.modified).toLocaleString();
        html += `
            <div class="artifact-item" onclick="showScreenshot('${screenshot.url}')">
                <div class="artifact-thumb">
                    <img src="${screenshot.url}" alt="${screenshot.filename}" loading="lazy">
                </div>
                <div class="artifact-info">
                    <div class="artifact-name">${screenshot.filename}</div>
                    <div class="artifact-meta">${date}</div>
                </div>
            </div>
        `;
    }
    elements.screenshotsList.innerHTML = html;
}

function renderVideos(videos) {
    if (!videos || videos.length === 0) {
        elements.videosList.innerHTML = '<div class="empty-state"><span class="icon">🎬</span><p>No videos</p></div>';
        return;
    }

    let html = '';
    for (const video of videos) {
        const date = new Date(video.modified).toLocaleString();
        const sizeMB = (video.size / 1024 / 1024).toFixed(1);
        html += `
            <div class="artifact-item" onclick="showVideo('${video.url}')">
                <div class="artifact-thumb">
                    <span class="icon">🎬</span>
                </div>
                <div class="artifact-info">
                    <div class="artifact-name">${video.filename}</div>
                    <div class="artifact-meta">${date} - ${sizeMB} MB</div>
                </div>
            </div>
        `;
    }
    elements.videosList.innerHTML = html;
}

function renderHealRequests(healRequests) {
    if (!healRequests || healRequests.length === 0) {
        elements.healList.innerHTML = '<div class="empty-state"><span class="icon">🩹</span><p>No heal requests</p></div>';
        return;
    }

    let html = '';
    for (const request of healRequests) {
        const date = new Date(request.modified).toLocaleString();
        html += `
            <div class="artifact-item" onclick="showHealRequest('${request.id}')">
                <div class="artifact-thumb">
                    <span class="icon">🩹</span>
                </div>
                <div class="artifact-info">
                    <div class="artifact-name">${request.filename}</div>
                    <div class="artifact-meta">${date}</div>
                </div>
            </div>
        `;
    }
    elements.healList.innerHTML = html;
}

// ==================== UI Functions ====================

function updateRunningState(isRunning) {
    state.isRunning = isRunning;
    
    elements.btnRunSelected.disabled = isRunning || !state.selectedCategory;
    elements.btnRunAll.disabled = isRunning;
    
    const indicator = elements.statusIndicator;
    indicator.className = 'status-indicator ' + (isRunning ? 'status-running' : 'status-idle');
    indicator.querySelector('.status-text').textContent = isRunning ? 'Running' : 'Idle';
}

function addLogEntry(type, message) {
    const log = elements.resultsLog;
    
    // Remove placeholder if exists
    const placeholder = log.querySelector('.placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<span class="log-time">${time}</span><span class="log-message">${escapeHtml(message)}</span>`;
    
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
    
    // Switch to results tab
    switchTab('results', document.querySelector('.panel-center'));
}

function clearResults() {
    elements.resultsLog.innerHTML = '<div class="placeholder"><p>Running tests...</p></div>';
}

function switchTab(tabId, panel) {
    const tabs = panel.querySelectorAll('.tab');
    const contents = panel.closest('.panel').querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabId);
    });
    
    contents.forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabId}`);
    });
}

function switchDetailTab(tabId) {
    const tabs = elements.testDetails.querySelectorAll('.detail-tab');
    const contents = elements.testDetails.querySelectorAll('.detail-content');
    
    tabs.forEach(tab => {
        tab.classList.toggle('active', tab.textContent.toLowerCase() === tabId);
    });
    
    contents.forEach(content => {
        const isActive = content.id === `detail-${tabId}`;
        content.classList.toggle('active', isActive);
        // Use inline style to ensure visibility
        content.style.display = isActive ? 'block' : 'none';
    });
}

function toggleCategory(categoryId) {
    const children = document.getElementById(`cat-${categoryId}`);
    const toggle = children.previousElementSibling.querySelector('.tree-toggle');
    
    children.classList.toggle('collapsed');
    toggle.textContent = children.classList.contains('collapsed') ? '▶' : '▼';
    
    // Select category for running
    state.selectedCategory = categoryId;
    state.selectedTest = null;
    elements.btnRunSelected.disabled = state.isRunning;
    elements.btnRunSelected.textContent = `Run ${categoryId}`;
}

function toggleSubcategory(categoryId, subcatId) {
    const children = document.getElementById(`subcat-${categoryId}-${subcatId}`);
    const toggle = children.previousElementSibling.querySelector('.tree-toggle');
    
    children.classList.toggle('collapsed');
    toggle.textContent = children.classList.contains('collapsed') ? '▶' : '▼';
}

async function selectTest(category, testPath) {
    // Update selection state
    state.selectedCategory = category;
    state.selectedTest = testPath;
    
    // Update UI selection
    document.querySelectorAll('.tree-header.selected').forEach(el => el.classList.remove('selected'));
    const selector = `[data-test="${category}/${testPath}"]`;
    const element = document.querySelector(selector);
    if (element) {
        element.classList.add('selected');
    }
    
    // Enable run button
    elements.btnRunSelected.disabled = state.isRunning;
    elements.btnRunSelected.innerHTML = `<span class="icon">▶</span> Run ${category}`;
    
    // Load test details
    elements.testDetails.innerHTML = '<div class="loading">Loading...</div>';
    const details = await fetchTestDetails(category, testPath);
    renderTestDetails(details);
    
    // Switch to details tab
    switchTab('details', document.querySelector('.panel-center'));
}

// ==================== Modal Functions ====================

function showModal(content) {
    elements.modalBody.innerHTML = content;
    elements.modal.classList.remove('hidden');
}

function hideModal() {
    elements.modal.classList.add('hidden');
    elements.modalBody.innerHTML = '';
}

function showScreenshot(url) {
    showModal(`<img src="${url}" alt="Screenshot">`);
}

function showVideo(url) {
    showModal(`<video src="${url}" controls autoplay></video>`);
}

async function showHealRequest(id) {
    const data = await fetchHealRequestContent(id);
    if (data) {
        showModal(`<pre>${escapeHtml(data.content)}</pre>`);
    }
}

// ==================== Helper Functions ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== Load Functions ====================

async function loadCategories() {
    elements.testTree.innerHTML = '<div class="loading">Loading tests...</div>';
    const categories = await fetchCategories();
    renderTestTree(categories);
}

async function loadScreenshots() {
    elements.screenshotsList.innerHTML = '<div class="loading">Loading...</div>';
    const data = await fetchScreenshots();
    renderScreenshots(data.screenshots);
}

async function loadVideos() {
    elements.videosList.innerHTML = '<div class="loading">Loading...</div>';
    const data = await fetchVideos();
    renderVideos(data.videos);
}

async function loadHealRequests() {
    elements.healList.innerHTML = '<div class="loading">Loading...</div>';
    const data = await fetchHealRequests();
    renderHealRequests(data.heal_requests);
}

async function refreshArtifacts() {
    await Promise.all([
        loadScreenshots(),
        loadVideos(),
        loadHealRequests()
    ]);
}

// ==================== Event Handlers ====================

elements.btnRunSelected.addEventListener('click', async () => {
    if (state.selectedCategory && !state.isRunning) {
        await runCategory(state.selectedCategory);
    }
});

elements.btnRunAll.addEventListener('click', async () => {
    if (!state.isRunning) {
        await runAllTests();
    }
});

elements.btnRefresh.addEventListener('click', async () => {
    await loadCategories();
    await refreshArtifacts();
});

// Tab switching
document.querySelectorAll('.tabs .tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const panel = tab.closest('.panel');
        switchTab(tab.dataset.tab, panel);
    });
});

// Modal close
elements.modal.querySelector('.modal-backdrop').addEventListener('click', hideModal);
elements.modal.querySelector('.modal-close').addEventListener('click', hideModal);
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') hideModal();
});

// ==================== Initialization ====================

async function init() {
    // Load initial data
    await loadCategories();
    await refreshArtifacts();
    
    // Connect to SSE for real-time updates (with delay to let page stabilize)
    setTimeout(() => {
        connectSSE();
    }, 2000);
}

// Start the app
init();
