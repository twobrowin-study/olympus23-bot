from spreadsheetbot.sheets.groups import GroupsAdapterClass, Groups
import pandas as pd

from spreadsheetbot.sheets.abstract import AbstractSheetAdapter

from spreadsheetbot.sheets.i18n import I18n
from spreadsheetbot.sheets.settings import Settings

from telegram import Update, Message
from telegram.ext import Application, ContextTypes
from telegram.constants import ParseMode, MessageEntityType

from ext.codes import Codes

#
# Init
#
async def _get_df(self: GroupsAdapterClass) -> pd.DataFrame:
    df = pd.DataFrame(await self.wks.get_all_records())
    df = df.drop(index = 0, axis = 0)
    df = df.loc[
        (df.chat_id != "") &
        (df.type.isin(I18n.super_admin_letters)) &
        (df.is_active == I18n.yes)
    ]
    df.chat_id = df.chat_id.apply(str)
    return df
GroupsAdapterClass._get_df = _get_df

async def _pre_async_init(self: GroupsAdapterClass):
    self.sheet_name = I18n.groups
    self.wks_row_pad = 2
GroupsAdapterClass._pre_async_init = _pre_async_init

async def _post_async_init(self: GroupsAdapterClass):
    self.letter_chats_chat_ids = self.as_df.loc[self.as_df.type.isin(I18n.letters)].chat_id.to_list()
GroupsAdapterClass._post_async_init = _post_async_init

#
# Senders
#
def send_to_all_letter_groups(self: GroupsAdapterClass, app: Application, message: str, parse_mode: str, send_photo: str = None):
    self._send_to_all_uids(
        self.as_df.type.isin(I18n.letters),
        app, message, parse_mode, send_photo
    )
GroupsAdapterClass.send_to_all_normal_groups = send_to_all_letter_groups
GroupsAdapterClass.send_to_all_letter_groups = send_to_all_letter_groups

def send_to_all_admin_groups(self: GroupsAdapterClass, app: Application, message: str, parse_mode: str, send_photo: str = None):
    self._send_to_all_uids(
        self.as_df.type == I18n.admin,
        app, message, parse_mode, send_photo
    )
GroupsAdapterClass.send_to_all_admin_groups = send_to_all_admin_groups

async def async_send_to_all_admin_groups(self: GroupsAdapterClass, app: Application, message: str, parse_mode: str, send_photo: str = None):
    for send_message_continue in self._get_send_to_all_uids_coroutines(
        self.as_df.type == I18n.admin,
        app, message, parse_mode, send_photo
    ):
        await send_message_continue
GroupsAdapterClass.async_send_to_all_admin_groups = async_send_to_all_admin_groups

def send_to_all_superadmin_groups(self: GroupsAdapterClass, app: Application, message: str, parse_mode: str, send_photo: str = None):
    self._send_to_all_uids(
        self.as_df.type == I18n.super,
        app, message, parse_mode, send_photo
    )
GroupsAdapterClass.send_to_all_superadmin_groups = send_to_all_superadmin_groups

async def async_send_to_all_superadmin_groups(self: GroupsAdapterClass, app: Application, message: str, parse_mode: str, send_photo: str = None):
    for send_message_continue in self._get_send_to_all_uids_coroutines(
        self.as_df.type == I18n.super,
        app, message, parse_mode, send_photo
    ):
        await send_message_continue
GroupsAdapterClass.async_send_to_all_superadmin_groups = async_send_to_all_superadmin_groups

#
# Filters
#
class IsSuperGroupClass(AbstractSheetAdapter.AbstractFilter):
    def filter(self, message: Message) -> bool:
        df = self.outer_obj.as_df
        return not df.loc[
            self.outer_obj.selector(message.chat_id) &
            (df.type == I18n.super)
        ].empty
IsSuperGroupFilter = Groups.GroupChatFilter & IsSuperGroupClass(outer_obj=Groups)

class IsAdminGroupClass(AbstractSheetAdapter.AbstractFilter):
    def filter(self, message: Message) -> bool:
        df = self.outer_obj.as_df
        return not df.loc[
            self.outer_obj.selector(message.chat_id) &
            (df.type == I18n.admin)
        ].empty
IsAdminGroupFilter = Groups.GroupChatFilter & IsAdminGroupClass(outer_obj=Groups)

class IsLetterGroupClass(AbstractSheetAdapter.AbstractFilter):
    def filter(self, message: Message) -> bool:
        df = self.outer_obj.as_df
        return not df.loc[
            self.outer_obj.selector(message.chat_id) &
            (df.type.isin(I18n.letters))
        ].empty
IsLetterGroupFilter = Groups.GroupChatFilter & IsLetterGroupClass(outer_obj=Groups)

