# JWT 토큰 보안 적용 가이드

이 문서는 SkyBoot Core API 프로젝트에서 엔드포인트에 JWT Access Token과 Refresh Token 보안을 적용하는 방법을 설명합니다.

## 📋 목차

1. [기본 개념](#기본-개념)
2. [의존성 함수 사용법](#의존성-함수-사용법)
3. [엔드포인트 보안 적용 예제](#엔드포인트-보안-적용-예제)
4. [다양한 인증 패턴](#다양한-인증-패턴)
5. [에러 처리](#에러-처리)
6. [베스트 프랙티스](#베스트-프랙티스)

## 🔐 기본 개념

### JWT 토큰 구조
- **Access Token**: 짧은 수명(30분), API 요청 시 사용
- **Refresh Token**: 긴 수명(7일), Access Token 갱신 시 사용

### 인증 플로우
1. 사용자 로그인 → Access Token + Refresh Token 발급
2. API 요청 시 Access Token을 Authorization 헤더에 포함
3. Access Token 만료 시 Refresh Token으로 새 Access Token 발급

## 🛠️ 의존성 함수 사용법

### 1. 기본 토큰 검증

```python
from app.utils.dependencies import verify_token_dependency

@router.get("/protected")
async def protected_endpoint(
    token_payload: dict = Depends(verify_token_dependency)
):
    """
    기본 토큰 검증만 수행
    token_payload에는 JWT 페이로드가 포함됨
    """
    user_id = token_payload.get("user_id")
    return {"message": f"Hello {user_id}"}
```

### 2. 현재 사용자 정보 가져오기

```python
from app.utils.dependencies import get_current_user

@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    현재 인증된 사용자 정보 반환
    current_user = {
        "user_id": "user123",
        "email": "user@example.com",
        "group_id": "group1",
        "sub": "user123"
    }
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"]
    }
```

### 3. 사용자 ID만 필요한 경우

```python
from app.utils.dependencies import get_current_user_id

@router.post("/posts")
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    사용자 ID만 필요한 경우 사용
    """
    # 게시글 생성 로직
    return post_service.create(db, post_data, author_id=current_user_id)
```

### 4. 데이터베이스와 사용자 정보 함께 사용

```python
from app.utils.dependencies import get_current_user_with_db

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    db_and_user = Depends(get_current_user_with_db)
):
    """
    데이터베이스 세션과 사용자 정보를 함께 가져옴
    """
    db, current_user = db_and_user
    return user_service.update_profile(db, current_user["user_id"], profile_data)
```

## 📝 엔드포인트 보안 적용 예제

### 사용자 관리 API 예제

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.dependencies import (
    get_current_user, 
    get_current_user_id, 
    verify_token_dependency
)

router = APIRouter(prefix="/users", tags=["사용자 관리"])

# 1. 사용자 생성 (관리자 권한 필요)
@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)  # JWT 토큰에서 사용자 ID 추출
):
    """
    새로운 사용자를 생성합니다.
    Authorization: Bearer <access_token> 헤더 필수
    """
    return user_service.create(db, user_data, created_by=current_user_id)

# 2. 사용자 목록 조회
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 전체 사용자 정보 필요
):
    """
    사용자 목록을 조회합니다.
    현재 사용자의 권한에 따라 조회 범위가 달라질 수 있습니다.
    """
    # 권한 체크 로직
    if current_user["group_id"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    return user_service.get_multi(db, skip=skip, limit=limit)

# 3. 특정 사용자 조회
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    특정 사용자 정보를 조회합니다.
    본인 정보이거나 관리자 권한이 있어야 합니다.
    """
    # 본인 정보 또는 관리자 권한 체크
    if current_user["user_id"] != user_id and current_user["group_id"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 정보이거나 관리자 권한이 필요합니다."
        )
    
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return user

# 4. 사용자 정보 수정
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    사용자 정보를 수정합니다.
    """
    return user_service.update(db, user_id, user_data, updated_by=current_user_id)

# 5. 사용자 삭제
@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    사용자를 삭제합니다.
    관리자 권한 필요
    """
    if current_user["group_id"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    return user_service.delete(db, user_id)
```

### 게시판 API 예제

```python
@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    새 게시글을 작성합니다.
    """
    return post_service.create(db, post_data, author_id=current_user_id)

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 조회 권한 체크용
):
    """
    게시글을 조회합니다.
    """
    post = post_service.get(db, post_id)
    
    # 비공개 게시글인 경우 작성자만 조회 가능
    if post.is_private and post.author_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비공개 게시글입니다."
        )
    
    return post
```

## 🔄 다양한 인증 패턴

### 1. 선택적 인증 (Optional Authentication)

```python
from typing import Optional
from app.utils.dependencies import get_current_user

@router.get("/public-posts")
async def get_public_posts(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)  # 선택적 인증
):
    """
    공개 게시글 조회 (로그인 선택사항)
    로그인한 사용자에게는 추가 정보 제공
    """
    posts = post_service.get_public_posts(db)
    
    if current_user:
        # 로그인한 사용자에게는 좋아요 상태 등 추가 정보 제공
        return post_service.add_user_specific_data(posts, current_user["user_id"])
    
    return posts
```

### 2. 권한 기반 접근 제어

```python
def require_admin(current_user: dict = Depends(get_current_user)):
    """
    관리자 권한 체크 의존성
    """
    if current_user["group_id"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    return current_user

@router.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(require_admin)  # 관리자 권한 필수
):
    """
    관리자 전용 사용자 삭제
    """
    return user_service.admin_delete(db, user_id, admin_user["user_id"])
```

### 3. 리프레시 토큰 검증

```python
from app.utils.dependencies import verify_refresh_token

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    db: Session = Depends(get_db),
    refresh_payload: dict = Depends(verify_refresh_token)  # 리프레시 토큰 검증
):
    """
    리프레시 토큰으로 새 액세스 토큰 발급
    """
    auth_service = AuthorInfoService()
    return auth_service.refresh_access_token(db, refresh_payload)
