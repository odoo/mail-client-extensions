/**
 * Update the application state with the new company created / enriched.
 * IT could be necessary to also update the contact if the contact is the company itself.
 */
function _setContactCompany(state, company, error) {
    if (company) {
        state.partner.company = company;
        if (state.partner.id === company.id) {
            // The contact is the same partner as the company
            // update his information
            state.partner.isCompany = true;
            state.partner.image = company.image;
            state.partner.phone = company.phone;
            state.partner.mobile = company.mobile;
        }
    }
    state.error = error;
    return (0, updateCard)((0, buildView)(state));
}
function onCreateCompany(state) {
    var _a = Partner.createCompany(state.partner.id),
        company = _a[0],
        error = _a[1];
    return _setContactCompany(state, company, error);
}
function onEnrichCompany(state) {
    var _a = Partner.enrichCompany(state.partner.company.id),
        company = _a[0],
        error = _a[1];
    return _setContactCompany(state, company, error);
}
function onUnfoldCompanyDescription(state) {
    state.isCompanyDescriptionUnfolded = true;
    return (0, updateCard)((0, buildView)(state));
}
function buildCompanyView(state, card) {
    if (state.partner.company) {
        var odooServerUrl = State.odooServerUrl;
        var cids = state.odooCompaniesParameter;
        var company = state.partner.company;
        var companySection = CardService.newCardSection().setHeader("<b>" + (0, _t)("Company Insights") + "</b>");
        if (!state.partner.id || state.partner.id !== company.id) {
            var companyContent = [company.email, company.phone]
                .filter(function (x) {
                    return x;
                })
                .map(function (x) {
                    return '<font color="#777777">'.concat(x, "</font>");
                });
            companySection.addWidget(
                (0, createKeyValueWidget)(
                    null,
                    company.name + "<br>" + companyContent.join("<br>"),
                    company.image || UI_ICONS.no_company,
                    null,
                    null,
                    company.id
                        ? odooServerUrl +
                              "/web#id=".concat(company.id, "&model=res.partner&view_type=form").concat(cids)
                        : null,
                    false,
                    company.email,
                    CardService.ImageCropType.CIRCLE,
                ),
            );
        }
        _addSocialButtons(companySection, company);
        if (company.description) {
            var MAX_DESCRIPTION_LENGTH = 70;
            if (company.description.length < MAX_DESCRIPTION_LENGTH || state.isCompanyDescriptionUnfolded) {
                companySection.addWidget((0, createKeyValueWidget)((0, _t)("Description"), company.description));
            } else {
                companySection.addWidget(
                    (0, createKeyValueWidget)(
                        (0, _t)("Description"),
                        company.description.substring(0, MAX_DESCRIPTION_LENGTH) +
                            "..." +
                            "<br/>" +
                            "<font color='#1a73e8'>" +
                            (0, _t)("Read more") +
                            "</font>",
                        null,
                        null,
                        null,
                        (0, actionCall)(state, "onUnfoldCompanyDescription"),
                    ),
                );
            }
        }
        if (company.address) {
            companySection.addWidget(
                (0, createKeyValueWidget)(
                    (0, _t)("Address"),
                    company.address,
                    UI_ICONS.location,
                    null,
                    null,
                    "https://www.google.com/maps/search/" + encodeURIComponent(company.address).replace("/", " "),
                ),
            );
        }
        if (company.phones) {
            companySection.addWidget((0, createKeyValueWidget)((0, _t)("Phones"), company.phones, UI_ICONS.phone));
        }
        if (company.website) {
            companySection.addWidget(
                (0, createKeyValueWidget)(
                    (0, _t)("Website"),
                    company.website,
                    UI_ICONS.website,
                    null,
                    null,
                    company.website,
                ),
            );
        }
        if (company.industry) {
            companySection.addWidget(
                (0, createKeyValueWidget)((0, _t)("Industry"), company.industry, UI_ICONS.industry),
            );
        }
        if (company.employees) {
            companySection.addWidget(
                (0, createKeyValueWidget)(
                    (0, _t)("Employees"),
                    (0, _t)("%s employees", company.employees),
                    UI_ICONS.people,
                ),
            );
        }
        if (company.foundedYear) {
            companySection.addWidget(
                (0, createKeyValueWidget)((0, _t)("Founded Year"), "" + company.foundedYear, UI_ICONS.foundation),
            );
        }
        if (company.tags) {
            companySection.addWidget((0, createKeyValueWidget)((0, _t)("Keywords"), company.tags, UI_ICONS.keywords));
        }
        if (company.companyType) {
            companySection.addWidget(
                (0, createKeyValueWidget)((0, _t)("Company Type"), company.companyType, UI_ICONS.company_type),
            );
        }
        if (company.annualRevenue) {
            companySection.addWidget(
                (0, createKeyValueWidget)((0, _t)("Annual Revenue"), company.annualRevenue, UI_ICONS.money),
            );
        }
        card.addSection(companySection);
        if (!company.isEnriched) {
            var enrichSection = CardService.newCardSection();
            enrichSection.addWidget(CardService.newTextParagraph().setText((0, _t)("No insights for this company.")));
            if (state.error.canCreateCompany && state.canCreatePartner) {
                enrichSection.addWidget(
                    CardService.newTextButton()
                        .setText((0, _t)("Enrich Company"))
                        .setOnClickAction((0, actionCall)(state, "onEnrichCompany")),
                );
            }
            card.addSection(enrichSection);
        }
    } else if (state.partner.id) {
        var companySection = CardService.newCardSection().setHeader("<b>" + (0, _t)("Company Insights") + "</b>");
        companySection.addWidget(
            CardService.newTextParagraph().setText((0, _t)("No company attached to this contact.")),
        );
        if (state.error.canCreateCompany && state.canCreatePartner) {
            companySection.addWidget(
                CardService.newTextButton()
                    .setText((0, _t)("Create a company"))
                    .setOnClickAction((0, actionCall)(state, "onCreateCompany")),
            );
        }
        card.addSection(companySection);
    }
}
function _addSocialButtons(section, company) {
    var socialMediaButtons = CardService.newButtonSet();
    var socialMedias = [
        {
            name: "Facebook",
            url: "https://facebook.com/",
            icon: SOCIAL_MEDIA_ICONS.facebook,
            key: "facebook",
        },
        {
            name: "Twitter",
            url: "https://twitter.com/",
            icon: SOCIAL_MEDIA_ICONS.twitter,
            key: "twitter",
        },
        {
            name: "LinkedIn",
            url: "https://linkedin.com/",
            icon: SOCIAL_MEDIA_ICONS.linkedin,
            key: "linkedin",
        },
        {
            name: "Github",
            url: "https://github.com/",
            icon: SOCIAL_MEDIA_ICONS.github,
            key: "github",
        },
        {
            name: "Crunchbase",
            url: "https://crunchbase.com/",
            icon: SOCIAL_MEDIA_ICONS.crunchbase,
            key: "crunchbase",
        },
    ];
    for (var _i = 0, socialMedias_1 = socialMedias; _i < socialMedias_1.length; _i++) {
        var media = socialMedias_1[_i];
        var url = company[media.key];
        if (url && url.length) {
            socialMediaButtons.addButton(
                CardService.newImageButton()
                    .setAltText(media.name)
                    .setIconUrl(media.icon)
                    .setOpenLink(CardService.newOpenLink().setUrl(media.url + url)),
            );
        }
    }
    section.addWidget(socialMediaButtons);
}
