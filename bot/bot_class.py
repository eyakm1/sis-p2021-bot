import asyncio
import json
import logging
from typing import Any, Tuple, Optional, Union

import aiohttp
from aiogram import Bot, Dispatcher

from bot import config, messaging
from bot.logger import get_logger
from bot.submission import Submission
import bot.utils as utils


class TelegramBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tcp_connector = aiohttp.TCPConnector(ssl_context=utils.get_ssl_context())
        self._session = aiohttp.ClientSession(connector=self._tcp_connector,
                                              timeout=kwargs["timeout"])
        self._logger = get_logger("bot_class")

    async def process_waiting(self) -> bool:
        success, waiting_list = \
            await self.api_request("get", f"{config.API_URL}/waiting",
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
            self._logger.info("Processing new submission %d...",
                              submission.id)
            chat_id = to_send["chat_id"]
            message_id = await self.process_submission(submission, chat_id)

            if message_id:
                await self.confirm_send(submission.id, submission.rid, chat_id, message_id)
            else:
                self._logger.warning("Sending submission %d failed",
                                     submission.id)
                return False
        return True

    async def delete_messages(self) -> bool:
        success, to_delete_list = await self.api_request("get",
                                                         f"{config.API_URL}/to_delete",
                                                         error_msg="Cannot get API "
                                                                   "/to_delete. Error: %s")
        if not success:
            return False
        for to_delete_msg in to_delete_list:
            success = await messaging.delete_message(self, to_delete_msg["tg_msg"]["chat_id"],
                                                     to_delete_msg["tg_msg"]["message_id"])
            if success:
                await self.confirm_delete(to_delete_msg["id"])
                self._logger.debug("Message %d was "
                                   "deleted from chat %d",
                                   to_delete_msg["tg_msg"]["message_id"],
                                   to_delete_msg["tg_msg"]["chat_id"])
            else:
                self._logger.warning("Message %d "
                                     "was NOT deleted from chat %d",
                                     to_delete_msg["tg_msg"]["message_id"],
                                     to_delete_msg["tg_msg"]["chat_id"])
                success = False
        return success

    async def confirm_send(self, submission_id: int, rid: int, chat_id: int, message_id: int) \
            -> bool:
        data = {
            "rid": rid,
            "tg_msg": {
                "chat_id": chat_id,
                "message_id": message_id
            }
        }
        success, _ = await self.api_request(
            "put",
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

    async def confirm_delete(self, submission_id: int) -> bool:
        success, _ = await self \
            .api_request("put",
                         f"{config.API_URL}/submissions/{submission_id}/confirm/delete",
                         success_msg=f"Submission {submission_id} successfully deleted",
                         error_msg=f"Confirming deleting submission {submission_id} failed! "
                                   f"Error: %s")
        return success

    async def subscribe(self, cid: int, chat_id: int) -> Tuple[bool, str]:
        done, data = await self.api_request("put",
                                            f"{config.API_URL}/contests/{cid}/subscribe",
                                            data=chat_id,
                                            success_msg=f"Successfully "
                                                        f"subscribed {chat_id} on {cid}",
                                            error_msg=f"Chat {chat_id} subscription "
                                                      f"on contest {cid} failed. Error: %s")
        return done, data

    async def unsubscribe(self, cid: int, chat_id: int) -> Tuple[bool, str]:
        done, data = await self.api_request("put",
                                            f"{config.API_URL}/contests/{cid}/unsubscribe",
                                            data=chat_id,
                                            success_msg=f"Chat {chat_id} unsubscribed from "
                                                        f"contest {cid}",
                                            error_msg=f"Could not unsubscribe {chat_id}"
                                                      f"from contest {cid}. Error: %s")
        return done, data

    async def unsubscribe_all(self, chat_id: int) -> Tuple[bool, str]:
        done, data = await self.api_request("post",
                                            f"{config.API_URL}/contests/all/unsubscribe",
                                            data=chat_id,
                                            success_msg=f"Chat {chat_id} unsubscribed from "
                                                        f"all contests",
                                            error_msg=f"Could not unsubscribe {chat_id}"
                                                      f"from all contests. Error: %s")
        return done, data

    async def process_group_submission(self, submission: Submission, chat_id: int) \
            -> Optional[int]:
        self._logger.debug("Submission %d should "
                           "be sent to channel %d",
                           submission.id, chat_id)
        message_id = await messaging.send_to_channel(self, submission, chat_id)
        return message_id

    # pylint: disable=too-many-arguments
    async def api_request(self, request_method: str, url: str, data: Union[dict, str, int] = None,
                          success_msg: str = None,
                          error_msg: str = "") -> Tuple[bool, Any]:
        """
            TLM API call
            :param request_method: http request method
            :param url: request url
            :param data: arguments for api call
            :param success_msg: logger message for successful call
            :param error_msg: logger message for unsuccessful call
            :returns:
                success - success of api call
                data - requested json in case of successful call,
                error message string or None otherwise
            """
        try:
            async with self._session.request(request_method, url, json=data) as result:
                if result.status == 200:
                    if success_msg:
                        self._logger.debug(success_msg)
                    if result.content_length:
                        return True, await result.json()
                    return True, None
                self._logger.warning(error_msg, "status code:" + str(result.status))
                return False, await result.text()
        except aiohttp.ClientConnectorError as error:
            if error_msg:
                self._logger.warning(error_msg, str(error))
                return False, None
        except json.decoder.JSONDecodeError as error:
            self._logger.error("Error while parsing API response "
                               "to json. %s", str(error))
            return False, None
        except asyncio.TimeoutError as error:
            logging.exception(error)
            return False, None


session_timeout = aiohttp.ClientTimeout(total=config.TIMEOUT_INTERVAL_SECONDS)
bot_instance = TelegramBot(token=config.BOT_TOKEN, timeout=session_timeout)
dp = Dispatcher(bot_instance)
