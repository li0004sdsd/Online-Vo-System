import requests
import json
import sys
from datetime import datetime

FRONTEND_URL = 'http://localhost:5173'
BACKEND_URL = 'http://localhost:8000/api'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_title(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")

def print_result(name, passed, details=''):
    status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
    print(f"  {status} - {name}")
    if details and not passed:
        print(f"      {Colors.YELLOW}{details}{Colors.ENDC}")

def print_summary(results):
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}  测试总结{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"  总测试数: {total}")
    print(f"  通过: {Colors.GREEN}{passed}{Colors.ENDC}")
    print(f"  失败: {Colors.RED}{failed}{Colors.ENDC}")
    print(f"  成功率: {Colors.BOLD}{(passed/total*100):.1f}%{Colors.ENDC}")
    
    if failed > 0:
        print(f"\n  {Colors.RED}失败的测试:{Colors.ENDC}")
        for r in results:
            if not r['passed']:
                print(f"    - {r['name']}: {r.get('details', '')}")
    
    return passed == total

def test_frontend_accessible():
    """测试前端服务器是否可访问"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code == 200, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_backend_accessible():
    """测试后端API是否可访问（无需认证的注册接口）"""
    try:
        response = requests.get(f'{BACKEND_URL}/auth/login/', timeout=5)
        return response.status_code == 405, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_user_registration():
    """测试用户注册功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "username": f"e2e_user_{timestamp}",
        "email": f"e2e_{timestamp}@example.com",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    
    try:
        response = requests.post(f'{BACKEND_URL}/auth/register/', json=user_data, timeout=5)
        if response.status_code != 201:
            return False, f"Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        if 'id' not in data or 'username' not in data:
            return False, "Response missing required fields"
        
        return True, f"User created: {data['username']} (ID: {data['id']})"
    except Exception as e:
        return False, str(e)

def test_user_login():
    """测试用户登录功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    register_data = {
        "username": f"e2e_login_{timestamp}",
        "email": f"e2e_login_{timestamp}@example.com",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    
    try:
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        
        response = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        if response.status_code != 200:
            return False, f"Login failed: Status {response.status_code}"
        
        data = response.json()
        if 'access' not in data or 'refresh' not in data:
            return False, "Tokens not in response"
        
        return True, "Login successful, tokens received"
    except Exception as e:
        return False, str(e)

def test_create_poll():
    """测试创建投票功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_poll_{timestamp}",
            "email": f"e2e_poll_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "E2E Test Poll - Favorite Color",
            "description": "What is your favorite color?",
            "allow_multiple": False,
            "options": ["Red", "Blue", "Green", "Yellow"]
        }
        
        response = requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        if response.status_code != 201:
            return False, f"Create poll failed: Status {response.status_code}, {response.text}"
        
        data = response.json()
        if 'id' not in data:
            return False, "Poll ID not in response"
        
        return True, f"Poll created: ID {data['id']}"
    except Exception as e:
        return False, str(e)

def test_get_poll_list():
    """测试获取投票列表功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_list_{timestamp}",
            "email": f"e2e_list_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "List Test Poll",
            "description": "Test poll for list",
            "allow_multiple": False,
            "options": ["A", "B", "C"]
        }
        requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        
        response = requests.get(f'{BACKEND_URL}/polls/', headers=headers, timeout=5)
        if response.status_code != 200:
            return False, f"Get list failed: Status {response.status_code}"
        
        data = response.json()
        if not isinstance(data, list):
            return False, "Response is not a list"
        
        return True, f"Poll list retrieved: {len(data)} polls"
    except Exception as e:
        return False, str(e)

def test_get_poll_detail():
    """测试获取投票详情功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_detail_{timestamp}",
            "email": f"e2e_detail_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "Detail Test Poll",
            "description": "Test poll for detail",
            "allow_multiple": True,
            "options": ["Option 1", "Option 2", "Option 3"]
        }
        create_resp = requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        poll_id = create_resp.json()['id']
        
        response = requests.get(f'{BACKEND_URL}/polls/{poll_id}/', headers=headers, timeout=5)
        if response.status_code != 200:
            return False, f"Get detail failed: Status {response.status_code}"
        
        data = response.json()
        if 'options' not in data or len(data['options']) != 3:
            return False, "Options missing or incorrect count"
        
        return True, f"Poll detail retrieved: {data['title']}"
    except Exception as e:
        return False, str(e)

