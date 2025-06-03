document.addEventListener("DOMContentLoaded", function () {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const fileNameDisplay = document.querySelector(".file-name");
    const previewContainer = document.getElementById("preview-container");

    dropzone.addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileNameDisplay.textContent = file.name;

            // Clear previous preview
            previewContainer.innerHTML = "";

            // Create file preview
            if (file.type.startsWith("image/")) {
                const img = document.createElement("img");
                img.src = URL.createObjectURL(file);
                img.onload = function () {
                    URL.revokeObjectURL(img.src);
                };
                img.style.display = "block";
                previewContainer.appendChild(img);
            } else if (file.type.startsWith("video/")) {
                const video = document.createElement("video");
                video.src = URL.createObjectURL(file);
                video.controls = true;
                video.onload = function () {
                    URL.revokeObjectURL(video.src);
                };
                video.style.display = "block";
                previewContainer.appendChild(video);
            }
        }
    });

    dropzone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropzone.style.borderColor = "#007bff";
    });

    dropzone.addEventListener("dragleave", function () {
        dropzone.style.borderColor = "#d1d1d1";
    });

    dropzone.addEventListener("drop", function (e) {
        e.preventDefault();
        fileInput.files = e.dataTransfer.files;
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileNameDisplay.textContent = file.name;

            // Clear previous preview
            previewContainer.innerHTML = "";

            // Create file preview
            if (file.type.startsWith("image/")) {
                const img = document.createElement("img");
                img.src = URL.createObjectURL(file);
                img.onload = function () {
                    URL.revokeObjectURL(img.src);
                };
                img.style.display = "block";
                previewContainer.appendChild(img);
            } else if (file.type.startsWith("video/")) {
                const video = document.createElement("video");
                video.src = URL.createObjectURL(file);
                video.controls = true;
                video.onload = function () {
                    URL.revokeObjectURL(video.src);
                };
                video.style.display = "block";
                previewContainer.appendChild(video);
            }
        }
    });
});
