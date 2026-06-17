from mangum import Mangum
from app.main import app

# Wrap the FastAPI ASGI app with Mangum for Vercel serverless
handler = Mangum(app, lifespan="off")
