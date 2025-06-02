let listClasificacion = [];

const contenedor = document.getElementById("tabla_clasificacion");

const LoadClasificacion = async () => {
  const response = await fetch("/api/list-clasificacion", { method: "GET" });
  const data = await response.json();
  console.log(data);

  listClasificacion = [];
  data._clasificacion.forEach((element) => {
    listClasificacion.push(element);
  });

  renderizarClasificaciones(listClasificacion);
};

document.addEventListener("DOMContentLoaded", LoadClasificacion);

const renderizarClasificaciones = (data) => {
  let information = "";

  if (data.length > 0) {
    data.forEach((element, index) => {
      let i = index + 1;
      let tipo = element.tipo_error.replace("_", " ");
      information += `
          <tr>
              <td>${i}</td>
              <td>${tipo}</td>
              <td>${element.comentario}</td>
              <td>
                  <div class="dropdown">
                      <a class="btn btn-secondary btn-sm dropdown-toggle" href="javascript:void(0)" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                          Acción
                      </a>
  
                      <ul class="dropdown-menu">
                          <li><a class="dropdown-item" href="javascript:void(0)" onclick="eliminarClasificacion(${index},${element.id})">Eliminar</a></li>
                      </ul>
                  </div>
              </td>
          </tr>
  `;
    });
  } else {
    information +=
      `
            <tr>
                <td colspan="4" style="text-align: center;">No se encuentra datos para mostrar.</td>
            </tr>
        `;
  }
  contenedor.innerHTML = information;
};

const eliminarClasificacion = async (index, id) => {
  try {
    swal({
      title: "Eliminar Clasificación?",
      text: "Seguro que deseas eliminar esta clasificación.",
      icon: "warning",
      buttons: true,
      dangerMode: true,
    }).then(async (willDelete) => {
      if (willDelete) {
        const res = await fetch("/api/eliminar-clasificacion", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id }),
        });

        const result = await res.json();

        if (res.ok) {
          if (index !== -1) listClasificacion.splice(index, 1);

          renderizarClasificaciones(listClasificacion);
        } else {
          alert("Error al eliminar: " + result.message);
        }
      }
    });
  } catch (err) {
    console.error("Error al eliminar:", err);
  }
};
