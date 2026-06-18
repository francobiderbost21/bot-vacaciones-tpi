"""
Bot simulador de Gestion de Vacaciones
Tecnicatura Universitaria en Programacion - Organizacion Empresarial

Implementa una Maquina de Estados que sigue el flujo definido en el
diagrama BPMN 2.0 (proceso "to-be"). Persiste datos en archivos CSV
que actuan como base de datos simulada.
"""

import csv
import os
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# Configuracion y rutas de archivos (base de datos simulada en CSV)
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_EMPLEADOS = os.path.join(BASE_DIR, "empleados.csv")
ARCHIVO_SUPERVISORES = os.path.join(BASE_DIR, "supervisores.csv")
ARCHIVO_SOLICITUDES = os.path.join(BASE_DIR, "solicitudes.csv")

MAX_INTENTOS = 3

# ------------------------------------------------------------------
# Estados de la Maquina de Estados (deben coincidir con el
# diccionario de datos / tabla de estados del informe)
# ------------------------------------------------------------------
INICIO = "INICIO"
IDENTIFICADO = "IDENTIFICADO"
INGRESO_FECHAS = "INGRESO_FECHAS"
FECHA_INICIO_OK = "FECHA_INICIO_OK"
CALCULANDO = "CALCULANDO"
CONFIRMANDO = "CONFIRMANDO"
REGISTRADO = "REGISTRADO"
SIN_SALDO = "SIN_SALDO"
CANCELADO = "CANCELADO"
ERROR_LIMITE = "ERROR_LIMITE"
FIN = "FIN"


