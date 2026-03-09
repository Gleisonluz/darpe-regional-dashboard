#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime

class DarpeApiTester:
    def __init__(self, base_url="https://darpe-dashboard.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_error(self, test_name, error_msg):
        """Log error for later reporting"""
        error_info = f"❌ {test_name}: {error_msg}"
        self.errors.append(error_info)
        print(error_info)

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = self.headers.copy()
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'message' in response_data:
                        print(f"   Response: {response_data['message']}")
                except:
                    pass
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json().get('detail', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                self.log_error(name, error_msg)

            return success, response.json() if response.status_code < 500 else {}

        except requests.exceptions.RequestException as e:
            self.log_error(name, f"Request failed: {str(e)}")
            return False, {}
        except Exception as e:
            self.log_error(name, f"Unexpected error: {str(e)}")
            return False, {}

    def test_health_checks(self):
        """Test basic health endpoints"""
        print("\n=== TESTING HEALTH ENDPOINTS ===")
        self.run_test("API Root", "GET", "", 200)
        self.run_test("Health Check", "GET", "health", 200)

    def test_public_endpoints(self):
        """Test public endpoints"""
        print("\n=== TESTING PUBLIC ENDPOINTS ===")
        
        # Test cities
        success, cities_data = self.run_test("Get Cities", "GET", "public/cidades", 200)
        if success and 'cidades' in cities_data:
            print(f"   Found {len(cities_data['cidades'])} cities")
        
        # Test units
        success, units_data = self.run_test("Get All Units", "GET", "public/unidades", 200)
        if success:
            print(f"   Found {len(units_data)} units")
            
        # Test units with filters
        self.run_test("Filter Units by City", "GET", "public/unidades?cidade=Itajaí", 200)
        self.run_test("Filter Units by Day", "GET", "public/unidades?dia_semana=domingo", 200)
        self.run_test("Filter Units by Name", "GET", "public/unidades?nome=Centro", 200)

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        # Test admin login
        admin_data = {
            "email": "admin@darpe.org",
            "senha": "admin123"
        }
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Admin login successful, role: {response['user']['role']}")
        else:
            self.log_error("Admin Login", "Failed to get access token")
        
        # Test atendente login  
        atendente_data = {
            "email": "atendente@darpe.org",
            "senha": "atendente123"
        }
        success, response = self.run_test("Atendente Login", "POST", "auth/login", 200, atendente_data)
        
        if success:
            print(f"   Atendente login successful, role: {response['user']['role']}")
        
        # Test invalid login
        invalid_data = {
            "email": "invalid@test.com",
            "senha": "wrongpass"
        }
        self.run_test("Invalid Login", "POST", "auth/login", 401, invalid_data)

    def test_protected_endpoints(self):
        """Test protected endpoints with authentication"""
        print("\n=== TESTING PROTECTED ENDPOINTS ===")
        
        if not self.token:
            self.log_error("Protected Endpoints", "No auth token available")
            return
        
        # Test get current user
        self.run_test("Get Current User", "GET", "auth/me", 200, auth_required=True)
        
        # Test units management (admin only)
        self.run_test("Get Units (Admin)", "GET", "units", 200, auth_required=True)
        
        # Test users management (admin only)
        self.run_test("Get Users (Admin)", "GET", "users", 200, auth_required=True)
        
        # Test agenda
        self.run_test("Get Agenda", "GET", "reports/agenda", 200, auth_required=True)

    def test_credential_system(self):
        """Test credential system for atendente"""
        print("\n=== TESTING CREDENTIAL SYSTEM ===")
        
        # Login as atendente first
        atendente_data = {
            "email": "atendente@darpe.org", 
            "senha": "atendente123"
        }
        success, response = self.run_test("Atendente Login for Credentials", "POST", "auth/login", 200, atendente_data)
        
        if success and 'access_token' in response:
            atendente_token = response['access_token']
            # Temporarily change token
            old_token = self.token
            self.token = atendente_token
            
            # Test credential endpoint
            success, cred_response = self.run_test("Get Digital Credential", "GET", "credential", 200, auth_required=True)
            
            if success:
                if 'qr_code' in cred_response:
                    print("   ✅ QR Code generated successfully")
                if 'user' in cred_response:
                    print(f"   User data: {cred_response['user']['nome_completo']}")
            
            # Restore admin token
            self.token = old_token
        else:
            self.log_error("Credential Test", "Could not login as atendente")

    def test_attendance_system(self):
        """Test attendance registration"""
        print("\n=== TESTING ATTENDANCE SYSTEM ===")
        
        # Login as atendente 
        atendente_data = {
            "email": "atendente@darpe.org",
            "senha": "atendente123"
        }
        success, response = self.run_test("Atendente Login for Attendance", "POST", "auth/login", 200, atendente_data)
        
        if success and 'access_token' in response:
            atendente_token = response['access_token']
            old_token = self.token
            self.token = atendente_token
            
            # Get units first
            success, units_data = self.run_test("Get Units for Attendance", "GET", "units", 200, auth_required=True)
            
            if success and len(units_data) > 0:
                unit_id = units_data[0]['id']
                
                # Register attendance
                attendance_data = {
                    "unidade_id": unit_id,
                    "funcao": "pregacao",
                    "observacao": "Test attendance registration"
                }
                self.run_test("Register Attendance", "POST", "attendance", 201, attendance_data, auth_required=True)
                
                # Get attendance records
                self.run_test("Get My Attendances", "GET", "attendance/my-records", 200, auth_required=True)
            
            # Restore admin token
            self.token = old_token
        else:
            self.log_error("Attendance Test", "Could not login as atendente")

    def test_notifications_system(self):
        """Test notifications"""
        print("\n=== TESTING NOTIFICATIONS SYSTEM ===")
        
        if not self.token:
            return
            
        # Test get notifications
        self.run_test("Get Notifications", "GET", "notifications", 200, auth_required=True)
        self.run_test("Get Unread Count", "GET", "notifications/unread-count", 200, auth_required=True)

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting DARPE Regional Itajaí API Tests")
        print("=" * 60)
        
        self.test_health_checks()
        self.test_public_endpoints()  
        self.test_authentication()
        self.test_protected_endpoints()
        self.test_credential_system()
        self.test_attendance_system()
        self.test_notifications_system()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "No tests run")
        
        if self.errors:
            print(f"\n❌ FAILED TESTS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        print("=" * 60)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = DarpeApiTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)