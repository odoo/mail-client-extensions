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
    var currentEmail = new Email(event.gmail.messageId, event.gmail.accessToken);
    var _a = Partner.enrichPartner(currentEmail.contactEmail, currentEmail.contactName),
        partner = _a[0],
        odooUserCompanies = _a[1],
        canCreatePartner = _a[2],
        canCreateProject = _a[3],
        error = _a[4];
    if (!partner) {
        // Should at least use the FROM headers to generate the partner
        throw new Error((0, _t)("Error during enrichment"));
    }
    var state = new State(
        partner,
        canCreatePartner,
        currentEmail,
        odooUserCompanies,
        null,
        null,
        canCreateProject,
        error,
    );
    return [(0, buildView)(state)];
}
