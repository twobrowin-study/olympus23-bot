import pandas as pd
from spreadsheetbot.sheets.switch import SwitchAdapterClass
from spreadsheetbot.sheets.i18n import I18n

async def _get_df(self: SwitchAdapterClass) -> pd.DataFrame:
    df = pd.DataFrame(await self.wks.get_all_records())
    df = df.drop(index = 0, axis = 0)
    df = df.loc[
        (df.bot_active.isin(I18n.yes_no))
    ]
    if df.empty:
        raise BaseException("Switch sheet is in bad condition")
    return df
SwitchAdapterClass._get_df = _get_df