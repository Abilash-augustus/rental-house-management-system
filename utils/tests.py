from django.test import TestCase
from utils.models import PaymentMethods

class WhateverTest(TestCase):

    def create_option(self, name="mpesa", account_name="bravin s",paybill_number='4353455', account_number="73284923032847"):
        return PaymentMethods.objects.create(
            name=name,account_name=account_name,paybill_number=paybill_number,
            account_number=account_number,
            )

    def test_paymment_options_creation(self):
        w = self.create_option()
        self.assertTrue(isinstance(w, PaymentMethods))
        self.assertEqual(w.__str__(), f"{w.name} - {w.account_number}")