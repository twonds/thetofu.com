"""Welcome to Reflex!."""

from reflex_deploy import styles

# Import all the pages.
from reflex_deploy.pages import *

import reflex as rx

# Create the app and compile it.
app = rx.App(style=styles.base_style)
app.compile()

# XXX - we should do readiness and liveliness endpoints and not just ping

# Need to add api endpoints
# The API server is in FastAPI - https://fastapi.tiangolo.com/tutorial/first-steps/#openapi-and-json-schema
# XXX - how can they work like frontend components?
# XXX - how do they interact with state?
# XXX - can the 'API' be deployed separately from the backend? Do they have to be?
from reflex_deploy.api import test
# https://github.com/reflex-dev/reflex/blob/7ae53cc5cfaf65bfaaa8ec31e2344a4afec3c92c/reflex/app.py#L235
app.api.get('/test')(test.test)
# curl http://127.0.0.1:8000/openapi.json | json_pp

