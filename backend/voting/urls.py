from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView, UserDetailView, PollViewSet, VoteView,
    AdminPollListView, AdminPollDetailView,
    AdminApprovePollView, AdminRejectPollView,
    AdminDashboardView
)

router = DefaultRouter()
router.register(r'polls', PollViewSet, basename='poll')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('', include(router.urls)),
    path('polls/<int:poll_id>/vote/', VoteView.as_view(), name='vote'),

    path('admin/polls/', AdminPollListView.as_view(), name='admin_poll_list'),
    path('admin/polls/<int:poll_id>/', AdminPollDetailView.as_view(), name='admin_poll_detail'),
    path('admin/polls/<int:poll_id>/approve/', AdminApprovePollView.as_view(), name='admin_approve_poll'),
    path('admin/polls/<int:poll_id>/reject/', AdminRejectPollView.as_view(), name='admin_reject_poll'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
]
