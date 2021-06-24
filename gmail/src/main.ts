import { buildView } from "./views/index";
import { Email } from "./models/email";
import { State } from "./models/state";
import { Partner } from "./models/partner";
import { _t } from "../services/translation";

/**
 * Entry point of the application, executed when an email is open.
 *
 * If the user is not connected to a Odoo database, we will contact IAP and enrich the
 * domain of the op penned email.
 *
 * If the user is connected to a Odoo database, we will fetch the corresponding partner
 * and other information like his leads, tickets, company...
 */
function onGmailMessageOpen(event) {
    GmailApp.setCurrentMessageAccessToken(event.gmail.accessToken);
    const currentEmail = new Email(event.gmail.messageId);
    const [partner, odooUserCompanies, error] = Partner.enrichPartner(
        currentEmail.contactEmail,
        currentEmail.contactName,
    );

    if (!partner) {
        // Should at least use the FROM headers to generate the partner
        throw new Error(_t("Error during enrichment"));
    }

    const state = new State(partner, currentEmail, odooUserCompanies, null, null, error);

    return [buildView(state)];
}
