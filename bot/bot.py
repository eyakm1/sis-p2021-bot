import config
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class Bot:

    def __init__(self):
        self.bot = telebot.TeleBot(config.bot_token)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            self.bot.send_message(call.message.chat.id, 'info')

        @self.bot.message_handler(commands=['get_list'])
        def message_handler(message):
            args = message.text.strip().split()
            item_cnt = 3
            if len(args) > 1:
                item_cnt = int(args[-1])

            self.bot.send_message(message.chat.id,
                                  'variants:',
                                  reply_markup=self.gen_markup(item_cnt))

        @self.bot.message_handler()
        def just_text(message):
            self.bot.reply_to(message, 'не понимаю Вас')

    @staticmethod
    def gen_markup(n):
        markup = InlineKeyboardMarkup()
        for i in range(n):
            markup.add(InlineKeyboardButton(i, callback_data=str(i)))
        return markup

    def run(self):
        self.bot.infinity_polling()


if __name__ == '__main__':
    my_bot = Bot()
    my_bot.run()
