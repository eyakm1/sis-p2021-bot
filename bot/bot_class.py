import json
from typing import Any, Tuple, Optional

import requests
import telebot

from bot import config, messaging
from bot.logger import get_logger
from bot.submission import Submission

bot_class_logger = get_logger("bot_class")
telebot.apihelper.READ_TIMEOUT = 10


class Bot(telebot.TeleBot):
    def process_waiting(self) -> bool:
        waiting_list, success = self.api_request(requests.get, f"{config.API_URL}/waiting",
                                                 error_msg="Cannot get API /waiting. Error: %s")
        if not success:
            return False
        for to_send in waiting_list:
            submission = Submission(
                id=to_send["id"],
                cid=to_send["cid"],
                rid=to_send["rid"],
                login=to_send["login"],
                problem=to_send["problem"],
                link=to_send["link"]
            )
            bot_class_logger.info("Processing new submission %d...",
                                  submission.id)
            chat_id = to_send["chat_id"]
            if to_send['status'] == 'assigned':
                message_id = self.process_private_submission(submission, chat_id)
            else:
                message_id = self.process_group_submission(submission, chat_id)

            if message_id:
                self.confirm_send(submission.id, submission.rid, chat_id, message_id)
            else:
                success = False
                bot_class_logger.warning("Sending submission %d failed",
                                         submission.id)
        return success

    def delete_messages(self) -> bool:
        to_delete_list, success = self.api_request(requests.get,
                                                  f"{config.API_URL}/to_delete",
                                                  error_msg="Cannot get API /to_delete. Error: %s")
        if not success:
            return False
        for to_delete_msg in to_delete_list:
            was_deleted = messaging.delete_message(self, to_delete_msg["tg_msg"]["chat_id"],
                                                   to_delete_msg["tg_msg"]["message_id"])
            if was_deleted:
                self.confirm_delete(to_delete_msg["id"])
                bot_class_logger.debug("Message %d was "
                                       "deleted from chat %d",
                                       to_delete_msg["tg_msg"]["message_id"],
                                       to_delete_msg["tg_msg"]["chat_id"])
            else:
                bot_class_logger.warning("Message %d "
                                         "was NOT deleted from chat %d",
                                         to_delete_msg["tg_msg"]["message_id"],
                                         to_delete_msg["tg_msg"]["chat_id"])
                success = False
        return success

    def change_assignee(self, submission_id: int, assignee: int) -> bool:
        _, success = self \
            .api_request(requests.put,
                         f"{config.API_URL}/submissions/{submission_id}/assignee",
                         data=assignee,
                         success_msg=f"Updated submission {submission_id} "
                                     f"assignee {assignee}",
                         error_msg=f"Updating submission {submission_id} assignee "
                                   f"{assignee} failed. Error: %s")
        return success

    def change_status(self, submission_id: id, status: str) -> bool:
        _, success = self \
            .api_request(requests.put,
                         f"{config.API_URL}/submissions/{submission_id}/status",
                         data=status,
                         success_msg=f"Status of submission {submission_id} "
                                     f"changed to {status}",
                         error_msg=f"Updating submission {submission_id} status to "
                                   f"{status} failed. Error: %s")
        return success

    def confirm_send(self, submission_id: int, rid: int, chat_id: int, message_id: int) -> bool:
        data = {
            "rid": rid,
            "tg_msg": {
                "chat_id": chat_id,
                "message_id": message_id
            }
        }
        _, success = self.api_request(
            requests.put,
            f"{config.API_URL}/submissions/{submission_id}/confirm/send",
            data=data,
            success_msg=f"Submission {submission_id} (rid: {rid}) "
                        f"successfully sent to {chat_id} and confirmed. "
                        f"msg_id: {message_id}",
            error_msg=f"Confirming sending submission "
                      f"{submission_id} (rid: {rid}) "
                      f"to {chat_id} failed! Error: %s"
        )
        return success

    def confirm_delete(self, submission_id: int) -> bool:
        _, success = self.api_request(
            requests.put,
            f"{config.API_URL}/submissions/{submission_id}/confirm/delete",
            success_msg=f"Submission {submission_id} successfully deleted",
            error_msg=f"Confirming deleting submission "
                      f"{submission_id} failed! "
                      f"Error: %s"
        )
        return success

    def snooze(self, submission_id: int) -> bool:
        _, success = self.api_request(
            requests.post,
            f"{config.API_URL}/submissions/{submission_id}/snooze",
            success_msg=f"Submission {submission_id} snoozed",
            error_msg=f"Snoozing submission {submission_id} failed! "
            f"Error: %s"
        )
        return success

    def subscribe(self, cid: int, chat_id: int) -> bool:
        _, success = self.api_request(requests.put,
                                      f"{config.API_URL}/contests/{cid}/subscribe",
                                      data=chat_id,
                                      success_msg=f"Successfully "
                                      f"subscribed {chat_id} on {cid}",
                                      error_msg=f"Chat {chat_id} subscription "
                                                f"on contest {cid} failed")
        return success

    def unsubscribe(self, cid: int, chat_id: int) -> bool:
        _, success = self.api_request(requests.put,
                                      f"{config.API_URL}/contests/{cid}/unsubscribe",
                                      data=chat_id,
                                      success_msg=f"Chat {chat_id} unsubscribed from "
                                                  f"contest {cid}",
                                      error_msg=f"Could not unsubscribe {chat_id}"
                                                f"from contest {cid}")
        return success

    def unsubscribe_all(self, chat_id: int) -> bool:
        _, success = self.api_request(requests.post,
                                      f"{config.API_URL}/contests/all/unsubscribe",
                                      data=chat_id,
                                      success_msg=f"Chat {chat_id} unsubscribed from "
                                                  f"all contests",
                                      error_msg=f"Could not unsubscribe {chat_id}"
                                                f"from all contests")
        return success

    def process_group_submission(self, submission: Submission, chat_id: int) -> Optional[int]:
        bot_class_logger.debug("Submission %d should "
                               "be sent to group %d",
                               submission.id, chat_id)
        message_id = messaging.send_to_group(self, submission, chat_id)
        return message_id

    def process_private_submission(self, submission: Submission, chat_id: int) -> Optional[int]:
        bot_class_logger.debug("Submission %d should be "
                               "sent to assignee %d", submission.id,
                               chat_id)
        message_id = messaging.send_assigned(self, submission, chat_id)
        return message_id

    @staticmethod
    def api_request(request_method, url: str, data: [dict, str, int] = None,
                    success_msg: str = None,
                    error_msg: str = None) -> Tuple[Any, bool]:
        try:
            result = request_method(url, json=data, cert=config.CERT)
            if result.status_code == 200:
                if success_msg:
                    bot_class_logger.debug(success_msg)
                if result.content:
                    return result.json(), True
                return None, True

            bot_class_logger.warning(error_msg, "status code:" + str(result.status_code))
            return result.content, False
        except requests.RequestException as error:
            if error_msg:
                bot_class_logger.warning(error_msg, str(error))
            return None, False
        except json.decoder.JSONDecodeError as error:
            bot_class_logger.error("Error while parsing API response "
                                   "to json. %s", str(error))
            return None, False


bot_instance = Bot(token=config.BOT_TOKEN)
