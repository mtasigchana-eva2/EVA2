const video=document.getElementById("video");

const canvas=document.getElementById("canvas");

const contexto=canvas.getContext("2d");

document

.getElementById("btnCamara")

.onclick=async()=>{

const stream=await navigator.mediaDevices.getUserMedia({

video:true

});

video.srcObject=stream;

}


document

.getElementById("capturar")

.onclick=async()=>{

contexto.drawImage(

video,

0,

0,

640,

480

);

const imagen=canvas.toDataURL("image/png");


const datos=new FormData();

datos.append(

"imagen",

imagen

);


await fetch(

"/biometria/guardar/",

{

method:"POST",

body:datos,

headers:{

"X-CSRFToken":getCookie("csrftoken")

}

}

);

alert("Rostro registrado correctamente.");

location.reload();

}


function getCookie(nombre){

let valor=null;

if(document.cookie!=""){

const cookies=document.cookie.split(";");

for(let cookie of cookies){

cookie=cookie.trim();

if(cookie.startsWith(nombre+"=")){

valor=decodeURIComponent(

cookie.substring(nombre.length+1)

);

break;

}

}

}

return valor;

}