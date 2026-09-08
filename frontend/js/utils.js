/**
 * Utility Functions
 */

// Toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <span class="toast-icon"><i class="fas ${icons[type] || icons.info}"></i></span>
        <span class="toast-message">${message}</span>
        <button class="toast-close"><i class="fas fa-times"></i></button>
    `;
    
    container.appendChild(toast);
    
    // Auto dismiss
    const timeout = setTimeout(() => {
        toast.remove();
    }, duration);
    
    // Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(timeout);
        toast.remove();
    });
    
    return toast;
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format number with commas
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString('en-US');
}

// Truncate text
function truncateText(text, maxLength = 100) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
}

// Get rating stars
function getRatingStars(rating) {
    const full = Math.floor(rating);
    const half = rating - full >= 0.5 ? 1 : 0;
    const empty = 5 - full - half;
    
    let stars = '';
    for (let i = 0; i < full; i++) stars += '<i class="fas fa-star"></i>';
    if (half) stars += '<i class="fas fa-star-half-alt"></i>';
    for (let i = 0; i < empty; i++) stars += '<i class="far fa-star"></i>';
    
    return stars;
}

// Get sentiment badge HTML
function getSentimentBadge(sentiment) {
    const classes = {
        'Positive': 'badge-positive',
        'Neutral': 'badge-neutral',
        'Negative': 'badge-negative'
    };
    const icons = {
        'Positive': 'fa-smile',
        'Neutral': 'fa-meh',
        'Negative': 'fa-frown'
    };
    return `<span class="badge ${classes[sentiment] || 'badge-neutral'}">
        <i class="fas ${icons[sentiment] || 'fa-meh'}"></i> ${sentiment || 'Unknown'}
    </span>`;
}

// Debounce function
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Loading spinner
function showLoading(container, message = 'Loading...') {
    container.innerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
}

function hideLoading(container) {
    // Remove spinner children
    const spinner = container.querySelector('.spinner-container');
    if (spinner) spinner.remove();
}

// Create chart with defaults
function createChart(ctx, type, data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: getComputedStyle(document.body).getPropertyValue('--text-secondary').trim() || '#475569'
                }
            }
        }
    };
    
    return new Chart(ctx, {
        type: type,
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

// Get CSS variable value
function getCSSVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Theme colors for charts
function getChartColors() {
    const isDark = document.body.classList.contains('dark-mode');
    return {
        primary: getCSSVar('--primary') || '#0C4A6E',
        secondary: getCSSVar('--secondary') || '#14B8A6',
        accent: getCSSVar('--accent') || '#F59E0B',
        success: getCSSVar('--success') || '#22C55E',
        danger: getCSSVar('--danger') || '#EF4444',
        warning: getCSSVar('--warning') || '#F59E0B',
        text: getCSSVar('--text') || '#0F172A',
        textSecondary: getCSSVar('--text-secondary') || '#475569',
        border: getCSSVar('--border') || '#E2E8F0'
    };
}

// Export utilities
window.utils = {
    showToast,
    formatDate,
    formatNumber,
    truncateText,
    getRatingStars,
    getSentimentBadge,
    debounce,
    escapeHtml,
    showLoading,
    hideLoading,
    createChart,
    getCSSVar,
    getChartColors
};