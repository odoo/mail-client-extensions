from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    currencies = """

    AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BIF BMD BND BOB BRL BSD BTN BWP BYR BZD CAD CDF CHF CLP CNY COP CRC CUP CVE CYP CZK DJF DKK DOP DZD ECS EEK EGP ERN ETB EUR FJD FKP GBP GEL GHS GIP GMD GNF GWP GYD HKD HNL HRK HTG HUF IDR ILS INR IQD IRR ISK ITL JMD JOD JPY KES KGS KHR KMF KPW KRW KWD KYD KZT LAK LBP LKR LRD LSL LTL LVL LYD MAD MDL MGA MKD MMK MNT MOP MRO MUR MVR MWK MXN MYR MZN NAD NGN NIO NOK NPR NZD OMR PAB PEN PGK PHP PKR PLN PLZ PYG QAR QTQ ROL RON RSD RUB RUR RWF SAR SBD SCR SDD SEK SGD SHP SIT SKK SLL SOD SRG SSP STD SVC SYP SZL THB TJR TMM TND TOP TPE TRL TRY TTD TWD TZS UAG UAH UGX USD UYP UYU UZS VEF VND VUB VUV WST XAF XCD XOF XPF YER YUM ZAR ZMK ZRZ ZWD

    """.strip().split()

    for c in currencies:
        util.ensure_xmlid_match_record(cr, 'base.%s' % c, 'res.currency', {'name': c, 'company_id': None})

    # ensure shortcuts exists...
    util.ensure_xmlid_match_record(cr, 'base.ir_ui_view_sc_partner0', 'ir.ui.view_sc', {
        'resource': 'ir.ui.menu',
        'res_id': util.ref(cr, 'base.menu_partner_form'),
        'user_id': util.ref(cr, 'base.user_root'),
    })
