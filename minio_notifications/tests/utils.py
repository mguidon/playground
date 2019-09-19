import docker

def setup_config(host, port, access_key, secret_key):
    client = docker.from_env()

    client.containers.run("minio/mc", "")
    


