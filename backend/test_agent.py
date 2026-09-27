from agent import analyze_incident


incident = """
The payment API is experiencing a large number of HTTP 503 errors.
CPU usage is around 90%, and the database connection pool is nearly exhausted.
Users are reporting failed payment attempts.
"""


result = analyze_incident(incident)

print("\n" + "=" * 70)
print("AI INCIDENT RESPONSE")
print("=" * 70)

print("\nNEW INCIDENT:")
print(result["incident"])

print("\nSIMILAR HISTORICAL INCIDENTS:")

for historical in result["historical_incidents"]:
    print(f"\nIncident #{historical['id']}")
    print(f"Title: {historical['title']}")
    print(f"Root Cause: {historical['root_cause']}")
    print(f"Resolution: {historical['resolution']}")
    print(f"Outcome: {historical['outcome']}")

print("\n" + "=" * 70)
print("AI ANALYSIS")
print("=" * 70)
print(result["analysis"])