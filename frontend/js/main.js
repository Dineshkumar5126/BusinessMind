/**
 * BusinessMind - Retail Sales Prediction & Analytics Dashboard
 * Dynamic API Client, Scenario Simulator, and Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // 1. Dynamic API Configuration
    // ==========================================
    function getApiBaseUrl() {
        // 1. Manual override if configured on window
        if (typeof window.API_BASE_URL === 'string' && window.API_BASE_URL.trim() !== '') {
            return window.API_BASE_URL.replace(/\/+$/, '');
        }
        // 2. Browser HTTP/HTTPS execution
        if (window.location.protocol.startsWith('http')) {
            // When served from the same Flask server
            if (window.location.port === '5000') {
                return '';
            }
            // Local development server on another port (e.g. 5500, 3000, 8080)
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                return 'http://localhost:5000';
            }
            // Production deployment on same host / reverse proxy
            return window.location.origin;
        }
        // 3. Fallback for file:// execution
        return 'http://localhost:5000';
    }

    const API_BASE = getApiBaseUrl();

    // ==========================================
    // 2. Theme Toggle Controller
    // ==========================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeIcon) themeIcon.classList.replace('fa-moon', 'fa-sun');
    }

    if (themeToggleBtn && themeIcon) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme === 'light') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'dark');
                themeIcon.classList.replace('fa-sun', 'fa-moon');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                themeIcon.classList.replace('fa-moon', 'fa-sun');
            }
        });
    }

    // ==========================================
    // 3. Real API Connection Status (GET /health)
    // ==========================================
    const statusIndicator = document.getElementById('status-indicator');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');

    async function checkApiHealth() {
        if (!statusIndicator || !statusDot || !statusText) return false;

        try {
            const response = await fetch(`${API_BASE}/health`, { method: 'GET' });
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'healthy' && data.model_loaded) {
                    statusIndicator.className = 'status-indicator connected';
                    statusText.textContent = `${data.model_algorithm || 'ML'} API Connected`;
                    return true;
                }
            }
            throw new Error('API reported unhealthy status');
        } catch (error) {
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'ML API Offline';
            return false;
        }
    }

    // Initial check
    checkApiHealth();
    // Re-verify periodically every 30 seconds
    setInterval(checkApiHealth, 30000);

    // ==========================================
    // 4. Dynamic Model Evaluation (GET /metrics)
    // ==========================================
    async function loadModelMetrics() {
        try {
            const response = await fetch(`${API_BASE}/metrics`, { method: 'GET' });
            if (!response.ok) return;

            const resData = await response.json();
            if (resData.status === 'success' && resData.metrics) {
                const m = resData.metrics;

                // KPI Header Cards
                if (m.XGBoost) {
                    const kpiR2 = document.getElementById('kpi-r2');
                    const kpiRmse = document.getElementById('kpi-rmse');
                    if (kpiR2 && typeof m.XGBoost.R2 === 'number') kpiR2.textContent = m.XGBoost.R2.toFixed(4);
                    if (kpiRmse && typeof m.XGBoost.RMSE === 'number') kpiRmse.textContent = m.XGBoost.RMSE.toFixed(2);
                }

                // Table cells
                if (m['Linear Regression']) {
                    const elMae = document.getElementById('lr-mae');
                    const elRmse = document.getElementById('lr-rmse');
                    const elR2 = document.getElementById('lr-r2');
                    if (elMae) elMae.textContent = m['Linear Regression'].MAE.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    if (elRmse) elRmse.textContent = m['Linear Regression'].RMSE.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    if (elR2) elR2.textContent = m['Linear Regression'].R2.toFixed(4);
                }
                if (m['Random Forest']) {
                    const elMae = document.getElementById('rf-mae');
                    const elRmse = document.getElementById('rf-rmse');
                    const elR2 = document.getElementById('rf-r2');
                    if (elMae) elMae.textContent = m['Random Forest'].MAE.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    if (elRmse) elRmse.textContent = m['Random Forest'].RMSE.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    if (elR2) elR2.textContent = m['Random Forest'].R2.toFixed(4);
                }
                if (m.XGBoost) {
                    const elMae = document.getElementById('xgb-mae');
                    const elRmse = document.getElementById('xgb-rmse');
                    const elR2 = document.getElementById('xgb-r2');
                    if (elMae) elMae.textContent = m.XGBoost.MAE.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    if (elRmse) elRmse.textContent = m.XGBoost.RMSE.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    if (elR2) elR2.textContent = m.XGBoost.R2.toFixed(4);
                }
            }
        } catch (err) {
            console.warn('Dynamic metrics fetch failed; retaining verified static metrics:', err);
        }
    }

    loadModelMetrics();

    // ==========================================
    // 5. Navigation & Scrollspy
    // ==========================================
    const navAnchors = document.querySelectorAll('.nav-menu .nav-item a');
    const sections = document.querySelectorAll('main section[id]');

    // Smooth click handler
    navAnchors.forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetEl = document.querySelector(targetId);
            if (targetEl) {
                targetEl.scrollIntoView({ behavior: 'smooth' });
                navAnchors.forEach(a => a.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // Scrollspy using IntersectionObserver
    if ('IntersectionObserver' in window && sections.length > 0) {
        const observerOptions = {
            root: null,
            rootMargin: '-20% 0px -70% 0px',
            threshold: 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    navAnchors.forEach(anchor => {
                        if (anchor.getAttribute('href') === `#${id}`) {
                            anchor.classList.add('active');
                        } else {
                            anchor.classList.remove('active');
                        }
                    });
                }
            });
        }, observerOptions);

        sections.forEach(section => observer.observe(section));
    }

    // ==========================================
    // 6. Prediction Engine Controller
    // ==========================================
    const predictBtn = document.getElementById('predict-btn');
    const predResult = document.getElementById('prediction-result');
    const predValue = document.getElementById('prediction-value');
    const askAiBtn = document.getElementById('ask-ai-btn');
    const aiInsightBox = document.getElementById('ai-insight-box');
    const aiInsightContent = document.getElementById('ai-insight-content');
    const aiProvenance = document.getElementById('ai-provenance');
    
    let lastPredictionData = null;

    if (predictBtn && predResult && predValue) {
        predictBtn.addEventListener('click', async () => {
            const storeId = document.getElementById('store-id').value;
            const date = document.getElementById('date').value;
            const promo = document.getElementById('promo').value;
            const holiday = document.getElementById('holiday').value;
            const schoolHoliday = document.getElementById('school-holiday').value;
            
            // Prevent multiple concurrent submissions
            predictBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Prediction...';
            predictBtn.disabled = true;
            predValue.textContent = '...';
            
            if (askAiBtn) askAiBtn.style.display = 'none';
            if (aiInsightBox) aiInsightBox.style.display = 'none';
            
            try {
                const payload = {
                    store_id: storeId,
                    date: date,
                    promo: promo,
                    state_holiday: holiday,
                    school_holiday: schoolHoliday
                };
                
                const response = await fetch(`${API_BASE}/predict`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (response.ok && data.status === 'success') {
                    predValue.textContent = `$${data.prediction.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                    
                    lastPredictionData = { ...payload, predicted_sales: data.prediction, prediction: data.prediction };
                    if (askAiBtn) {
                        askAiBtn.style.display = 'inline-flex';
                        askAiBtn.disabled = false;
                        askAiBtn.innerHTML = '<i class="fas fa-file-alt"></i> Generate Business Summary';
                    }
                } else {
                    predValue.textContent = 'Error';
                    alert('Prediction Error: ' + (data.error || 'Unknown error occurred.'));
                }
            } catch (error) {
                console.error('Error fetching prediction:', error);
                predValue.textContent = 'Error';
                alert('Failed to connect to the prediction API. Ensure the backend is running.');
            } finally {
                predictBtn.innerHTML = '<i class="fas fa-calculator"></i> Predict Sales';
                predictBtn.disabled = false;
            }
        });
    }

    // AI Advisor Insights Handler
    if (askAiBtn && aiInsightBox && aiInsightContent) {
        askAiBtn.addEventListener('click', async () => {
            if (!lastPredictionData) return;
            
            // Prevent multiple concurrent requests
            askAiBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Business Summary...';
            askAiBtn.disabled = true;
            aiInsightBox.style.display = 'block';
            if (aiProvenance) aiProvenance.innerHTML = '';
            aiInsightContent.innerHTML = '<div style="grid-column: 1 / -1; padding: 1.5rem; color: var(--text-muted);"><i class="fas fa-spinner fa-spin"></i> Synthesizing executive business insights...</div>';
            
            try {
                const response = await fetch(`${API_BASE}/insights`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(lastPredictionData)
                });
                
                const data = await response.json();
                
                if (response.ok && (data.status === 'success' || data.status === 'fallback')) {
                    const isFallback = Boolean(data.is_fallback || data.source === 'local' || data.status === 'fallback');

                    // Set clean unobtrusive provenance tag
                    if (aiProvenance) {
                        if (!isFallback && data.source === 'gemini') {
                            aiProvenance.className = 'ai-provenance live';
                            aiProvenance.innerHTML = '<span class="dot"></span><span>AI-generated · Gemini</span>';
                        } else {
                            aiProvenance.className = 'ai-provenance fallback';
                            aiProvenance.innerHTML = '<span class="dot"></span><span>Model-based fallback · AI service unavailable</span>';
                        }
                    }

                    aiInsightContent.innerHTML = data.insights;
                    
                    // Assign layout classes dynamically:
                    // 1. Sales Forecast Summary: Full width
                    // 2. Key Factors & 3. Business Interpretation: Two equal columns (half width each)
                    // 4. Recommended Actions: Full width
                    // 5. Risk and Limitations & 6. Final Business Insight: Two equal columns (half width each)
                    const reportSections = aiInsightContent.querySelectorAll('.ai-report-section');
                    reportSections.forEach(section => {
                        const headingEl = section.querySelector('.ai-report-heading');
                        if (headingEl) {
                            const headingText = headingEl.textContent.toLowerCase();
                            if (headingText.includes('summary') || 
                                headingText.includes('actions') || 
                                headingText.includes('business insight report')) {
                                section.classList.add('ai-full-width');
                                section.classList.remove('ai-half-width');
                            } else {
                                section.classList.add('ai-half-width');
                                section.classList.remove('ai-full-width');
                            }
                        } else {
                            section.classList.add('ai-full-width');
                        }
                    });
                } else {
                    if (aiProvenance) aiProvenance.innerHTML = '';
                    aiInsightContent.innerHTML = `<div style="grid-column: 1 / -1; color: var(--error);">Error: ${data.error || 'Unable to retrieve insights.'}</div>`;
                }
            } catch (error) {
                console.error('Error fetching AI insights:', error);
                if (aiProvenance) aiProvenance.innerHTML = '';
                aiInsightContent.innerHTML = '<div style="grid-column: 1 / -1; color: var(--error);">Failed to connect to AI Advisor service.</div>';
            } finally {
                askAiBtn.innerHTML = '<i class="fas fa-file-alt"></i> Generate Business Summary';
                askAiBtn.disabled = false;
            }
        });
    }

    // ==========================================
    // 7. Smart What-If Sales Analysis Controller
    // ==========================================
    const runWhatIfBtn = document.getElementById('run-whatif-btn');
    if (runWhatIfBtn) {
        runWhatIfBtn.addEventListener('click', async () => {
            const storeId = document.getElementById('whatif-store-id').value;
            const date = document.getElementById('whatif-date').value;

            // Baseline A
            const promoA = document.getElementById('whatif-promo-a').value;
            const holidayA = document.getElementById('whatif-holiday-a').value;
            const schoolA = document.getElementById('whatif-school-a').value;
            const compA = document.getElementById('whatif-comp-a').value;

            // Scenario B
            const promoB = document.getElementById('whatif-promo-b').value;
            const holidayB = document.getElementById('whatif-holiday-b').value;
            const schoolB = document.getElementById('whatif-school-b').value;
            const compB = document.getElementById('whatif-comp-b').value;

            const valAEl = document.getElementById('whatif-val-a');
            const valBEl = document.getElementById('whatif-val-b');
            const compCard = document.getElementById('whatif-comparison-card');
            const baseValEl = document.getElementById('comp-base-val');
            const simValEl = document.getElementById('comp-sim-val');
            const deltaAbsEl = document.getElementById('comp-delta-abs');
            const deltaPctEl = document.getElementById('comp-delta-pct');
            const sensitivityBar = document.getElementById('sensitivity-bar');

            runWhatIfBtn.disabled = true;
            runWhatIfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Simulating Scenarios...';
            valAEl.textContent = '...';
            valBEl.textContent = '...';

            try {
                const payloadA = {
                    store_id: storeId,
                    date: date,
                    promo: promoA,
                    state_holiday: holidayA,
                    school_holiday: schoolA
                };
                if (compA && compA.trim() !== '') {
                    payloadA.competition_distance = compA.trim();
                }

                const payloadB = {
                    store_id: storeId,
                    date: date,
                    promo: promoB,
                    state_holiday: holidayB,
                    school_holiday: schoolB
                };
                if (compB && compB.trim() !== '') {
                    payloadB.competition_distance = compB.trim();
                }

                // Call both predictions via the existing prediction backend
                const [resA, resB] = await Promise.all([
                    fetch(`${API_BASE}/predict`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payloadA)
                    }),
                    fetch(`${API_BASE}/predict`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payloadB)
                    })
                ]);

                const dataA = await resA.json();
                const dataB = await resB.json();

                if (!resA.ok || !resB.ok || dataA.status !== 'success' || dataB.status !== 'success') {
                    throw new Error(dataA.error || dataB.error || 'Scenario simulation failed.');
                }

                const predA = Number(dataA.prediction);
                const predB = Number(dataB.prediction);
                const deltaAbs = predB - predA;

                valAEl.textContent = `$${predA.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                valBEl.textContent = `$${predB.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

                baseValEl.textContent = `$${predA.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                simValEl.textContent = `$${predB.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

                const sign = deltaAbs >= 0 ? '+' : '';
                deltaAbsEl.textContent = `${sign}$${deltaAbs.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                deltaAbsEl.className = `comp-stat-val ${deltaAbs >= 0 ? 'positive' : 'negative'}`;

                // If baseline forecast is zero, division by zero is undefined -> display 'N/A'
                if (predA <= 0) {
                    deltaPctEl.textContent = 'N/A';
                    deltaPctEl.className = 'comp-stat-val';
                } else {
                    const deltaPct = (deltaAbs / predA) * 100;
                    deltaPctEl.textContent = `${sign}${deltaPct.toFixed(2)}%`;
                    deltaPctEl.className = `comp-stat-val ${deltaAbs >= 0 ? 'positive' : 'negative'}`;
                }

                // Calculate visual sensitivity share
                const total = predA + predB;
                const barPct = total > 0 ? (predB / total) * 100 : 50;
                sensitivityBar.style.width = `${Math.min(95, Math.max(5, barPct))}%`;

                compCard.style.display = 'block';
            } catch (err) {
                console.error('What-If simulation error:', err);
                alert('What-If Simulation Failed: ' + err.message);
            } finally {
                runWhatIfBtn.disabled = false;
                runWhatIfBtn.innerHTML = '<i class="fas fa-play"></i> Run Scenario Comparison';
            }
        });
    }

    // ==========================================
    // 8. Market Intelligence Controller
    // ==========================================
    // Tab Switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPaneId = btn.getAttribute('data-tab');
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // Helper: render clean disclaimer note
    function getDisclaimerHtml(disclaimer) {
        if (!disclaimer) return '';
        return `
            <p class="market-disclaimer-note">
                <i class="fas fa-info-circle"></i>
                <span>Illustrative benchmark data displayed when external search API operates in simulated mode.</span>
            </p>
        `;
    }

    // Helper: render clean source note
    function getSourceBadge(isFallback) {
        if (isFallback) {
            return '<span class="market-source-note"><i class="fas fa-circle-notch"></i> Illustrative simulated benchmark</span>';
        }
        return '<span class="market-source-note live"><i class="fas fa-circle" style="font-size: 0.45rem;"></i> Live search</span>';
    }

    // Helper: render legitimate URL or simulated benchmark label
    function renderCardLinkOrSource(item, isFallback) {
        if (!isFallback && item.url && (item.url.startsWith('http://') || item.url.startsWith('https://')) && !item.url.includes('example.com')) {
            return `<a href="${item.url}" target="_blank" rel="noopener noreferrer" class="market-card-link"><i class="fas fa-external-link-alt"></i> ${item.url}</a>`;
        }
        return `<div class="market-card-source"><span class="source-label">Source:</span> Illustrative simulated benchmark</div>`;
    }

    // 8A. Competitor Analysis
    const searchCompetitorBtn = document.getElementById('search-competitor-btn');
    const competitorInput = document.getElementById('competitor-input');
    const competitorResults = document.getElementById('competitor-results');

    if (searchCompetitorBtn && competitorInput && competitorResults) {
        searchCompetitorBtn.addEventListener('click', async () => {
            const name = competitorInput.value.trim();
            if (!name) {
                alert('Please enter a competitor name.');
                return;
            }

            searchCompetitorBtn.disabled = true;
            searchCompetitorBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            competitorResults.innerHTML = '<p class="market-empty-text"><i class="fas fa-spinner fa-spin"></i> Retrieving competitor intelligence...</p>';

            try {
                const response = await fetch(`${API_BASE}/market/competitor`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ competitor_name: name })
                });

                const data = await response.json();
                if (response.ok && data.status === 'success') {
                    const isFallback = Boolean(data.is_fallback);
                    let html = '';

                    if (isFallback && data.disclaimer) {
                        html += getDisclaimerHtml(data.disclaimer);
                    }

                    html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; margin-bottom: 0.75rem;">
                        <h3 style="font-size: 1.05rem; color: var(--text-main); font-weight: 600;">Findings for ${data.competitor}</h3>
                        ${getSourceBadge(isFallback)}
                    </div>`;

                    if (Array.isArray(data.findings) && data.findings.length > 0) {
                        data.findings.forEach(f => {
                            html += `
                                <div class="market-card">
                                    <div class="market-card-header">
                                        <div class="market-card-title">${f.title || 'Market Finding'}</div>
                                    </div>
                                    <div class="market-card-snippet">${f.snippet || 'No description available.'}</div>
                                    ${renderCardLinkOrSource(f, isFallback)}
                                </div>
                            `;
                        });
                    } else {
                        html += '<p class="market-empty-text">No organic search findings returned for this query.</p>';
                    }

                    competitorResults.innerHTML = html;
                } else {
                    competitorResults.innerHTML = `<p style="color: var(--error);">Error: ${data.error || 'Failed to retrieve competitor analysis.'}</p>`;
                }
            } catch (err) {
                console.error('Competitor search error:', err);
                competitorResults.innerHTML = '<p style="color: var(--error);">Unable to connect to market service.</p>';
            } finally {
                searchCompetitorBtn.disabled = false;
                searchCompetitorBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Competitor';
            }
        });
    }

    // 8B. Keyword & Demand Analysis
    const searchKeywordBtn = document.getElementById('search-keyword-btn');
    const keywordInput = document.getElementById('keyword-input');
    const keywordResults = document.getElementById('keyword-results');

    if (searchKeywordBtn && keywordInput && keywordResults) {
        searchKeywordBtn.addEventListener('click', async () => {
            const topic = keywordInput.value.trim();
            if (!topic) {
                alert('Please enter a retail keyword or category.');
                return;
            }

            searchKeywordBtn.disabled = true;
            searchKeywordBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Researching...';
            keywordResults.innerHTML = '<p class="market-empty-text"><i class="fas fa-spinner fa-spin"></i> Querying search patterns and demand keywords...</p>';

            try {
                const response = await fetch(`${API_BASE}/market/keyword`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: topic })
                });

                const data = await response.json();
                if (response.ok && data.status === 'success') {
                    const isFallback = Boolean(data.is_fallback);
                    let html = '';

                    if (isFallback && data.disclaimer) {
                        html += getDisclaimerHtml(data.disclaimer);
                    }

                    html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; margin-bottom: 0.75rem;">
                        <h3 style="font-size: 1.05rem; color: var(--text-main); font-weight: 600;">Demand Patterns for "${data.topic}"</h3>
                        ${getSourceBadge(isFallback)}
                    </div>`;

                    if (Array.isArray(data.related_keywords) && data.related_keywords.length > 0) {
                        html += `
                            <div class="market-card">
                                <div class="market-card-title" style="font-size: 0.875rem; margin-bottom: 0.4rem;"><i class="fas fa-tags"></i> Related Consumer Search Queries</div>
                                <div class="keyword-cloud">
                                    ${data.related_keywords.map(kw => `<span class="keyword-pill">${kw}</span>`).join('')}
                                </div>
                            </div>
                        `;
                    }

                    if (Array.isArray(data.top_results) && data.top_results.length > 0) {
                        data.top_results.forEach(r => {
                            html += `
                                <div class="market-card">
                                    <div class="market-card-title">${r.title || 'Market Search Result'}</div>
                                    <div class="market-card-snippet">${r.snippet || 'No description available.'}</div>
                                    ${renderCardLinkOrSource(r, isFallback)}
                                </div>
                            `;
                        });
                    }

                    keywordResults.innerHTML = html;
                } else {
                    keywordResults.innerHTML = `<p style="color: var(--error);">Error: ${data.error || 'Failed to retrieve keyword research.'}</p>`;
                }
            } catch (err) {
                console.error('Keyword search error:', err);
                keywordResults.innerHTML = '<p style="color: var(--error);">Unable to connect to keyword service.</p>';
            } finally {
                searchKeywordBtn.disabled = false;
                searchKeywordBtn.innerHTML = '<i class="fas fa-search"></i> Research Keywords';
            }
        });
    }

    // 8C. Trend Discovery
    const searchTrendBtn = document.getElementById('search-trend-btn');
    const trendInput = document.getElementById('trend-input');
    const trendResults = document.getElementById('trend-results');

    if (searchTrendBtn && trendInput && trendResults) {
        searchTrendBtn.addEventListener('click', async () => {
            const industry = trendInput.value.trim();
            if (!industry) {
                alert('Please enter an industry or retail sector.');
                return;
            }

            searchTrendBtn.disabled = true;
            searchTrendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Discovering...';
            trendResults.innerHTML = '<p class="market-empty-text"><i class="fas fa-spinner fa-spin"></i> Scanning retail industry trends...</p>';

            try {
                const response = await fetch(`${API_BASE}/market/trend`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ industry: industry })
                });

                const data = await response.json();
                if (response.ok && data.status === 'success') {
                    const isFallback = Boolean(data.is_fallback);
                    let html = '';

                    if (isFallback && data.disclaimer) {
                        html += getDisclaimerHtml(data.disclaimer);
                    }

                    html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; margin-bottom: 0.75rem;">
                        <h3 style="font-size: 1.05rem; color: var(--text-main); font-weight: 600;">Macro Trends: ${data.industry}</h3>
                        ${getSourceBadge(isFallback)}
                    </div>`;

                    if (Array.isArray(data.recent_trends) && data.recent_trends.length > 0) {
                        data.recent_trends.forEach(t => {
                            html += `
                                <div class="market-card">
                                    <div class="market-card-title">${t.title || 'Retail Trend Finding'}</div>
                                    <div class="market-card-snippet">${t.snippet || 'No description available.'}</div>
                                    ${renderCardLinkOrSource(t, isFallback)}
                                </div>
                            `;
                        });
                    } else {
                        html += '<p class="market-empty-text">No trend findings returned for this sector.</p>';
                    }

                    trendResults.innerHTML = html;
                } else {
                    trendResults.innerHTML = `<p style="color: var(--error);">Error: ${data.error || 'Failed to retrieve industry trends.'}</p>`;
                }
            } catch (err) {
                console.error('Trend search error:', err);
                trendResults.innerHTML = '<p style="color: var(--error);">Unable to connect to trend service.</p>';
            } finally {
                searchTrendBtn.disabled = false;
                searchTrendBtn.innerHTML = '<i class="fas fa-search"></i> Discover Trends';
            }
        });
    }

});
