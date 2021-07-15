import { buildView } from "./index";
import { updateCard, actionCall } from "./helpers";
import { SOCIAL_MEDIA_ICONS, UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify } from "./helpers";
import { URLS } from "../const";
import { ErrorMessage } from "../models/error_message";
import { State } from "../models/state";
import { Company } from "../models/company";
import { Partner } from "../models/partner";
import { _t } from "../services/translation";

/**
 * Update the application state with the new company created / enriched.
 * IT could be necessary to also update the contact if the contact is the company itself.
 */
function _setContactCompany(state: State, company: Company, error: ErrorMessage) {
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
    return updateCard(buildView(state));
}

function onCreateCompany(state: State) {
    const [company, error] = Partner.createCompany(state.partner.id);
    return _setContactCompany(state, company, error);
}

function onEnrichCompany(state: State) {
    const [company, error] = Partner.enrichCompany(state.partner.company.id);
    return _setContactCompany(state, company, error);
}

function onUnfoldCompanyDescription(state: State) {
    state.isCompanyDescriptionUnfolded = true;
    return updateCard(buildView(state));
}

export function buildCompanyView(state: State, card: Card) {
    if (state.partner.company) {
        const odooServerUrl = State.odooServerUrl;
        const cids = state.odooCompaniesParameter;
        const company = state.partner.company;

        const companySection = CardService.newCardSection().setHeader("<b>" + _t("Company Insights") + "</b>");

        if (!state.partner.id || state.partner.id !== company.id) {
            const companyContent = [company.email, company.phone]
                .filter((x) => x)
                .map((x) => `<font color="#777777">${x}</font>`);

            companySection.addWidget(
                createKeyValueWidget(
                    null,
                    company.name + "<br>" + companyContent.join("<br>"),
                    company.image || UI_ICONS.no_company,
                    null,
                    null,
                    company.id ? odooServerUrl + `/web#id=${company.id}&model=res.partner&view_type=form${cids}` : null,
                    false,
                    company.email,
                    CardService.ImageCropType.CIRCLE,
                ),
            );
        }

        _addSocialButtons(companySection, company);

        if (company.description) {
            const MAX_DESCRIPTION_LENGTH = 70;
            if (company.description.length < MAX_DESCRIPTION_LENGTH || state.isCompanyDescriptionUnfolded) {
                companySection.addWidget(createKeyValueWidget(_t("Description"), company.description));
            } else {
                companySection.addWidget(
                    createKeyValueWidget(
                        _t("Description"),
                        company.description.substring(0, MAX_DESCRIPTION_LENGTH) +
                            "..." +
                            "<br/>" +
                            "<font color='#1a73e8'>" +
                            _t("Read more") +
                            "</font>",
                        null,
                        null,
                        null,
                        actionCall(state, "onUnfoldCompanyDescription"),
                    ),
                );
            }
        }

        if (company.address) {
            companySection.addWidget(
                createKeyValueWidget(
                    _t("Address"),
                    company.address,
                    UI_ICONS.location,
                    null,
                    null,
                    "https://www.google.com/maps/search/" + encodeURIComponent(company.address).replace("/", " "),
                ),
            );
        }

        if (company.phones) {
            companySection.addWidget(createKeyValueWidget(_t("Phones"), company.phones, UI_ICONS.phone));
        }

        if (company.website) {
            companySection.addWidget(
                createKeyValueWidget(_t("Website"), company.website, UI_ICONS.website, null, null, company.website),
            );
        }

        if (company.industry) {
            companySection.addWidget(createKeyValueWidget(_t("Industry"), company.industry, UI_ICONS.industry));
        }

        if (company.employees) {
            companySection.addWidget(
                createKeyValueWidget(_t("Employees"), _t("%s employees", company.employees), UI_ICONS.people),
            );
        }

        if (company.foundedYear) {
            companySection.addWidget(
                createKeyValueWidget(_t("Founded Year"), "" + company.foundedYear, UI_ICONS.foundation),
            );
        }

        if (company.tags) {
            companySection.addWidget(createKeyValueWidget(_t("Keywords"), company.tags, UI_ICONS.keywords));
        }

        if (company.companyType) {
            companySection.addWidget(
                createKeyValueWidget(_t("Company Type"), company.companyType, UI_ICONS.company_type),
            );
        }

        if (company.annualRevenue) {
            companySection.addWidget(createKeyValueWidget(_t("Annual Revenue"), company.annualRevenue, UI_ICONS.money));
        }

        card.addSection(companySection);

        if (!company.isEnriched) {
            const enrichSection = CardService.newCardSection();
            enrichSection.addWidget(CardService.newTextParagraph().setText(_t("No insights for this company.")));
            if (state.error.canCreateCompany) {
                enrichSection.addWidget(
                    CardService.newTextButton()
                        .setText(_t("Enrich Company"))
                        .setOnClickAction(actionCall(state, "onEnrichCompany")),
                );
            }
            card.addSection(enrichSection);
        }
    } else if (state.partner.id) {
        const companySection = CardService.newCardSection().setHeader("<b>" + _t("Company Insights") + "</b>");
        companySection.addWidget(CardService.newTextParagraph().setText(_t("No company attached to this contact.")));

        if (state.error.canCreateCompany) {
            companySection.addWidget(
                CardService.newTextButton()
                    .setText(_t("Create a company"))
                    .setOnClickAction(actionCall(state, "onCreateCompany")),
            );
        }
        card.addSection(companySection);
    }
}

function _addSocialButtons(section: CardSection, company: Company) {
    const socialMediaButtons = CardService.newButtonSet();

    const socialMedias = [
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

    for (let media of socialMedias) {
        const url = company[media.key];
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
