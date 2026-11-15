from datetime import date, timedelta

from fastapi.testclient import TestClient


# ==========================================
# 1. TESTS DE AUTORES (CRUD)
# ==========================================


def test_crud_autores(client: TestClient):
    # Alta (POST)
    res = client.post(
        "/autores",
        json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"},
    )
    assert res.status_code == 201
    autor_id = res.json()["id"]
    assert res.json()["nombre"] == "Jorge Luis Borges"

    # Consulta listado (GET)
    res_list = client.get("/autores")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # Consulta individual (GET /{id})
    res_get = client.get(f"/autores/{autor_id}")
    assert res_get.status_code == 200
    assert res_get.json()["nacionalidad"] == "Argentina"

    # Modificación parcial (PATCH) y total (PUT)
    res_patch = client.patch(
        f"/autores/{autor_id}", json={"nombre": "J. L. Borges"}
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["nombre"] == "J. L. Borges"

    res_put = client.put(
        f"/autores/{autor_id}",
        json={"nombre": "Julio Cortázar", "nacionalidad": "Argentina"},
    )
    assert res_put.status_code == 200
    assert res_put.json()["nombre"] == "Julio Cortázar"

    # Baja (DELETE)
    res_del = client.delete(f"/autores/{autor_id}")
    assert res_del.status_code == 200
    assert client.get(f"/autores/{autor_id}").status_code == 404


def test_autor_inexistente_404(client: TestClient):
    assert client.get("/autores/999").status_code == 404
    assert (
        client.patch("/autores/999", json={"nombre": "X"}).status_code == 404
    )
    assert client.delete("/autores/999").status_code == 404


# ==========================================
# 2. TESTS DE LIBROS, UNICIDAD ISBN Y RELACIÓN N-N
# ==========================================


def test_crud_libros_y_unicidad_isbn(client: TestClient):
    # Alta exitosa
    res = client.post(
        "/libros",
        json={
            "titulo": "Ficciones",
            "isbn": "978-950-04-2739-5",
            "stock": 5,
            "anio": 1944,
        },
    )
    assert res.status_code == 201
    libro_id = res.json()["id"]
    assert res.json()["autores"] == []

    # Regla 8: ISBN duplicado en creación -> 409
    res_dup = client.post(
        "/libros",
        json={
            "titulo": "Otro Libro",
            "isbn": "978-950-04-2739-5",
            "stock": 2,
            "anio": 2000,
        },
    )
    assert res_dup.status_code == 409

    # Segundo libro para probar colisión de ISBN en update
    res_2 = client.post(
        "/libros",
        json={
            "titulo": "El Aleph",
            "isbn": "978-950-04-1111-1",
            "stock": 0,
            "anio": 1949,
        },
    )
    libro_2_id = res_2.json()["id"]

    # Regla 8: ISBN duplicado en modificación -> 409
    res_upd_dup = client.patch(
        f"/libros/{libro_2_id}", json={"isbn": "978-950-04-2739-5"}
    )
    assert res_upd_dup.status_code == 409

    # Modificación válida (PUT y PATCH)
    assert (
        client.patch(f"/libros/{libro_id}", json={"stock": 10}).status_code
        == 200
    )
    assert (
        client.put(
            f"/libros/{libro_id}",
            json={
                "titulo": "Ficciones (Ed. Especial)",
                "isbn": "978-950-04-2739-5",
                "stock": 4,
                "anio": 1944,
            },
        ).status_code
        == 200
    )

    # Filtro de libros disponibles (GET /libros?disponibles=true)
    disponibles = client.get("/libros?disponibles=true").json()
    assert len(disponibles) == 1
    assert disponibles[0]["id"] == libro_id

    no_disponibles = client.get("/libros?disponibles=false").json()
    assert len(no_disponibles) == 1
    assert no_disponibles[0]["id"] == libro_2_id

    todos = client.get("/libros").json()
    assert len(todos) == 2

    # Baja
    assert client.delete(f"/libros/{libro_2_id}").status_code == 200
    assert client.get(f"/libros/{libro_2_id}").status_code == 404


def test_asociar_autor_a_libro_n_a_n(client: TestClient):
    autor1 = client.post(
        "/autores",
        json={"nombre": "Bioy Casares", "nacionalidad": "Argentina"},
    ).json()
    autor2 = client.post(
        "/autores",
        json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"},
    ).json()
    libro = client.post(
        "/libros",
        json={
            "titulo": "Seis problemas para don Isidro Parodi",
            "isbn": "ISBN-BORGES-BIOY",
            "stock": 3,
            "anio": 1942,
        },
    ).json()

    # Asociar autor 1 y autor 2 al libro
    res1 = client.post(f"/libros/{libro['id']}/autores/{autor1['id']}")
    assert res1.status_code == 200
    assert len(res1.json()["autores"]) == 1

    res2 = client.post(f"/libros/{libro['id']}/autores/{autor2['id']}")
    assert res2.status_code == 200
    autores_resp = res2.json()["autores"]
    assert len(autores_resp) == 2
    assert {a["nombre"] for a in autores_resp} == {
        "Bioy Casares",
        "Jorge Luis Borges",
    }

    # Asociar el mismo autor dos veces -> 409 Conflict
    res_dup = client.post(f"/libros/{libro['id']}/autores/{autor1['id']}")
    assert res_dup.status_code == 409

    # Libro o autor inexistente -> 404 Not Found
    assert (
        client.post(f"/libros/999/autores/{autor1['id']}").status_code == 404
    )
    assert client.post(f"/libros/{libro['id']}/autores/999").status_code == 404


# ==========================================
# 3. TESTS DE SOCIOS Y UNICIDAD DE EMAIL
# ==========================================


def test_crud_socios_y_unicidad_email(client: TestClient):
    res = client.post(
        "/socios",
        json={"nombre": "Ana García", "email": "ana@example.com", "activo": True},
    )
    assert res.status_code == 201
    socio_id = res.json()["id"]

    # Regla 8: Email duplicado -> 409
    res_dup = client.post(
        "/socios",
        json={"nombre": "Otra Ana", "email": "ana@example.com", "activo": True},
    )
    assert res_dup.status_code == 409

    # Segundo socio
    res_2 = client.post(
        "/socios",
        json={"nombre": "Juan Pérez", "email": "juan@example.com", "activo": True},
    )
    socio_2_id = res_2.json()["id"]

    # Colisión de email en update -> 409
    assert (
        client.patch(
            f"/socios/{socio_2_id}", json={"email": "ana@example.com"}
        ).status_code
        == 409
    )

    # PUT y PATCH válidos
    assert (
        client.patch(
            f"/socios/{socio_id}", json={"nombre": "Ana M. García"}
        ).status_code
        == 200
    )
    assert (
        client.put(
            f"/socios/{socio_id}",
            json={
                "nombre": "Ana María García",
                "email": "ana@example.com",
                "activo": True,
            },
        ).status_code
        == 200
    )

    # Listado y detalle
    assert len(client.get("/socios").json()) == 2
    assert client.get(f"/socios/{socio_id}").status_code == 200

    # Delete y 404
    assert client.delete(f"/socios/{socio_2_id}").status_code == 200
    assert client.get(f"/socios/{socio_2_id}").status_code == 404
    assert client.get("/socios/999").status_code == 404


# ==========================================
# 4. TESTS DE REGLAS DE NEGOCIO DE PRÉSTAMOS
# ==========================================


def test_prestamo_exitoso_plazo_14_dias_y_descuento_stock(client: TestClient):
    socio = client.post(
        "/socios",
        json={"nombre": "Socio Lector", "email": "lector@example.com"},
    ).json()
    libro = client.post(
        "/libros",
        json={
            "titulo": "Rayuela",
            "isbn": "ISBN-RAYUELA",
            "stock": 2,
            "anio": 1963,
        },
    ).json()

    fecha_inicio = date(2026, 5, 1)
    res = client.post(
        "/prestamos",
        json={
            "socio_id": socio["id"],
            "libro_id": libro["id"],
            "fecha_prestamo": fecha_inicio.isoformat(),
        },
    )
    assert res.status_code == 201
    prestamo = res.json()

    # Regla 4: Plazo de 14 días exactos
    assert (
        prestamo["fecha_vencimiento"]
        == (fecha_inicio + timedelta(days=14)).isoformat()
    )
    assert prestamo["fecha_devolucion"] is None
    assert prestamo["multa"] == 0.0

    # Regla 2: Se descontó 1 unidad del stock
    libro_actualizado = client.get(f"/libros/{libro['id']}").json()
    assert libro_actualizado["stock"] == 1


def test_regla_1_limite_3_prestamos_activos(client: TestClient):
    socio = client.post(
        "/socios",
        json={"nombre": "Socio Voraz", "email": "voraz@example.com"},
    ).json()
    libro = client.post(
        "/libros",
        json={
            "titulo": "Cien años de soledad",
            "isbn": "ISBN-100",
            "stock": 10,
            "anio": 1967,
        },
    ).json()

    # Registrar 3 préstamos activos (permitido)
    for _ in range(3):
        r = client.post(
            "/prestamos",
            json={"socio_id": socio["id"], "libro_id": libro["id"]},
        )
        assert r.status_code == 201

    # El 4to préstamo activo debe fallar con 409 Conflict
    r_cuarto = client.post(
        "/prestamos",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert r_cuarto.status_code == 409

    # Verificar endpoint GET /socios/{id}/prestamos?activos=true
    activos = client.get(f"/socios/{socio['id']}/prestamos?activos=true").json()
    assert len(activos) == 3

    # Si devuelve uno, puede volver a pedir otro
    prestamo_a_devolver = activos[0]["id"]
    client.post(f"/prestamos/{prestamo_a_devolver}/devolucion")

    activos_luego = client.get(
        f"/socios/{socio['id']}/prestamos?activos=true"
    ).json()
    assert len(activos_luego) == 2

    inactivos_luego = client.get(
        f"/socios/{socio['id']}/prestamos?activos=false"
    ).json()
    assert len(inactivos_luego) == 1

    r_nuevo = client.post(
        "/prestamos",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert r_nuevo.status_code == 201


def test_regla_2_no_prestar_libro_sin_stock(client: TestClient):
    socio = client.post(
        "/socios",
        json={"nombre": "Socio Stock", "email": "stock@example.com"},
    ).json()
    libro = client.post(
        "/libros",
        json={
            "titulo": "Libro Agotado",
            "isbn": "ISBN-AGOTADO",
            "stock": 0,
            "anio": 2020,
        },
    ).json()

    res = client.post(
        "/prestamos",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert res.status_code == 409


def test_regla_3_socio_inactivo_no_puede_pedir_prestamos(client: TestClient):
    socio = client.post(
        "/socios",
        json={
            "nombre": "Socio Inactivo",
            "email": "inactivo@example.com",
            "activo": False,
        },
    ).json()
    libro = client.post(
        "/libros",
        json={
            "titulo": "Libro Disponible",
            "isbn": "ISBN-DISP",
            "stock": 5,
            "anio": 2021,
        },
    ).json()

    res = client.post(
        "/prestamos",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert res.status_code == 403


def test_regla_5_y_6_devolucion_a_tiempo_con_atraso_y_doble_devolucion(
    client: TestClient,
):
    socio = client.post(
        "/socios",
        json={"nombre": "Socio Multas", "email": "multas@example.com"},
    ).json()
    libro = client.post(
        "/libros",
        json={
            "titulo": "El Túnel",
            "isbn": "ISBN-TUNEL",
            "stock": 2,
            "anio": 1948,
        },
    ).json()

    # Caso A: Devolución a tiempo (multa = 0)
    fecha_p1 = date(2026, 3, 1)
    p1 = client.post(
        "/prestamos",
        json={
            "socio_id": socio["id"],
            "libro_id": libro["id"],
            "fecha_prestamo": fecha_p1.isoformat(),
        },
    ).json()

    # Devuelve exactamente el día de vencimiento (15 de marzo)
    res_dev1 = client.post(
        f"/prestamos/{p1['id']}/devolucion",
        json={"fecha_devolucion": "2026-03-15"},
    )
    assert res_dev1.status_code == 200
    assert res_dev1.json()["multa"] == 0.0
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 2

    # Regla 6: No se puede devolver un préstamo ya devuelto -> 409
    res_doble = client.post(f"/prestamos/{p1['id']}/devolucion")
    assert res_doble.status_code == 409

    # Caso B: Devolución con 5 días de atraso (multa = 5 * $100 = $500)
    p2 = client.post(
        "/prestamos",
        json={
            "socio_id": socio["id"],
            "libro_id": libro["id"],
            "fecha_prestamo": "2026-03-01",
        },
    ).json()
    # Vence 2026-03-15; devuelve 2026-03-20 (5 días tarde)
    res_dev2 = client.post(
        f"/prestamos/{p2['id']}/devolucion",
        json={"fecha_devolucion": "2026-03-20"},
    )
    assert res_dev2.status_code == 200
    assert res_dev2.json()["multa"] == 500.0
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 2


def test_regla_7_recursos_inexistentes_en_prestamos(client: TestClient):
    assert (
        client.post(
            "/prestamos", json={"socio_id": 999, "libro_id": 1}
        ).status_code
        == 404
    )
    socio = client.post(
        "/socios",
        json={"nombre": "Socio X", "email": "x@example.com"},
    ).json()
    assert (
        client.post(
            "/prestamos", json={"socio_id": socio["id"], "libro_id": 999}
        ).status_code
        == 404
    )
    assert client.post("/prestamos/999/devolucion").status_code == 404
    assert client.get("/prestamos/999").status_code == 404
    assert client.get("/socios/999/prestamos").status_code == 404
