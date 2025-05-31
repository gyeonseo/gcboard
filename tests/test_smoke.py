# tests/test_smoke.py

def test_backend_import():
    try:
        from backend.app import create_app
        app = create_app()
        assert app is not None
    except Exception as e:
        assert False, f"Import or app creation failed: {e}"