```

## ⚠️ 에러 처리

### 일반적인 인증 에러

```python
# 401 Unauthorized - 토큰이 없거나 유효하지 않음
{
    "detail": "유효하지 않거나 만료된 토큰입니다.",
    "headers": {"WWW-Authenticate": "Bearer"}
}

# 403 Forbidden - 토큰은 유효하지만 권한 부족
{
    "detail": "관리자 권한이 필요합니다."
}
```

### 커스텀 에러 처리

```python
@router.get("/sensitive-data")
async def get_sensitive_data(
    current_user: dict = Depends(get_current_user)
):
    try:
        # 민감한 데이터 조회 로직
        if not user_service.has_permission(current_user["user_id"], "sensitive_data.read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="민감한 데이터 조회 권한이 없습니다."
            )
        
        return sensitive_service.get_data(current_user["user_id"])
        
    except Exception as e:
        logger.error(f"민감한 데이터 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="데이터 조회 중 오류가 발생했습니다."
        )
```

## 🎯 베스트 프랙티스

### 1. 의존성 함수 선택 가이드

| 상황 | 사용할 의존성 함수 | 예시 |
|------|------------------|------|
| 기본 토큰 검증만 필요 | `verify_token_dependency` | 토큰 유효성만 확인 |
| 사용자 ID만 필요 | `get_current_user_id` | 로그 기록, 작성자 설정 |
| 전체 사용자 정보 필요 | `get_current_user` | 권한 체크, 프로필 조회 |
| DB와 사용자 정보 모두 필요 | `get_current_user_with_db` | 복잡한 비즈니스 로직 |
| 리프레시 토큰 검증 | `verify_refresh_token` | 토큰 갱신 엔드포인트 |

### 2. 보안 고려사항

```python
# ✅ 좋은 예시
@router.get("/users/{user_id}/private-info")
async def get_private_info(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    # 본인 정보만 조회 가능하도록 체크
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 정보만 조회할 수 있습니다."
        )
    
    return user_service.get_private_info(user_id)

# ❌ 나쁜 예시 - 권한 체크 없음
@router.get("/users/{user_id}/private-info")
async def get_private_info_bad(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    # 권한 체크 없이 모든 사용자 정보 조회 가능 (보안 취약점)
    return user_service.get_private_info(user_id)
```

### 3. 성능 최적화

```python
# 토큰 검증 결과 캐싱 (Redis 사용)
from app.utils.cache import cache_token_validation

@cache_token_validation(ttl=300)  # 5분 캐싱
def verify_token_with_cache(token: str):
    return verify_token(token, "access")
```

### 4. 로깅 및 모니터링

```python
@router.post("/critical-action")
async def critical_action(
    action_data: ActionData,
    current_user: dict = Depends(get_current_user)
):
    # 중요한 작업에 대한 로깅
    logger.info(
        f"🔒 Critical action attempted - User: {current_user['user_id']}, "
        f"Action: {action_data.action_type}, IP: {request.client.host}"
    )
    
    try:
        result = critical_service.perform_action(action_data, current_user["user_id"])
        
        logger.info(
            f"✅ Critical action completed - User: {current_user['user_id']}, "
            f"Result: {result.status}"
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"❌ Critical action failed - User: {current_user['user_id']}, "
            f"Error: {str(e)}"
        )
        raise
```

## 📚 추가 참고사항

### 환경 변수 설정

```bash
# .env 파일
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 프론트엔드 연동

```javascript
// JavaScript 예시
const response = await fetch('/api/v1/users', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
});

if (response.status === 401) {
    // 토큰 만료 시 리프레시 토큰으로 갱신
    await refreshAccessToken();
    // 원래 요청 재시도
}
```

이 가이드를 참고하여 프로젝트의 모든 보호된 엔드포인트에 적절한 JWT 토큰 보안을 적용하시기 바랍니다.