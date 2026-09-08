/**
 * Analytics / Exploratory Data Analysis Module
 * Timor-Leste Tourism Intelligence Platform
 *
 * Purpose:
 * - Dataset overview
 * - Rating analysis
 * - Category analysis
 * - Municipality analysis
 * - Review analysis
 * - Top destinations
 * - Tourism trend
 * - Sentiment analysis
 * - Correlation analysis
 * - Automatic EDA findings
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

            console.error(
                'Analytics initialization error:',
                error
            );

            if (typeof showToast === 'function') {

                showToast(
                    'Error loading analytics: ' +
                    error.message,
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

                <h2>📊 Data Analytics / EDA</h2>

                <p>
                    Exploratory Data Analysis of
                    Timor-Leste tourism data
                </p>

            </div>


            <!-- ==================================================
                 DATASET OVERVIEW
                 ================================================== -->

            <div
                class="quick-stats"
                id="quickStats"
            >
                <!-- Rendered by JS -->
            </div>


            <!-- ==================================================
                 RATING ANALYSIS
                 ================================================== -->

            <div class="charts-grid-2">

                <div class="chart-container">

                    <div class="chart-header">

                        <span class="chart-title">
                            ⭐ Rating Distribution
                        </span>

                    </div>

                    <div
                        class="chart-wrapper"
                        style="height: 360px;"
                    >

                        <canvas
                            id="ratingDistributionChart"
                        ></canvas>

                    </div>

                </div>


                <!-- ==================================================
                     REVIEW COUNT DISTRIBUTION
                     ================================================== -->

                <div class="chart-container">

                    <div class="chart-header">

                        <span class="chart-title">
                            💬 Review Count Distribution
                        </span>

                    </div>

                    <div
                        class="chart-wrapper"
                        style="height: 360px;"
                    >

                        <canvas
                            id="reviewDistributionChart"
                        ></canvas>

                    </div>

                </div>

            </div>


            <!-- ==================================================
                 CATEGORY + MUNICIPALITY
                 ================================================== -->

            <div class="charts-grid-2">

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

                        <canvas
                            id="categoryChart"
                        ></canvas>

                    </div>

                </div>


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

                        <canvas
                            id="municipalityChart"
                        ></canvas>

                    </div>

                </div>

            </div>


            <!-- ==================================================
                 TOURISM TREND
                 ================================================== -->

            <div
                class="chart-container"
                style="margin-top: 24px;"
            >

                <div class="chart-header">

                    <span class="chart-title">
                        📈 Tourism / Review Trend
                    </span>

                </div>

                <div
                    class="chart-wrapper"
                    style="height: 360px;"
                >

                    <canvas
                        id="trendChart"
                    ></canvas>

                </div>

            </div>


            <!-- ==================================================
                 TOP DESTINATIONS
                 ================================================== -->

            <div
                class="card"
                style="margin-top: 24px;"
            >

                <div class="card-header">

                    <span class="card-title">
                        🏆 Top 10 Most Reviewed Destinations
                    </span>

                </div>

                <div
                    id="topDestinations"
                    style="
                        display: grid;
                        gap: 10px;
                        margin-top: 12px;
                    "
                >
                    <!-- Rendered by JS -->
                </div>

            </div>


            <!-- ==================================================
                 CORRELATION ANALYSIS
                 ================================================== -->

            <div
                class="chart-container"
                style="margin-top: 24px;"
            >

                <div class="chart-header">

                    <span class="chart-title">
                        🔎 Rating vs Review Count
                    </span>

                </div>

                <div
                    class="chart-wrapper"
                    style="height: 400px;"
                >

                    <canvas
                        id="correlationChart"
                    ></canvas>

                </div>

                <div
                    id="correlationSummary"
                    style="
                        margin-top: 12px;
                        padding: 12px 16px;
                        border-radius: 8px;
                        background: var(--surface-hover);
                        color: var(--text-secondary);
                        font-size: 14px;
                    "
                >
                    Calculating relationship...
                </div>

            </div>


            <!-- ==================================================
                 SENTIMENT ANALYSIS
                 ================================================== -->

            <div
                class="card"
                style="margin-top: 24px;"
            >

                <div class="card-header">

                    <span class="card-title">
                        😊 Sentiment Distribution
                    </span>

                </div>


                <div
                    style="
                        display: grid;
                        grid-template-columns:
                            minmax(0, 1fr)
                            minmax(0, 1fr);
                        gap: 24px;
                        align-items: center;
                    "
                >

                    <div
                        class="chart-wrapper"
                        style="height: 330px;"
                    >

                        <canvas
                            id="sentimentChart"
                        ></canvas>

                    </div>


                    <div
                        id="sentimentDetails"
                        style="
                            display: grid;
                            grid-template-columns:
                                1fr 1fr;
                            gap: 16px;
                        "
                    >
                        <!-- Rendered by JS -->
                    </div>

                </div>

            </div>


            <!-- ==================================================
                 EDA FINDINGS
                 ================================================== -->

            <div
                class="card"
                style="margin-top: 24px;"
            >

                <div class="card-header">

                    <span class="card-title">
                        📝 EDA Findings
                    </span>

                </div>


                <div
                    id="edaFindings"
                    style="
                        display: grid;
                        gap: 12px;
                        margin-top: 8px;
                    "
                >
                    <!-- Rendered by JS -->
                </div>

            </div>

        `;
    },


    // ============================================================
    // LOAD ALL DESTINATIONS
    // ============================================================

    async loadAllDestinations() {

        const allDestinations = [];

        const limit = 100;

        let skip = 0;

        let total = null;

        let safetyCounter = 0;

        while (true) {

            safetyCounter++;

            if (safetyCounter > 20) {
                console.warn(
                    'Destination pagination safety limit reached.'
                );
                break;
            }

            const response =
                await api.getDestinations({
                    skip: skip,
                    limit: limit
                });

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

            }

            if (
                response &&
                Number.isFinite(
                    Number(response.total)
                )
            ) {

                total = Number(response.total);

            }

            if (items.length === 0) {
                break;
            }

            allDestinations.push(...items);

            skip += items.length;

            if (
                total !== null &&
                allDestinations.length >= total
            ) {
                break;
            }

            if (items.length < limit) {
                break;
            }
        }

        console.log(
            'EDA destinations loaded:',
            allDestinations.length
        );

        return allDestinations;
    },


    // ============================================================
    // LOAD DATA
    // ============================================================

    async loadData() {

        try {

            console.log(
                'Loading EDA analytics data...'
            );


            const [
                stats,
                categories,
                municipalities,
                sentiment,
                trendData,
                topDestinations,
                destinations
            ] = await Promise.all([

                api.getStatistics(),

                api.getCategoryAnalysis(),

                api.getMunicipalityAnalysis(),

                api.getSentimentSummaryGlobal(),

                api.getDashboardTrends(30),

                api.getTopDestinations(10),

                this.loadAllDestinations()

            ]);


            console.log(
                'EDA statistics:',
                stats
            );

            console.log(
                'EDA categories:',
                categories
            );

            console.log(
                'EDA municipalities:',
                municipalities
            );

            console.log(
                'EDA sentiment:',
                sentiment
            );

            console.log(
                'EDA trend:',
                trendData
            );

            console.log(
                'EDA top destinations:',
                topDestinations
            );

            console.log(
                'EDA all destinations:',
                destinations
            );


            // ----------------------------------------------------
            // Render
            // ----------------------------------------------------

            this.renderQuickStats(
                stats,
                destinations
            );


            this.renderRatingDistribution(
                stats,
                destinations
            );


            this.renderReviewDistribution(
                destinations
            );


            this.renderCategoryChart(
                categories
            );


            this.renderMunicipalityChart(
                municipalities
            );


            this.renderTrendChart(
                trendData
            );


            this.renderTopDestinations(
                topDestinations,
                destinations
            );


            this.renderCorrelationChart(
                destinations
            );


            this.renderSentiment(
                sentiment
            );


            this.renderFindings({
                stats,
                categories,
                municipalities,
                sentiment,
                destinations,
                topDestinations
            });


        } catch (error) {

            console.error(
                'Error loading EDA data:',
                error
            );

            if (typeof showToast === 'function') {

                showToast(
                    'Error loading analytics data: ' +
                    error.message,
                    'error'
                );

            }
        }
    },


    // ============================================================
    // QUICK STATS
    // ============================================================

    renderQuickStats(
        stats,
        destinations
    ) {

        const container =
            document.getElementById(
                'quickStats'
            );

        if (!container) {
            return;
        }


        stats = stats || {};

        destinations =
            Array.isArray(destinations)
                ? destinations
                : [];


        const totalDestinations =
            Number(
                stats.total_destinations
            ) ||
            destinations.length ||
            0;


        const totalReviews =
            Number(
                stats.total_reviews
            ) ||
            destinations.reduce(
                (sum, item) =>
                    sum +
                    (
                        Number(
                            item.review_count
                        ) || 0
                    ),
                0
            );


        const validRatings =
            destinations
                .map(
                    item =>
                        Number(item.rating)
                )
                .filter(
                    rating =>
                        Number.isFinite(rating) &&
                        rating > 0
                );


        const averageRating =
            validRatings.length > 0
                ? (
                    validRatings.reduce(
                        (sum, value) =>
                            sum + value,
                        0
                    ) /
                    validRatings.length
                ).toFixed(2)
                : '0.00';


        const averageReviews =
            totalDestinations > 0
                ? (
                    totalReviews /
                    totalDestinations
                ).toFixed(1)
                : '0.0';


        const destinationsWithReviews =
            destinations.filter(
                item =>
                    (
                        Number(
                            item.review_count
                        ) || 0
                    ) > 0
            ).length;


        const reviewCoverage =
            destinations.length > 0
                ? (
                    destinationsWithReviews /
                    destinations.length *
                    100
                ).toFixed(1)
                : '0.0';


        container.innerHTML = `

            <div class="stat-item">

                <div class="stat-value">

                    ${formatNumber(
                        totalDestinations
                    )}

                </div>

                <div class="stat-label">
                    Total Destinations
                </div>

            </div>


            <div class="stat-item">

                <div class="stat-value">

                    ${formatNumber(
                        totalReviews
                    )}

                </div>

                <div class="stat-label">
                    Total Review Count
                </div>

            </div>


            <div class="stat-item">

                <div class="stat-value">

                    ${averageRating}

                </div>

                <div class="stat-label">
                    Average Rating
                </div>

            </div>


            <div class="stat-item">

                <div class="stat-value">

                    ${averageReviews}

                </div>

                <div class="stat-label">
                    Avg Reviews / Destination
                </div>

            </div>


            <div class="stat-item">

                <div class="stat-value">

                    ${formatNumber(
                        destinationsWithReviews
                    )}

                </div>

                <div class="stat-label">
                    Destinations with Reviews
                </div>

            </div>


            <div class="stat-item">

                <div class="stat-value">

                    ${reviewCoverage}%

                </div>

                <div class="stat-label">
                    Review Coverage
                </div>

            </div>

        `;
    },


    // ============================================================
    // RATING DISTRIBUTION
    // ============================================================

    renderRatingDistribution(
        stats,
        destinations
    ) {

        const canvas =
            document.getElementById(
                'ratingDistributionChart'
            );

        if (!canvas) {
            return;
        }


        if (this.charts.ratingDistribution) {

            this.charts.ratingDistribution.destroy();

            this.charts.ratingDistribution = null;
        }


        const ratingBuckets = {
            '1 Star': 0,
            '2 Stars': 0,
            '3 Stars': 0,
            '4 Stars': 0,
            '5 Stars': 0
        };


        destinations.forEach(
            destination => {

                const rating =
                    Number(
                        destination.rating
                    );

                if (
                    !Number.isFinite(rating) ||
                    rating <= 0
                ) {
                    return;
                }


                let bucket;

                if (rating < 1.5) {

                    bucket = '1 Star';

                } else if (rating < 2.5) {

                    bucket = '2 Stars';

                } else if (rating < 3.5) {

                    bucket = '3 Stars';

                } else if (rating < 4.5) {

                    bucket = '4 Stars';

                } else {

                    bucket = '5 Stars';
                }


                ratingBuckets[bucket]++;
            }
        );


        const labels =
            Object.keys(
                ratingBuckets
            );

        const data =
            Object.values(
                ratingBuckets
            );


        const colors =
            typeof getChartColors === 'function'
                ? getChartColors()
                : {};


        this.charts.ratingDistribution =
            createChart(

                canvas.getContext('2d'),

                'bar',

                {

                    labels,

                    datasets: [

                        {

                            label:
                                'Destinations',

                            data,

                            backgroundColor: [

                                (colors.danger ||
                                    '#EF4444') + '80',

                                (colors.warning ||
                                    '#F59E0B') + '80',

                                (colors.accent ||
                                    '#F59E0B') + '80',

                                (colors.success ||
                                    '#22C55E') + '80',

                                (colors.primary ||
                                    '#0C4A6E') + '80'

                            ],

                            borderColor: [

                                colors.danger ||
                                    '#EF4444',

                                colors.warning ||
                                    '#F59E0B',

                                colors.accent ||
                                    '#F59E0B',

                                colors.success ||
                                    '#22C55E',

                                colors.primary ||
                                    '#0C4A6E'

                            ],

                            borderWidth: 2,

                            borderRadius: 5

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
                                precision: 0
                            },

                            title: {

                                display: true,

                                text:
                                    'Number of Destinations'

                            }

                        },

                        x: {

                            title: {

                                display: true,

                                text:
                                    'Rating'

                            }

                        }

                    }

                }

            );
    },


    // ============================================================
    // REVIEW COUNT DISTRIBUTION
    // ============================================================

    renderReviewDistribution(
        destinations
    ) {

        const canvas =
            document.getElementById(
                'reviewDistributionChart'
            );

        if (!canvas) {
            return;
        }


        if (this.charts.reviewDistribution) {

            this.charts.reviewDistribution.destroy();

            this.charts.reviewDistribution = null;
        }


        const buckets = {

            '0 Reviews': 0,

            '1–10': 0,

            '11–50': 0,

            '51–100': 0,

            '101–500': 0,

            '500+': 0

        };


        destinations.forEach(
            destination => {

                const count =
                    Number(
                        destination.review_count
                    ) || 0;


                if (count === 0) {

                    buckets['0 Reviews']++;

                } else if (count <= 10) {

                    buckets['1–10']++;

                } else if (count <= 50) {

                    buckets['11–50']++;

                } else if (count <= 100) {

                    buckets['51–100']++;

                } else if (count <= 500) {

                    buckets['101–500']++;

                } else {

                    buckets['500+']++;
                }

            }
        );


        this.charts.reviewDistribution =
            createChart(

                canvas.getContext('2d'),

                'bar',

                {

                    labels:
                        Object.keys(buckets),

                    datasets: [

                        {

                            label:
                                'Destinations',

                            data:
                                Object.values(buckets),

                            backgroundColor:
                                '#14B8A680',

                            borderColor:
                                '#14B8A6',

                            borderWidth: 2,

                            borderRadius: 5

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
                                precision: 0
                            },

                            title: {

                                display: true,

                                text:
                                    'Number of Destinations'

                            }

                        },

                        x: {

                            title: {

                                display: true,

                                text:
                                    'Review Count Range'

                            }

                        }

                    }

                }

            );
    },


    // ============================================================
    // CATEGORY CHART
    // ============================================================

    renderCategoryChart(
        categories
    ) {

        const canvas =
            document.getElementById(
                'categoryChart'
            );

        if (!canvas) {
            return;
        }


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


        const sorted =
            [...categories]
                .sort(
                    (a, b) =>
                        (
                            Number(b.count) || 0
                        ) -
                        (
                            Number(a.count) || 0
                        )
                );


        this.charts.category =
            createChart(

                canvas.getContext('2d'),

                'bar',

                {

                    labels:
                        sorted.map(
                            item =>
                                item.category ||
                                'Unknown'
                        ),

                    datasets: [

                        {

                            label:
                                'Destinations',

                            data:
                                sorted.map(
                                    item =>
                                        Number(
                                            item.count
                                        ) || 0
                                ),

                            backgroundColor:
                                '#0C4A6E80',

                            borderColor:
                                '#0C4A6E',

                            borderWidth: 2,

                            borderRadius: 5

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
                                precision: 0
                            },

                            title: {

                                display: true,

                                text:
                                    'Number of Destinations'

                            }

                        }

                    }

                }

            );
    },


    // ============================================================
    // MUNICIPALITY CHART
    // ============================================================

    renderMunicipalityChart(
        municipalities
    ) {

        const canvas =
            document.getElementById(
                'municipalityChart'
            );

        if (!canvas) {
            return;
        }


        if (this.charts.municipality) {

            this.charts.municipality.destroy();

            this.charts.municipality = null;
        }


        if (!Array.isArray(municipalities)) {
            return;
        }


        const sorted =
            [...municipalities]
                .sort(
                    (a, b) =>
                        (
                            Number(b.count) || 0
                        ) -
                        (
                            Number(a.count) || 0
                        )
                );


        this.charts.municipality =
            createChart(

                canvas.getContext('2d'),

                'bar',

                {

                    labels:
                        sorted.map(
                            item =>
                                item.municipality ||
                                'Unknown'
                        ),

                    datasets: [

                        {

                            label:
                                'Destinations',

                            data:
                                sorted.map(
                                    item =>
                                        Number(
                                            item.count
                                        ) || 0
                                ),

                            backgroundColor:
                                '#14B8A680',

                            borderColor:
                                '#14B8A6',

                            borderWidth: 2,

                            borderRadius: 4

                        }

                    ]

                },

                {

                    indexAxis: 'y',

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        x: {

                            beginAtZero: true,

                            ticks: {
                                precision: 0
                            },

                            title: {

                                display: true,

                                text:
                                    'Number of Destinations'

                            }

                        },

                        y: {

                            title: {

                                display: true,

                                text:
                                    'Municipality'

                            }

                        }

                    }

                }

            );
    },


    // ============================================================
    // TOURISM TREND
    // ============================================================

    renderTrendChart(
        trendData
    ) {

        const canvas =
            document.getElementById(
                'trendChart'
            );

        if (!canvas) {
            return;
        }


        if (this.charts.trend) {

            this.charts.trend.destroy();

            this.charts.trend = null;
        }


        trendData =
            trendData || {};


        const labels =
            Array.isArray(
                trendData.labels
            )
                ? trendData.labels
                : [];


        const datasets =
            Array.isArray(
                trendData.datasets
            )
                ? trendData.datasets
                : [];


        if (
            labels.length === 0 ||
            datasets.length === 0
        ) {

            canvas.parentElement.innerHTML = `

                <div
                    style="
                        padding: 60px 20px;
                        text-align: center;
                        color: var(--text-secondary);
                    "
                >

                    No trend data available.

                </div>

            `;

            return;
        }


        this.charts.trend =
            createChart(

                canvas.getContext('2d'),

                'line',

                {

                    labels,

                    datasets

                },

                {

                    plugins: {

                        legend: {

                            position:
                                'bottom'

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            title: {

                                display: true,

                                text:
                                    'Activity'

                            }

                        }

                    }

                }

            );
    },


    // ============================================================
    // TOP DESTINATIONS
    // ============================================================

    renderTopDestinations(
        topDestinations,
        destinations
    ) {

        const container =
            document.getElementById(
                'topDestinations'
            );

        if (!container) {
            return;
        }


        let items =
            Array.isArray(topDestinations)
                ? [...topDestinations]
                : [];


        if (items.length === 0) {

            items =
                [...destinations]
                    .sort(
                        (a, b) =>
                            (
                                Number(
                                    b.review_count
                                ) || 0
                            ) -
                            (
                                Number(
                                    a.review_count
                                ) || 0
                            )
                    )
                    .slice(0, 10);

        }


        if (items.length === 0) {

            container.innerHTML = `

                <div
                    style="
                        padding: 20px;
                        color: var(--text-secondary);
                    "
                >
                    No destination data available.
                </div>

            `;

            return;
        }


        container.innerHTML =
            items.slice(0, 10)
                .map(
                    (destination, index) => {

                        const name =
                            escapeHtml(
                                destination.name ||
                                'Unknown Destination'
                            );


                        const category =
                            escapeHtml(
                                destination.category ||
                                'General'
                            );


                        const municipality =
                            escapeHtml(
                                destination.municipality ||
                                'Unknown'
                            );


                        const reviews =
                            Number(
                                destination.review_count
                            ) || 0;


                        const rating =
                            Number(
                                destination.rating
                            );


                        const ratingText =
                            Number.isFinite(
                                rating
                            ) &&
                            rating > 0
                                ? rating.toFixed(1)
                                : 'N/A';


                        return `

                            <div
                                style="
                                    display: grid;
                                    grid-template-columns:
                                        50px
                                        minmax(0, 1fr)
                                        auto;
                                    gap: 14px;
                                    align-items: center;
                                    padding: 14px;
                                    border:
                                        1px solid
                                        var(--border);
                                    border-radius: 10px;
                                    background:
                                        var(--surface);
                                "
                            >

                                <div
                                    style="
                                        font-size: 20px;
                                        font-weight: 700;
                                        text-align: center;
                                        color:
                                            var(--primary);
                                    "
                                >
                                    #${index + 1}
                                </div>


                                <div>

                                    <div
                                        style="
                                            font-weight: 700;
                                            color: var(--text);
                                            margin-bottom: 4px;
                                        "
                                    >
                                        ${name}
                                    </div>


                                    <div
                                        style="
                                            font-size: 13px;
                                            color:
                                                var(--text-secondary);
                                        "
                                    >
                                        ${category}
                                        •
                                        ${municipality}
                                        •
                                        ${formatNumber(
                                            reviews
                                        )}
                                        reviews
                                    </div>

                                </div>


                                <div
                                    style="
                                        font-weight: 700;
                                        white-space: nowrap;
                                    "
                                >
                                    ⭐ ${ratingText}
                                </div>

                            </div>

                        `;
                    }
                )
                .join('');
    },


    // ============================================================
    // CORRELATION ANALYSIS
    // ============================================================

    renderCorrelationChart(
        destinations
    ) {

        const canvas =
            document.getElementById(
                'correlationChart'
            );

        const summary =
            document.getElementById(
                'correlationSummary'
            );


        if (!canvas) {
            return;
        }


        if (this.charts.correlation) {

            this.charts.correlation.destroy();

            this.charts.correlation = null;
        }


        const validData =
            destinations
                .map(
                    destination => ({

                        x:
                            Number(
                                destination.review_count
                            ),

                        y:
                            Number(
                                destination.rating
                            )

                    })
                )
                .filter(
                    item =>
                        Number.isFinite(item.x) &&
                        Number.isFinite(item.y) &&
                        item.x >= 0 &&
                        item.y > 0
                );


        if (validData.length === 0) {

            if (summary) {

                summary.textContent =
                    'Insufficient data for correlation analysis.';

            }

            return;
        }


        this.charts.correlation =
            createChart(

                canvas.getContext('2d'),

                'scatter',

                {

                    datasets: [

                        {

                            label:
                                'Destinations',

                            data:
                                validData,

                            backgroundColor:
                                '#8B5CF680',

                            borderColor:
                                '#8B5CF6',

                            pointRadius: 4,

                            pointHoverRadius: 6

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

                        x: {

                            beginAtZero: true,

                            title: {

                                display: true,

                                text:
                                    'Review Count'

                            }

                        },

                        y: {

                            beginAtZero: false,

                            title: {

                                display: true,

                                text:
                                    'Rating'

                            },

                            min: 0,

                            max: 5

                        }

                    }

                }

            );


        // --------------------------------------------------------
        // Pearson correlation
        // --------------------------------------------------------

        const correlation =
            this.calculatePearsonCorrelation(
                validData.map(item => item.x),
                validData.map(item => item.y)
            );


        if (summary) {

            if (
                Number.isFinite(correlation)
            ) {

                const strength =
                    Math.abs(correlation) >= 0.7
                        ? 'strong'
                        : Math.abs(correlation) >= 0.4
                            ? 'moderate'
                            : Math.abs(correlation) >= 0.2
                                ? 'weak'
                                : 'very weak';


                const direction =
                    correlation > 0
                        ? 'positive'
                        : correlation < 0
                            ? 'negative'
                            : 'no';


                summary.innerHTML = `

                    <strong>
                        Correlation result:
                    </strong>

                    Pearson r =
                    ${correlation.toFixed(3)}

                    <br>

                    The relationship between
                    review count and rating is
                    <strong>
                        ${strength} ${direction}
                    </strong>.

                `;

            } else {

                summary.textContent =
                    'Correlation could not be calculated.';
            }
        }
    },


    // ============================================================
    // PEARSON CORRELATION
    // ============================================================

    calculatePearsonCorrelation(
        x,
        y
    ) {

        if (
            !Array.isArray(x) ||
            !Array.isArray(y) ||
            x.length !== y.length ||
            x.length < 2
        ) {

            return NaN;
        }


        const n = x.length;


        const meanX =
            x.reduce(
                (sum, value) =>
                    sum + value,
                0
            ) / n;


        const meanY =
            y.reduce(
                (sum, value) =>
                    sum + value,
                0
            ) / n;


        let numerator = 0;

        let denominatorX = 0;

        let denominatorY = 0;


        for (
            let i = 0;
            i < n;
            i++
        ) {

            const dx =
                x[i] - meanX;

            const dy =
                y[i] - meanY;


            numerator +=
                dx * dy;

            denominatorX +=
                dx * dx;

            denominatorY +=
                dy * dy;
        }


        const denominator =
            Math.sqrt(
                denominatorX *
                denominatorY
            );


        if (denominator === 0) {
            return NaN;
        }


        return numerator / denominator;
    },


    // ============================================================
    // SENTIMENT
    // ============================================================

    renderSentiment(
        sentiment
    ) {

        const chartCanvas =
            document.getElementById(
                'sentimentChart'
            );


        const details =
            document.getElementById(
                'sentimentDetails'
            );


        if (!sentiment) {
            return;
        }


        const positive =
            Number(
                sentiment.positive
            ) || 0;


        const neutral =
            Number(
                sentiment.neutral
            ) || 0;


        const negative =
            Number(
                sentiment.negative
            ) || 0;


        const total =
            Number(
                sentiment.total
            ) || 0;


        const averageScore =
            Number(
                sentiment.average_score
            ) || 0;


        if (
            chartCanvas
        ) {

            if (this.charts.sentiment) {

                this.charts.sentiment.destroy();

                this.charts.sentiment = null;
            }


            this.charts.sentiment =
                createChart(

                    chartCanvas.getContext(
                        '2d'
                    ),

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

                                    positive,

                                    neutral,

                                    negative

                                ],

                                backgroundColor: [

                                    '#22C55E',

                                    '#F59E0B',

                                    '#EF4444'

                                ],

                                borderWidth: 2

                            }

                        ]

                    },

                    {

                        plugins: {

                            legend: {

                                position:
                                    'bottom'

                            }

                        }

                    }

                );
        }


        if (!details) {
            return;
        }


        const positiveReviews =
            total > 0
                ? Math.round(
                    positive /
                    100 *
                    total
                )
                : 0;


        const neutralReviews =
            total > 0
                ? Math.round(
                    neutral /
                    100 *
                    total
                )
                : 0;


        const negativeReviews =
            total > 0
                ? Math.round(
                    negative /
                    100 *
                    total
                )
                : 0;


        details.innerHTML = `

            <div
                style="
                    padding: 16px;
                    border-radius: 10px;
                    border-left:
                        4px solid
                        var(--success);
                    background:
                        rgba(
                            34,
                            197,
                            94,
                            0.05
                        );
                "
            >

                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color:
                            var(--success);
                    "
                >
                    ${positive}%
                </div>

                <div>
                    😊 Positive
                </div>

                <div
                    style="
                        font-size: 13px;
                        margin-top: 4px;
                        color:
                            var(--text-secondary);
                    "
                >
                    ${formatNumber(
                        positiveReviews
                    )}
                    reviews
                </div>

            </div>


            <div
                style="
                    padding: 16px;
                    border-radius: 10px;
                    border-left:
                        4px solid
                        var(--warning);
                    background:
                        rgba(
                            245,
                            158,
                            11,
                            0.05
                        );
                "
            >

                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color:
                            var(--warning);
                    "
                >
                    ${neutral}%
                </div>

                <div>
                    😐 Neutral
                </div>

                <div
                    style="
                        font-size: 13px;
                        margin-top: 4px;
                        color:
                            var(--text-secondary);
                    "
                >
                    ${formatNumber(
                        neutralReviews
                    )}
                    reviews
                </div>

            </div>


            <div
                style="
                    padding: 16px;
                    border-radius: 10px;
                    border-left:
                        4px solid
                        var(--danger);
                    background:
                        rgba(
                            239,
                            68,
                            68,
                            0.05
                        );
                "
            >

                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                        color:
                            var(--danger);
                    "
                >
                    ${negative}%
                </div>

                <div>
                    😞 Negative
                </div>

                <div
                    style="
                        font-size: 13px;
                        margin-top: 4px;
                        color:
                            var(--text-secondary);
                    "
                >
                    ${formatNumber(
                        negativeReviews
                    )}
                    reviews
                </div>

            </div>


            <div
                style="
                    padding: 16px;
                    border-radius: 10px;
                    background:
                        var(--surface-hover);
                "
            >

                <div
                    style="
                        font-size: 28px;
                        font-weight: 700;
                    "
                >
                    ${formatNumber(
                        total
                    )}
                </div>

                <div>
                    📝 Total Reviews
                </div>

                <div
                    style="
                        font-size: 13px;
                        margin-top: 4px;
                        color:
                            var(--text-secondary);
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
    },


    // ============================================================
    // EDA FINDINGS
    // ============================================================

    renderFindings(
        data
    ) {

        const container =
            document.getElementById(
                'edaFindings'
            );

        if (!container) {
            return;
        }


        const {
            stats,
            categories,
            municipalities,
            sentiment,
            destinations,
            topDestinations
        } = data;


        const findings = [];


        // --------------------------------------------------------
        // Finding 1 - Dataset
        // --------------------------------------------------------

        const totalDestinations =
            Number(
                stats?.total_destinations
            ) ||
            destinations.length ||
            0;


        findings.push({

            icon: '📌',

            title:
                'Dataset Overview',

            text:
                `The dataset contains approximately
                ${formatNumber(
                    totalDestinations
                )}
                tourism destinations.
                The analysis includes destination
                attributes, ratings, review counts,
                categories, and municipality information.`

        });


        // --------------------------------------------------------
        // Finding 2 - Category
        // --------------------------------------------------------

        if (
            Array.isArray(categories) &&
            categories.length > 0
        ) {

            const sortedCategories =
                [...categories]
                    .sort(
                        (a, b) =>
                            (
                                Number(b.count) || 0
                            ) -
                            (
                                Number(a.count) || 0
                            )
                    );


            const topCategory =
                sortedCategories[0];


            if (topCategory) {

                findings.push({

                    icon: '📊',

                    title:
                        'Category Distribution',

                    text:
                        `The category with the
                        largest number of destinations
                        is
                        "${topCategory.category ||
                            'Unknown'}"
                        with
                        ${formatNumber(
                            Number(
                                topCategory.count
                            ) || 0
                        )}
                        destinations.`

                });
            }
        }


        // --------------------------------------------------------
        // Finding 3 - Municipality
        // --------------------------------------------------------

        if (
            Array.isArray(municipalities) &&
            municipalities.length > 0
        ) {

            const sortedMunicipalities =
                [...municipalities]
                    .sort(
                        (a, b) =>
                            (
                                Number(b.count) || 0
                            ) -
                            (
                                Number(a.count) || 0
                            )
                    );


            const topMunicipality =
                sortedMunicipalities[0];


            if (topMunicipality) {

                findings.push({

                    icon: '🏛️',

                    title:
                        'Municipality Distribution',

                    text:
                        `The municipality with the
                        highest number of recorded
                        destinations is
                        "${topMunicipality.municipality ||
                            'Unknown'}"
                        with
                        ${formatNumber(
                            Number(
                                topMunicipality.count
                            ) || 0
                        )}
                        destinations.`

                });
            }
        }


        // --------------------------------------------------------
        // Finding 4 - Rating
        // --------------------------------------------------------

        const ratings =
            destinations
                .map(
                    item =>
                        Number(item.rating)
                )
                .filter(
                    value =>
                        Number.isFinite(value) &&
                        value > 0
                );


        if (ratings.length > 0) {

            const avgRating =
                ratings.reduce(
                    (sum, value) =>
                        sum + value,
                    0
                ) /
                ratings.length;


            findings.push({

                icon: '⭐',

                title:
                    'Rating Pattern',

                text:
                    `The average destination
                    rating in the available dataset
                    is
                    ${avgRating.toFixed(2)}
                    out of 5.`

            });
        }


        // --------------------------------------------------------
        // Finding 5 - Sentiment
        // --------------------------------------------------------

        if (sentiment) {

            const positive =
                Number(
                    sentiment.positive
                ) || 0;


            const neutral =
                Number(
                    sentiment.neutral
                ) || 0;


            const negative =
                Number(
                    sentiment.negative
                ) || 0;


            const dominant =
                Math.max(
                    positive,
                    neutral,
                    negative
                );


            let sentimentLabel =
                'Neutral';


            if (
                dominant === positive
            ) {

                sentimentLabel =
                    'Positive';

            } else if (
                dominant === negative
            ) {

                sentimentLabel =
                    'Negative';
            }


            findings.push({

                icon: '😊',

                title:
                    'Sentiment Pattern',

                text:
                    `The dominant sentiment
                    category is
                    ${sentimentLabel}.
                    Positive reviews represent
                    ${positive}%
                    of the analyzed review data,
                    while neutral and negative reviews
                    represent
                    ${neutral}%
                    and
                    ${negative}%
                    respectively.`

            });
        }


        // --------------------------------------------------------
        // Finding 6 - Review concentration
        // --------------------------------------------------------

        const sortedByReviews =
            [...destinations]
                .sort(
                    (a, b) =>
                        (
                            Number(
                                b.review_count
                            ) || 0
                        ) -
                        (
                            Number(
                                a.review_count
                            ) || 0
                        )
                );


        if (
            sortedByReviews.length > 0
        ) {

            const mostReviewed =
                sortedByReviews[0];


            findings.push({

                icon: '🏆',

                title:
                    'Review Concentration',

                text:
                    `"${mostReviewed.name ||
                        'Unknown Destination'}"
                    has the highest review count
                    in the destination dataset,
                    with approximately
                    ${formatNumber(
                        Number(
                            mostReviewed.review_count
                        ) || 0
                    )}
                    reviews.`

            });
        }


        // --------------------------------------------------------
        // Render
        // --------------------------------------------------------

        container.innerHTML =
            findings
                .map(
                    finding => `

                        <div
                            style="
                                display: grid;
                                grid-template-columns:
                                    42px
                                    minmax(0, 1fr);
                                gap: 12px;
                                padding: 14px 16px;
                                border:
                                    1px solid
                                    var(--border);
                                border-radius: 10px;
                                background:
                                    var(--surface);
                            "
                        >

                            <div
                                style="
                                    font-size: 22px;
                                    text-align: center;
                                "
                            >
                                ${finding.icon}
                            </div>


                            <div>

                                <div
                                    style="
                                        font-weight: 700;
                                        margin-bottom: 4px;
                                    "
                                >
                                    ${finding.title}
                                </div>


                                <div
                                    style="
                                        color:
                                            var(
                                                --text-secondary
                                            );
                                        line-height: 1.6;
                                        font-size: 14px;
                                    "
                                >
                                    ${finding.text}
                                </div>

                            </div>

                        </div>

                    `
                )
                .join('');
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