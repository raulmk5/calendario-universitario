import json
import requests

from datetime import date, timedelta

from config import API_BASE_URL, TEAM_ID, LEAGUE_ID

from generar_ics import generar_calendario

ARCHIVO_PARTIDOS = "partidos.json"


def cargar_partidos():
    with open(ARCHIVO_PARTIDOS, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos["partidos"]


def guardar_partidos(partidos):
    with open(ARCHIVO_PARTIDOS, "w", encoding="utf-8") as archivo:
        json.dump(
            {"partidos": partidos},
            archivo,
            indent=4,
            ensure_ascii=False
        )


def buscar_partidos_en_fecha(fecha):
    url = f"{API_BASE_URL}/eventsday.php"

    params = {
        "d": fecha.isoformat(),
        "l": LEAGUE_ID
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    datos = response.json()

    return datos.get("events") or []


def es_partido_de_la_u(evento):
    return (
        evento.get("idHomeTeam") == TEAM_ID
        or evento.get("idAwayTeam") == TEAM_ID
    )


partidos_guardados = cargar_partidos()

ids_guardados = {
    partido["id"]
    for partido in partidos_guardados
}

print("Partidos conocidos:", len(partidos_guardados))
print()
print("Buscando partidos nuevos...")
print()


# Empezamos desde la fecha actual
fecha_inicial = date.today()

# Revisaremos los próximos 15 días
dias_a_revisar = 15


for i in range(dias_a_revisar):

    fecha = fecha_inicial + timedelta(days=i)

    eventos = buscar_partidos_en_fecha(fecha)

    for evento in eventos:

        if not es_partido_de_la_u(evento):
            continue

        event_id = evento["idEvent"]

        print(
            "Encontrado:",
            evento["strEvent"],
            "|",
            evento["dateEvent"],
            evento["strTime"]
        )

        if event_id not in ids_guardados:

            partidos_guardados.append({
                "id": event_id
            })

            ids_guardados.add(event_id)

            print(">>> PARTIDO NUEVO GUARDADO")

        else:
            print("Ya estaba guardado.")


guardar_partidos(partidos_guardados)

print()
print("Generando calendario...")

generar_calendario()

print()
print("PROCESO COMPLETADO")