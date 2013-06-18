from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eid = util.ref(cr, 'hr.employee')
    if eid:
        cr.execute('SELECT id FROM hr_employee WHERE id=%s', (eid,))
        if cr.fetchone():
            return
        util.remove_record(cr, 'hr.employee')
    util.remove_record(cr, 'hr.employee_resource_resource')
