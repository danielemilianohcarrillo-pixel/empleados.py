import sqlite3
import os

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================

DB = "database/empleados.db"


def conectar():
    os.makedirs("database", exist_ok=True)
    return sqlite3.connect(DB)


# ==========================================
# CREACIÓN DE LA BASE DE DATOS
# ==========================================

def crear_bd():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleado (
            curp TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            calle TEXT,
            colonia TEXT,
            telefono TEXT,
            edad INTEGER,
            sueldo_mensual REAL
        )
    """)

    conexion.commit()
    conexion.close()


# ==========================================
# FUNCIÓN AUXILIAR PARA MOSTRAR UN EMPLEADO
# ==========================================

def mostrar_empleado(empleado):
    print("CURP:", empleado[0])
    print("Nombre:", empleado[1])
    print("Apellido:", empleado[2])
    print("Calle:", empleado[3] or "")
    print("Colonia:", empleado[4] or "")
    print("Teléfono:", empleado[5] or "")
    print("Edad:", empleado[6] if empleado[6] is not None else "")
    if empleado[7] is not None:
        print(f"Sueldo mensual: ${empleado[7]:,.2f}")
    else:
        print("Sueldo mensual:")


# ==========================================
# 1. ALTAS DE EMPLEADOS
# ==========================================

def alta_empleado():
    print("\n===== ALTA DE EMPLEADO =====")

    curp = input("CURP: ").strip().upper()
    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()
    calle = input("Calle: ").strip()
    colonia = input("Colonia: ").strip()
    telefono = input("Teléfono: ").strip()
    edad_txt = input("Edad: ").strip()
    sueldo_txt = input("Sueldo mensual: ").strip()

    if not curp or not nombre or not apellido:
        print("La CURP, el nombre y el apellido son obligatorios.")
        return

    if len(curp) != 18:
        print("La CURP debe tener 18 caracteres.")
        return

    try:
        edad = int(edad_txt)
        sueldo_mensual = float(sueldo_txt)
        if edad < 0 or sueldo_mensual < 0:
            raise ValueError
    except ValueError:
        print("La edad y el sueldo deben ser números válidos y positivos.")
        return

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO empleado (
                curp, nombre, apellido, calle,
                colonia, telefono, edad, sueldo_mensual
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            curp, nombre, apellido, calle,
            colonia, telefono, edad, sueldo_mensual
        ))

        conexion.commit()
        print("\nEmpleado registrado correctamente.")

    except sqlite3.IntegrityError:
        print("\nError: la CURP ya existe.")

    except sqlite3.Error as error:
        print("Error al registrar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 2. BAJAS DE EMPLEADOS
# ==========================================

def baja_empleado():
    print("\n===== BAJA DE EMPLEADO =====")

    curp = input("CURP del empleado: ").strip().upper()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT * FROM empleado
            WHERE curp = ?
        """, (curp,))

        empleado = cursor.fetchone()

        if empleado is None:
            print("No se encontró un empleado con esa CURP.")
            return

        print("\nDatos del empleado:")
        mostrar_empleado(empleado)

        confirmacion = input(
            "\n¿Desea eliminar este empleado? (S/N): "
        ).strip().upper()

        if confirmacion == "S":
            cursor.execute("""
                DELETE FROM empleado
                WHERE curp = ?
            """, (curp,))

            conexion.commit()
            print("Empleado eliminado correctamente.")
        else:
            print("Operación cancelada.")

    except sqlite3.Error as error:
        print("Error al eliminar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 3. MODIFICACIONES DE EMPLEADOS
# ==========================================

def modificar_empleado():
    print("\n===== MODIFICACIÓN DE EMPLEADO =====")

    curp = input("CURP del empleado: ").strip().upper()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT nombre, apellido, calle, colonia,
                   telefono, edad, sueldo_mensual
            FROM empleado
            WHERE curp = ?
        """, (curp,))

        empleado = cursor.fetchone()

        if empleado is None:
            print("No se encontró un empleado con esa CURP.")
            return

        print("\nIngrese los nuevos datos.")
        print("Presione ENTER para conservar el dato actual.")

        nombre = input(f"Nombre [{empleado[0]}]: ").strip()
        apellido = input(f"Apellido [{empleado[1]}]: ").strip()
        calle = input(f"Calle [{empleado[2] or ''}]: ").strip()
        colonia = input(f"Colonia [{empleado[3] or ''}]: ").strip()
        telefono = input(f"Teléfono [{empleado[4] or ''}]: ").strip()
        edad_txt = input(f"Edad [{empleado[5] or ''}]: ").strip()
        sueldo_txt = input(f"Sueldo mensual [{empleado[6] or ''}]: ").strip()

        # Conservar los valores anteriores cuando se pulsa ENTER
        nombre = nombre or empleado[0]
        apellido = apellido or empleado[1]
        calle = calle or empleado[2] or ""
        colonia = colonia or empleado[3] or ""
        telefono = telefono or empleado[4] or ""

        try:
            edad = int(edad_txt) if edad_txt else empleado[5]
            sueldo_mensual = (
                float(sueldo_txt) if sueldo_txt else empleado[6]
            )
            if (edad is not None and edad < 0) or \
               (sueldo_mensual is not None and sueldo_mensual < 0):
                raise ValueError
        except ValueError:
            print("La edad y el sueldo deben ser números válidos.")
            return

        cursor.execute("""
            UPDATE empleado
            SET nombre = ?,
                apellido = ?,
                calle = ?,
                colonia = ?,
                telefono = ?,
                edad = ?,
                sueldo_mensual = ?
            WHERE curp = ?
        """, (
            nombre, apellido, calle, colonia,
            telefono, edad, sueldo_mensual, curp
        ))

        conexion.commit()
        print("\nEmpleado modificado correctamente.")

    except sqlite3.Error as error:
        conexion.rollback()
        print("Error al modificar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 4. CONSULTA DE TODA LA TABLA
# ==========================================

def consultar_todos():
    print("\n===== LISTADO DE EMPLEADOS =====")

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT curp, nombre, apellido, calle,
                   colonia, telefono, edad, sueldo_mensual
            FROM empleado
            ORDER BY apellido, nombre
        """)

        empleados = cursor.fetchall()

        if not empleados:
            print("No hay empleados registrados.")
            return

        for empleado in empleados:
            print("-" * 50)
            mostrar_empleado(empleado)

        print("-" * 50)
        print("Total de empleados:", len(empleados))

    except sqlite3.Error as error:
        print("Error al consultar los empleados:", error)

    finally:
        conexion.close()


