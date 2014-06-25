

//----------------------------------------------------------------------------------------------------------------------------------------------

function parserDecimal_a(numero) {

    var numero;
    //Para formatos  1.254.783,2

    numero = numero.replace('.','');  // Convierto los puntos en vacios teniendo en cuenta que normalmente los datos de los bancos son 1.238.223,27
    numero = numero.replace('.','');  // Lo hago dos veces porque en las cantidades de más de un millón hay dos puntos.
    numero = numero.replace(',','.');  // Convierto las comas en puntos
    numero = numero.replace("'",'.');  // Convierto las comillas simples en puntos

    var val = parseFloat(numero);

    //if (isNaN(val)) {
    //val =  '0.00';
    //}


    return val;

}

//----------------------------------------------------------------------------------------------------------------------------------------------

function parserDecimal_b(numero) {

    var numero;
    //Para formatos 1,353,037.30

    numero = numero.replace(',','');  // Convierto las comas en vacios teniendo en cuenta que normalmente los datos de los bancos son 1,353,037.30
    numero = numero.replace(',','');  // Lo hago dos veces porque en las cantidades de más de un millón hay dos puntos.

    var val = parseFloat(numero);

    //if (isNaN(val)) {
    //val =  '0.00';
    //}


    return val;

}

//----------------------------------------------------------------------------------------------------------------------------------------------

function prueba(ide) {

    var elemento     = document.getElementById(ide).value;



    document.getElementById(ide).value = elemento;

}

//----------------------------------------------------------------------------------------------------------------------------------------------

function formatear(ide) {

    var elemento     = document.getElementById(ide).value;
    var n_caracteres = elemento.length;
    var comienzo     = n_caracteres - 2;
    var posicion     = elemento.indexOf(".");
    var resta        = n_caracteres - posicion;

    //var prueba       = elemento.indexOf(".")
    //alert(posicion)

    if (posicion >= 5) { // Entonces tiene un formato así: 1,353,037.30 y la posición puede ir desde la 5 hasta la 9 para el millon.
        elemento  = parserDecimal_b(elemento);  // el "." no esta en la posicion penultima o antepenultima 1000.05 ó 1000.5 y hace falta parsearlo por primera vez.
        //alert('parserDecimal_b')
    } else { // Entonces tiene un formato así: 1.254.783,2 y la posición puede ir desde la 1 hasta la 3 para el millon.
        //alert('parserDecimal_a')
        elemento  = parserDecimal_a(elemento);
    }

    document.getElementById(ide).value = elemento;

}

//----------------------------------------------------------------------------------------------------------------------------------------------

function unformatNumber(num) {
   return num.replace(/([^0-9\.\-])/g,'')*1;
}

//----------------------------------------------------------------------------------------------------------------------------------------------

function dar_formato(ide){

    var num    = document.getElementById(ide).value;
    var cadena = ""; var aux;

    var cont = 1,m,k;

    if(num<0) aux=1; else aux=0;

    num=num.toString();



    for(m=num.length-1; m>=0; m--){

     cadena = num.charAt(m) + cadena;

     if(cont%3 == 0 && m >aux)  cadena = "." + cadena; else cadena = cadena;

     if(cont== 3) cont = 1; else cont++;

    }

    cadena = cadena.replace(/.,/,",");

    //return cadena;
    document.getElementById(ide).value = cadena;

}


function desformatear(ide) {

    var num = document.getElementById(ide).value;
    var decimal = num.replace(/([^0-9\.\-])/g,'')*1;

    document.getElementById(ide).value = decimal;
}