def test_vote_single_choice():
    """测试单选投票功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_vote1_{timestamp}",
            "email": f"e2e_vote1_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "Single Choice Vote Test",
            "allow_multiple": False,
            "options": ["A", "B", "C"]
        }
        create_resp = requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        poll_id = create_resp.json()['id']
        
        detail_resp = requests.get(f'{BACKEND_URL}/polls/{poll_id}/', headers=headers, timeout=5)
        option_id = detail_resp.json()['options'][0]['id']
        
        vote_data = {"option_ids": [option_id]}
        response = requests.post(f'{BACKEND_URL}/polls/{poll_id}/vote/', json=vote_data, headers=headers, timeout=5)
        
        if response.status_code != 201:
            return False, f"Vote failed: Status {response.status_code}, {response.text}"
        
        return True, "Single choice vote successful"
    except Exception as e:
        return False, str(e)

def test_vote_multiple_choice():
    """测试多选投票功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_vote2_{timestamp}",
            "email": f"e2e_vote2_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "Multiple Choice Vote Test",
            "allow_multiple": True,
            "options": ["A", "B", "C", "D"]
        }
        create_resp = requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        poll_id = create_resp.json()['id']
        
        detail_resp = requests.get(f'{BACKEND_URL}/polls/{poll_id}/', headers=headers, timeout=5)
        options = detail_resp.json()['options']
        option_ids = [options[0]['id'], options[1]['id'], options[2]['id']]
        
        vote_data = {"option_ids": option_ids}
        response = requests.post(f'{BACKEND_URL}/polls/{poll_id}/vote/', json=vote_data, headers=headers, timeout=5)
        
        if response.status_code != 201:
            return False, f"Multiple vote failed: Status {response.status_code}, {response.text}"
        
        return True, "Multiple choice vote successful (3 options)"
    except Exception as e:
        return False, str(e)

def test_get_poll_results():
    """测试获取投票结果功能"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_result_{timestamp}",
            "email": f"e2e_result_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "Results Test Poll",
            "allow_multiple": False,
            "options": ["X", "Y", "Z"]
        }
        create_resp = requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        poll_id = create_resp.json()['id']
        
        detail_resp = requests.get(f'{BACKEND_URL}/polls/{poll_id}/', headers=headers, timeout=5)
        option_id = detail_resp.json()['options'][0]['id']
        
        vote_data = {"option_ids": [option_id]}
        requests.post(f'{BACKEND_URL}/polls/{poll_id}/vote/', json=vote_data, headers=headers, timeout=5)
        
        response = requests.get(f'{BACKEND_URL}/polls/{poll_id}/results/', headers=headers, timeout=5)
        if response.status_code != 200:
            return False, f"Get results failed: Status {response.status_code}"
        
        data = response.json()
        if 'total_votes' not in data or data['total_votes'] != 1:
            return False, f"Vote count incorrect: {data.get('total_votes', 'N/A')}"
        
        for opt in data['options']:
            if 'vote_count' not in opt:
                return False, "vote_count missing from options"
        
        return True, f"Results retrieved: total_votes={data['total_votes']}"
    except Exception as e:
        return False, str(e)

def test_unauthorized_access():
    """测试未授权访问拦截"""
    try:
        response = requests.get(f'{BACKEND_URL}/polls/', timeout=5)
        if response.status_code != 401:
            return False, f"Expected 401, got {response.status_code}"
        return True, "Unauthorized access correctly blocked"
    except Exception as e:
        return False, str(e)

def test_duplicate_vote_prevention():
    """测试重复投票拦截"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        register_data = {
            "username": f"e2e_dup_{timestamp}",
            "email": f"e2e_dup_{timestamp}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        requests.post(f'{BACKEND_URL}/auth/register/', json=register_data, timeout=5)
        
        login_data = {
            "username": register_data['username'],
            "password": "TestPass123!"
        }
        login_resp = requests.post(f'{BACKEND_URL}/auth/login/', json=login_data, timeout=5)
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        poll_data = {
            "title": "Duplicate Vote Test",
            "allow_multiple": False,
            "options": ["A", "B"]
        }
        create_resp = requests.post(f'{BACKEND_URL}/polls/', json=poll_data, headers=headers, timeout=5)
        poll_id = create_resp.json()['id']
        
        detail_resp = requests.get(f'{BACKEND_URL}/polls/{poll_id}/', headers=headers, timeout=5)
        option_id = detail_resp.json()['options'][0]['id']
        
        vote_data = {"option_ids": [option_id]}
        requests.post(f'{BACKEND_URL}/polls/{poll_id}/vote/', json=vote_data, headers=headers, timeout=5)
        
        response = requests.post(f'{BACKEND_URL}/polls/{poll_id}/vote/', json=vote_data, headers=headers, timeout=5)
        if response.status_code != 400:
            return False, f"Expected 400 for duplicate vote, got {response.status_code}"
        
        return True, "Duplicate vote correctly prevented"
    except Exception as e:
        return False, str(e)

