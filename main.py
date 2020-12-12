import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fire import Fire

app = FastAPI()


@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


def main(node: str):
    if node == "master":
        from routers import master
        app.include_router(master.router)
    elif node == "secondary":
        from routers import secondary
        app.include_router(secondary.router)
    else:
        raise ValueError(f"Node mode [{node}] should be one of master or secondary")

    uvicorn.run(app, host="0.0.0.0")


if __name__ == "__main__":
    Fire(main)
