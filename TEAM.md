# 팀 작업 문서: github/spec-kit 이슈 #4954

> 팀 공유용. **업스트림 PR에 포함하지 않는다.** fork는 공개 저장소이므로 개인정보나 비밀값은 적지 않는다.
> 기준일: 2026-11-27

## ⛔ 필수: 팀 PR은 반드시 `202202571/spec-kit`으로
**`github/spec-kit`으로 가는 PR은 마지막에 종훈만, 팀 검토를 마친 뒤 만든다.**

**PR은 아래 링크로 시작한다.** `내브랜치`만 내 브랜치 이름으로 바꾼다(먼저 push해야 한다).
```
https://github.com/202202571/spec-kit/compare/fix/4954-codex-hook-prefix...내브랜치?expand=1
```
GitHub의 **Compare & pull request** 버튼은 대상이 업스트림으로 잡힐 수 있으니 쓰지 않는다.

**Create pull request를 누르기 전에 모두 확인한다.** 하나라도 다르면 누르지 않는다.
- [ ] 주소가 `github.com/202202571/spec-kit/`으로 시작한다.
- [ ] 대상 저장소가 `github/spec-kit`이 아니다.
- [ ] base는 `fix/4954-codex-hook-prefix`, compare는 내 브랜치다.
- [ ] 변경 파일에 내 작업만 있고 `TEAM.md`, `CLAUDE.md`가 없다.
- [ ] PR 제목, 본문, 커밋 메시지에 `#4954`, 업스트림 URL, `@mnriem`이 없다. 이슈는 `issue 4954`로 적는다.

**만든 직후:** 주소가 `github.com/202202571/spec-kit/pull/번호`인지 확인한다.

**업스트림에 잘못 만들었다면:** 바로 닫고 종훈에게 알린 뒤 다시 만든다. 닫아도 업스트림에 기록은 남으므로, 만들기 전 확인이 중요하다.

## 1. 문제
Codex는 `$speckit-...`로 명령을 실행하는데, 생성된 `.agents/skills/*/SKILL.md`의 훅 블록(`Command:`, `To execute:`, `Executing:`)에는 `/{command}`가 남는다.

## 2. 현재 상태: 방향 확인 필요
- **10-30, #4954 (mnriem):** 광범위한 변경은 받지 않는다. 수정 위치는 Codex integration이다. `__SPECKIT_COMMAND_<NAME>__` 방식이 이미 있다.
- **11-02, 우리 답글:** 범위를 Codex integration으로 한정하고 토큰 방식을 활용하겠다고 했다.
- **11-17, #4958 (mnriem):** `/{command}` 방식은 유지할 의도가 아니었다. 재작성 장치를 더하지 말고, 기존 명령 참조 방식을 중심으로 필요한 first-party 템플릿을 고쳐 달라고 했다.
- **원래 설계:** `CodexIntegration.post_process_skill_content`에서 `` `/{command}` ``만 `` `${command}` ``로 치환한다. 11-17 댓글 기준으로는 거절될 수 있다.
- **제약:** `{command}`는 실행 중에 `.specify/extensions.yml`에서 채워지므로 설치 시점의 토큰으로 표현할 수 없다.
- **다음 할 일:** #4954에 방향 확인 댓글을 올린다(아직 게시 전). **답을 받기 전에는 PR을 보내지 않는다.**

| 관련 항목 | 상태 |
|---|---|
| #4954 | open, 담당자 없음 |
| PR #4958 | open, draft, stale 표시. `base.py` 공통 경로에서 치환하는 방식이며 재작업 요청을 받음 |
| PR #3474 | 작성자가 닫음. 메인테이너가 정규식 추측 재작성에 반대하고 토큰 방식을 제안 |

## 3. 진행 상황
- 회귀 테스트 4개 작성(`tests/integrations/test_integration_codex.py`, 아직 커밋 전). 원래 설계를 전제로 하므로 방향이 바뀌면 수정해야 한다.
  - 수정 전 코드: 버그를 잡는 2개 실패, 동작 유지 확인 2개 통과
