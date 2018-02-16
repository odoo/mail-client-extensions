# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def adapt_cron(cr, old_name, new_name, default_delay):
    util.create_column(cr, 'res_company', 'timesheet_mail_{}_allow'.format(new_name), 'boolean')
    util.create_column(cr, 'res_company', 'timesheet_mail_{}_delay'.format(new_name), 'int4')
    util.create_column(cr, 'res_company', 'timesheet_mail_{}_interval'.format(new_name), 'varchar')
    util.create_column(cr, 'res_company', 'timesheet_mail_{}_nextdate'.format(new_name), 'timestamp without time zone')

    cron = util.ref(cr, 'timesheet_grid.timesheet_reminder_' + old_name)
    if not cron:
        cr.execute("""
            UPDATE res_company
               SET timesheet_mail_{0}_allow = false,
                   timesheet_mail_{0}_delay=%s,
                   timesheet_mail_{0}_interval='weeks'
        """.format(new_name), [default_delay])
        return

    ICP = util.env(cr)['ir.config_parameter']
    delay = ICP.get_param('timesheet.reminder.{}.delay'.format(old_name)) or default_delay
    cr.execute("""
        UPDATE res_company
           SET timesheet_mail_{0}_allow = c.active,
               timesheet_mail_{0}_delay = %s,
               timesheet_mail_{0}_interval = c.interval_type,
               timesheet_mail_{0}_nextdate = c.nextcall
          FROM ir_cron c
         WHERE c.id = %s
    """.format(new_name), [int(delay), cron])

    ICP.set_param('timesheet.reminder.{}.delay'.format(old_name), None)     # unlink
    util.remove_record(cr, 'timesheet_grid.timesheet_reminder_' + old_name)


def migrate(cr, version):
    adapt_cron(cr, 'user', 'employee', 3)
    adapt_cron(cr, 'manager', 'manager', 7)
