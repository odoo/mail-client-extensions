function onNextLogin(event) {
    var validatedUrl = (0, format_1.formatUrl)(event.formInput.odooServerUrl);
    if (!validatedUrl) {
        return (0, helpers_1.notify)("Invalid URL");
    }
    if (!/^https:\/\/([^\/?]*\.)?odoo\.com(\/|$)/.test(validatedUrl)) {
        return (0, helpers_1.notify)("The URL must be a subdomain of odoo.com");
    }
    (0, translation_1.clearTranslationCache)();
    State.odooServerUrl = validatedUrl;
    if (!(0, odoo_auth_1.isOdooDatabaseReachable)(validatedUrl)) {
        return (0, helpers_1.notify)(
            "Could not connect to your database. Make sure the module is installed in Odoo (Settings > General Settings > Integrations > Mail Plugins)",
        );
    }
    return CardService.newActionResponseBuilder()
        .setOpenLink(
            CardService.newOpenLink()
                .setUrl(State.odooLoginUrl)
                .setOpenAs(CardService.OpenAs.OVERLAY)
                .setOnClose(CardService.OnClose.RELOAD_ADD_ON),
        )
        .build();
}
function buildLoginMainView() {
    var card = CardService.newCardBuilder();
    // Trick to make large centered button
    var invisibleChar = "⠀";
    var faqUrl = "https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html";
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
                    .setValue(State.odooServerUrl || ""),
            )
            .addWidget(
                CardService.newTextButton()
                    .setText(
                        (0, format_1.repeat)(invisibleChar, 12) + "Login" + (0, format_1.repeat)(invisibleChar, 12),
                    )
                    .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
                    .setBackgroundColor("#00A09D")
                    .setOnClickAction(CardService.newAction().setFunctionName("onNextLogin")),
            )
            .addWidget(CardService.newTextParagraph().setText((0, format_1.repeat)(invisibleChar, 13) + "<b>OR</b>"))
            .addWidget(
                CardService.newTextButton()
                    .setText(
                        (0, format_1.repeat)(invisibleChar, 11) + " Sign Up" + (0, format_1.repeat)(invisibleChar, 11),
                    )
                    .setOpenLink(
                        CardService.newOpenLink().setUrl(
                            "https://www.odoo.com/trial?selected_app=mail_plugin:crm:helpdesk:project",
                        ),
                    ),
            )
            .addWidget(
                (0, helpers_1.createKeyValueWidget)(
                    null,
                    "Create leads from emails sent to your email address.",
                    IMAGES_LOGIN.email,
                ),
            )
            .addWidget(
                (0, helpers_1.createKeyValueWidget)(
                    null,
                    "Create tickets from emails sent to your email address.",
                    IMAGES_LOGIN.ticket,
                ),
            )
            .addWidget(
                (0, helpers_1.createKeyValueWidget)(null, "Centralize Prospects' emails into CRM.", IMAGES_LOGIN.crm),
            )
            .addWidget(
                (0, helpers_1.createKeyValueWidget)(
                    null,
                    "Generate Tasks from emails sent to your email address in any Odoo project.",
                    IMAGES_LOGIN.project,
                ),
            )
            .addWidget(
                (0, helpers_1.createKeyValueWidget)(
                    null,
                    "Search and store insights on your contacts.",
                    IMAGES_LOGIN.search,
                ),
            )
            .addWidget(
                CardService.newTextParagraph().setText(
                    (0, format_1.repeat)(invisibleChar, 13) + '<a href="'.concat(faqUrl, '">FAQ</a>'),
                ),
            ),
    );
    return card.build();
}
