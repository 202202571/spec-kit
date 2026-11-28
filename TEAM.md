# 팀 작업 문서: github/spec-kit 이슈 #4954

> 팀 공유용. **업스트림 PR에 포함하지 않는다.** fork는 공개 저장소이므로 개인정보나 비밀값은 적지 않는다.
> 기준일: 2026-11-27

## ⛔ 필수: 팀 PR은 반드시 `202202571/spec-kit`으로
**`github/spec-kit`으로 가는 PR은 마지막에 김종훈만, 팀 검토를 마친 뒤 만든다.**

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

**업스트림에 잘못 만들었다면:** 바로 닫고 김종훈에게 알린 뒤 다시 만든다. 닫아도 업스트림에 기록은 남으므로, 만들기 전 확인이 중요하다.

## 0. 팀 기여 목표
**Codex 사용자가 훅 안내를 보고 실행 가능한 `$speckit-...` 명령을 받도록, 메인테이너가 동의한 방식으로 issue 4954 해결에 기여한다.**

성공 기준:
- [ ] 메인테이너와 해결 방향을 맞춘다. (11-27 질문 게시, 11-28 확인 시점까지 답변 없음)
- [ ] 변경 범위를 좁게 유지한다. 광범위한 변경은 하지 않는다.
- [ ] 회귀 테스트로 수정 전 실패 → 수정 후 통과를 증명하고, 담당자가 검토한다.
- [ ] 기존 동작에 새 실패가 없음을 확인한다.
- [ ] AI 사용과 각자의 기여를 사실대로 공개한다.
- [ ] 업스트림 PR을 보내고 리뷰에 대응한다.

머지는 메인테이너의 결정이라 보장할 수 없다. 방향이 바뀌거나 반려되어도 재현, 원인 분석, 선례 정리, 소통 과정은 팀의 결과물로 기록한다.

## 1. 문제
Codex는 `$speckit-...`로 명령을 실행하는데, 생성된 `.agents/skills/*/SKILL.md`의 훅 블록(`Command:`, `To execute:`, `Executing:`)에는 `/{command}`가 남는다.

## 2. 현재 상태: 방향 확인 필요
- **10-30, #4954 (mnriem):** 광범위한 변경은 받지 않는다. 수정 위치는 Codex integration이다. `__SPECKIT_COMMAND_<NAME>__` 방식이 이미 있다.
- **11-02, 우리 답글:** 범위를 Codex integration으로 한정하고 토큰 방식을 활용하겠다고 했다.
- **11-17, #4958 (mnriem):** `/{command}` 방식은 유지할 의도가 아니었다. 재작성 장치를 더하지 말고, 기존 명령 참조 방식을 중심으로 필요한 first-party 템플릿을 고쳐 달라고 했다.
- **원래 설계:** `CodexIntegration.post_process_skill_content`에서 `` `/{command}` ``만 `` `${command}` ``로 치환한다. 11-17 댓글 기준으로는 거절될 수 있다.
- **제약:** `{command}`는 실행 중에 `.specify/extensions.yml`에서 채워지므로 설치 시점의 토큰으로 표현할 수 없다.
- **11-27, 우리 댓글:** #4954에 방향 확인 질문을 올렸다. 답변 대기 중. **답을 받기 전에는 팀 PR을 병합하지 않고 업스트림 PR도 보내지 않는다.**

| 관련 항목 | 상태 |
|---|---|
| #4954 | open, 담당자 없음 |
| PR #4958 | open, draft, stale 표시. `base.py` 공통 경로에서 치환하는 방식이며 재작업 요청을 받음 |
| PR #3474 | 작성자가 닫음. 메인테이너가 정규식 추측 재작성에 반대하고 토큰 방식을 제안 |

## 3. 진행 상황
아래 구현과 테스트 초안은 AI 도구(Claude Code)로 작성했다. 원래 설계가 전제이므로 방향이 바뀌면 수정해야 한다.

| 항목 | 상태 |
|---|---|
| 구현 | `fix/4954-codex-override`에 push. fork PR #2 open, 병합 보류 |
| 테스트 초안 4개 | `test/4954-hook-prefix-tests`에 push. 담당자 검토 필요, PR 만들기 전 |
| 수동 재현 | 수정 전 버그 재현, 수정 후 `${command}` 확인 |

| 테스트 (Windows) | 수정 전 | 수정 후 (구현 + 테스트 초안) |
|---|---|---|
| 새 테스트 4개 | 2 failed, 2 passed | 4 passed |
| `test_integration_codex.py` | 실행 안 함 | 71 passed |
| `tests/integrations` | 31 failed, 3471 passed, 77 skipped | 31 failed, 3475 passed, 77 skipped |

`tests/integrations`의 실패 테스트 이름은 전후가 같고 새 실패는 없다. `WinError 1314`(권한 없음) 오류 29건을 확인했으며 나머지 원인은 확인하지 않았다.

## 4. 개발 환경 (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest tests/integrations/test_integration_codex.py -q
.\.venv\Scripts\python.exe -m pytest tests/integrations -q   # 약 18~22분
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
        ├── fix/4954-codex-override       (구현)
        └── test/4954-hook-prefix-tests   (테스트)

