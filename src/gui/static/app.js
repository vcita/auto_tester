/**
 * vcita Test Runner GUI - Frontend Application
 */

// ==================== State ====================

const state = {
    categories: [],
    selectedCategory: null,
    selectedTest: null,
    currentTestFilter: null, // { category, testName } when filtering runs by test
    activeCenterTab: 'details', // Track which center panel tab is active (details or runs)
    isRunning: false,
    eventSource: null
};

// ==================== DOM Elements ====================

// Initialize elements - will be set when DOM is ready
let elements = {};

function initializeElements() {
    elements = {
        testTree: document.getElementById('test-tree'),
        testDetails: document.getElementById('test-details'),
        resultsLog: document.getElementById('results-log'),
        runsList: document.getElementById('runs-list'),
        runsCategoryFilter: document.getElementById('runs-category-filter'),
        runsRefresh: document.getElementById('runs-refresh'),
        btnRunSelected: document.getElementById('btn-run-selected'),
        btnRunAll: document.getElementById('btn-run-all'),
        btnRefresh: document.getElementById('btn-refresh'),
        statusIndicator: document.getElementById('status-indicator'),
        modal: document.getElementById('modal'),
        modalBody: document.getElementById('modal-body')
    };
    
    console.log('Elements initialized:', Object.keys(elements).map(k => `${k}: ${elements[k] ? 'found' : 'NOT FOUND'}`).join(', '));
}

// ==================== API Functions ====================

async function fetchCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) {
            console.error('Failed to fetch categories:', response.status, response.statusText);
            return [];
        }
        const data = await response.json();
        console.log('Categories API response:', data);
        state.categories = data.categories || [];
        return state.categories;
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

async function fetchAllRuns() {
    try {
        const response = await fetch('/api/runs');
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch all runs:', error);
        return { runs: [] };
    }
}

