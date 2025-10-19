"""
DETERMINISTIC Test: SOL correlation analysis with SQL-only executables.

Use Case: "I want to see correlation between price, volume, and marketcap versus news on Web & X
of a crypto token, say $SOL. I also want to see what CTs are saying on X about SOL, and analyze
the correlation"

This test uses ONLY SQL executables (deterministic), so:
- First run: Generates Python script for visualization
- Second run: Reuses cached Python script (faster)

Execution Steps:
1. Generate SQL executable for fetching SOL price/volume/marketcap data
2. Generate SQL executable for fetching CT sentiment data from X
3. Generate Output executable for correlation visualization
4. Create blueprint with 2 steps:
   - Step 1: Run both SQL queries concurrently (price data & sentiment data)
   - Step 2: Run Output executable (receives results from both SQL queries)
5. Execute simulation TWICE and compare timing
"""

import httpx
import asyncio
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"


async def main():
    async with httpx.AsyncClient(timeout=180.0) as client:
        print("=" * 80)
        print("SOL Correlation Analysis - Strategy Factory Demo")
        print("=" * 80)

        # Step 1: Generate SQL executable using AI (text-to-SQL)
        print("\n[Step 1] Generating SQL executable using AI...")
        sql_exec = await client.post(
            f"{BASE_URL}/executables/generate-sql",
            json={
                "name": "Fetch SOL Market Data",
                "description": "Fetch SOL price, volume, and market_cap from the crypto_prices table for the symbol 'SOL', ordered by date descending, limit to 30 most recent records"
            }
        )
        sql_exec_data = sql_exec.json()
        sql_exec_id = sql_exec_data["id"]
        print(f"✓ Generated SQL executable: {sql_exec_id}")
        print(f"  Generated Query:\n{sql_exec_data['query']}")

        # Step 2: Generate SQL executable for CT sentiment data using AI
        print("\n[Step 2] Generating SQL executable for CT sentiment data...")
        sentiment_exec = await client.post(
            f"{BASE_URL}/executables/generate-sql",
            json={
                "name": "Fetch CT Sentiment on X",
                "description": "Fetch sentiment analysis data for Solana (SOL) from the twitter_sentiment table, including sentiment scores, key themes, and discussion volume for crypto traders, ordered by timestamp descending, limit to 30 most recent records"
            }
        )
        sentiment_exec_data = sentiment_exec.json()
        sentiment_exec_id = sentiment_exec_data["id"]
        print(f"✓ Generated SQL executable: {sentiment_exec_id}")
        print(f"  Generated Query:\n{sentiment_exec_data['query']}")

        # Step 3: Generate Output executable (metadata only, script generated at execution time)
        print("\n[Step 3] Creating Output executable for correlation visualization...")
        output_exec = await client.post(
            f"{BASE_URL}/executables/generate-output",
            json={
                "name": "SOL Correlation Visualization",
                "chart_type": "line_chart",
                "data_description": "SOL price, volume, market cap over time correlated with CT sentiment scores and key themes from X"
            }
        )
        output_exec_data = output_exec.json()
        output_exec_id = output_exec_data["id"]
        print(f"✓ Created Output executable: {output_exec_id}")
        print(f"  Description: {output_exec_data['description']}")

        # Step 4: Create blueprint with ordered steps
        print("\n[Step 4] Creating blueprint with ordered execution steps...")
        blueprint = await client.post(
            f"{BASE_URL}/blueprints/",
            json={
                "name": "SOL Correlation Analysis",
                "description": "Analyze correlation between SOL price/volume/marketcap and CT sentiment on X",
                "executable_ids": [sql_exec_id, sentiment_exec_id, output_exec_id],
                "steps": [
                    {
                        "executable_ids": [sql_exec_id, sentiment_exec_id]  # Step 1: Run both SQL queries concurrently
                    },
                    {
                        "executable_ids": [output_exec_id]  # Step 2: Run Output with results from step 1
                    }
                ]
            }
        )
        blueprint_data = blueprint.json()
        blueprint_id = blueprint_data["id"]
        print(f"✓ Created blueprint: {blueprint_id}")
        print(f"  Step 1: Price SQL & Sentiment SQL (concurrent)")
        print(f"  Step 2: Output (uses results from Step 1)")

        # Step 5: Create simulation
        print("\n[Step 5] Creating simulation...")
        simulation = await client.post(
            f"{BASE_URL}/simulations/",
            json={"blueprint_id": blueprint_id}
        )
        simulation_data = simulation.json()
        simulation_id = simulation_data["id"]
        print(f"✓ Created simulation: {simulation_id}")

        # Step 6: Skip input generation - SQL queries don't need inputs
        print("\n[Step 6] Skipping input generation (SQL queries don't require inputs)")

        print("\n" + "=" * 80)
        print("BENCHMARK: FIRST RUN (Script Generation)")
        print("=" * 80)

        # First execution - will generate the Python script
        print("\n[Run 1] Executing simulation for the FIRST time...")
        start_time_1 = time.time()

        execute_result_1 = await client.post(
            f"{BASE_URL}/simulations/{simulation_id}/execute"
        )

        if execute_result_1.status_code != 200:
            print(f"✗ Execution failed with status {execute_result_1.status_code}")
            print(f"Error: {execute_result_1.text}")
            return

        end_time_1 = time.time()
        execution_time_1 = end_time_1 - start_time_1

        execute_data_1 = execute_result_1.json()
        print(f"✓ First execution completed: {execute_data_1['status']}")
        print(f"⏱️  Time taken: {execution_time_1:.2f} seconds")

        # Retrieve first results
        results_1 = await client.get(
            f"{BASE_URL}/simulations/{simulation_id}/results"
        )
        results_data_1 = results_1.json()

        # Save the generated script
        python_script_1 = results_data_1.get(output_exec_id, "")

        print("\n" + "=" * 80)
        print("BENCHMARK: SECOND RUN (Cached Script)")
        print("=" * 80)

        # Create a second simulation with the same blueprint
        print("\n[Run 2] Creating new simulation for SECOND run...")
        simulation_2 = await client.post(
            f"{BASE_URL}/simulations/",
            json={"blueprint_id": blueprint_id}
        )
        simulation_2_data = simulation_2.json()
        simulation_2_id = simulation_2_data["id"]
        print(f"✓ Created second simulation: {simulation_2_id}")

        # Second execution - should reuse cached script (if deterministic)
        print("\n[Run 2] Executing simulation for the SECOND time...")
        start_time_2 = time.time()

        execute_result_2 = await client.post(
            f"{BASE_URL}/simulations/{simulation_2_id}/execute"
        )

        if execute_result_2.status_code != 200:
            print(f"✗ Execution failed with status {execute_result_2.status_code}")
            print(f"Error: {execute_result_2.text}")
            return

        end_time_2 = time.time()
        execution_time_2 = end_time_2 - start_time_2

        execute_data_2 = execute_result_2.json()
        print(f"✓ Second execution completed: {execute_data_2['status']}")
        print(f"⏱️  Time taken: {execution_time_2:.2f} seconds")

        # Retrieve second results
        results_2 = await client.get(
            f"{BASE_URL}/simulations/{simulation_2_id}/results"
        )
        results_data_2 = results_2.json()

        python_script_2 = results_data_2.get(output_exec_id, "")

        print("\n" + "=" * 80)
        print("FINAL RESULTS & COMPARISON")
        print("=" * 80)

        # Display timing comparison
        print("\n📊 TIMING COMPARISON:")
        print(f"  First Run:  {execution_time_1:.2f} seconds (Generated new Python script)")
        print(f"  Second Run: {execution_time_2:.2f} seconds (Should reuse cached script)")

        speedup = execution_time_1 / execution_time_2 if execution_time_2 > 0 else 0
        time_saved = execution_time_1 - execution_time_2
        print(f"  Speedup:    {speedup:.2f}x faster")
        print(f"  Time saved: {time_saved:.2f} seconds")

        # Check if scripts are identical (they should be for deterministic inputs)
        scripts_identical = python_script_1.strip() == python_script_2.strip()
        print(f"\n📝 SCRIPT COMPARISON:")
        print(f"  Scripts identical: {scripts_identical}")
        if scripts_identical:
            print(f"  ✓ Cache working correctly - same script reused")
        else:
            print(f"  ⚠️  Scripts differ - cache may not be working")

        print("\n📄 GENERATED PYTHON SCRIPT (Run 1):")
        print("-" * 80)
        print(python_script_1[:500] + "..." if len(python_script_1) > 500 else python_script_1)
        print("-" * 80)

        print("\n💾 SAMPLE DATA (SQL - Price Data):")
        sql_data = results_data_1.get(sql_exec_id, [])
        print(json.dumps(sql_data[:3] if isinstance(sql_data, list) else sql_data, indent=2))

        print("\n💾 SAMPLE DATA (SQL - Sentiment Data):")
        sentiment_data = results_data_1.get(sentiment_exec_id, [])
        print(json.dumps(sentiment_data[:3] if isinstance(sentiment_data, list) else sentiment_data, indent=2))

        print("\n" + "=" * 80)
        print("✅ DETERMINISTIC TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nKey Findings:")
        print("- Both runs used SQL executables only (deterministic)")
        print("- Python script should be identical in both runs")
        print("- Second run should be faster (cached script)")
        print("\nNext: Run test_sol_correlation_nondeterministic.py to see LLM impact")


if __name__ == "__main__":
    print("\nMake sure the FastAPI server is running: python main.py")
    print("Press Enter to continue...")
    input()

    asyncio.run(main())
