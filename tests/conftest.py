import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (
    Customer,
    Inventory,
    Product,
)


# --------------------------------------------------
# Isolated in-memory SQLite database for tests
# --------------------------------------------------

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# --------------------------------------------------
# Test client
# --------------------------------------------------

@pytest.fixture()
def client(monkeypatch):

    # Disable outbound webhook delivery during
    # most API tests.
    monkeypatch.setenv(
        "WEBHOOK_URL",
        "",
    )

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        seed_test_data(db)

    finally:
        db.close()

    with TestClient(app) as test_client:
        yield test_client


# --------------------------------------------------
# Seed minimal deterministic test data
# --------------------------------------------------

def seed_test_data(db):

    products = [
        Product(
            sku="PRX-001",
            product_name=(
                "M18 Inductive Proximity Sensor"
            ),
            category="Sensors",
            manufacturer="OmniSense",
            description=(
                "Industrial proximity sensor."
            ),
            unit_price=Decimal("42.50"),
        ),

        Product(
            sku="PLC-500",
            product_name=(
                "Compact PLC Controller"
            ),
            category="Controllers",
            manufacturer="ControlCore",
            description=(
                "Compact programmable controller."
            ),
            unit_price=Decimal("485.00"),
        ),
    ]

    db.add_all(products)

    inventory = [
        Inventory(
            sku="PRX-001",
            warehouse="Hamilton",
            quantity_available=180,
            reorder_level=40,
        ),

        Inventory(
            sku="PLC-500",
            warehouse="Hamilton",
            quantity_available=25,
            reorder_level=10,
        ),
    ]

    db.add_all(inventory)

    customers = [
        Customer(
            customer_code="CUST-001",
            company_name="ABC Manufacturing",
            contact_name="Daniel Brooks",
            email="daniel@example.com",
        ),

        Customer(
            customer_code="CUST-002",
            company_name="Northline Packaging",
            contact_name="Emma Wilson",
            email="emma@example.com",
        ),
    ]

    db.add_all(customers)

    db.commit()