async function fetchCategoryRuns(category) {
    try {
        const response = await fetch(`/api/runs/${encodeURIComponent(category)}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch category runs:', error);
        return { category, runs: [] };
    }
}

async function fetchRunDetails(category, runId) {
    try {
        const response = await fetch(`/api/runs/${encodeURIComponent(category)}/${encodeURIComponent(runId)}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch run details:', error);
        return null;
    }
}

async function fetchTestRuns(category, testName) {
    try {
        const response = await fetch(`/api/runs/${encodeURIComponent(category)}/test/${testName}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch test runs:', error);
        return { category, test_name: testName, runs: [] };
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
        loadRuns(); // Refresh runs list after completion
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
    if (!elements.testTree) {
        console.error('testTree element not found in renderTestTree');
        return;
    }
    
    if (!categories || categories.length === 0) {
        elements.testTree.innerHTML = '<div class="empty-state"><span class="icon">📁</span><p>No tests found</p></div>';
        return;
    }

    console.log('Rendering test tree with categories:', categories);
    let html = '';
    
    for (const category of categories) {
        console.log(`Rendering category: ${category.name}, tests: ${category.tests?.length || 0}, subcategories: ${category.subcategories?.length || 0}`);
        
        if (!category.id || !category.name) {
            console.warn('Category missing id or name:', category);
            continue;
        }
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

function renderRuns(runs, categoryFilter = null, testFilter = null) {
    if (!runs || runs.length === 0) {
        const message = testFilter 
            ? `No runs found for test: ${testFilter.testName}`
            : 'No runs found';
        elements.runsList.innerHTML = `<div class="empty-state"><span class="icon">📊</span><p>${message}</p></div>`;
        return;
    }

    // Show/hide filters based on whether a test is selected
    const runsHeader = document.querySelector('.runs-header');
    const runsFilters = document.querySelector('.runs-filters');
    if (runsHeader && runsFilters) {
        if (testFilter) {
            // Hide category filter when a test is selected
            runsFilters.style.display = 'none';
        } else {
            // Show category filter when viewing all runs
            runsFilters.style.display = 'flex';
        }
    }

    // Show header if filtering by test
    let headerHtml = '';
    if (testFilter) {
        headerHtml = `
            <div class="runs-test-header">
                <div class="runs-test-info">
                    <span class="icon">🧪</span>
                    <span><strong>Test:</strong> ${escapeHtml(testFilter.testName)}</span>
                </div>
            </div>
        `;
    }

    let html = headerHtml;
    for (const run of runs) {
        const runId = run.run_id || 'unknown';
        
        // Handle different run data structures
        // For category-specific runs, we have categoryFilter (folder name)
        // For all runs, we need to find the category folder name from the categories array
        let categoryDisplay = categoryFilter;
        let categoryFolder = categoryFilter; // Folder name for API calls
        
        if (!categoryFilter) {
            // For all runs from index, categories array contains display names
            // We need to map them to folder names
            if (run.categories && run.categories.length > 0) {
                if (run.categories.length === 1) {
                    // Single category - try to find folder name
                    categoryDisplay = run.categories[0];
                    categoryFolder = findCategoryFolderName(run.categories[0]);
                } else {
                    // Multiple categories - try to find folder names
                    categoryDisplay = `Multiple (${run.categories.length})`;
                    // Try to use first category's folder name for navigation
                    categoryFolder = findCategoryFolderName(run.categories[0]);
                }
            } else if (run.category_name) {
                // From category run.json - this is display name, need folder name
                categoryDisplay = run.category_name;
                categoryFolder = findCategoryFolderName(run.category_name);
            } else {
                categoryDisplay = 'unknown';
                categoryFolder = null;
            }
        }
        
        const startedAt = run.started_at || run.saved_at || new Date().toISOString();
        const date = new Date(startedAt).toLocaleString();
        
        // If filtering by test, show test-specific status and info
        let status, statusClass, passed, failed, skipped, total, duration;
        if (testFilter && run.test_result) {
            // Show test-specific result
            const testResult = run.test_result;
            status = testResult.status || 'unknown';
            statusClass = status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warning';
            passed = status === 'passed' ? 1 : 0;
            failed = status === 'failed' ? 1 : 0;
            skipped = status === 'skipped' ? 1 : 0;
            total = 1;
            duration = testResult.duration_ms ? formatDuration(testResult.duration_ms) : 'N/A';
        } else {
            // Show category run summary
            status = run.status || 'unknown';
            statusClass = status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warning';
            passed = run.passed || run.summary?.passed || 0;
            failed = run.failed || run.summary?.failed || 0;
            skipped = run.skipped || run.summary?.skipped || 0;
            total = run.total || run.summary?.total || (passed + failed + skipped);
            duration = run.duration_ms ? formatDuration(run.duration_ms) : 'N/A';
        }
        
        // Determine onClick handler
        let onClick;
        if (categoryFolder) {
            onClick = `showRunDetails('${categoryFolder}', '${runId}')`;
        } else if (run.categories && run.categories.length > 1) {
            // Multiple categories - show selection - escape properly for HTML attribute
            const categoriesStr = (run.categories || []).map(c => `'${c}'`).join(',');
            onClick = `showAllRunCategories('${runId}', [${categoriesStr}])`;
        } else {
            onClick = 'void(0)'; // No action
        }
        
        html += `
            <div class="run-item" onclick="${onClick}">
                <div class="run-header">
                    <div class="run-id">${runId}</div>
                    <div class="run-status ${statusClass}">${status.toUpperCase()}</div>
                </div>
                <div class="run-info">
                    <div class="run-meta">
                        ${testFilter ? '' : `<span class="run-category">${escapeHtml(categoryDisplay)}</span>`}
                        <span class="run-date">${date}</span>
                    </div>
                    <div class="run-stats">
                        ${testFilter ? 
                            '<span class="stat ' + statusClass + '">' + status.toUpperCase() + '</span>' :
                            '<span class="stat passed">✓ ' + passed + '</span>' +
                            '<span class="stat failed">✗ ' + failed + '</span>' +
                            '<span class="stat skipped">⊘ ' + skipped + '</span>' +
                            '<span class="stat total">Total: ' + total + '</span>'
                        }
                    </div>
                    <div class="run-duration">Duration: ${duration}</div>
                    ${testFilter && run.test_result && run.test_result.error ? 
                        '<div class="run-error-preview">' + escapeHtml(run.test_result.error.substring(0, 100)) + (run.test_result.error.length > 100 ? '...' : '') + '</div>' :
                        ''
                    }
                </div>
            </div>
        `;
    }
    elements.runsList.innerHTML = html;
}

function findCategoryFolderName(displayName) {
    // Try to find category folder name from display name
    // This is a best-effort mapping - ideally we'd have a proper mapping
    if (!state.categories || state.categories.length === 0) {
        // If categories not loaded yet, try common mappings
        const lowerName = displayName.toLowerCase();
        if (lowerName === 'clients') return 'clients';
        if (lowerName === 'scheduling') return 'scheduling';
        return lowerName.replace(/\s+/g, '_');
    }
    
    for (const category of state.categories) {
        if (category.name === displayName || category.id === displayName) {
            return category.id; // Return folder name
        }
        // Also check case-insensitive
        if (category.name.toLowerCase() === displayName.toLowerCase() || 
            category.id.toLowerCase() === displayName.toLowerCase()) {
            return category.id;
        }
    }
    // Fallback: assume display name is close to folder name
    return displayName.toLowerCase().replace(/\s+/g, '_');
}

function showAllRunCategories(runId, categories) {
    if (!categories || categories.length === 0) {
        return;
    }
    
    if (categories.length === 1) {
        const folderName = findCategoryFolderName(categories[0]);
        showRunDetails(folderName, runId);
        return;
    }
    
    // Show a list of categories to choose from
    let html = `
        <div class="run-details-view">
            <div class="run-details-header">
                <button class="btn btn-secondary" onclick="loadRuns()">← Back to Runs</button>
                <div class="run-details-title">
                    <h3>Run: ${runId}</h3>
                </div>
            </div>
            <div class="run-details-info">
                <p>This run contains multiple categories. Select a category to view details:</p>
                <div class="test-results-list" style="margin-top: 12px;">
    `;
    
    for (const category of categories) {
        const folderName = findCategoryFolderName(category);
        html += `
            <div class="test-result-item" onclick="showRunDetails('${folderName}', '${runId}')" style="cursor: pointer;">
                <div class="test-result-header">
                    <span class="test-result-name">${escapeHtml(category)}</span>
                    <span>→</span>
                </div>
            </div>
        `;
    }
    
    html += '</div></div></div>';
    elements.runsList.innerHTML = html;
}

function renderRunDetails(details, category, runId) {
    if (!details) {
        elements.runsList.innerHTML = '<div class="empty-state"><span class="icon">⚠️</span><p>Run details not found</p></div>';
        return;
    }

    const startedAt = details.started_at || details.saved_at || new Date().toISOString();
    const date = new Date(startedAt).toLocaleString();
    const status = details.status || 'unknown';
    const passed = details.passed || 0;
    const failed = details.failed || 0;
    const skipped = details.skipped || 0;
    const total = details.total || (passed + failed + skipped);
    const duration = details.duration_ms ? formatDuration(details.duration_ms) : 'N/A';
    
    const statusClass = status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warning';
    
    let html = `
        <div class="run-details-view">
            <div class="run-details-header">
                <button class="btn btn-secondary" onclick="loadRuns()">← Back to Runs</button>
                <div class="run-details-title">
                    <h3>Run: ${runId}</h3>
                    <div class="run-status ${statusClass}">${status.toUpperCase()}</div>
                </div>
            </div>
            <div class="run-details-info">
                <div class="run-details-meta">
                    <div><strong>Category:</strong> ${category}</div>
                    <div><strong>Started:</strong> ${date}</div>
                    <div><strong>Duration:</strong> ${duration}</div>
                </div>
                <div class="run-details-stats">
                    <div class="stat-item passed">Passed: ${passed}</div>
                    <div class="stat-item failed">Failed: ${failed}</div>
                    <div class="stat-item skipped">Skipped: ${skipped}</div>
                    <div class="stat-item total">Total: ${total}</div>
                </div>
            </div>
    `;
    
    // Add video if available
    if (details.video_path || details.video) {
        const videoUrl = details.video_path 
            ? `/api/runs/${encodeURIComponent(category)}/${encodeURIComponent(runId)}/video`
            : details.video;
        html += `
            <div class="run-details-section">
                <h4>Video Recording</h4>
                <video src="${videoUrl}" controls style="width: 100%; max-height: 400px;"></video>
            </div>
        `;
    }
    
    // Add test results
    if (details.test_artifacts && Object.keys(details.test_artifacts).length > 0) {
        html += '<div class="run-details-section"><h4>Test Results</h4><div class="test-results-list">';
        
        for (const [testName, artifacts] of Object.entries(details.test_artifacts)) {
            const result = artifacts.result || {};
            const testStatus = result.status || 'unknown';
            const testStatusClass = testStatus === 'passed' ? 'success' : testStatus === 'failed' ? 'error' : 'warning';
            const testDuration = result.duration_ms ? formatDuration(result.duration_ms) : 'N/A';
            
            html += `
                <div class="test-result-item ${testStatusClass}">
                    <div class="test-result-header">
                        <span class="test-result-name">${testName}</span>
                        <span class="test-result-status ${testStatusClass}">${testStatus.toUpperCase()}</span>
                    </div>
                    <div class="test-result-info">
                        <span>Duration: ${testDuration}</span>
                        ${result.error ? `<div class="test-result-error">${escapeHtml(result.error)}</div>` : ''}
                    </div>
            `;
            
            // Add screenshot if available
            if (artifacts.screenshot) {
                const screenshotUrl = `/api/runs/${encodeURIComponent(category)}/${encodeURIComponent(runId)}/tests/${encodeURIComponent(testName)}/screenshot`;
                html += `
                    <div class="test-result-artifacts">
                        <img src="${screenshotUrl}" alt="Screenshot" class="test-result-screenshot" onclick="showScreenshot('${screenshotUrl}')">
                    </div>
                `;
            }
            
            // Add heal request if available
            if (artifacts.heal_request) {
                const healUrl = `/api/runs/${encodeURIComponent(category)}/${encodeURIComponent(runId)}/tests/${encodeURIComponent(testName)}/heal_request`;
                html += `
                    <div class="test-result-artifacts">
                        <button class="btn btn-secondary" onclick="showRunHealRequest('${category}', '${runId}', '${testName}')">View Heal Request</button>
                    </div>
                `;
            }
            
            html += '</div>';
        }
        
        html += '</div></div>';
    }
    
    // Add test results from test_results array if available
    if (details.test_results && Array.isArray(details.test_results) && details.test_results.length > 0) {
        html += '<div class="run-details-section"><h4>Test Results</h4><div class="test-results-list">';
        
        for (const result of details.test_results) {
            const testName = result.test_name || 'unknown';
            const testStatus = result.status || 'unknown';
            const testStatusClass = testStatus === 'passed' ? 'success' : testStatus === 'failed' ? 'error' : 'warning';
            const testDuration = result.duration_ms ? formatDuration(result.duration_ms) : 'N/A';
            
            html += `
                <div class="test-result-item ${testStatusClass}">
                    <div class="test-result-header">
                        <span class="test-result-name">${testName}</span>
                        <span class="test-result-status ${testStatusClass}">${testStatus.toUpperCase()}</span>
                    </div>
                    <div class="test-result-info">
                        <span>Duration: ${testDuration}</span>
                        ${result.error ? `<div class="test-result-error">${escapeHtml(result.error)}</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        html += '</div></div>';
    }
    
    html += '</div>';
    elements.runsList.innerHTML = html;
}

function formatDuration(ms) {
    if (ms < 1000) return `${ms}ms`;
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
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
    
    // Results are always visible in the right panel, no need to switch tabs
}

function clearResults() {
    elements.resultsLog.innerHTML = '<div class="placeholder"><p>Running tests...</p><p class="results-note">This shows real-time output from the current test run.</p></div>';
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
    
    // Load test details first - it contains the test name we need
    elements.testDetails.innerHTML = '<div class="loading">Loading...</div>';
    const details = await fetchTestDetails(category, testPath);
    renderTestDetails(details);
    
    // Get the test name from details (display name like "Create Matter")
    // This is what's used in the run directory structure
    let testNameForRuns = details?.name;
    
    // Fallback: if details doesn't have name, try to find it from categories
    if (!testNameForRuns) {
        const categoryData = state.categories.find(cat => cat.id === category);
        if (categoryData) {
            // Search in direct tests
            const test = categoryData.tests?.find(t => t.id === testPath || t.path === `${category}/${testPath}`);
            if (test) {
                testNameForRuns = test.name;
            } else {
                // Search in subcategories
                for (const subcat of categoryData.subcategories || []) {
                    const subcatTest = subcat.tests?.find(t => t.id === testPath.split("/").pop() || t.path === `${category}/${testPath}`);
                    if (subcatTest) {
                        testNameForRuns = subcatTest.name;
                        break;
                    }
                }
            }
        }
    }
    
    // Final fallback: convert test ID to display name format
    if (!testNameForRuns) {
        const simpleTestName = testPath.split("/").pop();
        testNameForRuns = simpleTestName.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');
    }
    
    console.log('Test name for runs:', testNameForRuns, 'from testPath:', testPath);
    
    // Update runs to show test-specific runs
    state.currentTestFilter = { category, testName: testNameForRuns };
    
    // Preserve the current tab selection instead of always switching to details
    const centerPanel = document.querySelector('.panel-center');
    const currentActiveTab = centerPanel?.querySelector('.tab.active');
    const activeTabId = currentActiveTab?.dataset.tab || state.activeCenterTab || 'details';
    
    // Reload runs if runs tab is active
    if (activeTabId === 'runs') {
        await loadRuns(state.currentTestFilter);
    }
    
    // Only switch to details if no tab is currently active (first time)
    if (!currentActiveTab) {
        state.activeCenterTab = 'details';
        switchTab('details', centerPanel);
    } else {
        // Keep the current tab active - don't switch
        state.activeCenterTab = activeTabId;
    }
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
    if (!elements.testTree) {
        console.error('testTree element not found in loadCategories');
        return;
    }
    
    elements.testTree.innerHTML = '<div class="loading">Loading tests...</div>';
    try {
        const categories = await fetchCategories();
        console.log('Loaded categories:', categories);
        console.log('Number of categories:', categories?.length || 0);
        
        if (!categories || categories.length === 0) {
            elements.testTree.innerHTML = '<div class="empty-state"><span class="icon">📁</span><p>No tests found. Check console for errors.</p></div>';
            return;
        }
        
        console.log('Calling renderTestTree with', categories.length, 'categories');
        renderTestTree(categories);
    } catch (error) {
        console.error('Error loading categories:', error);
        console.error('Error stack:', error.stack);
        if (elements.testTree) {
            elements.testTree.innerHTML = `<div class="empty-state"><span class="icon">⚠️</span><p>Error loading tests: ${error.message}</p></div>`;
        }
    }
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

async function loadRuns(testFilter = null) {
    console.log('loadRuns called', { testFilter, categoryFilterValue: elements.runsCategoryFilter?.value });
    
    if (!elements.runsList) {
        console.error('runsList element not found');
        return;
    }
    
    elements.runsList.innerHTML = '<div class="loading">Loading runs...</div>';
    
    let runs = [];
    let categoryFilter = elements.runsCategoryFilter?.value || '';
    
    try {
        // If a specific test is selected, show only runs for that test
        if (testFilter && testFilter.category && testFilter.testName) {
            console.log('Loading test-specific runs:', testFilter);
            const data = await fetchTestRuns(testFilter.category, testFilter.testName);
            runs = data.runs || [];
            categoryFilter = testFilter.category; // Use test's category
        } else if (categoryFilter && categoryFilter !== '' && categoryFilter !== 'All Categories') {
            // Filter by category
            console.log('Loading category runs:', categoryFilter);
            const data = await fetchCategoryRuns(categoryFilter);
            runs = data.runs || [];
        } else {
            // Show all runs
            console.log('Loading all runs');
            const data = await fetchAllRuns();
            runs = data.runs || [];
            console.log('fetchAllRuns returned:', data);
        }
        
        console.log(`Loaded ${runs.length} runs:`, runs.map(r => r.run_id || r.id));
        renderRuns(runs, categoryFilter, testFilter);
    } catch (error) {
        console.error('Error loading runs:', error);
        elements.runsList.innerHTML = '<div class="error">Failed to load runs. Please refresh.</div>';
    }
}

async function showRunDetails(category, runId) {
    elements.runsList.innerHTML = '<div class="loading">Loading run details...</div>';
    const details = await fetchRunDetails(category, runId);
    renderRunDetails(details, category, runId);
}

async function showRunHealRequest(category, runId, testName) {
    try {
        const response = await fetch(`/api/runs/${encodeURIComponent(category)}/${encodeURIComponent(runId)}/tests/${encodeURIComponent(testName)}/heal_request`);
        const data = await response.json();
        if (data && data.content) {
            showModal(`<pre>${escapeHtml(data.content)}</pre>`);
        }
    } catch (error) {
        console.error('Failed to fetch heal request:', error);
    }
}

async function refreshArtifacts() {
    await Promise.all([
        loadScreenshots(),
        loadVideos(),
        loadHealRequests()
    ]);
}

async function populateCategoryFilter() {
    if (!elements.runsCategoryFilter) {
        console.error('runsCategoryFilter element not found');
        return;
    }
    
    const categories = await fetchCategories();
    const filter = elements.runsCategoryFilter;
    
    // Clear existing options except "All Categories"
    filter.innerHTML = '<option value="">All Categories</option>';
    
    // Add category options - use folder name (id) as value, display name as text
    for (const category of categories) {
        const option = document.createElement('option');
        option.value = category.id || category.path || category.name.toLowerCase(); // This is the folder name
        option.textContent = category.name || category.path || category.id; // This is the display name
        filter.appendChild(option);
    }
}

// ==================== Event Handlers ====================

function setupEventHandlers() {
    if (!elements.btnRunSelected || !elements.btnRunAll || !elements.btnRefresh) {
        console.error('Elements not initialized, cannot setup event handlers');
        return;
    }
    
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
        await populateCategoryFilter();
    });

    if (elements.runsRefresh) {
        elements.runsRefresh.addEventListener('click', async () => {
            await loadRuns();
        });
    }

    if (elements.runsCategoryFilter) {
        elements.runsCategoryFilter.addEventListener('change', async () => {
            await loadRuns();
        });
    }

    // Tab switching
    document.querySelectorAll('.tabs .tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const panel = tab.closest('.panel');
            const tabId = tab.dataset.tab;
            
            // Only handle center panel tabs
            if (panel && panel.classList.contains('panel-center')) {
                switchTab(tabId, panel);
                state.activeCenterTab = tabId; // Remember the selected tab
                
                // If switching to runs tab and a test is selected, load test-specific runs
                if (tabId === 'runs' && state.currentTestFilter) {
                    loadRuns(state.currentTestFilter);
                } else if (tabId === 'runs' && !state.currentTestFilter) {
                    loadRuns();
                }
            } else {
                // For other panels, just switch the tab
                switchTab(tabId, panel);
            }
        });
    });

    // Modal close
    if (elements.modal) {
        const backdrop = elements.modal.querySelector('.modal-backdrop');
        const closeBtn = elements.modal.querySelector('.modal-close');
        if (backdrop) backdrop.addEventListener('click', hideModal);
        if (closeBtn) closeBtn.addEventListener('click', hideModal);
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hideModal();
    });
}

// ==================== Initialization ====================

async function checkActiveRun() {
    // Check if there's an active run and load its output
    try {
        const response = await fetch('/api/active-run');
        const data = await response.json();
        
        if (data.is_active) {
            console.log('Active run detected:', data);
            updateRunningState(true);
            
            if (data.started_via_gui) {
                // Run started via GUI - SSE will handle updates
                addLogEntry('info', 'Test run in progress (started via GUI)');
            } else {
                // Run started via CLI - try to load existing output
                addLogEntry('info', `Test run in progress (started externally, run_id: ${data.run_id})`);
                await loadActiveRunOutput(data);
            }
        }
    } catch (error) {
        console.error('Error checking for active run:', error);
    }
}

async function loadActiveRunOutput(activeRunData) {
    // Load existing output from an active run
    try {
        const runId = activeRunData.run_id;
        if (!runId) return;
        
        const categories = activeRunData.categories || [];
        
        // Load output from each category in the run
        for (const category of categories) {
            try {
                const response = await fetch(`/api/runs/${category}/${runId}`);
                if (response.ok) {
                    const runDetails = await response.json();
                    
                    // Show category info
                    addLogEntry('info', `Category: ${category}`);
                    
                    // Show test results if available
                    if (runDetails.tests) {
                        for (const [testName, testData] of Object.entries(runDetails.tests)) {
                            if (testData.result) {
                                const status = testData.result.status || 'unknown';
                                const logType = status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warning';
                                addLogEntry(logType, `  ${status.toUpperCase()}: ${testName}`);
                                
                                if (status === 'failed' && testData.result.error) {
                                    addLogEntry('error', `    Error: ${testData.result.error}`);
                                }
                            }
                        }
                    }
                }
            } catch (error) {
                console.error(`Error loading output for category ${category}:`, error);
            }
        }
        
        addLogEntry('info', '--- Live updates will continue below ---');
    } catch (error) {
        console.error('Error loading active run output:', error);
    }
}

async function init() {
    console.log('init() called');
    // Load initial data
    try {
        await loadCategories();
        await populateCategoryFilter();
        console.log('About to call loadRuns()');
        await loadRuns();
        console.log('loadRuns() completed');
    } catch (error) {
        console.error('Error in init():', error);
    }
    
    // Check for active runs before connecting to SSE
    await checkActiveRun();
    
    // Connect to SSE for real-time updates (with delay to let page stabilize)
    setTimeout(() => {
        connectSSE();
    }, 2000);
}

// Start the app when DOM is ready
function startApp() {
    console.log('Starting app...');
    console.log('DOM ready state:', document.readyState);
    
    // Initialize elements first
    initializeElements();
    
    console.log('Test tree element:', elements.testTree);
    
    if (!elements.testTree) {
        console.error('test-tree element not found!');
        return;
    }
    
    // Setup event handlers after elements are initialized
    setupEventHandlers();
    
    init();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startApp);
} else {
    // DOM is already ready
    startApp();
}
