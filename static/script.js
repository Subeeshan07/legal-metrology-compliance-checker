/**
 * Legal Metrology Packaged Commodity Compliance Checker
 * Frontend Controller & Chart.js Integration
 * 
 * Target: Smart India Hackathon
 */

// Global State
let complianceDoughnutChart = null;
let violationsBarChart = null;

let currentScannedData = null;
let historyCurrentPage = 1;
const historyPageSize = 15;
let searchDebounceTimer = null;

// --------------------------------------------------------------------------
// Initialization & Tab Navigation
// --------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    initDropzone();
    loadDashboardStats();
    loadRecentScans();
    loadHistoryData();
    loadLegalRules();
});

function switchTab(tabId) {
    // Update nav tab buttons
    document.querySelectorAll(".nav-tab").forEach(tab => {
        if (tab.getAttribute("data-tab") === tabId) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });

    // Update tab panes
    document.querySelectorAll(".tab-pane").forEach(pane => {
        if (pane.id === `tab-${tabId}`) {
            pane.classList.add("active");
        } else {
            pane.classList.remove("active");
        }
    });

    // Refresh charts if dashboard selected
    if (tabId === "dashboard") {
        loadDashboardStats();
        loadRecentScans();
    } else if (tabId === "history") {
        loadHistoryData();
    }
}

// --------------------------------------------------------------------------
// Dashboard & Charts
// --------------------------------------------------------------------------
async function loadDashboardStats() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();

        // Update Counters
        document.getElementById("stat-total").innerText = Number(data.total_products).toLocaleString();
        document.getElementById("stat-compliant").innerText = Number(data.compliant).toLocaleString();
        document.getElementById("stat-non-compliant").innerText = Number(data.non_compliant).toLocaleString();
        document.getElementById("stat-review").innerText = Number(data.needs_review).toLocaleString();

        const total = data.total_products || 1;
        document.getElementById("stat-compliant-pct").innerText = `${((data.compliant / total) * 100).toFixed(1)}% full conformity`;
        document.getElementById("stat-non-compliant-pct").innerText = `${((data.non_compliant / total) * 100).toFixed(1)}% statutory violations`;
        document.getElementById("stat-review-pct").innerText = `${((data.needs_review / total) * 100).toFixed(1)}% non-standard / partial`;

        // Render Doughnut Chart
        renderComplianceDoughnut(data.compliance_distribution);

        // Render Violations Bar Chart
        renderViolationsBarChart(data.top_violations);

    } catch (err) {
        console.error("Error loading dashboard metrics:", err);
    }
}

function renderComplianceDoughnut(dist) {
    const ctx = document.getElementById("complianceDoughnutChart").getContext("2d");
    const labels = ["Compliant", "Non-Compliant", "Needs Review"];
    const values = [dist["Compliant"] || 0, dist["Non-Compliant"] || 0, dist["Needs Review"] || 0];
    const colors = ["#10b981", "#ef4444", "#f59e0b"];

    if (complianceDoughnutChart) {
        complianceDoughnutChart.data.datasets[0].data = values;
        complianceDoughnutChart.update();
    } else {
        complianceDoughnutChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: "#ffffff",
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const val = context.parsed;
                                const pct = ((val / total) * 100).toFixed(1);
                                return ` ${context.label}: ${val} (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: "70%"
            }
        });
    }

    // Custom Legend
    const legendContainer = document.getElementById("doughnut-legend");
    legendContainer.innerHTML = labels.map((label, idx) => `
        <div class="legend-item">
            <span class="legend-color" style="background-color: ${colors[idx]}"></span>
            <span>${label}: <strong>${values[idx]}</strong></span>
        </div>
    `).join("");
}

function renderViolationsBarChart(violationsObj) {
    const ctx = document.getElementById("violationsBarChart").getContext("2d");
    const labels = Object.keys(violationsObj);
    const dataValues = Object.values(violationsObj);

    if (violationsBarChart) {
        violationsBarChart.data.labels = labels;
        violationsBarChart.data.datasets[0].data = dataValues;
        violationsBarChart.update();
    } else {
        violationsBarChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Violations Recorded",
                    data: dataValues,
                    backgroundColor: "#3b82f6",
                    hoverBackgroundColor: "#1d4ed8",
                    borderRadius: 6,
                    maxBarThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Occurrences: ${ctx.parsed.x} products`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "#f1f5f9" },
                        ticks: { font: { size: 11 } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { font: { size: 11, weight: "500" } }
                    }
                }
            }
        });
    }
}

