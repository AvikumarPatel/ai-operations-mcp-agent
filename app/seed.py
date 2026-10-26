from app.database import Base, SessionLocal, engine
from app.models import Customer, Inventory, Product


Base.metadata.create_all(bind=engine)


PRODUCTS = [
    {
        "sku": "PRX-001",
        "product_name": "Inductive Proximity Sensor M18",
        "category": "Sensors",
        "manufacturer": "OmniSense",
        "description": "M18 inductive proximity sensor for industrial object detection.",
        "unit_price": 42.50,
    },
    {
        "sku": "PRX-002",
        "product_name": "Inductive Proximity Sensor M12",
        "category": "Sensors",
        "manufacturer": "OmniSense",
        "description": "Compact M12 inductive proximity sensor for automation systems.",
        "unit_price": 34.75,
    },
    {
        "sku": "PHO-101",
        "product_name": "Photoelectric Sensor",
        "category": "Sensors",
        "manufacturer": "VisionTech",
        "description": "Diffuse photoelectric sensor for industrial detection.",
        "unit_price": 58.25,
    },
    {
        "sku": "TMP-210",
        "product_name": "Industrial Temperature Sensor",
        "category": "Sensors",
        "manufacturer": "ThermaPro",
        "description": "Industrial temperature sensor with digital output.",
        "unit_price": 76.00,
    },
    {
        "sku": "PLC-500",
        "product_name": "Compact PLC Controller",
        "category": "Controllers",
        "manufacturer": "ControlWorks",
        "description": "Compact programmable logic controller for small automation systems.",
        "unit_price": 495.00,
    },
    {
        "sku": "HMI-300",
        "product_name": "7-inch Industrial HMI",
        "category": "HMI",
        "manufacturer": "ControlWorks",
        "description": "Industrial touchscreen HMI for machine visualization.",
        "unit_price": 620.00,
    },
]


INVENTORY = [
    {
        "sku": "PRX-001",
        "warehouse": "Hamilton",
        "quantity_available": 180,
        "reorder_level": 50,
    },
    {
        "sku": "PRX-002",
        "warehouse": "Hamilton",
        "quantity_available": 95,
        "reorder_level": 40,
    },
    {
        "sku": "PHO-101",
        "warehouse": "Milton",
        "quantity_available": 48,
        "reorder_level": 25,
    },
    {
        "sku": "TMP-210",
        "warehouse": "Milton",
        "quantity_available": 22,
        "reorder_level": 20,
    },
    {
        "sku": "PLC-500",
        "warehouse": "Hamilton",
        "quantity_available": 15,
        "reorder_level": 10,
    },
    {
        "sku": "HMI-300",
        "warehouse": "Hamilton",
        "quantity_available": 8,
        "reorder_level": 5,
    },
]


CUSTOMERS = [
    {
        "customer_code": "CUST-001",
        "company_name": "ABC Manufacturing",
        "contact_name": "Sarah Miller",
        "email": "sarah@example.com",
    },
    {
        "customer_code": "CUST-002",
        "company_name": "NorthStar Packaging",
        "contact_name": "Daniel Kim",
        "email": "daniel@example.com",
    },
    {
        "customer_code": "CUST-003",
        "company_name": "Metro Automation",
        "contact_name": "Emily Chen",
        "email": "emily@example.com",
    },
]


def seed_database():
    db = SessionLocal()

    try:
        if db.query(Product).count() == 0:
            db.add_all(
                [Product(**product) for product in PRODUCTS]
            )

        if db.query(Inventory).count() == 0:
            db.add_all(
                [Inventory(**item) for item in INVENTORY]
            )

        if db.query(Customer).count() == 0:
            db.add_all(
                [Customer(**customer) for customer in CUSTOMERS]
            )

        db.commit()

        print("Database seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()