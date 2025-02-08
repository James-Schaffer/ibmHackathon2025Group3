// Select elements
const video = document.getElementById("video");
const captureButton = document.getElementById("capture");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

// Access the phone's camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error("Error accessing camera:", error);
    }
}

// Capture image when button is clicked
captureButton.addEventListener("click", () => {
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame onto the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
});

// Start the camera on page load
startCamera();
