# Identity Lifecycle Automation

## ¿Qué problema resuelve?
El alta y baja manual de empleados en sistemas informáticos genera cuellos de botella, errores humanos de configuración y falta de trazabilidad. Este proyecto automatiza el ciclo de vida inicial de las identidades (Onboarding), garantizando que la creación de usuarios, la asignación de permisos y el registro de auditoría se realicen de forma estructurada, rápida e idempotente.

## Estado del Proyecto
*   **Fase 1 (Onboarding Local):** 🔷 VALIDADO
*   **Fase 2 (Integración Microsoft Entra ID):** ⬜ NO EMPEZADO

## Arquitectura y Flujo de Ejecución (Fase 1)
El sistema actual opera de forma 100% local procesando las altas mediante el siguiente flujo:
1. **Ingesta y Validación:** Lectura de un archivo CSV de Recursos Humanos y sanitización de datos.
2. **Generación de Identidad:** Creación algorítmica de nombres de usuario evitando colisiones (ej. `carjimgra1`, `carjimgra2`).
3. **Aprovisionamiento (Capa SO):** Ejecución de comandos Linux en segundo plano (`useradd`, `groupadd`, `mkdir`) para crear usuarios, asignar grupos por departamento y aplicar ACLs estrictas (`chown`, `chmod`).
4. **Auditoría (Capa BD):** Registro de la operación en una base de datos PostgreSQL utilizando el patrón UPSERT (`ON CONFLICT DO UPDATE`) para garantizar la idempotencia de los datos.

## Stack Tecnológico
*   **Sistema Operativo:** Linux (Ubuntu Server) / Bash
*   **Lenguaje:** Python 3 (librerías: `csv`, `subprocess`, `psycopg2`, `logging`)
*   **Base de Datos:** PostgreSQL (Esquema relacional y DDL)
*   **Control de Versiones:** Git / GitHub

## Criterios de Aceptación Cumplidos
- [x] Ingesta, validación y sanitización de archivos CSV.
- [x] Aprovisionamiento automatizado de usuarios en Linux con separación de privilegios (RBAC básico).
- [x] Prevención de Inyección SQL mediante el uso de variables bind (`%s`).
- [x] Infraestructura tolerante a fallos: Gestión segura de ciclos de vida de Sockets TCP (Context Managers y bloques `finally`).
- [x] Idempotencia absoluta: Una segunda ejecución del script no destruye datos existentes ni colapsa el motor de base de datos.
- [x] Persistencia de logs de auditoría en archivos físicos.
