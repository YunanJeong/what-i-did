# what-i-did

임의 GitHub 계정의 공개 레포지토리들을 분석해 **"이 사람이 실제로 무엇을 만들었는지"** 를 포트폴리오 문서(Markdown + Word)로 뽑아주는 CLI.

README만 읽으면 과장되거나 부정확할 때가 많으므로, 실제 소스 파일을 LLM에게 직접 보여주고 판단하게 한다.

## 주요 특징

- 공개 레포지토리만 대상 → **GitHub 토큰·인증 불필요**
- `~/.cache/what-i-did/<user>/<repo>.json` 에 repo별 분석 결과를 캐싱 → cron 주기 실행 시 재호출 없음
- Markdown 과 Word(`.docx`) 동시 출력. pandoc 외부 의존성 없이 `python-docx` 로 직접 작성
- 한국어 / 영어 출력 (`--lang ko|en`)
- Anthropic 모델 선택 가능 (기본 `claude-sonnet-4-6`)
- **Anthropic API 와 AWS Bedrock 양쪽 지원** (`--provider anthropic|bedrock`)
- repo 이름 기준 glob 으로 제외 가능

## 요구 사항

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- `git` (레포 클론용)
- LLM 인증 정보 (아래 "인증" 참고)

## 인증

코드에서 인증 값을 직접 다루지 않는다. 제공자별로 적절한 환경 변수를 쉘에 export 만 해두면 SDK 가 읽어간다.

### Anthropic API 경로 (기본)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### AWS Bedrock 경로

`--provider bedrock` 사용 시. 아래 중 한 가지 방식으로 자격 증명을 제공:

```bash
# 방법 1: Bedrock API key (bearer token)
export AWS_BEARER_TOKEN_BEDROCK="..."
export AWS_REGION="us-east-1"

# 방법 2: 표준 AWS 자격 증명 (IAM 사용자/역할)
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# 또는 `aws configure` 로 저장된 프로파일도 사용 가능
```

Bedrock 에서는 모델 id 형식이 다르다 (`anthropic.claude-...-v1:0`). `--model` 을 반드시 명시해야 한다.

## 설치

```bash
uv sync
```

## 사용법

```bash
uv run what-i-did <username> [옵션]
```

### 예시

