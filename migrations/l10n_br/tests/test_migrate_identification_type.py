from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class CheckIdentificationType(UpgradeCase):
    def prepare(self):
        Partner = self.env["res.partner"]
        brazil_id = self.env.ref("base.br").id
        return {
            "cpf_no_vat": Partner.create(
                {
                    "name": "cpf_no_vat",
                    "l10n_br_cpf_code": "476.608.398-96",
                    "country_id": brazil_id,
                }
            ).id,
            "no_cpf_vat": Partner.create(
                {
                    "name": "no_cpf_vat",
                    "vat": "57.113.014/0001-39",  # CNPJ
                    "country_id": brazil_id,
                }
            ).id,
            "cpf_vat": Partner.create(
                {
                    "name": "cpf_vat",
                    "vat": "49.823.375/0001-40",  # CNPJ
                    "l10n_br_cpf_code": "363.513.722-75",
                    "country_id": brazil_id,
                }
            ).id,
            "empty_vat_in_br": Partner.create(
                {
                    "name": "empty_vat_in_br",
                    "country_id": brazil_id,
                }
            ).id,
            "vat_outside_br": Partner.create(
                {
                    "name": "vat_outside_br",
                    "vat": "12345",
                }
            ).id,
            "empty_vat_outside_br": Partner.create(
                {
                    "name": "empty_vat_outside_br",
                }
            ).id,
        }

    def check(self, init):
        Partner = self.env["res.partner"]
        cpf_no_vat = Partner.browse(init["cpf_no_vat"])
        self.assertEqual(cpf_no_vat.vat, "476.608.398-96")
        self.assertEqual(cpf_no_vat.l10n_latam_identification_type_id, self.env.ref("l10n_br.cpf"))

        no_cpf_vat = Partner.browse(init["no_cpf_vat"])
        self.assertEqual(no_cpf_vat.vat, "57.113.014/0001-39")
        self.assertEqual(no_cpf_vat.l10n_latam_identification_type_id, self.env.ref("l10n_br.cnpj"))

        # We can't keep both, keep the existing vat field
        cpf_vat = Partner.browse(init["cpf_vat"])
        self.assertEqual(cpf_vat.vat, "49.823.375/0001-40")
        self.assertEqual(cpf_vat.l10n_latam_identification_type_id, self.env.ref("l10n_br.cnpj"))

        # The remaining partners shouldn't have changed (same VAT and the generic l10n_latam_base.it_vat document type)
        empty_vat_in_br = Partner.browse(init["empty_vat_in_br"])
        self.assertEqual(empty_vat_in_br.vat, False)
        self.assertEqual(empty_vat_in_br.l10n_latam_identification_type_id, self.env.ref("l10n_latam_base.it_vat"))

        vat_outside_br = Partner.browse(init["vat_outside_br"])
        self.assertEqual(vat_outside_br.vat, "12345")
        self.assertEqual(vat_outside_br.l10n_latam_identification_type_id, self.env.ref("l10n_latam_base.it_vat"))

        empty_vat_outside_br = Partner.browse(init["empty_vat_outside_br"])
        self.assertEqual(empty_vat_outside_br.vat, False)
        self.assertEqual(empty_vat_outside_br.l10n_latam_identification_type_id, self.env.ref("l10n_latam_base.it_vat"))
