/**
 * API Client for Timor-Leste Tourism Intelligence Platform
 */

const API_BASE = '/api';

class APIClient {

    constructor() {
        this.baseUrl = API_BASE;
    }

    async request(endpoint, options = {}) {

        const url = `${this.baseUrl}${endpoint}`;

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {

            const response = await fetch(url, config);

            if (!response.ok) {

                const errorData = await response
                    .json()
                    .catch(() => ({}));

                throw new Error(
                    errorData.detail ||
                    `HTTP ${response.status}: ${response.statusText}`
                );
            }

            const contentType =
                response.headers.get('content-type');

            if (
                contentType &&
                contentType.includes('application/json')
            ) {
                return await response.json();
            }

            return await response.text();

        } catch (error) {

            console.error(
                `API Error [${endpoint}]:`,
                error
            );

            throw error;
        }
    }


    // ========================================
    // DASHBOARD
    // ========================================

    async getDashboardSummary() {

        return this.request(
            '/analytics/dashboard/summary'
        );
    }

    async getDashboardTrends(days = 30) {

        return this.request(
            `/analytics/dashboard/trends?days=${days}`
        );
    }

    async getTopDestinations(limit = 6) {

        return this.request(
            `/analytics/dashboard/top-destinations?limit=${limit}`
        );
    }

    async getSentimentSummary() {

        return this.request(
            '/analytics/dashboard/sentiment-summary'
        );
    }


    // ========================================
    // DESTINATIONS
    // ========================================

    async getDestinations(params = {}) {

        const query =
            new URLSearchParams(params).toString();

        const endpoint =
            query
                ? `/destinations?${query}`
                : '/destinations';

        return this.request(endpoint);
    }

    async getDestination(id) {

        return this.request(
            `/destinations/${id}`
        );
    }

    async getCategories() {

        return this.request(
            '/destinations/categories/all'
        );
    }

    async getMunicipalities() {

        return this.request(
            '/destinations/municipalities/all'
        );
    }


    // ========================================
    // REVIEWS
    // ========================================

    async getReviews(params = {}) {

        const query =
            new URLSearchParams(params).toString();

        const endpoint =
            query
                ? `/reviews?${query}`
                : '/reviews';

        return this.request(endpoint);
    }

    async getReview(id) {

        return this.request(
            `/reviews/${id}`
        );
    }

    async createReview(data) {

        return this.request(
            '/reviews',
            {
                method: 'POST',
                body: JSON.stringify(data)
            }
        );
    }

    async getDestinationSentiment(destinationId) {

        return this.request(
            `/reviews/destination/${destinationId}/sentiment-summary`
        );
    }


    // ========================================
    // RECOMMENDATIONS
    // ========================================

    async getRecommendations(params = {}) {

        const query =
            new URLSearchParams(params).toString();

        const endpoint =
            query
                ? `/recommendations?${query}`
                : '/recommendations';

        return this.request(endpoint);
    }

    async getUserTypes() {

        return this.request(
            '/recommendations/user-types'
        );
    }

    async getBudgetOptions() {

        return this.request(
            '/recommendations/budget-options'
        );
    }


    // ========================================
    // ANALYTICS
    // ========================================

    async getStatistics() {

        return this.request(
            '/analytics/statistics'
        );
    }

    async getCategoryAnalysis() {

        return this.request(
            '/analytics/categories'
        );
    }

    async getMunicipalityAnalysis() {

        return this.request(
            '/analytics/municipalities'
        );
    }


    // ========================================
    // DATA MINING
    // ========================================

    async analyzeSentiment(text) {

        return this.request(
            '/mining/sentiment',
            {
                method: 'POST',
                body: JSON.stringify({
                    text: text
                })
            }
        );
    }

    async getSentimentSummaryGlobal() {

        return this.request(
            '/mining/sentiment-summary'
        );
    }

    async getSentimentKeywords(limit = 10) {

        return this.request(
            `/mining/sentiment-keywords?limit=${limit}`
        );
    }

    async runClustering(nClusters = 4) {

        return this.request(
            `/mining/clustering?n_clusters=${nClusters}`,
            {
                method: 'POST'
            }
        );
    }

    async getClusters() {

        return this.request(
            '/mining/clusters'
        );
    }

    async getClusterDetail(clusterId) {

        return this.request(
            `/mining/clusters/${clusterId}`
        );
    }

    async getClusteringStatus() {

        return this.request(
            '/mining/clustering/status'
        );
    }

    async getClusteringEvaluation(
        kMin = 2,
        kMax = 6
    ) {

        return this.request(
            `/mining/clustering/evaluation?k_min=${kMin}&k_max=${kMax}`
        );
    }

    async getClusteringStatistics() {

        return this.request(
            '/mining/clustering/statistics'
        );
    }


    // ========================================
    // REAL-TIME
    // ========================================

    async getRealtimeStatus() {

        return this.request(
            '/realtime/status'
        );
    }

    async triggerCollection() {

        return this.request(
            '/realtime/collect',
            {
                method: 'POST'
            }
        );
    }

    async getCollectionLogs(
        limit = 20,
        status = null
    ) {

        const params = new URLSearchParams();

        params.set(
            'limit',
            String(limit)
        );

        if (status) {

            params.set(
                'status',
                status
            );
        }

        return this.request(
            `/realtime/logs?${params.toString()}`
        );
    }

    async getCollectionSettings() {

        return this.request(
            '/realtime/settings'
        );
    }

    async updatePollingInterval(
        intervalSeconds
    ) {

        return this.request(
            `/realtime/settings/interval?interval_seconds=${intervalSeconds}`,
            {
                method: 'POST'
            }
        );
    }
}


// ========================================
// CREATE API INSTANCE
// ========================================

const api = new APIClient();


// ========================================
// EXPORT FOR USE IN OTHER JS FILES
// ========================================

window.api = api;