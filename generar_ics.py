import json
import requests

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from config import API_BASE_URL, TIMEZONE


ARCHIVO_PARTIDOS = "partidos.json"
ARCHIVO_ICS = "universitario.ics"


def cargar_ids():
    with open(ARCHIVO_PARTIDOS, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos["partidos"]


def obtener_partido(event_id):
    url = f"{API_BASE_URL}/lookupevent.php"

    response = requests.get(
        url,
        params={"id": event_id}
    )

    response.raise_for_status()

    eventos = response.json().get("events") or []

    if not eventos:
        return None

    return eventos[0]


def convertir_a_peru(partido):

    fecha = partido["dateEvent"]
    hora = partido["strTime"]

    fecha_utc = datetime.fromisoformat(
        f"{fecha}T{hora}"
    ).replace(
        tzinfo=ZoneInfo("UTC")
    )

    return fecha_utc.astimezone(
        ZoneInfo(TIMEZONE)
    )


def generar_calendario():

    calendario = Calendar()

    calendario.add(
        "prodid",
        "-//Calendario Universitario//ES"
    )

    calendario.add(
        "version",
        "2.0"
    )

    partidos = cargar_ids()

    for partido_guardado in partidos:

        partido = obtener_partido(
            partido_guardado["id"]
        )

        if not partido:
            continue

        inicio = convertir_a_peru(partido)

        evento = Event()

        evento.add(
            "uid",
            f'{partido["idEvent"]}@calendario-u'
        )

        evento.add(
            "summary",
            partido["strEvent"]
        )

        evento.add(
            "dtstart",
            inicio
        )

        evento.add(
            "dtend",
            inicio + timedelta(hours=2)
        )

        evento.add(
            "location",
            partido.get("strVenue") or ""
        )

        evento.add(
            "description",
            "Partido de Universitario de Deportes"
        )

        calendario.add_component(evento)

    with open(ARCHIVO_ICS, "wb") as archivo:
        archivo.write(
            calendario.to_ical()
        )

    print("Calendario ICS generado correctamente.")