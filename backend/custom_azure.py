from abc import ABC

from storages.backends.azure_storage import AzureStorage


class AzureStaticStorage(AzureStorage, ABC):
    account_name = 'djangotheorchidstorage'
    account_key = 'Pz42XCfcqOx3gIOa5UiE2FxpIL/O+U+K84tQzBZFhpGzByOOkYYuSZ6JohOZLGTZ3iI6wWcJOsv0M/Cm0u6v8Q=='
    azure_container = 'static'
    expiration_secs = None