- 수정 전 수동 재현 성공
- 소스 코드는 수정 전
- 수정 전 `tests/integrations`(Windows): 31 failed, 3471 passed, 77 skipped. `WinError 1314`(권한 없음) 오류가 29건 확인됨. 나머지 원인은 미확인

## 4. 개발 환경 (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest tests/integrations/test_integration_codex.py -q
.\.venv\Scripts\python.exe -m pytest tests/integrations -q   # 약 22분
```
- `Activate.ps1`은 쓰지 않고 `.venv`의 python.exe를 직접 호출한다.
- `py -3`가 실패하면 `py -0p`로 설치된 버전을 확인하고 `py -V:3.12 -m venv .venv`처럼 지정한다.
- PowerShell 코드는 Windows PowerShell 5.1에서 동작해야 한다.

## 5. 브랜치 전략
```
github/spec-kit : main
        ▲  업스트림 PR (마지막에 한 번)
fork : fix/4954-codex-hook-prefix        ← 공통(통합) 브랜치
        ▲  fork 안에서 PR + 팀원 리뷰
        ├── fix/4954-<담당 작업>
        └── test/4954-<담당 작업>

fork : docs/4954-team-notes              ← 이 문서 전용. 어디에도 merge하지 않음
```
| 용도 | 브랜치 이름 (작업 브랜치는 예시) |
|---|---|
| 통합 브랜치 (업스트림 PR용) | `fix/4954-codex-hook-prefix` |
| 팀 문서 | `docs/4954-team-notes` |
| 구현 담당 | `fix/4954-codex-override` |
| 테스트 담당 | `test/4954-hook-prefix-tests` |

fork 안의 PR 만드는 방법은 맨 위 **⛔ 필수** 절을 따른다. 생성 후에는 대상 저장소를 바꿀 수 없다.

- 공통 브랜치에는 직접 push하지 않고 fork 안의 PR로 합친다. PR의 base가 `github/spec-kit`이 아닌지 반드시 확인한다(GitHub의 기본값은 업스트림이다).
- 작업 브랜치는 공통 브랜치에서 만들고 짧게 유지한다.
- 같은 파일을 여러 명이 고치면 충돌하기 쉬우니 담당을 먼저 정한다.
- fork의 `main`에는 작업하지 않고 업스트림과 같게 유지한다.
- 팀원이 push하려면 fork의 collaborator 권한이 필요하다.

```powershell
# 팀원: 시작 (공통 브랜치가 push된 뒤)
git clone https://github.com/202202571/spec-kit.git
cd spec-kit
git switch fix/4954-codex-hook-prefix
git switch -c fix/4954-<담당 작업>