# ------------------------------------------------------------------
# Acceso a datos (simulacion de base de datos con CSV)
# ------------------------------------------------------------------
def leer_empleados():
    with open(ARCHIVO_EMPLEADOS, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def buscar_empleado(legajo):
    for emp in leer_empleados():
        if emp["legajo"].strip().upper() == legajo.strip().upper():
            return emp
    return None


def siguiente_id_solicitud():
    if not os.path.exists(ARCHIVO_SOLICITUDES):
        return "SOL-0001"
    with open(ARCHIVO_SOLICITUDES, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return f"SOL-{len(filas) + 1:04d}"


def guardar_solicitud(solicitud):
    existe = os.path.exists(ARCHIVO_SOLICITUDES) and os.path.getsize(ARCHIVO_SOLICITUDES) > 0
    campos = ["id_solicitud", "legajo_empleado", "fecha_inicio", "fecha_fin",
              "dias_solicitados", "estado", "fecha_solicitud", "observaciones"]
    with open(ARCHIVO_SOLICITUDES, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            writer.writeheader()
        writer.writerow(solicitud)


# ------------------------------------------------------------------
# Validaciones (camino infeliz / unhappy path)
# ------------------------------------------------------------------
def parsear_fecha(texto):
    """Devuelve un date si el formato DD/MM/AAAA es valido, o None."""
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError):
        return None


def calcular_dias_habiles(fecha_inicio, fecha_fin):
    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5:  # 0=lunes ... 4=viernes
            dias += 1
        actual += timedelta(days=1)
    return dias


def es_respuesta_si(texto):
    return texto.strip().upper() == "S"


def es_respuesta_no(texto):
    return texto.strip().upper() == "N"


# ------------------------------------------------------------------
# Comandos globales disponibles en cualquier paso
# ------------------------------------------------------------------
def es_comando_global(texto):
    return texto.strip().upper() in ("CANCELAR", "AYUDA", "SALIR")


def manejar_comando_global(texto, estado_actual):
    comando = texto.strip().upper()
    if comando == "SALIR":
        print("BOT: Sesion cerrada. Hasta luego.")
        return FIN, True
    if comando == "CANCELAR":
        print("BOT: Solicitud cancelada. No se realizaron cambios. ¡Hasta pronto!")
        return CANCELADO, True
    if comando == "AYUDA":
        print(f"BOT: Se encuentra en el paso '{estado_actual}'. "
              f"Comandos disponibles: CANCELAR, AYUDA, SALIR.")
        return estado_actual, False
    return estado_actual, False


# ------------------------------------------------------------------
# Maquina de Estados principal
# ------------------------------------------------------------------
def ejecutar_bot():
    print("BOT: ¡Bienvenido al sistema de Gestion de Vacaciones!")
    print("BOT: En cualquier momento puede escribir AYUDA, CANCELAR o SALIR.\n")

    estado = INICIO
    contexto = {
        "legajo": None,
        "empleado": None,
        "fecha_inicio": None,
        "fecha_fin": None,
        "dias_solicitados": None,
        "intentos": 0,
    }

    while estado != FIN and estado != CANCELADO and estado != ERROR_LIMITE \
            and estado != REGISTRADO and estado != SIN_SALDO:

        # --------------------- INICIO ---------------------
        if estado == INICIO:
            entrada = input("BOT: Por favor ingrese su legajo de empleado: ")
            if es_comando_global(entrada):
                estado, salir = manejar_comando_global(entrada, estado)
                if salir:
                    break
                continue

            empleado = buscar_empleado(entrada)
            if empleado is None:
                contexto["intentos"] += 1
                if contexto["intentos"] >= MAX_INTENTOS:
                    estado = ERROR_LIMITE
                else:
                    print(f"BOT: Legajo no encontrado. Verifique e ingrese "
                          f"nuevamente (intento {contexto['intentos']}/{MAX_INTENTOS}).")
                continue

            contexto["legajo"] = entrada.strip().upper()
            contexto["empleado"] = empleado
            contexto["intentos"] = 0
            estado = IDENTIFICADO

        # --------------------- IDENTIFICADO ---------------------
        elif estado == IDENTIFICADO:
            emp = contexto["empleado"]
            print(f"BOT: Hola, {emp['nombre']}. Usted tiene "
                  f"{emp['dias_disponibles']} dias disponibles.")
            entrada = input("BOT: ¿Desea solicitar vacaciones? (S/N): ")
            if es_comando_global(entrada):
                estado, salir = manejar_comando_global(entrada, estado)
                if salir:
                    break
                continue

            if es_respuesta_si(entrada):
                estado = INGRESO_FECHAS
            elif es_respuesta_no(entrada):
                print("BOT: De acuerdo. ¡Hasta pronto!")
                estado = FIN
            else:
                print("BOT: Por favor responda unicamente con S (si) o N (no).")

        # --------------------- INGRESO_FECHAS ---------------------
        elif estado == INGRESO_FECHAS:
            entrada = input("BOT: Ingrese la fecha de inicio (DD/MM/AAAA): ")
            if es_comando_global(entrada):
                estado, salir = manejar_comando_global(entrada, estado)
                if salir:
                    break
                continue

            fecha_inicio = parsear_fecha(entrada)
            if fecha_inicio is None:
                contexto["intentos"] += 1
                if contexto["intentos"] >= MAX_INTENTOS:
                    estado = ERROR_LIMITE
                else:
                    print(f"BOT: Formato invalido. Use DD/MM/AAAA "
                          f"(ej. 10/02/2026). Intento {contexto['intentos']}/{MAX_INTENTOS}.")
                continue

            contexto["fecha_inicio"] = fecha_inicio
            contexto["intentos"] = 0
            print("BOT: Fecha de inicio registrada.")
            estado = FECHA_INICIO_OK

        # --------------------- FECHA_INICIO_OK ---------------------
        elif estado == FECHA_INICIO_OK:
            entrada = input("BOT: Ingrese la fecha de fin (DD/MM/AAAA): ")
            if es_comando_global(entrada):
                estado, salir = manejar_comando_global(entrada, estado)
                if salir:
                    break
                continue

            fecha_fin = parsear_fecha(entrada)
            if fecha_fin is None:
                contexto["intentos"] += 1
                if contexto["intentos"] >= MAX_INTENTOS:
                    estado = ERROR_LIMITE
                else:
                    print(f"BOT: Formato invalido. Use DD/MM/AAAA. "
                          f"Intento {contexto['intentos']}/{MAX_INTENTOS}.")
                continue

            if fecha_fin < contexto["fecha_inicio"]:
                print("BOT: La fecha de fin no puede ser anterior a la de inicio.")
                continue  # vuelve a pedir fecha de fin (mismo estado)

            contexto["fecha_fin"] = fecha_fin
            contexto["intentos"] = 0
            estado = CALCULANDO

        # --------------------- CALCULANDO ---------------------
        elif estado == CALCULANDO:
            dias = calcular_dias_habiles(contexto["fecha_inicio"], contexto["fecha_fin"])
            contexto["dias_solicitados"] = dias

            disponibles = int(contexto["empleado"]["dias_disponibles"])
            if dias > disponibles:
                print(f"BOT: No posee saldo suficiente. Tiene {disponibles} "
                      f"dias disponibles y solicito {dias}.")
                estado = SIN_SALDO
                continue

            print(f"BOT: Se solicitan {dias} dias habiles.")
            estado = CONFIRMANDO

        # --------------------- CONFIRMANDO ---------------------
        elif estado == CONFIRMANDO:
            entrada = input("BOT: ¿Confirma la solicitud? (S/N): ")
            if es_comando_global(entrada):
                estado, salir = manejar_comando_global(entrada, estado)
                if salir:
                    break
                continue

            if es_respuesta_si(entrada):
                estado = REGISTRADO
            elif es_respuesta_no(entrada):
                estado = CANCELADO
            else:
                print("BOT: Por favor responda unicamente con S (si) o N (no).")

    # ------------------ Acciones finales segun estado ------------------
    if estado == REGISTRADO:
        solicitud = {
            "id_solicitud": siguiente_id_solicitud(),
            "legajo_empleado": contexto["legajo"],
            "fecha_inicio": contexto["fecha_inicio"].strftime("%d/%m/%Y"),
            "fecha_fin": contexto["fecha_fin"].strftime("%d/%m/%Y"),
            "dias_solicitados": contexto["dias_solicitados"],
            "estado": "PENDIENTE",
            "fecha_solicitud": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "observaciones": "",
        }
        guardar_solicitud(solicitud)
        print(f"BOT: Solicitud {solicitud['id_solicitud']} registrada. "
              f"Su supervisor sera notificado. ¡Hasta pronto!")

    elif estado == SIN_SALDO:
        print("BOT: No se pudo generar la solicitud por falta de saldo. ¡Hasta pronto!")

    elif estado == ERROR_LIMITE:
        print("BOT: Se supero el limite de intentos. Por favor contacte "
              "directamente a Recursos Humanos para continuar. ¡Hasta pronto!")

    elif estado == CANCELADO:
        # Mensaje ya fue mostrado en manejar_comando_global o en CONFIRMANDO
        if contexto.get("legajo"):
            print("BOT: Proceso finalizado sin cambios.")


if __name__ == "__main__":
    ejecutar_bot()
