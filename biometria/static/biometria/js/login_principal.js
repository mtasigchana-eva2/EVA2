document.addEventListener("DOMContentLoaded", () => {

    const boton = document.getElementById("btnBiometrico");

    boton.addEventListener("click", () => {

        window.location.href = "/biometria/login/";

    });

});