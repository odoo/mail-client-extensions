from textwrap import dedent

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("12.5")
class TestReadGroupRefactor(UpgradeCase):
    _wrapper = dedent(
        """
        # Some useless comment to assert comment are preserved
        if 'some useless code': # To assert code around is left untouched
            some = 'useless' + 'code'

            %s  # Indent under the `if` the test to assert the read_group remains indented

        # Some useless comment to assert comment are preserved
        if 'some useless code': # To assert code around is left untouched
            some = 'useless' + 'code'"""  # Force no carriage return to test `RefactoringTool` without carriage return
    )
    _tests = [
        (
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id')",
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id')",
        ),
        (
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id')",
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id')",
        ),
        (
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], 'company_id', ['company_id'])",
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], ['company_id'], ['company_id'])",
        ),
        (
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], ['company_id'], ['company_id'])",
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], ['company_id'], ['company_id'])",
        ),
        (
            "self.read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id')",
            "self.read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id')",
        ),
        (
            "self.read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id', offset=10)",
            "self.read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id', offset=10)",
        ),
        (
            "self.read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id', 10)",
            "self.read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id', 10)",
        ),
        (
            "self.read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id', offset=10, limit=10)",
            "self.read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id', offset=10, limit=10)",
        ),
        (
            "self.read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id', 10, 10)",
            "self.read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id', 10, 10)",
        ),
        (
            "User = self.env['res.users'];"
            "User.read_group([('company_id', 'in', [1, 2])], 'company_id', 'company_id')",
            "User = self.env['res.users'];"
            "User.read_group([('company_id', 'in', [1, 2])], ['company_id'], 'company_id')",
        ),
        (
            # If this could be supported that would be super cool, but I do not think its easily feasible,
            # so in the mean time this must be left untouched
            "fields = 'company_id';"
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], fields, ['company_id'])",
            "fields = 'company_id';"
            "self.env['res.users'].read_group([('company_id', 'in', [1, 2])], fields, ['company_id'])",
        ),
    ]

    def prepare(self):
        field_ids = []
        server_act_ids = []
        for i, (test, _) in enumerate(self._tests):
            field = self.env["ir.model.fields"].create(
                {
                    "name": "x_upgrade_read_group_%s" % i,
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "manual",
                    "field_description": "x_upgrade_read_group_%s" % i,
                    "compute": self._wrapper % test,
                    "store": False,
                    "ttype": "boolean",
                }
            )
            field_ids.append(field.id)
            server_act = self.env["ir.actions.server"].create(
                {
                    "name": "x_upgrade_read_group_%s" % i,
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "code",
                    "code": self._wrapper % test,
                }
            )
            server_act_ids.append(server_act.id)
        return (field_ids, server_act_ids)

    def check(self, init):
        field_ids, server_act_ids = init
        fields = self.env["ir.model.fields"].browse(field_ids)
        server_acts = self.env["ir.actions.server"].browse(server_act_ids)
        for field, server_act, (_, check) in zip(fields, server_acts, self._tests):
            self.assertEqual(field.compute, self._wrapper % check)
            self.assertEqual(server_act.code, self._wrapper % check)
