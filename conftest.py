import random

from django.core.management import call_command

from accounts.models import State, City, User
import pytest
from django.test.client import Client

import glob

from tests.constants import (
    COMMON_FIXTURE0, COMMON_CUSTOMER1, COMMON_CUSTOMER2, COMMON_CUSTOMER3, COMMON_AGENT1, COMMON_AGENT2, COMMON_AGENT3,
    COMMON_AGENT4, COMMON_AGENT5, COMMON_RESTAURANT1, COMMON_RESTAURANT2, COMMON_RESTAURANT3, COMMON_RESTAURANT4,
    COMMON_RESTAURANT5, COMMON_RESTAURANT6
)


@pytest.fixture
def load_initial_data():
    call_command('loaddata', glob.glob('fixtures/basic_fixtures/*'))


@pytest.fixture(autouse=True)
def autouse_db(db, load_initial_data):
    """This will allow all testcases to access database"""
    pass


@pytest.fixture(scope="session")
def load_data():
    def inner_function(*args):
        call_command('loaddata', *args)

    return inner_function


@pytest.fixture
def get_client(client):
    def inner_function():
        return Client()

    return inner_function


@pytest.fixture
def login_user(
        db,
        get_client
):
    def inner_function(email, password):
        data = dict(email=email, password=password)
        client = get_client()
        client.login(**data)
        return client, User.objects.get(email=email)
    return inner_function


@pytest.fixture
def test_password():
    return "Test@1234"


@pytest.fixture
def test_admin_password():
    return "123"


# Initial Data

@pytest.fixture
def get_register_form_initial_data(test_password):
    def inner_function(**kwargs):
        data = {
            "password1": test_password,
            "password2": test_password,
            "username": "default_user",
            "email": "default_user@test.com",
            "mobile_number": f"+9198989{random.randint(1000, 9999)}3"
        }
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_address_form_initial_data():
    def inner_function(city, state, **kwargs):
        data = {
            "address_line1": 'default_address_line1',
            "address_line2": 'default_address_line2',
            "street": "default_street",
            "landmark": "default_landmark",
            "pincode": "360007",
            "city": city.id,
            "state": state.id,
            "lat": 23.02419,
            "long": 12.2334,
        }
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_register_customer_user_initial_data(
        get_register_form_initial_data,
        get_address_form_initial_data,
):
    def inner_function(state, city, **kwargs):
        assert isinstance(state, State)
        assert isinstance(city, City)

        return {
            **get_register_form_initial_data(**kwargs),
            **get_address_form_initial_data(city, state, **kwargs)
        }
    return inner_function


@pytest.fixture
def get_restaurant_owner_form_initial_data(test_password):
    def inner_function(**kwargs):
        data = {
            "password1": test_password,
            "password2": test_password,
            "username": "default_restaurant",
            "email": "default_restaurant@test.com",
            "mobile_number": f"+9198989{random.randint(1000, 9999)}3"
        }
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_restaurant_form_initial_data():
    def inner_function(**kwargs):
        file = "media/default.jpg"
        data = {"name": 'default_restaurant_name', "image": (open(file, 'rb'), file), }
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_restaurant_document_form_initial_data():
    def inner_function(**kwargs):
        file = "media/default.jpg"
        data = {
            "account_no": '12345678',
            "ifsc_code": 'ABCD0123456',
            "pan_card": (open(file, 'rb'), file),
            "gst_certificate": (open(file, 'rb'), file),
            "fssai_certificate": (open(file, 'rb'), file)
        }
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_item_form_initial_data():
    def inner_function(**kwargs):
        data = {"name": "item_1", "quantity": 300, "available_quantity": 30, "unit": "grams", "price": 100,
                "discount": 10, "description": "very good taste", "image": "./media/default.jpg"}
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_agent_document_form_initial_data(test_password):
    def inner_function(**kwargs):
        filename = "media/default.jpg"
        data = {
            'account_no': 1234567890,
            'ifsc_code': 'ABCD0123456',
            'pancard_number': 'BNZAA2318J',
            'pancard_document': (open(filename, 'rb'), filename),
            'license_number': 'HR-0619850034761',
            'license_document': (open(filename, 'rb'), filename)
        }
        for k, v in data.items():
            if kwargs.get(k) is not None:
                data[k] = kwargs[k]
        return data
    return inner_function


@pytest.fixture
def get_delivery_agent_registration_data(
        get_register_form_initial_data,
        get_address_form_initial_data,
        get_agent_document_form_initial_data,
):
    def inner_function(state, city, **kwargs):
        assert isinstance(state, State)
        assert isinstance(city, City)

        return {
            **get_register_form_initial_data(**kwargs),
            **get_address_form_initial_data(city, state, **kwargs),
            **get_agent_document_form_initial_data(**kwargs)
        }
    return inner_function


@pytest.fixture
def get_add_restaurant_form_initial_data(
        get_address_form_initial_data,
        get_restaurant_form_initial_data,
        get_restaurant_document_form_initial_data
):
    def inner_function(**kwargs):
        assert isinstance(kwargs.get('state'), State)
        assert isinstance(kwargs.get('city'), City)
        data = {}
        data.update(get_address_form_initial_data(**kwargs))
        data.update(get_restaurant_form_initial_data(**kwargs))
        data.update(get_restaurant_document_form_initial_data(**kwargs))
        return data
    return inner_function


@pytest.fixture
def get_restaurant_registration_form_initial_data(
        get_restaurant_owner_form_initial_data,
        get_address_form_initial_data,
        get_restaurant_form_initial_data,
        get_restaurant_document_form_initial_data
):
    def inner_function(**kwargs):
        assert isinstance(kwargs.get('state'), State)
        assert isinstance(kwargs.get('city'), City)
        data = {}
        data.update(get_restaurant_owner_form_initial_data(**kwargs))
        data.update(get_address_form_initial_data(**kwargs))
        data.update(get_restaurant_form_initial_data(**kwargs))
        data.update(get_restaurant_document_form_initial_data(**kwargs))
        return data
    return inner_function


@pytest.fixture
def load_admin_panel_data(load_data):
    load_data(COMMON_FIXTURE0)
    load_data(COMMON_CUSTOMER1)
    load_data(COMMON_CUSTOMER2)
    load_data(COMMON_CUSTOMER3)
    load_data(COMMON_AGENT1)
    load_data(COMMON_AGENT2)
    load_data(COMMON_AGENT3)
    load_data(COMMON_AGENT4)
    load_data(COMMON_AGENT5)
    load_data(COMMON_RESTAURANT1)
    load_data(COMMON_RESTAURANT2)
    load_data(COMMON_RESTAURANT3)
    load_data(COMMON_RESTAURANT4)
    load_data(COMMON_RESTAURANT5)
    load_data(COMMON_RESTAURANT6)


# Fixtures for cart module

@pytest.fixture
def load_cart_prerequisite_data(load_data):
    load_data(COMMON_CUSTOMER1)
    load_data(COMMON_RESTAURANT6)


@pytest.fixture
def load_order_prerequisite_data(load_data):
    load_data(COMMON_CUSTOMER1)
    load_data(COMMON_RESTAURANT6)
    load_data(COMMON_AGENT4)
