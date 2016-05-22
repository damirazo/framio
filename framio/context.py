# coding: utf-8
from framio.exceptions import ContextBuildFailed

__author__ = 'damirazo <me@damirazo.ru>'


class Context(object):
    """
    Контекст запроса
    """

    _Empty = None
    """:type : None"""

    args = []
    kwargs = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                setattr(self, k, v)

    @classmethod
    def build(cls, rules, params):
        u"""
        Сборка контекста запроса на основе списка правил
        и переданных параметров.
        Возвращает заполненный экземпляр контекста запроса.

        :param rules: Список контекстных правил
        :type rules: dict
        :param params: Список параметров запроса
        :type params: dict

        :exception: ContextBuildFailed

        :rtype: Context
        """
        result = {}

        for name, rule in rules.items():
            value_type = rule.get('type', str)
            is_required = rule.get('required', False)
            default = rule.get('default', cls._Empty)

            if not callable(value_type):
                raise ContextBuildFailed(
                    'Функция преобразования контекста должна быть вызываемой')

            value = params.get(name, cls._Empty)

            if value is cls._Empty:
                if is_required and default is cls._Empty:
                    raise ContextBuildFailed((
                        'Не задано обязательное значение "{}"'
                    ).format(name))
                elif is_required:
                    value = default

            try:
                value = value_type(value)
            except TypeError:
                raise ContextBuildFailed((
                    'Не удается преобразовать значение параметра "{}"'
                ).format(name))

            result[name] = value

        return cls(**params)
