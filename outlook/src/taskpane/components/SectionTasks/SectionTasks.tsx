import * as React from 'react';
import Partner from '../../../classes/Partner';
import Project from '../../../classes/Project';
import Task from '../../../classes/Task';
import { _t } from '../../../utils/Translator';
import Section from '../Section/Section';
import api from '../../api';
import AppContext from '../AppContext';
import { Callout, DirectionalHint } from 'office-ui-fabric-react';
import SelectProjectDropdown from './SelectProjectDropdown';

type SectionTasksProps = {
    partner: Partner;
    canCreatePartner: boolean;
    canCreateProject: boolean;
};

type SectionTasksState = {
    tasks: Task[];
    isCollapsed: boolean;
    isProjectCalloutOpen: boolean;
    createCallback?: (any?) => {};
};

class SectionTasks extends React.Component<SectionTasksProps, SectionTasksState> {
    constructor(props, context) {
        super(props, context);
        const isCollapsed = !props.partner.tasks || !props.partner.tasks.length;
        this.state = {
            tasks: this.props.partner.tasks,
            isCollapsed: isCollapsed,
            isProjectCalloutOpen: false,
        };
    }

    private toggleProjectCallout = (callback) => {
        this.setState({
            isProjectCalloutOpen: !this.state.isProjectCalloutOpen,
            createCallback: callback,
        });
    };

    private onProjectSelected = (project: Project) => {
        this.setState({ isProjectCalloutOpen: false });
        this.state.createCallback({ project_id: project.id });
    };

    render() {
        return (
            <>
                <Section
                    className="collapse-task-section"
                    records={this.state.tasks}
                    partner={this.props.partner}
                    canCreatePartner={this.props.canCreatePartner}
                    model="project.task"
                    odooEndpointCreateRecord={api.createTask}
                    odooRecordIdName="task_id"
                    odooRedirectAction="project_mail_plugin.project_task_action_form_edit"
                    title="Tasks"
                    titleCount="Tasks (%(count)s)"
                    msgNoPartner="Save Contact to create new Tasks."
                    msgNoPartnerNoAccess="The Contact needs to exist to create Task."
                    msgNoRecord="No tasks found for this contact."
                    msgLogEmail="Log Email Into Task"
                    getRecordDescription={(task) => task.projectName}
                    onClickCreate={this.toggleProjectCallout}
                />
                {this.state.isProjectCalloutOpen && (
                    <Callout
                        directionalHint={DirectionalHint.bottomRightEdge}
                        directionalHintFixed={true}
                        onDismiss={() => this.setState({ isProjectCalloutOpen: false })}
                        preventDismissOnScroll={true}
                        setInitialFocus={true}
                        doNotLayer={true}
                        gapSpace={0}
                        role="alertdialog"
                        target=".collapse-task-section .collapse-section-button">
                        <SelectProjectDropdown
                            partner={this.props.partner}
                            canCreateProject={this.props.canCreateProject}
                            onProjectClick={this.onProjectSelected}
                        />
                    </Callout>
                )}
            </>
        );
    }
}

SectionTasks.contextType = AppContext;
export default SectionTasks;
