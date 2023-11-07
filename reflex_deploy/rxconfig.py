import reflex as rx

config = rx.Config(
    app_name="reflex_deploy",
    # For local host testing
    cp_backend_url="http://localhost:8000/controlpane",
    cp_web_url="http://localhost:3000"
)
