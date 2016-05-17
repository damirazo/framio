# coding: utf-8
from framio.action import Action

__author__ = 'damirazo <me@damirazo.ru>'


class BaseDemoAction(Action):

    def __init__(self):
        super(BaseDemoAction, self).__init__()

        self.add_child(MainAction())
        self.add_child(HelloAction())


class MainAction(Action):
    url = '/'

    def handler(self, context):
        return '<h1>Тестовая страница</h1>'


class HelloAction(Action):
    url = '/hello/<name>'

    def rules(self):
        return {
            'name': {'required': True, 'default': 'ololo'},
        }

    def handler(self, context):
        return 'Hello, {}'.format(context.name)
