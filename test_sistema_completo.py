# Generador de identificadores unicos universales para pruebas
import uuid
# Cliente HTTP para realizar peticiones REST y GraphQL
import httpx
# Framework de pruebas automatizadas
import pytest

# URL base del microservicio de autenticacion y usuarios
USERS_URL = "http://localhost:8001"
# URL base del microservicio editorial de publicaciones
PUBS_URL = "http://localhost:8002"
# URL base del microservicio de lectura y consultas GraphQL
READER_URL = "http://localhost:8003"

# Cliente HTTP compartido con tiempo limite de espera de 10 segundos
client = httpx.Client(timeout=10.0)

# Diccionario de estado compartido entre las etapas de la prueba
context = {}


# Prueba de disponibilidad y sondeo de salud de los tres microservicios
def test_01_health_checks():
    # Consulta de salud operativa en users-service
    r1 = client.get(f"{USERS_URL}/health")
    # Consulta de salud operativa en publications-service
    r2 = client.get(f"{PUBS_URL}/health")
    # Consulta de salud operativa en reader-graphql-service
    r3 = client.get(f"{READER_URL}/health")

    # Verifica respuesta HTTP 200 en users-service
    assert r1.status_code == 200, f"Error en users-service: {r1.text}"
    # Verifica respuesta HTTP 200 en publications-service
    assert r2.status_code == 200, f"Error en publications-service: {r2.text}"
    # Verifica respuesta HTTP 200 en reader-graphql-service
    assert r3.status_code == 200, f"Error en reader-graphql-service: {r3.text}"