# 팀 문서 읽기 (브랜치를 바꾸지 않음)
git fetch origin
git show origin/docs/4954-team-notes:TEAM.md
```

## 6. 커밋과 PR 규칙
- 커밋 메시지는 영어, Conventional Commits. 예: `fix(codex): use $ prefix in hook invocation lines`
- AI 에이전트를 쓴 커밋에는 `Assisted-by: <에이전트> (model: <모델>, supervised|autonomous)`를 넣는다. `supervised`는 사람이 커밋 전에 작성했거나 줄 단위로 검토한 경우만 해당한다. 도구가 붙인 `Co-Authored-By:`는 지우지 않는다.
- 공동 작업자는 `Co-authored-by: 이름 <GitHub noreply 이메일>`로 남긴다. squash할 때 빠지지 않게 확인한다.
- AI가 작성한 PR 본문과 댓글에도 각각 AI 사용을 밝힌다(CONTRIBUTING.md 참고).
- `TEAM.md`와 `CLAUDE.md`는 공통 브랜치와 작업 브랜치에 커밋하지 않는다.
- 업스트림 PR 전 확인: 메인테이너의 답, #4954와 #4958의 최신 상태, 작성 계정의 업스트림 open PR이 이미 3개인지 여부, 변경 파일 목록.

## 7. 역할 분담

| 담당 | 역할 | 수정하는 파일 | 작업 브랜치 | 산출물 |
|---|---|---|---|---|
| 종훈 | 메인 구현, 통합 담당 | `src/specify_cli/integrations/codex/__init__.py` | `fix/4954-codex-override` | 수정 코드, 수정 전후 수동 재현 결과, 업스트림 PR 본문 |
| 형섭 | 테스트 구현과 실행 | `tests/integrations/test_integration_codex.py` | `test/4954-hook-prefix-tests` | 회귀 테스트, 수정 전 실패 → 수정 후 통과 기록, 전체 테스트 결과 |
| 상균 | 코드 검토와 검증 | 원칙적으로 직접 수정하지 않음 (아래 참고) | 필요할 때 `fix/4954-review-<내용>` | 리뷰 의견, 다른 PC에서의 재현 확인, PR 전 최종 점검 |

### 역할별 할 일
**종훈**
- #4954에 방향 확인 댓글을 올리고 메인테이너의 답을 팀에 공유한다.
- 정해진 방향대로 구현한다. 방향이 바뀌면 이 문서부터 고친다.
- 팀 PR을 공통 브랜치에 합치고, 업스트림 PR을 만들고 메인테이너에게 답한다.

**형섭**
- 작성되어 있는 테스트 초안 4개를 넘겨받아 이해하고 보완한다(AI 도구로 작성한 초안이므로 직접 검토한다).
- 확인할 것: Codex 코어 스킬, `bug` 확장 스킬, URL·경로 유지, Claude 동작 유지.
- 수정 전 코드에서는 버그 테스트가 실패하고 수정 후에는 통과하는지 기록한다.
- `tests/integrations` 전체를 수정 전후로 실행해 **실패한 테스트 이름 목록을 비교**한다.

**상균**
- 종훈과 형섭의 PR을 리뷰한다.
- 확인할 것: 메인테이너 조건에 맞는 범위인지, 관계없는 변경이 없는지, URL·경로를 건드리지 않는지, `TEAM.md`·`CLAUDE.md`가 섞이지 않았는지, 커밋 trailer가 맞는지.
- 다른 PC에서 수동 재현을 해 결과를 확인한다.
- 업스트림 PR 전에 최종 diff와 PR 본문을 점검한다.

### 코드 수정 원칙 (충돌 방지)
- 고칠 점은 **PR 리뷰 댓글로 남기고, 작성자가 수정**한다.
- 상균이 직접 고쳐야 하면 작성자에게 먼저 알린다. 작성자의 PR이 합쳐진 뒤 공통 브랜치에서 `fix/4954-review-<내용>`을 만들어 PR을 올리고, 파일 담당자가 리뷰한다.
- 본인이 작성한 PR은 본인이 승인하거나 합치지 않는다. 상균이 직접 수정한 PR은 해당 파일 담당자가 검토한다.

### 작업 순서
1. 방향 확정: #4954 답변 확인 (종훈)
2. 테스트 PR 준비: 수정 전 실패 확인 (형섭). 아직 합치지 않는다.
3. 구현 PR 준비 (종훈). 형섭의 테스트를 가져와 통과를 확인한다.
4. 리뷰 (상균). 구현을 먼저 합치고, 이어서 테스트를 합친다. 테스트를 먼저 합치면 공통 브랜치가 실패 상태가 된다.
5. 공통 브랜치에서 최종 검증: 테스트 (형섭), 재현과 diff 점검 (상균)
6. 업스트림 Draft PR 생성 (종훈)

방향 확인을 기다리는 동안: 개발 환경 구성(전원), 수정 전 재현과 기준선 테스트(형섭, 상균).

### GitHub ID
| 담당 | GitHub ID |
|---|---|
| 종훈 | |
| 형섭 | |
| 상균 | |
