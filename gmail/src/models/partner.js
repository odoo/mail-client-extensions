/**
 * Represent the current partner and all the information about him.
 */
var Partner = /** @class */ (function () {
    function Partner() {}
    /**
     * Unserialize the partner object (reverse JSON.stringify).
     */
    Partner.fromJson = function (values) {
        var partner = new Partner();
        partner.id = values.id;
        partner.name = values.name;
        partner.email = values.email;
        partner.image = values.image;
        partner.isCompany = values.isCompany;
        partner.phone = values.phone;
        partner.mobile = values.mobile;
        partner.company = values.company ? Company.fromJson(values.company) : null;
        partner.isWriteable = values.isWriteable;
        partner.leads = values.leads
            ? values.leads.map(function (leadValues) {
                  return Lead.fromJson(leadValues);
              })
            : null;
        partner.tickets = values.tickets
            ? values.tickets.map(function (ticketValues) {
                  return Ticket.fromJson(ticketValues);
              })
            : null;
        partner.tasks = values.tasks
            ? values.tasks.map(function (taskValues) {
                  return Task.fromJson(taskValues);
              })
            : null;
        return partner;
    };
    Partner.fromOdooResponse = function (values) {
        var partner = new Partner();
        if (values.id && values.id > 0) {
            partner.id = values.id;
        }
        partner.name = values.name;
        partner.email = values.email;
        partner.image = values.image ? "data:image/png;base64," + values.image : null;
        partner.isCompany = values.is_company;
        partner.phone = values.phone;
        partner.mobile = values.mobile;
        // Undefined should be considered as True for retro-compatibility
        partner.isWriteable = values.can_write_on_partner !== false;
        if (values.company && values.company.id && values.company.id > 0) {
            partner.company = Company.fromOdooResponse(values.company);
        }
        return partner;
    };
    /**
     * Try to find information about the given email /name.
     *
     * If we are not logged to an Odoo database, enrich the email domain with IAP.
     * Otherwise fetch the partner on the user database.
     *
     * See `getPartner`
     */
    Partner.enrichPartner = function (email, name) {
        var odooServerUrl = State.odooServerUrl;
        var odooAccessToken = State.accessToken;
        if (odooServerUrl && odooAccessToken) {
            return this.getPartner(email, name);
        } else {
            var _a = this._enrichFromIap(email, name),
                partner = _a[0],
                error = _a[1];
            return [partner, null, false, false, error];
        }
    };
    /**
     * Extract the email domain and send a request to IAP
     * to find information about the company.
     */
    Partner._enrichFromIap = function (email, name) {
        var odooSharedSecret = State.odooSharedSecret;
        var userEmail = Session.getEffectiveUser().getEmail();
        var senderDomain = email.split("@").pop();
        var response = (0, postJsonRpcCached)(URLS.IAP_COMPANY_ENRICHMENT, {
            email: userEmail,
            domain: senderDomain,
            secret: odooSharedSecret,
        });
        var error = new ErrorMessage();
        if (!response) {
            error.setError("http_error_iap");
        } else if (response.error && response.error.length) {
            error.setError(response.error);
        }
        var partner = new Partner();
        partner.name = name;
        partner.email = email;
        if (response && response.name) {
            partner.company = Company.fromIapResponse(response);
        }
        return [partner, error];
    };
    /**
     * Create a "res.partner" with the given values in the Odoo database.
     */
    Partner.savePartner = function (partnerValues) {
        var url = State.odooServerUrl + URLS.PARTNER_CREATE;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(url, partnerValues, {
            Authorization: "Bearer " + accessToken,
        });
        return response && response.id;
    };
    /**
     * Fetch the given partner on the Odoo database and return all information about him.
     *
     * Return
     *      - The Partner related to the given email address
     *      - The list of Odoo companies in which the current user belongs
     *      - True if the current user can create partner in his Odoo database
     *      - True if the current user can create projects in his Odoo database
     *      - The error message if something bad happened
     */
    Partner.getPartner = function (email, name, partnerId) {
        if (partnerId === void 0) {
            partnerId = null;
        }
        var url = State.odooServerUrl + URLS.GET_PARTNER;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(
            url,
            { email: email, name: name, partner_id: partnerId },
            { Authorization: "Bearer " + accessToken },
        );
        if (!response || !response.partner) {
            var error = new ErrorMessage("http_error_odoo");
            var partner = Partner.fromJson({ name: name, email: email });
            return [partner, null, false, false, error];
        }
        var error = new ErrorMessage();
        if (response.enrichment_info && response.enrichment_info.type) {
            error.setError(response.enrichment_info.type, response.enrichment_info.info);
        } else if (response.partner.enrichment_info && response.partner.enrichment_info.type) {
            error.setError(response.partner.enrichment_info.type, response.partner.enrichment_info.info);
        }
        var partner = Partner.fromOdooResponse(response.partner);
        // Parse leads
        if (response.leads) {
            partner.leads = response.leads.map(function (leadValues) {
                return Lead.fromOdooResponse(leadValues);
            });
        }
        // Parse tickets
        if (response.tickets) {
            partner.tickets = response.tickets.map(function (ticketValues) {
                return Ticket.fromOdooResponse(ticketValues);
            });
        }
        // Parse tasks
        if (response.tasks) {
            partner.tasks = response.tasks.map(function (taskValues) {
                return Task.fromOdooResponse(taskValues);
            });
        }
        var canCreateProject = response.can_create_project !== false;
        var odooUserCompanies = response.user_companies || null;
        // undefined must be considered as true
        var canCreatePartner = response.can_create_partner !== false;
        return [partner, odooUserCompanies, canCreatePartner, canCreateProject, error];
    };
    /**
     * Perform a search on the Odoo database and return the list of matched partners.
     */
    Partner.searchPartner = function (query) {
        var url = State.odooServerUrl + URLS.SEARCH_PARTNER;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(url, { search_term: query }, { Authorization: "Bearer " + accessToken });
        if (!response || !response.partners) {
            return [[], new ErrorMessage("http_error_odoo")];
        }
        return [
            response.partners.map(function (values) {
                return Partner.fromOdooResponse(values);
            }),
            new ErrorMessage(),
        ];
    };
    /**
     * Create and enrich the company of the given partner.
     */
    Partner.createCompany = function (partnerId) {
        return this._enrichOrCreateCompany(partnerId, URLS.CREATE_COMPANY);
    };
    /**
     * Enrich the existing company.
     */
    Partner.enrichCompany = function (companyId) {
        return this._enrichOrCreateCompany(companyId, URLS.ENRICH_COMPANY);
    };
    Partner._enrichOrCreateCompany = function (partnerId, endpoint) {
        var url = State.odooServerUrl + endpoint;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(url, { partner_id: partnerId }, { Authorization: "Bearer " + accessToken });
        if (!response) {
            return [null, new ErrorMessage("http_error_odoo")];
        }
        if (response.error) {
            return [null, new ErrorMessage("odoo", response.error)];
        }
        var error = new ErrorMessage();
        if (response.enrichment_info && response.enrichment_info.type) {
            error.setError(response.enrichment_info.type, response.enrichment_info.info);
        }
        if (error.code) {
            error.canCreateCompany = false;
        }
        var company = response.company ? Company.fromOdooResponse(response.company) : null;
        return [company, error];
    };
    return Partner;
})();
