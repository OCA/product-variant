from odoo.addons.product.tests.test_product_attribute_value_config import (
    TestProductAttributeValueCommon,
)


class TestProductAttributeValueCommon(TestProductAttributeValueCommon):
    def test_fixed_and_extra_price(self):
        self.computer.company_id = False

        computer_ssd_256 = self._get_product_template_attribute_value(self.ssd_256)
        computer_ram_8 = self._get_product_template_attribute_value(self.ram_8)
        computer_hdd_1 = self._get_product_template_attribute_value(self.hdd_1)

        combination = computer_ssd_256 + computer_ram_8 + computer_hdd_1
        computer_variant = self.computer._get_variant_for_combination(combination)
        computer_variant.fix_price = 1000
        computer_variant._compute_variant_sale_price()
        total = computer_variant.fix_price + computer_variant.price_extra
        self.assertEqual(computer_variant.variant_sale_price, total)
