
import asyncio
import datetime
import os
import subprocess
import sys
from pathlib import Path

import pytest
import requests
import sqlalchemy as sa

import pika
from aiopg.sa import create_engine
from pytest_docker import docker_ip, docker_services

import utils

DATABASE="db_minio"
USER="user"
PASS="password"
ACCESS_KEY="12345678"
SECRET_KEY="12345678"
BUCKET_NAME="notifications"
RABBITMQ_USER="rabbit"
RABBITMQ_PASSWORD="rabbit"

def is_postgres_responsive(url):
    """Check if something responds to ``url`` """
    try:
        engine = sa.create_engine(url)
        conn = engine.connect()
        conn.close()
    except sa.exc.OperationalError:
        return False
    return True

def is_responsive(url, code=200):
    """Check if something responds to ``url`` syncronously"""
    try:
        response = requests.get(url)
        if response.status_code == code:
            return True
    except requests.exceptions.RequestException as _e:
        pass

    return False

def is_responsive_rabbit(rabbit):
    credentials = pika.PlainCredentials(rabbit['user'], rabbit['password'])
    parameters = pika.ConnectionParameters(host=rabbit['host'], port=rabbit['port'], credentials=credentials)

    # try to establish connection and check its status
    try:
        connection = pika.BlockingConnection(parameters)
        if connection.is_open:
            connection.close()
            return True
    except Exception as _e:
        pass
    
    return False

@pytest.fixture(scope='session')
def here():
    return Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent

@pytest.fixture(scope='session')
def docker_compose_file(here):
    """ Overrides pytest-docker fixture
    """
    old = os.environ.copy()

    # docker-compose reads these environs
    os.environ['POSTGRES_DB'] = DATABASE
    os.environ['POSTGRES_USER'] = USER
    os.environ['POSTGRES_PASSWORD'] = PASS
#    os.environ['POSTGRES_ENDPOINT'] = "FOO"  # TODO: update config schema!!
    os.environ['MINIO_ACCESS_KEY'] = ACCESS_KEY
    os.environ['MINIO_SECRET_KEY'] = SECRET_KEY
    os.environ["RABBITMQ_USER"] = RABBITMQ_USER
    os.environ["RABBITMQ_PASSWORD"] = RABBITMQ_PASSWORD

    dc_path = here / 'docker-compose.yml'

    assert dc_path.exists()
    yield str(dc_path)

    os.environ = old


@pytest.fixture(scope='session')
def postgres_service(docker_services, docker_ip):
    url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
        user=USER,
        password=PASS,
        database=DATABASE,
        host=docker_ip,
        port=docker_services.port_for('postgres', 5432),
    )

    # Wait until service is responsive.
    docker_services.wait_until_responsive(
        check=lambda: is_postgres_responsive(url),
        timeout=30.0,
        pause=0.1,
    )

    postgres_service = {
        'user': USER,
        'password': PASS,
        'database': DATABASE,
        'host': docker_ip,
        'port': docker_services.port_for('postgres', 5432)
    }

    return postgres_service


@pytest.fixture(scope='session')
def postgres_service_url(postgres_service, docker_services, docker_ip):
    postgres_service_url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
        user=USER,
        password=PASS,
        database=DATABASE,
        host=docker_ip,
        port=docker_services.port_for('postgres', 5432),
    )

    return postgres_service_url


@pytest.fixture(scope='function')
async def postgres_engine(loop, postgres_service_url):
    postgres_engine = await create_engine(postgres_service_url)

    yield postgres_engine

    if postgres_engine:
        postgres_engine.close()
        await postgres_engine.wait_closed()


@pytest.fixture(scope='session')
def minio_service(docker_services, docker_ip):

   # Build URL to service listening on random port.
    url = 'http://%s:%d/' % (
        docker_ip,
        docker_services.port_for('minio', 9000),
    )

    # Wait until service is responsive.
    docker_services.wait_until_responsive(
        check=lambda: is_responsive(url, 403),
        timeout=30.0,
        pause=0.1,
    )

    utils.setup_config(docker_ip, docker_services.port_for('minio', 9000), ACCESS_KEY, SECRET_KEY)


    return {
        'endpoint': '{ip}:{port}'.format(ip=docker_ip, port=docker_services.port_for('minio', 9000)),
        'access_key': ACCESS_KEY,
        'secret_key': SECRET_KEY,
        'bucket_name': BUCKET_NAME
    }

@pytest.fixture(scope='session')
def rabbit_service(docker_services, docker_ip):
    os.environ['RABBITMQ_HOST'] = "{host}".format(host=docker_ip)
    os.environ['RABBITMQ_PORT'] = "{port}".format(port=docker_services.port_for('rabbit', 5672))

   # Build URL to service listening on random port.
    url = 'amqp://{user}:{pw}@{url}:{port}'.format(user=RABBITMQ_USER, pw=RABBITMQ_PASSWORD, url=docker_ip, port=docker_services.port_for('rabbit', 5672))
   # ping_url = "{url}:{port}".format(url=docker_ip, port=docker_services.port_for('rabbit', 5672))

    rabbit = {
        'user': RABBITMQ_USER,
        'password': RABBITMQ_PASSWORD,
        'host': docker_ip,
        'port': docker_services.port_for('rabbit', 5672),
        'url': url
    }
    # Wait until service is responsive.
    docker_services.wait_until_responsive(
        check=lambda: is_responsive_rabbit(rabbit),
        timeout=30.0,
        pause=0.1,
    )
    return rabbit
