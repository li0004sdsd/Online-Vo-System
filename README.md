# Online-Vo-System · 在线投票平台

一个基于 Django REST Framework 和 Vue3 的全栈在线投票系统，支持用户注册登录、创建与参与投票、内容审核以及后台管理，并配套了独立的 API 与端到端自动化测试脚本。

## 技术栈

后端采用 Django + Django REST Framework，使用 JWT 鉴权，并实现了自定义的内容审核（moderation）与中间件（middleware）逻辑。前端基于 Vue 3 + Vite + Element Plus + Vue Router 构建。管理端是一个独立的 admin 模块。

## 测试

项目在根目录提供了 `test_api.py`（接口测试脚本）和 `test_e2e.py`（端到端流程测试，覆盖用户注册、登录、创建投票等场景，带彩色输出与通过率统计），以及 `test_admin.py`（管理后台测试）。`backend/voting/tests.py` 中还包含 Django 单元测试。

## 功能

支持用户注册与登录（JWT 鉴权）、创建投票与参与投票、内容审核（moderation），以及后台管理（admin）。

## 本地运行

后端：

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

前端：

```bash
cd frontend
npm install
npm run dev
```

运行测试：

```bash
python test_api.py
python test_e2e.py
python test_admin.py
```