# Prueba de registro de usuarios y obtencion de tokens JWT para cada rol
def test_02_registro_y_autenticacion():
    # Genera sufijo aleatorio para evitar colisiones de usuarios en reejecuciones
    uid = uuid.uuid4().hex[:6]

    # 1. Definicion de credenciales y registro del usuario publicador
    pub_username = f"publicador_{uid}"
    # Correo electronico unico para el publicador
    pub_email = f"pub_{uid}@test.com"
    # Estructura del cuerpo de la peticion para registro de publicador
    pub_data = {
        "username": pub_username,
        "email": pub_email,
        "password": "Password123!",
        "role": "PUBLICADOR",
    }
    # Envio de peticion POST para dar de alta al publicador
    r_reg_pub = client.post(f"{USERS_URL}/api/users/register", json=pub_data)
    # Comprueba que el usuario publicador se haya creado con codigo 201
    assert r_reg_pub.status_code == 201

    # 2. Inicio de sesion del publicador con credenciales en formato JSON
    login_payload_json = {
        "username": pub_username,
        "email": pub_email,
        "password": "Password123!",
    }
    # Envio de peticion POST de autenticacion para publicador
    r_log_pub = client.post(f"{USERS_URL}/api/users/login", json=login_payload_json)

    # Mecanismo de reintento si el endpoint espera datos en formato formulario
    if r_log_pub.status_code == 422:
        # Reintento con correo electronico como nombre de usuario en form-data
        r_log_pub = client.post(
            f"{USERS_URL}/api/users/login",
            data={"username": pub_email, "password": "Password123!"},
        )
        # Reintento con nombre de usuario en form-data si el anterior falla
        if r_log_pub.status_code == 422:
            r_log_pub = client.post(
                f"{USERS_URL}/api/users/login",
                data={"username": pub_username, "password": "Password123!"},
            )

    # Confirma que el inicio de sesion retorne HTTP 200 OK
    assert (
        r_log_pub.status_code == 200
    ), f"Fallo login publicador ({r_log_pub.status_code}): {r_log_pub.text}"
    # Guarda el token de acceso JWT del publicador en el contexto compartido
    context["token_pub"] = r_log_pub.json()["access_token"]

    # 3. Definicion de credenciales y registro del usuario aprobador
    aprob_username = f"aprobador_{uid}"
    # Correo electronico unico para el aprobador
    aprob_email = f"aprob_{uid}@test.com"
    # Estructura del cuerpo de la peticion para registro de aprobador
    aprob_data = {
        "username": aprob_username,
        "email": aprob_email,
        "password": "Password123!",
        "role": "APROBADOR",
    }
    # Envio de peticion POST para registrar al aprobador
    r_reg_aprob = client.post(f"{USERS_URL}/api/users/register", json=aprob_data)
    # Comprueba que el usuario aprobador se haya creado con codigo 201
    assert r_reg_aprob.status_code == 201

    # 4. Inicio de sesion del aprobador con credenciales en formato JSON
    login_payload_aprob = {
        "username": aprob_username,
        "email": aprob_email,
        "password": "Password123!",
    }
    # Envio de peticion POST de autenticacion para aprobador
    r_log_aprob = client.post(
        f"{USERS_URL}/api/users/login", json=login_payload_aprob
    )

    # Mecanismo de reintento si el endpoint espera formato formulario
    if r_log_aprob.status_code == 422:
        # Reintento con correo electronico en form-data
        r_log_aprob = client.post(
            f"{USERS_URL}/api/users/login",
            data={"username": aprob_email, "password": "Password123!"},
        )
        # Reintento con nombre de usuario en form-data
        if r_log_aprob.status_code == 422:
            r_log_aprob = client.post(
                f"{USERS_URL}/api/users/login",
                data={"username": aprob_username, "password": "Password123!"},
            )

    # Confirma que el inicio de sesion del aprobador retorne HTTP 200 OK
    assert (
        r_log_aprob.status_code == 200
    ), f"Fallo login aprobador ({r_log_aprob.status_code}): {r_log_aprob.text}"
    # Guarda el token de acceso JWT del aprobador en el contexto compartido
    context["token_aprob"] = r_log_aprob.json()["access_token"]


    # Prueba de creacion de categoria tematica y articulo inicial en borrador
    def test_03_crear_categoria_y_publicacion():
        # Cabecera de autorizacion HTTP Bearer con el token del publicador
        headers_pub = {"Authorization": f"Bearer {context['token_pub']}"}

        # Payload para creacion de categoria con nombre unico
        cat_payload = {
            "name": f"Categoria_{uuid.uuid4().hex[:5]}",
            "description": "Categoria de prueba automatizada",
        }
        # Envio de peticion POST para dar de alta la categoria editorial
        r_cat = client.post(
            f"{PUBS_URL}/api/publications/categories",
            headers=headers_pub,
            json=cat_payload,
        )
        # Verifica creacion exitosa de la categoria con codigo 201
        assert r_cat.status_code == 201
        # Extrae el identificador unico de la categoria creada
        cat_id = r_cat.json()["id"]

        # Payload del articulo asociado a la categoria creada
        pub_payload = {
            "title": "Prueba de Integracion E2E",
            "content": "Validando arquitectura de microservicios con pytest.",
            "category_id": cat_id,
        }
        # Envio de peticion POST para crear la publicacion
        r_pub = client.post(
            f"{PUBS_URL}/api/publications/",
            headers=headers_pub,
            json=pub_payload,
        )
        # Comprueba que la publicacion se cree con codigo 201
        assert r_pub.status_code == 201
        # Deserializa la respuesta de la publicacion
        pub_data = r_pub.json()
        # Verifica la regla de negocio: la publicacion debe nacer en estado BORRADOR
        assert pub_data["status"] == "BORRADOR"
        # Almacena el identificador de la publicacion en el contexto compartido
        context["pub_id"] = pub_data["id"]


    # Prueba de transiciones en la maquina de estados y generacion de auditoria
    def test_04_maquina_de_estados_y_auditoria():
        # Recupera el identificador de la publicacion creada
        pub_id = context["pub_id"]
        # Cabecera de autorizacion HTTP Bearer con el token del aprobador
        headers_aprob = {"Authorization": f"Bearer {context['token_aprob']}"}

        # 1. Transicion de estado: enviar publicacion a revision editorial
        r_rev = client.patch(
            f"{PUBS_URL}/api/publications/{pub_id}/status",
            headers=headers_aprob,
            json={"new_status": "EN_REVISION", "comments": "Pasa a revision editorial"},
        )
        # Valida que la transicion a revision responda HTTP 200 OK
        assert r_rev.status_code == 200, f"Error en EN_REVISION: {r_rev.text}"
        # Confirma que el estado actual sea EN_REVISION
        assert r_rev.json()["status"] == "EN_REVISION"

        # 2. Transicion de estado: aprobador valida y aprueba el contenido
        r_apr = client.patch(
            f"{PUBS_URL}/api/publications/{pub_id}/status",
            headers=headers_aprob,
            json={"new_status": "APROBADO", "comments": "Aprobado sin correcciones"},
        )
        # Valida que la aprobacion responda HTTP 200 OK
        assert r_apr.status_code == 200, f"Error en APROBADO: {r_apr.text}"
        # Confirma que el estado actual sea APROBADO
        assert r_apr.json()["status"] == "APROBADO"

        # 3. Transicion de estado: aprobador publica el articulo formalmente
        r_pub = client.patch(
            f"{PUBS_URL}/api/publications/{pub_id}/status",
            headers=headers_aprob,
            json={"new_status": "PUBLICADO", "comments": "Lanzamiento oficial"},
        )
        # Valida que la publicacion final responda HTTP 200 OK
        assert r_pub.status_code == 200, f"Error en PUBLICADO: {r_pub.text}"
        # Confirma que el estado actual sea PUBLICADO
        assert r_pub.json()["status"] == "PUBLICADO"


    # Prueba de consulta desacoplada via GraphQL consumiendo reader-graphql-service
    def test_05_consulta_graphql_reader():
        # Recupera el identificador de la publicacion desde el contexto
        pub_id = context["pub_id"]

        # Documento GraphQL solicitando datos del articulo, categoria e historial
        gql_query = f"""
        query {{
          getPublication(publicationId: {pub_id}) {{
            id
            title
            status
            category {{
              name
            }}
            history {{
              previousStatus
              newStatus
              comments
            }}
          }}
        }}
        """
        # Envia la consulta mediante peticion POST al endpoint de GraphQL
        res = client.post(f"{READER_URL}/graphql", json={"query": gql_query})
        # Verifica que la API de GraphQL responda con codigo 200 OK
        assert res.status_code == 200

        # Extrae el objeto retornado por el resolver getPublication
        data = res.json().get("data", {}).get("getPublication")
        # Valida que la publicacion exista y no sea nula
        assert data is not None
        # Confirma que el identificador coincida con el solicitado
        assert data["id"] == pub_id
        # Confirma que el estado reportado sea PUBLICADO
        assert data["status"] == "PUBLICADO"
        # Valida que la relacion con la categoria haya sido resuelta en el grafo
        assert data["category"]["name"] is not None
        # Verifica la trazabilidad: debe contener al menos 3 registros en historial
        assert len(data["history"]) >= 3