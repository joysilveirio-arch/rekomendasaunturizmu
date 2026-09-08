/**
 * Destinations Module
 */

const destinations = {
    currentPage: 1,
    pageSize: 12,
    totalItems: 0,
    filters: {
        search: '',
        category: '',
        municipality: '',
        min_rating: '',
        sort_by: 'popularity_score',
        sort_order: 'desc'
    },
    destinations: [],
    categories: [],
    municipalities: [],
    
    async init() {
        const container = document.getElementById('dashboardContainer');
        if (!container) return;
        
        try {
            await this.render(container);
            await this.loadFilters();
            await this.loadDestinations();
        } catch (error) {
            console.error('Destinations init error:', error);
            showToast('Error loading destinations: ' + error.message, 'error');
        }
    },
    
    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2>🏝️ Explore Destinations</h2>
                <p>Discover the best tourism destinations in Timor-Leste</p>
            </div>
            
            <div class="filter-bar" id="destFilterBar">
                <div class="filter-group">
                    <label><i class="fas fa-search"></i></label>
                    <input type="text" id="searchInput" placeholder="Search destinations..." />
                </div>
                <div class="filter-group">
                    <label>Category</label>
                    <select id="categoryFilter">
                        <option value="">All Categories</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Municipality</label>
                    <select id="municipalityFilter">
                        <option value="">All Municipalities</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Min Rating</label>
                    <select id="ratingFilter">
                        <option value="">Any</option>
                        <option value="4.0">4.0+</option>
                        <option value="4.5">4.5+</option>
                        <option value="4.8">4.8+</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Sort</label>
                    <select id="sortFilter">
                        <option value="popularity_score">Popularity</option>
                        <option value="rating">Rating</option>
                        <option value="name">Name</option>
                    </select>
                </div>
                <button class="btn btn-primary btn-sm" onclick="destinations.applyFilters()">
                    <i class="fas fa-filter"></i> Apply
                </button>
                <button class="btn btn-outline btn-sm" onclick="destinations.resetFilters()">
                    <i class="fas fa-undo"></i> Reset
                </button>
            </div>
            
            <div id="destinationsGrid" class="grid-3">
                <!-- Rendered by JS -->
            </div>
            
            <div class="pagination" id="destPagination">
                <!-- Rendered by JS -->
            </div>
        `;
        
        // Event listeners
        document.getElementById('searchInput').addEventListener('keyup', debounce((e) => {
            this.filters.search = e.target.value;
            this.currentPage = 1;
            this.loadDestinations();
        }, 300));
        
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.currentPage = 1;
            this.loadDestinations();
        });
        
        document.getElementById('municipalityFilter').addEventListener('change', (e) => {
            this.filters.municipality = e.target.value;
            this.currentPage = 1;
            this.loadDestinations();
        });
        
        document.getElementById('ratingFilter').addEventListener('change', (e) => {
            this.filters.min_rating = e.target.value;
            this.currentPage = 1;
            this.loadDestinations();
        });
        
        document.getElementById('sortFilter').addEventListener('change', (e) => {
            this.filters.sort_by = e.target.value;
            this.loadDestinations();
        });
    },
    
    async loadFilters() {
        try {
            const [categories, municipalities] = await Promise.all([
                api.getCategories(),
                api.getMunicipalities()
            ]);
            
            this.categories = categories.categories || [];
            this.municipalities = municipalities.municipalities || [];
            
            // Populate category filter
            const categorySelect = document.getElementById('categoryFilter');
            this.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                categorySelect.appendChild(option);
            });
            
            // Populate municipality filter
            const municipalitySelect = document.getElementById('municipalityFilter');
            this.municipalities.forEach(mun => {
                const option = document.createElement('option');
                option.value = mun;
                option.textContent = mun;
                municipalitySelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading filters:', error);
        }
    },
    
    async loadDestinations() {
        const grid = document.getElementById('destinationsGrid');
        showLoading(grid, 'Loading destinations...');
        
        try {
            const params = {
                skip: (this.currentPage - 1) * this.pageSize,
                limit: this.pageSize,
                ...this.filters
            };
            
            // Remove empty filters
            Object.keys(params).forEach(key => {
                if (params[key] === '' || params[key] === null || params[key] === undefined) {
                    delete params[key];
                }
            });
            
            const response = await api.getDestinations(params);
            this.destinations = response.items || [];
            this.totalItems = response.total || 0;
            
            this.renderDestinations();
            this.renderPagination();
            
        } catch (error) {
            console.error('Error loading destinations:', error);
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error Loading Destinations</h3>
                    <p>${error.message}</p>
                </div>
            `;
            showToast('Error loading destinations', 'error');
        }
    },
    
    renderDestinations() {
        const grid = document.getElementById('destinationsGrid');
        
        if (!this.destinations || this.destinations.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <i class="fas fa-search"></i>
                    <h3>No destinations found</h3>
                    <p>Try adjusting your filters or search query</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = this.destinations.map(dest => `
            <div class="card destination-card" onclick="destinations.viewDestination(${dest.id})">
                <div class="destination-image" style="background: linear-gradient(135deg, var(--primary-light), var(--primary)); height: 160px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; margin-bottom: 12px;">
                    ${dest.category === 'Beach' ? '🏖️' : 
                      dest.category === 'Nature' ? '🌿' : 
                      dest.category === 'Cultural' ? '🏛️' : 
                      dest.category === 'Adventure' ? '⛰️' : '📍'}
                </div>
                <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">${escapeHtml(dest.name)}</h3>
                <p style="color: var(--text-secondary); font-size: 14px; margin-bottom: 8px;">
                    <i class="fas fa-map-marker-alt" style="color: var(--primary);"></i> ${escapeHtml(dest.municipality || 'Unknown')}
                </p>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="color: #F59E0B;">${getRatingStars(dest.rating || 0)}</span>
                    <span style="font-weight: 600;">${dest.rating || '0.0'}</span>
                </div>
                <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px;">
                    <span class="badge badge-primary">${escapeHtml(dest.category || 'General')}</span>
                    <span class="badge badge-neutral">${formatNumber(dest.review_count || 0)} reviews</span>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 8px;">
                    <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); destinations.viewDestination(${dest.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); navigateTo('recommendations')">
                        <i class="fas fa-compass"></i> Explore
                    </button>
                </div>
            </div>
        `).join('');
    },
    
    renderPagination() {
        const container = document.getElementById('destPagination');
        const totalPages = Math.ceil(this.totalItems / this.pageSize);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<div style="display: flex; gap: 8px; justify-content: center; margin-top: 24px;">';
        
        if (this.currentPage > 1) {
            html += `<button class="btn btn-outline btn-sm" onclick="destinations.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>`;
        }
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                html += `<button class="btn btn-primary btn-sm" disabled>${i}</button>`;
            } else if (i === 1 || i === totalPages || Math.abs(i - this.currentPage) <= 2) {
                html += `<button class="btn btn-outline btn-sm" onclick="destinations.goToPage(${i})">${i}</button>`;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                html += `<span style="padding: 6px 8px;">...</span>`;
            }
        }
        
        if (this.currentPage < totalPages) {
            html += `<button class="btn btn-outline btn-sm" onclick="destinations.goToPage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>`;
        }
        
        html += '</div>';
        container.innerHTML = html;
    },
    
    goToPage(page) {
        this.currentPage = page;
        this.loadDestinations();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    applyFilters() {
        this.currentPage = 1;
        this.loadDestinations();
    },
    
    resetFilters() {
        this.filters = {
            search: '',
            category: '',
            municipality: '',
            min_rating: '',
            sort_by: 'popularity_score',
            sort_order: 'desc'
        };
        this.currentPage = 1;
        
        document.getElementById('searchInput').value = '';
        document.getElementById('categoryFilter').value = '';
        document.getElementById('municipalityFilter').value = '';
        document.getElementById('ratingFilter').value = '';
        document.getElementById('sortFilter').value = 'popularity_score';
        
        this.loadDestinations();
    },
    
    async viewDestination(id) {
        try {
            const dest = await api.getDestination(id);
            const sentiment = await api.getDestinationSentiment(id);
            
            // Show destination detail modal or navigate
            this.showDetailModal(dest, sentiment);
        } catch (error) {
            console.error('Error loading destination details:', error);
            showToast('Error loading destination details', 'error');
        }
    },
    
    showDetailModal(dest, sentiment) {
        // Create and show a modal with destination details
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            animation: fadeIn 0.3s ease;
        `;
        
        modal.innerHTML = `
            <div style="background: var(--surface); border-radius: var(--radius); max-width: 700px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 32px; position: relative;">
                <button onclick="this.closest('div[style]').remove()" style="position: absolute; top: 16px; right: 16px; background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary);">
                    <i class="fas fa-times"></i>
                </button>
                
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                    <div style="font-size: 48px;">${dest.category === 'Beach' ? '🏖️' : 
                        dest.category === 'Nature' ? '🌿' : 
                        dest.category === 'Cultural' ? '🏛️' : 
                        dest.category === 'Adventure' ? '⛰️' : '📍'}</div>
                    <div>
                        <h2 style="font-size: 28px; font-weight: 700;">${escapeHtml(dest.name)}</h2>
                        <p style="color: var(--text-secondary);">
                            <i class="fas fa-map-marker-alt" style="color: var(--primary);"></i> ${escapeHtml(dest.municipality || 'Unknown')}
                        </p>
                    </div>
                </div>
                
                <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 4px; font-size: 18px; font-weight: 600; color: #F59E0B;">
                        ${getRatingStars(dest.rating || 0)} ${dest.rating || '0.0'}
                    </div>
                    <span class="badge badge-primary">${escapeHtml(dest.category || 'General')}</span>
                    <span class="badge badge-neutral">${formatNumber(dest.review_count || 0)} reviews</span>
                    <span class="badge ${dest.price_level === 'Low' ? 'badge-success' : dest.price_level === 'High' ? 'badge-negative' : 'badge-neutral'}">
                        ${dest.price_level || 'Medium'} Budget
                    </span>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <h4 style="font-weight: 600; margin-bottom: 4px;">Description</h4>
                    <p style="color: var(--text-secondary);">${escapeHtml(dest.description || 'No description available.')}</p>
                </div>
                
                ${sentiment ? `
                    <div style="margin-bottom: 16px;">
                        <h4 style="font-weight: 600; margin-bottom: 8px;">Sentiment Analysis</h4>
                        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                            <div style="background: rgba(34, 197, 94, 0.1); padding: 8px 16px; border-radius: var(--radius-sm);">
                                <span style="color: var(--success);">😊 Positive ${sentiment.positive || 0}%</span>
                            </div>
                            <div style="background: rgba(245, 158, 11, 0.1); padding: 8px 16px; border-radius: var(--radius-sm);">
                                <span style="color: var(--warning);">😐 Neutral ${sentiment.neutral || 0}%</span>
                            </div>
                            <div style="background: rgba(239, 68, 68, 0.1); padding: 8px 16px; border-radius: var(--radius-sm);">
                                <span style="color: var(--danger);">😞 Negative ${sentiment.negative || 0}%</span>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <div style="display: flex; gap: 8px; margin-top: 16px;">
                    <button class="btn btn-primary" onclick="navigateTo('recommendations')">
                        <i class="fas fa-compass"></i> Get Recommendations
                    </button>
                    <button class="btn btn-outline" onclick="this.closest('div[style]').remove()">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }
};

// Load destinations function for navigation
function loadDestinations(query = '') {
    const container = document.getElementById('dashboardContainer') || document.getElementById('appContent');
    if (container) {
        if (query) {
            destinations.filters.search = query;
        }
        destinations.init();
    }
}