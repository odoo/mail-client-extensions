import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { Partner } from "../models/partner";
import { ErrorMessage } from "../models/error_message";
import { actionCall, pushCard, updateCard, notify } from "./helpers";
import { buildView } from "./index";
import { State } from "../models/state";
import { UI_ICONS } from "./icons";
import { onEmailAlreadyLoggedContact } from "./partner_actions";
import { buildCardActionsView } from "./card_actions";

function onSearchPartnerClick(state: State, parameters: any, inputs: any) {
    const query = inputs.search_partner_query || "";
    const [partners, error] =
        query && query.length ? Partner.searchPartner(query) : [[], new ErrorMessage()];
    if (error.code) {
        return notify(error.message);
    }

    state.searchedPartners = partners;

    const card = buildSearchPartnerView(state, query);
    return parameters.fixCard ? pushCard(card) : updateCard(card);
}
function onLogEmailPartner(state: State, parameters: any) {
    const partnerId = parameters.partnerId;

    if (!partnerId) {
        throw new Error(_t("This contact does not exist in the Odoo database."));
    }

    if (State.checkLoggingState(state.email.messageId, "res.partner", partnerId)) {
        const error = logEmail(partnerId, "res.partner", state.email);
        if (error.code) {
            return notify(error.message);
        }
        State.setLoggingState(state.email.messageId, "res.partner", partnerId);
        return updateCard(buildSearchPartnerView(state, parameters.query));
    }
    return notify(_t("Email already logged on the contact"));
}

function onOpenPartner(state: State, parameters: any) {
    const partner = Partner.fromJson(parameters.partner);
    const [newPartner, canCreatePartner, canCreateProject, error] = Partner.getPartner(
        partner.name,
        partner.email,
        partner.id,
    );
    if (error.code) {
        return notify(error.message);
    }
    const newState = new State(
        newPartner,
        canCreatePartner,
        state.email,
        null,
        null,
        canCreateProject,
    );
    return pushCard(buildView(newState));
}

export function buildSearchPartnerView(
    state: State,
    query: string,
    initialSearch: boolean = false,
    header: string = "",
    noLogIcon: boolean = false,
    fixCard: boolean = false,
) {
    const loggingState = State.getLoggingState(state.email.messageId);

    const card = CardService.newCardBuilder();
    buildCardActionsView(card);

    let partners = state.searchedPartners || [];
    let searchValue = query;

    if (initialSearch && partners.length <= 1) {
        partners = [];
        searchValue = "";
    }

    const searchSection = CardService.newCardSection();

    searchSection.addWidget(
        CardService.newTextInput()
            .setFieldName("search_partner_query")
            .setTitle(_t("Search contact"))
            .setValue(searchValue)
            .setOnChangeAction(actionCall(state, onSearchPartnerClick.name, { fixCard })),
    );

    searchSection.addWidget(
        CardService.newTextButton()
            .setText(_t("Search"))
            .setOnClickAction(actionCall(state, onSearchPartnerClick.name, { fixCard })),
    );

    if (header?.length) {
        searchSection.addWidget(CardService.newTextParagraph().setText(`<b>${header}</b>`));
    }

    for (let partner of partners) {
        const partnerCard = CardService.newDecoratedText()
            .setText(partner.name)
            .setWrapText(true)
            .setOnClickAction(actionCall(state, onOpenPartner.name, { partner: partner }))
            .setStartIcon(
                CardService.newIconImage()
                    .setIconUrl(partner.getImage())
                    .setImageCropType(CardService.ImageCropType.CIRCLE),
            );

        if (partner.isWritable && !noLogIcon) {
            partnerCard.setButton(
                loggingState["res.partner"].indexOf(partner.id) < 0
                    ? CardService.newImageButton()
                          .setAltText(_t("Log email"))
                          .setIconUrl(UI_ICONS.email_in_odoo)
                          .setOnClickAction(
                              actionCall(state, onLogEmailPartner.name, {
                                  partnerId: partner.id,
                                  query: query,
                              }),
                          )
                    : CardService.newImageButton()
                          .setAltText(_t("Email already logged on the contact"))
                          .setIconUrl(UI_ICONS.email_logged)
                          .setOnClickAction(actionCall(state, onEmailAlreadyLoggedContact.name)),
            );
        }

        if (partner.email) {
            partnerCard.setBottomLabel(partner.id ? partner.email : _t("New Person"));
        }

        searchSection.addWidget(partnerCard);
    }

    if ((!partners || !partners.length) && !initialSearch) {
        const noRecord = Utilities.base64Encode(
            Utilities.newBlob(Utilities.base64Decode(UI_ICONS.no_record))
                .getDataAsString()
                .replace("No record found.", _t("No record found."))
                .replace("Try using different keywords.", _t("Try using different keywords.")),
        );
        searchSection.addWidget(
            CardService.newImage().setImageUrl("data:image/svg+xml;base64," + noRecord),
        );
    }

    card.addSection(searchSection);
    return card.build();
}
