if __name__ == '__main__':
    import uvicorn

    uvicorn.run("src.server_v2:app", host="0.0.0.0", port=8000)
