/**
 * 단일 HTTP 클라이언트 래퍼
 * - 모든 API 호출을 통합 관리
 * - JWT 토큰 자동 처리
 * - 401 오류 시 자동 재시도
 * - 요청/응답 인터셉터
 */
class ApiClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.tokenManager = window.tokenManager;
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        this.retryCount = 1; // 401 오류 시 재시도 횟수
        this.isRefreshing = false; // 토큰 갱신 중 플래그
        this.failedQueue = []; // 토큰 갱신 중 대기 중인 요청들
        
        // 기본 인터셉터 설정
        this.setupDefaultInterceptors();
        
        // 토큰 매니저에 갱신 콜백 설정
        this.tokenManager.setRefreshCallback(this.refreshToken.bind(this));
    }

    /**
     * 기본 인터셉터 설정
     */
    setupDefaultInterceptors() {
        // 요청 인터셉터: 인증 헤더 추가
        this.addRequestInterceptor((config) => {
            const token = this.tokenManager.getAccessToken();
            if (token) {
                config.headers = config.headers || {};
                config.headers['Authorization'] = `Bearer ${token}`;
            }
            return config;
        });

        // 응답 인터셉터: 401 오류 처리
        this.addResponseInterceptor(
            (response) => response, // 성공 응답은 그대로 반환
            async (error) => {
                const originalRequest = error.config;
                
                if (error.status === 401 && !originalRequest._retry) {
                    return this.handle401Error(originalRequest);
                }
                
                throw error;
            }
        );
    }

    /**
     * 요청 인터셉터 추가
     * @param {Function} interceptor - 요청을 수정하는 함수
     */
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }

    /**
     * 응답 인터셉터 추가
     * @param {Function} onSuccess - 성공 응답 처리 함수
     * @param {Function} onError - 오류 응답 처리 함수
     */
    addResponseInterceptor(onSuccess, onError) {
        this.responseInterceptors.push({ onSuccess, onError });
    }

    /**
     * HTTP 요청 실행
     * @param {Object} config - 요청 설정
     * @returns {Promise<Object>}
     */
    async request(config) {
        const startTime = Date.now();
        
        try {
            // 요청 인터셉터 적용
            let processedConfig = await this.applyRequestInterceptors(config);
            
            // 실제 HTTP 요청
            const response = await this.executeRequest(processedConfig);
            
            // 응답 인터셉터 적용
            const processedResponse = await this.applyResponseInterceptors(response);
            
            // 성공 로그
            this.logRequest(processedConfig, processedResponse, Date.now() - startTime, 'success');
            
            return processedResponse;
            
        } catch (error) {
            // 오류 로그
            this.logRequest(config, error, Date.now() - startTime, 'error');
            
            // 응답 인터셉터의 오류 처리 적용
            for (const interceptor of this.responseInterceptors) {
                if (interceptor.onError) {
                    try {
                        return await interceptor.onError(error);
                    } catch (interceptorError) {
                        // 인터셉터에서 처리하지 못한 경우 계속 진행
                        continue;
                    }
                }
            }
            
            throw error;
        }
    }

    /**
     * 요청 인터셉터 적용
     * @param {Object} config - 요청 설정
     * @returns {Object}
     */
    async applyRequestInterceptors(config) {
        let processedConfig = { ...config };
        
        for (const interceptor of this.requestInterceptors) {
            processedConfig = await interceptor(processedConfig);
        }
        
        return processedConfig;
    }

    /**
     * 응답 인터셉터 적용
     * @param {Object} response - 응답 객체
     * @returns {Object}
     */
    async applyResponseInterceptors(response) {
        let processedResponse = response;
        
        for (const interceptor of this.responseInterceptors) {
            if (interceptor.onSuccess) {
                processedResponse = await interceptor.onSuccess(processedResponse);
            }
        }
        
        return processedResponse;
    }

    /**
     * 실제 HTTP 요청 실행
     * @param {Object} config - 요청 설정
     * @returns {Promise<Object>}
     */
    async executeRequest(config) {
        const url = config.url.startsWith('http') ? config.url : `${this.baseURL}${config.url}`;
        
        const fetchConfig = {
            method: config.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...config.headers
            }
        };

        // 요청 본문 추가
        if (config.data && ['POST', 'PUT', 'PATCH'].includes(fetchConfig.method)) {
            fetchConfig.body = typeof config.data === 'string' ? config.data : JSON.stringify(config.data);
        }

        const response = await fetch(url, fetchConfig);
        
        // 응답 데이터 파싱
        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        // 응답 객체 구성
        const result = {
            data,
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            config
        };

        // 오류 상태 체크
        if (!response.ok) {
            const error = new Error(`HTTP Error: ${response.status} ${response.statusText}`);
            error.response = result;
            error.status = response.status;
            error.config = config;
            throw error;
        }

        return result;
    }

    /**
     * 401 오류 처리
     * @param {Object} originalRequest - 원본 요청
     * @returns {Promise<Object>}
     */
    async handle401Error(originalRequest) {
        if (this.isRefreshing) {
            // 이미 토큰 갱신 중이면 대기열에 추가
            return new Promise((resolve, reject) => {
                this.failedQueue.push({ resolve, reject, request: originalRequest });
            });
        }

        originalRequest._retry = true;
        this.isRefreshing = true;

        try {
            // 토큰 갱신 시도
            const refreshSuccess = await this.tokenManager.refreshTokens();
            
            if (refreshSuccess) {
                // 대기 중인 요청들 처리
                this.processFailedQueue(null);
                
                // 원본 요청 재시도
                return this.request(originalRequest);
            } else {
                // 토큰 갱신 실패
                const error = new Error('토큰 갱신 실패');
                this.processFailedQueue(error);
                throw error;
            }
        } catch (error) {
            this.processFailedQueue(error);
            throw error;
        } finally {
            this.isRefreshing = false;
        }
    }

    /**
     * 대기 중인 요청들 처리
     * @param {Error|null} error - 오류 객체 (성공 시 null)
     */
    processFailedQueue(error) {
        this.failedQueue.forEach(({ resolve, reject, request }) => {
            if (error) {
                reject(error);
            } else {
                resolve(this.request(request));
            }
        });
        
        this.failedQueue = [];
    }

    /**
     * 토큰 갱신
     * @param {string} refreshToken - 리프레시 토큰
     * @returns {Promise<Object>}
     */
    async refreshToken(refreshToken) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    success: true,
                    accessToken: data.access_token,
                    refreshToken: data.refresh_token,
                    expiresIn: 3600 // 기본값
                };
            } else {
                const errorData = await response.json();
                return {
                    success: false,
                    error: errorData.detail || '토큰 갱신 실패'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * GET 요청
     * @param {string} url - 요청 URL
     * @param {Object} config - 추가 설정
     * @returns {Promise<Object>}
     */
    async get(url, config = {}) {
        return this.request({
            method: 'GET',
            url,
            ...config
        });
    }

    /**
     * POST 요청
     * @param {string} url - 요청 URL
     * @param {Object} data - 요청 데이터
     * @param {Object} config - 추가 설정
     * @returns {Promise<Object>}
     */
    async post(url, data, config = {}) {
        return this.request({
            method: 'POST',
            url,
            data,
            ...config
        });
    }

    /**
     * PUT 요청
     * @param {string} url - 요청 URL
     * @param {Object} data - 요청 데이터
     * @param {Object} config - 추가 설정
     * @returns {Promise<Object>}
     */
    async put(url, data, config = {}) {
        return this.request({
            method: 'PUT',
            url,
            data,
            ...config
        });
    }

    /**
     * DELETE 요청
     * @param {string} url - 요청 URL
     * @param {Object} config - 추가 설정
     * @returns {Promise<Object>}
     */
    async delete(url, config = {}) {
        return this.request({
            method: 'DELETE',
            url,
            ...config
        });
    }

    /**
     * 요청 로깅
     * @param {Object} config - 요청 설정
     * @param {Object} response - 응답 또는 오류
     * @param {number} duration - 요청 시간 (ms)
     * @param {string} type - 로그 타입 ('success' | 'error')
     */
    logRequest(config, response, duration, type) {
        const logData = {
            method: config.method || 'GET',
            url: config.url,
            status: response.status || (response.response ? response.response.status : 'ERROR'),
            duration: `${duration}ms`,
            timestamp: new Date().toISOString()
        };

        console.log(`[ApiClient] ${type.toUpperCase()}:`, logData);
        
        // UI 로그에 추가
        if (window.apiLogger) {
            window.apiLogger.addLog(
                config.method || 'GET',
                config.url,
                type,
                logData.status,
                duration
            );
        }
    }

    /**
     * 로그인
     * @param {string} userId - 사용자 ID
     * @param {string} password - 비밀번호
     * @returns {Promise<Object>}
     */
    async login(userId, password) {
        const response = await this.post('/api/v1/auth/login', {
            user_id: userId,
            password: password
        });

        if (response.data.access_token) {
            this.tokenManager.setTokens(
                response.data.access_token,
                response.data.refresh_token,
                3600 // 1시간
            );
        }

        return response;
    }

    /**
     * 로그아웃
     */
    logout() {
        this.tokenManager.clearTokens();
        console.log('[ApiClient] 로그아웃 완료');
    }
}

// 전역 API 클라이언트 인스턴스
window.apiClient = new ApiClient();