/**
 * SkyBoot Core API - 메인 애플리케이션
 * - UI 이벤트 처리
 * - API 테스트 인터페이스
 * - 로깅 시스템
 */

/**
 * API 로거 클래스
 */
class ApiLogger {
    constructor() {
        this.logs = [];
        this.maxLogs = 100;
    }

    /**
     * 로그 추가
     * @param {string} method - HTTP 메서드
     * @param {string} url - 요청 URL
     * @param {string} type - 로그 타입 ('success' | 'error' | 'retry' | 'info')
     * @param {string} status - 응답 상태
     * @param {number} duration - 요청 시간 (ms)
     */
    addLog(method, url, type, status = '', duration = 0) {
        const log = {
            id: Date.now() + Math.random(),
            timestamp: new Date(),
            method,
            url,
            type,
            status,
            duration
        };

        this.logs.unshift(log);
        
        // 최대 로그 수 제한
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(0, this.maxLogs);
        }

        this.renderLogs();
    }

    /**
     * 로그 렌더링
     */
    renderLogs() {
        const logsContainer = document.getElementById('requestLogs');
        if (!logsContainer) return;

        if (this.logs.length === 0) {
            logsContainer.innerHTML = '<p style="text-align: center; color: #718096; padding: 20px;">아직 요청 로그가 없습니다.</p>';
            return;
        }

        const logsHtml = this.logs.map(log => {
            const timeStr = log.timestamp.toLocaleTimeString();
            const durationStr = log.duration ? ` (${log.duration}ms)` : '';
            
            return `
                <div class="log-entry ${log.type}">
                    <div class="log-timestamp">${timeStr}</div>
                    <div class="log-details">
                        <span class="log-method">${log.method}</span>
                        <span class="log-url">${log.url}</span>
                        ${log.status ? `<span class="log-status ${log.type}">${log.status}</span>` : ''}
                        <span class="log-duration">${durationStr}</span>
                    </div>
                </div>
            `;
        }).join('');

        logsContainer.innerHTML = logsHtml;
    }

    /**
     * 로그 지우기
     */
    clearLogs() {
        this.logs = [];
        this.renderLogs();
    }
}

/**
 * 메인 애플리케이션 클래스
 */
class SkyBootApp {
    constructor() {
        this.apiClient = window.apiClient;
        this.tokenManager = window.tokenManager;
        this.logger = new ApiLogger();
        
        // 전역 로거 설정
        window.apiLogger = this.logger;
        
        this.initializeEventListeners();
        this.updateUI();
        
        console.log('🚀 SkyBoot Core API 클라이언트 초기화 완료');
    }

