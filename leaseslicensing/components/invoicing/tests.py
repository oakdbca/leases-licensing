from django.test import SimpleTestCase

from leaseslicensing.components.invoicing.models import ChargeMethod


class ChargeMethodTestCase(SimpleTestCase):
    def test_charge_method(self):
        charge_method = ChargeMethod(key="test", display_name="Test")
        self.assertEqual(charge_method.key, "test")