fork : docs/4954-team-notes              ← 이 문서 전용. 어디에도 merge하지 않음
```
| 용도 | 브랜치 이름 |
|---|---|
| 통합 브랜치 (업스트림 PR용) | `fix/4954-codex-hook-prefix` |
| 팀 문서 | `docs/4954-team-notes` |
| 구현 담당 (김종훈) | `fix/4954-codex-override` |
| 테스트 담당 (남준혁) | `test/4954-hook-prefix-tests` |

fork 안의 PR 만드는 방법은 맨 위 **⛔ 필수** 절을 따른다. 생성 후에는 대상 저장소를 바꿀 수 없다.

- 공통 브랜치에는 직접 push하지 않고 fork 안의 PR로 합친다. PR의 base가 `github/spec-kit`이 아닌지 반드시 확인한다(GitHub의 기본값은 업스트림이다).
- 작업 브랜치는 공통 브랜치에서 만들고 짧게 유지한다.
- 같은 파일을 여러 명이 고치면 충돌하기 쉬우니 담당을 먼저 정한다.
- fork의 `main`에는 작업하지 않고 업스트림과 같게 유지한다.
- 팀원이 push하려면 fork의 collaborator 권한이 필요하다.

```powershell
# 팀원: 시작
git clone https://github.com/202202571/spec-kit.git
cd spec-kit
git switch fix/4954-codex-hook-prefix
git switch -c <type>/4954-<작업>   # 새 작업 브랜치가 필요할 때
# 이미 있는 브랜치를 이어받을 때: git switch test/4954-hook-prefix-tests

