# coding: utf-8
from framio.action import Action

__author__ = 'damirazo <me@damirazo.ru>'


class IndexDemoAction(Action):
    url = '/'

    def handler(self, context):
        return self.render('index.html')


class BaseDemoAction(Action):
    url = '/main'

    def __init__(self):
        super(BaseDemoAction, self).__init__()

        self.add_child(MainAction())
        self.add_child(HelloAction())


class MainAction(Action):
    url = '/test'

    def handler(self, context):
        return '<h1>Тестовая страница</h1>'


class HelloAction(Action):
    url = '/hello'

    def handler(self, context):
        return 'Hello, {}'.format(self.request.args.get('name', 'World'))


class NotFoundAction(Action):

    def handler(self, context):
        return '404 not found O_O'
