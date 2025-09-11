import { apiClient } from './api-client'
import type { ApiMenuItem } from '../stores/menu-store'

/**
 * 메뉴 API 서비스
 * 백엔드에서 메뉴 데이터를 가져오는 기능을 제공합니다.
 */
export class MenuApiService {
  /**
   * 사용자의 메뉴 목록을 가져옵니다.
   * @returns Promise<ApiMenuItem[]> 메뉴 목록
   */
  static async getMenuItems(): Promise<ApiMenuItem[]> {
    try {
      // 백엔드 /v1/menus/tree 엔드포인트는 MenuTreeNode[] 형식으로 응답
      const response = await apiClient.get('/v1/menus/tree')
      
      // 백엔드 응답을 ApiMenuItem 형식으로 변환
      const menuTreeNodes = response.data
      return this.convertMenuTreeToApiMenuItems(menuTreeNodes)
    } catch (error: any) {
      console.error('메뉴 API 호출 오류:', error)
      
      if (error.response?.status === 401) {
        throw new Error('인증이 필요합니다. 다시 로그인해주세요.')
      } else if (error.response?.status === 403) {
        throw new Error('메뉴에 접근할 권한이 없습니다.')
      } else if (error.response?.status === 404) {
        throw new Error('메뉴 API를 찾을 수 없습니다.')
      } else if (error.response?.status >= 500) {
        throw new Error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
      } else {
        throw new Error(error.message || '메뉴 데이터를 가져오는데 실패했습니다.')
      }
    }
  }

  /**
   * MenuTreeNode를 ApiMenuItem으로 변환합니다.
   * @param menuTreeNodes 백엔드에서 받은 MenuTreeNode 배열
   * @returns ApiMenuItem 배열
   */
  private static convertMenuTreeToApiMenuItems(menuTreeNodes: any[]): ApiMenuItem[] {
    return menuTreeNodes.map(node => this.convertSingleMenuTreeNode(node))
  }

  /**
   * 단일 MenuTreeNode를 ApiMenuItem으로 변환합니다.
   * @param node MenuTreeNode 객체
   * @returns ApiMenuItem 객체
   */
  private static convertSingleMenuTreeNode(node: any): ApiMenuItem {
    return {
      id: parseInt(node.menu_no) || 0,
      name: node.menu_nm || '',
      display_name: node.menu_nm || '',
      path: node.progrm_file_nm || undefined,
      icon: node.relate_image_nm || undefined,
      parent_id: node.upper_menu_no ? parseInt(node.upper_menu_no) : null,
      order: node.menu_ordr ? parseFloat(node.menu_ordr.toString()) : 0,
      is_active: node.display_yn === 'Y',
      required_role: undefined,
      children: node.children ? node.children.map((child: any) => this.convertSingleMenuTreeNode(child)) : undefined
    }
  }

  /**
   * 특정 메뉴의 상세 정보를 가져옵니다.
   * @param menuId 메뉴 ID
   * @returns Promise<ApiMenuItem> 메뉴 상세 정보
   */
  static async getMenuItem(menuId: number): Promise<ApiMenuItem> {
    try {
      const response = await apiClient.get<{
        success: boolean
        data: ApiMenuItem
        message?: string
      }>(`/v1/menu/items/${menuId}`)
      
      if (response.data.success) {
        return response.data.data
      } else {
        throw new Error(response.data.message || '메뉴 정보를 가져오는데 실패했습니다.')
      }
    } catch (error: any) {
      console.error('메뉴 상세 API 호출 오류:', error)
      
      if (error.response?.status === 404) {
        throw new Error('요청한 메뉴를 찾을 수 없습니다.')
      } else {
        throw new Error(error.message || '메뉴 정보를 가져오는데 실패했습니다.')
      }
    }
  }

  /**
   * 사용자 권한에 따른 메뉴 목록을 가져옵니다.
   * @param roleId 역할 ID (선택사항)
   * @returns Promise<ApiMenuItem[]> 권한별 메뉴 목록
   */
  static async getMenuItemsByRole(roleId?: number): Promise<ApiMenuItem[]> {
    try {
      const params = roleId ? { role_id: roleId } : {}
      const response = await apiClient.get<{
        success: boolean
        data: ApiMenuItem[]
        message?: string
      }>('/v1/menu/items/by-role', { params })
      
      if (response.data.success) {
        return response.data.data
      } else {
        throw new Error(response.data.message || '권한별 메뉴 데이터를 가져오는데 실패했습니다.')
      }
    } catch (error: any) {
      console.error('권한별 메뉴 API 호출 오류:', error)
      throw new Error(error.message || '권한별 메뉴 데이터를 가져오는데 실패했습니다.')
    }
  }

  /**
   * 메뉴 트리 구조를 가져옵니다.
   * @returns Promise<ApiMenuItem[]> 계층 구조의 메뉴 목록
   */
  static async getMenuTree(): Promise<ApiMenuItem[]> {
    try {
      const response = await apiClient.get<{
        success: boolean
        data: ApiMenuItem[]
        message?: string
      }>('/v1/menu/tree')
      
      if (response.data.success) {
        return response.data.data
      } else {
        throw new Error(response.data.message || '메뉴 트리를 가져오는데 실패했습니다.')
      }
    } catch (error: any) {
      console.error('메뉴 트리 API 호출 오류:', error)
      throw new Error(error.message || '메뉴 트리를 가져오는데 실패했습니다.')
    }
  }

  /**
   * 메뉴 접근 권한을 확인합니다.
   * @param menuId 메뉴 ID
   * @returns Promise<boolean> 접근 권한 여부
   */
  static async checkMenuAccess(menuId: number): Promise<boolean> {
    try {
      const response = await apiClient.get<{
        success: boolean
        data: { hasAccess: boolean }
        message?: string
      }>(`/v1/menu/items/${menuId}/access`)
      
      if (response.data.success) {
        return response.data.data.hasAccess
      } else {
        return false
      }
    } catch (error: any) {
      console.error('메뉴 접근 권한 확인 오류:', error)
      return false
    }
  }
}

// 기본 내보내기
export default MenuApiService

// 편의를 위한 함수들
export const getMenuItems = MenuApiService.getMenuItems
export const getMenuItem = MenuApiService.getMenuItem
export const getMenuItemsByRole = MenuApiService.getMenuItemsByRole
export const getMenuTree = MenuApiService.getMenuTree
export const checkMenuAccess = MenuApiService.checkMenuAccess