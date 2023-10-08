from spreadsheetbot.spreadsheetbot import (
    SpreadSheetBot,
    HELP_COMMAND,
    REPORT_COMMAND,
    UPDATE_GROUP_USER_REQUEST,
    UPDATE_GROUP_GROUP_REQUEST,
    UPDATE_GROUP_CHAT_MEMBER
)

from spreadsheetbot.sheets.i18n import I18n
from spreadsheetbot.sheets.switch import Switch
from spreadsheetbot.sheets.settings import Settings
from spreadsheetbot.sheets.log import LogSheet
from spreadsheetbot.sheets.groups import Groups

from spreadsheetbot.basic.handlers import ErrorHandlerFun, ChatMemberHandlerFun

from spreadsheetbot.basic.log import Log
from logging import INFO, DEBUG
Log.setLevel(INFO)

from telegram import Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    Defaults
)

from ext.groups import (
    IsSuperGroupFilter,
    IsAdminGroupFilter,
    IsLetterGroupFilter,
    AdminNotifyStateFilter,
    LetterGroupCodeFoundFilter
)

from ext.codes import Codes

CANCEL_COMMAND = 'cancel'
NOTIFY_COMMAND = 'notify'

STATUS_ALPHA_COMMAND   = 'status_alpha'
STATUS_BETTA_COMMAND   = 'status_betta'
STATUS_GAMMA_COMMAND   = 'status_gamma'
STATUS_DELTA_COMMAND   = 'status_delta'
STATUS_EPSILON_COMMAND = 'status_epsilon'
STATUS_DZETTA_COMMAND  = 'status_dzetta'

class SpreadSheetBotExt(SpreadSheetBot):
    async def post_init(self, app: Application) -> None:
        Switch.set_sleep_time(self.switch_update_time)

        await I18n.async_init(self.sheets_secret, self.sheets_link)
        await LogSheet.async_init(self.sheets_secret, self.sheets_link)
        await Switch.async_init(self.sheets_secret, self.sheets_link)
        await Settings.async_init(self.sheets_secret, self.sheets_link)
        await Groups.async_init(self.sheets_secret, self.sheets_link)
        await Codes.async_init(self.sheets_secret, self.sheets_link)

        bot: Bot = app.bot
        await bot.set_my_commands([(HELP_COMMAND, Settings.help_command_description)])
        
        my_name = await bot.get_my_name()
        if my_name.name != Settings.my_name:
            await bot.set_my_name(Settings.my_name)
        
        my_short_description = await bot.get_my_short_description()
        if my_short_description.short_description  != Settings.my_short_description:
            await bot.set_my_short_description(Settings.my_short_description)
        
        my_description = await bot.get_my_description()
        if my_description.description  != Settings.my_description:
            await bot.set_my_description(Settings.my_description)

        await LogSheet.write(None, "Started an application")

        Switch.scheldue_update(app)

    def run_polling(self) -> None:
        Log.info("Starting...")
        app = ApplicationBuilder() \
            .token(self.bot_token) \
            .concurrent_updates(True) \
            .post_init(self.post_init) \
            .post_shutdown(self.post_shutdown) \
            .defaults(Defaults(disable_web_page_preview=True)) \
            .build()

        app.add_error_handler(ErrorHandlerFun)

        ##
        # Chat member handler
        ##
        app.add_handler(
            ChatMemberHandler(ChatMemberHandlerFun, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER, block=False),
            group=UPDATE_GROUP_CHAT_MEMBER
        )

        ##
        # Admin Group help handlers
        ##
        app.add_handlers([
            CommandHandler(HELP_COMMAND,   Groups.super_help_handler, filters=IsSuperGroupFilter, block=False),
            CommandHandler(HELP_COMMAND,   Groups.admin_help_handler, filters=IsAdminGroupFilter, block=False),
        ], group=UPDATE_GROUP_GROUP_REQUEST)

        ##
        # Admin Group notify and report handlers
        ##
        app.add_handlers([
            CommandHandler(CANCEL_COMMAND,         Groups.admin_cancel_handler,           filters=IsAdminGroupFilter, block=False),
            CommandHandler(NOTIFY_COMMAND,         Groups.admin_notify_set_state_handler, filters=IsAdminGroupFilter, block=False),
            MessageHandler(AdminNotifyStateFilter, Groups.admin_notify_proceed_handler,   block=False),
            CommandHandler(REPORT_COMMAND,         Groups.admin_report_handler,           filters=IsAdminGroupFilter, block=False),
        ], group=UPDATE_GROUP_GROUP_REQUEST)

        ##
        # Admin Group status handlers
        ##
        app.add_handlers([
            CommandHandler(STATUS_ALPHA_COMMAND,   Groups.admin_status_handler, filters=IsAdminGroupFilter, block=False),
            CommandHandler(STATUS_BETTA_COMMAND,   Groups.admin_status_handler, filters=IsAdminGroupFilter, block=False),
            CommandHandler(STATUS_GAMMA_COMMAND,   Groups.admin_status_handler, filters=IsAdminGroupFilter, block=False),
            CommandHandler(STATUS_DELTA_COMMAND,   Groups.admin_status_handler, filters=IsAdminGroupFilter, block=False),
            CommandHandler(STATUS_EPSILON_COMMAND, Groups.admin_status_handler, filters=IsAdminGroupFilter, block=False),
            CommandHandler(STATUS_DZETTA_COMMAND,  Groups.admin_status_handler, filters=IsAdminGroupFilter, block=False),

        ])

        ##
        # Normal Group handlers
        ##
        app.add_handlers([
            CommandHandler(HELP_COMMAND,               Groups.letter_help_handler,       filters=IsLetterGroupFilter, block=False),
            MessageHandler(LetterGroupCodeFoundFilter, Groups.letter_group_code_handler, block=False),
        ], group=UPDATE_GROUP_GROUP_REQUEST)

        app.run_polling()
        Log.info("Done. Goodby!")