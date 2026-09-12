"""
Latency & Generation Speed Benchmark for AI Career Copilot.

Compares inference latency and generation speed between:
1. Cloud API Provider: Groq (openai/gpt-oss-120b)
2. Local Model Provider: Ollama (qwen2.5:7b)

Metrics:
- End-to-end response latency (seconds)
- P50 Latency (Median typical latency across all runs)
- P95 Latency (Tail latency across all runs)
- Average Generation Speed (tokens per second)
- Cloud vs Local Speedup Factor
"""

import sys
import os
import json
import time
import argparse
import statistics
from pathlib import Path

# Ensure UTF-8 stdout for console on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from langchain_core.messages import HumanMessage
from services.llm_service import get_llm

RESULTS_DIR = Path(__file__).parent / "results"

# Benchmark Prompts representing realistic Career Copilot workloads
BENCHMARK_PROMPTS = [
    {
        "id": "quick_query",
        "name": "Quick Technical Lookup",
        "prompt": "List the top 3 core technical skills required for an AI Engineer working with Large Language Models. Keep the answer under 60 words."
    },
    {
        "id": "resume_summarize",
        "name": "Resume Profile Summary",
        "prompt": (
            "Summarize the following candidate background into 2 concise, executive bullet points:\n"
            "Computer Science student with experience building RAG systems using LangChain and ChromaDB. "
            "Engineered an automated complaint triage system processing 20,000 tickets across 12 departments with 91% accuracy. "
            "Developed a multi-modal visual search engine using CLIP and Qdrant with sub-50ms retrieval latency."
        )
    },
    {
        "id": "job_fit_analysis",
        "name": "Job Alignment Reasoning",
        "prompt": (
            "Analyze the candidate's fit for this role:\n"
            "Role: Junior AI Engineer (Requires: Python, RAG architectures, Vector DBs, REST APIs, Docker).\n"
            "Candidate Experience: Built production RAG with ChromaDB, FastAPI backends, and containerized deployment with Docker. Lacks cloud infrastructure experience (AWS/GCP).\n"
            "Provide: 1 major strength and 1 priority skill gap."
        )
    },
    {
        "id": "bullet_rewrite",
        "name": "Resume Bullet Rewriting",
        "prompt": (
            "Rewrite this resume bullet using the XYZ formula (Accomplished [X], as measured by [Y], by doing [Z]):\n"
            "'Built a deep learning classification model during my internship to route support tickets.'"
        )
    }
]


def check_provider_availability(provider: str) -> bool:
    if provider == "cloud":
        api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        return bool(api_key and api_key.strip())
    elif provider == "local":
        try:
            import urllib.request
            url = f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False
    return False


def estimate_tokens(text: str) -> int:
    """
    Estimate token count based on standard whitespace and punctuation ratio.
    ~4 characters per token or ~1.3 tokens per word.
    """
    if not text:
        return 0
    words = text.split()
    return max(1, int(len(words) * 1.3))


def calculate_percentiles(latencies: list) -> tuple:
    """
    Calculate P50 (median) and P95 from run latencies.
    For small samples (< 20), using max is a conservative tail indicator.
    """
    if not latencies:
        return 0.0, 0.0

    p50 = statistics.median(latencies)

    if len(latencies) >= 20:
        p95 = statistics.quantiles(latencies, n=20)[18]
    else:
        p95 = max(latencies)

    return round(p50, 2), round(p95, 2)


def measure_single_prompt(llm, prompt: str) -> dict:
    start_time = time.perf_counter()
    response = llm.invoke([HumanMessage(content=prompt)])
    elapsed = time.perf_counter() - start_time

    content = response.content if hasattr(response, "content") else str(response)
    if isinstance(content, list):
        content = " ".join(str(part) for part in content)

    # Try extracting token count from response metadata if available
    token_count = 0
    if hasattr(response, "response_metadata") and isinstance(response.response_metadata, dict):
        usage = response.response_metadata.get("token_usage", {})
        token_count = usage.get("completion_tokens", 0)

    if token_count == 0:
        token_count = estimate_tokens(content)

    gen_speed = token_count / elapsed if elapsed > 0 else 0.0

    return {
        "latency": round(elapsed, 3),
        "tokens": token_count,
        "generation_speed": round(gen_speed, 2),
        "output_length_chars": len(content),
        "error": None
    }


