import random
import time
from datetime import datetime, timedelta
from django.utils import timezone


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


def simulate_moderation_delay():
    return random.randint(60, 300)


def auto_moderate_poll(poll):
    from .models import Poll

    if poll.status != Poll.STATUS_PENDING:
        return

    delay = simulate_moderation_delay()
    time.sleep(min(delay, 2))

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
