import json
from django.core.exceptions import BadRequest
from django.views.decorators.http import (require_GET,
                                          require_POST,
                                          require_http_methods)
from django.http import HttpRequest, HttpResponse, JsonResponse
from tlm import db_manager
from tlm.models import submission_fields, Json


def parse_request_body(request: HttpRequest) -> Json:
    try:
        body = json.loads(request.read())
    except json.JSONDecodeError as err:
        raise BadRequest() from err
    return body


@require_POST
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
def confirm_send(request: HttpRequest, submission_id: int) -> HttpResponse:
    body = parse_request_body(request)

    if (body.get('tg_msg') is None) or (not isinstance(body['tg_msg'], dict)):
        return HttpResponse(status=400)
    if (body['tg_msg'].get('chat_id') is None) or (not isinstance(body['tg_msg']['chat_id'], int)):
        return HttpResponse(status=400)
    if (body['tg_msg'].get('message_id') is None) or \
       (not isinstance(body['tg_msg']['message_id'], int)):
        return HttpResponse(status=400)

    db_manager.confirm_send(submission_id, body)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
def confirm_delete(_, submission_id: int) -> HttpResponse:
    db_manager.confirm_delete(submission_id)
    return HttpResponse(status=200)


@require_GET
def waiting(_) -> HttpResponse:
    return JsonResponse(db_manager.get_waiting(), status=200, safe=False)


@require_GET
def delete(_) -> HttpResponse:
    return JsonResponse(db_manager.get_to_delete(), status=200, safe=False)


@require_http_methods(['PUT'])
def update_status(request: HttpRequest, submission_id: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, str):
        return HttpResponse(status=400)

    db_manager.update_status(submission_id, body)
    return HttpResponse(status=200)


@require_http_methods(['PUT'])
def update_assignee(request: HttpRequest, submission_id: int) -> HttpResponse:
    body = parse_request_body(request)

    if not isinstance(body, int):
        return HttpResponse(status=400)

    db_manager.update_assignee(submission_id, body)
    return HttpResponse(status=200)
