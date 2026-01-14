import { formatUrl, repeat } from "../utils/format";
import { notify, createKeyValueWidget } from "./helpers";
import { State } from "../models/state";
import { IMAGES_LOGIN } from "./icons";
import { getSupportedAddinVersion } from "../services/odoo_auth";
import { _t, clearTranslationCache } from "../services/translation";
import { setOdooServerUrl } from "src/services/app_properties";

function onNextLogin(event) {
    const validatedUrl = formatUrl(event.formInput.odooServerUrl);

    if (!validatedUrl) {
        return notify("Invalid URL");
    }

    if (!/^https:\/\/([^\/?]*\.)?odoo\.com(\/|$)/.test(validatedUrl)) {
        return notify("The URL must be a subdomain of odoo.com");
    }

    clearTranslationCache();

    setOdooServerUrl(validatedUrl);

    const version = getSupportedAddinVersion(validatedUrl);

    if (!version) {
        return notify(
            "Could not connect to your database. Make sure the module is installed in Odoo (Settings > General Settings > Integrations > Mail Plugins)",
        );
    }

    if (version !== 1) {
        return notify(
            "Oops, this addin is no longer compatible with your version of Odoo. Please install a newer version.",
        );
    }

    return CardService.newActionResponseBuilder()
        .setOpenLink(
            CardService.newOpenLink()
                .setUrl(State.odooLoginUrl)
                .setOpenAs(CardService.OpenAs.OVERLAY)
                .setOnClose(CardService.OnClose.RELOAD),
        )
        .build();
}

export function buildLoginMainView() {
    const card = CardService.newCardBuilder();

    // Trick to make large centered button
    const invisibleChar = "⠀";

    const faqUrl = "https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html";

    card.addSection(
        CardService.newCardSection()
            .addWidget(
                CardService.newImage().setAltText("Connect to your Odoo database").setImageUrl(IMAGES_LOGIN.main_image),
            )
            .addWidget(
                CardService.newTextInput()
                    .setFieldName("odooServerUrl")
                    .setTitle("Database URL")
                    .setHint("e.g. company.odoo.com")
                    .setValue(PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") || ""),
            )
            .addWidget(
                CardService.newTextButton()
                    .setText(repeat(invisibleChar, 12) + "Login" + repeat(invisibleChar, 12))
                    .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
                    .setBackgroundColor("#00A09D")
                    .setOnClickAction(CardService.newAction().setFunctionName(onNextLogin.name)),
            )
            .addWidget(CardService.newTextParagraph().setText(repeat(invisibleChar, 13) + "<b>OR</b>"))
            .addWidget(
                CardService.newTextButton()
                    .setText(repeat(invisibleChar, 11) + " Sign Up" + repeat(invisibleChar, 11))
                    .setOpenLink(
                        CardService.newOpenLink().setUrl(
                            "https://www.odoo.com/trial?selected_app=mail_plugin:crm:helpdesk:project",
                        ),
                    ),
            )
            .addWidget(
                createKeyValueWidget(null, "Create leads from emails sent to your email address.", IMAGES_LOGIN.email),
            )
            .addWidget(
                createKeyValueWidget(
                    null,
                    "Create tickets from emails sent to your email address.",
                    IMAGES_LOGIN.ticket,
                ),
            )
            .addWidget(createKeyValueWidget(null, "Centralize Prospects' emails into CRM.", IMAGES_LOGIN.crm))
            .addWidget(
                createKeyValueWidget(
                    null,
                    "Generate Tasks from emails sent to your email address in any Odoo project.",
                    IMAGES_LOGIN.project,
                ),
            )
            .addWidget(createKeyValueWidget(null, "Search and store insights on your contacts.", IMAGES_LOGIN.search))
            .addWidget(
                CardService.newTextParagraph().setText(repeat(invisibleChar, 13) + `<a href="${faqUrl}">FAQ</a>`),
            ),
    );

    return card.build();
}
