import requests
import time
import concurrent.futures
import statistics

URL = "http://localhost:8880/v1/audio/speech"
HEADERS = {"Content-Type": "application/json"}
CONCURRENCY = 5
ITERATIONS = 5

TEST_TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "Supertonic is a lightning-fast, on-device text-to-speech system.",
    "This is a test of the emergency broadcast system.",
    "Performance metrics are crucial for production deployments.",
    "Simulating high concurrency load on the GPU server."
]

def make_request(text):
    payload = {
        "model": "supertonic",
        "voice": "M1",
        "input": text
    }
    start_time = time.time()
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, stream=True)
        response.raise_for_status()
        size = 0
        for chunk in response.iter_content(chunk_size=8192):
            size += len(chunk)
        duration = time.time() - start_time
        return duration, size
    except Exception as e:
        print(f"Request failed: {e}")
        return None, 0

def run_load_test():
    print(f"Starting load test with {CONCURRENCY} concurrent threads...")
    latencies = []
    
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = []
        for i in range(ITERATIONS):
            for text in TEST_TEXTS:
                futures.append(executor.submit(make_request, text))
        
        for future in concurrent.futures.as_completed(futures):
            duration, size = future.result()
            if duration:
                latencies.append(duration)
                print(f".", end="", flush=True)
                
    end_total = time.time()
    total_time = end_total - start_total
    
    print("\n\nLoad Test Results:")
    print(f"Total Requests: {len(success_latencies := [l for l in latencies if l])}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Throughput: {len(latencies) / total_time:.2f} req/s")
    
    if latencies:
        print(f"Avg Latency: {statistics.mean(latencies):.4f}s")
        print(f"Min Latency: {min(latencies):.4f}s")
        print(f"Max Latency: {max(latencies):.4f}s")

if __name__ == "__main__":
    run_load_test()
