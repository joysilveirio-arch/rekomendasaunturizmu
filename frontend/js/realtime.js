/**
 * Real-Time Monitor Module
 */

const realtime = {
    status: null,
    logs: [],
    settings: null,
    intervalId: null,
    
    async init() {
        const container = document.getElementById('dashboardContainer');
        if (!container) return;
        
        try {
            await this.render(container);
            await this.loadData();
            
            // Auto-refresh every 10 seconds
            this.intervalId = setInterval(() => {
                this.loadData();
            }, 10000);
        } catch (error) {
            console.error('Real-time monitor init error:', error);
            showToast('Error loading real-time data: ' + error.message, 'error');
        }
    },
    
    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2>⚡ Real-Time Monitor</h2>
                <p>Monitor data collection status and system health</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
                <div class="card">
                    <h4 style="font-weight: 600; margin-bottom: 12px;">🔄 System Status</h4>
                    <div id="systemStatus">
                        <!-- Rendered by JS -->
                    </div>
                </div>
                <div class="card">
                    <h4 style="font-weight: 600; margin-bottom: 12px;">⚙️ Collection Settings</h4>
                    <div id="collectionSettings">
                        <!-- Rendered by JS -->
                    </div>
                </div>
            </div>
            
            <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
                <button class="btn btn-primary" id="manualCollectBtn">
                    <i class="fas fa-cloud-upload-alt"></i> Manual Collection
                </button>
                <button class="btn btn-outline" id="refreshLogsBtn">
                    <i class="fas fa-refresh"></i> Refresh Logs
                </button>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📋 Activity Log</span>
                    <span style="font-size: 13px; color: var(--text-secondary);" id="logCount">0 entries</span>
                </div>
                <div id="activityLog" style="max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 13px; background: var(--background); border-radius: var(--radius-sm); padding: 12px;">
                    <!-- Rendered by JS -->
                </div>
            </div>
        `;
        
        // Event listeners
        document.getElementById('manualCollectBtn').addEventListener('click', () => {
            this.manualCollect();
        });
        
        document.getElementById('refreshLogsBtn').addEventListener('click', () => {
            this.loadData();
            showToast('Logs refreshed', 'info');
        });
    },
    
    async loadData() {
        try {
            const [status, logs, settings] = await Promise.all([
                api.getRealtimeStatus(),
                api.getCollectionLogs(20),
                api.getCollectionSettings()
            ]);
            
            this.status = status;
            this.logs = logs || [];
            this.settings = settings;
            
            this.renderStatus();
            this.renderSettings();
            this.renderLogs();
            
        } catch (error) {
            console.error('Error loading real-time data:', error);
        }
    },
    
    renderStatus() {
        const container = document.getElementById('systemStatus');
        if (!container || !this.status) return;
        
        const statusItems = [
            { label: 'API Status', value: this.status.api_status || 'offline', icon: 'fa-plug' },
            { label: 'Database', value: this.status.database_status || 'disconnected', icon: 'fa-database' },
            { label: 'Pipeline', value: this.status.pipeline_status || 'idle', icon: 'fa-cogs' },
            { label: 'Last Update', value: this.status.last_update ? formatDate(this.status.last_update) : 'Never', icon: 'fa-clock' },
            { label: 'Next Update', value: this.status.next_update ? formatDate(this.status.next_update) : 'Unknown', icon: 'fa-calendar-plus' },
            { label: 'Records', value: formatNumber(this.status.records_collected || 0), icon: 'fa-file-alt' }
        ];
        
        container.innerHTML = statusItems.map(item => `
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">
                    <i class="fas ${item.icon}" style="width: 20px;"></i> ${item.label}
                </span>
                <span style="font-weight: 500; ${this.getStatusColor(item.value)}">
                    ${item.value}
                </span>
            </div>
        `).join('');
    },
    
    getStatusColor(value) {
        const lower = value.toLowerCase();
        if (lower.includes('online') || lower.includes('connected') || lower.includes('success')) {
            return 'color: var(--success);';
        } else if (lower.includes('offline') || lower.includes('disconnected') || lower.includes('failed')) {
            return 'color: var(--danger);';
        } else if (lower.includes('running')) {
            return 'color: var(--warning);';
        }
        return '';
    },
    
    renderSettings() {
        const container = document.getElementById('collectionSettings');
        if (!container || !this.settings) return;
        
        container.innerHTML = `
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Data Source</span>
                <span style="font-weight: 500;">${this.settings.data_source || 'mock'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Polling Interval</span>
                <span style="font-weight: 500;">${this.settings.polling_interval || 300}s</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Mock Data</span>
                <span style="font-weight: 500;">${this.settings.mock_data_enabled ? '✅ Enabled' : '❌ Disabled'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                <span style="color: var(--text-secondary);">API Configured</span>
                <span style="font-weight: 500;">${this.settings.api_configured ? '✅ Yes' : '❌ No'}</span>
            </div>
        `;
    },
    
    renderLogs() {
        const container = document.getElementById('activityLog');
        if (!container) return;
        
        const countEl = document.getElementById('logCount');
        if (countEl) countEl.textContent = `${this.logs.length} entries`;
        
        if (!this.logs || this.logs.length === 0) {
            container.innerHTML = `
                <div style="color: var(--text-muted); text-align: center; padding: 20px;">
                    No activity logs found
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.logs.map(log => {
            const time = log.created_at ? formatDate(log.created_at) : 'N/A';
            const statusIcon = log.status === 'success' ? '✅' : log.status === 'failed' ? '❌' : '⏳';
            const statusColor = log.status === 'success' ? 'var(--success)' : log.status === 'failed' ? 'var(--danger)' : 'var(--warning)';
            
            return `
                <div style="display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 12px;">
                    <span style="color: var(--text-muted); min-width: 140px;">${time}</span>
                    <span style="color: ${statusColor};">${statusIcon}</span>
                    <span style="flex: 1;">${escapeHtml(log.message || 'No message')}</span>
                    <span style="color: var(--text-muted); min-width: 60px; text-align: right;">${log.records_collected || 0} records</span>
                </div>
            `;
        }).join('');
        
        // Auto-scroll to bottom
        container.scrollTop = container.scrollHeight;
    },
    
    async manualCollect() {
        const btn = document.getElementById('manualCollectBtn');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Collecting...';
        btn.disabled = true;
        
        try {
            const result = await api.triggerCollection();
            showToast(`Data collection completed: ${result.records_collected} records`, 'success');
            await this.loadData();
        } catch (error) {
            console.error('Manual collection error:', error);
            showToast('Error during data collection: ' + error.message, 'error');
        } finally {
            btn.innerHTML = '<i class="fas fa-cloud-upload-alt"></i> Manual Collection';
            btn.disabled = false;
        }
    },
    
    destroy() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
};

// Load realtime function for navigation
function loadRealtime() {
    const container = document.getElementById('dashboardContainer') || document.getElementById('appContent');
    if (container) {
        // Clean up previous instance
        if (window._realtimeInstance) {
            window._realtimeInstance.destroy();
        }
        window._realtimeInstance = realtime;
        realtime.init();
    }
}