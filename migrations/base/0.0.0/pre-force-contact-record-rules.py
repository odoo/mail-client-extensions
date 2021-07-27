# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Disabling the contact "employees" rule without disabling the contact "access to private address" rule
    # has as effect to restrict completely the read access to all contacts to all users.
    # Besides, even for users having the "Access to private addresses" rule, they can only see "private" contacts
    # That doesn't make sense, and this prevents the good use of the database, since any record which read
    # a field from a partner will raise an access error (if not read with sudo)
    rule_employee_id = util.ref(cr, "base.res_partner_rule_private_employee")
    rule_group_id = util.ref(cr, "base.res_partner_rule_private_group")
    if rule_employee_id and rule_group_id:
        cr.execute(
            "SELECT id, active FROM ir_rule WHERE id IN %s",
            [(rule_employee_id, rule_group_id)],
        )
        rules = dict(cr.fetchall())
        if bool(rules.get(rule_group_id)) ^ bool(rules.get(rule_employee_id)):
            cr.execute("UPDATE ir_rule SET active = true WHERE id IN %s", [(rule_employee_id, rule_group_id)])
