from odoo.upgrade import util


def migrate(cr, version):
    # Return the moves where we deleted the old edi document, so we can recompute the old edi state
    # to avoid the field edi_state to appear when not necessary anymore after upgrade
    query = """
            DELETE FROM account_edi_document aed
                  USING account_edi_format aef
                  WHERE aed.edi_format_id = aef.id
                    AND aef.code = 'fattura_pa'
              RETURNING aed.move_id
        """
    util.recompute_fields(cr, "account.move", ["edi_state"], query=query, strategy="commit")

    util.remove_record(cr, "l10n_it_edi.edi_fatturaPA")
