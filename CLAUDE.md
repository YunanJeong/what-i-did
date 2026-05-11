# what-i-did — Claude 작업 가이드

임의 GitHub 계정의 공개 레포들을 분석해 포트폴리오(md + docx)를 생성하는 Python CLI.
사용법·배경 설명은 `README.md` 를 본다. 이 파일은 **다음 세션의 Claude 가 놓치지 말아야 할 규칙**만 담는다.

## 절대 어기지 말 것

1. **크레덴셜을 코드에서 다루지 않는다.**
   - `ANTHROPIC_API_KEY`, `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` 등 어떤 인증 값도 `os.environ`·`getenv`·설정 파일·로그·에러 메시지로 읽거나 노출하지 않는다.
   - 값 핸들링은 전부 `anthropic.Anthropic()` / `anthropic.AnthropicBedrock()` / boto3 에 위임한다.
2. **GitHub 토큰 관련 로직 추가 금지.** 공개 레포 + 비인증 REST + `git clone` 만으로 동작해야 한다. `--github-token` 같은 옵션을 무심코 만들지 말 것.
3. **`.claude/settings.local.json` 은 `.gitignore` 에 있다.** 커밋되지 않게 유지.

## 주요 명령

```bash
uv sync                                      # 의존성 설치
uv run what-i-did <username>                 # 기본 (anthropic, ko, claude-sonnet-4-6)
uv run what-i-did <username> --provider bedrock \
  --model 'global.anthropic.claude-sonnet-4-6'   # cross-region inference id 형식
# 또는: --model 'anthropic.claude-sonnet-4-5-20250929-v1:0' (region-specific)
uv run what-i-did <username> --include 'kafka-*' --exclude '*-manager'
uv run what-i-did <username> --refresh       # 캐시 무시
uv run ruff check src/                       # 린트
```

## 아키텍처 맵

```
cli.py                 typer 엔트리, provider 분기, 오케스트레이션
├─ collect.py          GitHub REST 목록 + git clone + 파일 선별 (바이너리/lock/.gitignore/size 필터)
├─ analyze.py          Anthropic SDK 호출. system 블록에 cache_control, output_config.format 로 JSON 강제
├─ cache.py            ~/.cache/what-i-did/<user>/<repo>.json 읽기/쓰기
├─ aggregate.py        is_toy 분리, tech_stack 카운트
├─ render/
│  ├─ markdown.py
│  └─ docx.py          python-docx 로 직접 작성 (pandoc 의존 없음)
├─ prompts/{ko,en}.py  SYSTEM / USER_TEMPLATE / SUMMARY_* / 라벨
└─ models.py           pydantic: RepoMeta, SelectedFile, RepoAnalysis, PortfolioSummary
```

## 캐시 정책

- 경로: `~/.cache/what-i-did/<user>/<repo>.json` (기본) 또는 `--cache-dir` 로 지정된 경로
- **존재하면 무조건 재사용.** SHA·mtime·TTL 기반 무효화는 도입하지 않는다.
- 사용자가 `--refresh` 줄 때만 캐시 무시. cron 주기 실행 시 LLM 재호출이 0에 수렴하도록 의도한 설계.
- 사용자는 `--cache-dir ./cache` 처럼 레포 안 경로를 지정해 캐시를 git 으로 공유할 수 있음 (README "여러 머신 간 캐시 공유" 섹션 참고). 이 패턴을 깨는 변경(캐시 파일에 머신 종속 절대경로·타임스탬프를 추가하는 등)은 피한다.

## Provider 분기

- `--provider anthropic` (기본): `ANTHROPIC_API_KEY` 사용. 모델 id 는 `claude-...` 형식.
- `--provider bedrock`: AWS 크레덴셜 사용. 모델 id 는 `anthropic.claude-...-v1:0` 또는 `us.anthropic.claude-...` (cross-region) 등 Bedrock 형식 필요 → `--model` 필수.

## 의도적으로 커밋되는 파일

- `what-i-did-yunanjeong-*.md|docx` — **샘플 결과물.** 사용자가 의도해서 커밋한 것. `.gitignore` 에 추가하지 말 것.
- `uv.lock` — 의존성 잠금 파일. 커밋이 정석.
- `cache/` (있을 경우) — 사용자가 `--cache-dir ./cache` 로 캐시를 레포 내부에 두고 git 으로 멀티 머신 동기화하는 패턴을 쓸 수 있음. `.gitignore` 에 추가하지 말 것.

## Claude 에게

- LLM 응답 스키마(`REPO_ANALYSIS_SCHEMA` in `analyze.py`)를 바꿀 때는 `models.RepoAnalysis` 와 `prompts/{ko,en}.py` 의 SYSTEM 설명도 함께 맞춰야 한다.
- prompt caching 의 캐시 히트를 깨지 않도록, 시스템 프롬프트 앞쪽에 가변 문자열(타임스탬프·username 등)을 섞지 말 것. 가변 내용은 user 메시지 쪽에 둔다.
- 바이너리 감지·파일 예산 등 상수는 `collect.py` 상단에 모여 있다. 수정 시 거기서만.
