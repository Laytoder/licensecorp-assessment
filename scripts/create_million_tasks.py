import requests

BASE_URL = "http://localhost:8002/tasks/populate/1000000"

def main():
    print("Starting batch task creation process...")
    try:
        response = requests.post(BASE_URL)
        response.raise_for_status()
        print(f"Successfully initiated the creation of 1,000,000 tasks. Response: {response.json()}")
    except Exception as e:
        print(f"Failed to initiate task creation: {e}")
        return

if __name__ == "__main__":
    main()
