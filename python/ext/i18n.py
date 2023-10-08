from spreadsheetbot.sheets.i18n import I18nAdapterClass

async def _post_async_init(self: I18nAdapterClass) -> None:
    for _,row in self.as_df.iterrows():
        setattr(self, row.key, row.value)
    self.yes_no      = [self.yes, self.no]
    self.super_admin = [self.super, self.admin]
    self.letter_keys = [
        'alpha',   'betta',
        'gamma',   'delta',
        'epsilon', 'dzetta'
    ]
    self.letters = [
        self.alpha,   self.betta,
        self.gamma,   self.delta,
        self.epsilon, self.dzetta
    ]
    self.super_admin_letters = self.super_admin + self.letters
I18nAdapterClass._post_async_init = _post_async_init

def get(self: I18nAdapterClass, key: str) -> str:
    return self._get(self.as_df.key == key).value
I18nAdapterClass.get = get

def get_letter(self: I18nAdapterClass, key: str) -> str:
    return self.get(f"{key}_letter")
I18nAdapterClass.get_letter = get_letter

def get_key_by_value(self: I18nAdapterClass, value: str) -> str:
    return self._get(self.as_df.value == value).key
I18nAdapterClass.get_key_by_value = get_key_by_value

def get_letter_by_group_type(self: I18nAdapterClass, group_type: str) -> str:
    key = self.get_key_by_value(group_type)
    return self.get_letter(key)
I18nAdapterClass.get_letter_by_group_type = get_letter_by_group_type