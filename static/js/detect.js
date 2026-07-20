const fileInput = document.getElementById("mriFile");
const dropZone = document.getElementById("dropZone");
const fileName = document.getElementById("fileName");
const fileMeta = document.getElementById("fileMeta");

const originalPreview = document.getElementById("originalPreview");
const resultPreview = document.getElementById("resultPreview");
const originalEmpty = document.getElementById("originalEmpty");
const resultEmpty = document.getElementById("resultEmpty");
const heatmapLayer = document.getElementById("heatmapLayer");
const resultStage = document.getElementById("resultStage");

const runBtn = document.getElementById("runBtn");
const clearBtn = document.getElementById("clearBtn");

const opacitySlider = document.getElementById("opacitySlider");
const opacityValue = document.getElementById("opacityValue");

const statusPill = document.getElementById("statusPill");
const scoreValue = document.getElementById("scoreValue");
const scoreLabel = document.getElementById("scoreLabel");

const processUpload = document.getElementById("processUpload");
const processPreprocess = document.getElementById("processPreprocess");
const processModel = document.getElementById("processModel");
const processDone = document.getElementById("processDone");

const analysisTextOne = document.getElementById("analysisTextOne");
const analysisTextTwo = document.getElementById("analysisTextTwo");
const analysisTextThree = document.getElementById("analysisTextThree");

const downloadImageBtn = document.getElementById("downloadImageBtn");
const downloadReportBtn = document.getElementById("downloadReportBtn");
const downloadOriginalBtn = document.getElementById("downloadOriginalBtn");

const caseIdInput = document.getElementById("caseId");
const modalityInput = document.getElementById("modality");
const notesInput = document.getElementById("notes");

let uploadedFile = null;
let localPreviewUrl = null;

let downloadOriginalUrl = null;
let downloadResultImageUrl = null;
let downloadReportUrl = null;

let latestOriginalImageUrl = null;
let latestResultImageUrl = null;


function createDefaultCaseId() {
    const now = new Date();

    const datePart = [
        now.getFullYear(),
        String(now.getMonth() + 1).padStart(2, "0"),
        String(now.getDate()).padStart(2, "0")
    ].join("");

    const timePart = [
        String(now.getHours()).padStart(2, "0"),
        String(now.getMinutes()).padStart(2, "0"),
        String(now.getSeconds()).padStart(2, "0")
    ].join("");

    return `CASE-${datePart}-${timePart}`;
}


function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


function resetProcess() {
    processUpload.classList.remove("done");
    processPreprocess.classList.remove("done");
    processModel.classList.remove("done");
    processDone.classList.remove("done");
}


function markProcessUpload() {
    processUpload.classList.add("done");
}


function markProcessPreprocess() {
    processPreprocess.classList.add("done");
}


function markProcessModel() {
    processModel.classList.add("done");
}


function markProcessDone() {
    processDone.classList.add("done");
}


function resetResultLinks() {
    downloadOriginalUrl = null;
    downloadResultImageUrl = null;
    downloadReportUrl = null;
    latestOriginalImageUrl = null;
    latestResultImageUrl = null;
}


function setWaitingState() {
    statusPill.textContent = "Status: Waiting";

    scoreValue.textContent = "--";
    scoreLabel.textContent = "Waiting for analysis";

    analysisTextOne.textContent = "Detection summaries will be shown here once analysis completes.";
    analysisTextTwo.textContent = "Displays abnormal regions, model confidence and image quality feedback.";
    analysisTextThree.textContent = "For research demonstration only; not valid for clinical diagnosis.";

    resetProcess();
    resetResultLinks();
}


function setProcessingState() {
    statusPill.textContent = "Status: Processing";

    scoreValue.textContent = "--";
    scoreLabel.textContent = "Running detection";

    analysisTextOne.textContent = "文件已上传到后端，正在进行保存与预处理。";
    analysisTextTwo.textContent = "模型接口正在运行，目前版本会调用 placeholder model。";
    analysisTextThree.textContent = "请等待结果返回。";

    resetProcess();
    markProcessUpload();

    runBtn.disabled = true;
    runBtn.textContent = "Processing...";
}


function setCompletedState(data) {
    statusPill.textContent = "Status: Completed";

    scoreValue.textContent = Number(data.score).toFixed(2);
    scoreLabel.textContent = data.score_label || "Completed";

    markProcessUpload();
    markProcessPreprocess();
    markProcessModel();
    markProcessDone();

    if (Array.isArray(data.analysis)) {
        analysisTextOne.textContent = data.analysis[0] || "";
        analysisTextTwo.textContent = data.analysis[1] || "";
        analysisTextThree.textContent = data.analysis[2] || "";
    }

    downloadOriginalUrl = data.download_original_url;
    downloadResultImageUrl = data.download_result_image_url;
    downloadReportUrl = data.download_report_url;

    latestOriginalImageUrl = data.original_image_url;
    latestResultImageUrl = data.result_image_url;

    originalPreview.src = latestOriginalImageUrl;
    originalPreview.style.display = "block";
    originalEmpty.style.display = "none";

    resultPreview.src = latestResultImageUrl;
    resultPreview.style.display = "block";
    resultPreview.style.opacity = opacitySlider.value / 100;

    resultEmpty.style.display = "none";
    heatmapLayer.style.display = "none";

    runBtn.disabled = false;
    runBtn.textContent = "Run Detection";
}


