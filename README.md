# Bot de Gestión de Vacaciones (Simulador)

Trabajo Práctico Integrador — Cátedra Organización Empresarial
Tecnicatura Universitaria en Programación (TUP) a Distancia — UTN

## Descripción

Simulador de chatbot que automatiza el proceso administrativo de **solicitud
de vacaciones**. Implementa una Máquina de Estados que sigue fielmente el
flujo definido en el diagrama BPMN 2.0 (proceso "to-be"), con persistencia
de datos en archivos CSV que simulan una base de datos.

El bot corre en consola: el empleado escribe respuestas en texto plano y el
sistema valida, calcula días hábiles, consulta saldo y registra la
solicitud para su posterior aprobación por parte del supervisor.

## Tecnologías utilizadas

- **Lenguaje:** Python 3.10+
- **Persistencia:** archivos `.csv` (módulo `csv` de la librería estándar)
- **Sin dependencias externas** — corre con Python puro

## Estructura del repositorio

```
.
├── bot_vacaciones.py    # Lógica principal del bot (máquina de estados)
├── empleados.csv        # Base de datos simulada de empleados
├── supervisores.csv     # Base de datos simulada de supervisores
├── solicitudes.csv      # Registro de solicitudes generadas (se completa en uso)
└── README.md            # Este archivo
```

## Cómo desplegarlo / ejecutarlo

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/<usuario>/<repositorio>.git
   cd <repositorio>
   ```

2. Verificar que Python 3 esté instalado:
   ```bash
   python3 --version
   ```

3. Ejecutar el bot:
   ```bash
   python3 bot_vacaciones.py
   ```

4. Seguir las instrucciones que el bot muestra en consola. En cualquier
   paso se puede escribir:
   - `AYUDA` → muestra ayuda contextual del paso actual
   - `CANCELAR` → cancela la solicitud en curso
   - `SALIR` → cierra la sesión

## Flujo del proceso (resumen)

1. El empleado ingresa su legajo.
2. El bot muestra el saldo de días disponibles.
3. El empleado ingresa fecha de inicio y fecha de fin.
4. El bot calcula los días hábiles solicitados.
5. Si hay saldo suficiente, se solicita confirmación.
6. Al confirmar, la solicitud se guarda en `solicitudes.csv` con estado
   `PENDIENTE`, lista para ser aprobada o rechazada por el supervisor.

El detalle completo de estados, validaciones y manejo de errores se
encuentra documentado en el **Diccionario de Datos** y el **Manual de
Usuario** entregados en el informe PDF del TPI.

## Simulación de la aprobación del supervisor

Dado que este es un simulador (sin integración real con Telegram/WhatsApp),
la aprobación del supervisor se simula editando manualmente el campo
`estado` en `solicitudes.csv`, cambiándolo de `PENDIENTE` a `APROBADO` o
`RECHAZADO`.

## Autores

- [Nombre Apellido 1]
- [Nombre Apellido 2]

## Cátedra

Organización Empresarial — Prof. Gabriela Martínez (titular)
