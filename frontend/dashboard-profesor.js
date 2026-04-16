// ==================== INICIALIZACIÓN DASHBOARD PROFESOR ==================== 

document.addEventListener('DOMContentLoaded', function() {
    // Verificar sesión
    const usuario = getUsuarioActual();
    if (!usuario) {
        window.location.href = '/';
        return;
    }

    // Llenar datos de usuario
    document.getElementById('usuarioNombre').textContent = usuario.nombre;
    document.getElementById('usuarioActual').textContent = usuario.nombre;

    // Cargar datos
    cargarResumen();
    cargarProximasReservas();
    cargarIncidenciasRecientes();
});

// ==================== CARGAR RESUMEN ==================== 

function cargarResumen() {
    const usuario = getUsuarioActual();
    
    // Reservas del usuario
    const miReservas = reservas.filter(r => r.usuarioId === usuario.id);
    document.getElementById('totalReservas').textContent = miReservas.length;

    // Incidencias del usuario
    const misIncidencias = incidencias.filter(i => i.usuarioId === usuario.id);
    document.getElementById('totalIncidencias').textContent = misIncidencias.filter(i => i.estado === 'Pendiente').length;

    // Aulas disponibles
    const aulasDisp = aulas.filter(a => a.estado === 'Disponible').length;
    document.getElementById('aulasDisponibles').textContent = aulasDisp;
}

// ==================== CARGAR PRÓXIMAS RESERVAS ==================== 

function cargarProximasReservas() {
    const usuario = getUsuarioActual();
    const miReservas = reservas.filter(r => r.usuarioId === usuario.id);
    const container = document.getElementById('proximasReservas');

    if (miReservas.length === 0) {
        container.innerHTML = '<p class="empty-state">No hay reservas próximas</p>';
        return;
    }

    container.innerHTML = miReservas.map(reserva => {
        const aula = aulas.find(a => a.id === reserva.aulaId);
        return `
            <div class="reserva-item">
                <div class="item-info">
                    <h3>${aula.nombre}</h3>
                    <p>${reserva.fecha} | ${reserva.horaInicio} - ${reserva.horaFin}</p>
                    <p style="color: var(--gray-600);">${reserva.motivo}</p>
                </div>
                <span class="item-status status-${reserva.estado.toLowerCase()}">${reserva.estado}</span>
            </div>
        `;
    }).join('');
}

// ==================== CARGAR INCIDENCIAS RECIENTES ==================== 

function cargarIncidenciasRecientes() {
    const usuario = getUsuarioActual();
    const misIncidencias = incidencias.filter(i => i.usuarioId === usuario.id);
    const container = document.getElementById('incidenciasRecientes');

    if (misIncidencias.length === 0) {
        container.innerHTML = '<p class="empty-state">No hay incidencias registradas</p>';
        return;
    }

    container.innerHTML = misIncidencias.map(incidencia => {
        const aula = aulas.find(a => a.id === incidencia.aulaId);
        return `
            <div class="incidencia-item">
                <div class="item-info">
                    <h3>${incidencia.tipo}</h3>
                    <p>${aula.nombre} | ${incidencia.fecha}</p>
                    <p style="color: var(--gray-600);">${incidencia.descripcion || incidencia.descripción || ""}</p>
                </div>
                <span class="item-status status-${incidencia.estado.toLowerCase()}">${incidencia.estado}</span>
            </div>
        `;
    }).join('');
}


