# 🤝 PDF Quality Checker v2.0 - 실시간 협업 기능 설계서

> **작성일**: 2025-01-11  
> **작성자**: Claude AI Assistant  
> **목적**: 팀 단위 PDF 품질 검사 협업을 위한 실시간 기능 설계

---

## 📋 목차
1. [개요](#1-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [핵심 기능](#3-핵심-기능)
4. [기술 스택](#4-기술-스택)
5. [구현 세부사항](#5-구현-세부사항)
6. [보안 및 권한](#6-보안-및-권한)
7. [UI/UX 설계](#7-uiux-설계)
8. [구현 로드맵](#8-구현-로드맵)

---

## 1. 개요

### 1.1 배경
인쇄 업계에서는 여러 담당자가 동시에 PDF 품질을 검토하고 수정 사항을 공유해야 하는 경우가 많습니다.

### 1.2 목표
- **실시간 동기화**: 여러 사용자의 작업 상태 실시간 공유
- **효율적 협업**: 중복 작업 방지 및 작업 분배
- **이력 관리**: 모든 변경사항 추적 및 감사
- **원활한 소통**: 내장 메시징 및 코멘트 시스템

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────┐
│                클라이언트 (N개)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Client #1 │  │Client #2 │  │Client #3 │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │ WebSocket
        ┌─────────────▼─────────────┐
        │     협업 서버 (Python)      │
        │  ┌─────────────────────┐  │
        │  │  FastAPI + Socket.IO │  │
        │  └─────────────────────┘  │
        │  ┌─────────────────────┐  │
        │  │   Session Manager    │  │
        │  └─────────────────────┘  │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │        데이터베이스         │
        │  ┌─────────────────────┐  │
        │  │     PostgreSQL       │  │
        │  └─────────────────────┘  │
        │  ┌─────────────────────┐  │
        │  │       Redis          │  │
        │  └─────────────────────┘  │
        └───────────────────────────┘
```

### 2.2 컴포넌트 설계

```python
# src/collaboration/server.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
from typing import Dict, List, Set

class CollaborationServer:
    """협업 서버 메인 클래스"""
    
    def __init__(self):
        self.app = FastAPI()
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.sessions: Dict[str, Session] = {}
        self.active_users: Dict[str, User] = {}
        
    async def start(self):
        """서버 시작"""
        self.setup_routes()
        self.setup_websocket()
        
    def setup_routes(self):
        """REST API 라우트 설정"""
        @self.app.get("/api/sessions")
        async def get_sessions():
            return list(self.sessions.values())
            
        @self.app.post("/api/session/create")
        async def create_session(session_data: SessionCreate):
            session = await self.create_new_session(session_data)
            return session
```

---

## 3. 핵심 기능

### 3.1 세션 관리

#### 3.1.1 세션 생성 및 참여
```python
@dataclass
class CollaborationSession:
    """협업 세션"""
    session_id: str
    name: str
    created_by: str
    created_at: datetime
    participants: List[User]
    files: List[PDFFile]
    status: SessionStatus
    settings: SessionSettings
    
class SessionManager:
    """세션 관리자"""
    
    async def create_session(self, 
                            creator: User,
                            name: str,
                            password: Optional[str] = None) -> CollaborationSession:
        """새 협업 세션 생성"""
        session = CollaborationSession(
            session_id=self.generate_session_id(),
            name=name,
            created_by=creator.user_id,
            created_at=datetime.now(),
            participants=[creator],
            files=[],
            status=SessionStatus.ACTIVE,
            settings=SessionSettings(password=password)
        )
        await self.save_session(session)
        return session
        
    async def join_session(self,
                          session_id: str,
                          user: User,
                          password: Optional[str] = None) -> bool:
        """세션 참여"""
        session = await self.get_session(session_id)
        if session.settings.password and session.settings.password != password:
            raise PermissionError("잘못된 비밀번호")
        session.participants.append(user)
        await self.broadcast_user_joined(session, user)
        return True
```

### 3.2 실시간 동기화

#### 3.2.1 파일 상태 동기화
```python
class FileStateSync:
    """파일 상태 동기화"""
    
    @dataclass
    class FileState:
        file_id: str
        path: Path
        status: ProcessingStatus
        assigned_to: Optional[str]
        locked_by: Optional[str]
        last_modified: datetime
        issues: List[Issue]
        
    async def sync_file_state(self, 
                             session_id: str,
                             file_state: FileState):
        """파일 상태 동기화"""
        # Redis에 상태 저장
        await self.redis.hset(
            f"session:{session_id}:files",
            file_state.file_id,
            file_state.json()
        )
        
        # 모든 참여자에게 브로드캐스트
        await self.broadcast_to_session(
            session_id,
            'file_state_update',
            file_state
        )
```

#### 3.2.2 실시간 커서 공유
```python
class CursorSharing:
    """실시간 커서 위치 공유"""
    
    async def update_cursor_position(self,
                                    session_id: str,
                                    user_id: str,
                                    file_id: str,
                                    page: int,
                                    x: float,
                                    y: float):
        """커서 위치 업데이트"""
        cursor_data = {
            'user_id': user_id,
            'file_id': file_id,
            'page': page,
            'position': {'x': x, 'y': y},
            'timestamp': time.time()
        }
        
        # 다른 사용자들에게 브로드캐스트
        await self.broadcast_to_others(
            session_id,
            user_id,
            'cursor_move',
            cursor_data
        )
```

### 3.3 작업 분배 시스템

#### 3.3.1 자동 작업 분배
```python
class TaskDistributor:
    """작업 분배 시스템"""
    
    async def distribute_files(self,
                              session: CollaborationSession,
                              files: List[PDFFile]) -> Dict[str, List[PDFFile]]:
        """파일을 참여자들에게 자동 분배"""
        active_users = [u for u in session.participants if u.is_active]
        
        if not active_users:
            return {}
            
        # 라운드 로빈 방식 분배
        distribution = {user.user_id: [] for user in active_users}
        
        for i, file in enumerate(files):
            user = active_users[i % len(active_users)]
            distribution[user.user_id].append(file)
            
            # 파일 할당 상태 업데이트
            await self.assign_file(file, user)
            
        return distribution
        
    async def reassign_task(self,
                           file: PDFFile,
                           from_user: User,
                           to_user: User):
        """작업 재할당"""
        file.assigned_to = to_user.user_id
        await self.notify_reassignment(file, from_user, to_user)
```

### 3.4 커뮤니케이션

#### 3.4.1 실시간 채팅
```python
class RealtimeChat:
    """실시간 채팅 시스템"""
    
    @dataclass
    class ChatMessage:
        message_id: str
        session_id: str
        user_id: str
        content: str
        timestamp: datetime
        attachments: List[str] = field(default_factory=list)
        
    async def send_message(self,
                          session_id: str,
                          user_id: str,
                          content: str):
        """메시지 전송"""
        message = ChatMessage(
            message_id=self.generate_message_id(),
            session_id=session_id,
            user_id=user_id,
            content=content,
            timestamp=datetime.now()
        )
        
        # 메시지 저장
        await self.save_message(message)
        
        # 브로드캐스트
        await self.broadcast_to_session(
            session_id,
            'new_message',
            message
        )
```

#### 3.4.2 파일 코멘트
```python
class FileComments:
    """파일 코멘트 시스템"""
    
    @dataclass
    class Comment:
        comment_id: str
        file_id: str
        page: int
        position: Dict[str, float]  # x, y, width, height
        content: str
        author: str
        created_at: datetime
        resolved: bool = False
        
    async def add_comment(self,
                         file_id: str,
                         page: int,
                         position: Dict[str, float],
                         content: str,
                         author: str):
        """코멘트 추가"""
        comment = Comment(
            comment_id=self.generate_comment_id(),
            file_id=file_id,
            page=page,
            position=position,
            content=content,
            author=author,
            created_at=datetime.now()
        )
        
        await self.save_comment(comment)
        await self.notify_new_comment(comment)
```

---

## 4. 기술 스택

### 4.1 서버
- **FastAPI**: REST API 및 WebSocket 서버
- **Socket.IO**: 실시간 양방향 통신
- **Celery**: 비동기 작업 처리
- **uvicorn**: ASGI 서버

### 4.2 데이터베이스
- **PostgreSQL**: 세션 및 사용자 데이터
- **Redis**: 캐싱 및 실시간 상태 관리
- **MinIO**: 파일 스토리지 (선택적)

### 4.3 클라이언트
- **socket.io-client**: Python 클라이언트
- **asyncio**: 비동기 처리

---

## 5. 구현 세부사항

### 5.1 클라이언트 통합

```python
# src/collaboration/client.py
import socketio
import asyncio
from typing import Optional, Callable

class CollaborationClient:
    """협업 클라이언트"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None
        
        # 이벤트 핸들러
        self.setup_handlers()
        
    def setup_handlers(self):
        """이벤트 핸들러 설정"""
        @self.sio.on('file_state_update')
        async def on_file_state_update(data):
            await self.handle_file_state_update(data)
            
        @self.sio.on('new_message')
        async def on_new_message(data):
            await self.handle_new_message(data)
            
        @self.sio.on('user_joined')
        async def on_user_joined(data):
            await self.handle_user_joined(data)
            
    async def connect(self) -> bool:
        """서버 연결"""
        try:
            await self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"연결 실패: {e}")
            return False
            
    async def create_session(self, name: str, password: Optional[str] = None):
        """세션 생성"""
        response = await self.sio.call('create_session', {
            'name': name,
            'password': password
        })
        self.session_id = response['session_id']
        return response
        
    async def join_session(self, session_id: str, password: Optional[str] = None):
        """세션 참여"""
        response = await self.sio.call('join_session', {
            'session_id': session_id,
            'password': password
        })
        self.session_id = session_id
        return response
```

### 5.2 충돌 해결

```python
class ConflictResolver:
    """충돌 해결 시스템"""
    
    async def handle_concurrent_edit(self,
                                    file_id: str,
                                    local_changes: Dict,
                                    remote_changes: Dict) -> Dict:
        """동시 편집 충돌 해결"""
        # 타임스탬프 기반 우선순위
        if local_changes['timestamp'] > remote_changes['timestamp']:
            # 로컬 변경사항 우선
            await self.notify_conflict_resolved(file_id, 'local')
            return local_changes
        else:
            # 원격 변경사항 우선
            await self.notify_conflict_resolved(file_id, 'remote')
            return remote_changes
            
    async def handle_file_lock_conflict(self,
                                       file_id: str,
                                       requesting_user: str,
                                       current_lock_user: str):
        """파일 잠금 충돌 처리"""
        # 현재 잠금 사용자에게 알림
        await self.notify_user(
            current_lock_user,
            f"{requesting_user}가 파일 편집을 요청했습니다."
        )
        
        # 요청자에게 대기 알림
        await self.notify_user(
            requesting_user,
            f"파일이 {current_lock_user}에 의해 편집 중입니다."
        )
```

---

## 6. 보안 및 권한

### 6.1 인증 시스템

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthSystem:
    """인증 시스템"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "your-secret-key"  # 환경변수로 관리
        self.ALGORITHM = "HS256"
        
    def create_access_token(self, user_id: str) -> str:
        """액세스 토큰 생성"""
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode = {
            "sub": user_id,
            "exp": expire
        }
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """사용자 인증"""
        user = await self.get_user(username)
        if not user:
            return None
        if not self.pwd_context.verify(password, user.hashed_password):
            return None
        return user
```

### 6.2 권한 관리

```python
from enum import Enum

class Permission(Enum):
    """권한 종류"""
    VIEW = "view"
    EDIT = "edit"
    DELETE = "delete"
    ADMIN = "admin"
    
class RoleManager:
    """역할 기반 권한 관리"""
    
    ROLES = {
        'admin': [Permission.VIEW, Permission.EDIT, Permission.DELETE, Permission.ADMIN],
        'editor': [Permission.VIEW, Permission.EDIT],
        'viewer': [Permission.VIEW]
    }
    
    async def check_permission(self,
                              user: User,
                              session: CollaborationSession,
                              permission: Permission) -> bool:
        """권한 확인"""
        user_role = await self.get_user_role(user, session)
        return permission in self.ROLES.get(user_role, [])
```

---

## 7. UI/UX 설계

### 7.1 협업 대시보드

```python
class CollaborationDashboard(ctk.CTkFrame):
    """협업 대시보드 UI"""
    
    def __init__(self, parent, client: CollaborationClient):
        super().__init__(parent)
        self.client = client
        
        # 레이아웃 구성
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        # 상단: 세션 정보
        self.session_info = SessionInfoPanel(self)
        self.session_info.pack(fill='x', padx=10, pady=5)
        
        # 중앙: 분할 뷰
        self.paned = ctk.CTkPanedWindow(self, orient='horizontal')
        self.paned.pack(fill='both', expand=True)
        
        # 좌측: 파일 목록 및 참여자
        self.left_panel = LeftPanel(self.paned)
        self.paned.add(self.left_panel)
        
        # 우측: 채팅 및 활동 로그
        self.right_panel = RightPanel(self.paned)
        self.paned.add(self.right_panel)
```

### 7.2 실시간 상태 표시

```python
class RealtimeStatusIndicator(ctk.CTkFrame):
    """실시간 상태 표시기"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 연결 상태
        self.connection_status = ctk.CTkLabel(
            self,
            text="● 연결됨",
            text_color="green"
        )
        self.connection_status.pack(side='left', padx=5)
        
        # 활성 사용자 수
        self.active_users = ctk.CTkLabel(
            self,
            text="👥 0명 온라인"
        )
        self.active_users.pack(side='left', padx=5)
        
        # 동기화 상태
        self.sync_status = ctk.CTkLabel(
            self,
            text="🔄 동기화됨"
        )
        self.sync_status.pack(side='left', padx=5)
        
    def update_status(self, connected: bool, users: int, synced: bool):
        """상태 업데이트"""
        # 연결 상태
        if connected:
            self.connection_status.configure(
                text="● 연결됨",
                text_color="green"
            )
        else:
            self.connection_status.configure(
                text="● 연결 끊김",
                text_color="red"
            )
            
        # 사용자 수
        self.active_users.configure(text=f"👥 {users}명 온라인")
        
        # 동기화 상태
        if synced:
            self.sync_status.configure(text="✅ 동기화됨")
        else:
            self.sync_status.configure(text="🔄 동기화 중...")
```

---

## 8. 구현 로드맵

### Phase 1: 기본 인프라 (2주)
- [ ] FastAPI 서버 구축
- [ ] WebSocket 통신 구현
- [ ] PostgreSQL/Redis 연동
- [ ] 기본 인증 시스템

### Phase 2: 핵심 협업 기능 (3주)
- [ ] 세션 관리 시스템
- [ ] 실시간 파일 상태 동기화
- [ ] 작업 분배 시스템
- [ ] 충돌 해결 메커니즘

### Phase 3: 커뮤니케이션 (2주)
- [ ] 실시간 채팅
- [ ] 파일 코멘트 시스템
- [ ] 알림 시스템
- [ ] 활동 로그

### Phase 4: UI 통합 (2주)
- [ ] 협업 대시보드
- [ ] 실시간 상태 표시
- [ ] 참여자 관리 UI
- [ ] 채팅 인터페이스

### Phase 5: 고급 기능 (3주)
- [ ] 화면 공유 (선택적)
- [ ] 음성 통화 (선택적)
- [ ] 버전 관리
- [ ] 감사 로그

### Phase 6: 최적화 및 배포 (1주)
- [ ] 성능 최적화
- [ ] 보안 강화
- [ ] Docker 컨테이너화
- [ ] 배포 스크립트

---

## 📎 부록

### A. API 엔드포인트

```yaml
# REST API
GET    /api/sessions              # 세션 목록
POST   /api/session/create        # 세션 생성
POST   /api/session/join          # 세션 참여
DELETE /api/session/{id}          # 세션 종료
GET    /api/session/{id}/files    # 파일 목록
GET    /api/session/{id}/users    # 참여자 목록

# WebSocket 이벤트
connect                           # 연결
disconnect                        # 연결 해제
create_session                    # 세션 생성
join_session                      # 세션 참여
file_state_update                 # 파일 상태 업데이트
send_message                      # 메시지 전송
cursor_move                       # 커서 이동
```

### B. 데이터베이스 스키마

```sql
-- 세션 테이블
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50),
    settings JSONB
);

-- 세션 참여자
CREATE TABLE session_participants (
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT NOW(),
    role VARCHAR(50),
    PRIMARY KEY (session_id, user_id)
);

-- 파일 상태
CREATE TABLE file_states (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    file_path TEXT,
    status VARCHAR(50),
    assigned_to UUID REFERENCES users(id),
    locked_by UUID REFERENCES users(id),
    last_modified TIMESTAMP,
    metadata JSONB
);

-- 채팅 메시지
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### C. 사용 예제

```python
# 클라이언트 사용 예제
async def main():
    # 클라이언트 생성
    client = CollaborationClient('http://localhost:8000')
    
    # 서버 연결
    await client.connect()
    
    # 세션 생성
    session = await client.create_session(
        name="인쇄물 품질 검사 - 2025년 1월",
        password="secure123"
    )
    
    # 파일 추가
    await client.add_files([
        Path("document1.pdf"),
        Path("document2.pdf")
    ])
    
    # 메시지 전송
    await client.send_message("품질 검사 시작합니다.")
    
    # 파일 상태 업데이트
    await client.update_file_state(
        file_id="file1",
        status="processing"
    )
    
# 실행
asyncio.run(main())
```

---

*이 문서는 PDF Quality Checker v2.0의 실시간 협업 기능 구현을 위한 상세 설계서입니다.*