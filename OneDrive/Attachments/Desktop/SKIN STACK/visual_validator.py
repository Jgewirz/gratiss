#!/usr/bin/env python3
"""
Visual System Validator for SkinStack
Provides a comprehensive visual report of system status
"""

import asyncio
import asyncpg
import redis.asyncio as redis
import httpx
import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import time

# Load environment
load_dotenv()

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}[{title}]{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*40}{Colors.ENDC}")

def print_success(message: str, detail: str = ""):
    """Print success message"""
    print(f"{Colors.GREEN}[OK]{Colors.ENDC} {message}", end="")
    if detail:
        print(f" {Colors.BLUE}{detail}{Colors.ENDC}")
    else:
        print()

def print_error(message: str, detail: str = ""):
    """Print error message"""
    print(f"{Colors.FAIL}[FAIL]{Colors.ENDC} {message}", end="")
    if detail:
        print(f" {Colors.WARNING}{detail}{Colors.ENDC}")
    else:
        print()

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}[WARN]{Colors.ENDC} {message}")

def print_metric(label: str, value: str, unit: str = ""):
    """Print a metric"""
    print(f"  {label:.<30} {Colors.BOLD}{value}{Colors.ENDC} {unit}")

def print_progress_bar(progress: float, width: int = 30):
    """Print a progress bar"""
    filled = int(width * progress)
    bar = '#' * filled + '-' * (width - filled)
    percentage = progress * 100
    print(f"  [{Colors.GREEN}{bar}{Colors.ENDC}] {percentage:.1f}%")

async def test_database_connection() -> Tuple[bool, Dict]:
    """Test database connection and basic operations"""
    results = {"status": False, "details": {}}

    try:
        # Connect
        start = time.time()
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        connect_time = (time.time() - start) * 1000

        results["details"]["connect_time"] = f"{connect_time:.1f}ms"

        # Test query
        start = time.time()
        version = await conn.fetchval("SELECT version()")
        query_time = (time.time() - start) * 1000

        results["details"]["query_time"] = f"{query_time:.1f}ms"
        results["details"]["version"] = version.split()[0] + " " + version.split()[1]

        # Get table counts
        tables = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        results["details"]["tables"] = len(tables)

        # Get total rows
        total_rows = 0
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['tablename']}")
            total_rows += count

        results["details"]["total_rows"] = total_rows

        await conn.close()
        results["status"] = True

    except Exception as e:
        results["details"]["error"] = str(e)

    return results["status"], results["details"]

async def test_redis_connection() -> Tuple[bool, Dict]:
    """Test Redis connection and operations"""
    results = {"status": False, "details": {}}

    try:
        # Connect
        r = await redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

        # Test ping
        start = time.time()
        await r.ping()
        ping_time = (time.time() - start) * 1000
        results["details"]["ping_time"] = f"{ping_time:.1f}ms"

        # Get info
        info = await r.info()
        results["details"]["version"] = info.get('redis_version', 'Unknown')
        results["details"]["memory"] = info.get('used_memory_human', 'Unknown')
        results["details"]["connected_clients"] = info.get('connected_clients', 0)

        # Test operations
        test_key = f"test_{datetime.now().timestamp()}"
        await r.set(test_key, "test_value")
        value = await r.get(test_key)
        await r.delete(test_key)

        results["status"] = value == b"test_value"
        await r.aclose()

    except Exception as e:
        results["details"]["error"] = str(e)

    return results["status"], results["details"]

async def test_api_endpoints() -> Tuple[bool, Dict]:
    """Test API endpoints"""
    results = {"status": True, "details": {"endpoints": []}}

    endpoints = [
        ("GET", "/healthz", None, "Health Check"),
        ("GET", "/docs", None, "API Documentation"),
        ("GET", "/api/stats/dashboard", None, "Dashboard Stats"),
    ]

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        for method, path, data, name in endpoints:
            try:
                start = time.time()

                if method == "GET":
                    response = await client.get(path)
                elif method == "POST":
                    response = await client.post(path, json=data)

                response_time = (time.time() - start) * 1000

                endpoint_result = {
                    "name": name,
                    "path": path,
                    "status": response.status_code,
                    "time": f"{response_time:.1f}ms",
                    "success": response.status_code < 400
                }

                results["details"]["endpoints"].append(endpoint_result)

                if not endpoint_result["success"]:
                    results["status"] = False

            except Exception as e:
                results["details"]["endpoints"].append({
                    "name": name,
                    "path": path,
                    "error": str(e),
                    "success": False
                })
                results["status"] = False

    return results["status"], results["details"]

async def check_system_performance() -> Dict:
    """Check system performance metrics"""
    metrics = {}

    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

        # Test redirect query performance
        times = []
        for _ in range(10):
            start = time.time()
            await conn.fetchrow("""
                SELECT * FROM tracking_links
                WHERE slug = $1 AND is_active = true
            """, "test_slug")
            times.append((time.time() - start) * 1000)

        times.sort()
        metrics["redirect_query"] = {
            "p50": f"{times[5]:.1f}ms",
            "p95": f"{times[9]:.1f}ms",
            "avg": f"{sum(times)/len(times):.1f}ms"
        }

        # Get database size
        db_size = await conn.fetchval("""
            SELECT pg_size_pretty(pg_database_size(current_database()))
        """)
        metrics["database_size"] = db_size

        # Get index usage
        index_usage = await conn.fetchval("""
            SELECT ROUND(100 * idx_scan / (seq_scan + idx_scan), 2) as percent
            FROM pg_stat_user_tables
            WHERE seq_scan + idx_scan > 0
            LIMIT 1
        """)
        metrics["index_usage"] = f"{index_usage}%" if index_usage else "N/A"

        await conn.close()

    except Exception as e:
        metrics["error"] = str(e)

    return metrics

