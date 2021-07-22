import json
from typing import Optional
import requests
import telebot
from common.models.models import Contest
import config
from logger import get_logger
import messaging
from submission import Submission

bot_class_logger = get_logger("bot_class")


class Bot(telebot.TeleBot):
    def process_waiting(self):
        waiting_list = self.api_request(requests.get, f"{config.API_URL}/waiting",
                                        error_msg="Cannot get API /waiting. Error: %s")
        if not waiting_list:
            return
        for to_send in waiting_list:
            submission = Submission(
                id=to_send["id"],
                cid=to_send["cid"],
                rid=to_send["rid"],
                login=to_send["login"],
                problem=to_send["problem"]
            )
            assignee = to_send["assignee"]
            bot_class_logger.info("Processing new submission %d...",
                                  submission.id)
            if assignee:
                chat_id, message_id = self.process_private_submission(submission, assignee)
            else:
                chat_id, message_id = self.process_group_submission(submission)

            if message_id:
                self.confirm_send(submission.id, chat_id, message_id)
            else:
                bot_class_logger.warning("Sending submission %d failed",
                                         submission.id)

    def delete_messages(self):
        to_delete_list = self.api_request(requests.get,
                                          f"{config.API_URL}/to_delete",
                                          error_msg="Cannot get API /to_delete. Error: %s")
        if not to_delete_list:
            return
        for to_delete_msg in to_delete_list:
            was_deleted = messaging.delete_message(self, to_delete_msg["tg_msg"]["message_id"],
                                                   to_delete_msg["tg_msg"]["chat_id"])
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

    @staticmethod
    def change_status(submission_id: id, status: str, assignee: int) -> bool:
        if not bot.api_request(requests.put, f"{config.API_URL}/submissions/{submission_id}/status",
                               data=status,
                               success_msg=f"Status of submission {submission_id} "
                                           f"changed to {status}",
                               error_msg=f"Updating submission {submission_id} status to "
                                         f"{status} failed. Error: %s"):
            return False
        if status == "assigned":
            return bot.api_request(requests.put,
                                   f"{config.API_URL}/submissions/{submission_id}/assignee",
                                   data=str(assignee),
                                   success_msg=f"Updated submission {submission_id} "
                                               f"assignee {assignee}",
                                   error_msg=f"Updating submission {submission_id} assignee "
                                             f"{assignee} failed. Error: %s") \
                   is not None
        return True

    @staticmethod
    def confirm_send(submission_id: int, chat_id: int, message_id: int):
        data = {
            "tg_msg": {
                "chat_id": chat_id,
                "message_id": message_id
            }
        }
        bot.api_request(requests.post, f"{config.API_URL}/submissions/{submission_id}/confirm/send",
                        data=data,
                        success_msg=f"Submission {submission_id} successfully sent to "
                                    f"{chat_id} and confirmed. msg_id: {message_id}",
                        error_msg=f"Confirming sending submission {submission_id} to "
                                  f"{chat_id} failed! Error: %s")

    @staticmethod
    def confirm_delete(submission_id: int):
        bot.api_request(requests.post,
                        f"{config.API_URL}/submissions/{submission_id}/confirm/delete",
                        success_msg=f"Submission {submission_id} successfully deleted",
                        error_msg=f"Confirming deleting submission {submission_id} failed! "
                                  f"Error: %s")

    def process_group_submission(self, submission: Submission) -> (Optional[int], Optional[int]):
        contest = Contest.objects.filter(cid=submission.cid).first()
        if contest:
            chat_id = contest.chat_id
            bot_class_logger.debug("Submission %d should "
                                   "be sent to group %d",
                                   submission.id, chat_id)
            message_id = messaging.send_to_group(self, submission, chat_id)
            return chat_id, message_id
        bot_class_logger.warning("Submission %d error: Contest was not "
                                 "registered in chat", submission.id)
        return None, None

    def process_private_submission(self, submission: Submission, assignee: int) -> (int, int):
        chat_id = assignee
        bot_class_logger.debug("Submission %d should be "
                               "sent to assignee %d", submission.id,
                               chat_id)
        message_id = messaging.send_assigned(self, submission, chat_id)
        return chat_id, message_id

    @staticmethod
    def api_request(request_method, url: str, data: [dict, str] = None,
                    success_msg: str = None,
                    error_msg: str = None):
        try:
            result = request_method(url, data=data)
            if result.status_code == 200:
                if success_msg:
                    bot_class_logger.debug(success_msg)
                return result.json()

            bot_class_logger.warning(error_msg, "status code:" + str(result.status_code))
            return None
        except requests.RequestException as error:
            if error_msg:
                bot_class_logger.warning(error_msg, str(error))
            return None
        except json.decoder.JSONDecodeError as error:
            bot_class_logger.error("Error while parsing API response "
                                   "to json. %s", str(error))
            return None


bot = Bot(token=config.BOT_TOKEN)
