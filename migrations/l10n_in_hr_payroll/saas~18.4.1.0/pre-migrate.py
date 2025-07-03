from odoo.upgrade import util


def migrate(cr, version):
    columns = [
        "l10n_in_residing_child_hostel",
    ]
    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)

    util.rename_field(cr, "l10n.in.tds.computation.wizard", "contract_id", "version_id")
