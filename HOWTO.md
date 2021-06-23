# Rutas
Hay 3 rutas
## Búsquedas por texto
La ruta `/api/search` es para realizar consultas de texto dentro de todos los documentos. Este requiere 2 parametros en la ruta, `text` y `page`.
## Búsqueda general
La ruta `/api/get` es para realizar una búsqueda más general. Si se realiza la búsqueda sinningún dato, se retornará todo las 10 primeras ocurrencias (este valor se puede cambiar en el back).
Esta ruta acepta el objeto.
```
{
    "page": int,
    "from": int,
    "until": int,
    "sector": [str],
    "region": [str]
}
```
Todos los parámetros del objeto son opcionales, en caso de no incluirse uno de ellos, se asumirá un valor que no realize ningún tipo de filtrado para ese parámetro.
## Filtros
La ruta `/api/filters` retorna los valores que pueden ir dentro del objeto anterior para los parámetros `sector` y `region`.
