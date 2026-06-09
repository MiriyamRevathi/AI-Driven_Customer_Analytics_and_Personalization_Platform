const uploadForm = document.getElementById("upload-form");
const uploadAlert = document.getElementById("upload-alert");
const uploadButton = document.getElementById("upload-button");

function showUploadAlert(message, type) {
    uploadAlert.textContent = message;
    uploadAlert.className = `alert alert-${type}`;
}

if (uploadForm) {
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(uploadForm);
        const originalButtonText = uploadButton.textContent;

        uploadButton.disabled = true;
        uploadButton.textContent = "Uploading...";
        uploadAlert.className = "alert d-none";

        try {
            const response = await fetch(uploadForm.action, {
                method: "POST",
                body: formData,
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                showUploadAlert(result.error || "Upload failed.", "danger");
                return;
            }

            showUploadAlert(
                `File uploaded successfully: ${result.filename}`,
                "success"
            );
            uploadForm.reset();
        } catch (error) {
            showUploadAlert(`Upload failed: ${error.message}`, "danger");
        } finally {
            uploadButton.disabled = false;
            uploadButton.textContent = originalButtonText;
        }
    });
}
