const input_fecha = document.getElementById("reporte-fecha")
const exportar_pdf = document.getElementById('exportar-pdf')
exportar_pdf.style.display='none'
const detalles = document.getElementById('detalles')
const view_informe = document.getElementById('informe')
view_informe.style.display = 'none'

exportar_pdf.addEventListener('click', async () => {
    const fecha = input_fecha.value;
    const { jsPDF } = window.jspdf;

    const canvasContainer = document.getElementById("informe");

    // Aumentar resoluci�n del canvas para mejor calidad
    const canvasImg = await html2canvas(canvasContainer, {
        scale: 2, // renderiza en mayor resoluci�n
        useCORS: true // por si hay im�genes externas
    });

    const imgData = canvasImg.toDataURL("image/png");
    const pdf = new jsPDF("landscape", "pt", "a4");

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgWidth = canvasImg.width;
    const imgHeight = canvasImg.height;

    const ratio = Math.min(pageWidth / imgWidth, pageHeight / imgHeight);
    const imgScaledWidth = imgWidth * ratio;
    const imgScaledHeight = imgHeight * ratio;

    const x = (pageWidth - imgScaledWidth) / 2;
    const y = 40;

    pdf.text("Reporte de Detecciones", 40, 30);
    pdf.addImage(imgData, "PNG", x, y, imgScaledWidth, imgScaledHeight);
    pdf.save(`ReporteGenerado-${fecha}.pdf`);
});

const GenerarReporte = async () => {
    const fecha = input_fecha.value;
    if (!fecha) return swal("Error !", "Debes seleccionar la fecha.", "error");

    const resp = await fetch(`/api/reporte-fecha/${fecha}`);
    const data = await resp.json();

    console.log(data)

    if (data.detecciones.length > 0) {
        exportar_pdf.style.display='block'
        view_informe.style.display = 'block'


        // Detalles
        detalles.innerHTML = `
            <p><strong>Fecha:</strong> ${data.fecha}</p>
            <p><strong>Total Detecciones:</strong> ${data.total_detecciones}</p>
            <p><strong>Total Errores:</strong> ${data.total_errores}</p>
        `

        // Grafico
        const labels = Object.keys(data.errores_por_tipo);
        const values = Object.values(data.errores_por_tipo);

        mostrarGrafico(data, labels, values);
    } else {
         exportar_pdf.style.display='none'
        view_informe.style.display = 'none'
        swal("Error !", "No existe detecciones en esa fecha.", "error");
    }
}

function mostrarGrafico(data, labels, values) {
    const ctx = document.getElementById("grafico-errores").getContext("2d");
    if (window.graficoExistente) {
        window.graficoExistente.destroy();
    }

    window.graficoExistente = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Errores por tipo',
                data: values,
                backgroundColor: ['#FFA500', '#FF8C00', '#FFD580', '#FF6347'], // colores ejemplo
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Reporte de Errores - ${data.fecha} (${data.total_errores}/${data.total_detecciones})`
                }
            }
        }
    });
}