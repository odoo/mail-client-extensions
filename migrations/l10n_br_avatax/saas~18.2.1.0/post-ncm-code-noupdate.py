def migrate(cr, version):
    cr.execute(
        "UPDATE ir_model_data SET noupdate = True WHERE module = 'l10n_br_avatax' AND model = 'l10n_br.ncm.code'"
    )
