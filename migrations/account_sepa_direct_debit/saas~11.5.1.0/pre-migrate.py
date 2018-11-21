# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_batch_payment", "sdd_required_collection_date", "date")
    util.remove_record(cr, "account_sepa_direct_debit.action_sepa_direct_debit_xml_archive_tree_act")
    util.remove_record(cr, "account_sepa_direct_debit.action_sdd_account_payment_generate_xml")

    util.remove_model(cr, "sdd.xml.archive")
    util.remove_model(cr, "sdd.generate.xml.wizard")
    util.remove_model(cr, "sdd.download.xml.wizard")
