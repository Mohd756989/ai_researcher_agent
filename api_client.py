"""
Thin HTTP client the Streamlit UI uses to talk to the FastAPI backend.
"""
import time
import requests


class ResearchAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def health(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=3)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def start_job(self, query: str) -> str:
        r = requests.post(f"{self.base_url}/research", json={"query": query}, timeout=10)
        r.raise_for_status()
        return r.json()["job_id"]

    def get_status(self, job_id: str) -> dict:
        r = requests.get(f"{self.base_url}/research/{job_id}", timeout=10)
        r.raise_for_status()
        return r.json()

    def poll_until_done(self, job_id: str, on_update=None, interval: float = 1.5, timeout: float = 300):
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_status(job_id)
            if on_update:
                on_update(status)
            if status["status"] in ("completed", "failed"):
                return status
            time.sleep(interval)
        raise TimeoutError("Research job timed out")
