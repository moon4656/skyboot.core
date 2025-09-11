import { User } from '../../pages/users/types'
import api from '../../services/api'
import apiClient from '../../services/api-client'

export type Pagination = {
  page: number
  perPage: number
  total: number
}

export type Sorting = {
  sortBy: keyof User | undefined
  sortingOrder: 'asc' | 'desc' | null
}

export type Filters = {
  isActive: boolean
  search: string
}

export const getUsers = async (filters: Partial<Filters & Pagination & Sorting>) => {
  const { isActive, search } = filters
  let filteredUsers: User[] = []
  
  try {
    const response = await apiClient.get('/v1/users')
    filteredUsers = response.data
  } catch (error) {
    console.error('Failed to fetch users:', error)
    // 빈 배열 반환하여 UI가 깨지지 않도록 함
    filteredUsers = []
  }

  filteredUsers = filteredUsers.filter((user) => user.active === isActive)

  if (search) {
    filteredUsers = filteredUsers.filter((user) => user.fullname.toLowerCase().includes(search.toLowerCase()))
  }

  const { page = 1, perPage = 10 } = filters || {}
  return {
    data: filteredUsers,
    pagination: {
      page,
      perPage,
      total: filteredUsers.length,
    },
  }
}

export const addUser = async (user: User) => {
  try {
    const response = await apiClient.post('/v1/users', user)
    return response.data
  } catch (error) {
    console.error('Failed to add user:', error)
    throw error
  }
}

export const updateUser = async (user: User) => {
  try {
    const response = await apiClient.put(`/v1/users/${user.id}`, user)
    return response.data
  } catch (error) {
    console.error('Failed to update user:', error)
    throw error
  }
}

export const removeUser = async (user: User) => {
  try {
    const response = await apiClient.delete(`/v1/users/${user.id}`)
    return response.data
  } catch (error) {
    console.error('Failed to remove user:', error)
    throw error
  }
}

export const uploadAvatar = async (body: FormData) => {
  try {
    const response = await apiClient.post('/v1/avatars', body)
    return response.data
  } catch (error) {
    console.error('Failed to upload avatar:', error)
    throw error
  }
}
