// Datos simulados y utilidades compartidas del frontend.

const DEFAULT_USUARIOS = [
    {
        id: 1,
        nombre: "Laura García",
        email: "laura@instituto.es",
        password: "123456",
        rol: "profesor",
        estado: "Activo"
    },
    {
        id: 2,
        nombre: "Administrador Centro",
        email: "admin@instituto.es",
        password: "123456",
        rol: "admin",
        estado: "Activo"
    },
    {
        id: 3,
        nombre: "Marta Ruiz",
        email: "marta@instituto.es",
        password: "123456",
        rol: "profesor",
        estado: "Activo"
    }
];

const USERS_STORAGE_KEY = "mock_usuarios";

function cloneUsuarios(list) {
    return list.map(function (usuario) {
        return Object.assign({}, usuario);
    });
}

function getUsuariosSimulados() {
    try {
        const raw = localStorage.getItem(USERS_STORAGE_KEY);
        if (!raw) {
            localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(DEFAULT_USUARIOS));
            return cloneUsuarios(DEFAULT_USUARIOS);
        }

        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed) || !parsed.length) {
            localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(DEFAULT_USUARIOS));
            return cloneUsuarios(DEFAULT_USUARIOS);
        }

        return parsed;
    } catch (error) {
        localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(DEFAULT_USUARIOS));
        return cloneUsuarios(DEFAULT_USUARIOS);
    }
}

function saveUsuariosSimulados(list) {
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(list));
}

const aulas = [
    {
        id: 1,
        nombre: "Aula 101",
        tipo: "Aula normal",
        capacidad: 30,
        planta: "1a",
        equipamiento: ["Proyector", "Pizarra digital", "WiFi"],
        estado: "Disponible"
    },
    {
        id: 2,
        nombre: "Laboratorio Informatica 2",
        tipo: "Laboratorio",
        capacidad: 20,
        planta: "2a",
        equipamiento: ["Ordenadores", "Proyector", "WiFi"],
        estado: "Disponible"
    },
    {
        id: 3,
        nombre: "Aula de Música",
        tipo: "Especializada",
        capacidad: 25,
        planta: "1a",
        equipamiento: ["Instrumentos", "Amplificadores", "WiFi"],
        estado: "Ocupada"
    },
    {
        id: 4,
        nombre: "Biblioteca",
        tipo: "Zona común",
        capacidad: 50,
        planta: "0a",
        equipamiento: ["WiFi", "Mesas de estudio"],
        estado: "Disponible"
    }
];

const reservas = [
    {
        id: 1,
        aulaId: 1,
        usuarioId: 1,
        fecha: "2026-04-10",
        horaInicio: "10:00",
        horaFin: "11:00",
        motivo: "Reunión de tutoría",
        estado: "Confirmada"
    },
    {
        id: 2,
        aulaId: 2,
        usuarioId: 1,
        fecha: "2026-04-11",
        horaInicio: "12:00",
        horaFin: "13:00",
        motivo: "Clase práctica",
        estado: "Pendiente"
    }
];

const incidencias = [
    {
        id: 1,
        aulaId: 1,
        usuarioId: 1,
        tipo: "Proyector averiado",
        prioridad: "Alta",
        descripcion: "El proyector no enciende.",
        estado: "Pendiente",
        fecha: "2026-04-09"
    },
    {
        id: 2,
        aulaId: 2,
        usuarioId: 1,
        tipo: "Ordenador no funciona",
        prioridad: "Media",
        descripcion: "Un equipo no arranca correctamente.",
        estado: "En curso",
        fecha: "2026-04-08"
    }
];

function getUsuarioActual() {
    try {
        const raw = localStorage.getItem("usuarioActual");
        if (!raw) {
            return null;
        }
        return JSON.parse(raw);
    } catch (error) {
        return null;
    }
}

function logout() {
    localStorage.removeItem("usuarioActual");
    window.location.href = "/";
}

const loginForm = document.querySelector(".login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(loginForm);

        try {
            const response = await fetch("/api/login/", {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });

            const payload = await response.json();
            if (!response.ok || !payload.ok || !payload.user) {
                alert((payload && payload.message) || "Email o contraseña incorrectos");
                return;
            }

            const usuario = payload.user;
            localStorage.setItem("usuarioActual", JSON.stringify(usuario));
            const userEmailQuery = usuario.email ? "?user_email=" + encodeURIComponent(usuario.email) : "";

            if (usuario.rol === "profesor") {
                window.location.href = "/dashboard-profesor/" + userEmailQuery;
            } else if (usuario.rol === "admin") {
                window.location.href = "/dashboard-admin/" + userEmailQuery;
            } else {
                window.location.href = "/";
            }
        } catch (error) {
            alert("No se pudo iniciar sesión. Inténtalo de nuevo.");
        }
    });
}

function setupRegisterForm() {
    const toggleButton = document.getElementById("btnMostrarRegistro");
    const registerForm = document.getElementById("registerForm");

    if (!toggleButton || !registerForm) {
        return;
    }

    toggleButton.addEventListener("click", function () {
        registerForm.classList.toggle("open");
        toggleButton.textContent = registerForm.classList.contains("open")
            ? "Ocultar registro"
            : "Crear cuenta de profesor";
    });

    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const nombre = (document.getElementById("registerName") || {}).value?.trim() || "";
        const email = (document.getElementById("registerEmail") || {}).value?.trim() || "";
        const password = (document.getElementById("registerPassword") || {}).value?.trim() || "";
        const confirmPassword = (document.getElementById("registerPasswordConfirm") || {}).value?.trim() || "";

        if (!nombre || !email || !password) {
            alert("Completa todos los campos del registro.");
            return;
        }

        if (password.length < 4) {
            alert("La contraseña debe tener al menos 4 caracteres.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Las contraseñas no coinciden.");
            return;
        }

        const formData = new FormData();
        formData.append("nombre", nombre);
        formData.append("email", email);
        formData.append("password", password);

        try {
            const response = await fetch("/api/register/", {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });

            const payload = await response.json();
            if (!response.ok || !payload.ok) {
                alert((payload && payload.message) || "No se pudo registrar el usuario.");
                return;
            }

            alert("Usuario registrado correctamente. Ahora puedes iniciar sesión.");
            
        } catch (error) {
            alert("No se pudo registrar el usuario. Inténtalo de nuevo.");
        }
    });
}

setupRegisterForm();
