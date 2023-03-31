function onSearchPartnerClick(state, parameters, inputs) {
    var inputQuery = inputs.search_partner_query;
    var query = (inputQuery && inputQuery.length && inputQuery[0]) || "";
    var _a = query && query.length ? Partner.searchPartner(query) : [[], new ErrorMessage()],
        partners = _a[0],
        error = _a[1];
    state.searchedPartners = partners;
    return (0, updateCard)(buildSearchPartnerView(state, query));
}
function onLogEmailPartner(state, parameters) {
    var partnerId = parameters.partnerId;
    if (!partnerId) {
        throw new Error((0, _t)("This contact does not exist in the Odoo database."));
    }
    if (State.checkLoggingState(state.email.messageId, "partners", partnerId)) {
        state.error = (0, logEmail)(partnerId, "res.partner", state.email);
        if (!state.error.code) {
            State.setLoggingState(state.email.messageId, "partners", partnerId);
        }
        return (0, updateCard)(buildSearchPartnerView(state, parameters.query));
    }
    return (0, notify)((0, _t)("Email already logged on the contact"));
}
function onOpenPartner(state, parameters) {
    var partner = parameters.partner;
    var _a = Partner.getPartner(partner.email, partner.name, partner.id),
        newPartner = _a[0],
        odooUserCompanies = _a[1],
        canCreatePartner = _a[2],
        canCreateProject = _a[3],
        error = _a[4];
    var newState = new State(
        newPartner,
        canCreatePartner,
        state.email,
        odooUserCompanies,
        null,
        null,
        canCreateProject,
        error,
    );
    return (0, pushCard)((0, buildView)(newState));
}
function buildSearchPartnerView(state, query, initialSearch) {
    if (initialSearch === void 0) {
        initialSearch = false;
    }
    var loggingState = State.getLoggingState(state.email.messageId);
    var card = CardService.newCardBuilder();
    var partners = (state.searchedPartners || []).filter(function (partner) {
        return partner.id;
    });
    var searchValue = query;
    if (initialSearch && partners.length <= 1) {
        partners = [];
        searchValue = "";
    }
    var searchSection = CardService.newCardSection();
    searchSection.addWidget(
        CardService.newTextInput()
            .setFieldName("search_partner_query")
            .setTitle((0, _t)("Search contact"))
            .setValue(searchValue)
            .setOnChangeAction((0, actionCall)(state, "onSearchPartnerClick")),
    );
    searchSection.addWidget(
        CardService.newTextButton()
            .setText((0, _t)("Search"))
            .setOnClickAction((0, actionCall)(state, "onSearchPartnerClick")),
    );
    for (var _i = 0, partners_1 = partners; _i < partners_1.length; _i++) {
        var partner = partners_1[_i];
        var partnerCard = CardService.newDecoratedText()
            .setText(partner.name)
            .setWrapText(true)
            .setOnClickAction((0, actionCall)(state, "onOpenPartner", { partner: partner }))
            .setStartIcon(
                CardService.newIconImage()
                    .setIconUrl(partner.image || (partner.isCompany ? UI_ICONS.no_company : UI_ICONS.person))
                    .setImageCropType(CardService.ImageCropType.CIRCLE),
            );
        if (partner.isWriteable) {
            partnerCard.setButton(
                loggingState["partners"].indexOf(partner.id) < 0
                    ? CardService.newImageButton()
                          .setAltText((0, _t)("Log email"))
                          .setIconUrl(UI_ICONS.email_in_odoo)
                          .setOnClickAction(
                              (0, actionCall)(state, "onLogEmailPartner", {
                                  partnerId: partner.id,
                                  query: query,
                              }),
                          )
                    : CardService.newImageButton()
                          .setAltText((0, _t)("Email already logged on the contact"))
                          .setIconUrl(UI_ICONS.email_logged)
                          .setOnClickAction((0, actionCall)(state, "onEmailAlreadyLogged")),
            );
        }
        if (partner.email) {
            partnerCard.setBottomLabel(partner.email);
        }
        searchSection.addWidget(partnerCard);
    }
    if ((!partners || !partners.length) && !initialSearch) {
        searchSection.addWidget(CardService.newTextParagraph().setText((0, _t)("No contact found.")));
    }
    card.addSection(searchSection);
    return card.build();
}
