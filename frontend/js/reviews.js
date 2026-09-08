/**
 * Reviews Module
 */

const reviews = {
    currentPage: 1,
    pageSize: 15,
    totalItems: 0,
    filters: {
        destination_id: '',
        sentiment: '',
        min_rating: '',
        max_rating: ''
    },
    sentimentSummary: null,
    
    async init() {
        const container = document.getElementById('dashboardContainer');
        if (!container) return;
        
        try {
            await this.render(container);
            await this.loadSentimentSummary();
            await this.loadReviews();
        } catch (error) {
            console.error('Reviews init error:', error);
            showToast('Error loading reviews: ' + error.message, 'error');
        }
    },
    
    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2>💬 Tourist Reviews</h2>
                <p>Analyze what tourists are saying about Timor-Leste destinations</p>
            </div>
            
            <div class="sentiment-summary" id="sentimentSummary" style="margin-bottom: 24px;">
                <!-- Rendered by JS -->
            </div>
            
            <div class="filter-bar" id="reviewFilterBar">
                <div class="filter-group">
                    <label>Sentiment</label>
                    <select id="sentimentFilter">
                        <option value="">All</option>
                        <option value="Positive">Positive</option>
                        <option value="Neutral">Neutral</option>
                        <option value="Negative">Negative</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Min Rating</label>
                    <select id="minRatingFilter">
                        <option value="">Any</option>
                        <option value="1">1★</option>
                        <option value="2">2★</option>
                        <option value="3">3★</option>
                        <option value="4">4★</option>
                        <option value="5">5★</option>
                    </select>
                </div>
                <button class="btn btn-primary btn-sm" onclick="reviews.applyFilters()">
                    <i class="fas fa-filter"></i> Apply
                </button>
                <button class="btn btn-outline btn-sm" onclick="reviews.resetFilters()">
                    <i class="fas fa-undo"></i> Reset
                </button>
            </div>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Review</th>
                            <th>Destination</th>
                            <th>Rating</th>
                            <th>Sentiment</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody id="reviewsTableBody">
                        <!-- Rendered by JS -->
                    </tbody>
                </table>
            </div>
            
            <div class="pagination" id="reviewPagination">
                <!-- Rendered by JS -->
            </div>
        `;
        
        // Event listeners
        document.getElementById('sentimentFilter').addEventListener('change', () => {
            this.filters.sentiment = document.getElementById('sentimentFilter').value;
            this.currentPage = 1;
            this.loadReviews();
        });
        
        document.getElementById('minRatingFilter').addEventListener('change', () => {
            this.filters.min_rating = document.getElementById('minRatingFilter').value;
            this.currentPage = 1;
            this.loadReviews();
        });
    },
    
    async loadSentimentSummary() {
        try {
            this.sentimentSummary = await api.getSentimentSummaryGlobal();
            this.renderSentimentSummary();
        } catch (error) {
            console.error('Error loading sentiment summary:', error);
        }
    },
    
    renderSentimentSummary() {
        const container = document.getElementById('sentimentSummary');
        if (!container || !this.sentimentSummary) return;
        
        const { positive, neutral, negative, total, average_score } = this.sentimentSummary;
        
        container.innerHTML = `
            <div class="sentiment-item positive">
                <div class="value">${positive || 0}%</div>
                <div class="label">😊 Positive</div>
            </div>
            <div class="sentiment-item neutral">
                <div class="value">${neutral || 0}%</div>
                <div class="label">😐 Neutral</div>
            </div>
            <div class="sentiment-item negative">
                <div class="value">${negative || 0}%</div>
                <div class="label">😞 Negative</div>
            </div>
            <div style="text-align: center; padding: 16px; background: var(--background); border-radius: var(--radius-sm);">
                <div style="font-size: 24px; font-weight: 700; color: var(--text);">${formatNumber(total)}</div>
                <div style="font-size: 13px; color: var(--text-secondary);">Total Reviews</div>
                <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">
                    Avg Score: ${average_score ? average_score.toFixed(3) : '0.000'}
                </div>
            </div>
        `;
    },
    
    async loadReviews() {
        const tbody = document.getElementById('reviewsTableBody');
        showLoading(tbody, 'Loading reviews...');
        
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
            
            const response = await api.getReviews(params);
            const items = response.items || [];
            this.totalItems = response.total || 0;
            
            this.renderReviews(items);
            this.renderPagination();
            
        } catch (error) {
            console.error('Error loading reviews:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 24px; color: var(--text-muted);"></i>
                        <p style="margin-top: 8px; color: var(--text-secondary);">Error loading reviews</p>
                    </td>
                </tr>
            `;
            showToast('Error loading reviews', 'error');
        }
    },
    
    renderReviews(items) {
        const tbody = document.getElementById('reviewsTableBody');
        
        if (!items || items.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px;">
                        <i class="fas fa-search" style="font-size: 24px; color: var(--text-muted);"></i>
                        <p style="margin-top: 8px; color: var(--text-secondary);">No reviews found</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = items.map(review => `
            <tr>
                <td style="max-width: 300px;">
                    <div style="font-weight: 500;">${escapeHtml(truncateText(review.review_text || 'No text', 80))}</div>
                    ${review.source ? `<div style="font-size: 12px; color: var(--text-muted);">Source: ${escapeHtml(review.source)}</div>` : ''}
                </td>
                <td>
                    <span style="font-weight: 500;">${escapeHtml(review.destination_name || 'Unknown')}</span>
                </td>
                <td>
                    <span style="color: #F59E0B;">${getRatingStars(review.rating || 0)}</span>
                    <span style="font-weight: 600;">${review.rating || '0.0'}</span>
                </td>
                <td>${getSentimentBadge(review.sentiment)}</td>
                <td style="font-size: 13px; color: var(--text-secondary);">
                    ${review.review_date ? formatDate(review.review_date) : formatDate(review.created_at)}
                </td>
            </tr>
        `).join('');
    },
    
    renderPagination() {
        const container = document.getElementById('reviewPagination');
        const totalPages = Math.ceil(this.totalItems / this.pageSize);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<div style="display: flex; gap: 8px; justify-content: center; margin-top: 24px;">';
        
        if (this.currentPage > 1) {
            html += `<button class="btn btn-outline btn-sm" onclick="reviews.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>`;
        }
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                html += `<button class="btn btn-primary btn-sm" disabled>${i}</button>`;
            } else if (i === 1 || i === totalPages || Math.abs(i - this.currentPage) <= 2) {
                html += `<button class="btn btn-outline btn-sm" onclick="reviews.goToPage(${i})">${i}</button>`;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                html += `<span style="padding: 6px 8px;">...</span>`;
            }
        }
        
        if (this.currentPage < totalPages) {
            html += `<button class="btn btn-outline btn-sm" onclick="reviews.goToPage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>`;
        }
        
        html += '</div>';
        container.innerHTML = html;
    },
    
    goToPage(page) {
        this.currentPage = page;
        this.loadReviews();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    applyFilters() {
        this.currentPage = 1;
        this.loadReviews();
    },
    
    resetFilters() {
        this.filters = {
            destination_id: '',
            sentiment: '',
            min_rating: '',
            max_rating: ''
        };
        this.currentPage = 1;
        
        document.getElementById('sentimentFilter').value = '';
        document.getElementById('minRatingFilter').value = '';
        
        this.loadReviews();
    }
};

// Load reviews function for navigation
function loadReviews() {
    const container = document.getElementById('dashboardContainer') || document.getElementById('appContent');
    if (container) {
        reviews.init();
    }
}