(function () {
    function getModalElements() {
        return {
            modal: document.getElementById("detailModal"),
            title: document.getElementById("detailModalTitle"),
            body: document.getElementById("detailModalBody"),
            close: document.getElementById("detailModalClose"),
            backdrop: document.getElementById("detailModalBackdrop")
        };
    }

    function openDetailModal(title, lines) {
        const elements = getModalElements();
        if (!elements.modal || !elements.title || !elements.body) {
            return;
        }

        elements.title.textContent = title || "Detalle";
        elements.body.innerHTML = "";

        (lines || []).forEach(function (line) {
            const wrapper = document.createElement("div");
            wrapper.className = "detail-line";

            const label = document.createElement("div");
            label.className = "detail-line-label";
            label.textContent = line.label;

            const value = document.createElement("div");
            value.className = "detail-line-value";
            value.textContent = line.value;

            wrapper.appendChild(label);
            wrapper.appendChild(value);
            elements.body.appendChild(wrapper);
        });

        elements.modal.classList.add("open");
        elements.modal.setAttribute("aria-hidden", "false");
    }

    function closeDetailModal() {
        const elements = getModalElements();
        if (!elements.modal) {
            return;
        }
        elements.modal.classList.remove("open");
        elements.modal.setAttribute("aria-hidden", "true");
    }

    function setupDetailModal() {
        const elements = getModalElements();
        if (!elements.modal) {
            return;
        }

        if (elements.close) {
            elements.close.addEventListener("click", closeDetailModal);
        }
        if (elements.backdrop) {
            elements.backdrop.addEventListener("click", closeDetailModal);
        }

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeDetailModal();
            }
        });
    }

    function showToast(message, type) {
        const container = document.getElementById("toastContainer");
        if (!container) {
            return;
        }

        const toast = document.createElement("div");
        toast.className = "app-toast" + (type ? " toast-" + type : "");
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(function () {
            toast.classList.add("show");
        }, 10);

        setTimeout(function () {
            toast.classList.remove("show");
            setTimeout(function () {
                toast.remove();
            }, 250);
        }, 2200);
    }

    window.showToast = showToast;

    function updateStatusPill(cell, text, cssClass) {
        if (!cell) {
            return;
        }
        const pill = cell.querySelector(".status-pill, .item-status") || cell;
        if (!pill) {
            return;
        }

        pill.className = pill.className.replace(/status-[a-z-]+/g, "").trim();
        if (cssClass) {
            pill.classList.add(cssClass);
        }
        pill.textContent = text;
    }

    function normalizeText(value) {
        return (value || "")
            .toString()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    function getCurrentUserIdentity() {
        let currentUser = null;
        if (typeof getUsuarioActual === "function") {
            currentUser = getUsuarioActual();
        }

        return {
            email: currentUser && currentUser.email ? currentUser.email : ""
        };
    }

    function setupBuscarAulas() {
        const minCapInput = document.getElementById("capacidadMinima");
        const table = document.querySelector(".data-table tbody");
        const dateInput = document.getElementById("fechaBusqueda");
        const reserveForms = Array.from(document.querySelectorAll(".backend-reserve-form"));

        const syncReserveForms = function () {
            const currentUser = getCurrentUserIdentity();
            reserveForms.forEach(function (form) {
                const emailInput = form.querySelector(".js-user-email");
                const fechaInput = form.querySelector("input[name='fecha']");
                const horarioInput = form.querySelector("input[name='horario']");

                if (emailInput) {
                    emailInput.value = currentUser.email || "";
                }
                if (fechaInput && dateInput) {
                    fechaInput.value = dateInput.value;
                }
                if (horarioInput) {
                    horarioInput.value = (document.getElementById("tramoBusqueda") || {}).value || horarioInput.value;
                }
            });
        };

        if (minCapInput && table) {
            const filterRows = function () {
                const minCap = parseInt(minCapInput.value || "0", 10);
                Array.from(table.querySelectorAll("tr")).forEach(function (row) {
                    const capCell = row.cells[2];
                    const capacity = parseInt((capCell ? capCell.textContent : "0").trim(), 10);
                    row.style.display = capacity >= minCap ? "" : "none";
                });
            };

            minCapInput.addEventListener("input", filterRows);
            filterRows();
        }

        if (!dateInput) {
            return;
        }

        syncReserveForms();

        dateInput.addEventListener("change", syncReserveForms);
        const tramoInput = document.getElementById("tramoBusqueda");
        if (tramoInput) {
            tramoInput.addEventListener("change", syncReserveForms);
        }
    }

    function setupRegistrarIncidencia() {
        const form = document.querySelector("main.content form");
        if (!form) {
            return;
        }

        const currentUser = getCurrentUserIdentity();
        const emailInput = form.querySelector(".js-user-email");
        if (emailInput) {
            emailInput.value = currentUser.email || "";
        }
    }

    function collectDetailsFromRow(row) {
        if (!row || !row.closest("table")) {
            return [];
        }

        const headers = Array.from(row.closest("table").querySelectorAll("thead th"));
        const cells = Array.from(row.querySelectorAll("td"));
        const lines = [];

        cells.forEach(function (cell, index) {
            if (index >= headers.length) {
                return;
            }
            const headerText = headers[index].textContent.trim();
            if (headerText.toLowerCase() === "acciones" || headerText.toLowerCase() === "accion") {
                return;
            }
            const value = cell.textContent.trim();
            if (value) {
                lines.push({ label: headerText, value: value });
            }
        });

        return lines;
    }

    function collectDetailsFromArticle(article) {
        if (!article) {
            return [];
        }

        const lines = [];
        const title = article.querySelector("h3");
        if (title) {
            lines.push({ label: "Titulo", value: title.textContent.trim() });
        }

        article.querySelectorAll("p").forEach(function (p, index) {
            const value = p.textContent.trim();
            if (value) {
                lines.push({ label: "Detalle " + (index + 1), value: value });
            }
        });
        return lines;
    }

    function cycleIncidenciaStatus(article) {
        if (!article) {
            return null;
        }

        const statusTag = article.querySelector(".tag");
        if (!statusTag) {
            return null;
        }

        const current = normalizeText(statusTag.textContent);
        let next = "Pendiente";

        if (current.includes("pendient")) {
            next = "En curso";
        } else if (current.includes("curso")) {
            next = "Resuelta";
        }

        statusTag.textContent = next;
        return next;
    }

    function filterGestionReservasByAula() {
        if (!window.location.pathname.includes("/gestion-reservas/")) {
            return;
        }

        const aulaParam = new URLSearchParams(window.location.search).get("aula");
        if (!aulaParam) {
            return;
        }

        Array.from(document.querySelectorAll(".data-table tbody tr")).forEach(function (row) {
            const aula = row.cells[1] ? row.cells[1].textContent.trim() : "";
            if (aula.toLowerCase() === aulaParam.toLowerCase()) {
                row.classList.add("row-focus");
            }
        });

        showToast("Filtrado por aula: " + aulaParam, "info");
    }

    function setupResponsiveTables() {
        const tables = Array.from(document.querySelectorAll(".data-table"));
        tables.forEach(function (table) {
            const headers = Array.from(table.querySelectorAll("thead th")).map(function (th) {
                return th.textContent.trim();
            });

            Array.from(table.querySelectorAll("tbody tr")).forEach(function (row) {
                Array.from(row.querySelectorAll("td")).forEach(function (cell, index) {
                    if (!cell.getAttribute("data-label")) {
                        const label = headers[index] || "Dato";
                        cell.setAttribute("data-label", label);
                    }
                });
            });
        });
    }

    function setupMobileSidebarControls() {
        const sidebar = document.getElementById("sidebarNav");
        const hamburgerBtn = document.querySelector(".hamburger-btn");
        if (!sidebar || !hamburgerBtn) {
            return;
        }

        const setOpenState = function (isOpen) {
            sidebar.classList.toggle("open", isOpen);
            document.body.classList.toggle("sidebar-open", isOpen);
            document.body.style.overflow = isOpen ? "hidden" : "";
        };

        window.toggleSidebar = function () {
            const isOpen = !sidebar.classList.contains("open");
            setOpenState(isOpen);
        };

        document.addEventListener("click", function (event) {
            if (window.innerWidth > 1024) {
                return;
            }

            const clickedOutside = !sidebar.contains(event.target) && !hamburgerBtn.contains(event.target);
            if (clickedOutside) {
                setOpenState(false);
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && window.innerWidth <= 1024) {
                setOpenState(false);
            }
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > 1024) {
                setOpenState(false);
            }
        });
    }

    function updateAulasStats() {
        if (!window.location.pathname.includes("/gestion-aulas/")) {
            return;
        }

        const rows = Array.from(document.querySelectorAll("#tablaAulasBody tr"));
        const total = rows.length;
        let disponibles = 0;
        let mantenimiento = 0;

        rows.forEach(function (row) {
            const statusText = row.cells[3] ? row.cells[3].textContent.trim() : "";
            const normalized = normalizeText(statusText);
            if (normalized.includes("dispon")) {
                disponibles += 1;
            }
            if (normalized.includes("manten")) {
                mantenimiento += 1;
            }
        });

        const stats = document.querySelectorAll(".management-grid .stat-number");
        if (stats[0]) {
            stats[0].textContent = String(total);
        }
        if (stats[1]) {
            stats[1].textContent = String(disponibles);
        }
        if (stats[2]) {
            stats[2].textContent = String(mantenimiento);
        }
    }

    function setupGestionAulasCrud() {
        if (!window.location.pathname.includes("/gestion-aulas/")) {
            return;
        }

        const tableBody = document.getElementById("tablaAulasBody");
        const form = document.getElementById("aulaForm");
        const btnNew = document.getElementById("btnNuevaAula");
        const btnSave = document.getElementById("btnGuardarAula");
        const btnCancel = document.getElementById("btnCancelarAula");
        const editIndexInput = document.getElementById("aulaEditIndex");
        const nombreInput = document.getElementById("aulaNombre");
        const tipoInput = document.getElementById("aulaTipo");
        const capacidadInput = document.getElementById("aulaCapacidad");
        const estadoInput = document.getElementById("aulaEstado");

        if (!tableBody || !form || !btnNew || !btnSave || !btnCancel || !editIndexInput || !nombreInput || !tipoInput || !capacidadInput || !estadoInput) {
            return;
        }

        const closeForm = function () {
            form.style.display = "none";
            editIndexInput.value = "";
            nombreInput.value = "";
            tipoInput.value = "Aula normal";
            capacidadInput.value = "25";
            estadoInput.value = "Disponible";
        };

        const openFormForNew = function () {
            closeForm();
            form.style.display = "grid";
            nombreInput.focus();
        };

        const openFormForEdit = function (row) {
            if (!row) {
                return;
            }
            form.style.display = "grid";
            editIndexInput.value = row.dataset.aulaId || String(Array.from(tableBody.children).indexOf(row));
            nombreInput.value = row.cells[0] ? row.cells[0].textContent.trim() : "";
            tipoInput.value = row.cells[1] ? row.cells[1].textContent.trim() : "Aula normal";
            capacidadInput.value = row.cells[2] ? row.cells[2].textContent.trim() : "25";
            estadoInput.value = row.cells[3] ? row.cells[3].textContent.trim() : "Disponible";
            nombreInput.focus();
        };

        btnNew.addEventListener("click", openFormForNew);
        btnCancel.addEventListener("click", closeForm);

        btnSave.addEventListener("click", function (event) {
            event.preventDefault();
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            if (typeof form.requestSubmit === "function") {
                form.requestSubmit();
            } else {
                form.submit();
            }
        });

        window.openAulaFormForEdit = openFormForEdit;
        updateAulasStats();
    }

    function updateUsuariosStats() {
        if (!window.location.pathname.includes("/gestion-usuarios/")) {
            return;
        }

        const rows = Array.from(document.querySelectorAll("#tablaUsuariosBody tr"));
        const total = rows.length;
        let profesores = 0;
        let admins = 0;

        rows.forEach(function (row) {
            const roleText = row.cells[2] ? row.cells[2].textContent.trim() : "";
            const normalized = normalizeText(roleText);
            if (normalized.includes("profesor")) {
                profesores += 1;
            }
            if (normalized.includes("admin")) {
                admins += 1;
            }
        });

        const stats = document.querySelectorAll(".management-grid .stat-number");
        if (stats[0]) {
            stats[0].textContent = String(total);
        }
        if (stats[1]) {
            stats[1].textContent = String(profesores);
        }
        if (stats[2]) {
            stats[2].textContent = String(admins);
        }
    }

    function setupGestionUsuariosCrud() {
        if (!window.location.pathname.includes("/gestion-usuarios/")) {
            return;
        }

        const tableBody = document.getElementById("tablaUsuariosBody");
        const form = document.getElementById("usuarioForm");
        const btnNew = document.getElementById("btnNuevoUsuario");
        const btnSave = document.getElementById("btnGuardarUsuario");
        const btnCancel = document.getElementById("btnCancelarUsuario");
        const editIndexInput = document.getElementById("usuarioEditIndex");
        const nombreInput = document.getElementById("usuarioNombre");
        const emailInput = document.getElementById("usuarioEmail");
        const passwordInput = document.getElementById("usuarioPassword");
        const rolInput = document.getElementById("usuarioRol");
        const estadoInput = document.getElementById("usuarioEstado");

        if (!tableBody || !form || !btnNew || !btnSave || !btnCancel || !editIndexInput || !nombreInput || !emailInput || !passwordInput || !rolInput || !estadoInput) {
            return;
        }

        const closeForm = function () {
            form.style.display = "none";
            editIndexInput.value = "";
            nombreInput.value = "";
            emailInput.value = "";
            passwordInput.value = "";
            rolInput.value = "profesor";
            estadoInput.value = "Activo";
        };

        const openFormForNew = function (defaultRole) {
            closeForm();
            form.style.display = "grid";
            rolInput.value = defaultRole || "profesor";
            passwordInput.placeholder = "Opcional (si vacia: 123456)";
            nombreInput.focus();
        };

        const openFormForEdit = function (row) {
            if (!row) {
                return;
            }

            form.style.display = "grid";
            editIndexInput.value = row.dataset.userId || String(Array.from(tableBody.children).indexOf(row));
            nombreInput.value = row.cells[0] ? row.cells[0].textContent.trim() : "";
            emailInput.value = row.cells[1] ? row.cells[1].textContent.trim() : "";
            rolInput.value = normalizeText(row.cells[2] ? row.cells[2].textContent.trim() : "").includes("admin") ? "admin" : "profesor";
            estadoInput.value = row.cells[3] ? row.cells[3].textContent.trim() : "Activo";
            passwordInput.value = "";
            passwordInput.placeholder = "Deja vacio para mantener la contrasena";
            nombreInput.focus();
        };

        btnNew.addEventListener("click", function () {
            openFormForNew("profesor");
        });
        btnCancel.addEventListener("click", closeForm);

        btnSave.addEventListener("click", function () {
            if (typeof form.requestSubmit === "function") {
                form.requestSubmit();
            } else {
                form.submit();
            }
        });

        window.openUsuarioFormForEdit = openFormForEdit;
        updateUsuariosStats();
    }

    function handleTableButton(button) {
        if (button.closest("form[data-backend-save='true']")) {
            return;
        }

        const action = button.textContent.trim().toLowerCase();
        const row = button.closest("tr");
        const article = button.closest("article");
        const statusCell = row ? row.cells[row.cells.length - 2] : null;

        if (window.location.pathname.includes("/gestion-aulas/") && action.includes("editar")) {
            if (typeof window.openAulaFormForEdit === "function") {
                window.openAulaFormForEdit(row);
            }
            return;
        }

        if (window.location.pathname.includes("/gestion-usuarios/") && action.includes("editar")) {
            if (typeof window.openUsuarioFormForEdit === "function") {
                window.openUsuarioFormForEdit(row);
            }
            return;
        }

        if (action.includes("cancelar")) {
            updateStatusPill(statusCell, "Cancelada", "status-maintenance");
            showToast("Reserva cancelada.", "success");
            return;
        }

        if (action.includes("validar")) {
            updateStatusPill(statusCell, "Confirmada", "status-available");
            showToast("Reserva validada.", "success");
            return;
        }

        if (action.includes("bloquear") || action.includes("desactivar")) {
            updateStatusPill(statusCell, "Mantenimiento", "status-maintenance");
            showToast("Aula actualizada a mantenimiento.", "warning");
            updateAulasStats();
            return;
        }

        if (action.includes("reactivar")) {
            updateStatusPill(statusCell, "Activo", "status-available");
            showToast("Usuario reactivado.", "success");
            updateUsuariosStats();
            return;
        }

        if (action.includes("resolver")) {
            if (article) {
                const firstTag = article.querySelector(".tag");
                if (firstTag) {
                    firstTag.textContent = "Resuelta";
                }
            }
            showToast("Incidencia marcada como resuelta.", "success");
            return;
        }

        if (action.includes("cambiar estado")) {
            const newState = cycleIncidenciaStatus(article);
            if (!newState) {
                showToast("No se pudo actualizar el estado.", "warning");
                return;
            }

            showToast("Estado actualizado a: " + newState + ".", "success");
            return;
        }

        if (action.includes("ver") || action.includes("detalle") || action.includes("editar") || action.includes("permisos") || action.includes("mover") || action.includes("asignar") || action.includes("cambiar estado")) {
            let lines = collectDetailsFromRow(row);
            if (!lines.length) {
                lines = collectDetailsFromArticle(article);
            }
            if (!lines.length) {
                lines = [{ label: "Informacion", value: "No hay datos disponibles." }];
            }

            lines.push({ label: "Accion", value: button.textContent.trim() });
            openDetailModal("Detalle de registro", lines);
            return;
        }

        showToast("Accion ejecutada.", "info");
    }

    function setupGenericButtons() {
        document.addEventListener("click", function (event) {
            const button = event.target.closest("button.action-button, .management-actions button");
            if (!button) {
                return;
            }

            if (
                button.id === "btnNuevaAula"
                || button.id === "btnGuardarAula"
                || button.id === "btnCancelarAula"
                || button.id === "btnNuevoUsuario"
                || button.id === "btnGuardarUsuario"
                || button.id === "btnCancelarUsuario"
            ) {
                return;
            }

            if (button.closest("form[data-backend-save='true']")) {
                return;
            }

            handleTableButton(button);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        setupDetailModal();
        setupBuscarAulas();
        setupRegistrarIncidencia();
        setupGenericButtons();
        filterGestionReservasByAula();
        setupResponsiveTables();
        setupMobileSidebarControls();
        setupGestionAulasCrud();
        setupGestionUsuariosCrud();
    });
})();
