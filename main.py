from fastapi import FastAPI

from routers import categories, products

app = FastAPI()
# add internal routers here

# add external routers here
app.include_router(categories.router)
app.include_router(products.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