def evaluate_provider(provider_name: str, runs: int = 5) -> dict:
    original_provider = config.LLM_PROVIDER
    config.LLM_PROVIDER = provider_name

    model_name = config.GROQ_MODEL if provider_name == "cloud" else config.LLM_MODEL
    print("\n" + "=" * 65)
    print(f"EVALUATING PROVIDER: {provider_name.upper()} ({model_name})")
    print(f"Total Prompts: {len(BENCHMARK_PROMPTS)} | Runs Per Prompt: {runs} | Total Inferences: {len(BENCHMARK_PROMPTS) * runs}")
    print("=" * 65)

    try:
        llm = get_llm()
    except Exception as e:
        config.LLM_PROVIDER = original_provider
        print(f"Error initializing LLM for {provider_name}: {e}")
        return {"error": str(e), "results": []}

    results = []
    all_individual_latencies = []
    all_individual_tokens = []
    all_individual_speeds = []

    for item in BENCHMARK_PROMPTS:
        prompt_id = item["id"]
        name = item["name"]
        prompt = item["prompt"]

        prompt_latencies = []
        prompt_tokens = []
        prompt_speeds = []

        print(f"\n[Test] {name}")
        for r in range(runs):
            try:
                metrics = measure_single_prompt(llm, prompt)
                prompt_latencies.append(metrics["latency"])
                prompt_tokens.append(metrics["tokens"])
                prompt_speeds.append(metrics["generation_speed"])

                all_individual_latencies.append(metrics["latency"])
                all_individual_tokens.append(metrics["tokens"])
                all_individual_speeds.append(metrics["generation_speed"])

                run_label = f" (Run {r+1}/{runs})" if runs > 1 else ""
                print(f"  Result{run_label}: {metrics['latency']:.2f}s | {metrics['tokens']} tokens | {metrics['generation_speed']:.1f} tok/s")
            except Exception as e:
                print(f"  Error on {name} (Run {r+1}): {e}")

        valid_latencies = [lat for lat in prompt_latencies if lat is not None]
        avg_lat = sum(valid_latencies) / len(valid_latencies) if valid_latencies else 0.0
        avg_tok = sum(prompt_tokens) / len(prompt_tokens) if prompt_tokens else 0
        prompt_tot_tokens = sum(prompt_tokens)
        prompt_tot_elapsed = sum(valid_latencies)
        prompt_gen_speed = prompt_tot_tokens / prompt_tot_elapsed if prompt_tot_elapsed > 0 else 0.0

        p50_prompt, p95_prompt = calculate_percentiles(valid_latencies)

        results.append({
            "id": prompt_id,
            "name": name,
            "average_latency": round(avg_lat, 2),
            "p50_latency": p50_prompt,
            "p95_latency": p95_prompt,
            "average_tokens": int(avg_tok),
            "generation_speed": round(prompt_gen_speed, 2),
            "all_runs_latency": [round(l, 2) for l in valid_latencies]
        })

    config.LLM_PROVIDER = original_provider

    overall_avg_lat = sum(all_individual_latencies) / len(all_individual_latencies) if all_individual_latencies else 0.0
    overall_p50_lat, overall_p95_lat = calculate_percentiles(all_individual_latencies)

    # Total generated tokens divided by total elapsed request time
    total_tokens = sum(all_individual_tokens)
    total_elapsed = sum(all_individual_latencies)
    overall_generation_speed = total_tokens / total_elapsed if total_elapsed > 0 else 0.0

    summary = {
        "provider": provider_name,
        "model": model_name,
        "total_prompts": len(BENCHMARK_PROMPTS),
        "runs_per_prompt": runs,
        "total_inferences": len(all_individual_latencies),
        "total_tokens_generated": total_tokens,
        "total_elapsed_time": round(total_elapsed, 2),
        "average_latency": round(overall_avg_lat, 2),
        "p50_latency": overall_p50_lat,
        "p95_latency": overall_p95_lat,
        "min_latency": round(min(all_individual_latencies), 2) if all_individual_latencies else 0.0,
        "max_latency": round(max(all_individual_latencies), 2) if all_individual_latencies else 0.0,
        "average_generation_speed": round(overall_generation_speed, 2),
        "all_latencies": [round(l, 2) for l in all_individual_latencies],
        "results": results
    }

    print("-" * 65)
    print(f"Summary for {provider_name.upper()} ({model_name}):")
    print(f"  Total Inferences:        {summary['total_inferences']}")
    print(f"  Average Latency:         {summary['average_latency']:.2f}s")
    print(f"  P50 (Median) Latency:    {summary['p50_latency']:.2f}s")
    print(f"  P95 (Tail) Latency:      {summary['p95_latency']:.2f}s")
    print(f"  Min / Max Latency:       {summary['min_latency']:.2f}s / {summary['max_latency']:.2f}s")
    print(f"  Overall Generation Speed:{summary['average_generation_speed']:.1f} tokens/sec ({total_tokens} tokens / {total_elapsed:.1f}s)")
    print("-" * 65)

    return summary



