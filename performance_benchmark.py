"""Performance benchmark for ncr_lookup.get_location.

Usage:
    python performance_benchmark.py
    python performance_benchmark.py --queries 50000
    python performance_benchmark.py --source both --queries 2000

Note:
    --queries is the number of lookups per scenario.
    Since this script runs 2 scenarios, total lookups = --queries * 2.
"""

from __future__ import annotations

import argparse
import random
import statistics
import time

from ncr_lookup import get_location, load_ncr
from ncr_geojson_embedded import GEOJSON as EMBEDDED_GEOJSON


def benchmark_query_batch(features, points):
    latencies_ms = []
    hits = 0
    start_total = time.perf_counter()

    for lat, lon in points:
        t0 = time.perf_counter()
        result = get_location(lat, lon, features)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        if result is not None:
            hits += 1

    total_s = time.perf_counter() - start_total
    qps = len(points) / total_s if total_s > 0 else float("inf")

    return {
        "queries": len(points),
        "hits": hits,
        "hit_rate": hits / len(points) if points else 0,
        "total_s": total_s,
        "qps": qps,
        "avg_ms": statistics.mean(latencies_ms) if latencies_ms else 0,
        "p50_ms": statistics.median(latencies_ms) if latencies_ms else 0,
        "p95_ms": statistics.quantiles(latencies_ms, n=20)[18] if len(latencies_ms) >= 20 else 0,
        "max_ms": max(latencies_ms) if latencies_ms else 0,
    }


def load_features_from_embedded():
    return [
        (feat["geometry"], feat["properties"].get("adm4_en"), feat["properties"].get("city"))
        for feat in EMBEDDED_GEOJSON["features"]
    ]


def load_features_from_file(path):
    return load_ncr(path)


def pretty_print(title, stats):
    print(f"\n{title}")
    print("-" * len(title))
    print(f"queries : {stats['queries']}")
    print(f"hits    : {stats['hits']} ({stats['hit_rate'] * 100:.2f}%)")
    print(f"total   : {stats['total_s']:.4f} s")
    print(f"throughput: {stats['qps']:.2f} queries/s")
    print(f"latency avg/p50/p95/max: {stats['avg_ms']:.4f} / {stats['p50_ms']:.4f} / {stats['p95_ms']:.4f} / {stats['max_ms']:.4f} ms")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--queries",
        type=int,
        default=10000,
        help="Number of queries per scenario (total lookups = queries * 2)",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--source",
        choices=["file", "embedded", "both"],
        default="both",
        help="GeoJSON source to benchmark",
    )
    args = parser.parse_args()

    random.seed(args.seed)

    fixed_points = [(14.531659172292766, 121.0736745605332)] * args.queries
    random_points = [
        (random.uniform(14.35, 14.85), random.uniform(120.85, 121.15))
        for _ in range(args.queries)
    ]

    total_lookups = args.queries * 2
    print(f"Planned total get_location calls per source: {total_lookups}")

    sources = ["file", "embedded"] if args.source == "both" else [args.source]

    for source in sources:
        if source == "file":
            t0 = time.perf_counter()
            features = load_features_from_file("ncr_barangays_geojson.geojson")
            load_s = time.perf_counter() - t0
        else:
            t0 = time.perf_counter()
            features = load_features_from_embedded()
            load_s = time.perf_counter() - t0

        print(f"\nSource: {source}")
        print(f"Loaded {len(features)} features in {load_s:.4f} s")

        fixed_stats = benchmark_query_batch(features, fixed_points)
        random_stats = benchmark_query_batch(features, random_points)

        pretty_print("Scenario A: repeated known-valid point", fixed_stats)
        pretty_print("Scenario B: random points in NCR bounding box", random_stats)


if __name__ == "__main__":
    main()
