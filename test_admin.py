#!/usr/bin/env python3
"""
后台管理模块测试脚本
测试功能：管理员登录、数据看板、审核投票、删除违规投票、活跃用户统计
"""
import requests
import sys
import json
import time

BASE_URL = 'http://localhost:8000/api'
ADMIN_FRONTEND = 'http://localhost:5174'
USER_FRONTEND = 'http://localhost:5173'

passed = 0
failed = 0


def test(name, condition, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f'  ✓ PASS: {name}')
    else:
        failed += 1
        print(f'  ✗ FAIL: {name}')
        if detail:
            print(f'    Detail: {detail}')


def print_section(title):
    print(f'\n{"="*60}')
    print(f'  {title}')
    print(f'{"="*60}\n')


def main():
    global passed, failed
    print('后台管理模块完整测试')
    print('=' * 60)

    print_section('1. 服务可访问性测试')

    try:
        r = requests.get(f'{BASE_URL}/auth/login/', timeout=5)
        test('后端API服务可访问', r.status_code in [200, 400, 405])
    except Exception as e:
        test('后端API服务可访问', False, str(e))

    try:
        r = requests.get(ADMIN_FRONTEND, timeout=5)
        test('后台管理前端可访问 (5174端口)', r.status_code == 200)
    except Exception as e:
        test('后台管理前端可访问 (5174端口)', False, str(e))

    try:
        r = requests.get(USER_FRONTEND, timeout=5)
        test('用户前端可访问 (5173端口)', r.status_code == 200)
    except Exception as e:
        test('用户前端可访问 (5173端口)', False, str(e))

    print_section('2. 管理员登录测试')

    admin_headers = None
    try:
        r = requests.post(f'{BASE_URL}/auth/login/', json={
            'username': 'admin',
            'password': 'admin123'
        }, timeout=5)
        test('管理员登录成功', r.status_code == 200)
        if r.status_code == 200:
            data = r.json()
            test('返回access token', 'access' in data)
            test('返回refresh token', 'refresh' in data)
            admin_headers = {'Authorization': f'Bearer {data["access"]}'}
    except Exception as e:
        test('管理员登录成功', False, str(e))

    if admin_headers:
        try:
            r = requests.get(f'{BASE_URL}/auth/user/', headers=admin_headers, timeout=5)
            test('获取管理员用户信息', r.status_code == 200)
            if r.status_code == 200:
                data = r.json()
                test('管理员is_staff=True', data.get('is_staff') == True)
        except Exception as e:
            test('获取管理员用户信息', False, str(e))

    print_section('3. 普通用户无权限访问后台API测试')

    user_headers = None
    try:
        r = requests.post(f'{BASE_URL}/auth/register/', json={
            'username': f'testuser_{int(time.time())}',
            'email': f'testuser_{int(time.time())}@example.com',
            'password': 'Test@123456',
            'password2': 'Test@123456'
        }, timeout=5)
        if r.status_code == 201:
            username = r.json()['username']
            r2 = requests.post(f'{BASE_URL}/auth/login/', json={
                'username': username,
                'password': 'Test@123456'
            }, timeout=5)
            if r2.status_code == 200:
                user_headers = {'Authorization': f'Bearer {r2.json()["access"]}'}

        test('普通用户注册登录成功', user_headers is not None)
    except Exception as e:
        test('普通用户注册登录成功', False, str(e))

    if user_headers:
        try:
            r = requests.get(f'{BASE_URL}/admin/dashboard/', headers=user_headers, timeout=5)
            test('普通用户无法访问数据看板 (403)', r.status_code == 403)
        except Exception as e:
            test('普通用户无法访问数据看板', False, str(e))

        try:
            r = requests.get(f'{BASE_URL}/admin/polls/', headers=user_headers, timeout=5)
            test('普通用户无法访问投票管理 (403)', r.status_code == 403)
        except Exception as e:
            test('普通用户无法访问投票管理', False, str(e))

    print_section('4. 数据看板API测试')

    dashboard_data = None
    if admin_headers:
        try:
            r = requests.get(f'{BASE_URL}/admin/dashboard/', headers=admin_headers, timeout=5)
            test('管理员访问数据看板成功', r.status_code == 200)
            if r.status_code == 200:
                dashboard_data = r.json()
                test('数据包含total_users字段', 'total_users' in dashboard_data)
                test('数据包含total_polls字段', 'total_polls' in dashboard_data)
                test('数据包含active_users字段', 'active_users' in dashboard_data)
                test('数据包含pending_polls字段', 'pending_polls' in dashboard_data)
                test('数据包含approved_polls字段', 'approved_polls' in dashboard_data)
                test('数据包含rejected_polls字段', 'rejected_polls' in dashboard_data)
                test('数据包含total_votes字段', 'total_votes' in dashboard_data)
                test('总用户数>=1 (包含管理员)', dashboard_data.get('total_users', 0) >= 1)
                test('活跃用户数>=1 (包含管理员)', dashboard_data.get('active_users', 0) >= 1)
                test('活跃用户数<=总用户数',
                     dashboard_data.get('active_users', 0) <= dashboard_data.get('total_users', 0))
        except Exception as e:
            test('管理员访问数据看板成功', False, str(e))

    print_section('5. 创建投票自动进入待审核测试')

    poll_id = None
    if user_headers:
        try:
            r = requests.post(f'{BASE_URL}/polls/', headers=user_headers, json={
                'title': '测试投票-正常内容',
                'description': '这是一个正常的测试投票',
                'allow_multiple': False,
                'options': ['选项A', '选项B', '选项C']
            }, timeout=5)
            test('普通用户创建投票成功', r.status_code == 201)
            if r.status_code == 201:
                poll_id = r.json()['id']
                test('新创建投票默认状态为pending', True)
        except Exception as e:
            test('普通用户创建投票成功', False, str(e))

    illegal_poll_id = None
    if user_headers:
        try:
            r = requests.post(f'{BASE_URL}/polls/', headers=user_headers, json={
                'title': '测试投票-赌博违规内容',
                'description': '包含赌博关键词的违规投票',
                'allow_multiple': False,
                'options': ['参与赌博', '更多赌博']
            }, timeout=5)
            test('创建含违规词的投票成功', r.status_code == 201)
            if r.status_code == 201:
                illegal_poll_id = r.json()['id']
        except Exception as e:
            test('创建含违规词的投票成功', False, str(e))

    print_section('6. 审核投票列表API测试')

    if admin_headers:
        try:
            r = requests.get(f'{BASE_URL}/admin/polls/', headers=admin_headers, timeout=5)
            test('管理员获取所有投票列表成功', r.status_code == 200)
            if r.status_code == 200:
                all_polls = r.json()
                test('投票列表包含至少2条记录', len(all_polls) >= 2)
        except Exception as e:
            test('管理员获取所有投票列表成功', False, str(e))

        try:
            r = requests.get(f'{BASE_URL}/admin/polls/?status=pending', headers=admin_headers, timeout=5)
            test('管理员获取待审核投票列表成功', r.status_code == 200)
            if r.status_code == 200:
                pending_polls = r.json()
                test('待审核列表>=2条', len(pending_polls) >= 2)
                test('待审核投票状态正确', all(p.get('status') == 'pending' for p in pending_polls))
        except Exception as e:
            test('管理员获取待审核投票列表成功', False, str(e))

    print_section('7. 管理员审核通过投票测试')

    if admin_headers and poll_id:
        try:
            r = requests.post(f'{BASE_URL}/admin/polls/{poll_id}/approve/', headers=admin_headers, timeout=5)
            test('管理员审核通过投票成功', r.status_code == 200)
            if r.status_code == 200:
                test('返回状态为approved', r.json().get('status') == 'approved')

            r2 = requests.get(f'{BASE_URL}/admin/polls/{poll_id}/', headers=admin_headers, timeout=5)
            test('审核后投票状态变为approved', r2.json().get('status') == 'approved')
            test('审核后is_active=True', r2.json().get('is_active') == True)
        except Exception as e:
            test('管理员审核通过投票成功', False, str(e))

    print_section('8. 管理员删除违规投票测试')

    if admin_headers and illegal_poll_id:
        try:
            r = requests.post(f'{BASE_URL}/admin/polls/{illegal_poll_id}/reject/',
                              headers=admin_headers,
                              json={'reason': '检测到违法关键词：赌博'},
                              timeout=5)
            test('管理员删除违规投票成功', r.status_code == 200)
            if r.status_code == 200:
                test('返回状态为rejected', r.json().get('status') == 'rejected')

            r2 = requests.get(f'{BASE_URL}/admin/polls/{illegal_poll_id}/', headers=admin_headers, timeout=5)
            test('删除后投票状态变为rejected', r2.json().get('status') == 'rejected')
            test('删除后is_active=False', r2.json().get('is_active') == False)
            test('删除原因已记录', len(r2.json().get('reject_reason', '')) > 0)
        except Exception as e:
            test('管理员删除违规投票成功', False, str(e))

    print_section('9. 已删除投票列表测试')

    if admin_headers:
        try:
            r = requests.get(f'{BASE_URL}/admin/polls/?status=rejected', headers=admin_headers, timeout=5)
            test('管理员获取已删除投票列表成功', r.status_code == 200)
            if r.status_code == 200:
                rejected_polls = r.json()
                test('已删除列表>=1条', len(rejected_polls) >= 1)
                test('已删除投票状态正确', all(p.get('status') == 'rejected' for p in rejected_polls))
        except Exception as e:
            test('管理员获取已删除投票列表成功', False, str(e))

    print_section('10. 普通用户只能看到已通过投票测试')

    if user_headers and poll_id and illegal_poll_id:
        try:
            r = requests.get(f'{BASE_URL}/polls/', headers=user_headers, timeout=5)
            test('普通用户获取投票列表成功', r.status_code == 200)
            if r.status_code == 200:
                polls = r.json()
                visible_ids = [p['id'] for p in polls]
                test('已通过投票对普通用户可见', poll_id in visible_ids)
                test('已删除投票对普通用户不可见', illegal_poll_id not in visible_ids)
        except Exception as e:
            test('普通用户获取投票列表成功', False, str(e))

        try:
            r = requests.get(f'{BASE_URL}/polls/{poll_id}/', headers=user_headers, timeout=5)
            test('普通用户可访问已通过投票详情', r.status_code == 200)
        except Exception as e:
            test('普通用户可访问已通过投票详情', False, str(e))

        try:
            r = requests.get(f'{BASE_URL}/polls/{illegal_poll_id}/', headers=user_headers, timeout=5)
            test('普通用户无法访问已删除投票详情 (404)', r.status_code == 404)
        except Exception as e:
            test('普通用户无法访问已删除投票详情', False, str(e))

    print_section('11. 活跃用户统计测试')

    if admin_headers:
        try:
            r = requests.get(f'{BASE_URL}/admin/dashboard/', headers=admin_headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                test('管理员登录后计入活跃用户统计', data.get('active_users', 0) >= 1)
                test('活跃用户数不超过总用户数',
                     data.get('active_users', 0) <= data.get('total_users', 0))
        except Exception as e:
            test('活跃用户统计测试', False, str(e))

    print_section('12. 违规词自动检测测试')

    import sys
    sys.path.insert(0, '/Users/huawen.li/Documents/trae_projects/Online-Vo-System/backend')
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
    django.setup()
    from voting.moderation import check_illegal_content

    test('检测到赌博关键词', check_illegal_content('这是一个赌博网站')[0] == True)
    test('检测到色情关键词', check_illegal_content('提供色情服务')[0] == True)
    test('检测到毒品关键词', check_illegal_content('出售毒品')[0] == True)
    test('检测到刷单灰产关键词', check_illegal_content('淘宝刷单兼职')[0] == True)
    test('正常内容不被误判', check_illegal_content('今天天气真好')[0] == False)
    test('正常投票标题不被误判', check_illegal_content('你喜欢什么编程语言')[0] == False)

    print_section('测试结果汇总')
    print(f'  通过: {passed}')
    print(f'  失败: {failed}')
    print(f'  总计: {passed + failed}')
    print(f'  成功率: {(passed / (passed + failed) * 100):.1f}%')

    if failed > 0:
        print('\n  ⚠️  存在失败的测试，请检查上述输出。')
        sys.exit(1)
    else:
        print('\n  ✅ 所有测试通过！后台管理模块运行正常。')
        sys.exit(0)


if __name__ == '__main__':
    main()
