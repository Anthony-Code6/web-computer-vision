const videoFeed = document.getElementById("videoFeed");
const detectionsContainer = document.getElementById("detectionsContainer");
let currentStream = null;
let intervalId = null;

async function startCamera() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        currentStream = stream;
        videoFeed.srcObject = stream;
        videoFeed.style.display = "block";
        videoFeed.classList.add("video-active");

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        intervalId = setInterval(async () => {
          if (!videoFeed.videoWidth) return;

          canvas.width = videoFeed.videoWidth;
          canvas.height = videoFeed.videoHeight;
          ctx.drawImage(videoFeed, 0, 0, canvas.width, canvas.height);
          const imageData = canvas.toDataURL("image/jpeg");

          try {
            const response = await fetch("/analizar_frame", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ image: imageData }),
            });

            const data = await response.json();

            if (data.image) {
              const img = document.createElement("img");
              img.src = data.image;
              img.alt = "Resultado de detección";
              img.classList.add("detection-img");
              detectionsContainer.prepend(img);
            }
          } catch (err) {
            console.error("Error procesando el frame:", err);
          }
        }, 5000);
      })
      .catch((err) => {
        console.error("Error al acceder a la cámara: ", err);
      });
  } else {
    console.error("El navegador no soporta acceso a la cámara.");
  }
}

function stopCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach((track) => track.stop());
    currentStream = null;
  }
  clearInterval(intervalId);
  videoFeed.srcObject = null;
  videoFeed.style.display = "none";
  videoFeed.classList.remove("video-active");
}
