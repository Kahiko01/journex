import subprocess
import json

print("=== USING CURL THROUGH PYTHON ===\n")

# Run curl command
result = subprocess.run(
    ['curl.exe', '-s', 'http://localhost:8000/api/v1/trades/'],
    capture_output=True,
    text=True
)

print(f"Curl exit code: {result.returncode}")
print(f"Curl stdout length: {len(result.stdout)}")

if result.stdout:
    try:
        trades = json.loads(result.stdout)
        print(f"Found {len(trades)} trades")
        if len(trades) > 0:
            print("\nFirst trade:")
            print(json.dumps(trades[0], indent=2))
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"First 200 chars: {result.stdout[:200]}")
else:
    print("No output from curl")
    print(f"Stderr: {result.stderr}")
