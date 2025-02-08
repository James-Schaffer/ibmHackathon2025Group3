const video = document.getElementById("video");
const captureButton = document.getElementById("capture");
const capturedImage = document.getElementById("capturedImage");

// Start the camera
async function startCamera() {
    alert("Starting camera...");

    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("getUserMedia() is not supported in this browser.");
            return;
        }

        alert("Requesting camera access...");
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: "environment" } // Use "environment" for the back camera
        });

        alert("Camera access granted!");
        video.srcObject = stream;

    } catch (error) {
        alert(`Camera access error: ${error.name} - ${error.message}`);
        console.error("Camera error:", error);
    }
}

// Capture image
captureButton.addEventListener("click", () => {
    if (!video.srcObject) {
        alert("Error: Camera not started!");
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");

    alert("Capturing image...");
    
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    capturedImage.src = canvas.toDataURL("image/png");
});

// Start the camera
startCamera();
