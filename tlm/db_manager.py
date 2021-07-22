import functools
from typing import Callable
from datetime import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
from tlm.models import Submission
from tlm.models import JsonObj, JsonList
from tlm.config import resend_interval


def post_submissions(request_body: JsonList) -> None:
    for submission_data in request_body:
        submission, _ = Submission.objects.get_or_create(cid=submission_data['cid'],
                                                         login=submission_data['login'],
                                                         problem=submission_data['problem'])

        submission.rid = submission_data['rid']
        if submission.assignee is None:
            submission.status = 'unassigned'
        else:
            submission.status = 'assigned'
        submission.sent_to_chat = False

        submission.save()


def get_waiting() -> JsonList:
    waiting_filter = Q(sent_to_chat=False) & (Q(status='assigned') | Q(status='unassigned'))
    waiting = Submission.objects.filter(waiting_filter)

    submissions_list = [submission.submission_dict() for submission in waiting]

    return submissions_list


def get_to_delete() -> JsonList:
    delete_filter = Q(status='closed', sent_to_chat=True) | (
        Q(last_update_time__lt=datetime.now() - resend_interval) &
        (Q(status='unassigned') | Q(status='assigned'))
    )
    to_delete = Submission.objects.filter(delete_filter)

    submissions_list = [submission.tg_msg_dict() for submission in to_delete]

    return submissions_list


def submission_op(fn: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(fn)
    def ret(submission_id: int, *args, **kwargs) -> None:
        submission = get_object_or_404(Submission, pk=submission_id)
        fn(submission, *args, **kwargs)
        submission.save()
    return ret


@submission_op
def confirm_send(submission: Submission, request_body: JsonObj) -> None:
    submission.message_id = request_body['tg_msg']['message_id']
    submission.chat_id = request_body['tg_msg']['chat_id']
    submission.last_update_time = datetime.now()
    submission.sent_to_chat = True


@submission_op
def confirm_delete(submission: Submission) -> None:
    submission.sent_to_chat = False


@submission_op
def update_status(submission: Submission, status: str) -> None:
    submission.status = status


@submission_op
def update_assignee(submission: Submission, assignee: int) -> None:
    submission.assignee = assignee