def test_frontend_pages():
    """测试前端页面是否可访问"""
    tests = [
        ('/login', '登录页面'),
        ('/register', '注册页面'),
    ]
    
    results = []
    for path, name in tests:
        try:
            response = requests.get(f'{FRONTEND_URL}{path}', timeout=5)
            results.append(response.status_code == 200)
            print_result(name, response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            results.append(False)
            print_result(name, False, str(e))
    
    return all(results), "All frontend pages accessible"

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  在线投票系统 - 端到端集成测试{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  前端: {FRONTEND_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  后端: {BACKEND_URL}{Colors.ENDC}")
    
    results = []
    
    # 1. 可访问性测试
    print_title("1. 服务可访问性测试")
    tests = [
        ("前端服务器", test_frontend_accessible),
        ("后端API", test_backend_accessible),
    ]
    for name, test_func in tests:
        passed, details = test_func()
        results.append({'name': name, 'passed': passed, 'details': details})
        print_result(name, passed, details)
    
    # 2. 用户认证测试
    print_title("2. 用户认证模块测试")
    tests = [
        ("用户注册", test_user_registration),
        ("用户登录", test_user_login),
        ("未授权访问拦截", test_unauthorized_access),
    ]
    for name, test_func in tests:
        passed, details = test_func()
        results.append({'name': name, 'passed': passed, 'details': details})
        print_result(name, passed, details)
    
    # 3. 投票管理测试
    print_title("3. 投票管理模块测试")
    tests = [
        ("创建投票", test_create_poll),
        ("获取投票列表", test_get_poll_list),
        ("获取投票详情", test_get_poll_detail),
    ]
    for name, test_func in tests:
        passed, details = test_func()
        results.append({'name': name, 'passed': passed, 'details': details})
        print_result(name, passed, details)
    
    # 4. 投票功能测试
    print_title("4. 投票功能模块测试")
    tests = [
        ("单选投票", test_vote_single_choice),
        ("多选投票", test_vote_multiple_choice),
        ("重复投票拦截", test_duplicate_vote_prevention),
    ]
    for name, test_func in tests:
        passed, details = test_func()
        results.append({'name': name, 'passed': passed, 'details': details})
        print_result(name, passed, details)
    
    # 5. 结果统计测试
    print_title("5. 结果统计模块测试")
    tests = [
        ("获取投票结果", test_get_poll_results),
    ]
    for name, test_func in tests:
        passed, details = test_func()
        results.append({'name': name, 'passed': passed, 'details': details})
        print_result(name, passed, details)
    
    # 6. 前端页面测试
    print_title("6. 前端页面测试")
    passed, details = test_frontend_pages()
    results.append({'name': '前端页面可访问性', 'passed': passed, 'details': details})
    
    # 总结
    all_passed = print_summary(results)
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}  ✅ 所有测试通过！系统运行正常。{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}  ❌ 部分测试失败，请检查错误信息。{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
