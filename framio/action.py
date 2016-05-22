# coding: utf-8
from flask import request
from framio.context import Context

__author__ = 'damirazo <me@damirazo.ru>'


class Action(object):
    """
    Базовый класс для действий приложения
    """
    url = None
    """:type : None or str"""

    parent = None
    """:type: None or Action"""

    controller = None
    """:type : None or framio.controller.Controller"""

    available_methods = []
    """:type : list"""

    def __init__(self):
        super(Action, self).__init__()
        self._children = []

    def rules(self):
        """
        Список правил для формирования контекста запроса
        :rtype: dict
        """
        return {}

    def handler(self, context):
        """
        Метод с реализацией логики действия
        """
        raise NotImplementedError('Метод `handler` должен быть переопределен!')

    def pre_handler(self, context):
        """
        Вызывается до момента вызова метода с основной логикой действия.
        Может использоваться для дополнительных проверок
        или модификации контекста запроса.

        :param context: Сгенерированный контекст запроса
        :type context: Context
        """
        pass

    def handler_wrapper(self, *args, **kwargs):
        """
        Обертка над основной логикой действия.
        """
        context = Context.build(self.rules(), kwargs)

        self.pre_handler(context)

        try:
            response = self.handler(context)
        except NotImplementedError:
            raise
        except Exception as exception:
            return self.failure_handler(context, exception)
        else:
            return self.post_handler(context, response)

    def post_handler(self, context, response):
        """
        Вызывается после выполнения основной логики действия
        и формирования ответа.

        :param context: Контекст запроса
        :type context: Context
        :param response: Ответ действия
        """
        return response

    def failure_handler(self, context, exception):
        """
        Вызывается при возникновении исключения в логике действия.
        По умолчанию пробрасывает возникшее исключение дальше.

        :param context: Контекст запроса
        :type context: Context
        :param exception: Выброшенное исключение
        :type exception: Exception
        """
        raise exception

    def add_child(self, action):
        """
        Регистрация дочернего действия

        :param action : Класс действия
        :type action : Action
        """
        action.parent = self
        self._children.append(action)

    @property
    def full_url(self):
        """
        Полный URL до данного действия

        :rtype : str
        """
        url_segment = self.url or ''
        parent = self.parent

        while parent:
            url_segment = (parent.url or '') + url_segment
            parent = parent.parent

        segments = filter(None, url_segment.split('/'))

        return '/' + '/'.join(segments)

    @property
    def children(self):
        """
        Список дочерних действий

        :rtype : list
        """
        return self._children

    @property
    def cfg(self):
        """
        Делегирование доступа к методу
        с получением доступа к настройкам приложения

        :rtype : dict
        """
        return self.controller.cfg

    @property
    def request(self):
        """
        Объект входящего запроса
        """
        return request
