from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestDomainProductType(UpgradeCase):
    def prepare(self):
        if util.module_installed(self.env.cr, "stock") or not util.module_installed(self.env.cr, "event_sale"):
            return {}

        filter_pt_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["event", "consu"])]',
            }
        )
        filter_pt_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["event"])]',
            }
        )
        filter_pt_3 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 3",
                "model_id": "product.template",
                "domain": '[("detailed_type", "=", "event")]',
            }
        )
        filter_pt_4 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 4",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["event", "service"])]',
            }
        )
        filter_pt_5 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 5",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["event", "service", "consu"])]',
            }
        )
        filter_pt_6 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 6",
                "model_id": "product.template",
                "domain": '[("detailed_type", "!=", "event")]',
            }
        )
        filter_pt_7 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event 7",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["event", "service"])]',
            }
        )
        filter_pp_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product product event 1",
                "model_id": "product.product",
                "domain": '[("detailed_type", "in", ["event", "consu"])]',
            }
        )
        filter_pp_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product product event 2",
                "model_id": "product.product",
                "domain": '[("detailed_type", "not in", ["event"])]',
            }
        )
        return {
            "template_event": (
                filter_pt_1 | filter_pt_2 | filter_pt_3 | filter_pt_4 | filter_pt_5 | filter_pt_6 | filter_pt_7
            ).ids,
            "product_event": (filter_pp_1 | filter_pp_2).ids,
        }

    def check(self, init):
        if util.module_installed(self.env.cr, "stock") or not util.module_installed(self.env.cr, "event_sale"):
            return

        pt_filters = self.env["ir.filters"].browse(init["template_event"])
        pp_filters = self.env["ir.filters"].browse(init["product_event"])
        self.assertRecordValues(
            pt_filters,
            [
                {
                    "domain": "['|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                },
                {"domain": "['&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"},
                {"domain": "['&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"},
                {"domain": "[('type', 'in', ['service'])]"},
                {"domain": "[('type', 'in', ['service', 'consu'])]"},
                {"domain": "['!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"},
                {"domain": "[('type', 'not in', ['service'])]"},
            ],
        )
        self.assertRecordValues(
            pp_filters,
            [
                {
                    "domain": "['|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                },
                {"domain": "['!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"},
            ],
        )
