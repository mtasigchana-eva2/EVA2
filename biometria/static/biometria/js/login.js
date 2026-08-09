document.addEventListener("DOMContentLoaded", () => {

    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const contexto = canvas.getContext("2d");
    const boton = document.getElementById("ingresar");

    navigator.mediaDevices
        .getUserMedia({
            video: true
        })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(error => {
            alert("No fue posible acceder a la cámara.");
            console.error(error);
        });

    boton.addEventListener("click", async () => {

        const username = document.getElementById("username").value.trim();

        if (username === "") {
            alert("Ingrese su usuario.");
            return;
        }

        contexto.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );

        const imagen = canvas.toDataURL("image/png");

        const datos = new FormData();

        datos.append("username", username);
        datos.append("imagen", imagen);

        try {

            const respuesta = await fetch("/biometria/login/", {
                method: "POST",
                body: datos,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            });

            const resultado = await respuesta.json();

            if (resultado.ok) {

                alert("Bienvenido " + username);

                window.location.href = resultado.redirect_url;

            } else {

                alert(resultado.error);

            }

        } catch (error) {

            console.error(error);

            alert("Error al conectar con el servidor.");

        }

    });

});


function getCookie(nombre) {

    let valor = null;

    if (document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(nombre + "=")) {

                valor = decodeURIComponent(
                    cookie.substring(nombre.length + 1)
                );

                break;

            }

        }

    }

    return valor;

}