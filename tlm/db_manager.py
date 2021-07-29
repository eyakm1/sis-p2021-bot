import functools
from typing import Callable, List
from django.utils import timezone
from django.db.models import F, Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import BadRequest
from tlm.models import Submission, Subscription
from tlm.models import JsonObj, JsonList
from tlm import config


@transaction.atomic
def post_submissions(request_body: JsonList) -> None:
    for submission_data in request_body:
        submission, _ = Submission.objects.get_or_create(cid=submission_data['cid'],
                                                         login=submission_data['login'],
                                                         problem=submission_data['problem'],
                                                         defaults=
                                                         {'rid': submission_data['rid'],
                                                          'judge_link': submission_data['link']})
        if submission.status == 'closed':
            if not submission.target_chat_id:
                submission.status = 'unassigned'
            else:
                submission.status = 'assigned'

        # This subscription always exists as we do not explicitly delete them
        submission_subscription = Subscription.objects.get(cid=submission.cid)
        if submission.status == 'unassigned':
            submission.target_chat_id = submission_subscription.chat_id

        # Check if submission from scraper is newer than one in database
        if submission_data['rid'] > submission.rid:
            submission.rid = submission_data['rid']
            submission.judge_link = submission_data['link']

        submission.save()


@transaction.atomic
def get_waiting() -> JsonList:
    waiting_filter = Q(sent_to_chat=False, chat_rid=None,
                       status__in=['assigned', 'unassigned']) & ~Q(target_chat_id=None) & \
                     (Q(last_snooze_time=None) |
                      Q(last_snooze_time__lt=timezone.now() - config.snooze_interval))
    waiting = Submission.objects.filter(waiting_filter)

    submissions_list = [submission.submission_dict() for submission in waiting]

    return submissions_list


@transaction.atomic
def get_to_delete() -> JsonList:
    delete_filter = Q(sent_to_chat=True) & (
            Q(status='closed') |
            Q(last_update_time__lt=timezone.now() - config.resend_interval,
              status__in=['assigned', 'unassigned']) |
            Q(last_snooze_time__gt=timezone.now() - config.snooze_interval,
              status__in=['assigned', 'unassigned']) |
            ~Q(target_chat_id=F('chat_id')) |
            ~Q(rid=F('chat_rid'))
    )

    to_delete = Submission.objects.filter(delete_filter)

    submissions_list = [submission.tg_msg_dict() for submission in to_delete]

    return submissions_list


def submission_op(fn: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(fn)
    def ret(submission_id: int, *args, **kwargs) -> None:
        with transaction.atomic():
            submission = get_object_or_404(Submission, pk=submission_id)
            fn(submission, *args, **kwargs)
            submission.save()

    return ret


@submission_op
def confirm_send(submission: Submission, request_body: JsonObj) -> None:
    submission.message_id = request_body['tg_msg']['message_id']
    submission.chat_id = request_body['tg_msg']['chat_id']
    submission.chat_rid = request_body['rid']
    submission.last_update_time = timezone.now()
    submission.sent_to_chat = True


@submission_op
def confirm_delete(submission: Submission) -> None:
    submission.sent_to_chat = False
    submission.chat_rid = None
    submission.chat_id = None
    submission.message_id = None


@submission_op
def update_status(submission: Submission, status: str) -> None:
    if status == 'unassigned':
        # This subscription always exists as we do not explicitly delete them
        submission_subscription = Subscription.objects.get(cid=submission.cid)
        submission.target_chat_id = submission_subscription.chat_id
    if status == 'closed' and submission.status == 'unassigned':
        # This assignee will be restored to group id on next scraping
        submission.target_chat_id = None
    submission.status = status


@submission_op
def update_assignee(submission: Submission, assignee: int) -> None:
    submission.target_chat_id = assignee


@submission_op
def snooze(submission: Submission) -> None:
    submission.last_snooze_time = timezone.now()


@transaction.atomic
def subscribe(cid: int, chat_id: int) -> None:
    subscription, _ = Subscription.objects.get_or_create(cid=cid)

    if subscription.chat_id == chat_id:
        raise BadRequest('You have already subscribed to this contest')
    if subscription.chat_id:
        raise BadRequest('There is a chat subscribed to this contest')

    subscription.chat_id = chat_id
    subscription.save()


@transaction.atomic
def unsubscribe(cid: int, chat_id: int) -> None:
    subscription = get_object_or_404(Subscription, cid=cid)

    if subscription.chat_id != chat_id:
        raise BadRequest('You are not subscribed to this contest')

    subscription.chat_id = None
    subscription.save()

    contest_submissions = Submission.objects.filter(cid=cid, status='unassigned')
    contest_submissions.update(target_chat_id=None)


@transaction.atomic
def unsubscribe_all(chat_id: int) -> None:
    all_subscriptions = Subscription.objects.filter(chat_id=chat_id)
    all_subscriptions.update(chat_id=None)


@transaction.atomic
def get_contests() -> List[int]:
    contests_list = [subscription.cid
                     for subscription in Subscription.objects.filter(~Q(chat_id=None))]
    return contests_list


@transaction.atomic
def get_submissions(cid: int) -> JsonList:
    unclosed_filter = Q(cid=cid) & ~Q(status='closed')
    unclosed_submissions = Submission.objects.filter(unclosed_filter)

    submissions_list = [{'submission_id': submission.pk,
                         'rid': submission.rid}
                        for submission in unclosed_submissions]

    return submissions_list
