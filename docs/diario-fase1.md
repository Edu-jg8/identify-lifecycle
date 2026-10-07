# Registro de Actividad 

**Fecha :** 07 de Octubre de 2026
**Proyecto :** 01-Identify Lifecycle
**Fase :** 1 - Onboarding local

## Objetivo de hoy

Automatizar completamente el ciclo de vida inicial de un usuario a partir de un CSV de RRHH: validación de datos, creación estructurada del usuario y su entorno en el sistema operativo Linux, y registro auditable en una base de datos PostgreSQL garantizando que el proceso sea seguro, repetible (idempotente) y tolerante a fallos.

## Conocimientos previos

* Manejo intermedio de Linux (comandos básicos de usuarios y permisos), programación en Python (scripting básico), fundamentos de bases de datos relacionales y uso de Git.

## Investigación realizada 

* **Sistemas (Linux):** Gestión de memoria física y virtual (OOM Killer, archivos Swap). Ejecución de comandos del sistema desde Python (subprocess) y validación de existencia de usuarios/grupos a nivel de SO (getent). Asignación de permisos granulares y aislamiento de directorios (chown, chmod).
* **Aplicación (Python):** Lógica para generación dinámica de identidades (evitando colisiones como carjimgra1, carjimgra2). Manejo de excepciones granulares y gestión del ciclo de vida de conexiones de red (Sockets TCP) mediante bloques try...except...finally y Context Managers.
* **Base de datos (PostgreSQL):** Implementación del driver psycopg2. Diseño DDL seguro (CREATE TABLE IF NOT EXISTS). Prevención de Inyecciones SQL usando placeholders (%s). Idempotencia en la ingesta de datos a través de sentencias UPSERT (ON CONFLICT DO UPDATE).

## Problemas encontrados

* **Caída catastrófica de infraestructura:** El servidor Ubuntu colapsaba repetidamente, cerrando la sesión SSH y deteniendo VS Code. El sistema arrojaba el error Out of memory: Killed process.
* **Rendimiento y colisiones en la aplicación:**

    Ejecutar el script por segunda vez provocaba un error fatal de la base de datos por violación de Primary Key al intentar insertar empleados ya existentes.

    La arquitectura inicial abría y cerraba una conexión TCP con PostgreSQL por cada fila del CSV, lo cual es ineficiente y peligroso en producción.

## Soluciones Aplicadas

* **Hardware y SO (Hardening):** Escalado vertical de la VM desde VirtualBox asignando 4096 MB de RAM Base. Creación estática de un archivo de paginación (swapfile) de 2GB con permisos estrictos (600) para dotar al OOM Killer de una red de seguridad, estabilizando el servidor frente a los picos de consumo de VS Code y PostgreSQL.

* **Infraestructura DDL:** 
Implementación de la cláusula CREATE TABLE IF NOT EXISTS para cumplir con la resiliencia en despliegues automatizados.

* **Lógica DML:** 
Implementación del patrón UPSERT en Python utilizando la cláusula ON CONFLICT (usuario) DO UPDATE SET en la sentencia INSERT. Esto permite ejecutar el mismo CSV de RRHH múltiples veces sin generar errores de UniqueViolation ni duplicar empleados.

* **Arquitectura de Red Python:** Refactorización crítica del script para resolver el problema N+1 y las fugas de memoria
    
    Se extrajo la conexión a la base de datos fuera del bucle for, abriendo el túnel TCP una sola vez al inicio del programa.

    Se encapsuló el cierre de los Sockets TCP (cursor.close() y conn.close()) dentro de un bloque incondicional finally para garantizar la destrucción 
    del túnel incluso ante fallos críticos del sistema.

    Integración segura con PostgreSQL (uso de placeholders contra SQL Injection)

## Resultado

Se trata de una infraestructura local automatizada para el aprovisionamiento de identidades. Utilizando Python, el sistema ingesta y sanitiza un archivo CSV para crear usuarios y configurar permisos de directorios a nivel de sistema operativo en Linux. Toda la información se registra de forma centralizada en una base de datos PostgreSQL aplicando lógica idempotente (UPSERT) para evitar errores de duplicidad si el código se ejecuta múltiples veces. Lo que se ha logrado en esta fase uno es consolidar un sistema funcional y auditable que resuelve el alta de empleados en local, sirviendo como paso previo obligatorio antes de su integración con la nube.