class AdminNotifyStateClass(AbstractSheetAdapter.AbstractFilter):
    def filter(self, message: Message) -> bool:
        df = self.outer_obj.as_df
        return not df.loc[
            self.outer_obj.selector(message.chat_id) &
            (df.type == I18n.admin) &
            (df.state == I18n.notify)
        ].empty
AdminNotifyStateFilter = IsAdminGroupFilter & AdminNotifyStateClass(outer_obj=Groups)

class LetterGroupCodeFoundClass(AbstractSheetAdapter.AbstractFilter):
    def filter(self, message: Message) -> bool:
        df = Codes.as_df
        group = self.outer_obj._get(self.outer_obj.selector(message.chat_id))
        group_name = I18n.get_key_by_value(group.type)
        key = message.text
        return Codes.check_if_group_not_fond_code(key, group_name) and key in Codes.code_keys
LetterGroupCodeFoundFilter = IsLetterGroupFilter & LetterGroupCodeFoundClass(outer_obj=Groups)

#
# Handlers
#
async def super_help_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Settings.help_super_group)
GroupsAdapterClass.super_help_handler = super_help_handler

async def admin_help_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Settings.help_admin_group)
GroupsAdapterClass.admin_help_handler = admin_help_handler

async def letter_help_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group = self._get(self.selector(update.effective_chat.id))
    group_title:  str = group.type
    group_letter: str = I18n.get_letter_by_group_type(group.type)
    await update.message.reply_markdown(Settings.help_letter_group.format(
        group_title = group_title,
        group_letter = group_letter,
    ))
GroupsAdapterClass.letter_help_handler = letter_help_handler

async def admin_cancel_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Settings.cancel_admin_message)
    await self._update_record(update.effective_chat.id, 'state', '')
GroupsAdapterClass.admin_cancel_handler = admin_cancel_handler

async def admin_notify_set_state_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Settings.notify_admin_start_message)
    await self._update_record(update.effective_chat.id, 'state', I18n.notify)
GroupsAdapterClass.admin_notify_set_state_handler = admin_notify_set_state_handler

async def admin_notify_proceed_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id in self.letter_chats_chat_ids:
        await update.message.copy(chat_id)
    await update.message.reply_markdown(Settings.notify_admin_done_message)
    await self._update_record(update.effective_chat.id, 'state', '')
GroupsAdapterClass.admin_notify_proceed_handler = admin_notify_proceed_handler

async def react_to_code(self: GroupsAdapterClass, code: pd.Series,
                        group_title: str, group_letter: str, group_name: str,
                        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_markdown(code.text_markdown)
    await Codes.set_group_found_code(code.key, group_name)

    admin_message = Settings.admin_group_code_found_template.format(
        group_title = group_title,
        group_letter = group_letter,
        code_key = code.key
    )
    await self.async_send_to_all_admin_groups(context.application, admin_message, ParseMode.MARKDOWN)
GroupsAdapterClass.react_to_code = react_to_code

async def letter_group_code_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code = Codes.get(update.message.text)
    
    group = self._get(self.selector(update.effective_chat.id))
    group_title:  str = group.type
    group_letter: str = I18n.get_letter_by_group_type(group.type)
    group_name:   str = I18n.get_key_by_value(group.type)

    await self.react_to_code(code, group_title, group_letter, group_name, update, context)

    found_number = Codes.get_found_number(group_name)
    await update.message.reply_markdown(
        Settings.found_codes_template.format(
            found_number = found_number,
            complete_number = Codes.complete_number
        )
    )

    if found_number == Codes.complete_number:
        await self.react_to_code(Codes.last, group_title, group_letter, group_name, update, context)
GroupsAdapterClass.letter_group_code_handler = letter_group_code_handler

async def admin_report_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    found_codes_list = "\n".join([
        Settings.found_codes_list_template.format(
            group_title  = I18n.get(group_name),
            group_letter = I18n.get_letter(group_name),
            found_number = Codes.get_found_number(group_name)
        )
        for group_name in I18n.letter_keys
    ])
    await update.message.reply_markdown(Settings.report_template.format(found_codes_list=found_codes_list))
GroupsAdapterClass.admin_report_handler = admin_report_handler

async def admin_status_handler(self: GroupsAdapterClass, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for entity in update.message.entities:
        if entity.type == MessageEntityType.BOT_COMMAND:
            group_name = update.message.parse_entity(entity)[1:].split('@')[0].removeprefix('status_')
    
    codes_status_list = "\n".join([
        Settings.codes_status_template.format(
            key = key,
            status = I18n.found if Codes.check_if_group_fond_code(key, group_name) else I18n.not_found
        )
        for key in Codes.code_keys
    ])
    await update.message.reply_markdown(
        Settings.status_template.format(
            group_title       = I18n.get(group_name),
            group_letter      = I18n.get_letter(group_name),
            codes_status_list = codes_status_list
        )
    )
GroupsAdapterClass.admin_status_handler = admin_status_handler