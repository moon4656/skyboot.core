/**
 * JWT 토큰 관리 클래스
 * - Access Token과 Refresh Token 관리
 * - 토큰 만료 시간 추적
 * - 자동 토큰 갱신
 */
class TokenManager {
    constructor() {
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenExpiry = null;
        this.refreshCallback = null;
        
        // 로컬 스토리지에서 토큰 복원
        this.loadTokensFromStorage();
        
        // 토큰 만료 체크 타이머 시작
        this.startTokenExpiryCheck();
    }

    /**
     * 토큰 설정
     * @param {string} accessToken - 액세스 토큰
     * @param {string} refreshToken - 리프레시 토큰
     * @param {number} expiresIn - 만료 시간 (초)
     */
    setTokens(accessToken, refreshToken, expiresIn = 3600) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.tokenExpiry = new Date(Date.now() + (expiresIn * 1000));
        
        // 로컬 스토리지에 저장
        this.saveTokensToStorage();
        
        this.logTokenStatus('토큰 설정 완료');
    }

    /**
     * 액세스 토큰 반환
     * @returns {string|null}
     */
    getAccessToken() {
        if (this.isTokenExpired()) {
            this.logTokenStatus('토큰 만료됨');
            return null;
        }
        return this.accessToken;
    }

    /**
     * 리프레시 토큰 반환
     * @returns {string|null}
     */
    getRefreshToken() {
        return this.refreshToken;
    }

    /**
     * 토큰 만료 여부 확인
     * @returns {boolean}
     */
    isTokenExpired() {
        if (!this.tokenExpiry || !this.accessToken) {
            return true;
        }
        
        // 만료 5분 전을 만료로 간주 (여유시간)
        const bufferTime = 5 * 60 * 1000; // 5분
        return Date.now() >= (this.tokenExpiry.getTime() - bufferTime);
    }

    /**
     * 토큰 유효성 확인
     * @returns {boolean}
     */
    hasValidToken() {
        return this.accessToken && !this.isTokenExpired();
    }

    /**
     * 토큰 갱신 필요 여부 확인
     * @returns {boolean}
     */
    needsRefresh() {
        return this.refreshToken && this.isTokenExpired();
    }

    /**
     * 토큰 갱신 콜백 설정
     * @param {Function} callback - 토큰 갱신 함수
     */
    setRefreshCallback(callback) {
        this.refreshCallback = callback;
    }

    /**
     * 토큰 갱신 시도
     * @returns {Promise<boolean>}
     */
    async refreshTokens() {
        if (!this.refreshCallback || !this.refreshToken) {
            this.logTokenStatus('토큰 갱신 불가능 - 콜백 또는 리프레시 토큰 없음');
            return false;
        }

        try {
            this.logTokenStatus('토큰 갱신 시도 중...');
            const result = await this.refreshCallback(this.refreshToken);
            
            if (result.success) {
                this.setTokens(
                    result.accessToken, 
                    result.refreshToken || this.refreshToken,
                    result.expiresIn
                );
                this.logTokenStatus('토큰 갱신 성공');
                return true;
            } else {
                this.logTokenStatus('토큰 갱신 실패: ' + result.error);
                this.clearTokens();
                return false;
            }
        } catch (error) {
            this.logTokenStatus('토큰 갱신 오류: ' + error.message);
            this.clearTokens();
            return false;
        }
    }

    /**
     * 토큰 삭제
     */
    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenExpiry = null;
        
        // 로컬 스토리지에서 삭제
        localStorage.removeItem('skyboot_access_token');
        localStorage.removeItem('skyboot_refresh_token');
        localStorage.removeItem('skyboot_token_expiry');
        
        this.logTokenStatus('토큰 삭제됨');
    }

    /**
     * 로컬 스토리지에서 토큰 로드
     */
    loadTokensFromStorage() {
        try {
            this.accessToken = localStorage.getItem('skyboot_access_token');
            this.refreshToken = localStorage.getItem('skyboot_refresh_token');
            
            const expiryStr = localStorage.getItem('skyboot_token_expiry');
            if (expiryStr) {
                this.tokenExpiry = new Date(expiryStr);
            }
            
            if (this.accessToken) {
                this.logTokenStatus('로컬 스토리지에서 토큰 복원됨');
            }
        } catch (error) {
            console.error('토큰 로드 오류:', error);
            this.clearTokens();
        }
    }

    /**
     * 로컬 스토리지에 토큰 저장
     */
    saveTokensToStorage() {
        try {
            if (this.accessToken) {
                localStorage.setItem('skyboot_access_token', this.accessToken);
            }
            if (this.refreshToken) {
                localStorage.setItem('skyboot_refresh_token', this.refreshToken);
            }
            if (this.tokenExpiry) {
                localStorage.setItem('skyboot_token_expiry', this.tokenExpiry.toISOString());
            }
        } catch (error) {
            console.error('토큰 저장 오류:', error);
        }
    }

    /**
     * 토큰 만료 체크 타이머 시작
     */
    startTokenExpiryCheck() {
        // 1분마다 토큰 상태 체크
        setInterval(() => {
            this.updateTokenStatus();
        }, 60000);
        
        // 초기 상태 업데이트
        this.updateTokenStatus();
    }

    /**
     * 토큰 상태 업데이트
     */
    updateTokenStatus() {
        const statusElement = document.getElementById('tokenStatus');
        if (!statusElement) return;

        if (!this.accessToken) {
            statusElement.textContent = '토큰 없음';
            statusElement.className = 'token-status';
        } else if (this.isTokenExpired()) {
            statusElement.textContent = '토큰 만료됨';
            statusElement.className = 'token-status expired';
        } else {
            const remainingTime = Math.floor((this.tokenExpiry.getTime() - Date.now()) / 1000 / 60);
            statusElement.textContent = `토큰 활성 (${remainingTime}분 남음)`;
            statusElement.className = 'token-status active';
        }
    }

    /**
     * 토큰 상태 로깅
     * @param {string} message - 로그 메시지
     */
    logTokenStatus(message) {
        console.log(`[TokenManager] ${message}`);
        
        // UI 상태 업데이트
        this.updateTokenStatus();
        
        // 로그에 추가
        if (window.apiLogger) {
            window.apiLogger.addLog('TOKEN', message, 'info');
        }
    }

    /**
     * 토큰 정보 반환 (디버깅용)
     * @returns {Object}
     */
    getTokenInfo() {
        return {
            hasAccessToken: !!this.accessToken,
            hasRefreshToken: !!this.refreshToken,
            isExpired: this.isTokenExpired(),
            expiryTime: this.tokenExpiry,
            remainingMinutes: this.tokenExpiry ? 
                Math.floor((this.tokenExpiry.getTime() - Date.now()) / 1000 / 60) : 0
        };
    }
}

// 전역 토큰 매니저 인스턴스
window.tokenManager = new TokenManager();