# 팀 문서 읽기 (브랜치를 바꾸지 않음)
git fetch origin
git show origin/docs/4954-team-notes:TEAM.md
```

### 병합 규칙 (fork 안의 팀 PR)
**아래를 모두 만족해야 병합한다.**
- [ ] 메인테이너의 방향 답변을 확인했고, PR 내용이 그 방향과 맞는다. **답변 전에는 병합하지 않는다.**
- [ ] 작성자가 아닌 팀원이 검토하고 승인했다.
- [ ] 실행한 테스트와 결과가 PR 본문에 있고, 기준선에 없던 새 실패가 없다. (수정 전 코드에서의 테스트 실패 확인은 예외)
- [ ] base가 `202202571/spec-kit`의 `fix/4954-codex-hook-prefix`다.

| PR | 승인 | 병합 |
|---|---|---|
| 구현 PR (김종훈) | 심형섭 | 심형섭 |
| 테스트 PR (남준혁) | 한상균 | 김종훈 |
| 템플릿 등 그 밖의 PR | 작성자가 아닌 팀원 | 승인한 팀원 |

- 병합 방식은 **Rebase and merge**를 쓴다(저장소 설정에서 허용된 경우). 병합 커밋이 생기지 않고 커밋 메시지의 trailer가 유지된다.
- 순서는 **구현 PR → 테스트 PR**. 테스트 PR은 병합 전에 최신 공통 브랜치를 반영해 통과를 확인한다.
- 병합 후 각자 공통 브랜치를 `git pull`로 갱신하고, 두 PR을 모두 병합하면 테스트를 다시 실행한다.

## 6. 커밋과 PR 규칙
- 커밋 trailer는 한 줄 명령으로 넣고 `git log -1 --format=%B`로 확인한다(여러 줄 붙여넣기에서 빠진 적이 있음). 예: `git commit -m "제목" --trailer "Assisted-by: ..."`
- 커밋 메시지는 영어, Conventional Commits. 예: `fix(codex): use $ prefix in hook invocation lines`
- AI 에이전트를 쓴 커밋에는 `Assisted-by: <에이전트> (model: <모델>, supervised|autonomous)`를 넣는다. `supervised`는 사람이 커밋 전에 작성했거나 줄 단위로 검토한 경우만 해당한다. 도구가 붙인 `Co-Authored-By:`는 지우지 않는다.
- 공동 작업자는 `Co-authored-by: 이름 <GitHub noreply 이메일>`로 남긴다. squash할 때 빠지지 않게 확인한다.
- AI가 작성한 PR 본문과 댓글에도 각각 AI 사용을 밝힌다(CONTRIBUTING.md 참고).
- `TEAM.md`와 `CLAUDE.md`는 공통 브랜치와 작업 브랜치에 커밋하지 않는다.
- 업스트림 PR 전 확인: 메인테이너의 답, #4954와 #4958의 최신 상태, 작성 계정의 업스트림 open PR이 이미 3개인지 여부, 변경 파일 목록.

## 7. 역할 분담

| 담당 | 역할 | 작업 브랜치 | 산출물 |
|---|---|---|---|
| 김종훈 | 구현 · 메인테이너 소통 · 통합 | `fix/4954-codex-override` | 수정 코드(초안 구현됨), 이슈 댓글, 업스트림 PR과 리뷰 대응 |
| 심형섭 | 재현 · 렌더 경로 추적 · 코드 리뷰 | (코드 수정 없음) | 재현 로그, 훅 렌더 경로 흐름도, 구현 PR 리뷰 |
| 한상균 | 선례 · 영향 범위 · 토큰 치환 분석 | (방향에 따라) `fix/4954-hook-templates` | 선례 정리, 고정된 `/` 줄 목록, 토큰 치환 대상 분류 |
| 남준혁 | 회귀 테스트 | `test/4954-hook-prefix-tests` | 테스트 보완, 수정 전 실패 → 수정 후 통과 증거, 전체 테스트 비교 |
| 이윤기 | 연습 PR #5003 · Windows 검증 · 기록 | (#5003은 별도 브랜치) | #5003의 Bash·Python·PowerShell 수정, Windows 동작 검증, 메인 PR 체크리스트, Notion 주간 기록 |

수정하는 파일: 구현은 `src/specify_cli/integrations/codex/__init__.py`, 테스트는 `tests/integrations/test_integration_codex.py`.

### 역할별 할 일
**김종훈**
- 메인테이너와 소통하고 답을 팀에 공유한다.
- 구현 PR을 맡고, 방향이 바뀌면 이 문서부터 고친 뒤 작업을 다시 나눈다.
- 구현 diff를 직접 읽고 팀에 변경 내용을 설명한다(AI 도구로 작성한 초안).
- 업스트림 PR을 만들고 리뷰에 대응한다.

**심형섭**
- 수정 전과 후를 자기 PC에서 재현하고 로그를 남긴다.
- 코어·확장·프리셋 스킬이 `post_process_skill_content()`를 거치는지 코드에서 직접 확인해 흐름도로 그린다.
- 위 내용을 바탕으로 구현 PR을 리뷰한다: 빠진 생성 경로, 범위 밖 변경, URL·경로 영향.

**한상균**
- 선례(#3451, #3474, #4958)와 메인테이너 의견을 원문 기준으로 정리한다.
- `templates/commands/`와 `extensions/`에서 `/{command}` 줄 목록을 만들고, 토큰으로 바꿀 수 있는 것과 없는 것(실행 중에 정해지는 값)을 분류한다.
- **메인테이너가 템플릿 수정을 요청한 경우에만** 해당 템플릿을 수정한다. 그전에는 템플릿을 고치지 않는다.
- 테스트 PR을 리뷰한다.

**남준혁**
- 테스트 초안 4개를 넘겨받아 직접 검토하고 보완한다(AI 도구로 작성한 초안).
- 확인할 것: Codex 코어 스킬, `bug` 확장 스킬, URL·경로 유지, Claude 동작 유지.
- 다른 통합까지 접두사를 검사할지 검토한다. 현재 범위는 Codex이므로 다른 통합은 **동작 유지 확인**만 하고, Kimi 문제는 메모로 남긴다.
- 수정 전 실패 → 수정 후 통과를 기록하고, `tests/integrations` 전후의 **실패 테스트 이름 목록**을 비교한다.

**이윤기**
- 연습 PR #5003을 진행한다. 메인 이슈 브랜치와 섞지 않는다.
- Windows PowerShell 5.1 환경에서 메인 수정의 수동 재현을 검증한다.
- 업스트림 PR 전 체크리스트(변경 파일, trailer, AI 사용 공개, `TEAM.md`·`CLAUDE.md` 제외)를 만들고 확인한다.
- 팀원에게 결과를 모아 Notion에 주간 기록을 남긴다.

발표와 보고서에는 **각자 실제로 한 작업**을 적는다. 이미 되어 있는 재현·경로 확인·구현을 다시 확인한 것은 "검증"으로 적는다.

### 코드 수정 원칙 (충돌 방지)
- 고칠 점은 **PR 리뷰 댓글로 남기고, 작성자가 수정**한다.
- 남의 담당 파일을 직접 고쳐야 하면 담당자에게 먼저 알린다. 담당자의 PR이 합쳐진 뒤 별도 브랜치에서 PR을 올리고, 담당자가 리뷰한다.
- 본인이 작성한 PR은 본인이 승인하거나 합치지 않는다.

### 작업 순서
1. 방향 확정: #4954 답변 확인 (김종훈)
2. 테스트 보완: 수정 전 실패 확인 (남준혁). 아직 합치지 않는다.
3. 구현 확정: 남준혁의 테스트를 가져와 통과 확인 (김종훈)
4. 리뷰: 구현 PR (심형섭), 테스트 PR (한상균). 구현을 먼저 합치고 테스트를 합친다.
5. 최종 검증: 전체 테스트 (남준혁), Windows 재현과 체크리스트 (이윤기)
6. 업스트림 Draft PR 생성 (김종훈)

방향 확인을 기다리는 동안: 개발 환경 구성(전원), 재현과 흐름도(심형섭), 선례와 줄 목록(한상균), 테스트 검토(남준혁), #5003(이윤기).

### GitHub ID
| 담당 | GitHub ID |
|---|---|
| 김종훈 | |
| 심형섭 | |
| 한상균 | |
| 남준혁 | |
| 이윤기 | |
