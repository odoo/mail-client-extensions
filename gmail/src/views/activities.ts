import { Activity } from "../models/activity";
import { buildCardActionsView } from "./card_actions";
import { createKeyValueWidget, actionCall, notify, updateCard } from "./helpers";
import { _t } from "../services/translation";
import { getOdooRecordURL } from "src/services/odoo_redirection";
import { UI_ICONS } from "./icons";

function onDone(parameters: any) {
    const ok = Activity.fromJson(parameters.activity).markDone();
    if (!ok) {
        return notify(_t("Could not mark the activity as done."));
    }
    return updateActivityCard(parameters);
}

function onEdit(parameters: any) {
    return buildActivityEditView(Activity.fromJson(parameters.activity), parameters.sectionIndex);
}

function onCancel(parameters: any) {
    const ok = Activity.fromJson(parameters.activity).markCancel();
    if (!ok) {
        return notify(_t("Could not cancel the activity."));
    }
    return updateActivityCard(parameters);
}

function onSubmit(parameters: any, inputs: any) {
    const activitiesGroups = Activity.fromJson(parameters.activity).edit(
        inputs.summary,
        inputs.date_deadline.msSinceEpoch,
    );
    if (!activitiesGroups) {
        return notify(_t("Could not edit the activity."));
    }
    return updateCard(buildActivitiesView(activitiesGroups, parameters.sectionIndex));
}

function updateActivityCard(parameters: any) {
    const activitiesGroups = parameters.activitiesGroups
        .map((v) => [
            v[0],
            v[1]
                .map((values) => Activity.fromJson(values))
                .filter((activity) => activity.id !== parameters?.activity?.id),
        ])
        .filter((v) => v[1].length);
    return updateCard(buildActivitiesView(activitiesGroups, parameters.sectionIndex));
}

function onSectionChange(parameters: any, inputs: any) {
    parameters.sectionIndex = parseInt(inputs.section_index);
    return updateActivityCard(parameters);
}

export function buildActivitiesView(
    activitiesGroups: [string, Activity[]][],
    sectionIndex: number = 1,
) {
    const card = CardService.newCardBuilder();
    const [title, activities] = activitiesGroups[sectionIndex];

    buildCardActionsView(card);
    const section = CardService.newCardSection().setHeader(`<b>${_t("Activities")}</b>`);

    const options = CardService.newSelectionInput()
        .setType(CardService.SelectionInputType.DROPDOWN)
        .setFieldName("section_index")
        .setOnChangeAction(actionCall(null, onSectionChange.name, { activitiesGroups }));

    let i = 0;
    for (const [title, _] of activitiesGroups) {
        options.addItem(title, i, i === sectionIndex);
        i++;
    }
    section.addWidget(options);

    for (const activity of activities) {
        let recordButton = null;

        if (activity.resId && activity.resModel) {
            const link = getOdooRecordURL(activity.resModel, activity.resId);
            recordButton = CardService.newImageButton()
                .setAltText(_t("Open the record"))
                .setIconUrl(UI_ICONS.link)
                .setOpenLink(CardService.newOpenLink().setUrl(link));
        }

        section.addWidget(
            createKeyValueWidget(
                activity.resName,
                activity.summary,
                null,
                activity.dateDeadlineStr,
                recordButton,
            ),
        );

        const buttonSet = CardService.newButtonSet();
        buttonSet
            .addButton(
                CardService.newTextButton()
                    .setText(_t("Done"))
                    .setOnClickAction(
                        actionCall(null, onDone.name, { activity, activitiesGroups, sectionIndex }),
                    )
                    .setBackgroundColor("#875a7b"),
            )
            .addButton(
                CardService.newTextButton().setText(_t("Cancel")).setOnClickAction(
                    actionCall(null, onCancel.name, {
                        activity,
                        activitiesGroups,
                        sectionIndex,
                    }),
                ),
            )
            .addButton(
                CardService.newTextButton()
                    .setText(_t("Edit"))
                    .setOnClickAction(
                        actionCall(null, onEdit.name, { activity, activitiesGroups, sectionIndex }),
                    ),
            );
        section.addWidget(buttonSet);
    }

    card.addSection(section);
    return card.build();
}

export function buildActivityEditView(activity: Activity, sectionIndex: number) {
    const card = CardService.newCardBuilder();

    buildCardActionsView(card);
    const section = CardService.newCardSection().setHeader(`<b>${_t("Activity")}</b>`);

    section.addWidget(
        CardService.newTextInput()
            .setFieldName("summary")
            .setTitle(_t("Summary"))
            .setValue(activity.summary),
    );

    section.addWidget(
        CardService.newDatePicker()
            .setTitle(_t("Date Deadline"))
            .setFieldName("date_deadline")
            .setValueInMsSinceEpoch(activity.dateDeadlineTimestamp * 1000),
    );

    section.addWidget(
        CardService.newTextButton()
            .setText(_t("Edit"))
            .setOnClickAction(actionCall(null, onSubmit.name, { activity, sectionIndex })),
    );

    card.addSection(section);
    return card.build();
}
