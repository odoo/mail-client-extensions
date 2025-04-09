from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_work_entry.l10n_ch_swissdec_unpaid_wt", util.update_record_from_xml)
