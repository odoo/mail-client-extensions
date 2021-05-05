# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("14.5")
class FleetCategoryCase(UpgradeCase):
    def prepare(self):
        company_ids = self.env["res.company"].create(
            [
                {"name": "Fleet test company 1"},
                {"name": "Fleet test company 2"},
            ]
        )
        user_ids = self.env["res.users"].create(
            [
                {
                    "name": "Mister Fleet",
                    "login": "mfl",
                    "company_ids": [(6, 0, company_ids.ids)],
                    "company_id": company_ids[0].id,
                },
                {
                    "name": "Miss Fleet",
                    "login": "mif",
                    "company_ids": [(6, 0, company_ids.ids)],
                    "company_id": company_ids[0].id,
                },
            ]
        )
        # Required for vehicle creation
        brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Aixam",
            }
        )
        model = self.env["fleet.vehicle.model"].create(
            {
                "brand_id": brand.id,
                "name": "Coupe GTI",
            }
        )
        # Create 2 vehicles per company per manager + 2 vehicles with both null + 2 vehicles with no company but manager
        vehicles = self.env["fleet.vehicle"]
        vehicles |= vehicles.create(
            {
                "model_id": model.id,
                "company_id": False,
            }
        )
        vehicles |= vehicles.create(
            {
                "model_id": model.id,
                "company_id": False,
            }
        )
        vehicles |= vehicles.create(
            {
                "model_id": model.id,
                "manager_id": user_ids[0].id,
                "company_id": False,
            }
        )
        vehicles |= vehicles.create(
            {
                "model_id": model.id,
                "manager_id": user_ids[0].id,
                "company_id": False,
            }
        )
        for company_id in company_ids:
            for manager_id in user_ids:
                for _i in range(2):
                    vehicles |= vehicles.create(
                        {
                            "model_id": model.id,
                            "manager_id": manager_id.id,
                            "company_id": company_id.id,
                        }
                    )

        return (
            [company.id for company in company_ids],
            [manager.id for manager in user_ids],
            [vehicle.id for vehicle in vehicles],
        )

    def check(self, init):
        companies, managers, vehicles = init
        # company_ids = self.env["res.company"].browse(companies)
        # user_ids = self.env["res.users"].browse(managers)
        vehicle_ids = self.env["fleet.vehicle"].browse(vehicles)

        # We should have 3 fleet.category for our first manager and 2 for our second
        fleet_ids = self.env["fleet.category"].search(
            [
                ("manager_id", "in", managers),
            ]
        )
        self.assertEqual(len(fleet_ids.filtered(lambda c: c.manager_id.id == managers[0])), 3)
        self.assertEqual(len(fleet_ids.filtered(lambda c: c.manager_id.id == managers[1])), 2)

        # Vehicles with no manager should not have a fleet_id
        for vehicle in vehicle_ids.filtered(lambda v: not v.manager_id):
            self.assertEqual(vehicle.fleet_id.id, False)
        # Those who do should have a fleet_id
        for vehicle in vehicle_ids.filtered(lambda v: v.manager_id):
            self.assertEqual(vehicle.fleet_id.id is not False, True)

        # Verify that two vehicles with the same manager and company have the same fleet
        for company in [False] + companies:
            for manager in managers:
                vehicles = vehicle_ids.filtered(lambda v: v.company_id.id == company and v.manager_id.id == manager)
                # manager 2 doesn't have any vehicles with no company
                if vehicles:
                    self.assertEqual(len(vehicles.fleet_id.ids), 1)
                elif company:
                    raise AssertionError("No vehicles with company %d" % company)