function setErrorState(message) {
    statusPill.textContent = "Status: Error";

    scoreValue.textContent = "--";
    scoreLabel.textContent = "Analysis failed";

    analysisTextOne.textContent = message || "后端处理失败。";
    analysisTextTwo.textContent = "请检查文件格式、文件大小，或确认 Flask 服务是否正常运行。";
    analysisTextThree.textContent = "如果错误持续出现，需要检查 app.py 的终端报错信息。";

    runBtn.disabled = false;
    runBtn.textContent = "Run Detection";
}


function handleFile(file) {
    uploadedFile = file;

    if (localPreviewUrl) {
        URL.revokeObjectURL(localPreviewUrl);
    }

    localPreviewUrl = URL.createObjectURL(file);

    fileName.textContent = file.name;
    fileMeta.textContent = `${formatFileSize(file.size)} · ${file.type || "Medical image data"}`;

    setWaitingState();

    const isImage = file.type.startsWith("image/");

    if (isImage) {
        originalPreview.src = localPreviewUrl;
        originalPreview.style.display = "block";
        originalEmpty.style.display = "none";
    } else {
        originalPreview.removeAttribute("src");
        originalPreview.style.display = "none";
        originalEmpty.style.display = "block";
        originalEmpty.innerHTML = `
            <p>MRI file uploaded</p>
            <span>${file.name}</span>
        `;
    }

    resultPreview.removeAttribute("src");
    resultPreview.style.display = "none";
    resultPreview.style.opacity = 1;

    resultEmpty.style.display = "block";
    resultEmpty.innerHTML = `
        <p>Generated anomaly image</p>
        <span>点击 Run Detection 后显示后端返回结果</span>
    `;

    heatmapLayer.style.display = "none";
}


async function runDetection() {
    if (!uploadedFile) {
        statusPill.textContent = "Status: Please Upload File";
        return;
    }

    setProcessingState();

    const formData = new FormData();
    formData.append("mriFile", uploadedFile);
    formData.append("caseId", caseIdInput.value);
    formData.append("modality", modalityInput.value);
    formData.append("notes", notesInput.value);

    try {
        setTimeout(markProcessPreprocess, 250);
        setTimeout(markProcessModel, 500);

        const response = await fetch("/api/detect", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Detection request failed.");
        }

        setCompletedState(data);

    } catch (error) {
        setErrorState(error.message);
    }
}


function clearAll() {
    uploadedFile = null;

    if (localPreviewUrl) {
        URL.revokeObjectURL(localPreviewUrl);
        localPreviewUrl = null;
    }

    fileInput.value = "";
    caseIdInput.value = createDefaultCaseId();
    modalityInput.value = "T1";
    notesInput.value = "";

    fileName.textContent = "No file selected";
    fileMeta.textContent = "Waiting for upload";

    originalPreview.removeAttribute("src");
    originalPreview.style.display = "none";
    originalEmpty.style.display = "block";
    originalEmpty.innerHTML = `
        <p>Original image preview</p>
        <span>上传图像后显示在这里</span>
    `;

    resultPreview.removeAttribute("src");
    resultPreview.style.display = "none";
    resultPreview.style.opacity = 1;

    resultEmpty.style.display = "block";
    resultEmpty.innerHTML = `
        <p>Generated anomaly image</p>
        <span>点击 Run Detection 后显示结果</span>
    `;

    heatmapLayer.style.display = "none";

    opacitySlider.value = 65;
    opacityValue.textContent = "65%";

    setWaitingState();
}


function openDownload(url, emptyMessage) {
    if (!url) {
        statusPill.textContent = emptyMessage;
        return;
    }

    window.location.href = url;
}


fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];

    if (file) {
        handleFile(file);
    }
});


dropZone.addEventListener("dragover", function (event) {
    event.preventDefault();
    dropZone.classList.add("dragging");
});


dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("dragging");
});


dropZone.addEventListener("drop", function (event) {
    event.preventDefault();
    dropZone.classList.remove("dragging");

    const file = event.dataTransfer.files[0];

    if (file) {
        fileInput.files = event.dataTransfer.files;
        handleFile(file);
    }
});


opacitySlider.addEventListener("input", function () {
    const value = Number(opacitySlider.value);
    opacityValue.textContent = `${value}%`;

    if (latestResultImageUrl) {
        resultPreview.style.opacity = value / 100;
    }
});


runBtn.addEventListener("click", runDetection);


clearBtn.addEventListener("click", clearAll);


downloadImageBtn.addEventListener("click", function () {
    openDownload(downloadResultImageUrl, "Status: No Result Image");
});


downloadReportBtn.addEventListener("click", function () {
    openDownload(downloadReportUrl, "Status: No Report File");
});


downloadOriginalBtn.addEventListener("click", function () {
    openDownload(downloadOriginalUrl, "Status: No Uploaded File");
});


caseIdInput.value = createDefaultCaseId();
setWaitingState();