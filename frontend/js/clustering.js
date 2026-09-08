/**
 * Clustering Module
 */

const clustering = {
    clusters: [],
    status: null,
    isRunning: false,
    
    async init() {
        const container = document.getElementById('dashboardContainer');
        if (!container) return;
        
        try {
            await this.render(container);
            await this.loadStatus();
            await this.loadClusters();
        } catch (error) {
            console.error('Clustering init error:', error);
            showToast('Error loading clustering data: ' + error.message, 'error');
        }
    },
    
    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2>📊 K-Means Clustering</h2>
                <p>Discover hidden patterns and group destinations by similar characteristics</p>
            </div>
            
            <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px;">
                <div class="card" style="flex: 1; min-width: 200px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 32px;">📊</div>
                        <div>
                            <div style="font-size: 24px; font-weight: 700;" id="clusterCount">-</div>
                            <div style="color: var(--text-secondary); font-size: 14px;">Active Clusters</div>
                        </div>
                    </div>
                </div>
                <div class="card" style="flex: 1; min-width: 200px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 32px;">📈</div>
                        <div>
                            <div style="font-size: 24px; font-weight: 700;" id="silhouetteScore">-</div>
                            <div style="color: var(--text-secondary); font-size: 14px;">Silhouette Score</div>
                        </div>
                    </div>
                </div>
                <div class="card" style="flex: 1; min-width: 200px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 32px;">🏷️</div>
                        <div>
                            <div style="font-size: 24px; font-weight: 700;" id="statusLabel">-</div>
                            <div style="color: var(--text-secondary); font-size: 14px;">Status</div>
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <button class="btn btn-primary" id="runClusteringBtn">
                        <i class="fas fa-play"></i> Run Clustering
                    </button>
                    <div class="form-group" style="margin-bottom: 0;">
                        <select id="nClustersSelect" style="padding: 8px 12px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--background);">
                            <option value="3">3 Clusters</option>
                            <option value="4" selected>4 Clusters</option>
                            <option value="5">5 Clusters</option>
                            <option value="6">6 Clusters</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div id="clusterResults">
                <div class="empty-state">
                    <i class="fas fa-layer-group" style="font-size: 48px; color: var(--text-muted);"></i>
                    <h3>No Clusters Found</h3>
                    <p>Run the clustering algorithm to discover destination groups.</p>
                    <button class="btn btn-primary" onclick="clustering.runClustering()" style="margin-top: 16px;">
                        <i class="fas fa-play"></i> Run Clustering Now
                    </button>
                </div>
            </div>
        `;
        
        // Event listeners
        document.getElementById('runClusteringBtn').addEventListener('click', () => {
            this.runClustering();
        });
    },
    
    async loadStatus() {
        try {
            this.status = await api.getClusteringStatus();
            
            document.getElementById('statusLabel').textContent = this.status.status === 'completed' ? '✅ Completed' : '⏳ Not Run';
            document.getElementById('clusterCount').textContent = this.status.n_clusters || 0;
            document.getElementById('silhouetteScore').textContent = this.status.silhouette_score !== null ? this.status.silhouette_score.toFixed(3) : 'N/A';
            
        } catch (error) {
            console.error('Error loading status:', error);
        }
    },
    
    async loadClusters() {
        try {
            this.clusters = await api.getClusters();
            
            if (this.clusters && this.clusters.length > 0) {
                this.renderClusters();
            }
        } catch (error) {
            console.error('Error loading clusters:', error);
        }
    },
    
    renderClusters() {
        const container = document.getElementById('clusterResults');
        
        if (!this.clusters || this.clusters.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-layer-group" style="font-size: 48px; color: var(--text-muted);"></i>
                    <h3>No Clusters Found</h3>
                    <p>Run the clustering algorithm to discover destination groups.</p>
                </div>
            `;
            return;
        }
        
        const colors = ['#0C4A6E', '#14B8A6', '#F59E0B', '#8B5CF6', '#22C55E', '#EF4444'];
        
        container.innerHTML = this.clusters.map((cluster, index) => `
            <div class="card" style="margin-bottom: 16px; border-left: 4px solid ${colors[index % colors.length]};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <h3 style="font-size: 18px; font-weight: 600;">${escapeHtml(cluster.cluster_name || `Cluster ${cluster.cluster_id}`)}</h3>
                        <p style="color: var(--text-secondary); font-size: 14px;">
                            ${cluster.count || 0} destinations • Avg Rating: ${cluster.avg_rating || 0} • Avg Popularity: ${cluster.avg_popularity || 0}
                        </p>
                    </div>
                    <div>
                        <span class="badge badge-primary">Cluster ${cluster.cluster_id}</span>
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">
                    ${(cluster.destinations || []).map(d => `
                        <span class="badge badge-neutral" style="cursor: pointer;" onclick="destinations.viewDestination(${d.id})">
                            ${escapeHtml(d.name)}
                        </span>
                    `).join('')}
                </div>
            </div>
        `).join('');
    },
    
    async runClustering() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        const btn = document.getElementById('runClusteringBtn');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        btn.disabled = true;
        
        const container = document.getElementById('clusterResults');
        showLoading(container, 'Running K-Means clustering...');
        
        try {
            const nClusters = parseInt(document.getElementById('nClustersSelect').value) || 4;
            const result = await api.runClustering(nClusters);
            
            showToast(`Clustering completed with ${nClusters} clusters!`, 'success');
            
            // Reload data
            await this.loadStatus();
            await this.loadClusters();
            
        } catch (error) {
            console.error('Error running clustering:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: var(--danger);"></i>
                    <h3>Clustering Failed</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="clustering.runClustering()" style="margin-top: 16px;">
                        <i class="fas fa-redo"></i> Try Again
                    </button>
                </div>
            `;
            showToast('Error running clustering: ' + error.message, 'error');
        } finally {
            this.isRunning = false;
            btn.innerHTML = '<i class="fas fa-play"></i> Run Clustering';
            btn.disabled = false;
        }
    }
};

// Load clustering function for navigation
function loadClustering() {
    const container = document.getElementById('dashboardContainer') || document.getElementById('appContent');
    if (container) {
        clustering.init();
    }
}