
from src.application.application_factory import ApplicationFactory
from src.application.style_configurator import StyleConfigurator
from src.application.window_factory import WindowFactory


def run() -> int:

    app = ApplicationFactory.create()

    style_builder = StyleConfigurator().configure(app)

    WindowFactory.create_main_window(style_builder)

    return app.exec()