#!/usr/bin/env python3
"""
Demo Script for Natural Language Queries
Demonstrates Cohere AI integration with safety compliance analysis
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Backend API endpoint
API_URL = os.getenv("API_URL", "https://sre-backend-az1.azurewebsites.net")

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def demo_natural_language_search():
    """Demo natural language image search"""
    print_header("DEMO: Natural Language Image Search")

    queries = [
        "turbine sites with workers without hard hats",
        "sites with high safety compliance",
        "engineer with hard hat and tablet in hand"
    ]

    for query in queries:
        print(f"Query: '{query}'")
        try:
            response = requests.post(
                f"{API_URL}/sre/images/search-nl",
                json={"query": query, "top_k": 5},
                timeout=30
            )
            if response.ok:
                results = response.json()
                print(f"✅ Found {len(results.get('results', []))} matches")
                for i, result in enumerate(results.get('results', [])[:3], 1):
                    print(f"   {i}. {result.get('image_id')} - Score: {result.get('similarity_score', 0):.3f}")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")
        print()

def demo_safety_analysis():
    """Demo safety compliance analysis"""
    print_header("DEMO: Safety Compliance Analysis")

    try:
        response = requests.post(
            f"{API_URL}/sre/images/safety-analysis",
            json={"max_images": 20},
            timeout=30
        )
        if response.ok:
            analysis = response.json()
            print("✅ Safety Analysis Complete\n")
            print(f"Overall Score: {analysis.get('overall_safety_score', 0)}/100")
            print(f"\nFindings:")
            for finding in analysis.get('findings', [])[:5]:
                print(f"  • {finding}")
            print(f"\nRecommendations:")
            for rec in analysis.get('recommendations', [])[:3]:
                print(f"  • {rec}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def demo_chat_with_images():
    """Demo RAG-based chat about images"""
    print_header("DEMO: Chat with Site Images (RAG)")

    questions = [
        "What safety violations do you see across our sites?",
        "Which sites need immediate attention?",
        "Describe the overall safety compliance posture"
    ]

    for question in questions:
        print(f"Question: '{question}'")
        try:
            response = requests.post(
                f"{API_URL}/sre/images/chat",
                json={"query": question, "max_results": 10},
                timeout=30
            )
            if response.ok:
                result = response.json()
                print(f"✅ Response:\n{result.get('answer', 'No answer')[:200]}...\n")
            else:
                print(f"❌ Error: {response.status_code}\n")
        except Exception as e:
            print(f"❌ Exception: {e}\n")

def demo_log_analysis():
    """Demo log analysis for Error 400"""
    print_header("DEMO: Log Analysis - Top IP Addresses")

    try:
        response = requests.post(
            f"{API_URL}/sre/top-ips",
            json={"status_code": "400", "top_n": 10},
            timeout=30
        )
        if response.ok:
            result = response.json()
            print("✅ Top IPs generating Error 400:\n")
            for ip_data in result.get('top_ips', [])[:5]:
                print(f"  {ip_data['ip']}: {ip_data['count']} requests")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def demo_system_status():
    """Demo system status check"""
    print_header("DEMO: System Status Check")

    try:
        response = requests.get(f"{API_URL}/sre/status", timeout=10)
        if response.ok:
            status = response.json()
            print("✅ System Status:\n")
            print(f"Deployment: {status['deployment']['version']} ({status['deployment']['zone']})")
            print(f"\nAzure Services:")
            for service, state in status['azure_services'].items():
                print(f"  • {service}: {state}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all demos"""
    print("\n")
    print("*" * 70)
    print("  CMPE 273 SRE AI Agent Hackathon - Live Demo")
    print("  Team OPSC: Bala Anbalagan, Varad Poddar, Samip Niraula")
    print("*" * 70)

    # Check if backend is accessible
    print(f"\n🔗 Backend API: {API_URL}")
    try:
        response = requests.get(f"{API_URL}/sre/deployment-version", timeout=5)
        if response.ok:
            print(f"✅ Backend online: {response.json()}")
        else:
            print(f"⚠️  Backend returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        print("\n⚠️  Make sure the backend is running and accessible!")
        return

    # Run demos
    demo_system_status()
    demo_natural_language_search()
    demo_safety_analysis()
    demo_chat_with_images()
    demo_log_analysis()

    print("\n" + "="*70)
    print("  Demo Complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
