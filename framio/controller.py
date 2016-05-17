# coding: utf-8
from flask import Flask
from framio.settings import DEFAULT_SETTINGS

__author__ = 'damirazo <me@damirazo.ru>'


class Controller(object):
    """
    Базовый класс контроллера приложения
    """
    _app = None
    """:type : Flask"""

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

        class _View(object):

            def __init__(self, action_handler):
                self.handler = action_handler

            def __call__(self, *args, **kwargs):
                return self.handler(*args, **kwargs)

        def _recursive_register(a):
            """
            Рекурсивная сборка дочерних действий

            :param a: Обрабатываемое действие
            :type a: framio.action.Action
            """
            url = a.full_url

            # Регистрируем только те маршруты, что имеют URL.
            # Все прочие считаем группами и проходим по дочерним.
            if url:
                if url in self._actions:
                    raise ValueError((
                        'URL "{}" уже использовался для действия {}'
                    ).format(url, self._actions[url].__class__.__name__))

                self._actions[a.full_url] = a

                params = {'rule': a.full_url}
                """:type : dict[str, object]"""
                if a.available_methods:
                    params.update({'methods': a.available_methods})

                view = a.handler_wrapper
                view.__func__.__name__ = (
                    '_{}_handler'.format(a.__class__.__name__))

                # Регистрируем маршрут
                self.app.route(**params)(view)

            # Проставляем ссылку на контроллер
            a.controller = self

            for child_action in a.children:
                _recursive_register(child_action)

        for action in actions:
            _recursive_register(action)

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

        self.app.run(
            host=self.cfg.get('HOST', '127.0.0.1'),
            port=self.cfg.get('PORT', 8080),
            debug=self.cfg['DEBUG'],
        )
