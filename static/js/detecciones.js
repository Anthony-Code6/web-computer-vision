let listaDetecciones = [];
// const contenedor = document.getElementById("row-data");

const myModal = new bootstrap.Modal("#staticBackdrop", {
  keyboard: false,
});

const contenedor = document.getElementById("tabla_detecciones");
const contenido_clasificado = document.getElementById(
  "tabla_detecciones_clasificado"
);

const tabla_clasificado = document.getElementById("tabla_clasificado");
tabla_clasificado.style.display = "none";

const tabla_sin_clasificado = document.getElementById("tabla_sin_clasificado");
tabla_sin_clasificado.style.display = "block";

const cargarDetecciones = async () => {
  const response = await fetch("/api/list-detections", { method: "GET" });
  const datos = await response.json();
  console.log(datos);

  listaDetecciones = [];

  if (datos._deteccion.length > 0) {
    datos._deteccion.forEach((element) => {
      listaDetecciones.push(element);
    });
    renderizarDetecciones(listaDetecciones);
  } else {
    tabla_sin_clasificado.style.display = "none";
    datos._detecciones.forEach((element) => {
      listaDetecciones.push(element);
    });

    tabla_clasificado.style.display = "block";
    renderizarDeteccionesClasificados(listaDetecciones);
  }
};

document.addEventListener("DOMContentLoaded", cargarDetecciones);

const renderizarDetecciones = (data) => {
  let information = "";

  if (data.length > 0) {
    data.forEach((element, index) => {
      let i = index + 1;
      let confianza = Math.floor(element.confianza);

      information += `
          <tr>
              <td>${i}</td>
              <td class="text-center">
                <button type="button" class="btn btn-light btn-sm" data-bs-toggle="modal" data-bs-target="#model_imagen" onclick="ViewModal('${
                  element.imagen_url
                }')">
                  Imagen
                </button>
              </td>
              <td>${element.tiempo_procesamiento + "ms"}</td>
              <td> ${confianza + "%"}</td>
              <td>${element.fecha}</td>
              <td>
                    ${
                      element.estado
                        ? `
                      <div class="estado_hongo">
                        Hongo
                      </div>
                      `
                        : `
                      <div class="estado_sano">
                        Sano
                      </div>
                      `
                    }
              </td>
              <td>
                  <div class="dropdown">
                      <a class="btn btn-secondary btn-sm dropdown-toggle" href="javascript:void(0)" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                          Acción
                      </a>
  
                      <ul class="dropdown-menu">
                        <li>
                          <a class="dropdown-item" href="javascript:void(0)" data-bs-toggle="modal" data-bs-target="#staticBackdrop" onclick="Clasificar('${
                            element.id
                          }')">
                            Clasificar
                          </a>
                        </li>
                        <li>
                          <a class="dropdown-item" href="javascript:void(0)" onclick="eliminarDeteccion(${index},${
        element.id
      },'${element.imagen_url}')">
                            Eliminar
                          </a>
                        </li>
                      </ul>
                  </div>
              </td>
          </tr>
  `;
    });
  } else {
    cargarDetecciones();
  }

  contenedor.innerHTML = information;
};

const renderizarDeteccionesClasificados = (data) => {
  let information = "";
  if (data.length > 0) {
    data.forEach((element, index) => {
      let i = index + 1;
      let confianza = Math.floor(element.confianza);

      information += `
            <tr>
                <td>${i}</td>
                <td class="text-center">
                  <button type="button" class="btn btn-light btn-sm" data-bs-toggle="modal" data-bs-target="#model_imagen" onclick="ViewModal('${
                    element.imagen_url
                  }')">
                    Imagen
                  </button>
                </td>
                <td>${element.tiempo_procesamiento + "ms"}</td>
                <td> ${confianza + "%"}</td>
                <td>${element.fecha}</td>
                <td>
                      ${
                        element.estado
                          ? `
                        <div class="estado_hongo">
                          Hongo
                        </div>
                        `
                          : `
                        <div class="estado_sano">
                          Sano
                        </div>
                        `
                      }
                </td>
            </tr>
    `;
    });
  } else {
    information += `
    <tr>
        <td colspan="6" class="text-center">No se encontraron datos.</td>
    </tr>
    `;
  }

  contenido_clasificado.innerHTML = information;
};

const deteccion_id = document.getElementById("deteccion_id");
const comentario = document.getElementById("comentario");
const Clasificar = (id) => {
  deteccion_id.value = id;
  comentario.value = "";
};

const imagen_modal = document.getElementById("imagen_modal_read");
const ViewModal = (imagen) => {
  imagen_modal.src = imagen;
};

const filtrarDetecciones = () => {
  const estado = document.getElementById("filtro-estado").value;
  const fecha = document.getElementById("filtro-fecha").value;

  let filtro = listaDetecciones.filter((d) => {
    const estadoMatch =
      estado === "" ||
      Boolean(d.estado) === Boolean(estado == "hongo" ? true : false);
    const fechaMatch = !fecha || d.fecha.startsWith(fecha);
    return estadoMatch && fechaMatch;
  });

  renderizarDetecciones(filtro);
  renderizarDeteccionesClasificados(filtro);
};

const eliminarDeteccion = async (index, id, imagen_url) => {
  try {
    swal({
      title: "Eliminar Deteccion?",
      text: "Seguro que deseas eliminar esta detección.",
      icon: "warning",
      buttons: true,
      dangerMode: true,
    }).then(async (willDelete) => {
      if (willDelete) {
        const res = await fetch("/api/eliminar-deteccion", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id, imagen_url }),
        });

        const result = await res.json();

        if (res.ok) {
          if (index !== -1) listaDetecciones.splice(index, 1);

          renderizarDetecciones(listaDetecciones);
        } else {
          swal("Error !", result.message, "error");
        }
      }
    });
  } catch (err) {
    console.error("Error al eliminar:", err);
  }
};

const reportarError = async (form) => {
  const formData = new FormData(form);
  let id = formData.get("deteccion_id");
  const data = {
    deteccion_id: formData.get("deteccion_id"),
    tipo_error: formData.get("tipo_error"),
    comentario: formData.get("comentario"),
  };

  try {
    const res = await fetch("/api/marcar_error", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await res.json();

    if (res.ok) {
      myModal.hide();
      swal(
        "Exito !",
        "La clasificacion de error se guardo correctamente",
        "success"
      );

      const index = listaDetecciones.findIndex(
        (item) => Number(item.id) === Number(id)
      );
      if (index !== -1) listaDetecciones.splice(index, 1);

      if (listaDetecciones.length < 8) {
        await cargarDetecciones();
      } else {
        renderizarDetecciones(listaDetecciones);
      }
    } else {
      swal("Error !", "Ocurrio un problema.", "error");
    }
  } catch (err) {
    console.error("Error al enviar el reporte:", err);
  }
};
