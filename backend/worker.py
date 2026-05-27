import logging

from rq import Connection, Worker

from app.cache import get_redis
from app.jobs import QUEUE_NAME

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main() -> None:
    connection = get_redis()
    with Connection(connection):
        worker = Worker([QUEUE_NAME])
        worker.work()


if __name__ == "__main__":
    main()
