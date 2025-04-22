let listaDetecciones = [];
const contenedor = document.getElementById('row-data')

const cargarDetecciones = async () => {
    const response = await fetch('/api/list-detections', { method: 'GET' })
    const datos = await response.json()

    listaDetecciones = []

    let information = ''

    if (datos._deteccion.length >= 0) {
        datos._deteccion.forEach(element => {
            listaDetecciones.push(element)
        })

        renderizarDetecciones(listaDetecciones)
    } else {
        information += `
         <div class="text-center">
            Cargando ....
        </div>
        `
        contenedor.innerHTML = information
    }

}

document.addEventListener('DOMContentLoaded', cargarDetecciones);

const renderizarDetecciones = (data) => {
    let information = ''
    data.forEach(element => {
        confianza = Math.floor(element.confianza)

        information += `
            <div class="col-lg-4 col-md-6 col-sm-12">
                <div class="card">
                    <img src="${element.imagen_url}" class="card-img-top" alt="${element.id}" loading="lazy">
                    <div class="card-body">
                        <div class="details">
                            <div class="estado">
                               ${element.estado ? 'Hongo' : 'Sano'}
                            </div>
                            <div class="confianza">
                               ${confianza + '%'}
                            </div>

                            <div class="tiempo">
                               ${element.tiempo_procesamiento + 'ms'}
                            </div>
                        </div>
                        <form action="javascript:void(0)" method="POST" onsubmit="reportarError(this)">
                            <input type="hidden" name="deteccion_id" value="${element.id}">
                            <input type="hidden" name="imagen_url" value="${element.imagen_url}">
                            <label>Tipo de error:</label>
                            <select name="tipo_error" class="form-select shadow-none" required>
                                <option value="falso_positivo">Falso Positivo</option>
                                <option value="falso_negativo">Falso Negativo</option>
                            </select>
                            <label>Comentario:</label>
                            <textarea name="comentario" class="form-control shadow-none"
                                placeholder="Comentario opcional..." required></textarea>
                            <div class="button d-flex justify-content-between mt-2">
                                <button type="submit" class="btn btn-primary">Registrar Error</button>
                                <button type="button" class="btn btn-danger" onclick="eliminarDeteccion(this.form)">Eliminar</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            `
    });

    contenedor.innerHTML = information;
}

const eliminarDeteccion = async (form) => {
    const id = form.deteccion_id.value;
    const imagen_url = form.imagen_url.value;

    //if (!confirm("Estas seguro de que quieres eliminar esta deteccion?")) return;

    try {
        const res = await fetch('/api/eliminar-deteccion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, imagen_url })
        });

        const result = await res.json();

        if (res.ok) {
            const index = listaDetecciones.findIndex(item => Number(item.id) === Number(id));
            if (index !== -1) listaDetecciones.splice(index, 1);

            if (listaDetecciones.length < 8) {
                await cargarDetecciones();
            } else {
                renderizarDetecciones(listaDetecciones)
            }

            if (listaDetecciones.length < 8) {
                await cargarDetecciones();
            } else {
                renderizarDetecciones(listaDetecciones)
            }

        } else {
            alert('Error al eliminar: ' + result.message);
        }
    } catch (err) {
        console.error('Error al eliminar:', err);
    }
}

const reportarError = async (form) => {
    const formData = new FormData(form);
    const data = {
        deteccion_id: formData.get('deteccion_id'),
        tipo_error: formData.get('tipo_error'),
        comentario: formData.get('comentario')
    };

    try {
        const res = await fetch('/api/marcar_error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            cargarDetecciones()
        } else {
            alert('Error al reportar: ' + result.message);
        }
    } catch (err) {
        console.error('Error al enviar el reporte:', err);
    }
};

