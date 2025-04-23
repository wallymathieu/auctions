# Load testing

```
python3 -m venv load_testing
source load_testing/bin/activate
python3 -m pip install locust
```

test with:
```
locust -f LocustFile.py --host=http://localhost:8080
```