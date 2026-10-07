import csv
import logging
import subprocess
import os
import psycopg2


# Configuracion basica de logs
logging.basicConfig(level=logging.INFO, filename = './logs/onboarding.log', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)
def limpieza_datos(texto) :
	""" Limpieza de espacios en blancos y estandarizacion """
	return texto.strip().lower() if texto else ""

def generar_usuario(nombre, apellido1, apellido2) :
	"""
	Construimos el username (ej : Carlos, Jimenez Grados -> carjimgra)
	"""
	n_limpio = limpieza_datos(nombre)
	a1_limpio = limpieza_datos(apellido1)
	a2_limpio = limpieza_datos(apellido2)
	usuario = n_limpio[:3] + a1_limpio[:3] + a2_limpio[:3]
	return usuario

def procesar_csv(ruta):
	logger.info("-" * 50)
	lista_usuarios = {} #guarda las veces que se repiten los nombres
	
	try:
		conn = None
		cursor = None
		conn, cursor = conexion_bd() #Establecemos conexion con la base de datos
		logger.info("-" * 50)
		with open(ruta,mode='r',encoding='utf-8') as f:
			lector = csv.DictReader(f)
			for fila in lector : 
				nombre = fila.get('Nombre','')
				apellido1 = fila.get('Primer Apellido','')
				apellido2 = fila.get('Segundo Apellido','')
				if not nombre or not apellido1 or not apellido2 :
					logger.warning("Fila ignorada: faltan datos criticos")
					continue
				usuario_base = generar_usuario(nombre,apellido1,apellido2)
				if usuario_base in lista_usuarios : #Busca entre coincidencias entre las claves
					usuario_red = usuario_base + str(lista_usuarios[usuario_base])
					lista_usuarios[usuario_base] += 1
				else :
					usuario_red = usuario_base
					lista_usuarios[usuario_base]=1
				
				logger.info(f"Usuario generado : {nombre}, {apellido1} {apellido2} -> {usuario_red}")
				logger.info("")
				departamento = limpieza_datos(fila.get('Departamento',''))
				asignar_usuarios(usuario_red,departamento)
				asignacion_directorios(departamento)
				
				rellenar_bd(cursor, usuario_red, nombre, apellido1, apellido2, departamento, fila.get('Fecha de Inicio',''))
				logger.info("")
				logger.info("-" * 50)
		conn.commit() #Guardamos los cambios en la base de datos
		logger.info("NO SE HAN DETECTADO ERRORES CRITICOS")


	except FileNotFoundError as e:
		logger.error(f"Archivo o comando no encontrado : {e}")

	except PermissionError as e:
		logger.error(f"Permisos insuficiente para leer el archivo : {e}")

	except csv.Error as e:
		logger.error(f"El archivo tiene un formato csv invalido : {e}")

	except subprocess.CalledProcessError as e:
		logger.error(f"Fallo al ejecutar un comando en el terminal : {e}")

	except psycopg2.Error as e:
			logger.error(f"Error al conectar a la base de datos: {e}")

	except Exception as e :
		logger.error(f"Fallo critico inesperado, mensaje : {e}")

	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()
		logger.info("-" * 50)
		logger.info("\n\n")


def asignar_usuarios(usuario,grupo):



	#Comprobamos si existe ya el grupo
	comando_check = ["getent","group",grupo]
	resultado_check = subprocess.run(comando_check, capture_output = True)
	#getent devuelve un 0 si encuentra el grupo y un numero distinto si no lo encuntra o si funciona algo mal

	if resultado_check.returncode == 0:
		logger.info(f"El grupo {grupo} ya existe en el sistema. Omitiendo creacion")
	else:
		comando_creacion = ["sudo","groupadd",grupo]
		subprocess.run(comando_creacion, check=True)
		logger.info(f"Grupo {grupo} creado ...")

	#Comprobamos si existe el usuario
	comando_check2 = ["getent","passwd",usuario]
	resultado_check2 = subprocess.run(comando_check2, capture_output = True)
	if resultado_check2.returncode == 0:
		logger.info(f"Ususario {usuario} ya existe, omitiendo creacion ...")
	else:
		comando_asignacion_usuario = ["sudo","useradd", "-m", "-s", "/bin/bash","-G",grupo,usuario]
		subprocess.run(comando_asignacion_usuario,check=True)
		logger.info(f"Nuevo usuario {usuario} agregado al grupo {grupo}")

	logger.info("")
def asignacion_directorios(grupo):

	ruta_departamento = f"/company/{grupo}"
	if(os.path.exists(ruta_departamento)):
		logger.info(f"El directorio {ruta_departamento} ya existe, omitimos creacion, asignacion de grupo y de creador")
	else :
		comando_creacion = ["sudo","mkdir",ruta_departamento]
		subprocess.run(comando_creacion,check=True)
		comando_chown = ["sudo","chown","-R","root:"+grupo,ruta_departamento]
		subprocess.run(comando_chown,check=True)
		comando_chmod = ["sudo","chmod","770",ruta_departamento]
		subprocess.run(comando_chmod,check=True)
		logger.info(f"Asignacion de grupo, creador y permisos realizado para {ruta_departamento}")

	logger.info("")


def conexion_bd():
	
	conn = psycopg2.connect(
				dbname = "identidades",
				user = "user_identidades",
				password = "eduj",
				host = "localhost",
				port = "5432"
	)
	cursor = conn.cursor()
	logger.info("Conexión a la base de datos establecida")

	with open("sql/empleados.sql","r") as archivo_sql:
		creacion_tabla = archivo_sql.read()
				
	#Ejecutamos la creacion de la tabla si no exisitiera
	cursor.execute(creacion_tabla)	
	return conn, cursor

def rellenar_bd(cursor, usuario,nombre,primer_apellido,segundo_apellido,departamento,fecha_inicio):
	
	

	#Insertamos los datos del empleado en la tabla, y prevenimos inyecciones SQL usando placeholders
	insert_query = """
	INSERT INTO empleados (usuario, nombre, primer_apellido, segundo_apellido, departamento, fecha_inicio, estado)
	VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO')
	ON CONFLICT (usuario)
	DO UPDATE SET
		departamento = EXCLUDED.departamento,
		fecha_inicio = EXCLUDED.fecha_inicio;
	"""
	cursor.execute(insert_query,(usuario, nombre, primer_apellido, segundo_apellido, departamento, fecha_inicio))
	
	logger.info(f"Datos del empleado {nombre} {primer_apellido} {segundo_apellido} insertados en la base de datos")

if __name__ == "__main__":
	procesar_csv("data/employees.csv")







