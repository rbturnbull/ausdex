import pytest

@pytest.fixture
def check_viz():
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    from ausdex import viz
    return viz
