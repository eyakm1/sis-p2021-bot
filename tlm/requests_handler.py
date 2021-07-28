import functools
import json
from typing import Callable
from django.core.exceptions import BadRequest
from django.views.decorators.http import (require_GET,
                                          require_POST,
                                          require_http_methods)
from django.http import HttpRequest, HttpResponse, JsonResponse
from tlm import db_manager
from tlm.models import submission_fields, Json


def handle_bad_request_message(fn: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(fn)
    def ret(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            response = fn(request, *args, **kwargs)
        except BadRequest as err:
            return HttpResponse(status=400, content_type='text/plain', content=str(err))
        return response
    return ret


def parse_request_body(request: HttpRequest) -> Json:
    try:
        body = json.loads(request.read())
    except json.JSONDecodeError as err:
        raise BadRequest('Error parsing request body') from err
    return body


@require_POST
@handle_bad_request_message
def add_submissions(request: HttpRequest) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, list):
        return HttpResponse(status=400)

    request_body = list()
    for submission in body:
        try:
            request_body.append({k: typ(submission.get(k))
                                 for k, typ in submission_fields.items()})
        except ValueError:
            return HttpResponse(status=400)

    db_manager.post_submissions(request_body)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
@handle_bad_request_message
def confirm_send(request: HttpRequest, submission_id: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body.get('tg_msg'), dict):
        return HttpResponse(status=400)
    if not isinstance(body['tg_msg'].get('chat_id'), int):
        return HttpResponse(status=400)
    if not isinstance(body['tg_msg'].get('message_id'), int):
        return HttpResponse(status=400)
    if not isinstance(body.get('rid'), int):
        return HttpResponse(status=400)

    db_manager.confirm_send(submission_id, body)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
@handle_bad_request_message
def confirm_delete(_, submission_id: int) -> HttpResponse:
    db_manager.confirm_delete(submission_id)
    return HttpResponse(status=200)


@require_GET
@handle_bad_request_message
def waiting(_) -> HttpResponse:
    return JsonResponse(db_manager.get_waiting(), status=200, safe=False)


@require_GET
@handle_bad_request_message
def delete(_) -> HttpResponse:
    return JsonResponse(db_manager.get_to_delete(), status=200, safe=False)


@require_http_methods(['PUT'])
@handle_bad_request_message
def update_status(request: HttpRequest, submission_id: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, str):
        return HttpResponse(status=400)

    db_manager.update_status(submission_id, body)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
@handle_bad_request_message
def update_assignee(request: HttpRequest, submission_id: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, int):
        return HttpResponse(status=400)

    db_manager.update_assignee(submission_id, body)
    return HttpResponse(status=200)


@require_POST
def snooze(request: HttpRequest, submission_id: int) -> HttpResponse:
    db_manager.snooze(submission_id)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
@handle_bad_request_message
def subscribe_contest(request: HttpRequest, cid: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, int):
        return HttpResponse(status=400)

    db_manager.subscribe(cid, body)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
@handle_bad_request_message
def unsubscribe_contest(request: HttpRequest, cid: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, int):
        return HttpResponse(status=400)

    db_manager.unsubscribe(cid, body)
    return HttpResponse(status=200)


@require_POST
@handle_bad_request_message
def unsubscribe_all(request: HttpRequest) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, int):
        return HttpResponse(status=400)

    db_manager.unsubscribe_all(body)
    return HttpResponse(status=200)


@require_GET
@handle_bad_request_message
def contests(_) -> HttpResponse:
    return JsonResponse(db_manager.get_contests(), status=200, safe=False)
