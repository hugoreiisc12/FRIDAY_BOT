from Dependenciais.depend import WebDriverFactory


def test_webdriver_factory_has_method():
    assert hasattr(WebDriverFactory, 'create_driver')
    # Não executamos o driver por segurança em ambientes sem GUI
