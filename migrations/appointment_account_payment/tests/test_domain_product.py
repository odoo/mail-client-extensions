from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestDomainProductType(UpgradeCase):
    def prepare(self):
        # Only booking_fees
        filter_pt_only_booking_fees_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booking fees 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "=", "booking_fees")]',
            }
        )
        filter_pt_only_booking_fees_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booking fees 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "!=", "booking_fees")]',
            }
        )
        filter_pt_only_booking_fees_3 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booking fees 3",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["booking_fees"])]',
            }
        )
        filter_pt_only_booking_fees_4 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booking fees 4",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["booking_fees"])]',
            }
        )

        # booking_fees and service
        filter_pt_service_booking_fees_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template service booking fees 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["booking_fees", "service"])]',
            }
        )
        filter_pt_service_booking_fees_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template service booking fees 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["booking_fees", "service"])]',
            }
        )
        # booking_fees and consu
        filter_pt_consu_booking_fees_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu booking fees 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["booking_fees", "consu"])]',
            }
        )
        filter_pt_consu_booking_fees_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu booking fees 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["booking_fees", "consu"])]',
            }
        )
        # booking_fees, service and consu
        filter_pt_service_consu_booking_fees_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template service consu booking fees 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["booking_fees", "consu", "service"])]',
            }
        )
        filter_pt_service_consu_booking_fees_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template service consu booking fees 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["booking_fees", "consu", "service"])]',
            }
        )
        return {
            "template_only_booking_fees": (
                filter_pt_only_booking_fees_1
                | filter_pt_only_booking_fees_2
                | filter_pt_only_booking_fees_3
                | filter_pt_only_booking_fees_4
            ).ids,
            "template_service_booking_fees": (filter_pt_service_booking_fees_1 | filter_pt_service_booking_fees_2).ids,
            "template_consu_booking_fees": (filter_pt_consu_booking_fees_1 | filter_pt_consu_booking_fees_2).ids,
            "template_service_consu_booking_fees": (
                filter_pt_service_consu_booking_fees_1 | filter_pt_service_consu_booking_fees_2
            ).ids,
        }

    def check(self, init):
        pt_only_booking_fees_filters = self.env["ir.filters"].browse(init["template_only_booking_fees"])
        pt_service_booking_fees_filters = self.env["ir.filters"].browse(init["template_service_booking_fees"])
        pt_consu_booking_fees_filters = self.env["ir.filters"].browse(init["template_consu_booking_fees"])
        pt_service_consu_booking_fees_filters = self.env["ir.filters"].browse(
            init["template_service_consu_booking_fees"]
        )
        self.assertRecordValues(
            pt_only_booking_fees_filters,
            [
                {"domain": "['&', ('type', '=', 'service'), ('sale_ok', '=', True)]"},
                {"domain": "['!', '&', ('type', '=', 'service'), ('sale_ok', '=', True)]"},
                {"domain": "['&', ('type', '=', 'service'), ('sale_ok', '=', True)]"},
                {"domain": "['!', '&', ('type', '=', 'service'), ('sale_ok', '=', True)]"},
            ],
        )
        self.assertRecordValues(
            pt_service_booking_fees_filters,
            [
                {"domain": "[('type', 'in', ['service'])]"},
                {"domain": "[('type', 'not in', ['service'])]"},
            ],
        )
        if util.module_installed(self.env.cr, "stock"):
            self.assertRecordValues(
                pt_consu_booking_fees_filters,
                [
                    {
                        "domain": "['&', ('is_storable', '=', False), '|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('sale_ok', '=', True)]"
                    },
                    {
                        "domain": "['|', ('is_storable', '=', True), '|', ('type', 'not in', ['consu']), '!', '&', ('type', '=', 'service'), ('sale_ok', '=', True)]"
                    },
                ],
            )
            self.assertRecordValues(
                pt_service_consu_booking_fees_filters,
                [
                    {"domain": "['&', ('is_storable', '=', False), ('type', 'in', ['consu', 'service'])]"},
                    {"domain": "['|', ('is_storable', '=', True), ('type', 'not in', ['consu', 'service'])]"},
                ],
            )
            return
        self.assertRecordValues(
            pt_consu_booking_fees_filters,
            [
                {"domain": "['|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('sale_ok', '=', True)]"},
                {
                    "domain": "['|', ('type', 'not in', ['consu']), '!', '&', ('type', '=', 'service'), ('sale_ok', '=', True)]"
                },
            ],
        )
        self.assertRecordValues(
            pt_service_consu_booking_fees_filters,
            [
                {"domain": "[('type', 'in', ['consu', 'service'])]"},
                {"domain": "[('type', 'not in', ['consu', 'service'])]"},
            ],
        )
