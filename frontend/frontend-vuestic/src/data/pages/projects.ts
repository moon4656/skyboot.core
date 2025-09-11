import api from '../../services/api'
import { Project } from '../../pages/projects/types'
import apiClient from '../../services/api-client'

export type Pagination = {
  page: number
  perPage: number
  total: number
}

export type Sorting = {
  sortBy: 'project_owner' | 'team' | 'created_at'
  sortingOrder: 'asc' | 'desc' | null
}

export const getProjects = async (options: Partial<Sorting> & Pagination) => {
  let projects: Project[] = []
  
  try {
    const response = await apiClient.get('/v1/projects')
    projects = response.data
  } catch (error) {
    console.error('Failed to fetch projects:', error)
    projects = []
  }

  return {
    data: projects,
    pagination: {
      page: options.page,
      perPage: options.perPage,
      total: projects.length,
    },
  }
}

export const addProject = async (project: Omit<Project, 'id' | 'created_at'>) => {
  try {
    const response = await apiClient.post('/v1/projects', project)
    return response.data
  } catch (error) {
    console.error('Failed to add project:', error)
    throw error
  }
}

export const updateProject = async (project: Omit<Project, 'created_at'>) => {
  try {
    const response = await apiClient.put(`/v1/projects/${project.id}`, project)
    return response.data
  } catch (error) {
    console.error('Failed to update project:', error)
    throw error
  }
}

export const removeProject = async (project: Project) => {
  try {
    const response = await apiClient.delete(`/v1/projects/${project.id}`)
    return response.data
  } catch (error) {
    console.error('Failed to remove project:', error)
    throw error
  }
}
