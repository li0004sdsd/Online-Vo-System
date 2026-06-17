import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

def print_response(name, response):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Status: {response.status_code}")
    if response.status_code != 204 and response.content:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")
    print('='*60)

def test_api():
    print("Starting API tests...")
    
    # 1. Test registration
    print("\n" + "="*60)
    print("1. Testing User Registration")
    print("="*60)
    
    user_data = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    
    response = requests.post(f'{BASE_URL}/auth/register/', json=user_data)
    print_response("Register User 1", response)
    assert response.status_code == 201, "Registration failed"
    user1_id = response.json()['id']
    
    # Register second user
    user_data2 = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    response = requests.post(f'{BASE_URL}/auth/register/', json=user_data2)
    print_response("Register User 2", response)
    assert response.status_code == 201, "Registration failed"
    
    # 2. Test login
    print("\n" + "="*60)
    print("2. Testing User Login")
    print("="*60)
    
    login_data = {
        "username": "testuser1",
        "password": "TestPass123!"
    }
    response = requests.post(f'{BASE_URL}/auth/login/', json=login_data)
    print_response("Login User 1", response)
    assert response.status_code == 200, "Login failed"
    tokens = response.json()
    access_token = tokens['access']
    refresh_token = tokens['refresh']
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Login user2
    login_data2 = {
        "username": "testuser2",
        "password": "TestPass123!"
    }
    response = requests.post(f'{BASE_URL}/auth/login/', json=login_data2)
    print_response("Login User 2", response)
    assert response.status_code == 200, "Login failed"
    tokens2 = response.json()
    access_token2 = tokens2['access']
    headers2 = {
        'Authorization': f'Bearer {access_token2}'
    }
    
    # 3. Test get user info
    print("\n" + "="*60)
    print("3. Testing Get User Info")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/auth/user/', headers=headers)
    print_response("Get User Info", response)
    assert response.status_code == 200, "Get user info failed"
    
    # 4. Test token refresh
    print("\n" + "="*60)
    print("4. Testing Token Refresh")
    print("="*60)
    
    response = requests.post(f'{BASE_URL}/auth/refresh/', json={'refresh': refresh_token})
    print_response("Token Refresh", response)
    assert response.status_code == 200, "Token refresh failed"
    
    # 5. Test create poll
    print("\n" + "="*60)
    print("5. Testing Create Poll")
    print("="*60)
    
    poll_data = {
        "title": "Best Programming Language?",
        "description": "What is your favorite programming language?",
        "allow_multiple": False,
        "options": ["Python", "JavaScript", "Java", "Go"]
    }
    response = requests.post(f'{BASE_URL}/polls/', json=poll_data, headers=headers)
    print_response("Create Poll 1 (Single Choice)", response)
    assert response.status_code == 201, "Create poll failed"
    poll1_id = response.json()['id']
    
    # Create multiple choice poll
    poll_data2 = {
        "title": "Which databases have you used?",
        "description": "Select all databases you have experience with",
        "allow_multiple": True,
        "options": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle"]
    }
    response = requests.post(f'{BASE_URL}/polls/', json=poll_data2, headers=headers)
    print_response("Create Poll 2 (Multiple Choice)", response)
    assert response.status_code == 201, "Create poll failed"
    poll2_id = response.json()['id']
    
    # 6. Test list polls
    print("\n" + "="*60)
    print("6. Testing List Polls")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/polls/', headers=headers)
    print_response("List All Polls", response)
    assert response.status_code == 200, "List polls failed"
    polls = response.json()
    print(f"Total polls: {len(polls)}")
    assert len(polls) >= 2, "Expected at least 2 polls"
    
    # 7. Test poll detail
    print("\n" + "="*60)
    print("7. Testing Poll Detail")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/polls/{poll1_id}/', headers=headers)
    print_response("Get Poll 1 Detail", response)
    assert response.status_code == 200, "Get poll detail failed"
    poll_detail = response.json()
    assert poll_detail['id'] == poll1_id
    assert len(poll_detail['options']) == 4
    option1_id = poll_detail['options'][0]['id']
    option2_id = poll_detail['options'][1]['id']
    
    response = requests.get(f'{BASE_URL}/polls/{poll2_id}/', headers=headers)
    print_response("Get Poll 2 Detail", response)
    assert response.status_code == 200, "Get poll detail failed"
    poll2_detail = response.json()
    poll2_option1_id = poll2_detail['options'][0]['id']
    poll2_option2_id = poll2_detail['options'][1]['id']
    poll2_option3_id = poll2_detail['options'][2]['id']
    
    # 8. Test vote - single choice
    print("\n" + "="*60)
    print("8. Testing Vote - Single Choice")
    print("="*60)
    
    vote_data = {
        "option_ids": [option1_id]
    }
    response = requests.post(f'{BASE_URL}/polls/{poll1_id}/vote/', json=vote_data, headers=headers)
    print_response("Vote on Poll 1 (User 1)", response)
    assert response.status_code == 201, "Vote failed"
    
    # Try voting again (should fail)
    response = requests.post(f'{BASE_URL}/polls/{poll1_id}/vote/', json=vote_data, headers=headers)
    print_response("Vote Again on Poll 1 (Should Fail)", response)
    assert response.status_code == 400, "Should not allow voting twice"
    
    # User 2 votes on poll 1
    vote_data2 = {
        "option_ids": [option2_id]
    }
    response = requests.post(f'{BASE_URL}/polls/{poll1_id}/vote/', json=vote_data2, headers=headers2)
    print_response("Vote on Poll 1 (User 2)", response)
    assert response.status_code == 201, "Vote failed"
    
    # 9. Test vote - multiple choice
    print("\n" + "="*60)
    print("9. Testing Vote - Multiple Choice")
    print("="*60)
    
    vote_data_multi = {
        "option_ids": [poll2_option1_id, poll2_option2_id, poll2_option3_id]
    }
    response = requests.post(f'{BASE_URL}/polls/{poll2_id}/vote/', json=vote_data_multi, headers=headers)
    print_response("Vote on Poll 2 (Multiple Options, User 1)", response)
    assert response.status_code == 201, "Multiple choice vote failed"
    
    # Test trying to vote multiple on single choice poll (should fail)
    vote_data_invalid = {
        "option_ids": [option1_id, option2_id]
    }
    response = requests.post(f'{BASE_URL}/polls/{poll1_id}/vote/', json=vote_data_invalid, headers=headers2)
    print_response("Try Multiple Votes on Single Choice Poll (Should Fail)", response)
    assert response.status_code == 400, "Should not allow multiple votes on single choice poll"
    
    # 10. Test get poll results
    print("\n" + "="*60)
    print("10. Testing Get Poll Results")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/polls/{poll1_id}/results/', headers=headers)
    print_response("Get Poll 1 Results", response)
    assert response.status_code == 200, "Get results failed"
    results = response.json()
    print(f"Total votes: {results['total_votes']}")
    assert results['total_votes'] == 2, "Expected 2 votes"
    
    for option in results['options']:
        print(f"  {option['text']}: {option['vote_count']} votes")
    
    response = requests.get(f'{BASE_URL}/polls/{poll2_id}/results/', headers=headers)
    print_response("Get Poll 2 Results", response)
    assert response.status_code == 200, "Get results failed"
    results2 = response.json()
    print(f"Total votes: {results2['total_votes']}")
    assert results2['total_votes'] == 3, "Expected 3 votes"
    
    # 11. Test list polls with vote status
    print("\n" + "="*60)
    print("11. Testing List Polls with Vote Status")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/polls/', headers=headers)
    print_response("List Polls with has_voted status", response)
    polls = response.json()
    for poll in polls:
        print(f"  Poll: {poll['title']}, has_voted: {poll['has_voted']}, votes: {poll['total_votes']}")
    
    # 12. Test unauthorized access
    print("\n" + "="*60)
    print("12. Testing Unauthorized Access")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/polls/')
    print_response("Get Polls Without Auth (Should Fail)", response)
    assert response.status_code == 401, "Should require authentication"
    
    # 13. Test invalid login
    print("\n" + "="*60)
    print("13. Testing Invalid Login")
    print("="*60)
    
    invalid_login = {
        "username": "testuser1",
        "password": "WrongPassword!"
    }
    response = requests.post(f'{BASE_URL}/auth/login/', json=invalid_login)
    print_response("Invalid Login (Should Fail)", response)
    assert response.status_code == 401, "Should not allow invalid login"
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print(f"\nSummary:")
    print(f"- User 1 ID: {user1_id}")
    print(f"- Poll 1 ID (Single Choice): {poll1_id}")
    print(f"- Poll 2 ID (Multiple Choice): {poll2_id}")
    print(f"- Total votes recorded: 5 (2 in poll1, 3 in poll2)")

if __name__ == '__main__':
    test_api()
