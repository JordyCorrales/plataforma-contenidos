# Plataforma de Gestión y Publicación de Contenidos Digitales

## 1. Requisitos Previos e Instalación

### Herramientas del Sistema
- Docker Engine
- Docker Compose 
- Git para control de versiones

### Para Pruebas Locales Fuera de Contenedor
- Python 3.10 o superior.
- Gestor de paquetes `pip` y modulo `venv`.

### Descarga del Proyecto
Clonar el repositorio y ubicarse en el directorio

```bash
git clone https://github.com/JordyCorrales/plataforma-contenidos.git
cd plataforma-contenidos
```

---

## 2. Configuración de Variables de Entorno

El proyecto implementa un esquema de configuración desacoplado basado en variables de entorno.

### Archivo de Variables Local
Crear el archivo `.env` a partir de la plantilla declarativa `.env.example`:

```bash
cp .env.example .env
```

### Variables Configuradas
El archivo `.env` contiene los parámetros esenciales

- `POSTGRES_USER`: Usuario administrador del motor de base de datos. Valor por defecto: `editorial_user`.
- `POSTGRES_PASSWORD`: Contraseña del usuario de base de datos. Valor por defecto: `editorial_pass_local`.
- `POSTGRES_DB`: Nombre de la base de datos creada en la inicialización. Valor por defecto: `editorial_db`.
- `DATABASE_URL`: Cadena de conexión completa utilizada por los microservicios. Valor por defecto: `postgresql+psycopg2://editorial_user:editorial_pass_local@postgres-db:5432/editorial_db`.
- `JWT_SECRET_KEY`: Clave para firma y verificación de tokens JWT. Valor por defecto: `clave_secreta_desarrollo_local_cambiar_en_prod`.
- `JWT_ALGORITHM`: Algoritmo criptografico. Valor por defecto: `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de vigencia del token de sesión Valor por defecto: `60`.

Nota: El archivo `docker-compose.yml` utiliza sintaxis de interpolación `${VARIABLE:-valor_por_defecto}`, por lo que el sistema puede iniciar de forma inmediata incluso si no se ha copiado previamente el archivo `.env`.

---

## 3. Ejecución del Sistema con Docker Compose

El despliegue, la construcción de imágenes y la orquestación de redes y volúmenes se gestionan de forma centralizada con Docker Compose.

### Construcción y Puesta en Marcha de Todos los Servicios
Para construir las imágenes de los microservicios y levantar todo

```bash
docker compose up -d --build
```

### Comprobación del Estado de los Contenedores
Para verificar que los cuatro servicios se encuentren en estado activo:

```bash
docker compose ps
```

### Inspección de Registros y Logs en Tiempo Real
Para visualizar la salida unificada de todos los contenedores:

```bash
docker compose logs -f
```

Para consultar los logs de un servicio en particular:

```bash
docker compose logs -f users-service
docker compose logs -f publications-service
docker compose logs -f reader-graphql-service
docker compose logs -f postgres-db
```

### Detención e Inicio de Servicios para Pruebas
Para detener un microservicio especifico y validar la tolerancia a fallos del resto del cluster:

```bash
docker compose stop users-service
```

Para reiniciar el servicio detenido:

```bash
docker compose start users-service
```

Para recargar un servicio tras modificaciones de código:

```bash
docker compose restart reader-graphql-service
```

### Eliminar y Limpieza de Recursos
Para detener y eliminar los contenedores y redes conservando los datos persistidos en el volumen:

```bash
docker compose down
```

Para detener y purgar contenedores, redes y el volumen persistente de la base de datos:

```bash
docker compose down -v
```

---

## 4. Verificación de Servicios e Interfaces

Una vez desplegados los servicios quedan disponibles en los siguientes puertos:

### 1. Base de Datos Relacional (`postgres-db`)
- Puerto host: `5432`
- Motor: PostgreSQL 15 Alpine

### 2. Microservicio de Usuarios y Autenticación (`users-service`)
- Puerto host: `8001`
- Documentación Swagger UI: `http://localhost:8001/docs`

### 3. Microservicio de Publicaciones y Gestión Editorial (`publications-service`)
- Puerto host: `8002`
- Documentación Swagger UI: `http://localhost:8002/docs`

### 4. Microservicio de Consulta y GraphQL (`reader-graphql-service`)
- Puerto host: `8003`
- Endpoint de consultas GraphQL: `http://localhost:8003/graphql`
- Interfaz interactiva GraphiQL: abrir `http://localhost:8003/graphql` directamente en el navegador web 

---

## 5. Ejecución de Pruebas

### Ejecución del test(`test_sistema_completo.py`)
El archivo `test_sistema_completo.py` valida de forma secuencial la comunicación entre los tres microservicios, el control de acceso por roles, la persistencia en PostgreSQL, estados editoriales y la consulta de datos  en GraphQL.

#### Preparación del Entorno de Pruebas en el Host
Crear un entorno virtual de Python e instalar las dependencias de prueba:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install httpx pytest
```

#### Ejecución  con Pytest
Asegurarse de que los contenedores estén levantados (`docker compose up -d`) y ejecutar:

```bash
pytest -v test_sistema_completo.py
```

#### Desglose de Pruebas Ejecutadas
- `test_01_health_checks`: Verifica que los tres endpoints de salud respondan con codigo HTTP 200.
- `test_02_registro_y_autenticacion`: Registra un usuario `PUBLICADOR` y un `APROBADOR`, autentica ambos y extrae sus tokens JWT.
- `test_03_crear_categoria_y_publicacion`: Crea una categoría y un articulo en estado `BORRADOR` con el token del publicador.
- `test_04_maquina_de_estados_y_auditoria`: Ejecuta las transiciones `BORRADOR` -> `EN_REVISION` -> `APROBADO` -> `PUBLICADO` con el token del aprobador.
- `test_05_consulta_graphql_reader`: Ejecuta una consulta GraphQL sobre `reader-graphql-service` comprobando la publicación, su categoría y registros en el historial de auditoria.

### Pruebas Manuales 

#### Prueba Manual de Consulta en GraphiQL (`reader-graphql-service`)
1. Abrir `http://localhost:8003/graphql` en el navegador.
2. Introducir la siguiente consulta en el panel izquierdo:
   ```graphql
   query {
     listPublications(status: "PUBLICADO") {
       id
       title
       status
       category {
         name
       }
       history {
         previousStatus
         newStatus
         comments
         timestamp
       }
     }
   }
   ```
3. Presionar el botón de ejecución (Play) y confirmar que la respuesta JSON contenga los datos de las publicaciones en estado publicado junto con sus relaciones anidadas.