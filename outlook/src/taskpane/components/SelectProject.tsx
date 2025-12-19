import { Button, makeStyles } from '@fluentui/react-components'
import React, { useContext } from 'react'
import { _t } from '../../helpers/translate'
import { Project } from '../../models/project'
import CreateProject from './CreateProject'
import ErrorContext from './Error'
import SearchRecords from './SearchRecords'

export interface SelectProjectProps {
    canCreateProject: boolean
    onSelectProject: Function
    pushPage: Function
}

const useStyles = makeStyles({})

const SelectProject: React.FC<SelectProjectProps> = (
    props: SelectProjectProps
) => {
    const { canCreateProject, onSelectProject, pushPage } = props
    const showError = useContext(ErrorContext)?.showError
    const styles = useStyles()

    const [loading, setLoading] = React.useState(true)
    const [noProject, setNoProject] = React.useState(false)
    const [initProjects, setInitProjects] = React.useState(null)

    const searchProject = async (query: string): Promise<Project[]> => {
        const [result, error] = await Project.searchProject(query)
        if (error.code) {
            showError(error.message)
            return []
        }
        return result
    }

    const initSearch = async () => {
        const projects = await searchProject('')
        setNoProject(!projects.length)
        setInitProjects(projects)
        setLoading(false)
    }

    React.useEffect(() => {
        initSearch()
    }, [])

    if (noProject) {
        if (canCreateProject) {
            return <CreateProject onCreate={onSelectProject} />
        }
        return (
            <div>
                <h4>{_t('No project')}</h4>
                <span>
                    {_t(
                        'There are no project in your database. Please ask your project manager to create one.'
                    )}
                </span>
            </div>
        )
    }

    const onShowCreatePage = () => {
        pushPage(
            <CreateProject
                onCreate={(project: Project) => {
                    onSelectProject(project, 2)
                }}
            />
        )
    }

    const createButton = canCreateProject && (
        <Button onClick={onShowCreatePage}>{_t('Create Project')}</Button>
    )

    return (
        <SearchRecords<Project>
            key={loading.toString()}
            bottom={createButton}
            loading={loading}
            onClick={onSelectProject}
            search={searchProject}
            model="project.project"
            searchPlaceholder={_t('Search a Project')}
            records={initProjects || []}
            nameAttribute="name"
            descriptionAttribute="description"
            title={_t('Create a Task in an existing Project')}
        />
    )
}

export default SelectProject
