# coding: utf-8
import os
from framio.controller import Controller

__author__ = 'damirazo <me@damirazo.ru>'


controller = Controller()
controller.run(
    path=os.path.abspath(os.path.dirname(__file__)),
    name=__name__,
)