async function loadRecentScans() {
    try {
        const res = await fetch("/api/products?limit=5&offset=0");
        const data = await res.json();
        const tbody = document.getElementById("recent-scans-body");
        tbody.innerHTML = "";

        if (!data.products || data.products.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No surveillance records available.</td></tr>`;
            return;
        }

        data.products.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${p.id}</strong></td>
                <td>${escapeHtml(p.product_name)}</td>
                <td><span class="badge-soft">${escapeHtml(p.category || 'Food')}</span></td>
                <td>${escapeHtml(p.net_quantity)}</td>
                <td>${escapeHtml(p.mrp)}</td>
                <td>${formatStatusPill(p.compliance_status)}</td>
                <td style="max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(p.violations)}">${escapeHtml(p.violations)}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick='viewProductAuditSheet(${JSON.stringify(p).replace(/'/g, "&apos;")})'>
                        <i class="fa-solid fa-file-invoice"></i> Audit
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading recent scans:", err);
    }
}

// --------------------------------------------------------------------------
// Product Scanner: Dropzone, Image Upload & Presets
// --------------------------------------------------------------------------
let selectedFile = null;
let currentSampleId = null;

function initDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("label-image-input");
    const removeBtn = document.getElementById("btn-remove-img");

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    removeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        resetImageUpload();
    });
}

function handleSelectedFile(file) {
    selectedFile = file;
    currentSampleId = null;
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById("image-preview").src = e.target.result;
        document.getElementById("dropzone-content").classList.add("hidden");
        document.getElementById("preview-wrapper").classList.remove("hidden");
        document.getElementById("ocr-source-tag").innerText = `Image: ${file.name}`;
    };
    reader.readAsDataURL(file);
    showToast("Product label image loaded. Click 'Analyze Declarations' to extract OCR text and verify.", "info");
}

function resetImageUpload() {
    selectedFile = null;
    currentSampleId = null;
    document.getElementById("label-image-input").value = "";
    document.getElementById("image-preview").src = "";
    document.getElementById("preview-wrapper").classList.add("hidden");
    document.getElementById("dropzone-content").classList.remove("hidden");
    document.getElementById("ocr-source-tag").innerText = "Source: Ready";
}

function loadSample(sampleType) {
    currentSampleId = sampleType;
    selectedFile = null;

    const sampleImages = {
        "compliant": "/static/samples/sample_compliant_atta.png",
        "non_compliant": "/static/samples/sample_non_compliant_chips.png",
        "needs_review": "/static/samples/sample_needs_review_spice.png"
    };

    document.getElementById("image-preview").src = sampleImages[sampleType] || "";
    document.getElementById("dropzone-content").classList.add("hidden");
    document.getElementById("preview-wrapper").classList.remove("hidden");
    document.getElementById("ocr-source-tag").innerText = `Preset: ${sampleType.toUpperCase()}`;

    // Auto-trigger analysis for seamless testing
    runAnalysis();
}

async function runAnalysis() {
    const rawText = document.getElementById("raw-ocr-text").value.trim();

    if (!selectedFile && !currentSampleId && !rawText) {
        showToast("Please select a sample preset, upload a label image, or enter OCR text to analyze.", "warning");
        return;
    }

    const btn = document.getElementById("btn-analyze");
    const originalBtnHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Performing OCR & Verification...`;

    try {
        const formData = new FormData();
        if (selectedFile) {
            formData.append("label_image", selectedFile);
        }
        if (currentSampleId) {
            formData.append("sample_id", currentSampleId);
        }
        if (rawText) {
            formData.append("manual_text", rawText);
        }

        const response = await fetch("/api/scan", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            currentScannedData = data;
            displayScanResults(data);
            showToast(`Analysis completed: Verdict is ${data.compliance.overall_status}`, data.compliance.overall_status === "COMPLIANT" ? "success" : "danger");
        } else {
            showToast(data.error || "Analysis failed.", "danger");
        }

    } catch (err) {
        console.error("Scan error:", err);
        showToast("Error processing label image. " + err.message, "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalBtnHtml;
    }
}

function displayScanResults(data) {
    document.getElementById("scanner-placeholder").classList.add("hidden");
    document.getElementById("scanner-results").classList.remove("hidden");

    // Populate raw OCR text if not manually typed
    document.getElementById("raw-ocr-text").value = data.ocr_text || "";
    if (data.ocr_source) {
        document.getElementById("ocr-source-tag").innerText = `Source: ${data.ocr_source}`;
    }

    // 1. Overall Status Banner
    const status = data.compliance.overall_status;
    const banner = document.getElementById("status-banner");
    const bannerIcon = document.getElementById("banner-icon");
    const bannerTitle = document.getElementById("banner-status-text");
    const bannerSub = document.getElementById("banner-subtext");

    banner.className = "status-banner";
    if (status === "COMPLIANT") {
        banner.classList.add("banner-compliant");
        bannerIcon.innerHTML = `<i class="fa-solid fa-circle-check"></i>`;
        bannerTitle.innerText = "COMPLIANT";
        bannerSub.innerText = "All mandatory packaged commodity declarations conform with Legal Metrology (Packaged Commodities) Rules, 2011.";
    } else if (status === "NON-COMPLIANT") {
        banner.classList.add("banner-non-compliant");
        bannerIcon.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i>`;
        bannerTitle.innerText = "NON-COMPLIANT";
        bannerSub.innerText = `Detected ${data.compliance.violations.length} statutory violation(s) under Legal Metrology Rules, 2011.`;
    } else {
        banner.classList.add("banner-review");
        bannerIcon.innerHTML = `<i class="fa-solid fa-eye"></i>`;
        bannerTitle.innerText = "NEEDS REVIEW";
        bannerSub.innerText = "Declarations detected with non-standard units, incomplete address, or potential ambiguity.";
    }

    // 2. Extracted Declarations Grid
    const ent = data.extracted_entities || {};
    const grid = document.getElementById("declarations-grid");
    
    const fields = [
        { label: "Generic Product Name", val: ent.product_name, rule: "Rule 6(1)(b)" },
        { label: "Net Quantity", val: ent.net_quantity, rule: "Rule 6(1)(c)" },
        { label: "Maximum Retail Price (MRP)", val: ent.mrp, rule: "Rule 6(1)(da)" },
        { label: "Date of Mfg / Packing", val: ent.mfg_date, rule: "Rule 6(1)(d)" },
        { label: "Manufacturer / Packer", val: ent.manufacturer, rule: "Rule 6(1)(a)" },
        { label: "Consumer Care Contact", val: ent.consumer_care, rule: "Rule 6(1)(e)" },
        { label: "Country of Origin", val: ent.country_of_origin, rule: "Rule 6(1)(n)" }
    ];

    grid.innerHTML = fields.map(f => {
        const hasVal = f.val && f.val.trim().length > 0 && f.val.toLowerCase() !== "not declared";
        return `
            <div class="declaration-item">
                <div class="dec-header">
                    <span class="dec-title">${escapeHtml(f.label)}</span>
                    <span class="badge-soft">${f.rule}</span>
                </div>
                <div class="dec-value ${hasVal ? '' : 'text-danger'}">
                    ${hasVal ? escapeHtml(f.val) : '<i class="fa-solid fa-circle-xmark"></i> Not Declared / Undetected'}
                </div>
            </div>
        `;
    }).join("");

    // 3. Rule-by-Rule Checklist
    const checklist = document.getElementById("rules-checklist");
    checklist.innerHTML = (data.compliance.checks || []).map(c => {
        let cls = "rule-pass";
        let icon = `<i class="fa-solid fa-circle-check"></i>`;
        let tagCls = "text-success";

        if (c.status === "FAIL") {
            cls = "rule-fail";
            icon = `<i class="fa-solid fa-circle-xmark"></i>`;
            tagCls = "text-danger";
        } else if (c.status === "WARNING") {
            cls = "rule-warning";
            icon = `<i class="fa-solid fa-triangle-exclamation"></i>`;
            tagCls = "text-warning";
        }

        return `
            <div class="rule-item ${cls}">
                <div class="rule-status-icon">${icon}</div>
                <div class="rule-content">
                    <div class="rule-head">
                        <span class="rule-tag ${tagCls}">${escapeHtml(c.rule)}: ${escapeHtml(c.title)}</span>
                        <span class="badge-soft">${c.status}</span>
                    </div>
                    <p class="rule-msg">${escapeHtml(c.message)}</p>
                    <p class="rule-rec"><i class="fa-solid fa-arrow-right"></i> ${escapeHtml(c.recommendation)}</p>
                </div>
            </div>
        `;
    }).join("");
}

function resetScanner() {
    resetImageUpload();
    document.getElementById("raw-ocr-text").value = "";
    document.getElementById("scanner-results").classList.add("hidden");
    document.getElementById("scanner-placeholder").classList.remove("hidden");
    currentScannedData = null;
    showToast("Scanner reset.", "info");
}

async function saveCurrentScan() {
    if (!currentScannedData) {
        showToast("No active scan data to save.", "warning");
        return;
    }

    const ent = currentScannedData.extracted_entities || {};
    const comp = currentScannedData.compliance || {};

    const payload = {
        product_name: ent.product_name || "Scanned Packaged Commodity",
        category: "Packaged Food",
        manufacturer: ent.manufacturer || "Not Declared",
        net_quantity: ent.net_quantity || "Not Declared",
        mrp: ent.mrp || "Not Declared",
        mfg_date: ent.mfg_date || "Not Declared",
        consumer_care: ent.consumer_care || "Not Declared",
        country_of_origin: ent.country_of_origin || "Not Declared",
        compliance_status: comp.overall_status || "NEEDS REVIEW",
        violations: comp.violations_summary || "None",
        ocr_confidence: "96%"
    };

    try {
        const btn = document.getElementById("btn-save-record");
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Saving...`;

        const res = await fetch("/api/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const resData = await res.json();

        if (resData.success) {
            showToast(`Product recorded successfully with ID: ${resData.record.id}`, "success");
            loadDashboardStats();
            loadRecentScans();
            loadHistoryData();
        } else {
            showToast("Failed to save product record.", "danger");
        }
    } catch (e) {
        console.error("Save error:", e);
        showToast("Error saving record.", "danger");
    } finally {
        const btn = document.getElementById("btn-save-record");
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> Saved to Records`;
    }
}

// --------------------------------------------------------------------------
// Product History & Surveillance Database
// --------------------------------------------------------------------------
async function loadHistoryData() {
    const searchVal = document.getElementById("history-search").value.trim();
    const statusVal = document.getElementById("history-status-filter").value;
    const catVal = document.getElementById("history-category-filter").value;

    const offset = (historyCurrentPage - 1) * historyPageSize;
    let url = `/api/products?limit=${historyPageSize}&offset=${offset}`;

    if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;
    if (statusVal && statusVal !== "ALL") url += `&status=${encodeURIComponent(statusVal)}`;
    if (catVal && catVal !== "ALL") url += `&category=${encodeURIComponent(catVal)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        renderHistoryTable(data.products || []);
        updateHistoryPagination(data.total || 0);

    } catch (err) {
        console.error("Error loading history:", err);
    }
}

function renderHistoryTable(products) {
    const tbody = document.getElementById("history-tbody");
    tbody.innerHTML = "";

    if (products.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-muted">No matching packaged commodities found.</td></tr>`;
        return;
    }

    products.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${p.id}</strong></td>
            <td>
                <div style="font-weight:600;">${escapeHtml(p.product_name)}</div>
                <div style="font-size:11px; color:var(--text-muted);">${escapeHtml(p.manufacturer)}</div>
            </td>
            <td><span class="badge-soft">${escapeHtml(p.category || 'Food')}</span></td>
            <td>${escapeHtml(p.net_quantity)}</td>
            <td>${escapeHtml(p.mrp)}</td>
            <td>${escapeHtml(p.mfg_date)}</td>
            <td>${formatStatusPill(p.compliance_status)}</td>
            <td style="max-width:240px; font-size:12px;" title="${escapeHtml(p.violations)}">
                ${escapeHtml(p.violations)}
            </td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick='viewProductAuditSheet(${JSON.stringify(p).replace(/'/g, "&apos;")})'>
                    <i class="fa-solid fa-file-invoice"></i> Audit
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function updateHistoryPagination(total) {
    const totalPages = Math.ceil(total / historyPageSize) || 1;
    const startIdx = total === 0 ? 0 : (historyCurrentPage - 1) * historyPageSize + 1;
    const endIdx = Math.min(historyCurrentPage * historyPageSize, total);

    document.getElementById("pagination-summary").innerText = `Showing ${startIdx}-${endIdx} of ${total} products`;
    document.getElementById("current-page-num").innerText = `Page ${historyCurrentPage} of ${totalPages}`;

    document.getElementById("btn-prev").disabled = historyCurrentPage <= 1;
    document.getElementById("btn-next").disabled = historyCurrentPage >= totalPages;
}

function changePage(delta) {
    historyCurrentPage += delta;
    if (historyCurrentPage < 1) historyCurrentPage = 1;
    loadHistoryData();
}

function debounceSearch() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        historyCurrentPage = 1;
        loadHistoryData();
    }, 300);
}

