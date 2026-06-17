from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Poll, Option, Vote


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class OptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Option
        fields = ['id', 'text', 'vote_count']


class PollListSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    has_voted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'creator', 'created_at', 'end_time',
                  'is_active', 'allow_multiple', 'total_votes', 'has_voted']


class PollDetailSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    options = OptionSerializer(many=True)
    total_votes = serializers.IntegerField(read_only=True)
    has_voted = serializers.BooleanField(read_only=True)
    user_votes = serializers.ListField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'creator', 'created_at', 'end_time',
                  'is_active', 'allow_multiple', 'options', 'total_votes', 'has_voted', 'user_votes']


class PollCreateSerializer(serializers.ModelSerializer):
    options = serializers.ListField(child=serializers.CharField(max_length=200), write_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'end_time', 'allow_multiple', 'options']
        read_only_fields = ['id']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        for option_text in options_data:
            Option.objects.create(poll=poll, text=option_text)
        return poll


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'poll', 'option', 'voted_at']
        read_only_fields = ['user', 'poll', 'voted_at']


class VoteCreateSerializer(serializers.Serializer):
    option_ids = serializers.ListField(child=serializers.IntegerField())

    def validate(self, attrs):
        poll = self.context['poll']
        if not poll.is_active:
            raise serializers.ValidationError("This poll is not active.")
        if poll.end_time and poll.end_time < poll.end_time.now():
            raise serializers.ValidationError("This poll has ended.")
        return attrs


class PollResultSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)
    total_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'options', 'total_votes']
