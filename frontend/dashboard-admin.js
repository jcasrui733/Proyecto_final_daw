// ==================== INICIALIZACIÓN DASHBOARD ADMIN ====================

document.addEventListener('DOMContentLoaded', function () {
    const usuario = getUsuarioActual();
    if (!usuario) {
        window.location.href = '/';
        return;
    }

    document.getElementById('usuarioActual').textContent = usuario.nombre;
});

