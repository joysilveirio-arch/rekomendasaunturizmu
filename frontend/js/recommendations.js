/**
 * Recommendations Module
 */

const recommendations = {
    userTypes: [],
    budgetOptions: [],
    results: [],
    isGenerating: false,
    
    async init() {
        const container = document.getElementById('dashboardContainer');
        if (!container) return;
        
        try {
            await this.render(container);
            await this.loadOptions();
        } catch (error) {
            console.error('Recommendations init error:', error);
            showToast('Error loading recommendations: ' + error.message, 'error');
        }
    },
    
    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2>🎯 Find Your Perfect Destination</h2>
                <p>Tell us what kind of experience you want, and we'll find the best matches</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 24px;">
                <div class="card" style="position: sticky; top: 90px;">
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Your Preferences</h3>
                    
                    <div class="form-group">
                        <label>Tourist Type</label>
                        <select id="userTypeSelect">
                            <option value="">Select your type...</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Category</label>
                        <select id="categorySelect">
                            <option value="">Any</option>
                            <option value="Beach">🏖️ Beach</option>
                            <option value="Nature">🌿 Nature</option>
                            <option value="Cultural">🏛️ Cultural</option>
                            <option value="Adventure">⛰️ Adventure</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Preferred Municipality</label>
                        <select id="municipalitySelect">
                            <option value="">Any</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Minimum Rating</label>
                        <select id="minRatingSelect">
                            <option value="3.0">3.0+</option>
                            <option value="3.5">3.5+</option>
                            <option value="4.0" selected>4.0+</option>
                            <option value="4.5">4.5+</option>
                            <option value="4.8">4.8+</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Budget</label>
                        <select id="budgetSelect">
                            <option value="Low">💰 Low</option>
                            <option value="Medium" selected>💰💰 Medium</option>
                            <option value="High">💰💰💰 High</option>
                        </select>
                    </div>
                    
                    <button class="btn btn-primary" id="generateBtn" style="width: 100%; justify-content: center;">
                        <i class="fas fa-compass"></i> Generate Recommendations
                    </button>
                </div>
                
                <div>
                    <div id="recommendationResults">
                        <div class="empty-state" style="padding: 40px 20px;">
                            <i class="fas fa-compass" style="font-size: 48px; color: var(--text-muted);"></i>
                            <h3>Ready to Explore</h3>
                            <p>Fill in your preferences and click "Generate Recommendations" to find your perfect destination in Timor-Leste.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Event listener for generate button
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generateRecommendations();
        });
        
        // Also generate on Enter key
        document.querySelectorAll('#userTypeSelect, #categorySelect, #municipalitySelect, #minRatingSelect, #budgetSelect')
            .forEach(el => {
                el.addEventListener('keyup', (e) => {
                    if (e.key === 'Enter') this.generateRecommendations();
                });
            });
    },
    
    async loadOptions() {
        try {
            // Load municipalities
            const municipalities = await api.getMunicipalities();
            const munSelect = document.getElementById('municipalitySelect');
            (municipalities.municipalities || []).forEach(mun => {
                const option = document.createElement('option');
                option.value = mun;
                option.textContent = mun;
                munSelect.appendChild(option);
            });
            
            // Load user types
            const userTypes = await api.getUserTypes();
            this.userTypes = userTypes.user_types || [];
            const typeSelect = document.getElementById('userTypeSelect');
            this.userTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                typeSelect.appendChild(option);
            });
            
            // Load budget options
            const budgets = await api.getBudgetOptions();
            this.budgetOptions = budgets.budget_options || [];
            
        } catch (error) {
            console.error('Error loading options:', error);
            showToast('Error loading options', 'warning');
        }
    },
    
    async generateRecommendations() {
        if (this.isGenerating) return;
        
        const userType = document.getElementById('userTypeSelect').value;
        if (!userType) {
            showToast('Please select your tourist type', 'warning');
            return;
        }
        
        this.isGenerating = true;
        const btn = document.getElementById('generateBtn');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;
        
        const resultsContainer = document.getElementById('recommendationResults');
        showLoading(resultsContainer, 'Finding the best destinations for you...');
        
        try {
            const params = {
                user_type: userType,
                category: document.getElementById('categorySelect').value || '',
                municipality: document.getElementById('municipalitySelect').value || '',
                min_rating: parseFloat(document.getElementById('minRatingSelect').value) || 3.0,
                budget: document.getElementById('budgetSelect').value || 'Medium',
                limit: 10
            };
            
            const response = await api.getRecommendations(params);
            this.results = response.recommendations || [];
            
            this.renderResults();
            
            if (this.results.length === 0) {
                showToast('No recommendations found matching your criteria', 'info');
            } else {
                showToast(`Found ${this.results.length} recommendations! 🎉`, 'success');
            }
            
        } catch (error) {
            console.error('Error generating recommendations:', error);
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: var(--danger);"></i>
                    <h3>Error Generating Recommendations</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="recommendations.generateRecommendations()" style="margin-top: 16px;">
                        <i class="fas fa-redo"></i> Try Again
                    </button>
                </div>
            `;
            showToast('Error generating recommendations', 'error');
        } finally {
            this.isGenerating = false;
            btn.innerHTML = '<i class="fas fa-compass"></i> Generate Recommendations';
            btn.disabled = false;
        }
    },
    
    renderResults() {
        const container = document.getElementById('recommendationResults');
        
        if (!this.results || this.results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search" style="font-size: 48px; color: var(--text-muted);"></i>
                    <h3>No matches found</h3>
                    <p>Try adjusting your preferences to find more destinations.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">
                🎯 Recommended for You (${this.results.length})
            </h3>
            ${this.results.map((item, index) => this.renderRecommendationItem(item, index)).join('')}
        `;
    },
    
    renderRecommendationItem(item, index) {
        const dest = item.destination;
        const score = (item.score * 100).toFixed(0);
        const matchDetails = item.match_details || {};
        
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`;
        
        return `
            <div class="card" style="margin-bottom: 16px; animation: slideIn 0.3s ease; animation-delay: ${index * 0.05}s;">
                <div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                        <div style="font-size: 32px; font-weight: 700; color: var(--text-muted); min-width: 40px;">
                            ${medal}
                        </div>
                        <div>
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <h4 style="font-size: 18px; font-weight: 600;">${escapeHtml(dest.name)}</h4>
                                <span class="badge badge-primary">${escapeHtml(dest.category || 'General')}</span>
                                <span class="badge badge-neutral">${escapeHtml(dest.municipality || 'Unknown')}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-top: 4px;">
                                <span style="color: #F59E0B;">${getRatingStars(dest.rating || 0)} ${dest.rating || '0.0'}</span>
                                <span style="color: var(--text-secondary); font-size: 14px;">
                                    ${formatNumber(dest.review_count || 0)} reviews
                                </span>
                                <span style="color: var(--text-secondary); font-size: 14px;">
                                    💰 ${dest.price_level || 'Medium'}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; min-width: 80px;">
                        <div style="font-size: 28px; font-weight: 700; color: var(--success);">
                            ${score}%
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Match Score</div>
                        <div class="progress-bar" style="width: 80px; margin: 4px auto 0;">
                            <div class="progress-fill success" style="width: ${score}%;"></div>
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap;">
                    <button class="btn btn-primary btn-sm" onclick="destinations.viewDestination(${dest.id})">
                        <i class="fas fa-eye"></i> Explore
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="navigateTo('destinations')">
                        <i class="fas fa-map-marker-alt"></i> More Destinations
                    </button>
                </div>
            </div>
        `;
    }
};

// Load recommendations function for navigation
function loadRecommendations() {
    const container = document.getElementById('dashboardContainer') || document.getElementById('appContent');
    if (container) {
        recommendations.init();
    }
}