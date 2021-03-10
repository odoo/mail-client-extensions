import { logEmail } from "../services/log_email";
import { Partner } from "../models/partner";
import { ErrorMessage } from "../models/error_message";
import { createKeyValueWidget, actionCall, pushCard, updateCard, notify } from "./helpers";
import { buildView } from "./index";
import { State } from "../models/state";
import { SOCIAL_MEDIA_ICONS, UI_ICONS } from "./icons";

function onSearchPartnerClick(state: State, parameters: any, inputs: any) {
    const inputQuery = inputs.search_partner_query;
    const query = (inputQuery && inputQuery.length && inputQuery[0]) || "";
    const [partners, error] = query && query.length ? Partner.searchPartner(query) : [[], new ErrorMessage()];

    state.searchedPartners = partners;

    return updateCard(buildSearchPartnerView(state, query));
}
function onLogEmailPartner(state: State, parameters: any) {
    const emailBody = state.email.body;
    const partnerId = parameters.partnerId;

    if (!partnerId) {
        throw new Error("This contact does not exist in the Odoo database.");
    }

    if (State.setLoggingState(state.email.messageId, "partners", partnerId)) {
        logEmail(partnerId, "res.partner", emailBody);
        return updateCard(buildSearchPartnerView(state, parameters.query));
    }
    return notify("Email already logged on the contact");
}

function onOpenPartner(state: State, parameters: any) {
    const partner = parameters.partner;
    const [newPartner, error] = Partner.getPartner(partner.email, partner.name, partner.id);
    const newState = new State(newPartner, state.email, null, error);
    return pushCard(buildView(newState));
}

export function buildSearchPartnerView(state: State, query: string, initialSearch: boolean = false) {
    const loggingState = State.getLoggingState(state.email.messageId);

    const card = CardService.newCardBuilder();
    let partners = (state.searchedPartners || []).filter((partner) => partner.id);
    let searchValue = query;

    if (initialSearch && partners.length <= 1) {
        partners = [];
        searchValue = "";
    }

    const searchSection = CardService.newCardSection();

    searchSection.addWidget(
        CardService.newTextInput()
            .setFieldName("search_partner_query")
            .setTitle("Search contact")
            .setValue(searchValue)
            .setOnChangeAction(actionCall(state, "onSearchPartnerClick")),
    );

    searchSection.addWidget(
        CardService.newTextButton().setText("Search").setOnClickAction(actionCall(state, "onSearchPartnerClick")),
    );

    for (let partner of partners) {
        const partnerCard = CardService.newDecoratedText()
            .setTopLabel(partner.name)
            .setText(partner.email)
            .setWrapText(true)
            .setOnClickAction(actionCall(state, "onOpenPartner", { partner: partner }))
            .setButton(
                loggingState["partners"].indexOf(partner.id) < 0
                    ? CardService.newImageButton()
                          .setAltText("Log email")
                          .setIconUrl(UI_ICONS.email_in_odoo)
                          .setOnClickAction(
                              actionCall(state, "onLogEmailPartner", {
                                  partnerId: partner.id,
                                  query: query,
                              }),
                          )
                    : CardService.newImageButton()
                          .setAltText("Email already logged")
                          .setIconUrl(UI_ICONS.email_logged)
                          .setOnClickAction(actionCall(state, "onEmailAlreadyLogged")),
            );
        if (partner.image) {
            partnerCard.setIconUrl(partner.image);
        }
        searchSection.addWidget(partnerCard);
    }

    if ((!partners || !partners.length) && !initialSearch) {
        searchSection.addWidget(CardService.newTextParagraph().setText("No contact found."));
    }

    card.addSection(searchSection);
    return card.build();
}
