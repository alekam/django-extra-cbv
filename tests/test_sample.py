# coding: utf-8

from django.test import TestCase


class SampleTest(TestCase):

    def test_sample(self):
        self.assertFalse(False)
        self.assertTrue(True)
