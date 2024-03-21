from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestFlexibleCalendar(UpgradeCase):
    def prepare(self):
        """
        create resource (employee) with no calendar_id (flexible working calendar before migration)
        """
        self.flex_resource = (
            self.env["resource.resource"]
            .with_company(self.env.company)
            .create(
                {
                    "name": "Test FlexResource",
                    "resource_type": "user",
                    "company_id": self.env.company.id,
                    "calendar_id": False,
                }
            )
        )
        # set the calendar_id as False explicitely after the default calendar gets assigned on creation (happens in 17.0)
        self.flex_resource.calendar_id = False
        return {"flex_resource_id": self.flex_resource.id}

    def check(self, init):
        """
        check that:
        - flex_resource created in prerate is assigned a flexible calendar
        """
        self.assertTrue(self.env["resource.resource"].browse(init["flex_resource_id"]).calendar_id.flexible_hours)
