from odoo.upgrade import util


def migrate(cr, version):
    holidays_allocation = util.orm.env(cr)["hr.leave.allocation"]
    cr.execute("SELECT id FROM hr_leave_allocation WHERE name IS NULL")
    ids = [res[0] for res in cr.fetchall()]
    for allocation in util.iter_browse(holidays_allocation, ids):
        allocation.name = allocation._get_title()
