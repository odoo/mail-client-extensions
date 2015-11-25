# -*- coding: utf-8 -*-


def migrate(cr, version):

    cr.execute("""ALTER TABLE account_tax
        DROP CONSTRAINT account_tax_name_company_uniq
        """)

    mapping_table = [
        ('TVA 21% - Services', '21% Services'),
        ('TVA 21%', '21%'),
        ('TVA 12% - Services', '12% Services'),
        ('TVA 12%', '12%'),
        ('TVA 6% - Services', '6% Services'),
        ('TVA 6%', '6%'),
        ('TVA 0% - Services', '0% Services'),
        ('TVA 0%', '0%'),
        ('TVA 0% Cocontractant', '0% Cocontractant'),
        ('TVA services EU', '0% EU Services'),
        ('TVA Marchandises EU (Code L)', '0% EU L'),
        ('TVA marchandises EU (Code T)', '0% EU T'),
        ('TVA export hors EU', '0% Export Non EU'),
        ('TVA Déductible 21% - Approvisionn. et marchandises', '21% Marchandises'),
        ('TVA Déductible 12% - Approvisionn. et marchandises', '12% Marchandises'),
        ('TVA Déductible 6% - Approvisionn. et marchandises', '6% Marchandises'),
        ('TVA à l\'entrée 0% - Approvisionn. et marchandises', '0% Marchandises'),
        ('TVA Déductible 21% - Services', '21% Services'),
        ('TVA Déductible 12% - Services', '12% Services'),
        ('TVA Déductible 6% - Services', '6% Services'),
        ('TVA à l\'entrée 0% - Services', '0% Services'),
        ('TVA Déductible 21% - Biens divers', '21% Biens divers'),
        ('TVA Déductible 12% - Biens divers', '12% Biens divers'),
        ('TVA Déductible 6% - Biens divers', '6% Biens divers'),
        ('TVA à l\'entrée 0% - Biens divers', '0% Biens divers'),
        ('TVA Déductible 21% - Biens d\'investissement', '21% Biens d\'investissement'),
        ('TVA Déductible 12% - Biens d\'investissement', '12% Biens d\'investissement'),
        ('TVA Déductible 6% - Biens d\'investissement', '6% Biens d\'investissement'),
        ('TVA à l\'entrée 0% - Biens d\'investissement', '0% Biens d\'investissement'),
        ('TVA Déductible 21% Cocontract. - Approvisionn. et marchandises', '21% Cocontract. - Approvisionn. et marchandises'),
        ('TVA Déductible 12% Cocontract. - Approvisionn. et marchandises', '12% Cocontract. - Approvisionn. et marchandises'),
        ('TVA Déductible 0% Cocontract. - Approvisionn. et marchandises', '0% Cocontract. - Approvisionn. et marchandises'),
        ('TVA entrante - Frais de voiture - TVA 50% Non Déductible (Prix Excl.)', 'TVA Entrant - Frais de voiture - VAT 50% Non Deductible (Price Excl.)'),
        ('TVA entrante - Frais de voiture - TVA 50% Non Deductible (Price Incl.)', 'TVA Entrant - Frais de voiture - VAT 50% Non Deductible (Price Incl.)'),
        ('TVA à l\'entrée 0% Hors EU - Biens d\'investissement', '0% Non EU - Biens d\'investissement'),
    ]

    for entry in mapping_table:
        cr.execute("""UPDATE account_tax
            SET name = %s
            WHERE name = %s
            """, (entry[1], entry[0]))