async def generate_visual_report():
    """Generate comprehensive visual validation report"""

    print_header("SKINSTACK VISUAL SYSTEM VALIDATOR")
    print(f"{Colors.BLUE}Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")

    # 1. Database Connection
    print_section("DATABASE CONNECTION")
    db_status, db_details = await test_database_connection()

    if db_status:
        print_success("PostgreSQL Connection", "HEALTHY")
        print_metric("Version", db_details.get("version", "Unknown"))
        print_metric("Connect Time", db_details.get("connect_time", "N/A"))
        print_metric("Query Time", db_details.get("query_time", "N/A"))
        print_metric("Tables", str(db_details.get("tables", 0)))
        print_metric("Total Rows", f"{db_details.get('total_rows', 0):,}")
    else:
        print_error("PostgreSQL Connection", "FAILED")
        print_warning(f"Error: {db_details.get('error', 'Unknown error')}")

    # 2. Redis Cache
    print_section("REDIS CACHE")
    redis_status, redis_details = await test_redis_connection()

    if redis_status:
        print_success("Redis Connection", "HEALTHY")
        print_metric("Version", redis_details.get("version", "Unknown"))
        print_metric("Ping Time", redis_details.get("ping_time", "N/A"))
        print_metric("Memory Usage", redis_details.get("memory", "N/A"))
        print_metric("Connected Clients", str(redis_details.get("connected_clients", 0)))
    else:
        print_error("Redis Connection", "FAILED")
        if "error" in redis_details:
            print_warning(f"Error: {redis_details['error']}")

    # 3. API Endpoints
    print_section("API ENDPOINTS")
    api_status, api_details = await test_api_endpoints()

    if "endpoints" in api_details:
        success_count = sum(1 for e in api_details["endpoints"] if e.get("success"))
        total_count = len(api_details["endpoints"])

        print(f"Testing {total_count} endpoints...")
        print_progress_bar(success_count / total_count if total_count > 0 else 0)

        for endpoint in api_details["endpoints"]:
            if endpoint.get("success"):
                status_color = Colors.GREEN
                status_text = f"[{endpoint.get('status')}]"
            else:
                status_color = Colors.FAIL
                status_text = "[FAIL]"

            print(f"  {status_color}*{Colors.ENDC} {endpoint['name']:.<30} "
                  f"{status_color}{status_text}{Colors.ENDC} "
                  f"{endpoint.get('time', 'N/A')}")

            if "error" in endpoint:
                print(f"    {Colors.WARNING}+- {endpoint['error']}{Colors.ENDC}")

    # 4. Performance Metrics
    print_section("PERFORMANCE METRICS")
    perf_metrics = await check_system_performance()

    if "redirect_query" in perf_metrics:
        print_success("Query Performance")
        redirect = perf_metrics["redirect_query"]
        print_metric("  P50 Latency", redirect.get("p50", "N/A"))
        print_metric("  P95 Latency", redirect.get("p95", "N/A"))
        print_metric("  Avg Latency", redirect.get("avg", "N/A"))

    if "database_size" in perf_metrics:
        print_metric("Database Size", perf_metrics["database_size"])

    if "index_usage" in perf_metrics:
        print_metric("Index Usage", perf_metrics["index_usage"])

    # 5. System Summary
    print_section("SYSTEM SUMMARY")

    # Calculate overall health score
    health_score = 0
    max_score = 4

    if db_status: health_score += 1
    if redis_status: health_score += 1
    if api_status: health_score += 1
    if "redirect_query" in perf_metrics: health_score += 1

    health_percentage = (health_score / max_score) * 100

    print(f"\n{Colors.BOLD}Overall Health Score:{Colors.ENDC}")
    print_progress_bar(health_score / max_score)

    if health_percentage >= 75:
        status_color = Colors.GREEN
        status_text = "HEALTHY"
    elif health_percentage >= 50:
        status_color = Colors.WARNING
        status_text = "WARNING"
    else:
        status_color = Colors.FAIL
        status_text = "CRITICAL"

    print(f"\n{Colors.BOLD}System Status: {status_color}{status_text}{Colors.ENDC}")

    # Recommendations
    if health_percentage < 100:
        print(f"\n{Colors.WARNING}{Colors.BOLD}Recommendations:{Colors.ENDC}")
        if not db_status:
            print(f"  -Fix database connection issues")
        if not redis_status:
            print(f"  -Check Redis service is running")
        if not api_status:
            print(f"  -Ensure API server is running on port 8000")

    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.CYAN}Validation complete at {datetime.now().strftime('%H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

async def main():
    """Main entry point"""
    try:
        await generate_visual_report()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Validation interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main())