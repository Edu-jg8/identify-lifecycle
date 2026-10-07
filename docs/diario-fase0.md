# Registro de Actividad 

**Fecha :** 2 de Octubre de 2026
**Proyecto :** 01-Identify Lifecycle
**Fase :** 0 - Preparación del entorno Linux

## Objetivo de hoy
Desplegar una infraestructura virtual aislada y preparar el ecosistema de desarrollo (Git, Python, bases de datos)
asegurando un consumo mínimo de recursos

## Conocimientos previos

* Manejo de la terminal de Linux
* Fundamentos de virtualización
* Ejecución de comandos básicos en la terminal

## Investigación realizada 

* Diferencia entre un SO con y sin entorno gráfico para servidores.
* Arquitectura de procesos en segundo plano de Linux (systemd).
* Orden de operaciones seguro al combinar control de versiones y entornos de ejecución aislados (Python .venv).

## Problemas encontrados

* Incopatibilidad entre la distribución de telcados con la asignada para la consola virtual
* Dudas sobre la terminología de asignacion de recursos (CPUs vs hilos) en el hipervisor.

## Decisiones de Arquitectura y Ejecución

* **Virtualización:** Se instaló VirtualBox + Extension Pack (para soporte de cifrado). Se optó por la ISO de
 Ubuntu Server (sin GIU) asignando 2 vCPUs, 2 Gb de RAM y 25 Gb de disco para no saturar al anfitrión.
* **Sistema Base:** Sincronización e instalación de parches críticos con :
	`sudo apt update && sudo apt upgrade`
* **Stack Técnico:** Despliegue de los paquetes base con:
	`sudo apt install postgresql git python3-pip python3-venv`
* **Scaffolding:** Creación de directorio raiz, inicialización del entorno virtual, activación del mismo y posteior
inicialización del repositorio local
	`python3 -m venv .venv`
	`šource .venv/bin/activate`^
	`git init`^

## Resultado

Entorno base operativo. El daemon de la base de datos relacional está activo y escuchando peticiones.
