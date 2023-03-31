function onLogEmail(state) {
    var partnerId = state.partner.id;
    if (!partnerId) {
        throw new Error((0, _t)("This contact does not exist in the Odoo database."));
    }
    if (State.checkLoggingState(state.email.messageId, "partners", partnerId)) {
        state.error = (0, logEmail)(partnerId, "res.partner", state.email);
        if (!state.error.code) {
            State.setLoggingState(state.email.messageId, "partners", partnerId);
        }
        return (0, updateCard)((0, buildView)(state));
    }
    return (0, notify)((0, _t)("Email already logged on the contact"));
}
function onSavePartner(state) {
    var partnerValues = {
        name: state.partner.name,
        email: state.partner.email,
        company: state.partner.company && state.partner.company.id,
    };
    var partnerId = Partner.savePartner(partnerValues);
    if (partnerId) {
        state.partner.id = partnerId;
        state.searchedPartners = null;
        state.error = new ErrorMessage();
        return (0, updateCard)((0, buildView)(state));
    } else {
        return (0, notify)((0, _t)("Can not save the contact"));
    }
}
function onEmailAlreadyLogged(state) {
    return (0, notify)((0, _t)("Email already logged on the contact"));
}
function buildPartnerView(state, card) {
    var partner = state.partner;
    var odooServerUrl = State.odooServerUrl;
    var canContactOdooDatabase = state.error.canContactOdooDatabase && State.isLogged;
    var loggingState = State.getLoggingState(state.email.messageId);
    var isEmailLogged = partner.id && loggingState["partners"].indexOf(partner.id) >= 0;
    var partnerSection = CardService.newCardSection().setHeader("<b>" + (0, _t)("Contact") + "</b>");
    var partnerButton = null;
    if (canContactOdooDatabase && !partner.id) {
        partnerButton = state.canCreatePartner
            ? CardService.newImageButton()
                  .setAltText((0, _t)("Save in Odoo"))
                  .setIconUrl(UI_ICONS.save_in_odoo)
                  .setOnClickAction((0, actionCall)(state, "onSavePartner"))
            : null;
    } else if (canContactOdooDatabase && !isEmailLogged) {
        partnerButton = partner.isWriteable
            ? CardService.newImageButton()
                  .setAltText((0, _t)("Log email"))
                  .setIconUrl(UI_ICONS.email_in_odoo)
                  .setOnClickAction((0, actionCall)(state, "onLogEmail"))
            : null;
    } else if (canContactOdooDatabase && isEmailLogged) {
        partnerButton = CardService.newImageButton()
            .setAltText((0, _t)("Email already logged on the contact"))
            .setIconUrl(UI_ICONS.email_logged)
            .setOnClickAction((0, actionCall)(state, "onEmailAlreadyLogged"));
    } else if (!State.isLogged) {
        // button "Log the email" but it redirects to the login page
        partnerButton = CardService.newImageButton()
            .setAltText((0, _t)("Log email"))
            .setIconUrl(UI_ICONS.email_in_odoo)
            .setOnClickAction((0, actionCall)(state, "buildLoginMainView"));
    }
    var partnerContent = [partner.email, partner.phone]
        .filter(function (x) {
            return x;
        })
        .map(function (x) {
            return '<font color="#777777">'.concat(x, "</font>");
        });
    var cids = state.odooCompaniesParameter;
    var partnerCard = (0, createKeyValueWidget)(
        null,
        partner.name + "<br>" + partnerContent.join("<br>"),
        partner.image || (partner.isCompany ? UI_ICONS.no_company : UI_ICONS.person),
        null,
        partnerButton,
        partner.id
            ? odooServerUrl + "/web#id=".concat(partner.id, "&model=res.partner&view_type=form").concat(cids)
            : canContactOdooDatabase
            ? null
            : (0, actionCall)(state, "buildLoginMainView"),
        false,
        partner.email,
        CardService.ImageCropType.CIRCLE,
    );
    partnerSection.addWidget(partnerCard);
    (0, buildPartnerActionView)(state, partnerSection);
    card.addSection(partnerSection);
    if (canContactOdooDatabase) {
        (0, buildLeadsView)(state, card);
        (0, buildTicketsView)(state, card);
        (0, buildTasksView)(state, card);
    }
    return card;
}
