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
            // Local development server running on a separate port (e.g. Live Server on 5500, 3000, 8080)
            if ((window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && 
                window.location.port !== '5000' && window.location.port !== '') {
                return 'http://localhost:5000';
            }
            // Same origin for production deployment on Render and local Flask server
            return '';
        }
        // 3. Fallback for file:// execution
        return 'http://localhost:5000';
    }

    const API_BASE = getApiBaseUrl();

    // ==========================================
    // 2. Light / Dark Theme Controller
    // ==========================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (themeIcon) {
                themeIcon.className = 'fas fa-sun';
            }
            if (themeText) {
                themeText.textContent = 'Light Mode';
            }
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            if (themeIcon) {
                themeIcon.className = 'fas fa-moon';
            }
            if (themeText) {
                themeText.textContent = 'Dark Mode';
            }
        }
    }

    // Default to 'light' for first-time visitors
    const initialTheme = localStorage.getItem('businessmind_theme') || 'light';
    applyTheme(initialTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const activeTheme = document.documentElement.getAttribute('data-theme');
            const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
            localStorage.setItem('businessmind_theme', nextTheme);
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
            aiInsightContent.innerHTML = '<div style="grid-column: 1 / -1; padding: 1.5rem; color: var(--text-muted);"><i class="fas fa-spinner fa-spin"></i> Synthesizing executive business insights...</div>';
            
            try {
                const response = await fetch(`${API_BASE}/insights`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(lastPredictionData)
                });
                
                const data = await response.json();
                
                if (response.ok && (data.status === 'success' || data.status === 'fallback')) {
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
                    aiInsightContent.innerHTML = `<div style="grid-column: 1 / -1; color: var(--danger);">Error: ${data.error || 'Unable to retrieve insights.'}</div>`;
                }
            } catch (error) {
                console.error('Error fetching AI insights:', error);
                aiInsightContent.innerHTML = '<div style="grid-column: 1 / -1; color: var(--danger);">Failed to connect to business insights service.</div>';
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

});
