# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    if util.has_enterprise():
        util.new_module(cr, 'account_bank_statement_import_camt',
                        deps=('account_bank_statement_import',))
        util.new_module(cr, 'account_bank_statement_import_csv',
                        deps=('account_bank_statement_import', 'base_import'))

        util.new_module(cr, 'web_enterprise', deps=('web',), auto_install=True)

        util.new_module_dep(cr, 'crm_voip', 'web_enterprise')

        util.new_module(cr, 'grid', deps=('web',), auto_install=True)
        util.new_module(cr, 'timesheet_grid', deps=('grid', 'hr_timesheet'), auto_install=True)
        util.new_module(cr, 'hr_timesheet_sheet_timesheet_grid',
                        deps=('hr_timesheet_sheet', 'timesheet_grid'), auto_install=True)
        util.new_module(cr, 'timesheet_grid_sale',
                        deps=('timesheet_grid', 'sale_timesheet'), auto_install=True)

    util.new_module_dep(cr, 'base_import', 'web_kanban')
    util.new_module_dep(cr, 'hr_holidays', 'product')

    util.new_module(cr, 'hr_timesheet_attendance',
                    deps=('hr_timesheet', 'hr_attendance'),
                    auto_install=True)

    if "saas" in version:
        # for saas-10 databases
        util.new_module(cr, "hw_screen", deps={"hw_proxy"})
        util.new_module(cr, "l10n_fr_certification", deps={"l10n_fr"})
        util.new_module(cr, "l10n_fr_sale_closing", deps={"l10n_fr_certification"}, auto_install=True)
        util.new_module(cr, "l10n_fr_pos_cert", deps={"l10n_fr_certification", "point_of_sale"})
        util.new_module(cr, "l10n_in_schedule6", deps={"account"})

    util.new_module(cr, 'payment_payumoney', deps=('payment',))
    util.new_module(cr, 'payment_stripe', deps=('payment',))

    util.ENVIRON['sale_layout_installed'] = util.module_installed(cr, 'sale_layout')
    util.merge_module(cr, 'sale_layout', 'sale')

    util.merge_module(cr, 'sale_service', 'sale_timesheet')

    # reassign fields to related modules
    warn_fields = {
        'sale': ('sale', 'res.partner'),
        'purchase': ('purchase', 'res.partner'),
        'picking': ('stock', 'res.partner'),
        'invoice': ('account', 'res.partner'),
        'sale_line': ('sale', 'product.template'),
        'purchase_line': ('purchase', 'product.template'),
    }
    for prefix, (module, model) in warn_fields.items():
        util.move_field_to_module(cr, model, prefix + '_warn', 'warning', module)
        util.move_field_to_module(cr, model, prefix + '_warn_msg', 'warning', module)

    util.ENVIRON['warning_installed'] = util.module_installed(cr, 'warning')
    util.remove_module(cr, 'warning')

    # fix missing xmlids for some ir.module.module
    # a module with no xml id base.module_machintruc will likely crash later in the migration process
    cr.execute("""INSERT INTO ir_model_data (noupdate,module,model,res_id,name)
                  (SELECT TRUE,
                          'base',
                          'ir.module.module',
                          m.id,
                          'module_' || m.name
                   FROM ir_module_module m
                   LEFT OUTER JOIN
                     (SELECT *
                      FROM ir_model_data
                      WHERE model='ir.module.module') AS x ON m.id = x.res_id
                   WHERE x.module IS NULL);""")
