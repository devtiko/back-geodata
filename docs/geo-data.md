# Datos geográficos

## Qué representan los datos

División geográfica de México en estados, municipios y localidades. Cada nivel describe áreas administrativas o asentamientos y su ubicación territorial. Las geometrías permiten reconocer sus límites y su distribución espacial.

## Origen de los datos

La información proviene del Instituto Nacional de Estadística y Geografía (INEGI) y es transformada por [`etl-geodata`](https://github.com/devtiko/etl-geodata). El contenido corresponde a la información disponible en INEGI al momento de la transformación y puede cambiar cuando INEGI la actualiza.

## Campos de los registros

### Estados

| Campo | Descripción |
|---|---|
| `cvegeo` | Clave geoestadística del estado (2 caracteres). |
| `cve_ent` | Clave del estado (2 caracteres). |
| `nomgeo` | Nombre geográfico. |
| `nom_abrev` | Nombre abreviado, cuando está disponible. |
| `geometry` | Geometría `MultiPolygon`, o `null` si no se obtuvo. |

### Municipios

| Campo | Descripción |
|---|---|
| `cvegeo` | Clave geoestadística compuesta del municipio (5 caracteres). |
| `cve_ent` | Clave del estado (2 caracteres). |
| `cve_mun` | Clave del municipio dentro del estado (3 caracteres). |
| `nomgeo` | Nombre del municipio. |
| `geometry` | Geometría `MultiPolygon`, o `null` si no se obtuvo. |

### Localidades

| Campo | Descripción |
|---|---|
| `cvegeo` | Clave geoestadística compuesta de la localidad (9 caracteres). |
| `cve_ent` | Clave del estado (2 caracteres). |
| `cve_mun` | Clave del municipio (3 caracteres). |
| `cve_loc` | Clave de la localidad (4 caracteres). |
| `nomgeo` | Nombre de la localidad. |
| `latitud` | Latitud de referencia, cuando está disponible. |
| `longitud` | Longitud de referencia, cuando está disponible. |
| `geometry` | Geometría `MultiPolygon`, o `null` si no se obtuvo. |

Las coordenadas `latitud` y `longitud` son valores de referencia y no sustituyen a la geometría de la localidad.

## Geometrías

| Campo | Descripción |
|---|---|
| `type` | Tipo de geometría. En los datos procesados es `MultiPolygon`. |
| `crs` | Código de referencia espacial, cuando está disponible. |
| `coordinates` | Coordenadas anidadas que definen los polígonos y sus límites. |

## Claves y relaciones geográficas

- Las claves deben conservarse como cadenas para evitar la pérdida de ceros iniciales o alteraciones de formato.
- `cve_ent` identifica el estado.
- `cve_mun` no debe utilizarse por sí sola para identificar un municipio, ya que su clave es única dentro de cada estado. La identificación debe considerar la combinación `cve_ent` + `cve_mun`.
- `cvegeo` identifica el registro geográfico correspondiente a cada nivel.
- Las claves de cada nivel permiten relacionar estados con sus municipios y municipios con sus localidades.
- Los nombres pueden incluir acentos y se conservan como los entrega el servicio.
