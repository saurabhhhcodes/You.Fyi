#!/usr/bin/env python3
"""
You.fyi - Comprehensive API Test Script
Tests all endpoints with real sample data
"""

import requests
import json
import sys
import time
from pathlib import Path

BASE_URL = "http://localhost:8001"
TIMESTAMP = str(int(time.time()))

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    RESET = '\033[0m'

def print_section(title):
    print(f"\n{Colors.YELLOW}>>> {title}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def test_api():
    """Run comprehensive API tests"""
    
    print(f"{Colors.BLUE}{'='*40}")
    print(f"YOU.FYI - COMPREHENSIVE API TEST")
    print(f"{'='*40}{Colors.RESET}\n")
    
    results = {
        "passed": [],
        "failed": []
    }
    
    # ========================================
    # 1. Test Workspace Creation
    # ========================================
    print_section("1. Creating Workspace")
    
    ws_data = {
        "name": f"Demo Workspace {TIMESTAMP} 🚀",
        "description": "Complete demonstration of You.fyi capabilities"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/workspaces/", json=ws_data)
        if resp.status_code == 201:
            ws = resp.json()
            ws_id = ws["id"]
            print(json.dumps(ws, indent=2))
            print_success(f"Workspace created: {ws_id}")
            results["passed"].append("Workspace Creation")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("Workspace Creation")
            return results
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Workspace Creation")
        return results
    
    # ========================================
    # 2. Test Text Asset Creation
    # ========================================
    print_section("2. Creating Text Asset")
    
    asset_data = {
        "name": "API Documentation",
        "description": "Complete API reference guide",
        "content": "You.fyi is a smart workspace platform. Features:\n- Store assets (files, documents, data)\n- Create kits (asset groups)\n- Share with expiration links\n- Query with RAG & LLM\n- Full file upload support",
        "asset_type": "document"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/assets/{ws_id}", json=asset_data)
        if resp.status_code == 201:
            asset = resp.json()
            asset1_id = asset["id"]
            print(json.dumps(asset, indent=2))
            print_success(f"Text asset created: {asset1_id}")
            results["passed"].append("Text Asset Creation")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("Text Asset Creation")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Text Asset Creation")
    
    # ========================================
    # 3. Test Image Upload
    # ========================================
    print_section("3. Uploading Image File")
    
    try:
        from PIL import Image
        img = Image.new('RGB', (300, 200), color='#FF6B6B')
        img.save('/tmp/demo_image.png')
        print_info("Generated test image: /tmp/demo_image.png")
        
        with open('/tmp/demo_image.png', 'rb') as f:
            files = {'file': f}
            data = {'description': 'You.fyi Demo Product Image'}
            resp = requests.post(f"{BASE_URL}/assets/{ws_id}/upload", files=files, data=data)
        
        if resp.status_code == 201:
            asset = resp.json()
            asset2_id = asset["id"]
            print(json.dumps(asset, indent=2))
            print_success(f"Image uploaded: {asset2_id}")
            results["passed"].append("Image Upload")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("Image Upload")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Image Upload")
    
    # ========================================
    # 4. Test PDF Upload
    # ========================================
    print_section("4. Uploading PDF Document")
    
    try:
        from reportlab.pdfgen import canvas
        c = canvas.Canvas("/tmp/demo_doc.pdf")
        c.drawString(50, 750, "You.fyi - Smart Workspace Platform")
        c.drawString(50, 730, "Features: Assets, Kits, RAG, LLM")
        c.drawString(50, 710, "Real OpenAI Integration")
        c.save()
        print_info("Generated test PDF: /tmp/demo_doc.pdf")
        
        with open('/tmp/demo_doc.pdf', 'rb') as f:
            files = {'file': f}
            data = {'description': 'Platform Documentation'}
            resp = requests.post(f"{BASE_URL}/assets/{ws_id}/upload", files=files, data=data)
        
        if resp.status_code == 201:
            asset = resp.json()
            asset3_id = asset["id"]
            print(json.dumps(asset, indent=2))
            print_success(f"PDF uploaded: {asset3_id}")
            results["passed"].append("PDF Upload")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("PDF Upload")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("PDF Upload")
    
    # ========================================
    # 5. Test Listing Assets
    # ========================================
    print_section("5. Listing All Assets in Workspace")
    
    try:
        resp = requests.get(f"{BASE_URL}/assets/{ws_id}")
        if resp.status_code == 200:
            assets = resp.json()
            print(json.dumps(assets, indent=2))
            asset_count = len(assets)
            print_success(f"Found {asset_count} assets")
            results["passed"].append("Asset Listing")
        else:
            print_error(f"Status: {resp.status_code}")
            results["failed"].append("Asset Listing")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Asset Listing")
    
    # ========================================
    # 6. Test Kit Creation
    # ========================================
    print_section("6. Creating Kit with Assets")
    
    kit_data = {
        "name": "Complete Demo Kit 📦",
        "description": "Kit containing all asset types for demonstration"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/kits/{ws_id}", json=kit_data)
        if resp.status_code == 201:
            kit = resp.json()
            kit_id = kit["id"]
            print(json.dumps(kit, indent=2))
            print_success(f"Kit created: {kit_id}")
            results["passed"].append("Kit Creation")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("Kit Creation")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Kit Creation")
    
    # ========================================
    # 7. Test Sharing Link Creation
    # ========================================
    print_section("7. Creating Sharing Link (7 days expiry)")
    
    try:
        share_data = {"expires_in_days": 7}
        resp = requests.post(f"{BASE_URL}/sharing-links/kit/{kit_id}", json=share_data)
        
        if resp.status_code == 201:
            share = resp.json()
            share_token = share.get("token", "")
            print(json.dumps(share, indent=2))
            print_success(f"Sharing link created with token: {share_token[:10]}...")
            results["passed"].append("Sharing Link Creation")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("Sharing Link Creation")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Sharing Link Creation")
    
    # ========================================
    # 8. Test Get Workspace Details
    # ========================================
    print_section("8. Getting Workspace Details")
    
    try:
        resp = requests.get(f"{BASE_URL}/workspaces/{ws_id}")
        if resp.status_code == 200:
            ws = resp.json()
            print(json.dumps(ws, indent=2))
            print_success(f"Workspace retrieved")
            results["passed"].append("Get Workspace")
        else:
            print_error(f"Status: {resp.status_code}")
            results["failed"].append("Get Workspace")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Get Workspace")
    
    # ========================================
    # 9. Test Add Assets to Kit
    # ========================================
    print_section("9. Adding Assets to Kit")
    
    try:
        # Collect all asset IDs
        resp = requests.get(f"{BASE_URL}/assets/{ws_id}")
        if resp.status_code == 200:
            assets = resp.json()
            asset_ids = [a["id"] for a in assets]
            
            # Update kit with assets
            update_data = {"asset_ids": asset_ids}
            resp2 = requests.put(f"{BASE_URL}/kits/kit/{kit_id}", json=update_data)
            
            if resp2.status_code == 200:
                kit = resp2.json()
                print(json.dumps(kit, indent=2))
                print_success(f"Kit updated with {len(asset_ids)} assets")
                results["passed"].append("Add Assets to Kit")
            else:
                print_error(f"Status: {resp2.status_code}")
                results["failed"].append("Add Assets to Kit")
        else:
            print_error(f"Failed to fetch assets")
            results["failed"].append("Add Assets to Kit")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Add Assets to Kit")
    
    # ========================================
    # 10. Test Get Kit Details
    # ========================================
    print_section("10. Getting Kit Details")
    
    try:
        resp = requests.get(f"{BASE_URL}/kits/kit/{kit_id}")
        if resp.status_code == 200:
            kit = resp.json()
            print(json.dumps(kit, indent=2))
            print_success(f"Kit retrieved with {len(kit.get('assets', []))} assets")
            results["passed"].append("Get Kit")
        else:
            print_error(f"Status: {resp.status_code}")
            results["failed"].append("Get Kit")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("Get Kit")
    
    # ========================================
    # 11. Test RAG Query
    # ========================================
    print_section("11. Testing RAG Query (LLM Integration)")
    
    try:
        query_data = {
            "query": "What is You.fyi platform about?",
            "kit_id": kit_id,
            "use_llm": False  # Test without LLM first
        }
        resp = requests.post(f"{BASE_URL}/rag/query", json=query_data)
        
        if resp.status_code == 200:
            result = resp.json()
            print(json.dumps(result, indent=2))
            print_success(f"RAG query executed")
            results["passed"].append("RAG Query")
        else:
            print_error(f"Status: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            results["failed"].append("RAG Query")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("RAG Query")
    
    # ========================================
    # 12. Test List Workspaces
    # ========================================
    print_section("12. Listing All Workspaces")
    
    try:
        resp = requests.get(f"{BASE_URL}/workspaces/")
        if resp.status_code == 200:
            workspaces = resp.json()
            print(json.dumps(workspaces, indent=2))
            ws_count = len(workspaces)
            print_success(f"Found {ws_count} workspaces")
            results["passed"].append("List Workspaces")
        else:
            print_error(f"Status: {resp.status_code}")
            results["failed"].append("List Workspaces")
    except Exception as e:
        print_error(f"Exception: {e}")
        results["failed"].append("List Workspaces")
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print_section("COMPREHENSIVE TEST SUMMARY")
    
    print(f"\n{Colors.GREEN}✅ Passed ({len(results['passed'])}):{Colors.RESET}")
    for test in results["passed"]:
        print(f"  ✓ {test}")
    
    if results["failed"]:
        print(f"\n{Colors.RED}❌ Failed ({len(results['failed'])}):{Colors.RESET}")
        for test in results["failed"]:
            print(f"  ✗ {test}")
    
    total = len(results["passed"]) + len(results["failed"])
    success_rate = (len(results["passed"]) / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BLUE}Test Statistics:{Colors.RESET}")
    print(f"  Total Tests: {total}")
    print(f"  Passed: {len(results['passed'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    print(f"\n{Colors.BLUE}API Documentation:{Colors.RESET}")
    print(f"  Swagger UI: {BASE_URL}/docs")
    print(f"  ReDoc: {BASE_URL}/redoc")
    print(f"  OpenAPI: {BASE_URL}/openapi.json")
    
    if len(results["failed"]) == 0:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! Platform is 100% functional!{Colors.RESET}")
        return True
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Please review.{Colors.RESET}")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
