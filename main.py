
import csv #Manejo de csv
import os
from faker import Faker
from sqlalchemy import create_engine, text #Permite ejecutar conexiones a MySQL
#create_engine es la conexión que permite ejecutar INSERT INTO, CREATE TABLE a través de python
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv #Permite leer todo lo que tenga en las variables de entorno. 
#¿Qué tengo en las variables de entorno? 


def ensure_database(db_url: str) -> None:
    """Create the target MySQL database if it doesn't exist."""
    url = make_url(db_url)
    dbname = url.database
    if not dbname:
        return
    server_url = url.set(database=None)
    engine = create_engine(server_url, future=True)
    with engine.begin() as conn:
        print(f"Creating database {dbname}")
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))


def main() -> None:
    fake = Faker('es_ES')
    rows = [{
        "nombre": fake.name(),
        "email": fake.email(),
        "direccion": fake.address().replace("\n", ", "),
        "telefono": fake.phone_number(),
        "edad": fake.random_int(min=18, max=90),
        "fecha_nacimiento": str(fake.date_of_birth(minimum_age=18, maximum_age=90)),
        "ciudad": fake.city(),
    } for _ in range(100000)] #Se insertan 100.000 registros utilizando Faker.

    with open("datos_falsos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre", "email", "direccion", "telefono", "edad", "fecha_nacimiento", "ciudad"])
        w.writeheader()
        w.writerows(rows)

    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL no está definida. Se omite la ingesta.")
        return

    ensure_database(db_url)
    engine = create_engine(db_url, future=True)
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS datos_falsos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                direccion TEXT NOT NULL,
                telefono VARCHAR(50) NOT NULL,
                edad INT NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                ciudad VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ))
        conn.execute(
            text("INSERT INTO datos_falsos (nombre, email, direccion, telefono, edad, fecha_nacimiento, ciudad) VALUES (:nombre, :email, :direccion, :telefono, :edad, :fecha_nacimiento, :ciudad)"),
            rows,
        )
    print("CSV generado e insertado en la base de datos.")


if __name__ == "__main__":
    main()