    /**
     * 이벤트 리스너 초기화
     */
    initializeEventListeners() {
        // 로그인 버튼
        document.getElementById('loginBtn').addEventListener('click', () => {
            this.handleLogin();
        });

        // 로그아웃 버튼
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.handleLogout();
        });

        // API 요청 버튼
        document.getElementById('sendRequestBtn').addEventListener('click', () => {
            this.handleApiRequest();
        });

        // 로그 지우기 버튼
        document.getElementById('clearLogsBtn').addEventListener('click', () => {
            this.logger.clearLogs();
        });

        // Enter 키 처리
        document.getElementById('userId').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });

        document.getElementById('password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });

        document.getElementById('apiUrl').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleApiRequest();
        });

        // API 메서드 변경 시 요청 본문 표시/숨김
        document.getElementById('apiMethod').addEventListener('change', (e) => {
            const requestBodyContainer = document.querySelector('.request-body');
            const showBody = ['POST', 'PUT', 'PATCH'].includes(e.target.value);
            requestBodyContainer.style.display = showBody ? 'block' : 'none';
        });

        // 토큰 상태 변경 감지
        setInterval(() => {
            this.updateUI();
        }, 1000);
    }

    /**
     * 로그인 처리
     */
    async handleLogin() {
        const userId = document.getElementById('userId').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!userId || !password) {
            this.showMessage('사용자 ID와 비밀번호를 입력해주세요.', 'error');
            return;
        }

        const loginBtn = document.getElementById('loginBtn');
        const originalText = loginBtn.textContent;
        
        try {
            loginBtn.textContent = '로그인 중...';
            loginBtn.disabled = true;
            loginBtn.classList.add('loading');

            const response = await this.apiClient.login(userId, password);
            
            this.showMessage('로그인 성공!', 'success');
            this.updateUI();
            
            // 사용자 정보 표시
            if (response.data.user_info) {
                const userInfo = response.data.user_info;
                this.showMessage(`환영합니다, ${userInfo.user_nm || userInfo.user_id}님!`, 'info');
            }
            
        } catch (error) {
            console.error('로그인 오류:', error);
            let errorMessage = '로그인 실패';
            
            if (error.response && error.response.data) {
                errorMessage = error.response.data.detail || errorMessage;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.showMessage(errorMessage, 'error');
        } finally {
            loginBtn.textContent = originalText;
            loginBtn.disabled = false;
            loginBtn.classList.remove('loading');
        }
    }

    /**
     * 로그아웃 처리
     */
    handleLogout() {
        this.apiClient.logout();
        this.showMessage('로그아웃 되었습니다.', 'info');
        this.updateUI();
        
        // 응답 영역 초기화
        document.getElementById('responseStatus').textContent = '-';
        document.getElementById('responseTime').textContent = '-';
        document.getElementById('responseBody').textContent = '응답이 여기에 표시됩니다...';
    }

    /**
     * API 요청 처리
     */
    async handleApiRequest() {
        const method = document.getElementById('apiMethod').value;
        const url = document.getElementById('apiUrl').value.trim();
        const requestBodyText = document.getElementById('requestBody').value.trim();

        if (!url) {
            this.showMessage('API 엔드포인트를 입력해주세요.', 'error');
            return;
        }

        let requestData = null;
        if (['POST', 'PUT', 'PATCH'].includes(method) && requestBodyText) {
            try {
                requestData = JSON.parse(requestBodyText);
            } catch (error) {
                this.showMessage('요청 본문이 올바른 JSON 형식이 아닙니다.', 'error');
                return;
            }
        }

        const sendBtn = document.getElementById('sendRequestBtn');
        const originalText = sendBtn.textContent;
        const startTime = Date.now();
        
        try {
            sendBtn.textContent = '요청 중...';
            sendBtn.disabled = true;
            sendBtn.classList.add('loading');

            let response;
            switch (method) {
                case 'GET':
                    response = await this.apiClient.get(url);
                    break;
                case 'POST':
                    response = await this.apiClient.post(url, requestData);
                    break;
                case 'PUT':
                    response = await this.apiClient.put(url, requestData);
                    break;
                case 'DELETE':
                    response = await this.apiClient.delete(url);
                    break;
                default:
                    throw new Error('지원하지 않는 HTTP 메서드입니다.');
            }

            const duration = Date.now() - startTime;
            this.displayResponse(response, duration, 'success');
            
        } catch (error) {
            console.error('API 요청 오류:', error);
            const duration = Date.now() - startTime;
            this.displayResponse(error.response || error, duration, 'error');
        } finally {
            sendBtn.textContent = originalText;
            sendBtn.disabled = false;
            sendBtn.classList.remove('loading');
        }
    }

    /**
     * 응답 표시
     * @param {Object} response - 응답 객체
     * @param {number} duration - 요청 시간
     * @param {string} type - 응답 타입 ('success' | 'error')
     */
    displayResponse(response, duration, type) {
        const statusElement = document.getElementById('responseStatus');
        const timeElement = document.getElementById('responseTime');
        const bodyElement = document.getElementById('responseBody');

        // 상태 표시
        const status = response.status || 'ERROR';
        statusElement.textContent = `${status} ${response.statusText || ''}`;
        statusElement.className = `response-status ${type}`;

        // 시간 표시
        timeElement.textContent = `${duration}ms`;

        // 응답 본문 표시
        let displayData;
        if (response.data) {
            displayData = response.data;
        } else if (response.message) {
            displayData = { error: response.message };
        } else {
            displayData = response;
        }

        bodyElement.textContent = JSON.stringify(displayData, null, 2);
    }

    /**
     * UI 상태 업데이트
     */
    updateUI() {
        const hasValidToken = this.tokenManager.hasValidToken();
        
        // 버튼 상태 업데이트
        document.getElementById('loginBtn').disabled = hasValidToken;
        document.getElementById('logoutBtn').disabled = !hasValidToken;
        document.getElementById('sendRequestBtn').disabled = !hasValidToken;
        
        // 토큰 상태는 TokenManager에서 자동 업데이트됨
    }

    /**
     * 메시지 표시
     * @param {string} message - 메시지 내용
     * @param {string} type - 메시지 타입 ('success' | 'error' | 'info')
     */
    showMessage(message, type) {
        // 기존 메시지 제거
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // 새 메시지 생성
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        // 인증 섹션 다음에 삽입
        const authSection = document.querySelector('.auth-section');
        authSection.insertAdjacentElement('afterend', messageDiv);

        // 3초 후 자동 제거
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 3000);
    }

    /**
     * 레거시 API 호출 마이그레이션 예제
     */
    demonstrateLegacyMigration() {
        console.log('=== 레거시 API 호출 마이그레이션 예제 ===');
        
        // 기존 방식 (레거시)
        console.log('❌ 레거시 방식:');
        console.log(`
        // 기존 코드
        fetch('/api/v1/users', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status === 401) {
                // 수동으로 토큰 갱신 처리...
            }
            return response.json();
        })
        .catch(error => {
            console.error('오류:', error);
        });
        `);
        
        // 새로운 방식 (Trae)
        console.log('✅ 새로운 방식 (Trae):');
        console.log(`
        // 새로운 코드
        apiClient.get('/api/v1/users')
            .then(response => {
                console.log('데이터:', response.data);
            })
            .catch(error => {
                console.error('오류:', error);
            });
        
        // 또는 async/await
        try {
            const response = await apiClient.get('/api/v1/users');
            console.log('데이터:', response.data);
        } catch (error) {
            console.error('오류:', error);
        }
        `);
        
        console.log('🎯 장점:');
        console.log('- 자동 토큰 관리');
        console.log('- 401 오류 시 자동 재시도');
        console.log('- 통합된 오류 처리');
        console.log('- 요청/응답 로깅');
        console.log('- 인터셉터를 통한 확장성');
    }
}

// DOM 로드 완료 후 애플리케이션 시작
document.addEventListener('DOMContentLoaded', () => {
    window.skyBootApp = new SkyBootApp();
    
    // 개발자 도구에서 마이그레이션 예제 확인 가능
    console.log('💡 레거시 마이그레이션 예제를 보려면 skyBootApp.demonstrateLegacyMigration() 을 실행하세요.');
});