# ==========================================
# 5. CONSULTA POR CURP
# ==========================================

def consultar_curp():
    print("\n===== CONSULTA POR CURP =====")

    curp = input("Ingrese la CURP: ").strip().upper()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT curp, nombre, apellido, calle,
                   colonia, telefono, edad, sueldo_mensual
            FROM empleado
            WHERE curp = ?
        """, (curp,))

        empleado = cursor.fetchone()

        if empleado:
            print("\n===== DATOS DEL EMPLEADO =====")
            mostrar_empleado(empleado)
        else:
            print("No se encontró un empleado con esa CURP.")

    except sqlite3.Error as error:
        print("Error al consultar al empleado:", error)

    finally:
        conexion.close()


# ==========================================
# 6. MENÚ PRINCIPAL
# ==========================================

def menu():
    while True:
        print("\n" + "=" * 45)
        print("     SISTEMA DE CONTROL DE EMPLEADOS ACME")
        print("=" * 45)
        print("1. Alta de empleados")
        print("2. Baja de empleados")
        print("3. Modificación de empleados")
        print("4. Consulta de toda la tabla")
        print("5. Consulta por CURP")
        print("6. Salir del sistema")
        print("=" * 45)

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            alta_empleado()

        elif opcion == "2":
            baja_empleado()

        elif opcion == "3":
            modificar_empleado()

        elif opcion == "4":
            consultar_todos()

        elif opcion == "5":
            consultar_curp()

        elif opcion == "6":
            print("\nSaliendo del sistema...")
            print("Gracias por utilizar el sistema.")
            break

        else:
            print("\nOpción inválida. Seleccione del 1 al 6.")


# ==========================================
# INICIO DEL PROGRAMA
# ==========================================

if __name__ == "__main__":
    crear_bd()
    menu()
