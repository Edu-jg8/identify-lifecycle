

CREATE TABLE IF NOT EXISTS empleados (
    usuario VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    primer_apellido VARCHAR(20) NOT NULL,
    segundo_apellido VARCHAR(20),
    departamento VARCHAR(20) NOT NULL,  
    fecha_inicio DATE NOT NULL,
    correo_electronico VARCHAR(100) UNIQUE,
    estado VARCHAR(20) DEFAULT 'activo' NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
