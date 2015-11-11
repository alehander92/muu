from muu import muu

import pytest


class TestDecorator(object):

    def test_simple_lambdas(self):
        @muu
        def fun(a):
            return lam()['a']

        assert fun('')() == 'a'

    def test_lambdas_with_assign(self):
        @muu
        def fun(x, z=2):
            return lam(e)[
                y < - x,
                y + e]

        assert fun(2)(2) == 4
