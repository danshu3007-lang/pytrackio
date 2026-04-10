import pytest
from pytrackio import track, get_registry


def test_reset_after_resets_registry():
    registry = get_registry()
    registry.reset()

    @track(reset_after=3)
    def dummy():
        pass

    metric_name = dummy.__wrapped__.__qualname__ if hasattr(dummy, "__wrapped__") else "test_reset_after_resets_registry.<locals>.dummy"

    dummy()
    dummy()
    assert registry.summary(metric_name) is not None  # not reset yet

    dummy()  # 3rd call — triggers reset
    assert registry.summary(metric_name) is None  # reset happened


def test_reset_after_restarts_counter():
    registry = get_registry()
    registry.reset()

    @track(reset_after=2)
    def task():
        pass

    metric_name = "test_reset_after_restarts_counter.<locals>.task"

    task()
    task()  # reset
    task()  # 1st call of new cycle
    summary = registry.summary(metric_name)
    assert summary is not None
    assert summary.calls == 1  # only 1 call since last reset


def test_reset_after_none_does_not_reset():
    registry = get_registry()
    registry.reset()

    @track
    def stable():
        pass

    metric_name = "test_reset_after_none_does_not_reset.<locals>.stable"

    for _ in range(10):
        stable()

    summary = registry.summary(metric_name)
    assert summary is not None
    assert summary.calls == 10


def test_reset_after_with_errors():
    registry = get_registry()
    registry.reset()

    @track(reset_after=2)
    def flaky():
        raise ValueError("boom")

    metric_name = "test_reset_after_with_errors.<locals>.flaky"

    with pytest.raises(ValueError):
        flaky()
    with pytest.raises(ValueError):
        flaky()  # 2nd call — triggers reset

    assert registry.summary(metric_name) is None


def test_reset_after_thread_safety():
    import threading
    registry = get_registry()
    registry.reset()

    @track(reset_after=50)
    def concurrent():
        pass

    metric_name = "test_reset_after_thread_safety.<locals>.concurrent"

    threads = [threading.Thread(target=concurrent) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Either reset happened twice (50+50) or once — both valid
    summary = registry.summary(metric_name)
    if summary:
        assert summary.calls <= 50