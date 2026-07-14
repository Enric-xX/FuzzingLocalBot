// ============================================================
// SCRIPT.JS
// ============================================================

document.addEventListener('DOMContentLoaded', function() {

    // Año actual en el footer
    const yearSpan = document.querySelector('.footer p');
    if (yearSpan) {
        const year = new Date().getFullYear();
        yearSpan.innerHTML = yearSpan.innerHTML.replace('2024', year);
    }

    // Mensaje de consola
    console.log('⚡ Fuzzing Bot - Landing Page');
    console.log('🔒 Recuerda usar VPN para pruebas de pentesting.');

});
