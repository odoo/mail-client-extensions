import { Spinner, SpinnerSize, TextField } from 'office-ui-fabric-react';
import * as React from 'react';
import Partner from '../../../classes/Partner';
import Project from '../../../classes/Project';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../utils/httpRequest';
import { OdooTheme } from '../../../utils/Themes';
import { _t } from '../../../utils/Translator';
import api from '../../api';
import './SelectProjectDropdown.css';
import AppContext from '../AppContext';

type SelectProjectProps = {
    partner: Partner;
    canCreateProject: boolean;
    onProjectClick: (project: Project) => void;
};

type SelectProjectState = {
    query: string;
    isLoading: boolean;
    projects: Project[];
};

class SelectProjectDropdown extends React.Component<SelectProjectProps, SelectProjectState> {
    constructor(props, context) {
        super(props, context);
        this.state = { query: '', isLoading: false, projects: [] };
    }

    private projectsRequest;

    private onQueryChanged = (event) => {
        const query = event.target.value;
        this.setState({ query: query });
        this.cancelProjectsRequest();
        if (query.length > 0) {
            this.getProjectsRequest(query);
        } else {
            this.setState({ isLoading: false, projects: [] });
        }
    };

    private cancelProjectsRequest = () => {
        if (this.projectsRequest) this.projectsRequest.cancel();
    };

    private getProjectsRequest = async (searchTerm: string) => {
        if (!searchTerm || !searchTerm.length) {
            return;
        }

        this.setState({ isLoading: true });

        this.projectsRequest = sendHttpRequest(
            HttpVerb.POST,
            api.baseURL + api.searchProject,
            ContentType.Json,
            this.context.getConnectionToken(),
            { search_term: searchTerm },
            true,
        );

        this.context.addRequestCanceller(this.projectsRequest.cancel);

        let response = null;
        try {
            response = JSON.parse(await this.projectsRequest.promise);
        } catch (error) {
            if (error) {
                this.setState({ isLoading: false, projects: [] });
                this.context.showHttpErrorMessage(error);
            }
            return;
        }
        const projects = response.result.map((project_json) => Project.fromJson(project_json));
        this.setState({ projects: projects, isLoading: false });
    };

    private createProject = async () => {
        const createProjectRequest = sendHttpRequest(
            HttpVerb.POST,
            api.baseURL + api.createProject,
            ContentType.Json,
            this.context.getConnectionToken(),
            { name: this.state.query },
            true,
        );

        this.setState({ isLoading: true });

        let response = null;
        try {
            response = JSON.parse(await createProjectRequest.promise);
        } catch (error) {
            if (error) {
                this.setState({ isLoading: false, projects: [] });
                this.context.showHttpErrorMessage(error);
                this.setState({ isLoading: false });
            }
            return;
        }

        const createdProject = Project.fromJson(response.result);
        this.props.onProjectClick(createdProject);
    };

    private getProjects = () => {
        const searchedTermExists = this.state.projects.filter(
            (p) => p.name.toUpperCase() === this.state.query.toUpperCase(),
        ).length;

        const allowCreateNewProject = this.props.canCreateProject && !!this.state.query.length && !searchedTermExists;

        return (
            <div>
                {this.state.projects.map((project) => (
                    <div
                        key={project.id}
                        className="project-search-result-text"
                        onClick={() => this.props.onProjectClick(project)}>
                        {project.name}
                    </div>
                ))}
                {allowCreateNewProject && (
                    <div className="create-project-text" onClick={this.createProject}>
                        {_t('Create %(name)s', { name: this.state.query })}
                    </div>
                )}
                {this.state.query.length && !allowCreateNewProject && !this.state.projects.length ? (
                    <div>{_t('No Project Found')}</div>
                ) : null}
                {this.state.isLoading && (
                    <Spinner theme={OdooTheme} size={SpinnerSize.large} className="project-result-spinner" />
                )}
            </div>
        );
    };

    render() {
        return (
            <div className="project-result-container">
                <div>{_t('Pick a Project to create a Task')}</div>
                <div className="project-search-bar">
                    <TextField
                        className="input-search"
                        placeholder={_t('Search Projects...')}
                        onChange={this.onQueryChanged}
                        value={this.state.query}
                        autoComplete="off"
                        onFocus={(e) => e.target.select()}
                    />
                </div>
                {this.getProjects()}
            </div>
        );
    }
}

SelectProjectDropdown.contextType = AppContext;
export default SelectProjectDropdown;
