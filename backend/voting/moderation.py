import random
import threading
import time
from django.utils import timezone
from django.db import close_old_connections
from django.conf import settings


ILLEGAL_KEYWORDS = [
    '赌博', '博彩', '彩票', '赌球',
    '色情', '黄色', '卖淫', '嫖娼',
    '毒品', '吸毒', '贩毒',
    '诈骗', '传销', '非法集资',
    '枪支', '弹药', '军火',
    '假币', '洗钱',
    '暴力', '恐怖', '极端',
    '代考', '作弊',
    '刷票', '水军',
    '贷款', '高利贷', '裸贷',
]

GREY_INDUSTRY_KEYWORDS = [
    '刷单', '刷信誉', '刷钻',
    '兼职打字', '日结',
    '微商代理', '三级分销',
    '网络赚钱', '轻松赚钱', '月入过万',
    '保健品', '壮阳', '丰胸',
    '高仿', '精仿', 'A货',
    '发票', '代开发票',
    '办证', '刻章',
]


class ModerationTaskQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._tasks = []
        self._lock = threading.Lock()
        self._worker_thread = None
        self._stop_event = threading.Event()
        self._start_worker()

    def _start_worker(self):
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def _worker(self):
        while not self._stop_event.is_set():
            task = None
            with self._lock:
                if self._tasks:
                    task = self._tasks.pop(0)

            if task:
                try:
                    poll_id, scheduled_time = task
                    delay = scheduled_time - time.time()
                    if delay > 0:
                        time.sleep(delay)
                    self._execute_moderation(poll_id)
                except Exception as e:
                    print(f'Moderation task error: {e}')
                finally:
                    close_old_connections()
            else:
                time.sleep(0.5)

    def _execute_moderation(self, poll_id):
        from .models import Poll

        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return

        if poll.status != Poll.STATUS_PENDING:
            return

        is_illegal, reason = check_poll_content(poll)

        poll.reviewed_at = timezone.now()
        if is_illegal:
            poll.status = Poll.STATUS_REJECTED
            poll.reject_reason = reason
            poll.is_active = False
        else:
            poll.status = Poll.STATUS_APPROVED
            poll.is_active = True

        poll.save()

    def add_task(self, poll_id, delay_seconds=None):
        if delay_seconds is None:
            if getattr(settings, 'DEBUG', False):
                delay_seconds = random.randint(1, 3)
            else:
                delay_seconds = random.randint(60, 300)

        scheduled_time = time.time() + delay_seconds

        with self._lock:
            self._tasks.append((poll_id, scheduled_time))

        return delay_seconds


_moderation_queue = None


def get_moderation_queue():
    global _moderation_queue
    if _moderation_queue is None:
        _moderation_queue = ModerationTaskQueue()
    return _moderation_queue


def check_illegal_content(text):
    if not text:
        return False, None

    text_lower = text.lower()

    for keyword in ILLEGAL_KEYWORDS:
        if keyword in text_lower:
            return True, f'检测到违法关键词: {keyword}'

    for keyword in GREY_INDUSTRY_KEYWORDS:
        if keyword in text_lower:
            return True, f'检测到灰产关键词: {keyword}'

    return False, None


def check_poll_content(poll):
    content_to_check = f'{poll.title} {poll.description}'
    for option in poll.options.all():
        content_to_check += f' {option.text}'

    return check_illegal_content(content_to_check)


def submit_moderation_task(poll):
    queue = get_moderation_queue()
    delay = queue.add_task(poll.id)
    return delay


def auto_moderate_poll(poll):
    from .models import Poll

    if poll.status != Poll.STATUS_PENDING:
        return

    is_illegal, reason = check_poll_content(poll)

    poll.reviewed_at = timezone.now()
    if is_illegal:
        poll.status = Poll.STATUS_REJECTED
        poll.reject_reason = reason
        poll.is_active = False
    else:
        poll.status = Poll.STATUS_APPROVED
        poll.is_active = True

    poll.save()
    return poll.status, poll.reject_reason if is_illegal else None