```bash
# 기본: 한국어, claude-sonnet-4-6 (Anthropic API 경로)
uv run what-i-did octocat

# 영어 출력
uv run what-i-did octocat --lang en

# 특정 레포만 분석 (repo 이름에 glob 매칭, 반복 가능)
uv run what-i-did yunanjeong --include 'kafka-*' --include 'kstreams-*'

# 특정 레포 제외 (repo 이름에 glob 매칭, 반복 가능)
uv run what-i-did octocat --exclude 'test-*' --exclude 'sandbox'

# include 와 exclude 는 함께 쓸 수 있다 (include 먼저, 그 후 exclude)
uv run what-i-did yunanjeong --include 'kafka-*' --exclude '*-manager'

# 모델 교체
uv run what-i-did octocat --model claude-opus-4-7

# AWS Bedrock 경로 (모델 id 는 Bedrock 형식)
uv run what-i-did octocat \
  --provider bedrock \
  --model 'global.anthropic.claude-sonnet-4-6'

# 출력 경로 (확장자 제외). .md 와 .docx 가 함께 생성됨
uv run what-i-did octocat --output ./out/portfolio-octocat

# 캐시 무시하고 전체 재분석
uv run what-i-did octocat --refresh

# 디버깅: 앞의 N개 repo 만
uv run what-i-did octocat --max-repos 2
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `USERNAME` | *(필수)* | 분석할 GitHub 사용자명 |
| `--include`, `-i` | — | repo 이름에 매칭할 glob. 매칭되는 것만 남김. 반복 가능. exclude 보다 먼저 적용 |
| `--exclude`, `-e` | — | repo 이름에 매칭할 glob. 반복 가능 |
| `--provider`, `-p` | `anthropic` | LLM 제공자: `anthropic` 또는 `bedrock` |
| `--model`, `-m` | `claude-sonnet-4-6` *(anthropic 일 때)* | 모델 id. bedrock 에서는 필수 |
| `--lang`, `-l` | `ko` | 출력 언어 (`ko` 또는 `en`) |
| `--output`, `-o` | `./what-i-did-<user>-<YYYYMMDD>` | 확장자를 뺀 출력 경로 |
| `--refresh` | off | 캐시를 무시하고 전체 재분석 |
| `--max-repos` | — | 분석할 repo 개수 상한 (디버그용) |
| `--cache-dir` | `~/.cache/what-i-did` | 캐시 디렉토리 |
| `--include-forks` | off | fork 된 repo 포함 |

## 출력물 구성

1. **전체 요약** — 모든 repo 분석을 근거로 LLM 이 한 단락 요약
2. **주요 프로젝트** — `is_toy=false` 판정된 repo 카드 (목적 · 주요 기능 · 사용 기술 · 구현 특이점 · 기여 범위)
3. **사이드 · 학습용 프로젝트** — 튜토리얼/템플릿 수준으로 판정된 repo
4. **기술 스택** — repo 간 집계된 기술 카운트 표

## 캐싱 동작

- 경로: `~/.cache/what-i-did/<username>/<repo>.json`
- 파일이 **존재하면 무조건 재사용**. LLM 재호출 없이 md/docx 만 다시 렌더링한다.
- `--refresh` 는 캐시를 전부 무시하고 재분석한다.
- repo 변경을 자동 감지하지는 않는다. cron 으로 주기 실행해도 저렴하게 유지되며, 갱신이 필요할 때는 명시적으로 `--refresh`.

### 여러 머신 간 캐시 공유 (캐시를 git 으로 백업)

`--cache-dir` 을 레포 안의 경로로 지정하면 분석 캐시가 레포에 함께 따라온다. 다른 머신에서 `git pull` 만으로 LLM 재호출 없이 문서를 재생성할 수 있다.

```bash
# 캐시를 레포 안 ./cache 에 쌓기
uv run what-i-did yunanjeong --cache-dir ./cache

# 캐시 파일 커밋
git add cache/
git commit -m "update analysis cache"
git push

# 다른 머신에서
git pull
uv run what-i-did yunanjeong --cache-dir ./cache   # LLM 호출 없이 캐시 재사용
```

**주의:** 캐시 파일에는 LLM 이 생성한 평가 텍스트(`user_contribution_notes` 에 "기여 범위 제한적" 같은 판정 포함 가능)가 들어간다. 본인 계정 분석 결과를 본인의 공개 레포에 담는 건 문제없지만, 타인 계정을 분석한 캐시를 공개 레포에 올리는 건 피하는 게 좋다.

## 토큰 사용량 (대략)

- 실행이 끝나면 합계 토큰이 출력된다.
- **첫 실행 (캐시 없음)**: 46개 repo 분석 시 입력 ~68만 / 출력 ~3만 토큰. `claude-sonnet-4-6` 기준 약 $2.5 수준.
- **두 번째 실행부터**: 캐시 파일이 있는 repo 는 LLM 호출 없이 그대로 재사용 → 전체 요약 1회(~$0.07) 만 발생. repo 가 변해도 자동 감지하지 않으니 갱신하려면 `--refresh`.

## 한계

- 공개 레포만 분석한다. private repo 는 지원하지 않는다.
- 비인증 GitHub REST 를 쓰므로 시간당 60회 제한을 받는다. repo 100개 내외까지는 문제 없다.
- 대용량 repo 는 150K자 예산 안에 우선순위 파일(README, manifest, entrypoint, 소스)만 넣어 분석한다. 잘린 경우 `truncated=true` 로 표기된다.
- 바이너리, lock 파일, `node_modules`, `dist`, `.git` 등은 자동 제외된다.

## 샘플

저장소에 `what-i-did-yunanjeong-*.md` / `.docx` 샘플이 포함되어 있다. 실제 실행 결과를 그대로 커밋한 것.

## 라이선스

MIT — [LICENSE](./LICENSE) 참고.
