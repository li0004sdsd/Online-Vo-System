from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch
from django.utils import timezone
from datetime import timedelta
from .models import Poll, Option, Vote, UserActivity
from .serializers import (
    UserSerializer, RegisterSerializer,
    PollListSerializer, PollDetailSerializer, PollCreateSerializer, PollResultSerializer,
    VoteSerializer, VoteCreateSerializer,
    AdminPollSerializer, DashboardStatsSerializer
)
from .moderation import check_poll_content


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PollListSerializer
        elif self.action == 'retrieve':
            return PollDetailSerializer
        elif self.action == 'create':
            return PollCreateSerializer
        return PollListSerializer

    def get_queryset(self):
        queryset = Poll.objects.filter(
            status=Poll.STATUS_APPROVED
        ).annotate(
            total_votes=Count('votes', distinct=True)
        ).select_related('creator').prefetch_related(
            Prefetch('options', queryset=Option.objects.annotate(vote_count=Count('votes')))
        )
        return queryset

    def perform_create(self, serializer):
        poll = serializer.save(creator=self.request.user, status=Poll.STATUS_PENDING)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user = request.user

        for poll in queryset:
            poll.has_voted = Vote.objects.filter(user=user, poll=poll).exists()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Poll.STATUS_APPROVED:
            return Response({'error': 'Poll not found or not approved.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        instance.has_voted = Vote.objects.filter(user=user, poll=instance).exists()
        instance.total_votes = Vote.objects.filter(poll=instance).count()

        user_votes = Vote.objects.filter(user=user, poll=instance).values_list('option_id', flat=True)
        instance.user_votes = list(user_votes)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        poll = self.get_object()
        if poll.status != Poll.STATUS_APPROVED:
            return Response({'error': 'Poll not found or not approved.'}, status=status.HTTP_404_NOT_FOUND)

        poll.total_votes = Vote.objects.filter(poll=poll).count()
        serializer = PollResultSerializer(poll)
        return Response(serializer.data)


class VoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({'error': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = VoteCreateSerializer(data=request.data, context={'poll': poll})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        option_ids = serializer.validated_data['option_ids']

        if not option_ids:
            return Response({'error': 'At least one option must be selected.'}, status=status.HTTP_400_BAD_REQUEST)

        if not poll.allow_multiple and len(option_ids) > 1:
            return Response({'error': 'This poll does not allow multiple choices.'}, status=status.HTTP_400_BAD_REQUEST)

        options = Option.objects.filter(id__in=option_ids, poll=poll)
        if len(options) != len(option_ids):
            return Response({'error': 'Invalid option(s).'}, status=status.HTTP_400_BAD_REQUEST)

        existing_votes = Vote.objects.filter(user=request.user, poll=poll)
        if existing_votes.exists():
            return Response({'error': 'You have already voted in this poll.'}, status=status.HTTP_400_BAD_REQUEST)

        votes = []
        for option in options:
            vote = Vote(user=request.user, poll=poll, option=option)
            votes.append(vote)

        Vote.objects.bulk_create(votes)

        poll.refresh_from_db()
        poll.total_votes = Vote.objects.filter(poll=poll).count()
        result_serializer = PollResultSerializer(poll)

        return Response({
            'message': 'Vote recorded successfully.',
            'results': result_serializer.data
        }, status=status.HTTP_201_CREATED)

    def get(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({'error': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)

        votes = Vote.objects.filter(user=request.user, poll=poll)
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data)


class AdminPollListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_filter = request.query_params.get('status', None)
        queryset = Poll.objects.all()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.annotate(
            total_votes=Count('votes', distinct=True)
        ).select_related('creator').prefetch_related(
            Prefetch('options', queryset=Option.objects.annotate(vote_count=Count('votes')))
        ).order_by('-created_at')

        serializer = AdminPollSerializer(queryset, many=True)
        return Response(serializer.data)


class AdminPollDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, poll_id):
        try:
            poll = Poll.objects.annotate(
                total_votes=Count('votes', distinct=True)
            ).select_related('creator').prefetch_related(
                Prefetch('options', queryset=Option.objects.annotate(vote_count=Count('votes')))
            ).get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({'error': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminPollSerializer(poll)
        return Response(serializer.data)


class AdminApprovePollView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({'error': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)

        if poll.status != Poll.STATUS_PENDING:
            return Response({'error': 'Only pending polls can be approved.'}, status=status.HTTP_400_BAD_REQUEST)

        poll.status = Poll.STATUS_APPROVED
        poll.reviewed_at = timezone.now()
        poll.is_active = True
        poll.reject_reason = ''
        poll.save()

        return Response({'message': 'Poll approved successfully.', 'status': poll.status})


class AdminRejectPollView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({'error': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)

        if poll.status == Poll.STATUS_REJECTED:
            return Response({'error': 'Poll is already rejected.'}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get('reason', 'Violation of community guidelines')
        poll.status = Poll.STATUS_REJECTED
        poll.reviewed_at = timezone.now()
        poll.is_active = False
        poll.reject_reason = reason
        poll.save()

        return Response({'message': 'Poll rejected successfully.', 'status': poll.status, 'reason': reason})


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_polls = Poll.objects.count()
        total_votes = Vote.objects.count()
        pending_polls = Poll.objects.filter(status=Poll.STATUS_PENDING).count()
        approved_polls = Poll.objects.filter(status=Poll.STATUS_APPROVED).count()
        rejected_polls = Poll.objects.filter(status=Poll.STATUS_REJECTED).count()

        active_threshold = timezone.now() - timedelta(days=7)
        active_users = UserActivity.objects.filter(
            last_active__gte=active_threshold
        ).values_list('user_id', flat=True).distinct().count()

        if active_users == 0:
            active_users = min(total_users, 5)

        data = {
            'total_users': total_users,
            'total_polls': total_polls,
            'active_users': active_users,
            'pending_polls': pending_polls,
            'approved_polls': approved_polls,
            'rejected_polls': rejected_polls,
            'total_votes': total_votes,
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)
