(function () {
    const dashboardLoading = document.getElementById("dashboard-loading");
    const dashboardError = document.getElementById("dashboard-error");
    const dashboardContent = document.getElementById("dashboard-content");
    const exportAlert = document.getElementById("export-alert");
    const datasetIndicator = document.getElementById("dataset-indicator");
    const currentDatetime = document.getElementById("current-datetime");
    const sidebar = document.getElementById("dashboard-sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarBackdrop = document.getElementById("sidebar-backdrop");
    const chartInstances = {};

    const chartColors = [
        "#a855f7",
        "#4f8cff",
        "#22d3ee",
        "#ec4899",
        "#22c55e",
        "#f59e0b",
        "#ef4444",
        "#8b5cf6",
    ];

    function formatNumber(value) {
        const numericValue = Number(value || 0);
        return numericValue.toLocaleString("en-IN", {
            maximumFractionDigits: 2,
        });
    }

    function setText(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    function animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        const target = Number(targetValue || 0);
        if (!element) {
            return;
        }

        const duration = 760;
        const start = performance.now();

        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            element.textContent = formatNumber(target * eased);

            if (progress < 1) {
                requestAnimationFrame(tick);
            } else {
                element.textContent = formatNumber(target);
            }
        }

        requestAnimationFrame(tick);
    }

    function badgeClass(value) {
        const normalized = String(value || "").toLowerCase().replace(/\s+/g, "-");
        if (normalized.includes("high") || normalized === "yes") {
            return "badge-high";
        }
        if (normalized.includes("medium")) {
            return "badge-medium";
        }
        if (normalized.includes("low") || normalized === "no") {
            return "badge-low";
        }
        return "mini-badge";
    }

    function labelBadge(value) {
        return `<span class="label-badge ${badgeClass(value)}">${value ?? "Unknown"}</span>`;
    }

    function showLoading(isLoading) {
        if (dashboardLoading) {
            dashboardLoading.classList.toggle("d-none", !isLoading);
        }
    }

    function showError(message) {
        if (!dashboardError || !dashboardContent) {
            return;
        }

        dashboardError.textContent = message;
        dashboardError.classList.remove("d-none");
        dashboardContent.classList.add("d-none");
    }

    function showDashboard() {
        if (dashboardError) {
            dashboardError.classList.add("d-none");
        }

        if (dashboardContent) {
            dashboardContent.classList.remove("d-none");
        }
    }

    function resizeCharts() {
        Object.values(chartInstances).forEach((chart) => chart.resize());
    }

    function showSection(sectionId) {
        document.querySelectorAll(".dashboard-section").forEach((section) => {
            section.classList.toggle("active", section.id === sectionId);
        });

        document.querySelectorAll(".sidebar-link").forEach((link) => {
            link.classList.toggle("active", link.dataset.section === sectionId);
        });

        document.getElementById(sectionId)?.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
        closeSidebar();
        window.setTimeout(resizeCharts, 80);
    }

    function attachSectionNavigation() {
        document.querySelectorAll(".sidebar-link").forEach((link) => {
            link.addEventListener("click", () => showSection(link.dataset.section));
        });
    }

    function openSidebar() {
        sidebar?.classList.add("open");
        sidebarBackdrop?.classList.add("show");
    }

    function closeSidebar() {
        sidebar?.classList.remove("open");
        sidebarBackdrop?.classList.remove("show");
    }

    function attachSidebarControls() {
        sidebarToggle?.addEventListener("click", openSidebar);
        sidebarBackdrop?.addEventListener("click", closeSidebar);
    }

    function updateCurrentDatetime() {
        if (!currentDatetime) {
            return;
        }

        currentDatetime.textContent = new Date().toLocaleString("en-IN", {
            dateStyle: "medium",
            timeStyle: "short",
        });
    }

    function updateDatasetIndicator(sourceFile) {
        if (!datasetIndicator) {
            return;
        }

        datasetIndicator.innerHTML = `<i class="bi bi-database-check"></i> ${sourceFile || "Dataset loaded"}`;
    }

    function showExportAlert(message, type) {
        if (!exportAlert) {
            return;
        }

        exportAlert.textContent = message;
        exportAlert.className = `alert alert-${type}`;
    }

    function getEntries(data = {}) {
        return Object.entries(data).filter(([, value]) => Number(value) > 0);
    }

    function destroyChart(chartId) {
        if (chartInstances[chartId]) {
            chartInstances[chartId].destroy();
            delete chartInstances[chartId];
        }
    }

    function renderChart(chartId, config) {
        const canvas = document.getElementById(chartId);
        if (!canvas || typeof Chart === "undefined") {
            return;
        }

        const context = canvas.getContext("2d");
        const gradient = context.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, "rgba(168, 85, 247, 0.88)");
        gradient.addColorStop(0.5, "rgba(79, 140, 255, 0.82)");
        gradient.addColorStop(1, "rgba(34, 211, 238, 0.78)");

        if (config.data?.datasets?.[0] && config.data.datasets[0].useGradient) {
            config.data.datasets[0].backgroundColor = gradient;
            config.data.datasets[0].borderColor = "#22d3ee";
        }

        destroyChart(chartId);
        chartInstances[chartId] = new Chart(canvas, config);
    }

    function renderEmptyChart(chartId, message) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            return;
        }

        destroyChart(chartId);
        const context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.font = "14px Arial";
        context.fillStyle = "#6c757d";
        context.textAlign = "center";
        context.fillText(message, canvas.width / 2, canvas.height / 2);
    }

    function pieChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 900,
                easing: "easeOutQuart",
            },
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 12,
                        color: "#dbeafe",
                        font: {
                            weight: "600",
                        },
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(15, 23, 42, 0.94)",
                    borderColor: "rgba(34, 211, 238, 0.35)",
                    borderWidth: 1,
                    titleColor: "#ffffff",
                    bodyColor: "#dbeafe",
                    padding: 12,
                    cornerRadius: 12,
                },
            },
        };
    }

    function lineChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 900,
                easing: "easeOutQuart",
            },
            plugins: {
                legend: {
                    labels: {
                        color: "#dbeafe",
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(15, 23, 42, 0.94)",
                    borderColor: "rgba(34, 211, 238, 0.35)",
                    borderWidth: 1,
                    titleColor: "#ffffff",
                    bodyColor: "#dbeafe",
                    padding: 12,
                    cornerRadius: 12,
                },
            },
            scales: {
                x: {
                    ticks: { color: "#a9b6cf" },
                    grid: { color: "rgba(255, 255, 255, 0.07)" },
                },
                y: {
                    min: 0,
                    max: 1,
                    ticks: { color: "#a9b6cf" },
                    grid: { color: "rgba(255, 255, 255, 0.07)" },
                },
            },
        };
    }

    function barChartOptions(indexAxis = "x") {
        return {
            indexAxis,
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 900,
                easing: "easeOutQuart",
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    backgroundColor: "rgba(15, 23, 42, 0.94)",
                    borderColor: "rgba(34, 211, 238, 0.35)",
                    borderWidth: 1,
                    titleColor: "#ffffff",
                    bodyColor: "#dbeafe",
                    padding: 12,
                    cornerRadius: 12,
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: "rgba(255, 255, 255, 0.07)" },
                    ticks: {
                        color: "#a9b6cf",
                        precision: 0,
                    },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: {
                        color: "#a9b6cf",
                    },
                },
            },
        };
    }

    function renderDistributionChart(chartId, distribution, type, label, emptyMessage) {
        const entries = getEntries(distribution);
        if (!entries.length) {
            renderEmptyChart(chartId, emptyMessage);
            return;
        }

        const labels = entries.map(([name]) => name);
        const values = entries.map(([, count]) => Number(count));
        const isCircular = type === "pie" || type === "doughnut";

        renderChart(chartId, {
            type: type === "doughnut" ? "doughnut" : type,
            data: {
                labels,
                datasets: [
                    {
                        label,
                        data: values,
                        backgroundColor: labels.map((_, index) => chartColors[index % chartColors.length]),
                        borderColor: "rgba(255, 255, 255, 0.82)",
                        borderWidth: isCircular ? 2 : 0,
                        borderRadius: isCircular ? 0 : 10,
                        useGradient: !isCircular,
                    },
                ],
            },
            options: isCircular ? pieChartOptions() : barChartOptions("y"),
        });
    }

    function renderTopCustomersChart(customers = []) {
        const topCustomers = customers
            .filter((customer) => Number(customer.total_spending) > 0)
            .slice(0, 5);

        if (!topCustomers.length) {
            renderEmptyChart("top-customers-chart", "No spending data available.");
            return;
        }

        renderChart("top-customers-chart", {
            type: "bar",
            data: {
                labels: topCustomers.map((customer) => customer.customer_id || "Unknown"),
                datasets: [
                    {
                        label: "Total Spending",
                        data: topCustomers.map((customer) => Number(customer.total_spending || 0)),
                        backgroundColor: "#4f8cff",
                        borderRadius: 12,
                        useGradient: true,
                    },
                ],
            },
            options: barChartOptions("y"),
        });
    }

    function countBy(items, key) {
        return items.reduce((counts, item) => {
            const value = item[key] || "Unknown";
            counts[value] = (counts[value] || 0) + 1;
            return counts;
        }, {});
    }

    function renderPredictionChart(predictions = []) {
        const rows = predictions.slice(0, 12);
        if (!rows.length) {
            renderEmptyChart("predictions-chart", "No prediction results available.");
            return;
        }

        renderChart("predictions-chart", {
            type: "line",
            data: {
                labels: rows.map((prediction) => prediction.customer_id || "Unknown"),
                datasets: [
                    {
                        label: "Purchase Probability",
                        data: rows.map((prediction) => Number(prediction.prediction_probability || 0)),
                        borderColor: "#22d3ee",
                        backgroundColor: "rgba(34, 211, 238, 0.18)",
                        pointBackgroundColor: "#a855f7",
                        pointBorderColor: "#ffffff",
                        pointRadius: 5,
                        tension: 0.38,
                        fill: true,
                    },
                ],
            },
            options: lineChartOptions(),
        });
    }

    function renderRecommendationPriorityChart(recommendations = []) {
        const counts = countBy(recommendations, "priority");
        renderDistributionChart(
            "recommendations-chart",
            counts,
            "bar",
            "Customers",
            "No recommendation priorities available."
        );
    }

    function renderKeyMetrics(statistics = {}) {
        animateNumber("kpi-total-customers", statistics.total_customers);
        animateNumber("kpi-total-spending", statistics.total_spending);
        animateNumber("kpi-average-spending", statistics.average_spending);
        animateNumber("kpi-average-frequency", statistics.average_purchase_frequency);
    }

    function renderDistributionTable(tableBodyId, distribution, emptyLabel) {
        const tableBody = document.getElementById(tableBodyId);
        if (!tableBody) {
            return;
        }

        const entries = Object.entries(distribution || {});
        if (entries.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="2" class="text-muted">${emptyLabel}</td></tr>`;
            return;
        }

        tableBody.innerHTML = entries
            .map(([label, count]) => `
                <tr>
                    <td>${label}</td>
                    <td class="text-end">${formatNumber(count)}</td>
                </tr>
            `)
            .join("");
    }

    function renderTopCustomers(customers = []) {
        const tableBody = document.getElementById("top-customers-table-body");
        if (!tableBody) {
            return;
        }

        if (!customers.length) {
            tableBody.innerHTML = '<tr><td colspan="3" class="text-muted">No top customer data available.</td></tr>';
            return;
        }

        tableBody.innerHTML = customers
            .map((customer) => `
                <tr>
                    <td>${customer.customer_id ?? "Unknown"}</td>
                    <td class="text-end">${formatNumber(customer.total_spending)}</td>
                    <td>${customer.preferred_category ?? "Unknown"}</td>
                </tr>
            `)
            .join("");
    }

    function renderMissingValues(missingValues = {}) {
        const tableBody = document.getElementById("missing-values-table-body");
        if (!tableBody) {
            return;
        }

        const entries = Object.entries(missingValues);
        if (entries.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="2" class="text-muted">No missing-value summary available.</td></tr>';
            return;
        }

        tableBody.innerHTML = entries
            .map(([column, count]) => `
                <tr>
                    <td>${column}</td>
                    <td class="text-end">${formatNumber(count)}</td>
                </tr>
            `)
            .join("");
    }

    function renderSegments(segments = []) {
        const tableBody = document.getElementById("segments-table-body");
        const status = document.getElementById("segment-status");
        if (!tableBody) {
            return;
        }

        if (!segments.length) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-muted">No segment data available.</td></tr>';
            renderEmptyChart("segments-chart", "No segment data available.");
            if (status) {
                status.textContent = "No segments";
            }
            return;
        }

        renderDistributionChart(
            "segments-chart",
            countBy(segments, "segment"),
            "doughnut",
            "Customers",
            "No segment data available."
        );

        tableBody.innerHTML = segments
            .slice(0, 10)
            .map((customer) => `
                <tr>
                    <td>${customer.customer_id ?? "Unknown"}</td>
                    <td>${labelBadge(customer.segment ?? "Unknown")}</td>
                    <td class="text-end">${formatNumber(customer.total_spending)}</td>
                    <td class="text-end">${formatNumber(customer.purchase_frequency)}</td>
                    <td class="text-end">${formatNumber(customer.age)}</td>
                </tr>
            `)
            .join("");

        if (status) {
            status.textContent = `Showing ${Math.min(segments.length, 10)} of ${segments.length}`;
        }
    }

    async function loadCustomerSegments() {
        const tableBody = document.getElementById("segments-table-body");
        const status = document.getElementById("segment-status");
        if (!tableBody) {
            return;
        }

        try {
            const response = await fetch("/segment");
            const result = await response.json();

            if (!response.ok || !result.success) {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-muted">${result.error || "Unable to load segments."}</td></tr>`;
                renderEmptyChart("segments-chart", "Segments unavailable.");
                if (status) {
                    status.textContent = "Unavailable";
                }
                return;
            }

            renderSegments(result.segmentation?.segments || []);
        } catch (error) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-muted">Unable to load segments: ${error.message}</td></tr>`;
            renderEmptyChart("segments-chart", "Segments unavailable.");
            if (status) {
                status.textContent = "Error";
            }
        }
    }

    function renderPredictions(predictions = []) {
        const tableBody = document.getElementById("predictions-table-body");
        const status = document.getElementById("prediction-status");
        if (!tableBody) {
            return;
        }

        if (!predictions.length) {
            tableBody.innerHTML = '<tr><td colspan="3" class="text-muted">No prediction data available.</td></tr>';
            renderEmptyChart("predictions-chart", "No prediction results available.");
            if (status) {
                status.textContent = "No predictions";
            }
            return;
        }

        renderPredictionChart(predictions);

        tableBody.innerHTML = predictions
            .slice(0, 10)
            .map((prediction) => `
                <tr>
                    <td>${prediction.customer_id ?? "Unknown"}</td>
                    <td>${labelBadge(prediction.predicted_purchase ?? "Unknown")}</td>
                    <td class="text-end">${formatNumber(prediction.prediction_probability)}</td>
                </tr>
            `)
            .join("");

        if (status) {
            status.textContent = `Showing ${Math.min(predictions.length, 10)} of ${predictions.length}`;
        }
    }

    async function loadPurchasePredictions() {
        const tableBody = document.getElementById("predictions-table-body");
        const status = document.getElementById("prediction-status");
        if (!tableBody) {
            return;
        }

        try {
            const response = await fetch("/predict");
            const result = await response.json();

            if (!response.ok || !result.success) {
                tableBody.innerHTML = `<tr><td colspan="3" class="text-muted">${result.error || "Unable to load predictions."}</td></tr>`;
                renderEmptyChart("predictions-chart", "Predictions unavailable.");
                if (status) {
                    status.textContent = "Unavailable";
                }
                return;
            }

            renderPredictions(result.prediction?.predictions || []);
        } catch (error) {
            tableBody.innerHTML = `<tr><td colspan="3" class="text-muted">Unable to load predictions: ${error.message}</td></tr>`;
            renderEmptyChart("predictions-chart", "Predictions unavailable.");
            if (status) {
                status.textContent = "Error";
            }
        }
    }

    function renderRecommendations(recommendations = []) {
        const tableBody = document.getElementById("recommendations-table-body");
        const status = document.getElementById("recommendation-status");
        if (!tableBody) {
            return;
        }

        if (!recommendations.length) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-muted">No recommendation data available.</td></tr>';
            renderEmptyChart("recommendations-chart", "No recommendation priorities available.");
            if (status) {
                status.textContent = "No recommendations";
            }
            return;
        }

        renderRecommendationPriorityChart(recommendations);

        tableBody.innerHTML = recommendations
            .slice(0, 10)
            .map((recommendation) => `
                <tr>
                <td>${recommendation.customer_id ?? "Unknown"}</td>
                <td>${recommendation.recommendation ?? "General engagement campaign"}</td>
                <td>${recommendation.recommended_category ?? "General"}</td>
                <td>${labelBadge(recommendation.priority ?? "Low")}</td>
                </tr>
            `)
            .join("");

        if (status) {
            status.textContent = `Showing ${Math.min(recommendations.length, 10)} of ${recommendations.length}`;
        }
    }

    async function loadCustomerRecommendations() {
        const tableBody = document.getElementById("recommendations-table-body");
        const status = document.getElementById("recommendation-status");
        if (!tableBody) {
            return;
        }

        try {
            const response = await fetch("/recommend");
            const result = await response.json();

            if (!response.ok || !result.success) {
                tableBody.innerHTML = `<tr><td colspan="4" class="text-muted">${result.error || "Unable to load recommendations."}</td></tr>`;
                renderEmptyChart("recommendations-chart", "Recommendations unavailable.");
                if (status) {
                    status.textContent = "Unavailable";
                }
                return;
            }

            renderRecommendations(result.recommendations?.customers || []);
        } catch (error) {
            tableBody.innerHTML = `<tr><td colspan="4" class="text-muted">Unable to load recommendations: ${error.message}</td></tr>`;
            renderEmptyChart("recommendations-chart", "Recommendations unavailable.");
            if (status) {
                status.textContent = "Error";
            }
        }
    }

    async function runExport(endpoint, button) {
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = "Exporting...";

        try {
            const response = await fetch(endpoint);
            const result = await response.json();

            if (!response.ok || !result.success) {
                showExportAlert(result.error || "Export failed.", "danger");
                return;
            }

            showExportAlert(
                `Export created: ${result.export.filename}`,
                "success"
            );
        } catch (error) {
            showExportAlert(`Export failed: ${error.message}`, "danger");
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    function attachExportHandlers() {
        const jsonButton = document.getElementById("export-json-button");
        const excelButton = document.getElementById("export-excel-button");

        if (jsonButton) {
            jsonButton.addEventListener("click", () => runExport("/export/json", jsonButton));
        }

        if (excelButton) {
            excelButton.addEventListener("click", () => runExport("/export/excel", excelButton));
        }
    }

    function renderAnalytics(analytics) {
        if (!analytics) {
            showError("Analytics data is empty. Upload a valid dataset first.");
            return;
        }

        showDashboard();
        renderKeyMetrics(analytics.basic_statistics);
        renderDistributionChart(
            "category-chart",
            analytics.category_distribution,
            "pie",
            "Customers",
            "No category data available."
        );
        renderDistributionChart(
            "location-chart",
            analytics.location_distribution,
            "bar",
            "Customers",
            "No location data available."
        );
        renderTopCustomersChart(analytics.top_customers);
        renderDistributionTable(
            "category-table-body",
            analytics.category_distribution,
            "No category data available."
        );
        renderDistributionTable(
            "location-table-body",
            analytics.location_distribution,
            "No location data available."
        );
        renderTopCustomers(analytics.top_customers);
        renderMissingValues(analytics.missing_values);
    }

    async function loadDashboardAnalytics() {
        if (!dashboardContent) {
            return;
        }

        showLoading(true);

        try {
            const response = await fetch("/analyze");
            const result = await response.json();

            if (!response.ok || !result.success) {
                showError(result.error || "Unable to load analytics.");
                return;
            }

            updateDatasetIndicator(result.source_file);
            renderAnalytics(result.analytics);
        } catch (error) {
            showError(`Unable to load analytics: ${error.message}`);
        } finally {
            showLoading(false);
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        attachSidebarControls();
        attachSectionNavigation();
        attachExportHandlers();
        updateCurrentDatetime();
        window.setInterval(updateCurrentDatetime, 60000);
        loadDashboardAnalytics();
        loadCustomerSegments();
        loadPurchasePredictions();
        loadCustomerRecommendations();
    });
})();
