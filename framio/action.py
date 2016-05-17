# coding: utf-8
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
        return {}

    def handler(self, context):
        """
        Метод с реализацией логики действия
        """
        raise NotImplementedError('Метод `handler` должен быть переопределен!')

    def pre_handler(self, context):
        pass

    def handler_wrapper(self, **kwargs):
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
        return response

    def failure_handler(self, context, exception):
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
        if self.url is None and self.parent is None:
            return

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
