from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestMigrateRecruitment(UpgradeCase):
    def prepare(self):
        self.env.cr.execute("""
        UPDATE ir_config_parameter
        SET value = 'jobs-listings@linkedin.com,custom_blacklist@custom.com'
        WHERE "key" = 'hr_recruitment.blacklisted_emails'""")

    def check(self, init):
        # Total number of platforms should be 3 (default data) + 1 (the unknown blacklisted platform)
        platforms = self.env["hr.job.platform"].search([])
        self.assertEqual(len(platforms), 4)

        # Upgrade should not override the new regex defined in data
        linkedin_regex = self.env["hr.job.platform"].search([("email", "=", "jobs-listings@linkedin.com")])
        self.assertEqual(linkedin_regex.regex, "New application:.*from (.*)")

        # Unknown blacklisted mail should have (?!) as regex
        unknown_regex = self.env["hr.job.platform"].search([("email", "=", "custom_blacklist@custom.com")])
        self.assertEqual(unknown_regex.regex, "(?!)")
