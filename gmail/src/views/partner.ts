import { buildLeadsView } from "./leads";
import { buildTasksView } from "./tasks";
import { buildTicketsView } from "./tickets";
import { buildPartnerActionView } from "./partner_actions";
import { actionCall, createKeyValueWidget, notify, updateCard } from "./helpers";
import { getOdooServerUrl } from "src/services/app_properties";
import { State } from "../models/state";
import { _t } from "../services/translation";
import { buildCardActionsView } from "./card_actions";
import { Partner } from "src/models/partner";
import { buildView } from "./index";

export function onReloadPartner(state: State) {
    const values = Partner.getPartner(state.partner.name, state.partner.email, state.partner.id);

    [state.partner, state.canCreatePartner, state.canCreateProject] = values;

    if (values[3].code) {
        return notify(values[3].message);
    }

    return updateCard(buildView(state));
}

export function buildPartnerView(state: State, card: Card) {
    card.addCardAction(
        CardService.newCardAction()
            .setText(_t("Refresh"))
            .setOnClickAction(actionCall(state, onReloadPartner.name)),
    );

    buildCardActionsView(card);

    const partner = state.partner;
    const odooServerUrl = getOdooServerUrl();

    const partnerSection = CardService.newCardSection().setHeader(
        "<b>" + _t("Contact Details") + "</b>",
    );

    let partnerContent = [
        partner.parentName && `🏢 ${partner.parentName}`,
        partner.email && `✉️ ${partner.email}`,
        partner.phone && `📞 ${partner.phone}`,
    ]
        .filter((x) => x)
        .map((x) => `<font color="#777777">${x}</font>`)
        .join("<br>");
    if (!partner.id) {
        partnerContent = _t("New Person");
    }

    const partnerCard = createKeyValueWidget(
        null,
        partner.name || partner.email || "",
        partner.getImage(),
        partnerContent.length ? partnerContent : null,
        null,
        null,
        false,
        partner.email,
        CardService.ImageCropType.CIRCLE,
    );

    partnerSection.addWidget(partnerCard);

    buildPartnerActionView(state, partnerSection);

    card.addSection(partnerSection);

    if (State.isLogged) {
        buildLeadsView(state, card);
        buildTicketsView(state, card);
        buildTasksView(state, card);
    }

    return card;
}
