import { buildView } from "./views/index";
import { Email } from "./models/email";
import { State } from "./models/state";
import { Partner } from "./models/partner";
import { _t } from "./services/translation";
import { buildLoginMainView } from "./views/login";

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
    GmailApp.setCurrentMessageAccessToken(event.messageMetadata.accessToken);
    const currentEmail = new Email(event.gmail.messageId, event.gmail.accessToken);

    let state = null;
    if (currentEmail.contacts.length > 1) {
        // More than one contact, we will need to choose the right one
        const [searchedPartners, error] = Partner.searchPartner(
            currentEmail.contacts.map((c) => c.email),
        );
        if (error.code) {
            return buildLoginMainView();
        }
        const existingPartnersEmails = searchedPartners.map((p) => p.email);

        for (const contact of currentEmail.contacts) {
            if (existingPartnersEmails.includes(contact.email)) {
                continue;
            }
            searchedPartners.push(Partner.fromJson({ name: contact.name, email: contact.email }));
        }

        state = new State(null, false, currentEmail, searchedPartners, null, false);
    } else {
        const [partner, canCreatePartner, canCreateProject, error] = Partner.getPartner(
            currentEmail.contacts[0].name,
            currentEmail.contacts[0].email,
        );
        if (error.code) {
            return buildLoginMainView();
        }

        state = new State(partner, canCreatePartner, currentEmail, null, null, canCreateProject);
    }

    return [buildView(state)];
}
