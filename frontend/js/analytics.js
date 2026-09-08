/**
 * Analytics Module
 */

const analytics = {
    charts: {},

    // ============================================================
    // INITIALIZE
    // ============================================================

    async init() {
        const container =
            document.getElementById('dashboardContainer') ||
            document.getElementById('appContent');

        if (!container) {
            console.error('Analytics container not found.');
            return;
        }

        try {
            await this.render(container);
            await this.loadData();
        } catch (error) {
            console.error('Analytics init error:', error);

            if (typeof showToast === 'function') {
                showToast(
                    'Error loading analytics: ' + error.message,
                    'error'
                );
            }
        }
    },

    // ============================================================
    // RENDER PAGE
    // ============================================================

    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2>📊 Data Analytics</h2>
                <p>
                    Comprehensive analysis of
                    Timor-Leste tourism data
                </p>
            </div>

            <!-- QUICK STATS -->
            <div
                class="quick-stats"
                id="quickStats"
            >
                <!-- Rendered by JS -->
            </div>

            <!-- CHARTS -->
            <div class="charts-grid-2">

                <!-- CATEGORY -->
                <div class="chart-container">
                    <div class="chart-header">
                        <span class="chart-title">
                            📊 Category Analysis
                        </span>
                    </div>

                    <div
                        class="chart-wrapper"
                        style="height: 400px;"
                    >
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>

                <!-- MUNICIPALITY -->
                <div class="chart-container">
                    <div class="chart-header">
                        <span class="chart-title">
                            🏛️ Municipality Analysis
                        </span>
                    </div>

                    <div
                        class="chart-wrapper"
                        style="height: 400px;"
                    >
                        <canvas id="municipalityChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- SENTIMENT -->
            <div
                class="card"
                style="margin-top: 24px;"
            >
                <div class="card-header">
                    <span class="card-title">
                        📋 Sentiment Distribution
                    </span>
                </div>

                <div
                    id="sentimentDetails"
                    style="
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 16px;
                        margin-top: 8px;
                    "
                >
                    <!-- Rendered by JS -->
                </div>
            </div>
        `;
    },

    // ============================================================
    // LOAD DATA
    // ============================================================

    async loadData() {
        try {
            console.log('Loading analytics data...');

            const stats = await api.getStatistics();
            const categories = await api.getCategoryAnalysis();
            const municipalities = await api.getMunicipalityAnalysis();
            const sentiment = await api.getSentimentSummaryGlobal();

            console.log('Analytics statistics:', stats);
            console.log('Analytics categories:', categories);
            console.log('Analytics municipalities:', municipalities);
            console.log('Analytics sentiment:', sentiment);

            this.renderQuickStats(stats);
            this.renderCategoryChart(categories);
            this.renderMunicipalityChart(municipalities);
            this.renderSentimentDetails(sentiment);

        } catch (error) {
            console.error(
                'Error loading analytics data:',
                error
            );

            if (typeof showToast === 'function') {
                showToast(
                    'Error loading analytics data',
                    'error'
                );
            }
        }
    },

    // ============================================================
    // QUICK STATS
    // ============================================================

    renderQuickStats(stats) {
        const container =
            document.getElementById('quickStats');

        if (!container) {
            return;
        }

        stats = stats || {};

        const totalDestinations =
            Number(stats.total_destinations) || 0;

        const totalReviews =
            Number(stats.total_reviews) || 0;

        const reviewsPerDestination =
            totalDestinations > 0
                ? (
                    totalReviews / totalDestinations
                ).toFixed(1)
                : '0.0';

        container.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">
                    ${formatNumber(totalDestinations)}
                </div>

                <div class="stat-label">
                    Total Destinations
                </div>
            </div>

            <div class="stat-item">
                <div class="stat-value">
                    ${formatNumber(totalReviews)}
                </div>

                <div class="stat-label">
                    Total Reviews
                </div>
            </div>

            <div class="stat-item">
                <div class="stat-value">
                    ${reviewsPerDestination}
                </div>

                <div class="stat-label">
                    Reviews per Destination
                </div>
            </div>

            <div class="stat-item">
                <div class="stat-value">
                    ${reviewsPerDestination}
                </div>

                <div class="stat-label">
                    Avg Reviews per Place
                </div>
            </div>
        `;
    },

    // ============================================================
    // CATEGORY CHART
    // ============================================================

    renderCategoryChart(categories) {
        const canvas =
            document.getElementById('categoryChart');

        if (!canvas) {
            console.error(
                'categoryChart canvas not found.'
            );
            return;
        }

        const ctx = canvas.getContext('2d');

        if (this.charts.category) {
            this.charts.category.destroy();
            this.charts.category = null;
        }

        if (!Array.isArray(categories)) {
            console.error(
                'Category data is not an array:',
                categories
            );
            return;
        }

        if (categories.length === 0) {
            console.warn(
                'No category data available.'
            );
            return;
        }

        const colorPalette = [
            '#0C4A6E',
            '#14B8A6',
            '#F59E0B',
            '#8B5CF6',
            '#22C55E',
            '#EF4444',
            '#EC4899',
            '#3B82F6'
        ];

        this.charts.category = createChart(
            ctx,
            'bar',
            {
                labels: categories.map(
                    item => item.category || 'Unknown'
                ),

                datasets: [
                    {
                        label: 'Destinations',

                        data: categories.map(
                            item =>
                                Number(item.count) || 0
                        ),

                        backgroundColor: categories.map(
                            (_, index) =>
                                colorPalette[
                                    index % colorPalette.length
                                ] + '80'
                        ),

                        borderColor: categories.map(
                            (_, index) =>
                                colorPalette[
                                    index % colorPalette.length
                                ]
                        ),

                        borderWidth: 2,
                        borderRadius: 4
                    }
                ]
            },
            {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            stepSize: 1,
                            precision: 0
                        },

                        title: {
                            display: true,
                            text: 'Number of Destinations'
                        }
                    }
                }
            }
        );
    },

    // ============================================================
    // MUNICIPALITY CHART
    // ============================================================

    renderMunicipalityChart(municipalities) {
        const canvas =
            document.getElementById(
                'municipalityChart'
            );

        if (!canvas) {
            console.error(
                'municipalityChart canvas not found.'
            );
            return;
        }

        const ctx = canvas.getContext('2d');

        if (this.charts.municipality) {
            this.charts.municipality.destroy();
            this.charts.municipality = null;
        }

        /*
         * IMPORTANT:
         *
         * Chart.js 3/4 does NOT support
         * the old "horizontalBar" chart type.
         *
         * We use:
         *
         * type: "bar"
         *
         * together with:
         *
         * indexAxis: "y"
         *
         * to create a horizontal bar chart.
         */

        if (!Array.isArray(municipalities)) {
            console.error(
                'Municipality data is not an array:',
                municipalities
            );
            return;
        }

        if (municipalities.length === 0) {
            console.warn(
                'No municipality data available.'
            );
            return;
        }

        console.log(
            'Rendering municipality chart with:',
            municipalities
        );

        const colorPalette = [
            '#14B8A6',
            '#0C4A6E',
            '#F59E0B',
            '#8B5CF6',
            '#22C55E',
            '#EF4444',
            '#EC4899',
            '#3B82F6'
        ];

        this.charts.municipality = createChart(
            ctx,
            'bar',
            {
                labels: municipalities.map(
                    item =>
                        item.municipality || 'Unknown'
                ),

                datasets: [
                    {
                        label: 'Destinations',

                        data: municipalities.map(
                            item =>
                                Number(item.count) || 0
                        ),

                        backgroundColor:
                            municipalities.map(
                                (_, index) =>
                                    colorPalette[
                                        index % colorPalette.length
                                    ] + '80'
                            ),

                        borderColor:
                            municipalities.map(
                                (_, index) =>
                                    colorPalette[
                                        index % colorPalette.length
                                    ]
                            ),

                        borderWidth: 2,
                        borderRadius: 4
                    }
                ]
            },
            {
                /*
                 * Chart.js 3/4:
                 * horizontal bar chart
                 */
                indexAxis: 'y',

                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    x: {
                        beginAtZero: true,

                        ticks: {
                            stepSize: 1,
                            precision: 0
                        },

                        title: {
                            display: true,
                            text: 'Number of Destinations'
                        }
                    },

                    y: {
                        title: {
                            display: true,
                            text: 'Municipality'
                        }
                    }
                }
            }
        );
    },

    // ============================================================
    // SENTIMENT DETAILS
    // ============================================================

    renderSentimentDetails(sentiment) {
        const container =
            document.getElementById(
                'sentimentDetails'
            );

        if (!container || !sentiment) {
            return;
        }

        const positive =
            Number(sentiment.positive) || 0;

        const neutral =
            Number(sentiment.neutral) || 0;

        const negative =
            Number(sentiment.negative) || 0;

        const total =
            Number(sentiment.total) || 0;

        const averageScore =
            Number(sentiment.average_score) || 0;

        const positiveReviews =
            total > 0
                ? Math.round(
                    positive / 100 * total
                )
                : 0;

        const neutralReviews =
            total > 0
                ? Math.round(
                    neutral / 100 * total
                )
                : 0;

        const negativeReviews =
            total > 0
                ? Math.round(
                    negative / 100 * total
                )
                : 0;

        container.innerHTML = `
            <!-- POSITIVE -->
            <div
                style="
                    background: rgba(
                        34,
                        197,
                        94,
                        0.05
                    );
                    padding: 16px;
                    border-radius: var(--radius-sm);
                    border-left:
                        4px solid var(--success);
                "
            >
                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color: var(--success);
                    "
                >
                    ${positive}%
                </div>

                <div
                    style="
                        color: var(--text-secondary);
                    "
                >
                    😊 Positive Reviews
                </div>

                <div
                    style="
                        font-size: 13px;
                        color: var(--text-secondary);
                        margin-top: 4px;
                    "
                >
                    ${formatNumber(positiveReviews)}
                    reviews
                </div>
            </div>

            <!-- NEUTRAL -->
            <div
                style="
                    background: rgba(
                        245,
                        158,
                        11,
                        0.05
                    );
                    padding: 16px;
                    border-radius: var(--radius-sm);
                    border-left:
                        4px solid var(--warning);
                "
            >
                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color: var(--warning);
                    "
                >
                    ${neutral}%
                </div>

                <div
                    style="
                        color: var(--text-secondary);
                    "
                >
                    😐 Neutral Reviews
                </div>

                <div
                    style="
                        font-size: 13px;
                        color: var(--text-secondary);
                        margin-top: 4px;
                    "
                >
                    ${formatNumber(neutralReviews)}
                    reviews
                </div>
            </div>

            <!-- NEGATIVE -->
            <div
                style="
                    background: rgba(
                        239,
                        68,
                        68,
                        0.05
                    );
                    padding: 16px;
                    border-radius: var(--radius-sm);
                    border-left:
                        4px solid var(--danger);
                "
            >
                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color: var(--danger);
                    "
                >
                    ${negative}%
                </div>

                <div
                    style="
                        color: var(--text-secondary);
                    "
                >
                    😞 Negative Reviews
                </div>

                <div
                    style="
                        font-size: 13px;
                        color: var(--text-secondary);
                        margin-top: 4px;
                    "
                >
                    ${formatNumber(negativeReviews)}
                    reviews
                </div>
            </div>

            <!-- TOTAL -->
            <div
                style="
                    background: var(--surface-hover);
                    padding: 16px;
                    border-radius: var(--radius-sm);
                "
            >
                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color: var(--text);
                    "
                >
                    ${formatNumber(total)}
                </div>

                <div
                    style="
                        color: var(--text-secondary);
                    "
                >
                    📝 Total Reviews
                </div>

                <div
                    style="
                        font-size: 13px;
                        color: var(--text-secondary);
                        margin-top: 4px;
                    "
                >
                    Avg Score:
                    ${
                        averageScore
                            ? averageScore.toFixed(3)
                            : '0.000'
                    }
                </div>
            </div>
        `;
    }
};


// ============================================================
// LOAD ANALYTICS
// ============================================================

function loadAnalytics() {
    const container =
        document.getElementById(
            'dashboardContainer'
        ) ||
        document.getElementById(
            'appContent'
        );

    if (!container) {
        console.error(
            'Analytics page container not found.'
        );
        return;
    }

    analytics.init();
}