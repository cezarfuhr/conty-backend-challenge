import pytest
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test to avoid conflicts."""
    if hasattr(app.state, 'limiter'):
        app.state.limiter._storage.reset()
    yield
    if hasattr(app.state, 'limiter'):
        app.state.limiter._storage.reset()
