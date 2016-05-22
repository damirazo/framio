# coding: utf-8
import os
from framio.controller import Controller
from demo.main.actions import NotFoundAction

__author__ = 'damirazo <me@damirazo.ru>'


# Инициация экземпляра контроллера
controller = Controller()
# Функция обработки 404 ошибки
controller.register_error_handler(NotFoundAction(), 404)
# Запуск контроллера
controller.run(
    path=os.path.abspath(os.path.dirname(__file__)),
    name=__name__,
)
