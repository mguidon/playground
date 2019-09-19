import pytest

import pika


def test_minio(minio_service):
    print(minio_service)

def test_rabbit(rabbit_service):
    print(rabbit_service)

def test_pika(rabbit_service):
    credentials = pika.PlainCredentials(rabbit_service['user'], rabbit_service['password'])
    parameters = pika.ConnectionParameters(host=rabbit_service['host'], port=rabbit_service['port'], credentials=credentials)

    # try to establish connection and check its status
    try:
        connection = pika.BlockingConnection(parameters)
        if connection.is_open:
            print('OK')
            connection.close()
            assert True
    except Exception as error:
        print('Error:', error.__class__.__name__)
        assert False

    