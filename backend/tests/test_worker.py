from unittest.mock import MagicMock

import worker


def test_worker_main_uses_rq_worker(monkeypatch) -> None:
    fake_connection = object()
    fake_worker = MagicMock()

    monkeypatch.setattr(worker, "get_redis", lambda: fake_connection)
    monkeypatch.setattr(worker, "Worker", fake_worker)

    worker.main()

    fake_worker.assert_called_once_with([worker.QUEUE_NAME], connection=fake_connection)
    fake_worker.return_value.work.assert_called_once_with()
