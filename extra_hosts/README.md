## Pass extra hosts to docker in docker
- Host has entry in `etc/hosts`:
```
192.168.186.1 predator.osparc.io predator
```
i.e. host can `ping` predator.

- docker container can `ping predator` if `extra_hosts` is passed via `docker-compose`
- docker in docker can `ping predaotr` if `extra_hosts` is passed via python API


