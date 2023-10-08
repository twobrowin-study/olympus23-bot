import pandas as pd
from spreadsheetbot.sheets.abstract import AbstractSheetAdapter

from telegram import Message, Update, Chat
from telegram.ext import Application, ContextTypes

from spreadsheetbot.sheets.i18n import I18n
from spreadsheetbot.sheets.settings import Settings
from spreadsheetbot.sheets.report import Report

class CodesAdapterClass(AbstractSheetAdapter):
    def __init__(self) -> None:
        super().__init__('codes', 'codes', initialize_as_df=True)
        self.uid_col = 'key'
        self.wks_row_pad = 2
        self.found_colname = lambda group_name: f"found_{group_name}"
    
    async def _pre_async_init(self):
        self.sheet_name = I18n.codes
    
    async def _get_df(self) -> pd.DataFrame:
        df = pd.DataFrame(await self.wks.get_all_records())
        df = df.drop(index = 0, axis = 0)
        df = df.loc[
            (df.key != "") &
            (df.text_markdown != "") &
            (df.is_active == I18n.yes)
        ]
        df.key = df.key.apply(str)
        return df
    
    async def _post_async_init(self):
        self.code_keys = self.as_df.loc[
            self.as_df.key != I18n.last
        ].key.to_list()
        self.complete_number = len(self.code_keys)
        self.last = self.get(I18n.last)
    
    def get(self, key: str) -> pd.Series:
        return self._get(self.as_df.key == key)
    
    async def set_group_found_code(self, key: str, group_name: str) -> None:
        await self._update_record(key, self.found_colname(group_name), I18n.yes)
    
    def check_if_group_not_fond_code(self, key: str, group_name: str) -> bool:
        return self.as_df.loc[
            (self.as_df.key == key) &
            (self.as_df[self.found_colname(group_name)] == I18n.yes)
        ].empty
    
    def check_if_group_fond_code(self, key: str, group_name: str) -> bool:
        return not self.check_if_group_not_fond_code(key, group_name)
    
    def get_found_number(self, group_name: str) -> int:
        return self.as_df.loc[
            (self.as_df.key != I18n.last) &
            (self.as_df[self.found_colname(group_name)] == I18n.yes)
        ].shape[0]

Codes = CodesAdapterClass()
