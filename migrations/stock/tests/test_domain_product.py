from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestDomainProductType(UpgradeCase):
    def prepare(self):
        filter_pt_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template 1",
                "model_id": "product.template",
                "domain": '[("type", "in", ["product", "consu"])]',
            }
        )
        filter_pt_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template 2",
                "model_id": "product.template",
                "domain": '[("type", "in", ["product"])]',
            }
        )
        filter_pt_3 = self.env["ir.filters"].create(
            {
                "name": "Filter product template 3",
                "model_id": "product.template",
                "domain": '[("type", "=", "product")]',
            }
        )
        filter_pt_4 = self.env["ir.filters"].create(
            {
                "name": "Filter product template 4",
                "model_id": "product.template",
                "domain": '[("type", "=", "consu")]',
            }
        )
        filter_pt_5 = self.env["ir.filters"].create(
            {
                "name": "Filter product template 5",
                "model_id": "product.template",
                "domain": '[("type", "in", ["product", "service"])]',
            }
        )
        filter_pt_6 = self.env["ir.filters"].create(
            {
                "name": "Filter product template 6",
                "model_id": "product.template",
                "domain": '[("type", "in", ["consu", "service"])]',
            }
        )
        filter_pp_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product product 1",
                "model_id": "product.product",
                "domain": '[("type", "in", ["product", "consu"])]',
            }
        )
        filter_pp_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product product 2",
                "model_id": "product.product",
                "domain": '[("type", "not in", ["product"])]',
            }
        )
        filter_move_1 = self.env["ir.filters"].create(
            {
                "name": "Filter move 1",
                "model_id": "stock.move",
                "domain": '[("product_type", "in", ["consu", "product"])]',
            }
        )
        filter_move_2 = self.env["ir.filters"].create(
            {
                "name": "Filter move 2",
                "model_id": "stock.move",
                "domain": '[("product_type", "=", "product")]',
            }
        )
        filter_move_3 = self.env["ir.filters"].create(
            {
                "name": "Filter move 3",
                "model_id": "stock.move",
                "domain": '[("product_type", "=", "consu")]',
            }
        )
        return {
            "template": (filter_pt_1 | filter_pt_2 | filter_pt_3 | filter_pt_4 | filter_pt_5 | filter_pt_6).ids,
            "product": (filter_pp_1 | filter_pp_2).ids,
            "move": (filter_move_1 | filter_move_2 | filter_move_3).ids,
        }

    def check(self, init):
        pt_filters = self.env["ir.filters"].browse(init["template"])
        pp_filters = self.env["ir.filters"].browse(init["product"])
        move_filters = self.env["ir.filters"].browse(init["move"])
        self.assertRecordValues(
            pt_filters,
            [
                {"domain": "['|', ('is_storable', '=', True), ('type', 'in', ['consu'])]"},
                {"domain": "[('is_storable', '=', True)]"},
                {"domain": "[('is_storable', '=', True)]"},
                {"domain": "['&', ('type', '=', 'consu'), ('is_storable', '=', False)]"},
                {"domain": "['|', ('is_storable', '=', True), ('type', 'in', ['service'])]"},
                {"domain": "['&', ('is_storable', '=', False), ('type', 'in', ['consu', 'service'])]"},
            ],
        )
        self.assertRecordValues(
            pp_filters,
            [
                {"domain": "['|', ('is_storable', '=', True), ('type', 'in', ['consu'])]"},
                {"domain": "[('is_storable', '=', False)]"},
            ],
        )
        self.assertRecordValues(
            move_filters,
            [
                {"domain": "[(1, '=', 1)]"},
                {"domain": "[('is_storable', '=', True)]"},
                {"domain": "[('is_storable', '=', False)]"},
            ],
        )
