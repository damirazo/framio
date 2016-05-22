# coding: utf-8
from flask import Flask
from functools import partial
from framio.settings import DEFAULT_SETTINGS

__author__ = 'damirazo <me@damirazo.ru>'


def lazy_method(method):
    """
    Декоратор для реализации "ленивого" метода,
    логика которого будет вызвана после инициализации приложения

    :param method: Обертываемый метод
    """
    def wrapper(self, *args, **kwargs):
        if self._app is None:
            self._app_logic_queue.append(
                partial(method, self, *args, **kwargs))
        else:
            method(self, *args, **kwargs)

    return wrapper


class Controller(object):
    """
    Базовый класс контроллера приложения
    """
    _app = None
    """:type : Flask"""
    _app_logic_queue = []
    """:type : list"""

    _actions = {}
    """:type : dict"""

    _harvested = False
    """:type : bool"""
    
    def __new__(cls):
        """
        Логика реализации паттерна синглтон
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(Controller, cls).__new__(cls)

        return cls._instance

    @property
    def app(self):
        """
        Свойство для read only доступа к экземпляру приложения

        :rtype : Flask
        """
        return self._app

    @app.setter
    def app(self, app_instance):
        """
        Установка значения экземпляра приложения
        Значение будет установлено лишь единожды, без возможности перезаписи

        :param app_instance: Экземпляр приложения Flask
        :type app_instance: Flask
        """
        if self._app is None:
            self._app = app_instance

    @property
    def cfg(self):
        """
        Доступ к настройкам приложения

        :rtype : dict
        """
        return self.app.config

    def register_actions(self, actions):
        """
        Регистрация действий

        :param actions: Список регистрируемых действий
        :type actions: list
        """

        def _recursive_register(a):
            """
            Рекурсивная сборка дочерних действий

            :param a: Обрабатываемое действие
            :type a: framio.action.Action
            """
            url = a.full_url
            cls_name = lambda x: x.__class__.__name__

            if not url:
                raise RuntimeError((
                    'Для действия {} не задано значение атрибута url'
                ).format(cls_name(a)))

            if url in self._actions:
                raise ValueError((
                    'URL "{}" уже использовался для действия {}'
                ).format(url, cls_name(self._actions[url])))

            self._actions[url] = a

            params = {'rule': url}
            """:type : dict[str, object]"""
            if a.available_methods:
                params.update({'methods': a.available_methods})

            view = a.handler_wrapper
            view.__func__.__name__ = (
                '_{}_handler'.format(cls_name(a)))

            # Регистрируем маршрут
            self.app.route(**params)(view)

            # Проставляем ссылку на контроллер
            a.controller = self

            for child_action in a.children:
                _recursive_register(child_action)

        for action in actions:
            _recursive_register(action)

    @lazy_method
    def register_error_handler(self, action, http_code):
        """
        Регистрация действия для обработки ошибок

        :param action: Действие, получающее управление
            в момент возникновения ошибки
        :type action: framio.action.Action
        :param http_code: обрабатываемый HTTP код
        :type http_code: int
        """
        view = action.handler_wrapper
        view.__func__.__name__ = (
            '_{}_handler'.format(action.__class__.__name__))

        # Регистрируем как функцию обработки ошибок
        self.app.errorhandler(http_code)(view)

        # Проставляем ссылку на контроллер
        action.controller = self

    def harvest(self, apps):
        """
        Сборка действий из всех зарегистрированных пакетов

        :param apps: Список пакетов приложения
        :type apps: list
        """
        for app in apps:
            try:
                module = __import__(
                    '{}.app'.format(app),
                    fromlist=['register_actions'],
                )
            except ImportError:
                continue
                
            if hasattr(module, 'register_actions'):
                self.register_actions(module.register_actions())

        self._harvested = True

    def apply_lazy_logic(self):
        """
        Применение отложенной до момента инициализации приложения логики
        """
        for method in self._app_logic_queue:
            method()

    def run(self, path, name):
        """
        Запуск приложения

        :param path: Путь до директории приложения
        :type path: str
        :param name: Имя окружения приложения
        :type name: str
        """
        if not self._harvested:
            self._app = Flask(
                import_name=name,
                instance_path=path,
                instance_relative_config=True,
            )
            self._app.config.from_object(DEFAULT_SETTINGS)
            self._app.config.from_pyfile('local_settings.py', silent=True)

            # Собираем список действий
            self.harvest(apps=self.cfg['INSTALLED_APPS'])
            # Применение отложенной логики
            self.apply_lazy_logic()

        self.app.run(
            host=self.cfg.get('HOST', '127.0.0.1'),
            port=self.cfg.get('PORT', 8080),
            debug=self.cfg['DEBUG'],
        )
