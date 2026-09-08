/**
 * Dashboard Module
 *
 * Responsibilities:
 * - Render dashboard layout
 * - Load dashboard statistics
 * - Render KPI cards
 * - Render tourism trend chart
 * - Render sentiment chart
 * - Render top destinations
 * - Render rating distribution
 * - Load ALL destinations with pagination
 * - Render ALL valid destinations on Leaflet map
 * - Load K-Means clustering evaluation
 * - Render clustering evaluation
 * - Render cluster distribution
 * - Render cluster interpretation
 * - Prevent duplicate dashboard initialization
 */

const dashboard = {
    charts: {},
    map: null,
    mapMarkers: [],
    initPromise: null,

    /**
     * Initialize dashboard.
     */
    async init() {
        const container = document.getElementById('dashboardContainer');

        if (!container) {
            return;
        }

        if (this.initPromise) {
            console.log(
                'Dashboard initialization already running. Reusing existing request.'
            );

            return this.initPromise;
        }

        if (document.getElementById('tourismMap')) {
            console.log(
                'Dashboard already initialized. Skipping duplicate initialization.'
            );

            return;
        }

        this.initPromise = (async () => {
            try {
                console.log('Dashboard initialization started.');

                await this.render(container);
                await this.loadData();

                console.log('Dashboard initialization completed.');
            } catch (error) {
                console.error(
                    'Dashboard initialization error:',
                    error
                );

                if (typeof showToast === 'function') {
                    showToast(
                        'Error loading dashboard: ' + error.message,
                        'error'
                    );
                }
            } finally {
                this.initPromise = null;
            }
        })();

        return this.initPromise;
    },

    /**
     * Render dashboard HTML.
     */
    async render(container) {
        container.innerHTML = `
            <!-- DASHBOARD WELCOME -->
            <div class="dashboard-welcome">
                <h1>
                    <span class="greeting">
                        Good Morning 👋
                    </span>
                </h1>

                <h1>
                    Tourism Intelligence Dashboard
                </h1>

                <p>
                    Monitor tourism trends and discover
                    insights from Timor-Leste tourism data.
                </p>
            </div>


            <!-- KPI CARDS -->
            <div
                class="kpi-grid"
                id="kpiGrid"
            >
            </div>


            <!-- TOURISM MAP -->
            <div class="chart-container tourism-map-container">
                <div class="chart-header">
                    <span class="chart-title">
                        <i class="fas fa-map-marked-alt"></i>
                        Timor-Leste Tourism Map
                    </span>

                    <span
                        id="mapDestinationCount"
                        class="map-destination-count"
                    >
                        Loading destinations...
                    </span>
                </div>

                <div
                    id="tourismMap"
                    class="tourism-map"
                    style="
                        height: 500px;
                        width: 100%;
                    "
                ></div>
            </div>


            <!-- TOURISM TREND + SENTIMENT -->
            <div class="charts-grid">

                <!-- TOURISM TREND -->
                <div class="chart-container">
                    <div class="chart-header">
                        <span class="chart-title">
                            📈 Tourism Trend
                        </span>
                    </div>

                    <div
                        class="chart-wrapper"
                        style="
                            position: relative;
                            height: 350px;
                        "
                    >
                        <canvas id="trendChart"></canvas>
                    </div>
                </div>


                <!-- SENTIMENT -->
                <div class="chart-container">
                    <div class="chart-header">
                        <span class="chart-title">
                            📊 Sentiment Distribution
                        </span>
                    </div>

                    <div
                        class="chart-wrapper"
                        style="
                            position: relative;
                            height: 350px;
                        "
                    >
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>

            </div>


            <!-- TOP DESTINATIONS + RATING -->
            <div class="charts-grid-2">

                <!-- TOP DESTINATIONS -->
                <div class="chart-container">
                    <div class="chart-header">
                        <span class="chart-title">
                            🏆 Top Destinations
                        </span>
                    </div>

                    <div
                        class="top-destinations-list"
                        id="topDestinations"
                    >
                    </div>
                </div>


                <!-- RATING DISTRIBUTION -->
                <div class="chart-container">
                    <div class="chart-header">
                        <span class="chart-title">
                            📊 Rating Distribution
                        </span>
                    </div>

                    <div
                        class="chart-wrapper"
                        style="
                            position: relative;
                            height: 350px;
                        "
                    >
                        <canvas id="ratingChart"></canvas>
                    </div>
                </div>

            </div>


            <!-- ========================================= -->
            <!-- DATA MINING / K-MEANS EVALUATION -->
            <!-- ========================================= -->

            <div
                class="chart-container"
                id="clusteringEvaluationContainer"
                style="margin-top: 24px;"
            >

                <div class="chart-header">
                    <span class="chart-title">
                        <i class="fas fa-project-diagram"></i>
                        K-Means Clustering Evaluation
                    </span>

                    <span
                        id="clusteringStatusBadge"
                        class="map-destination-count"
                    >
                        Loading...
                    </span>
                </div>


                <!-- CLUSTERING KPI -->
                <div
                    id="clusteringKpiGrid"
                    class="kpi-grid"
                    style="margin-top: 16px;"
                >
                </div>


                <!-- EVALUATION CHART -->
                <div
                    class="chart-wrapper"
                    style="
                        position: relative;
                        height: 380px;
                        margin-top: 20px;
                    "
                >
                    <canvas id="clusteringEvaluationChart"></canvas>
                </div>

            </div>


            <!-- ========================================= -->
            <!-- CLUSTER DISTRIBUTION -->
            <!-- ========================================= -->

            <div
                class="charts-grid"
                style="margin-top: 24px;"
            >

                <!-- CLUSTER DISTRIBUTION -->
                <div class="chart-container">

                    <div class="chart-header">
                        <span class="chart-title">
                            <i class="fas fa-layer-group"></i>
                            Cluster Distribution
                        </span>
                    </div>

                    <div
                        class="chart-wrapper"
                        style="
                            position: relative;
                            height: 350px;
                        "
                    >
                        <canvas id="clusterDistributionChart"></canvas>
                    </div>

                </div>


                <!-- CLUSTER INTERPRETATION -->
                <div class="chart-container">

                    <div class="chart-header">
                        <span class="chart-title">
                            <i class="fas fa-chart-bar"></i>
                            Cluster Interpretation
                        </span>
                    </div>

                    <div
                        id="clusterInterpretation"
                        style="
                            max-height: 350px;
                            overflow-y: auto;
                            padding: 10px;
                        "
                    >
                        <p class="empty-state">
                            Loading cluster information...
                        </p>
                    </div>

                </div>

            </div>
        `;
    },


    /**
     * Load dashboard data.
     */
    async loadData() {
        try {
            console.log('Loading dashboard API data...');

            /*
             * Normal dashboard APIs.
             *
             * Clustering APIs are loaded separately so that
             * a clustering API problem does not break the
             * normal dashboard.
             */
            const [
                summary,
                trendData,
                sentimentData,
                topDestinations,
                stats
            ] = await Promise.all([
                api.getDashboardSummary(),
                api.getDashboardTrends(30),
                api.getSentimentSummary(),
                api.getTopDestinations(5),
                api.getStatistics()
            ]);


            /*
             * Render KPI cards.
             */
            this.renderKPIs(summary || {});


            /*
             * Render tourism trend.
             */
            this.renderTrendChart(trendData || {});


            /*
             * Render sentiment.
             */
            this.renderSentimentChart(sentimentData || {});


            /*
             * Render top destinations.
             */
            this.renderTopDestinations(
                topDestinations || []
            );


            /*
             * Render rating distribution.
             */
            this.renderRatingChart(
                stats && stats.rating_distribution
                    ? stats.rating_distribution
                    : []
            );


            /*
             * Load ALL destinations.
             */
            const allDestinations =
                await this.loadAllDestinations();

            console.log(
                `All destinations loaded: ${allDestinations.length}`
            );


            /*
             * Render all destinations on map.
             */
            this.renderTourismMap(
                allDestinations
            );


            /*
             * Load clustering evaluation.
             *
             * This is independent from the map and
             * normal dashboard charts.
             */
            await this.loadClusteringData();

        } catch (error) {
            console.error(
                'Dashboard load error:',
                error
            );

            if (typeof showToast === 'function') {
                showToast(
                    'Error loading dashboard data: ' +
                    error.message,
                    'error'
                );
            }
        }
    },


    /**
     * Load ALL destinations using API pagination.
     */
    async loadAllDestinations() {
        const allDestinations = [];

        const limit = 100;
        let skip = 0;
        let total = null;

        while (true) {
            console.log(
                `Loading destinations: skip=${skip}, limit=${limit}`
            );

            const response =
                await api.getDestinations({
                    skip: skip,
                    limit: limit
                });


            /*
             * Normalize response.
             */
            let items = [];

            if (Array.isArray(response)) {
                items = response;
            } else if (
                response &&
                Array.isArray(response.items)
            ) {
                items = response.items;
            } else if (
                response &&
                Array.isArray(response.data)
            ) {
                items = response.data;
            } else if (
                response &&
                Array.isArray(response.destinations)
            ) {
                items = response.destinations;
            }


            /*
             * Read total.
             */
            if (
                response &&
                typeof response.total === 'number'
            ) {
                total = response.total;
            }


            /*
             * Stop if no data.
             */
            if (items.length === 0) {
                console.log(
                    'No more destinations returned by API.'
                );

                break;
            }


            /*
             * Add current page.
             */
            allDestinations.push(...items);

            console.log(
                `Loaded ${items.length} destinations. ` +
                `Total loaded: ${allDestinations.length}` +
                (
                    total !== null
                        ? ` / ${total}`
                        : ''
                )
            );


            /*
             * Move to next page.
             */
            skip += items.length;


            /*
             * Stop when total reached.
             */
            if (
                total !== null &&
                allDestinations.length >= total
            ) {
                break;
            }


            /*
             * Stop if final page.
             */
            if (items.length < limit) {
                break;
            }
        }


        /*
         * Remove duplicates.
         */
        const uniqueDestinations = [];
        const seen = new Set();

        for (const destination of allDestinations) {

            const key =
                destination.id ??
                destination.place_id ??
                (
                    `${destination.name || 'unknown'}-` +
                    `${destination.latitude}-` +
                    `${destination.longitude}`
                );

            if (!seen.has(key)) {
                seen.add(key);

                uniqueDestinations.push(
                    destination
                );
            }
        }


        console.log(
            `All destinations loaded: ${uniqueDestinations.length}`
        );

        return uniqueDestinations;
    },


    /**
     * Render KPI cards.
     */
    renderKPIs(summary) {
        const grid =
            document.getElementById('kpiGrid');

        if (!grid) {
            return;
        }


        const kpis =
            summary.kpis || [
                {
                    label: 'Total Destinations',
                    value:
                        summary.total_destinations || 0,
                    icon: 'fa-map-marker-alt',
                    trend: 0
                },
                {
                    label: 'Total Reviews',
                    value:
                        summary.total_reviews || 0,
                    icon: 'fa-comments',
                    trend: 0
                },
                {
                    label: 'Average Rating',
                    value:
                        summary.average_rating || '0.0',
                    icon: 'fa-star',
                    trend: 0
                },
                {
                    label: 'Positive Sentiment',
                    value:
                        (
                            summary.positive_sentiment || 0
                        ) + '%',
                    icon: 'fa-smile',
                    trend: 0
                },
                {
                    label: 'Active Clusters',
                    value:
                        summary.active_clusters || 0,
                    icon: 'fa-layer-group',
                    trend: 0
                },
                {
                    label: 'Last Update',
                    value:
                        summary.last_update
                            ? formatDate(
                                summary.last_update
                            )
                            : 'N/A',
                    icon: 'fa-clock',
                    trend: 0
                }
            ];


        const iconColors = [
            'blue',
            'green',
            'yellow',
            'purple',
            'red',
            'teal'
        ];


        grid.innerHTML =
            kpis.map(
                (kpi, index) => `
                    <div class="kpi-card">

                        <div
                            class="kpi-icon ${
                                iconColors[
                                    index %
                                    iconColors.length
                                ]
                            }"
                        >
                            <i
                                class="fas ${kpi.icon}"
                            ></i>
                        </div>

                        <div class="kpi-value">
                            ${kpi.value}
                        </div>

                        <div class="kpi-label">
                            ${kpi.label}
                        </div>

                        ${
                            kpi.trend !== undefined
                                ? `
                                    <div
                                        class="kpi-trend ${
                                            kpi.trend > 0
                                                ? 'up'
                                                : kpi.trend < 0
                                                    ? 'down'
                                                    : 'neutral'
                                        }"
                                    >
                                        <i
                                            class="fas ${
                                                kpi.trend > 0
                                                    ? 'fa-arrow-up'
                                                    : kpi.trend < 0
                                                        ? 'fa-arrow-down'
                                                        : 'fa-minus'
                                            }"
                                        ></i>

                                        ${Math.abs(
                                            kpi.trend
                                        )}%
                                    </div>
                                `
                                : ''
                        }

                    </div>
                `
            ).join('');
    },


    /**
     * Render tourism trend chart.
     */
    renderTrendChart(data) {
        const canvas =
            document.getElementById(
                'trendChart'
            );

        if (!canvas) {
            return;
        }

        const ctx =
            canvas.getContext('2d');


        if (this.charts.trend) {
            this.charts.trend.destroy();
            this.charts.trend = null;
        }


        const colors =
            getChartColors();


        this.charts.trend =
            createChart(
                ctx,
                'line',
                {
                    labels:
                        data.labels || [],

                    datasets:
                        data.datasets ||
                        [
                            {
                                label:
                                    'Tourist Activity',

                                data: [],

                                borderColor:
                                    colors.primary,

                                backgroundColor:
                                    colors.primary +
                                    '20',

                                fill: true,

                                tension: 0.4
                            }
                        ]
                },
                {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero: true,

                            grid: {
                                color:
                                    getCSSVar(
                                        '--border'
                                    ) ||
                                    '#E2E8F0'
                            }
                        },

                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            );
    },


    /**
     * Render sentiment chart.
     */
    renderSentimentChart(data) {
        const canvas =
            document.getElementById(
                'sentimentChart'
            );

        if (!canvas) {
            return;
        }


        const ctx =
            canvas.getContext('2d');


        if (this.charts.sentiment) {
            this.charts.sentiment.destroy();
            this.charts.sentiment = null;
        }


        const colors =
            getChartColors();


        this.charts.sentiment =
            createChart(
                ctx,
                'doughnut',
                {
                    labels: [
                        'Positive',
                        'Neutral',
                        'Negative'
                    ],

                    datasets: [
                        {
                            data: [
                                Number(
                                    data.positive
                                ) || 0,

                                Number(
                                    data.neutral
                                ) || 0,

                                Number(
                                    data.negative
                                ) || 0
                            ],

                            backgroundColor: [
                                colors.success ||
                                    '#22C55E',

                                colors.warning ||
                                    '#F59E0B',

                                colors.danger ||
                                    '#EF4444'
                            ],

                            borderWidth: 2,

                            borderColor:
                                getCSSVar(
                                    '--surface'
                                ) ||
                                '#FFFFFF'
                        }
                    ]
                },
                {
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            );
    },


    /**
     * Render top destinations.
     */
    renderTopDestinations(destinations) {
        const container =
            document.getElementById(
                'topDestinations'
            );

        if (!container) {
            return;
        }


        let items = destinations;


        if (
            destinations &&
            Array.isArray(
                destinations.items
            )
        ) {
            items =
                destinations.items;

        } else if (
            destinations &&
            Array.isArray(
                destinations.data
            )
        ) {
            items =
                destinations.data;
        }


        if (
            !Array.isArray(items) ||
            items.length === 0
        ) {
            container.innerHTML = `
                <p class="empty-state">
                    No destinations found
                </p>
            `;

            return;
        }


        container.innerHTML =
            items.map(
                (dest, index) => `
                    <div
                        class="top-destination-item"
                        onclick="navigateTo(
                            'destinations',
                            '${encodeURIComponent(
                                dest.name || ''
                            )}'
                        )"
                    >

                        <span
                            class="top-destination-rank"
                        >
                            #${index + 1}
                        </span>


                        <div
                            class="top-destination-info"
                        >
                            <div
                                class="top-destination-name"
                            >
                                ${
                                    escapeHtml(
                                        dest.name ||
                                        'Unknown'
                                    )
                                }
                            </div>


                            <div
                                class="top-destination-meta"
                            >
                                ${
                                    escapeHtml(
                                        dest.category ||
                                        'General'
                                    )
                                }

                                •

                                ${
                                    formatNumber(
                                        dest.review_count ||
                                        0
                                    )
                                }

                                reviews
                            </div>
                        </div>


                        <div
                            class="top-destination-rating"
                        >
                            <i
                                class="fas fa-star"
                                style="
                                    color: #F59E0B;
                                "
                            ></i>

                            ${
                                dest.rating ||
                                '0.0'
                            }
                        </div>

                    </div>
                `
            ).join('');
    },


    /**
     * Render rating distribution.
     */
    renderRatingChart(ratingDistribution) {
        const canvas =
            document.getElementById(
                'ratingChart'
            );

        if (!canvas) {
            return;
        }


        const ctx =
            canvas.getContext('2d');


        if (this.charts.rating) {
            this.charts.rating.destroy();
            this.charts.rating = null;
        }


        const colors =
            getChartColors();


        const distribution =
            Array.isArray(
                ratingDistribution
            )
                ? ratingDistribution
                : [];


        const labels =
            distribution.map(
                item =>
                    item.range ||
                    'N/A'
            );


        const data =
            distribution.map(
                item =>
                    Number(
                        item.count
                    ) || 0
            );


        this.charts.rating =
            createChart(
                ctx,
                'bar',
                {
                    labels: labels,

                    datasets: [
                        {
                            label:
                                'Destinations',

                            data: data,

                            backgroundColor: [
                                colors.danger +
                                    '80',

                                colors.warning +
                                    '80',

                                colors.accent +
                                    '80',

                                colors.success +
                                    '80'
                            ],

                            borderColor: [
                                colors.danger,

                                colors.warning,

                                colors.accent,

                                colors.success
                            ],

                            borderWidth: 2,

                            borderRadius: 4
                        }
                    ]
                },
                {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero: true,

                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            );
    },


    /**
     * Load clustering evaluation data.
     *
     * Uses:
     * GET /api/mining/clustering/evaluation?k_min=2&k_max=6
     *
     * Also loads:
     * GET /api/mining/clustering/status
     *
     * And:
     * GET /api/mining/clustering/statistics
     */
    async loadClusteringData() {
        try {
            console.log(
                'Loading K-Means clustering evaluation...'
            );


            const [
                evaluation,
                status,
                statistics
            ] = await Promise.all([
                api.request(
                    '/mining/clustering/evaluation?k_min=2&k_max=6'
                ),

                api.request(
                    '/mining/clustering/status'
                ),

                api.request(
                    '/mining/clustering/statistics'
                )
            ]);


            console.log(
                'Clustering evaluation:',
                evaluation
            );

            console.log(
                'Clustering status:',
                status
            );

            console.log(
                'Clustering statistics:',
                statistics
            );


            /*
             * Render evaluation.
             */
            this.renderClusteringEvaluation(
                evaluation || {},
                status || {}
            );


            /*
             * Render cluster distribution.
             */
            this.renderClusterDistribution(
                status || {},
                statistics || {}
            );


            /*
             * Render cluster interpretation.
             */
            this.renderClusterInterpretation(
                statistics || {},
                status || {}
            );

        } catch (error) {
            console.error(
                'Clustering dashboard error:',
                error
            );

            const badge =
                document.getElementById(
                    'clusteringStatusBadge'
                );

            if (badge) {
                badge.textContent =
                    'Evaluation unavailable';
            }

            const interpretation =
                document.getElementById(
                    'clusterInterpretation'
                );

            if (interpretation) {
                interpretation.innerHTML = `
                    <p class="empty-state">
                        Clustering evaluation data
                        is currently unavailable.
                    </p>
                `;
            }
        }
    },


    /**
     * Render clustering KPI cards and
     * Silhouette Score evaluation chart.
     */
    renderClusteringEvaluation(
        evaluation,
        status
    ) {
        const kpiGrid =
            document.getElementById(
                'clusteringKpiGrid'
            );

        const badge =
            document.getElementById(
                'clusteringStatusBadge'
            );


        const bestK =
            Number(
                evaluation.best_k ||
                status.n_clusters ||
                0
            );


        const silhouette =
            Number(
                evaluation.best_silhouette_score ??
                status.silhouette_score ??
                0
            );


        const totalDestinations =
            Number(
                status.n_destinations ||
                0
            );


        const quality =
            status.cluster_quality ||
            this.getClusterQuality(
                silhouette
            );


        if (badge) {
            badge.textContent =
                `${quality} • K=${bestK}`;
        }


        if (kpiGrid) {
            const kpis = [
                {
                    label: 'Algorithm',
                    value: 'K-Means',
                    icon: 'fa-project-diagram'
                },

                {
                    label: 'Optimal K',
                    value: bestK,
                    icon: 'fa-layer-group'
                },

                {
                    label: 'Silhouette Score',
                    value: silhouette.toFixed(4),
                    icon: 'fa-chart-line'
                },

                {
                    label: 'Cluster Quality',
                    value: quality,
                    icon: 'fa-check-circle'
                },

                {
                    label: 'Destinations',
                    value:
                        formatNumber(
                            totalDestinations
                        ),
                    icon: 'fa-map-marker-alt'
                }
            ];


            const iconColors = [
                'blue',
                'green',
                'yellow',
                'purple',
                'teal'
            ];


            kpiGrid.innerHTML =
                kpis.map(
                    (kpi, index) => `
                        <div class="kpi-card">

                            <div
                                class="kpi-icon ${
                                    iconColors[
                                        index %
                                        iconColors.length
                                    ]
                                }"
                            >
                                <i
                                    class="fas ${kpi.icon}"
                                ></i>
                            </div>


                            <div class="kpi-value">
                                ${escapeHtml(
                                    String(
                                        kpi.value
                                    )
                                )}
                            </div>


                            <div class="kpi-label">
                                ${escapeHtml(
                                    kpi.label
                                )}
                            </div>

                        </div>
                    `
                ).join('');
        }


        /*
         * Prepare evaluation results.
         */
        const results =
            Array.isArray(
                evaluation.results
            )
                ? [...evaluation.results]
                : [];


        /*
         * Sort K ascending.
         */
        results.sort(
            (a, b) =>
                Number(a.k || 0) -
                Number(b.k || 0)
        );


        const canvas =
            document.getElementById(
                'clusteringEvaluationChart'
            );

        if (!canvas) {
            return;
        }


        if (this.charts.clusteringEvaluation) {
            this.charts.clusteringEvaluation.destroy();

            this.charts.clusteringEvaluation =
                null;
        }


        const labels =
            results.map(
                item =>
                    `K=${item.k}`
            );


        const scores =
            results.map(
                item =>
                    Number(
                        item.silhouette_score
                    ) || 0
            );


        const colors =
            getChartColors();


        this.charts.clusteringEvaluation =
            createChart(
                canvas.getContext('2d'),
                'bar',
                {
                    labels: labels,

                    datasets: [
                        {
                            label:
                                'Silhouette Score',

                            data: scores,

                            backgroundColor:
                                colors.primary +
                                '80',

                            borderColor:
                                colors.primary,

                            borderWidth: 2,

                            borderRadius: 5
                        }
                    ]
                },
                {
                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            display: false
                        },

                        tooltip: {
                            callbacks: {
                                label:
                                    context =>
                                        `Silhouette Score: ${Number(
                                            context.raw
                                        ).toFixed(4)}`
                            }
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero: true,

                            max: 1,

                            title: {
                                display: true,

                                text:
                                    'Silhouette Score'
                            }
                        },

                        x: {
                            title: {
                                display: true,

                                text:
                                    'Number of Clusters (K)'
                            }
                        }
                    }
                }
            );
    },


    /**
     * Render cluster distribution chart.
     */
    renderClusterDistribution(
        status,
        statistics
    ) {
        const canvas =
            document.getElementById(
                'clusterDistributionChart'
            );

        if (!canvas) {
            return;
        }


        if (this.charts.clusterDistribution) {
            this.charts.clusterDistribution.destroy();

            this.charts.clusterDistribution =
                null;
        }


        let clusterSizes = {};


        /*
         * Prefer status.cluster_sizes.
         */
        if (
            status &&
            status.cluster_sizes
        ) {
            clusterSizes =
                status.cluster_sizes;
        }


        /*
         * If status does not contain sizes,
         * try statistics.
         */
        if (
            Object.keys(clusterSizes).length === 0 &&
            statistics &&
            Array.isArray(
                statistics.clusters
            )
        ) {
            statistics.clusters.forEach(
                cluster => {
                    clusterSizes[
                        cluster.cluster_id
                    ] =
                        Number(
                            cluster.count
                        ) || 0;
                }
            );
        }


        const clusterIds =
            Object.keys(
                clusterSizes
            ).sort(
                (a, b) =>
                    Number(a) -
                    Number(b)
            );


        const counts =
            clusterIds.map(
                id =>
                    Number(
                        clusterSizes[id]
                    ) || 0
            );


        const labels =
            clusterIds.map(
                id =>
                    `Cluster ${id}`
            );


        this.charts.clusterDistribution =
            createChart(
                canvas.getContext('2d'),
                'bar',
                {
                    labels: labels,

                    datasets: [
                        {
                            label:
                                'Destinations',

                            data: counts,

                            backgroundColor:
                                getChartColors()
                                    .accent +
                                '80',

                            borderColor:
                                getChartColors()
                                    .accent,

                            borderWidth: 2,

                            borderRadius: 5
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
                            beginAtZero: true
                        }
                    }
                }
            );
    },


    /**
     * Render cluster interpretation.
     */
    renderClusterInterpretation(
        statistics,
        status
    ) {
        const container =
            document.getElementById(
                'clusterInterpretation'
            );

        if (!container) {
            return;
        }


        let clusters =
            statistics &&
            Array.isArray(
                statistics.clusters
            )
                ? statistics.clusters
                : [];


        /*
         * If statistics endpoint does not
         * return cluster data, build a basic
         * interpretation from cluster sizes.
         */
        if (
            clusters.length === 0 &&
            status &&
            status.cluster_sizes
        ) {
            clusters =
                Object.entries(
                    status.cluster_sizes
                ).map(
                    ([clusterId, count]) => ({
                        cluster_id:
                            Number(clusterId),

                        cluster_name:
                            this.getDefaultClusterName(
                                Number(clusterId)
                            ),

                        count:
                            Number(count) || 0
                    })
                );
        }


        if (clusters.length === 0) {
            container.innerHTML = `
                <p class="empty-state">
                    No cluster interpretation data available.
                </p>
            `;

            return;
        }


        clusters.sort(
            (a, b) =>
                Number(
                    a.cluster_id || 0
                ) -
                Number(
                    b.cluster_id || 0
                )
        );


        container.innerHTML =
            clusters.map(
                cluster => {

                    const clusterId =
                        Number(
                            cluster.cluster_id
                        );


                    const count =
                        Number(
                            cluster.count
                        ) || 0;


                    const name =
                        cluster.cluster_name ||
                        this.getDefaultClusterName(
                            clusterId
                        );


                    const percentage =
                        status &&
                        Number(
                            status.n_destinations
                        ) > 0
                            ? (
                                count /
                                Number(
                                    status.n_destinations
                                )
                            ) *
                            100
                            : 0;


                    return `
                        <div
                            style="
                                padding: 14px;
                                margin-bottom: 10px;
                                border: 1px solid var(--border, #E2E8F0);
                                border-radius: 8px;
                                background: var(--surface, #FFFFFF);
                            "
                        >

                            <div
                                style="
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    gap: 10px;
                                "
                            >

                                <strong>
                                    Cluster ${clusterId}
                                    -
                                    ${escapeHtml(
                                        name
                                    )}
                                </strong>

                                <span>
                                    ${formatNumber(
                                        count
                                    )}
                                    destinations
                                </span>

                            </div>


                            <div
                                style="
                                    margin-top: 8px;
                                    height: 7px;
                                    background: var(--border, #E2E8F0);
                                    border-radius: 5px;
                                    overflow: hidden;
                                "
                            >
                                <div
                                    style="
                                        width: ${Math.min(
                                            percentage,
                                            100
                                        )}%;
                                        height: 100%;
                                        background: var(--primary, #2563EB);
                                    "
                                ></div>
                            </div>


                            <div
                                style="
                                    margin-top: 6px;
                                    font-size: 12px;
                                    opacity: 0.75;
                                "
                            >
                                ${percentage.toFixed(1)}%
                                of all destinations
                            </div>

                        </div>
                    `;
                }
            ).join('');
    },


    /**
     * Return cluster quality based on
     * Silhouette Score.
     */
    getClusterQuality(score) {
        const value =
            Number(score) || 0;


        if (value >= 0.70) {
            return 'Excellent';
        }

        if (value >= 0.50) {
            return 'Good';
        }

        if (value >= 0.25) {
            return 'Fair';
        }

        return 'Weak';
    },


    /**
     * Default cluster names.
     *
     * These are used only if the API does not
     * provide cluster_name.
     */
    getDefaultClusterName(clusterId) {
        const names = {
            0: 'Popular Destinations',
            1: 'General Tourism',
            2: 'Specialized Destinations',
            3: 'Emerging Destinations'
        };

        return (
            names[clusterId] ||
            `Tourism Cluster ${clusterId}`
        );
    },


    /**
     * Render Leaflet tourism map.
     *
     * Receives ALL destinations loaded by
     * loadAllDestinations().
     */
    renderTourismMap(destinations) {
        const mapElement =
            document.getElementById(
                'tourismMap'
            );

        const countElement =
            document.getElementById(
                'mapDestinationCount'
            );


        if (!mapElement) {
            console.warn(
                'Tourism map container not found.'
            );

            return;
        }


        /*
         * Check Leaflet.
         */
        if (
            typeof L === 'undefined'
        ) {
            console.error(
                'Leaflet.js is not loaded.'
            );

            if (countElement) {
                countElement.textContent =
                    'Leaflet unavailable';
            }

            return;
        }


        /*
         * Normalize destinations.
         */
        let items = [];


        if (
            Array.isArray(
                destinations
            )
        ) {
            items =
                destinations;

        } else if (
            destinations &&
            Array.isArray(
                destinations.items
            )
        ) {
            items =
                destinations.items;

        } else if (
            destinations &&
            Array.isArray(
                destinations.data
            )
        ) {
            items =
                destinations.data;

        } else if (
            destinations &&
            Array.isArray(
                destinations.destinations
            )
        ) {
            items =
                destinations.destinations;
        }


        /*
         * Find valid coordinates.
         */
        const validDestinations =
            items.filter(
                dest => {

                    const lat =
                        Number(
                            dest.latitude
                        );

                    const lng =
                        Number(
                            dest.longitude
                        );


                    return (
                        Number.isFinite(lat) &&
                        Number.isFinite(lng) &&
                        lat >= -90 &&
                        lat <= 90 &&
                        lng >= -180 &&
                        lng <= 180
                    );
                }
            );


        console.log(
            `Tourism map: ${validDestinations.length} destinations with valid coordinates out of ${items.length}.`
        );


        /*
         * Update counter.
         */
        if (countElement) {
            countElement.textContent =
                `${validDestinations.length} destinations mapped`;
        }


        /*
         * Remove old map.
         */
        if (this.map) {
            try {
                this.map.remove();
            } catch (error) {
                console.warn(
                    'Could not remove previous Leaflet map:',
                    error
                );
            }

            this.map = null;
            this.mapMarkers = [];
        }


        /*
         * Timor-Leste center.
         */
        const timorLesteCenter = [
            -8.85,
            125.75
        ];


        /*
         * Create map.
         */
        this.map =
            L.map(
                'tourismMap',
                {
                    center:
                        timorLesteCenter,

                    zoom: 8,

                    zoomControl: true,

                    scrollWheelZoom: true
                }
            );


        /*
         * OpenStreetMap tiles.
         */
        L.tileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {
                maxZoom: 19,

                attribution:
                    '&copy; OpenStreetMap contributors'
            }
        ).addTo(
            this.map
        );


        /*
         * Create marker for every destination.
         */
        validDestinations.forEach(
            dest => {

                const lat =
                    Number(
                        dest.latitude
                    );

                const lng =
                    Number(
                        dest.longitude
                    );


                const marker =
                    L.marker(
                        [
                            lat,
                            lng
                        ]
                    ).addTo(
                        this.map
                    );


                const name =
                    escapeHtml(
                        dest.name ||
                        'Unknown Destination'
                    );


                const municipality =
                    escapeHtml(
                        dest.municipality ||
                        'Unknown'
                    );


                const category =
                    escapeHtml(
                        dest.category ||
                        'General'
                    );


                const rating =
                    Number(
                        dest.rating
                    );


                const popularity =
                    Number(
                        dest.popularity_score
                    );


                const reviewCount =
                    Number(
                        dest.review_count
                    ) || 0;


                const ratingText =
                    Number.isFinite(
                        rating
                    )
                        ? rating.toFixed(1)
                        : 'N/A';


                const popularityText =
                    Number.isFinite(
                        popularity
                    )
                        ? popularity.toFixed(1)
                        : 'N/A';


                const popupHtml = `
                    <div
                        style="
                            min-width: 220px;
                            line-height: 1.5;
                        "
                    >

                        <h3
                            style="
                                margin: 0 0 8px 0;
                                font-size: 16px;
                            "
                        >
                            ${name}
                        </h3>


                        <div>
                            <strong>
                                Municipality:
                            </strong>
                            ${municipality}
                        </div>


                        <div>
                            <strong>
                                Category:
                            </strong>
                            ${category}
                        </div>


                        <div>
                            <strong>
                                Rating:
                            </strong>
                            ⭐ ${ratingText}
                        </div>


                        <div>
                            <strong>
                                Popularity:
                            </strong>
                            ${popularityText}
                        </div>


                        <div>
                            <strong>
                                Reviews:
                            </strong>
                            ${formatNumber(
                                reviewCount
                            )}
                        </div>


                        <div
                            style="
                                margin-top: 6px;
                                font-size: 11px;
                                opacity: 0.7;
                            "
                        >
                            ${lat.toFixed(5)},
                            ${lng.toFixed(5)}
                        </div>

                    </div>
                `;


                marker.bindPopup(
                    popupHtml
                );


                this.mapMarkers.push(
                    marker
                );
            }
        );


        /*
         * Fit map to markers.
         */
        if (
            this.mapMarkers.length > 0
        ) {
            const group =
                L.featureGroup(
                    this.mapMarkers
                );


            this.map.fitBounds(
                group
                    .getBounds()
                    .pad(0.08)
            );

        } else {

            this.map.setView(
                timorLesteCenter,
                8
            );
        }


        /*
         * Fix dynamic map size.
         */
        setTimeout(
            () => {

                if (!this.map) {
                    return;
                }


                this.map.invalidateSize();


                if (
                    this.mapMarkers.length > 0
                ) {
                    const group =
                        L.featureGroup(
                            this.mapMarkers
                        );


                    this.map.fitBounds(
                        group
                            .getBounds()
                            .pad(0.08)
                    );
                }

            },
            300
        );
    }
};


/**
 * Initialize dashboard when DOM is ready.
 */
document.addEventListener(
    'DOMContentLoaded',
    function() {

        const dashboardContainer =
            document.getElementById(
                'dashboardContainer'
            );


        if (
            dashboardContainer
        ) {
            dashboard.init();
        }
    }
);


/**
 * Load dashboard function for SPA navigation.
 */
function loadDashboard() {

    const container =
        document.getElementById(
            'dashboardContainer'
        ) ||
        document.getElementById(
            'appContent'
        );


    if (container) {
        dashboard.init();
    }
}