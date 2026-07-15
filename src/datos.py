from sqlmodel import Session, select
from datetime import datetime
from models import engine, ProductType, Product


def guardar_datos_extraidos(datos_extraidos):
    with Session(engine) as session:
        tipos_cache = {}

        for dato in datos_extraidos:
            nombre_categoria = dato["categorias"]

            # ── 1. GESTIÓN DE CATEGORÍA (Mantenemos la validación para evitar errores de duplicidad) ──
            if nombre_categoria not in tipos_cache:
                statement = select(ProductType).where(
                    ProductType.name == nombre_categoria
                )
                tipo_db = session.exec(statement).first()

                if not tipo_db:
                    tipo_db = ProductType(name=nombre_categoria)
                    session.add(tipo_db)
                    session.commit()
                    session.refresh(tipo_db)

                tipos_cache[nombre_categoria] = tipo_db

            # ── 2. GUARDADO DIRECTO DEL PRODUCTO (Sin leer ni actualizar) ──
            nuevo_producto = Product(
                product_id=dato["product_id"],
                title=dato["title"],
                price_eur=dato["price_eur"],
                scraped_at=datetime.now(),
                type=tipos_cache[nombre_categoria],
            )
            session.add(nuevo_producto)
        session.commit()
