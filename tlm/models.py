from typing import Dict, Any, List, TypeVar
from django.db import models

# pylint: disable=W0511
# TODO: place JsonObj, JsonList, Json somewhere else
JsonObj = Dict[str, Any]
JsonList = List[JsonObj]
Json = TypeVar('Json', JsonList, JsonObj)

submission_fields = {'cid': int,
                     'rid': int,
                     'login': str,
                     'problem': str,
                     'link': str}


class Subscription(models.Model):
    cid = models.BigIntegerField(null=False, primary_key=True, unique=True)
    chat_id = models.BigIntegerField(null=True)


class Submission(models.Model):
    cid = models.BigIntegerField(null=False)
    rid = models.BigIntegerField(null=False)
    login = models.CharField(max_length=255, null=False)
    problem = models.CharField(max_length=255, null=False)

    judge_link = models.CharField(max_length=255, null=False)
    status = models.CharField(max_length=20, default='unassigned')
    target_chat_id = models.BigIntegerField(null=True)
    chat_rid = models.BigIntegerField(null=True)
    chat_id = models.BigIntegerField(null=True)
    message_id = models.BigIntegerField(null=True)

    last_update_time = models.DateTimeField(null=True)
    sent_to_chat = models.BooleanField(default=False)
    last_snooze_time = models.DateTimeField(null=True)

    def submission_dict(self) -> JsonObj:
        res = {'id': self.pk,
               'cid': self.cid,
               'rid': self.rid,
               'login': self.login,
               'problem': self.problem,
               'chat_id': self.target_chat_id,
               'status': self.status,
               'link': self.judge_link}
        return res

    def tg_msg_dict(self) -> JsonObj:
        res = {'id': self.pk,
               'tg_msg': {
                   'chat_id': self.chat_id,
                   'message_id': self.message_id
               }}
        return res

    class Meta:
        unique_together = ('cid', 'login', 'problem')
