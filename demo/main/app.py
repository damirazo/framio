# coding: utf-8
from demo.main.actions import BaseDemoAction, IndexDemoAction

__author__ = 'damirazo <me@damirazo.ru>'


def register_actions():
    return (
        IndexDemoAction(),
        BaseDemoAction(),
    )