function exportFilteredCSV() {
    const searchVal = document.getElementById("history-search").value.trim();
    const statusVal = document.getElementById("history-status-filter").value;
    const catVal = document.getElementById("history-category-filter").value;

    let exportUrl = `/api/products?limit=2000&offset=0`;
    if (searchVal) exportUrl += `&search=${encodeURIComponent(searchVal)}`;
    if (statusVal && statusVal !== "ALL") exportUrl += `&status=${encodeURIComponent(statusVal)}`;
    if (catVal && catVal !== "ALL") exportUrl += `&category=${encodeURIComponent(catVal)}`;

    fetch(exportUrl)
        .then(res => res.json())
        .then(data => {
            if (!data.products || data.products.length === 0) {
                showToast("No data to export.", "warning");
                return;
            }
            const headers = ["id", "product_name", "category", "manufacturer", "net_quantity", "mrp", "mfg_date", "consumer_care", "country_of_origin", "compliance_status", "violations"];
            const csvRows = [headers.join(",")];

            data.products.forEach(p => {
                const row = headers.map(h => `"${String(p[h] || '').replace(/"/g, '""')}"`);
                csvRows.push(row.join(","));
            });

            const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `legal_metrology_surveillance_export_${Date.now()}.csv`;
            link.click();
            showToast("CSV dataset exported successfully.", "success");
        });
}

