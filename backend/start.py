import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run("api.api:app", host="127.0.0.1", port=8000, reload=True, log_config="api/log_conf.yml")