def print_comparison_table(cloud_summary: dict, local_summary: dict):
    print("\n" + "=" * 80)
    print("                 LATENCY & GENERATION SPEED BENCHMARK")
    print("=" * 80)
    col_w = [26, 24, 24]
    header = f"{'Benchmark Task':<{col_w[0]}} | {'Cloud (Groq)':<{col_w[1]}} | {'Local (Ollama)':<{col_w[2]}}"
    print(header)
    print("-" * col_w[0] + "-+-" + "-" * col_w[1] + "-+-" + "-" * col_w[2])

    cloud_map = {r["id"]: r for r in cloud_summary.get("results", [])}
    local_map = {r["id"]: r for r in local_summary.get("results", [])}

    for item in BENCHMARK_PROMPTS:
        pid = item["id"]
        name = item["name"]

        c_item = cloud_map.get(pid, {})
        l_item = local_map.get(pid, {})

        c_text = f"{c_item.get('average_latency', 0.0):.2f}s ({c_item.get('generation_speed', 0.0):.0f} t/s)" if c_item else "N/A"
        l_text = f"{l_item.get('average_latency', 0.0):.2f}s ({l_item.get('generation_speed', 0.0):.0f} t/s)" if l_item else "N/A"

        print(f"{name:<{col_w[0]}} | {c_text:<{col_w[1]}} | {l_text:<{col_w[2]}}")

    print("-" * col_w[0] + "-+-" + "-" * col_w[1] + "-+-" + "-" * col_w[2])
    c_avg = f"{cloud_summary.get('average_latency', 0.0):.2f}s"
    l_avg = f"{local_summary.get('average_latency', 0.0):.2f}s"
    print(f"{'Average Latency':<{col_w[0]}} | {c_avg:<{col_w[1]}} | {l_avg:<{col_w[2]}}")

    c_p50 = f"{cloud_summary.get('p50_latency', 0.0):.2f}s"
    l_p50 = f"{local_summary.get('p50_latency', 0.0):.2f}s"
    print(f"{'P50 Latency (Median)':<{col_w[0]}} | {c_p50:<{col_w[1]}} | {l_p50:<{col_w[2]}}")

    c_p95 = f"{cloud_summary.get('p95_latency', 0.0):.2f}s"
    l_p95 = f"{local_summary.get('p95_latency', 0.0):.2f}s"
    print(f"{'P95 Latency (Tail 95th)':<{col_w[0]}} | {c_p95:<{col_w[1]}} | {l_p95:<{col_w[2]}}")

    c_spd = f"{cloud_summary.get('average_generation_speed', 0.0):.1f} tokens/sec"
    l_spd = f"{local_summary.get('average_generation_speed', 0.0):.1f} tokens/sec"
    print(f"{'Avg Generation Speed':<{col_w[0]}} | {c_spd:<{col_w[1]}} | {l_spd:<{col_w[2]}}")

    c_lat = cloud_summary.get("average_latency", 0.0)
    l_lat = local_summary.get("average_latency", 0.0)
    if c_lat > 0 and l_lat > 0:
        speedup = l_lat / c_lat
        print(f"{'Cloud Speedup Factor':<{col_w[0]}} | {speedup:.1f}x faster than local  | Reference baseline")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Evaluate LLM latency across Cloud (Groq) and Local (Ollama) providers.")
    parser.add_argument(
        "--provider",
        choices=["both", "cloud", "local"],
        default="both",
        help="Provider to evaluate: 'both' (default), 'cloud', or 'local'."
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs per prompt to average (default: 5)."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file under backend/evaluation/results/."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Optional custom output path for JSON results."
    )

    args = parser.parse_args()

    cloud_ready = check_provider_availability("cloud")
    local_ready = check_provider_availability("local")

    print("=" * 65)
    print("AI CAREER COPILOT - INFERENCE LATENCY BENCHMARK")
    print(f"Target Provider:  {args.provider.upper()}")
    print(f"Runs Per Prompt:  {args.runs}")
    print(f"Cloud (Groq):     {'Available' if cloud_ready else 'Not configured / missing API key'}")
    print(f"Local (Ollama):   {'Online' if local_ready else 'Offline / not reachable'}")
    print("=" * 65)

    cloud_summary = {}
    local_summary = {}

    if args.provider in ["both", "cloud"]:
        if cloud_ready:
            cloud_summary = evaluate_provider("cloud", runs=args.runs)
        else:
            print("\nSkipping Cloud: GROQ_API_KEY is not configured.")

    if args.provider in ["both", "local"]:
        if local_ready:
            local_summary = evaluate_provider("local", runs=args.runs)
        else:
            print("\nSkipping Local: Ollama server is not running on configured endpoint.")

    if cloud_summary and local_summary:
        print_comparison_table(cloud_summary, local_summary)

    # Save results if requested
    if args.save or args.output:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = Path(args.output) if args.output else (RESULTS_DIR / f"latency_eval_{int(time.time())}.json")
        combined_data = {
            "timestamp": int(time.time()),
            "cloud": cloud_summary,
            "local": local_summary
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2)
        print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
