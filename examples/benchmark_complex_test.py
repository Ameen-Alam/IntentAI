#!/usr/bin/env python3
"""
Benchmark complex intent detection and parameter extraction for the published IntentAI PyPI package.
Generates a CSV report of the results.
"""

import csv
from intentai import tool_call, get_tools_from_functions, detect_tool_and_params

@tool_call(
    name="book_flight",
    description="Book a flight ticket",
    trigger_phrases=["book flight", "flight ticket", "reserve flight"],
    examples=["book flight to Paris", "reserve flight for tomorrow"]
)
def book_flight(destination: str, date: str, passengers: int = 1, class_type: str = "economy") -> str:
    return f"Flight booked to {destination} on {date} for {passengers} passenger(s) in {class_type} class."

@tool_call(
    name="weather_forecast",
    description="Get weather forecast for a city",
    trigger_phrases=["weather", "forecast", "temperature"],
    examples=["weather in Berlin", "forecast for Tokyo"]
)
def weather_forecast(city: str, days: int = 1, units: str = "celsius") -> str:
    return f"Weather in {city} for {days} day(s): 20°{units[0].upper()}"

tools = get_tools_from_functions(book_flight, weather_forecast)

inputs = [
    "Book flight to New York for 2 people business class next Monday",
    "What's the weather in Madrid for the next 3 days?",
    "Reserve flight Paris",
    "Temperature in Rome tomorrow",
    "flight ticket Tokyo",
    "weather forecast",
    "book flight",
    "random gibberish input"
]

expected = [
    "book_flight",
    "weather_forecast",
    "book_flight",
    "weather_forecast",
    "book_flight",
    "weather_forecast",
    "book_flight",
    None
]

print("\n===== IntentAI Complex Benchmark Test =====\n")
results = []
for idx, text in enumerate(inputs):
    result = detect_tool_and_params(text, tools)
    exp = expected[idx]
    if result:
        tool = result['tool']
        conf = result['confidence']
        params = result['parameters']
        passed = (tool == exp)
        print(f"Input: {text}")
        print(f"  Tool: {tool}")
        print(f"  Confidence: {conf:.2f}")
        print(f"  Parameters: {params}")
    else:
        tool = None
        conf = None
        params = None
        passed = (exp is None)
        print(f"Input: {text}")
        print("  No tool detected")
    print("-" * 40)
    results.append({
        'Input': text,
        'Detected Tool': tool,
        'Confidence': f"{conf:.2f}" if conf is not None else '',
        'Parameters': str(params) if params is not None else '',
        'Expected': exp,
        'Pass': 'PASS' if passed else 'FAIL'
    })

correct = sum(1 for r in results if r['Pass'] == 'PASS')
print(f"\nBenchmark Accuracy: {correct}/{len(expected)} ({correct/len(expected)*100:.1f}%)\n")

# Write CSV report
csv_path = "benchmark_report.csv"
with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ['Input', 'Detected Tool', 'Confidence', 'Parameters', 'Expected', 'Pass']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow(row)
print(f"CSV report saved to {csv_path}") 