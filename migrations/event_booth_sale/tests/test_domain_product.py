from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestDomainProductType(UpgradeCase):
    def prepare(self):
        # Only event_booth
        filter_pt_only_booth_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booth 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "=", "event_booth")]',
            }
        )
        filter_pt_only_booth_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booth 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "!=", "event_booth")]',
            }
        )
        filter_pt_only_booth_3 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booth 3",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["event_booth"])]',
            }
        )
        filter_pt_only_booth_4 = self.env["ir.filters"].create(
            {
                "name": "Filter product template booth 4",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["event_booth"])]',
            }
        )

        # event_booth and event
        filter_pt_event_booth_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event booth 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["event", "event_booth"])]',
            }
        )
        filter_pt_event_booth_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event booth 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["event", "event_booth"])]',
            }
        )

        # event_booth and service
        filter_pt_booth_service_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template service booth 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["service", "event_booth"])]',
            }
        )
        filter_pt_booth_service_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template service booth 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["service", "event_booth"])]',
            }
        )

        # event_booth and consu
        filter_pt_booth_consu_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu booth 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["consu", "event_booth"])]',
            }
        )
        filter_pt_booth_consu_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu booth 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["consu", "event_booth"])]',
            }
        )

        # event_booth, service and event
        filter_pt_event_booth_service_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event booth service 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["service", "event", "event_booth"])]',
            }
        )
        filter_pt_event_booth_service_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event booth service 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["service", "event", "event_booth"])]',
            }
        )

        # event_booth, event and consu
        filter_pt_event_booth_consu_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event consu booth 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["consu", "event", "event_booth"])]',
            }
        )
        filter_pt_event_booth_consu_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template event consu booth 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["consu", "event", "event_booth"])]',
            }
        )

        # event_booth, service and consu
        filter_pt_consu_booth_service_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu booth service 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["service", "consu", "event_booth"])]',
            }
        )
        filter_pt_consu_booth_service_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu booth service 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["service", "consu", "event_booth"])]',
            }
        )

        # event_booth, service and consu
        filter_pt_consu_event_booth_service_1 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu event booth service 1",
                "model_id": "product.template",
                "domain": '[("detailed_type", "in", ["service", "consu", "event", "event_booth"])]',
            }
        )
        filter_pt_consu_event_booth_service_2 = self.env["ir.filters"].create(
            {
                "name": "Filter product template consu event booth service 2",
                "model_id": "product.template",
                "domain": '[("detailed_type", "not in", ["service", "consu", "event", "event_booth"])]',
            }
        )

        return {
            "template_only_booth": (
                filter_pt_only_booth_1 | filter_pt_only_booth_2 | filter_pt_only_booth_3 | filter_pt_only_booth_4
            ).ids,
            "template_event_booth": (filter_pt_event_booth_1 | filter_pt_event_booth_2).ids,
            "template_booth_service": (filter_pt_booth_service_1 | filter_pt_booth_service_2).ids,
            "template_booth_consu": (filter_pt_booth_consu_1 | filter_pt_booth_consu_2).ids,
            "template_event_booth_service": (filter_pt_event_booth_service_1 | filter_pt_event_booth_service_2).ids,
            "template_event_booth_consu": (filter_pt_event_booth_consu_1 | filter_pt_event_booth_consu_2).ids,
            "template_booth_service_consu": (filter_pt_consu_booth_service_1 | filter_pt_consu_booth_service_2).ids,
            "template_all_type": (filter_pt_consu_event_booth_service_1 | filter_pt_consu_event_booth_service_2).ids,
        }

    def check(self, init):
        pt_only_booth_filters = self.env["ir.filters"].browse(init["template_only_booth"])
        pt_event_booth_filters = self.env["ir.filters"].browse(init["template_event_booth"])
        pt_booth_service_filters = self.env["ir.filters"].browse(init["template_booth_service"])
        pt_booth_consu_filters = self.env["ir.filters"].browse(init["template_booth_consu"])
        pt_event_booth_service_filters = self.env["ir.filters"].browse(init["template_event_booth_service"])
        pt_event_booth_consu_filters = self.env["ir.filters"].browse(init["template_event_booth_consu"])
        pt_booth_service_consu_filters = self.env["ir.filters"].browse(init["template_booth_service_consu"])
        pt_all_type_filters = self.env["ir.filters"].browse(init["template_all_type"])
        self.assertRecordValues(
            pt_only_booth_filters,
            [
                {"domain": "['&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"},
                {"domain": "['!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"},
                {"domain": "['&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"},
                {"domain": "['!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"},
            ],
        )
        self.assertRecordValues(
            pt_event_booth_filters,
            [
                {
                    "domain": "['|', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth'), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                },
                {
                    "domain": "['|', '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth'), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                },
            ],
        )
        self.assertRecordValues(
            pt_booth_service_filters,
            [
                {"domain": "[('type', 'in', ['service'])]"},
                {"domain": "[('type', 'not in', ['service'])]"},
            ],
        )
        self.assertRecordValues(
            pt_event_booth_service_filters,
            [
                {"domain": "[('type', 'in', ['service'])]"},
                {"domain": "[('type', 'not in', ['service'])]"},
            ],
        )
        if util.module_installed(self.env.cr, "stock"):
            self.assertRecordValues(
                pt_booth_consu_filters,
                [
                    {
                        "domain": "['&', ('is_storable', '=', False), '|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"
                    },
                    {
                        "domain": "['|', ('is_storable', '=', True), '|', ('type', 'not in', ['consu']), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"
                    },
                ],
            )
            self.assertRecordValues(
                pt_event_booth_consu_filters,
                [
                    {
                        "domain": "['&', ('is_storable', '=', False), '|', '|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth'), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                    },
                    {
                        "domain": "['|', ('is_storable', '=', True), '|', '|', ('type', 'not in', ['consu']), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth'), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                    },
                ],
            )
            self.assertRecordValues(
                pt_booth_service_consu_filters,
                [
                    {"domain": "['&', ('is_storable', '=', False), ('type', 'in', ['service', 'consu'])]"},
                    {"domain": "['|', ('is_storable', '=', True), ('type', 'not in', ['service', 'consu'])]"},
                ],
            )
            self.assertRecordValues(
                pt_all_type_filters,
                [
                    {"domain": "['&', ('is_storable', '=', False), ('type', 'in', ['service', 'consu'])]"},
                    {"domain": "['|', ('is_storable', '=', True), ('type', 'not in', ['service', 'consu'])]"},
                ],
            )
            return
        self.assertRecordValues(
            pt_booth_consu_filters,
            [
                {
                    "domain": "['|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"
                },
                {
                    "domain": "['|', ('type', 'not in', ['consu']), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth')]"
                },
            ],
        )
        self.assertRecordValues(
            pt_event_booth_consu_filters,
            [
                {
                    "domain": "['|', '|', ('type', 'in', ['consu']), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth'), '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                },
                {
                    "domain": "['|', '|', ('type', 'not in', ['consu']), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event_booth'), '!', '&', ('type', '=', 'service'), ('service_tracking', '=', 'event')]"
                },
            ],
        )
        self.assertRecordValues(
            pt_booth_service_consu_filters,
            [
                {"domain": "[('type', 'in', ['service', 'consu'])]"},
                {"domain": "[('type', 'not in', ['service', 'consu'])]"},
            ],
        )
        self.assertRecordValues(
            pt_all_type_filters,
            [
                {"domain": "[('type', 'in', ['service', 'consu'])]"},
                {"domain": "[('type', 'not in', ['service', 'consu'])]"},
            ],
        )