// --------------------------------------------------------------------------
// Legal Metrology Rules Reference Tab
// --------------------------------------------------------------------------
async function loadLegalRules() {
    try {
        const res = await fetch("/api/rules");
        const data = await res.json();
        const grid = document.getElementById("rules-cards-grid");

        grid.innerHTML = (data.rules || []).map(r => `
            <div class="rule-ref-card">
                <span class="rule-ref-num">${escapeHtml(r.rule)}</span>
                <h4 class="rule-ref-title">${escapeHtml(r.title)}</h4>
                <p class="rule-ref-desc">${escapeHtml(r.description)}</p>
                <div class="rule-ref-penalty">
                    <strong><i class="fa-solid fa-triangle-exclamation"></i> Penalty:</strong> ${escapeHtml(r.penalty)}
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Error loading legal rules reference:", err);
    }
}

// --------------------------------------------------------------------------
// Audit Certificate / Printable Modal
// --------------------------------------------------------------------------
function viewProductAuditSheet(product) {
    document.getElementById("report-ref-id").innerText = product.id || "LMC-AUDIT";
    document.getElementById("rep-date").innerText = product.scanned_timestamp || new Date().toLocaleString();

    const status = product.compliance_status || "NEEDS REVIEW";
    const verdictBox = document.getElementById("rep-verdict-box");
    const verdictTag = document.getElementById("rep-verdict-tag");
    const verdictDesc = document.getElementById("rep-verdict-desc");

    verdictBox.className = "report-verdict-box";
    if (status === "COMPLIANT") {
        verdictBox.classList.add("verdict-compliant");
        verdictTag.innerText = "COMPLIANT";
        verdictDesc.innerText = "The packaged commodity satisfies all mandatory statutory declarations under PCR 2011.";
    } else if (status === "NON-COMPLIANT") {
        verdictBox.classList.add("verdict-non-compliant");
        verdictTag.innerText = "NON-COMPLIANT";
        verdictDesc.innerText = "Critical mandatory declarations missing or in violation of statutory rules.";
    } else {
        verdictBox.classList.add("verdict-review");
        verdictTag.innerText = "NEEDS REVIEW";
        verdictDesc.innerText = "Non-standard units or incomplete details requiring secondary manual inspection.";
    }

    // Populate attributes
    document.getElementById("rep-name").innerText = product.product_name || "--";
    document.getElementById("rep-mfr").innerText = product.manufacturer || "--";
    document.getElementById("rep-qty").innerText = product.net_quantity || "--";
    document.getElementById("rep-mrp").innerText = product.mrp || "--";
    document.getElementById("rep-mfg").innerText = product.mfg_date || "--";
    document.getElementById("rep-cc").innerText = product.consumer_care || "--";
    document.getElementById("rep-origin").innerText = product.country_of_origin || "--";

    // Build checklist table
    const tbody = document.getElementById("rep-rules-tbody");
    const violations = product.violations || "";

    const standardChecks = [
        { rule: "Rule 6(1)(a)", title: "Manufacturer/Packer Name & Address" },
        { rule: "Rule 6(1)(b)", title: "Common/Generic Name of Commodity" },
        { rule: "Rule 6(1)(c)", title: "Net Quantity & Standard Units" },
        { rule: "Rule 6(1)(d)", title: "Month & Year of Mfg/Packing" },
        { rule: "Rule 6(1)(da)", title: "Retail Sale Price (MRP incl. of taxes)" },
        { rule: "Rule 6(1)(e)", title: "Consumer Care Grievance Details" },
        { rule: "Rule 6(1)(n)", title: "Country of Origin Declaration" }
    ];

    tbody.innerHTML = standardChecks.map(item => {
        const isViolated = violations.includes(item.rule);
        const st = isViolated ? (status === "NON-COMPLIANT" ? "FAIL" : "WARNING") : "PASS";
        const badge = st === "PASS" ? '<span class="status-pill pill-compliant">PASS</span>' :
                      st === "FAIL" ? '<span class="status-pill pill-non-compliant">VIOLATION</span>' :
                      '<span class="status-pill pill-review">WARNING</span>';

        return `
            <tr>
                <td><strong>${item.rule}</strong></td>
                <td>${item.title}</td>
                <td>${badge}</td>
                <td>${isViolated ? escapeHtml(violations) : 'Conforms to statutory format'}</td>
            </tr>
        `;
    }).join("");

    document.getElementById("report-modal").classList.remove("hidden");
}

function openPrintModal() {
    if (!currentScannedData) {
        showToast("No active scan data available to generate report.", "warning");
        return;
    }
    const ent = currentScannedData.extracted_entities || {};
    const comp = currentScannedData.compliance || {};

    const tempProduct = {
        id: "LMC-LIVE-SCAN",
        product_name: ent.product_name || "Scanned Commodity",
        manufacturer: ent.manufacturer || "Not Declared",
        net_quantity: ent.net_quantity || "Not Declared",
        mrp: ent.mrp || "Not Declared",
        mfg_date: ent.mfg_date || "Not Declared",
        consumer_care: ent.consumer_care || "Not Declared",
        country_of_origin: ent.country_of_origin || "Not Declared",
        compliance_status: comp.overall_status || "NEEDS REVIEW",
        violations: comp.violations_summary || "None",
        scanned_timestamp: new Date().toLocaleString()
    };

    viewProductAuditSheet(tempProduct);
}

function closeReportModal() {
    document.getElementById("report-modal").classList.add("hidden");
}

function printReport() {
    window.print();
}

// --------------------------------------------------------------------------
// Utilities & Helpers
// --------------------------------------------------------------------------
function formatStatusPill(status) {
    if (status === "COMPLIANT") {
        return `<span class="status-pill pill-compliant"><i class="fa-solid fa-circle-check"></i> COMPLIANT</span>`;
    } else if (status === "NON-COMPLIANT") {
        return `<span class="status-pill pill-non-compliant"><i class="fa-solid fa-triangle-exclamation"></i> NON-COMPLIANT</span>`;
    } else {
        return `<span class="status-pill pill-review"><i class="fa-solid fa-eye"></i> NEEDS REVIEW</span>`;
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showToast(msg, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "fa-circle-info";
    if (type === "success") icon = "fa-circle-check";
    if (type === "danger") icon = "fa-circle-xmark";
    if (type === "warning") icon = "fa-triangle-exclamation";

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(msg)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.4s ease";
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}
