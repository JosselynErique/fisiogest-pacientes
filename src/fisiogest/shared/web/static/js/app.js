// Confirmación para acciones sensibles: <form data-confirmar="¿Seguro?">
document.addEventListener("submit", (evento) => {
    const mensaje = evento.target.dataset.confirmar;
    if (mensaje && !window.confirm(mensaje)) {
        evento.preventDefault();
    }
});

// Envío automático de filtros: <select data-autoenviar>
document.addEventListener("change", (evento) => {
    if (evento.target.matches("[data-autoenviar]")) {
        evento.target.form.submit();
    }
});

// Botón de impresión: <button data-imprimir>
document.addEventListener("click", (evento) => {
    if (evento.target.matches("[data-imprimir]")) {
        window.print();
    }
});
