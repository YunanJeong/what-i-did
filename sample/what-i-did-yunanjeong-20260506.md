# yunanjeong 의 포트폴리오

## 전체 요약

yunanjeong은 Apache Kafka 생태계(Connect, Streams, ksqlDB, MirrorMaker)를 중심으로 데이터 파이프라인 구축과 운영 자동화에 집중해온 개발자로, 커넥터 오프셋 제어·대량 커넥터 등록·커스텀 파티셔너 플러그인 개발 등 실무 운영 문제를 직접 코드로 해결한 사례가 다수 있다. Kubernetes 인프라 측면에서는 Helm 차트 작성, K3s 클러스터 구성, EKS 프로비저닝, Fluentd·Fluent Bit·Filebeat 기반 로그 수집 파이프라인, PLG 스택 및 멀티클러스터 Prometheus 모니터링 구성까지 관찰·수집·시각화 전 영역을 다루고 있다. Terraform과 Packer를 활용한 AWS IaC 작업도 꾸준히 이어져 있으며, EC2 위 Kafka 배포, EKS VPC 구성, GPU AMI 자동 빌드 등 다양한 클라우드 인프라 시나리오를 코드로 정의해왔다. Python으로는 Kafka Connect 관리 라이브러리, Prometheus 메트릭 수집 후 LLM 분석 리포팅 도구, S3-Athena 파티션 자동화, FTP-S3 데이터 수집 파이프라인 등 운영 자동화 유틸리티를 반복적으로 작성해왔으며, 최근에는 Anthropic API와 AWS Bedrock을 활용해 GitHub 레포지토리를 소스 코드 수준에서 분석하는 CLI 도구도 직접 제작했다.

## 주요 프로젝트

### [cmm](https://github.com/YunanJeong/cmm)
_스타: 2_
> Centralized Monitoring for Multi-clusters

**목적:** 여러 Kubernetes 클러스터를 중앙에서 통합 모니터링할 수 있도록 kube-prometheus-stack Helm 차트의 values를 구성한 프로젝트입니다. 각 클러스터에 Prometheus와 node-exporter를 배포하고, 중앙 노드의 Grafana에서 다수의 Prometheus를 datasource로 참조하는 멀티클러스터 모니터링 구조를 구현합니다.

**주요 기능:**
- 중앙 Grafana에 여러 클러스터의 Prometheus를 additionalDataSources로 등록하여 단일 대시보드에서 멀티클러스터 메트릭 조회
- 각 클러스터용 values 파일(each_cluster.yaml)과 중앙 모니터용 values 파일(central_monitor.yaml)을 역할별로 분리 구성
- Grafana 알림 규칙(메모리·스토리지 임계값 초과 감지)과 컨택포인트(이메일, MS Teams, LINE, AWS SNS)를 코드로 프로비저닝
- GitHub Raw URL을 통해 커스텀 Grafana 대시보드 JSON을 프로비저닝하여 차트 외부에서 대시보드 버전 관리
- envsubst를 활용한 환경변수 기반 민감정보(관리자 패스워드, SMTP, Webhook URL 등) 분리 적용
- serviceMonitorSelectorNilUsesHelmValues 설정으로 클러스터 내 모든 ServiceMonitor를 Prometheus 수집 대상으로 확장

**사용 기술:** Helm, kube-prometheus-stack, Prometheus, Grafana, Prometheus Operator, node-exporter, Alertmanager, Loki, Kubernetes, AWS SNS, Traefik

**구현 특이점:**
- 커스텀 Helm 차트나 template 편집 없이 values 파일만으로 멀티클러스터 중앙 모니터링 구조를 구현하여 유지보수 부담을 낮춤
- Grafana persistence.type을 statefulset으로 설정해 helm uninstall 후에도 데이터가 보존되도록 PVC 생명주기를 명시적으로 제어
- 대시보드 JSON을 레포지토리 Raw URL로 참조하는 방식으로, 차트 외부에서 대시보드를 독립적으로 버전 관리하는 구조 채택
- WSL·EKS 등 환경별 차이를 주석과 별도 reference 파일로 문서화하여 운영 환경 재현성을 확보

### [how-to-manage-git](https://github.com/YunanJeong/how-to-manage-git)
_Shell · 스타: 2_
> 개인 참고용

**목적:** 여러 로컬 Git 저장소에서 만료된 토큰을 일괄 교체하는 셸 스크립트와, Git 운용 중 자주 헷갈리는 브랜치·사용자 정보·태그·레포 통합 등의 노하우를 정리한 개인 참고 레포지토리입니다.

**주요 기능:**
- 환경변수로 OLD/NEW 토큰을 받아 보안 정보가 stdout에 노출되지 않도록 처리
- 루트 디렉터리 아래 모든 .git/config를 재귀 탐색하여 토큰을 일괄 교체
- 교체 대상 경로를 인자로 지정하거나 현재 디렉터리를 기본값으로 사용
- 브랜치·사용자 정보·태그·레포 통합 등 Git 운용 주제별 문서 정리

**사용 기술:** Shell, Git, sed, find

**구현 특이점:**
- set -euo pipefail로 오류·미정의 변수·파이프 실패 시 즉시 종료되도록 안전성을 확보한 점
- 토큰 값을 export 환경변수로만 주입하고 bashrc 등에 기록하지 말도록 스크립트 내 주석으로 명시한 보안 처리 방식
- GNU sed와 BSD sed의 -i 옵션 차이를 주석으로 명기하여 macOS 환경에서의 이식성 문제를 미리 안내한 점

### [kafka-connect-manager](https://github.com/YunanJeong/kafka-connect-manager)
_Python · 스타: 2_
> kafka connect에서 connector를 생성, 삭제, 관리하기 위한 라이브러리.실사용시 편의성을 고려하여 조금씩 개선해나간다.

**목적:** Kafka Connect REST API를 통해 커넥터를 등록·삭제·관리하기 위한 유틸리티 라이브러리. YAML/JSON/Python 형식의 커넥터 설정 파일을 작성하고, 이를 Kafka Connect에 일괄 배포하는 작업을 자동화한다.

**주요 기능:**
- YAML 설정 파일에서 공통(common) 항목과 개별 커넥터 항목을 분리하여 기술하고, 배포 시 병합하여 REST API로 전송
- Shell 스크립트(apply-connectors.sh) 단일 파일로 YAML → JSON 변환 후 HTTP PUT으로 커넥터 등록 및 업데이트
- plan-connectors.sh로 실제 전송 없이 최종 커넥터 설정과 curl 명령어를 미리 출력해 검증
- Python lib/connect.py의 Connector 클래스로 커넥터 생성·삭제·조회를 추상화하고, suffix 옵션으로 테스트용 커넥터 이름을 구분 등록
- lib/broker.py로 Kafka 토픽 생성·삭제·레코드 조회를 래핑하여 커넥터 등록 전 토픽 준비를 자동화
- JDBC Source Connector를 임시 생성·조회 후 자동 삭제하는 방식으로 DB 쿼리 결과를 일회성으로 확인하는 테스트 유틸 제공

**사용 기술:** Python, Shell, Kafka Connect, Kafka, yq, jq, kcat, requests, PyYAML, envsubst, curl

**구현 특이점:**
- 메시지 전달 로직(lib/)과 커넥터 설정(config/)을 명시적으로 분리하여, 설정 변경이 코드 수정 없이 YAML/Python 파일만으로 이루어지도록 설계
- Python 기반 legacy 앱에서 Shell 단일 파일 방식으로 점진적으로 전환하면서 두 접근법을 병행 제공하고, POST 대신 PUT을 채택해 등록과 업데이트를 단일 명령으로 처리
- envsubst를 활용해 YAML 설정 내 ${DB_HOST} 같은 환경변수 자리를 배포 시점에 주입하여 자격증명을 설정 파일에서 분리
- apply-connectors-debian.sh와 apply-connectors.sh로 의존성 구성(python-yq vs go-yq)을 분리해 컨테이너·폐쇄망 등 환경별 배포 제약에 대응

### [kafka-connect-s3-without-topicname](https://github.com/YunanJeong/kafka-connect-s3-without-topicname)
_Shell · 스타: 2_
> Custom Partitioner: TopiclessTimeBasedPartitioner

**목적:** Kafka S3 Sink Connector의 기본 파티셔너가 S3 경로에 토픽명을 포함시키는 문제를 해결하기 위해, 토픽명 없이 시간 기반 파티셔닝 경로를 생성하는 커스텀 파티셔너 플러그인입니다.

**주요 기능:**
- TimeBasedPartitioner를 상속하여 generatePartitionedPath 메서드를 오버라이드, S3 경로에서 토픽명 세그먼트를 제거
- Maven 프로젝트로 패키징하여 기존 S3 Sink Connector 디렉토리에 jar 파일로 추가 가능
- 커스텀 파티셔너 클래스명을 connector 설정 파일에 지정하는 방식으로 기존 S3 Sink Connector와 연동
- S3 Sink Connector 및 커스텀 파티셔너가 미리 통합된 Docker 이미지를 빌드·배포하는 스크립트 제공
- Docker Hub에 이미지를 퍼블리시하여 Kubernetes 등 컨테이너 환경에서 즉시 사용 가능하도록 구성

**사용 기술:** Java, Maven, Kafka Connect, Confluent kafka-connect-storage-partitioner, Docker, Shell

**구현 특이점:**
- 단 5줄의 Java 코드로 confluent의 TimeBasedPartitioner를 상속해 generatePartitionedPath만 오버라이드함으로써 S3 경로 구조를 변경—최소한의 코드로 원하는 동작을 정확히 구현
- pom.xml에 confluent Maven 저장소와 kafka-connect-storage-partitioner 의존성만 선언하여, S3 Sink Connector가 이미 보유한 의존성과 중복을 최소화하는 경량 jar 구성
- build_sinkcon.sh에서 S3 Sink Connector와 커스텀 파티셔너 jar를 각각 wget으로 내려받아 조합한 Docker 이미지를 빌드·태깅·푸시까지 자동화
- README에서 S3 경로 형식 변화(<prefix>/<topic>/<encodedPartition> → <prefix>/<encodedPartition>)를 before/after로 명시하고, 파일명 변경을 지양하는 이유(offset 트러블슈팅)까지 설계 의도를 구체적으로 문서화

### [linux-tips](https://github.com/YunanJeong/linux-tips)
_Shell · 스타: 2_
> Linux Tips mainly for Ubuntu/Debian, WSL2

**목적:** Ubuntu/Debian 및 WSL2 환경에서 반복적으로 필요한 Linux 운영 지식을 주제별로 정리한 개인 참고 문서 저장소입니다. 파일 시스템, 패키지 관리, 권한 설정, 백그라운드 실행 등 실무에서 자주 마주치는 상황에 대한 명령어와 해설을 담고 있습니다.

**주요 기능:**
- dpkg/apt를 활용한 오프라인 환경용 .deb 패키지 추출 스크립트 3종 제공 (apt-cache, apt-cache depends, apt-rdepends 방식 비교)
- Confluent Schema Registry 및 Confluent Community 패키지를 오프라인 배포용으로 추출하는 자동화 스크립트 작성
- root 권한이 필요한 경로에 파일을 쓰는 두 가지 방법(sudo mv, sudo tee) 정리 및 원인 설명
- file descriptor 임시/영구 설정 방법과 systemd 서비스 파일에서의 LimitNOFILE 적용 방법 안내
- vim 컬러 및 인덴트 설정을 일반 계정과 root 계정 양쪽에 적용하는 .vimrc 구성 및 원격 빠른 설치 스크립트 제공
- Gemini CLI의 계층형 설정(Global/Local) 구조와 보안 설정 파일 템플릿 구성 가이드 작성

**사용 기술:** Shell, Bash, apt, dpkg, systemd, vim, WSL2, Docker, ncftp, DBeaver, Gemini CLI

**구현 특이점:**
- dpkg 추출 방식을 3가지 접근법으로 분류하고 각각의 장단점을 명시하여 상황에 따라 선택할 수 있도록 구성한 점
- sudo가 리다이렉션(>)에 적용되지 않는 원인을 설명하고 /tmp 경유 이동과 sudo tee 두 가지 해결책을 함께 제시한 점
- vim 설정을 일반 계정과 sudo vi 양쪽에 적용하기 위해 /root/.vimrc와 ~/.vimrc를 분리해야 하는 이유를 구체적으로 설명하고 원라이너 설치 스크립트까지 포함한 점
- Gemini CLI의 Global/Local 설정 우선순위 구조를 정리하고 .geminiignore, settings.json, GEMINI.md 역할을 구분한 프로젝트 템플릿을 제공한 점

### [plg-stack](https://github.com/YunanJeong/plg-stack)
_스타: 2_
> Promtail, Loki, and Grafana for K8s Log Monitoring

**목적:** Kubernetes 클러스터의 컨테이너 로그를 수집·저장·시각화하기 위한 PLG(Promtail + Loki + Grafana) 스택 Helm values 구성 모음입니다. EKS를 포함한 다양한 K8s 환경에 맞춰 바로 적용할 수 있도록 시나리오별 values 파일을 제공합니다.

**주요 기능:**
- Promtail DaemonSet으로 K8s 컨테이너 로그를 수집하여 Loki에 푸시
- Loki Compactor 기반 retention 정책 설정으로 로그 보존 기간 제어
- EKS 환경 전용 values 파일에서 ECR 프라이빗 레지스트리 이미지, NLB 어노테이션, EBS PV 마이그레이션 절차를 포함한 배포 구성 제공
- 정적/동적 PV 프로비저닝 양쪽을 지원하는 PVC·PV 매니페스트 및 loki-stack 차트의 동적 프로비저닝 강제 동작 우회 방법 구현
- Grafana 대시보드(gnetId 13639, 15141, 22874)를 values에서 선언적으로 프로비저닝
- Promtail에 system-node-critical PriorityClass와 NoSchedule toleration을 설정하여 신규 노드 진입 시 로그 수집 누락 방지

**사용 기술:** Helm, Loki, Promtail, Grafana, Kubernetes, Amazon EKS, Amazon EBS, AWS Load Balancer Controller, Karpenter

**구현 특이점:**
- loki-stack 차트가 storageClassName 빈 문자열과 미기입을 구분하지 못해 정적 프로비저닝이 강제 동작하는 버그를 분석하고, 별도 PVC·PV 매니페스트 사전 생성 + existingClaim 참조 방식으로 우회하는 구체적인 해법을 문서화 및 구현
- EBS PV 마이그레이션 시나리오(스냅샷 → 복제 EBS → PV 매니페스트 재생성 → 신규 Helm 배포)를 loki-eks-ebs-pv.yaml 파일과 주석으로 절차화
- promtail-loki-affinity.yaml에서 Karpenter nodepool 레이블 기반 OR/AND 복합 nodeAffinity 조건을 활용해 특정 고부하 노드를 Promtail 스케줄링에서 제외하는 패턴 구현
- too many outstanding requests 오류 대응으로 querier.max_concurrent 및 query_scheduler.max_outstanding_requests_per_tenant를 2048로 조정하는 설정을 별도 EKS values에 명시

### [terraform-test](https://github.com/YunanJeong/terraform-test)
_HCL · 스타: 2_
> AWS IaC Modules, UseCases, Test

**목적:** AWS EC2 인프라를 코드로 관리하기 위한 Terraform IaC 모듈 모음으로, Ubuntu 및 Windows SQL Server 인스턴스의 프로비저닝부터 보안그룹 설정, DB 초기화까지 재사용 가능한 형태로 구성되어 있습니다.

**주요 기능:**
- Ubuntu 단일/다중 EC2 인스턴스를 모듈 호출 한 번으로 생성하고 SSH remote-exec로 초기 명령어 실행
- Windows Server + SQL Server EC2 인스턴스를 user_data 기반 WinRM 초기화 및 winrm remote-exec로 자동 프로비저닝
- template_file을 활용해 DB 사용자·비밀번호·포트를 변수로 주입한 SQL 초기화 스크립트를 원격 인스턴스에 전송 및 실행
- 보안그룹(SSH, DB, WinRM, 인스턴스 간 상호통신)을 용도별로 모듈화하여 여러 인스턴스에 재사용 가능하게 구성
- null_resource와 depends_on을 조합해 기존 실행 중인 GitLab 인스턴스에 신규 보안그룹을 추가한 뒤 순서 보장된 remote-exec 실행
- setup-infra-examples 디렉터리에 단일 Ubuntu, SQL Server, 복합 구성, 다중 Ubuntu 등 사용 시나리오별 예제 제공

**사용 기술:** Terraform, HCL, AWS EC2, AWS Security Groups, WinRM, SQL Server, PowerShell, T-SQL

**구현 특이점:**
- multi_ubuntu 모듈에서 count로 생성된 인스턴스의 public/private IP 전체를 for 표현식으로 순회해 /32 CIDR로 변환 후 상호통신 보안그룹에 동적으로 주입하는 방식을 구현
- AWS EC2 Windows에서 SSH·WinRM 직접 연결이 동작하지 않는 문제를 user_data PowerShell 스크립트로 WinRM을 사전 초기화하여 우회하고, rsadecrypt로 password_data를 복호화해 연결하는 방법을 직접 검증하고 문서화
- null_resource + depends_on 패턴을 사용해 기존 인스턴스(GitLab)에 보안그룹이 추가된 이후에만 신규 인스턴스의 git clone이 실행되도록 리소스 간 실행 순서를 명시적으로 제어
- 보안그룹 등록을 aws_network_interface_sg_attachment로 분리하여 이미 실행 중인 인스턴스에도 사후 보안그룹을 붙일 수 있는 register_sgroup 모듈을 별도 추상화

### [container-orchestration](https://github.com/YunanJeong/container-orchestration)
_Shell · 스타: 1_
> Container Orchestration Tips, Examples, Practice

**목적:** Docker 및 Kubernetes 환경을 실무·학습 양쪽에서 활용하기 위한 컨테이너 오케스트레이션 설정 모음으로, Docker 설치·데몬 구성부터 K3s 클러스터 구축, EKS Karpenter 노드풀 정의까지 다룬다.

**주요 기능:**
- Docker Engine 설치 자동화 및 데몬 옵션(로그 드라이버, 프라이빗 레지스트리, overlay2 스토리지) 스크립트로 구성
- K3s 컨트롤플레인 설치와 kubectl 별칭·kubeconfig 권한 설정을 단일 셸 스크립트로 자동화
- K3s 1년 만료 인증서를 매월 1일 자동 갱신하는 crontab 등록 스크립트 작성(server/agent 노드 자동 판별 포함)
- Pod·ReplicaSet·Deployment·Service(ClusterIP/NodePort/LoadBalancer)·Ingress 오브젝트를 단계별 예제 매니페스트로 구성
- MetalLB를 이용한 로컬 LoadBalancer 환경 구성(K3s용, minikube용 각각 분리)
- AWS EKS Karpenter v1 API 기반 EC2NodeClass·NodePool 정의 샘플 작성(v1beta1 → v1 변경사항 주석 포함)

**사용 기술:** Docker, Docker Compose, Kubernetes, K3s, Helm, k9s, MetalLB, Karpenter, Redis, MariaDB, WordPress, Kafka UI, Grafana, Shell

**구현 특이점:**
- daemon.json 생성 스크립트에서 로그 max-size·max-file, overlay2 스토리지 드라이버, insecure-registry를 환경변수 기본값 패턴(URL_DOCKER:-"docker.wai")으로 처리해 재사용성을 높임
- K3s 인증서 갱신 스크립트가 systemctl is-active로 현재 노드 역할(server vs agent)을 런타임에 판별한 뒤 각각 다른 cron 명령을 등록하는 구조로 작성됨
- Karpenter v1 매니페스트에 v1beta1 대비 변경된 필수 필드(amiSelectorTerms, group/kind in nodeClassRef, consolidateAfter, expireAfter 위치 이동)를 인라인 주석으로 명시해 마이그레이션 참조 자료로 활용 가능
- Ingress 예제에서 subpath 리다이렉션이 정상 동작하지 않는 이유(앱 자체 내부 리다이렉션 충돌)를 주석으로 직접 분석하고 helm 설정 우회 방법을 제안

### [kafka-tips](https://github.com/YunanJeong/kafka-tips)
_HCL · 스타: 1_
> Kafka Tips for operations, test, deploy, customize

**목적:** Apache Kafka의 배포, 운영, 커넥터 관리에 필요한 Terraform 인프라 코드와 Python 유틸리티, 운영 노하우를 한 곳에 정리한 레퍼런스 저장소입니다. AWS EC2 위에서 Kafka 브로커·Connect·ksqlDB를 설치·구성하는 PoC 모듈과, 실제 운영에서 발생하는 커넥터 오프셋 제어 문제를 다루는 도구를 포함합니다.

**주요 기능:**
- Terraform으로 AWS EC2에 Apache Kafka 및 Confluent Platform을 설치 유형별(바이너리, deb 패키지)로 자동 프로비저닝
- Kafka Connect를 distributed 모드 및 systemd 서비스로 구성하고 JDBC Source·S3 Sink·Debezium 커넥터를 연결
- JDBC Source Connector의 connect-offsets 토픽을 직접 조작하여 다수 커넥터의 오프셋을 특정 시점으로 되돌리는 셸 스크립트 워크플로우 제공
- Python requests를 이용한 Kafka Connect REST API 커넥터 등록·조회·삭제 유틸리티 및 다양한 모드(incrementing, timestamp, bulk, query) 테스트 예제 제공
- Kafka 0.9 레거시 브로커에서 최신 버전(3.4)으로 MirrorMaker를 통해 미러링하는 환경 구성
- Windows SQL Server EC2 인스턴스를 WinRM으로 원격 초기화하고 Debezium CDC 커넥터와 연동하는 Terraform 모듈 구성

**사용 기술:** Terraform, HCL, AWS EC2, Apache Kafka, Confluent Platform, Kafka Connect, ksqlDB, Debezium, JDBC Source Connector, S3 Sink Connector, Python, requests, jq, kcat, Bash, systemd, Microsoft SQL Server

**구현 특이점:**
- connect-offsets 오프셋 주입 시 파티션을 명시하지 않고 key 해싱 자동 배치를 활용하도록 설계하여, 잘못된 파티션 주입으로 인한 오프셋 미인식 문제를 명시적으로 방지하고 있음
- Terraform template_file로 AWS 퍼블릭 DNS, AWS 자격증명 등 환경별 가변값을 server.properties와 systemd 서비스 파일에 렌더링하여 주입하는 방식으로 설정 파일의 재사용성을 확보
- PoC 디렉토리를 0번부터 8번까지 점진적 확장 구조(broker → connect → systemd → connector → ksqlDB → Confluent 패키지 방식 → Debezium → 레거시)로 구성하여 각 모듈이 이전 단계 위에 쌓이는 관계를 명확히 표현
- cutoff ID 선택 로직에서 타겟 시간 직후 행의 id-1을 사용하여 중복은 허용하되 누락은 방지하는 정책을 스크립트에 명시적으로 구현

### [kstreams-deploy](https://github.com/YunanJeong/kstreams-deploy)
_Java · 스타: 1_
> on Kubernetes

**목적:** Kafka Streams 애플리케이션을 Kubernetes 환경에서 빌드하고 배포하기 위한 예시 및 템플릿 모음이다. 다양한 스트림 처리 패턴(필터링, 분기, 스키마 주입, 시간 기반 토픽 분리 등)을 각각 독립적인 컨테이너 이미지와 Helm value 파일로 관리한다.

**주요 기능:**
- 정규식 기반 다중 토픽 구독 및 JSON 필터링·키 재할당 처리
- split()/branch()를 활용한 조건부 토픽 분기 및 에러 라우팅
- 메시지 타임스탬프 기반 동적 출력 토픽명 생성(연월 suffix 자동 부여)
- DB 적재용 스키마(schema+payload) 주입 및 SHA-256 해시 기반 파티션 키 생성
- STREAMS_ 환경변수 prefix를 Kafka 클라이언트 설정 키로 동적 변환 및 유효성 검증
- Skaffold 프로파일을 통해 이미지 빌드부터 Helm 배포까지 단일 명령으로 실행

**사용 기술:** Java, Kafka Streams, Apache Kafka, Jackson, Maven, Gradle, Docker, Kubernetes, Helm, Skaffold, JUnit Jupiter, Logback, SLF4J, commons-codec, logstash-logback-encoder, system-stubs-jupiter

**구현 특이점:**
- KafkaClientPropertiesLoader 클래스에서 리플렉션으로 StreamsConfig·ConsumerConfig·ProducerConfig 등 주요 Kafka 설정 클래스의 static String 상수를 수집해 유효한 설정 키 집합을 빌드하고, 환경변수에서 변환된 키가 이 집합에 없으면 IllegalArgumentException을 던지는 런타임 검증 로직을 구현했다.
- Jackson의 readTree()가 단일 문자열·숫자·boolean 값을 JsonNode로 파싱해버리는 동작을 인식하고, isObject() || isArray() 조건으로 엄밀한 JSON 객체/배열 여부를 판별하는 isValidJsonString() 메서드를 별도로 작성했으며, 이를 두 가지 구현(IsValidJson vs IsValidJsonException)으로 나누어 동작 차이를 테스트로 검증했다.
- TimeUtils 클래스를 불변 유틸리티(private 생성자, static final 포맷터)로 설계하여 스레드 안전성을 확보하고, TZ 환경변수 미설정 시 Asia/Seoul을 기본값으로 사용하도록 Optional로 처리했다.
- skaffold.yaml을 프로파일 기반으로 구성하여 각 스트림 앱의 Docker context, 이미지명, Helm value 파일을 프로파일 단위로 격리하고 setValueTemplates로 빌드된 이미지 태그를 배포 시점에 자동 주입하도록 설계했다.

### [nexus-repos](https://github.com/YunanJeong/nexus-repos)
_Shell · 스타: 1_
> by helm

**목적:** Sonatype Nexus Repository Manager를 Kubernetes(K3s) 환경에 Helm으로 배포하고 운영하기 위한 설정 및 유틸리티 모음입니다. Docker, PyPI, APT, raw 파일 등 다양한 패키지 저장소를 사설 인프라에서 운영할 수 있도록 구성 절차와 활용법을 정리합니다.

**주요 기능:**
- K3s 설치 및 Helm 연결을 자동화하는 셸 스크립트 제공
- 최소 구성·기본값·프로덕션 예시의 세 가지 Helm values 파일을 용도별로 분리하여 제공
- Docker Registry API v2를 호출해 저장소 내 이미지별·태그별 실제 레이어 크기를 집계하는 스크립트 구현
- 멀티 아키텍처(manifest list) 이미지와 단일 아키텍처 이미지를 분기 처리하여 용량 산출
- Traefik Ingress를 통한 도메인 기반 접근 및 사설 Docker 레지스트리 이중 등록(docker.wai / private.docker.wai) 설정
- 프로덕션 값 파일에 JVM 메모리 튜닝 옵션 및 Nexus DB 마이그레이션 유의사항 주석으로 문서화

**사용 기술:** Sonatype Nexus3, Helm, Kubernetes, K3s, Traefik, Docker Registry API v2, Shell, jq, YAML

**구현 특이점:**
- getEachSize.sh에서 /v2/_catalog → 태그 목록 → 매니페스트 순으로 API를 단계적으로 호출하고, manifests 키 존재 여부로 멀티 아키텍처 이미지를 감지해 플랫폼별 digest를 순회하며 레이어 크기를 합산하는 로직을 직접 구현
- 프로덕션 values 파일에서 -XX:+UseContainerSupport 플래그로 컨테이너 환경의 CPU 인식 문제를 명시적으로 처리하고, Nexus 3.71 이상의 OrientDB→H2 DB 마이그레이션 필요성을 이미지 태그 주석에 기록하여 운영 리스크를 문서화
- value_minimum_set.yaml과 value_production_example_set.yaml을 분리해 스토리지 크기(8Gi vs 150Gi), 서비스 타입(ClusterIP vs LoadBalancer), Docker 레지스트리 수 등 실제 운영 규모 차이를 명확히 구분

### [Algorithm-OptimalBST](https://github.com/YunanJeong/Algorithm-OptimalBST)
_Java_
> Algorithm Project - Translator by Optimal Binary Search Tree

**목적:** 영어 단어의 출현 빈도를 기반으로 최적 이진 탐색 트리(Optimal BST)를 구성하고, 이를 활용해 영어 텍스트를 한국어로 번역하는 프로그램입니다.

**주요 기능:**
- 입력 파일에서 단어 출현 빈도를 집계하고 확률을 계산하여 데이터 테이블 구성
- 동적 프로그래밍 방식으로 비용 행렬(mainTable)과 루트 행렬(rootTable)을 재귀적으로 채워 Optimal BST 구축
- rootTable을 기반으로 실제 BSTNode 트리 구조를 재귀적으로 생성
- BST 탐색을 통해 영어 단어를 한국어로 변환하고 결과를 output.txt에 저장
- Apache Commons Lang의 StringUtils를 활용해 줄 단위 단어 빈도 집계 처리

**사용 기술:** Java, Apache Commons Lang

**구현 특이점:**
- calculateMainRootTableValue가 i, j, startColumn 세 파라미터로 대각선 방향 순회를 재귀 호출로 구현하여 DP 테이블 전체를 채우는 구조가 비자명하게 설계됨
- ConstructManager, FrequencyManager, TranslateManager로 역할을 분리해 각 단계(빈도 수집 → 트리 구축 → 번역)가 독립적으로 관리됨
- 확률 기반 가중치를 누적 합산하여 최소 비용 루트를 선택하는 Optimal BST 알고리즘 핵심 로직이 직접 구현됨

### [ansible-test](https://github.com/YunanJeong/ansible-test)

**목적:** Ansible을 처음 설정하고 사용하는 과정에서 필요한 설치 방법, 핵심 개념, 사전 준비 작업을 정리한 학습 및 참고용 노트입니다.

**주요 기능:**
- Python, Ubuntu, CentOS, macOS 등 다양한 환경별 Ansible 설치 방법 정리
- Control Node / Managed Node / Inventory 등 핵심 용어 및 개념 설명
- WSL과 EC2 조합 등 실제 테스트 환경 구성 사례 기록
- Ansible 초기 셋업 시 공통적으로 겪는 ssh 연결 및 인프라 환경 준비 작업 안내

**사용 기술:** Ansible, Python, Ubuntu, CentOS, AWS EC2, WSL

**구현 특이점:**
- 여러 배포판·환경에서의 버전별 설치 방법을 한 곳에 모아 실무 참조 용도로 구성
- 블로그 튜토리얼에서 자주 생략되는 사전 준비 단계(ssh 연결, 인프라 셋업)를 별도 문서(0_ready.md)로 분리해 안내

### [db-helm](https://github.com/YunanJeong/db-helm)

**목적:** Kubernetes 환경에서 MySQL을 빠르게 배포하고 반복 테스트할 수 있도록 Bitnami Helm 차트용 values 설정을 정리한 레포지토리입니다. WSL, EC2 등 다양한 환경에서 겪은 접속 이슈와 해결 방법도 함께 기록되어 있습니다.

**주요 기능:**
- Bitnami MySQL Helm 차트(11.1.2) 배포에 사용할 커스텀 values 파일 작성
- Primary 서비스를 LoadBalancer 타입으로 노출하여 클러스터 외부에서 3306/33060 포트로 직접 접근 가능하도록 구성
- 테스트 편의를 위해 liveness·readiness·startup probe를 모두 비활성화하고 PersistentVolume도 비활성화하는 옵션 적용
- Secondary 레플리카 수를 0으로 설정해 단독 Primary 구성으로 간소화
- localhost vs 127.0.0.1 소켓/TCP 접근 차이 및 WSL 환경의 초기화 지연 원인 분석 및 문서화
- Helm install/upgrade 명령어와 MySQL 클라이언트 접속 방법을 재사용 가능한 형태로 정리

**사용 기술:** Helm, Bitnami MySQL, Kubernetes, MySQL

**구현 특이점:**
- 단순 values 복사가 아니라 테스트 시나리오에 맞게 probe 전체 비활성화·PV 비활성화·Secondary replicaCount 0을 의도적으로 조합해 최소 구성을 설계한 점
- localhost 접속 실패 원인을 소켓 통신 경로 문제로 정확히 진단하고, 127.0.0.1로 우회하는 해결책을 실제 에러 메시지와 함께 문서화한 점
- WSL 환경에서 발생하는 MySQL 서버 업그레이드 프로세스 지연을 로그 타임스탬프로 특정하고, 회사 네트워크·방화벽 가설을 포함해 재현 조건을 기록한 점

### [devenv-windows-java-intellij-git](https://github.com/YunanJeong/devenv-windows-java-intellij-git)

**목적:** Windows 환경에서 IntelliJ와 Java 개발 환경을 구성할 때 겪을 수 있는 시행착오와 설정 방법을 정리한 가이드 레포지토리입니다. WSL2 연동 및 Git 설정 관련 주의사항을 실용적인 관점에서 기록합니다.

**주요 기능:**
- Windows에서 IntelliJ + Java + Git 빠른 초기 설정 방법 안내
- IntelliJ에서 WSL2 경로의 프로젝트를 열어 리눅스 환경으로 개발하는 방법 설명
- WSL2 + IntelliJ 조합에서 Gradle 미지원(Maven만 가능) 이슈 명시
- IntelliJ Git 커밋 시 전역/로컬 git config 적용 방식 차이 정리
- Git Bash 미설치 시 IntelliJ가 WSL2의 .gitconfig를 수정하는 동작 및 다중 계정 주의사항 기록
- 예제 Gradle 프로젝트(JUnit 5 기반) 포함

**사용 기술:** Java, IntelliJ IDEA, Gradle, Git, WSL2, JUnit Jupiter

**구현 특이점:**
- IntelliJ가 Git Bash 없이 전역 커밋을 시도할 때 WSL2의 .gitconfig를 수정하며 IncludeIf 조건이 무시된다는 비자명한 동작을 직접 검증해 문서화한 점
- WSL2 + IntelliJ 조합에서 Gradle이 오류를 일으키고 Maven만 정상 동작한다는 실사용 제약을 명확히 명시
- 다중 Git 계정(개인/업무) 환경에서 발생할 수 있는 config 충돌 상황과 대응 방안을 구체적으로 기술

### [ec2-k8s-deploy](https://github.com/YunanJeong/ec2-k8s-deploy)
_HCL_
> ec2-k8s-deploy

**목적:** AWS EC2 인스턴스 위에 Terraform을 사용해 K3s 기반 Kubernetes 클러스터를 자동으로 프로비저닝하는 IaC 프로젝트입니다. 컨트롤플레인과 다수의 에이전트 노드를 한 번의 명령으로 구성할 수 있습니다.

**주요 기능:**
- Terraform 변수 파일(config.tfvars)로 노드 수, AMI, 볼륨 등 클러스터 규모를 파라미터화하여 구성
- EC2 인스턴스 프로비저닝 후 SSH remote-exec로 K3s 컨트롤플레인·에이전트 노드를 자동 설치 및 연결
- 컨트롤플레인 노드에서 서버 토큰을 로컬로 추출한 뒤 에이전트 노드에 전달하는 멀티노드 조인 흐름 구현
- Nexus(Docker 레지스트리, 파일 저장소)·GitLab 보안그룹에 EC2 인스턴스 IP를 동적으로 허용 규칙으로 등록
- Docker daemon.json을 통한 사설 레지스트리 및 로그 설정(max-size 10m) 포함 Docker 설치 자동화
- K3s 인증서 1년 만료에 대비해 서버·에이전트 노드 역할을 자동 판별하고 월별 cron 갱신 작업을 등록

**사용 기술:** Terraform, HCL, AWS EC2, AWS Security Groups, K3s, Docker, Helm, k9s, Bash

**구현 특이점:**
- 보안그룹 생성 후 인스턴스에 추가하는 방식 대신 기존 저장소 보안그룹에 규칙을 직접 추가하는 방식을 택해, 인스턴스당 보안그룹 개수 제한 문제를 의도적으로 회피한 설계
- 컨트롤플레인 설치 완료 후 local-exec로 node-token을 로컬 파일에 저장하고, 이후 에이전트 null_resource가 해당 파일을 읽어 K3S_TOKEN 환경변수로 주입하는 순차적 의존성 체인 구성
- install_cron_k3s_cert_rotate.sh에서 systemctl 상태 확인으로 노드 역할(server/agent)을 런타임에 판별한 뒤 각각 다른 cron 커맨드를 등록하여 단일 스크립트로 양쪽 노드 유형을 처리
- Docker 로그 max-size를 10m으로 설정하고 K3s kubelet 기본값과 일치시켜 불필요한 에러 메시지 발생을 방지한 운영 디테일 반영

### [efk-tester-by-terraform](https://github.com/YunanJeong/efk-tester-by-terraform)
_HCL_
>  This repository quickly & automatically creates an Elastic(ELK, EFK) stack testbed on AWS with Terraform IaC.

**목적:** Terraform IaC를 사용해 AWS 위에 EFK(Elasticsearch + Fluentd + Kibana) 스택 테스트 환경을 자동으로 프로비저닝하는 도구입니다. 새로 생성된 인스턴스의 IP와 호스트명을 설정 파일에 자동 반영하여 스택 간 연결을 즉시 구성합니다.

**주요 기능:**
- AWS EC2 인스턴스 및 보안 그룹을 Terraform으로 자동 생성·할당
- 신규 인스턴스의 public IP와 private hostname을 Terraform template_file로 EFK 설정 파일에 동적 주입
- SSH remote-exec provisioner로 원격 인스턴스에 설정 파일 전송 및 서비스 재시작 자동화
- AMI 재사용 방식(fast-tester)과 설치부터 진행하는 방식(version-install) 두 가지 시나리오 제공
- version-install 모드에서 가용 RAM의 절반을 Elasticsearch 힙 메모리로 자동 설정
- Fluentd beats 플러그인(fluent-plugin-beats)을 원격 인스턴스에 자동 설치

**사용 기술:** Terraform, HCL, AWS EC2, AWS Security Groups, Elasticsearch, Kibana, Fluentd, td-agent, Filebeat

**구현 특이점:**
- Fluentd 설정 파일의 `$` 변수 표기와 Terraform template_file의 `$` interpolation이 충돌하는 문제를 `$$` 이스케이프로 해결하고, 그 이유를 README에 별도 문서화함
- elasticsearch 보안 그룹의 9200 포트 허용 CIDR을 `concat(var.my_ip_list, [fluentd 인스턴스 public IP])`로 동적 구성하여 불필요한 공개 노출 없이 스택 내부 통신을 허용
- `cloud-init status --wait` 명령을 remote-exec 첫 줄에 두어 인스턴스 초기화 완료 전 명령 실행으로 인한 오류를 방지
- 가용 RAM을 `free --giga`로 조회한 뒤 절반 값을 셸 연산으로 계산하여 jvm.options에 동적 주입하는 방식으로 인스턴스 사양에 무관한 힙 설정을 구현

### [eks-deploy](https://github.com/YunanJeong/eks-deploy)
_HCL_
> eks-deploy-terraform

**목적:** Terraform을 사용하여 AWS 환경에 EKS 클러스터와 전용 VPC 네트워크 인프라를 자동으로 프로비저닝하는 IaC 모듈입니다. 다른 프로젝트와 격리된 독립적인 Kubernetes 운영 환경을 코드로 정의하고 배포할 수 있습니다.

**주요 기능:**
- EKS 전용 VPC, 서브넷, 인터넷 게이트웨이를 신규로 완전 생성하여 환경 격리
- 워커 노드를 프라이빗 서브넷에 배치하고 NAT 게이트웨이를 통해 외부 통신 제어
- 퍼블릭 서브넷을 별도 구성하여 ALB/NLB 로드 밸런서 배치 지원
- AWS 공식 Terraform 모듈을 활용해 EKS Control Plane-노드 간 보안 그룹 및 IAM 역할 자동 구성
- params.tf에 리전, 클러스터명, 노드 사양 등 자주 변경되는 변수를 분리하여 재사용성 확보
- outputs.tf를 통해 생성된 리소스 주요 정보 출력

**사용 기술:** Terraform, HCL, AWS EKS, AWS VPC, AWS NAT Gateway, AWS IAM, Kubernetes

**구현 특이점:**
- 단일 NAT 게이트웨이(single_nat_gateway = true) 옵션을 기본값으로 설정하되, README에 운영 환경에서의 변경 방향을 명시해 비용과 가용성 트레이드오프를 의식적으로 문서화한 점
- 변경 빈도가 높은 파라미터(리전, 클러스터명, 노드 사양)를 params.tf로 분리하여 설정 변경 시 다른 파일을 수정하지 않아도 되는 구조를 설계
- 로컬 tfstate 기본 구성에서 S3+DynamoDB 원격 백엔드로의 전환 방향을 주의 사항에 포함하여 협업·운영 확장성을 고려한 설계 의도를 명시

### [flink-test](https://github.com/YunanJeong/flink-test)

**목적:** Apache Flink를 직접 설치·운용해보며 Kafka Connect 및 Kafka Streams와의 역할 비교 및 적용 가능성을 탐색하는 테스트 레포지토리입니다.

**주요 기능:**
- Flink를 분석 도구로서 평가 및 검토
- Kafka Connect + Kafka Streams 조합과 Flink 간의 처리량·속도 비교 분석
- 대규모 데이터 처리 시나리오에서의 Flink 적용 가능성 검토
- 코딩 자유도 측면에서 Flink의 활용 범위 정리

**사용 기술:** Apache Flink, Apache Kafka, Kafka Connect, Kafka Streams

**구현 특이점:**
- Kafka 생태계 내에서 Flink의 포지셔닝을 처리량, 자유도, 운영 비용 측면으로 나누어 실용적으로 정리한 점
- 단순 기술 나열이 아니라 기존 스택과의 중복성 및 도입 비용을 함께 고려한 현실적인 관점이 담겨 있음

### [fluentd-helm](https://github.com/YunanJeong/fluentd-helm)
_Dockerfile_
> Multi-platform Interoperability on Kubernetes

**목적:** Kubernetes 환경에서 Fluentd를 Helm으로 배포하고, Kafka·Loki·Redis 등 이기종 데이터 플랫폼 간 파이프라인을 구성하기 위한 설정 템플릿 및 참고 레포지토리입니다. HTTP 수신부터 Kafka Produce/Consume, Beats 수신, 플랫폼 간 포워딩까지 다양한 연동 시나리오를 Helm values 파일 단위로 제공합니다.

**주요 기능:**
- Kafka Produce/Consume 파이프라인 구성 (kafka2, rdkafka2, kafka_group, rdkafka_group 플러그인 대응 values 파일 제공)
- SASL 인증이 적용된 Kafka 연동 설정 구성 (scram sha256/sha512)
- Filebeat(fluent-plugin-beats) 수신 후 topic_key 기반 멀티토픽 Kafka 라우팅 및 다중 Pod 스케일 아웃 구성
- 오프라인 환경에서 initContainer와 emptyDir 볼륨을 활용한 gem 플러그인 설치 방법 구현
- fluentd 멀티워커(<system> workers) 설정과 worker_id 기반 파일 버퍼 식별자 적용
- Loki·Redis·Kafka·Grafana 등 연동 대상 플랫폼의 테스트용 Helm values 파일 동봉

**사용 기술:** Fluentd, Helm, Kubernetes, K3s, Kafka, Loki, Grafana, Redis, Filebeat, fluent-plugin-kafka, fluent-plugin-redis, fluent-plugin-beats, rdkafka, librdkafka, Prometheus, Docker

**구현 특이점:**
- 오프라인 플러그인 설치 패턴을 initContainer + hostPath 볼륨 + emptyDir 공유 볼륨의 3단계로 구체적으로 구현하여, 인터넷이 차단된 환경에서도 gem 설치가 가능하도록 설계했습니다.
- rawstring 무파싱 전달을 위해 input 측 parser @type none과 output 측 formatter @type single_value를 조합하는 방식을 여러 시나리오(http2kafka, beats2kafka)에 걸쳐 일관되게 적용했습니다.
- beats2kafka_keyfilter_multipods.yaml에서 record_modifier 필터로 tag 기반 topickey 필드를 생성하고, buffer chunk key를 topickey로 지정하여 멀티토픽 전송과 버퍼 청크 분리를 동시에 처리하는 구성을 구현했습니다.
- plugin_rdkafka/README.md에서 kafka/rdkafka 계열 플러그인 타입별 차이(ruby 기반 vs C 라이브러리, consumer-group 지원 여부, 버전 호환성)를 직접 정리하여 플러그인 선택 기준을 문서화했습니다.

### [forwarders](https://github.com/YunanJeong/forwarders)
_Shell_
> fluentbit, filbeat 등등 테스트 및 배포용 레포지토리.  그 때 그 때 설정하다보니까 기억이 잘 안남. 템플릿도 잡아놓고 특히 쿠버네티스용 차트 설정으로도 좀 만들어 놔야지

**목적:** Fluent Bit와 Filebeat를 다양한 환경(Linux, Windows, Kubernetes)에 배포하고 운영하기 위한 설정 템플릿 및 운영 참고 레포지토리입니다. 각 포워더의 설치 스크립트, Helm values, Kafka 출력 설정 등을 관리합니다.

**주요 기능:**
- Filebeat를 Ubuntu에 설치하고 systemd 서비스로 등록하는 셸 스크립트 제공
- Filebeat → Kafka 출력 설정 파일 작성 (gzip 압축, ACK 정책, 메시지 크기 제한, 불필요 메타데이터 필드 제거 포함)
- Fluent Bit Bitnami Helm Chart의 values.yaml 커스터마이징 (DaemonSet/Deployment 전환, 보안 컨텍스트, PDB, 프로브 등)
- Fluent Bit의 메모리 버퍼·파일 버퍼 동작 원리 및 [SERVICE]/[INPUT]/[OUTPUT] 섹션별 설정 방법 문서화
- 파일 고유성 식별 방식(inode+DeviceId vs. fingerprint)과 파일 로테이션 패턴별 로그 중복·누락 시나리오 정리
- Fluent Bit과 Filebeat의 멀티 아웃풋, Fluentd 연동, Windows 환경 호환성 등 운영 관점 비교 정리

**사용 기술:** Fluent Bit, Filebeat, Kafka, Helm, Kubernetes, Shell, YAML

**구현 특이점:**
- fluent-bit 버퍼 문서에서 메모리버퍼와 파일버퍼가 각각 [INPUT]/[OUTPUT] 섹션에 분산 설정되는 이유를 파이프라인 아키텍처 관점에서 설명하고, storage.max_chunks_up과 Mem_Buf_Limit의 상호 배타적 동작까지 구체적으로 기술함
- beat2kafka.yml에서 fingerprint 길이를 기본값(1024)에서 256으로 줄이면서 그 트레이드오프(파일 고유성 vs. 소형 파일 누락 가능성)를 주석으로 명시하는 등 실운영 경험이 반영된 설정값 선택
- Filebeat의 Elastic 버전 정책(Minor 버전이 사실상 Patch 레벨)을 정리하여 버전 선택 시 주의점을 실무 관점에서 기술함
- values.yaml에서 containerSecurityContext에 readOnlyRootFilesystem, capabilities drop ALL, seccompProfile RuntimeDefault 등 프로덕션 수준의 보안 설정을 명시적으로 구성함

### [ftp-to-s3](https://github.com/YunanJeong/ftp-to-s3)
_Python_

**목적:** FTP 서버에서 전일자 파일을 자동으로 수집해 AWS S3에 업로드하는 데이터 파이프라인입니다. 순수 Python 스크립트 버전과 Snakemake 기반 DAG 버전 두 가지 구현을 함께 제공합니다.

**주요 기능:**
- FTP 서버 접속 후 전일자 날짜 경로의 파일 목록을 자동으로 조회
- 서브디렉토리를 포함한 FTP 경로를 재귀적으로 탐색하여 전체 파일 경로 수집
- ncftpget을 활용한 FTP 파일 다운로드 및 AWS CLI를 활용한 S3 업로드
- 업로드 성공 후 로컬 임시 파일 자동 정리
- YAML 설정 파일로 FTP 접속 정보·로컬 경로·S3 경로를 외부에서 주입
- crontab을 이용한 매일 새벽 정기 실행 스케줄링

**사용 기술:** Python, Snakemake, ftplib, ncftp, AWS CLI, YAML, crontab

**구현 특이점:**
- ftplib의 cwd 시도·실패 방식으로 디렉토리 여부를 판별하는 is_directory 함수를 구현해 별도 속성 조회 없이 재귀 탐색을 가능하게 함
- FTP 550 에러(경로 없음)는 조용히 넘기고 그 외 에러는 그대로 전파하는 세분화된 예외 처리를 get_ftp_directory_items에 적용
- boto3 대신 AWS CLI, ftplib 대신 ncftpget을 의도적으로 선택한 이유를 문서에 명시(성능·재귀 다운로드 편의성)
- 순수 Python 버전에서 Snakemake DAG 버전으로의 발전 과정을 legacy 디렉토리에 보존하여 설계 진화 흐름을 추적 가능하게 유지

### [ghub-mouse-doubleclick-reducer](https://github.com/YunanJeong/ghub-mouse-doubleclick-reducer)
_Lua_

**목적:** Logitech G Hub 환경에서 마우스 사이드 버튼의 의도치 않은 이중 클릭(더블클릭)을 무시하는 스크립트입니다. 설정한 시간 간격 이내에 반복 입력이 감지되면 해당 이벤트를 무시하여 오작동을 방지합니다.

**주요 기능:**
- 지정 버튼의 연속 입력 간격을 측정하여 설정값(기본 300ms) 이내 중복 클릭 무시
- 정상 클릭 시 Alt+Left 키 조합으로 브라우저/탐색기 뒤로가기 동작 실행
- 이벤트 처리 결과를 JSON 형식의 로그 메시지로 출력하여 인터벌 튜닝 지원
- 대상 버튼 번호와 무시 인터벌을 상단 상수로 분리하여 간편하게 조정 가능

**사용 기술:** Lua, Logitech G Hub

**구현 특이점:**
- 이벤트 로그를 JSON 구조체 형식으로 포맷하여 타임스탬프·인터벌·케이스를 함께 기록함으로써 인터벌 값 튜닝 시 로그 분석이 용이하도록 설계
- IGNORE_INTERVAL_MS 한 줄만 수정하면 필터링 민감도를 즉시 조정할 수 있도록 설정값을 코드 최상단에 명시적으로 분리
- testPress 함수를 별도로 유지해 goBack 동작을 실제 키 입력 없이 테스트할 수 있는 전환 구조를 마련

### [gitlab-ce-install](https://github.com/YunanJeong/gitlab-ce-install)

**목적:** GitLab CE(Community Edition)를 Ubuntu 환경에 설치하고 버전 업그레이드하는 과정을 정리한 운영 참고 문서입니다.

**주요 기능:**
- apt 패키지 관리자를 이용한 GitLab CE 설치 절차 안내
- 업그레이드 경로(Upgrade Path) 및 required upgrade stop 개념 설명
- 서드파티 패키지 저장소 등록 명령어 제공
- GPG 키 처리 오류 등 업그레이드 시 흔한 문제 상황 대응법 정리

**사용 기술:** GitLab CE, Ubuntu, apt, Bash

**구현 특이점:**
- GitLab 공식 문서가 gitlab-ee 기준으로 작성되어 있음을 인지하고 gitlab-ce로 치환해 적용하는 실용적 주의사항을 명시함
- required upgrade stop 개념을 소개하고 공식 업그레이드 경로 확인 도구 링크를 함께 제공해 버전 마이그레이션 리스크를 낮추는 방향으로 구성함

### [kafka-connect-s3-secnumbertimebasedpartitioner](https://github.com/YunanJeong/kafka-connect-s3-secnumbertimebasedpartitioner)
_Java_
> SecTimeBasedPartitioner: Custom Partitioner for S3 Sink Connector. 

**목적:** Kafka S3 Sink Connector에서 Unix 타임스탬프(초 단위)를 그대로 사용하여 S3 파티셔닝 경로를 생성하는 커스텀 파티셔너입니다. 기존 TimeBasedPartitioner가 초 단위 숫자 타임스탬프를 밀리초로 잘못 해석하는 문제를 해결합니다.

**주요 기능:**
- 초 단위 Unix 타임스탬프(Number 타입)를 밀리초로 변환하여 올바른 S3 파티션 경로 생성
- Confluent TimeBasedPartitioner를 상속하여 기존 설정과의 호환성 유지
- RecordFieldSecNumber라는 신규 TimestampExtractor를 등록하여 설정만으로 교체 가능
- Struct 및 Map 두 가지 레코드 값 타입 모두 지원
- 중첩 필드 접근을 위해 DataUtils.getNestedFieldValue 활용
- 기존 Wallclock·Record·RecordField extractor는 원본 구현체로 위임

**사용 기술:** Java, Apache Kafka Connect, Confluent kafka-connect-storage-partitioner, Maven

**구현 특이점:**
- newTimestampExtractor를 오버라이드하여 기존 extractor 이름(Wallclock, Record, RecordField)은 원본 클래스로 위임하고, 신규 RecordFieldSecNumber만 커스텀 클래스로 라우팅하는 스위치 구조로 하위 호환성을 유지
- INT32/INT64 필드와 Map 내 Number 타입 모두에서 longValue() * 1000 변환을 적용해 타입별 분기를 일관되게 처리
- 숫자처럼 생긴 문자열 타임스탬프를 정규식(NUMERIC_TIMESTAMP_PATTERN)으로 먼저 판별하고, 실패 시 ISO 날짜 파서로 fallback하는 extractTimestampFromString 구현
- S3 Sink Connector jar에 이미 포함된 의존성과 중복을 피하기 위해 partitioner 클래스만 독립 jar로 빌드하도록 pom.xml과 빌드 가이드를 구성

### [kafka-jdbc-connector-control](https://github.com/YunanJeong/kafka-jdbc-connector-control)
_Smarty_
> db구조는 제각각. 백의DB,천의Table에서 데이터를 편하게 긁어오자.

**목적:** 수백 개의 DB와 수천 개의 테이블에서 Kafka JDBC Source Connector를 자동으로 대량 등록·관리하기 위한 도구입니다. 테이블당 커넥터를 하나씩 운용하는 구조에서 발생하는 반복 작업을 자동화합니다.

**주요 기능:**
- 환경변수로 DB 목록과 테이블 목록을 받아 모든 조합에 대해 커넥터를 자동 등록
- Python string.Template을 활용해 커넥터 설정 JSON을 동적으로 생성
- Kafka Connect REST API(PUT /connectors/{name}/config)를 통해 커넥터를 등록 또는 갱신
- Helm Chart의 Kubernetes Job으로 커넥터 등록 작업을 배포 환경에서 실행
- values.yaml의 env 블록으로 환경변수를 일원화하여 DB 접속 정보 및 커넥터 설정을 관리

**사용 기술:** Python, Kafka Connect, JDBC Source Connector, Helm, Kubernetes, Docker

**구현 특이점:**
- DB 목록과 테이블 목록의 조합을 이중 루프로 순회하며 커넥터 이름을 `{db_host}_{table}` 형식으로 자동 생성함으로써, 수천 개 커넥터 등록을 선언적 설정 한 벌로 처리할 수 있는 구조를 설계했다
- values.yaml의 connect.template 필드에 커넥터 설정 JSON 템플릿을 통째로 주입하고, Python의 string.Template으로 치환하는 방식을 택해 커넥터 설정 포맷 변경에 유연하게 대응할 수 있다
- Helm Job 템플릿에서 values.env를 range로 순회해 임의 환경변수를 자유롭게 추가할 수 있도록 설계하여, 새로운 커넥터 파라미터 추가 시 템플릿 수정 없이 values.yaml만 변경하면 된다
- 1테이블-1커넥터 구조의 트레이드오프(whitelist/blacklist 대비 query 모드 자유도, 개별 Producer 대비 운영 난이도)를 README에 명시적으로 설명하여 설계 의도를 문서화했다

### [lora-sd](https://github.com/YunanJeong/lora-sd)
_HCL_
> LoRA(Low Rank Adaptation), Stable-Diffusion(Model), Packer

**목적:** LoRA 파인튜닝과 Stable Diffusion WebUI를 온디맨드로 실행할 수 있는 AWS AMI를 Packer로 자동 빌드하는 프로젝트입니다. NVIDIA GPU 환경 세팅부터 kohya_ss, AUTOMATIC1111 WebUI 설치까지 이미지 생성 과정을 자동화합니다.

**주요 기능:**
- Packer를 이용해 Ubuntu 기반 GPU AMI를 자동 빌드
- NVIDIA Driver 및 CUDA 12.5 설치 스크립트를 단계별로 분리하여 관리
- AUTOMATIC1111 Stable Diffusion WebUI를 AMI에 사전 설치 및 초기 구동까지 완료
- kohya_ss LoRA 학습 환경을 AMI 빌드 시점에 포함
- WebUI 설치 완료 감지 후 프로세스를 자동 종료하는 대기 스크립트로 Packer 빌드 흐름 제어
- Ubuntu 22 GPU 전용 이미지와 Ubuntu 24 LTS 이미지 두 가지 소스 AMI 전략 지원

**사용 기술:** HCL, Packer, Bash, NVIDIA CUDA, Python, Stable Diffusion WebUI, kohya_ss, filebrowser, AWS EC2

**구현 특이점:**
- webui.sh가 설치와 실행을 동시에 수행하는 특성상 Packer 빌드가 세션에 블로킹되는 문제를 nohup 백그라운드 감시 스크립트(wait_webui_install.sh)로 해결 — 단순 sleep 대신 HTTP 200 응답 폴링 방식으로 설치 완료 시점을 감지
- 설치 소요 시간이 가변적인 WebUI 초기 구동을 curl 폴링(최대 120회, 10초 간격)으로 처리하여 타이밍 의존성을 제거
- GPU AMI 소스를 두 가지로 분리해 사전 설치 항목에 따라 setup 명령을 다르게 구성, 동일 코드베이스에서 유연한 빌드 경로 제공
- Python 3.10 가상환경을 webui.sh 실행 전에 직접 생성하는 우회 처리로 알려진 버그를 명시적으로 해결

### [metric-llm-reporter](https://github.com/YunanJeong/metric-llm-reporter)
_Shell_
> 목적: 내 서버들 너가 모니터링 해줘!@ 

**목적:** 여러 대의 Prometheus 서버에서 서버 메트릭을 수집하고, LLM을 통해 SRE 관점의 이상 분석을 수행한 뒤 결과를 이메일로 발송하는 자동화 리포팅 도구입니다.

**주요 기능:**
- 복수의 Prometheus 서버를 LABEL|URL 형식으로 정의하고 한 번에 메트릭 수집
- CPU, 메모리, 디스크, 네트워크 수신/송신 지표를 현재값과 24시간 전 값의 증감폭과 함께 계산
- 80%(!), 90%(!!) 임계값 기호를 포함한 1노드 1줄 압축 포맷으로 LLM 입력 토큰 최소화
- Ollama(로컬 LLM), OpenAI 호환 API, AWS Bedrock 세 가지 AI 엔진을 환경변수 하나로 전환 지원
- Source/Job/Instance 통합 식별자와 N:1 단축 ID 매핑 테이블로 AI 분석 시 데이터 혼선 방지
- fetch, brain, mail 세 모듈을 독립 실행 가능하도록 설계하여 파이프라인 조합 및 단독 테스트 지원

**사용 기술:** Shell, Prometheus, Ollama, OpenAI API, AWS Bedrock, AWS CLI, curl, jq, mailutils

**구현 특이점:**
- jq 내부에서 helper 함수(get_val, fmt_diff)를 정의하고 오늘/어제 JSON을 단일 스트림으로 처리하여 외부 반복 없이 증감폭과 임계값 기호를 한 번에 산출하는 format_compact 구현
- AI_TYPE 환경변수 하나로 Ollama, OpenAI 호환 REST API, AWS Bedrock CLI 경로를 분기하면서 각 엔진의 응답 파싱 포맷 차이를 모듈 내부에서 흡수하는 구조
- 환경변수 직접 주입 → 파라미터 지정 파일 → 기본 0.env 순의 3단계 우선순위를 각 모듈이 동일하게 준수하여 prod/dev/staging 환경을 파일 교체만으로 전환 가능
- AWS Bedrock 호출 실패 시 에러 메시지, 모델 ID, 리전, CLI 버전, 권한 확인 명령어를 stderr에 구조적으로 출력하는 디버깅 안내 구현

### [my-helm-charts](https://github.com/YunanJeong/my-helm-charts)
_Java_

**목적:** Kubernetes 환경에서 Kafka 및 Kafka Streams 애플리케이션을 헬름 차트로 배포·관리하기 위한 커스텀 차트 저장소입니다. 경량 Kafka 스택 배포용 차트(skafka)와 Kafka Streams 앱 배포용 차트(kstreams)를 함께 제공합니다.

**주요 기능:**
- bitnami/kafka, kafka-ui, kubernetes-dashboard를 단일 릴리즈로 묶어 Kubernetes에 배포하는 skafka 차트 제공
- Kafka Streams 앱 이미지를 헬름 values로 교체할 수 있도록 설계된 범용 kstreams 차트 제공
- kafkaClientOverrides 값을 STREAMS_* 환경변수 형식으로 자동 변환하여 Streams 앱에 주입
- Kafka 브로커 준비 여부를 확인하는 initContainer(readinessCheck) 옵션을 차트 내 구현
- Skaffold 프로파일을 활용해 이미지 빌드·헬름 배포를 통합한 로컬 개발 워크플로우 구성
- Jackson JsonNode를 Kafka Streams Serde로 사용할 수 있는 JsonNodeSerde 직접 구현 및 샘플 토폴로지 제공

**사용 기술:** Helm, Kubernetes, Kafka Streams, Apache Kafka, Skaffold, Docker, Java, Maven, bitnami/kafka, kafka-ui, kubernetes-dashboard, SLF4J, Logback, JUnit Jupiter

**구현 특이점:**
- kstreams 차트의 Deployment 템플릿에서 kafkaClientOverrides 맵의 키를 upper+replace 변환하여 STREAMS_* 환경변수로 매핑하며, application.id·bootstrap.servers 예약 키 충돌 시 fail로 즉시 에러를 발생시키는 가드 로직을 구현
- 사용자 env에서 STREAMS_ 접두어 사용 시 명시적 오류 메시지로 차단하여 환경변수 네임스페이스 충돌을 차트 레벨에서 방지
- Kafka Streams 앱 이미지(repository)가 유스케이스마다 달라지는 특성을 반영해 이미지 자체를 헬름 커스텀 value로 취급하는 설계 방침을 차트 구조에 명시적으로 반영
- Skaffold 프로파일을 통해 이미지 빌드 결과의 레지스트리·태그 정보를 setValueTemplates로 헬름에 자동 전달하는 빌드-배포 파이프라인 구성

### [packer](https://github.com/YunanJeong/packer)
_HCL_

**목적:** HashiCorp Packer를 사용해 AWS AMI 등 여러 플랫폼의 머신 이미지를 IaC 방식으로 빌드·관리하기 위한 템플릿 및 워크플로우 레포지토리입니다.

**주요 기능:**
- HCL 포맷(.pkr.hcl)으로 Packer 템플릿 작성
- AWS AMI 대상 이미지 빌드 파이프라인 구성
- packer init / fmt / validate / inspect / build 커맨드 기반 워크플로우 정리
- 멀티 플랫폼(AWS, Docker, VMware, GCP, Azure) 지원 범위 문서화
- 템플릿 병렬 실행을 활용한 테스트 전략 기술

**사용 기술:** Packer, HCL, AWS AMI, AWS CLI

**구현 특이점:**
- JSON 대신 HCL을 선택한 이유(최신 사양, 가독성, 유지보수성)를 명확히 기술하고 .pkr.hcl 전용 확장자 사용
- IaC와 LLM 시너지에 대한 실무적 관점을 README에 포함해 단순 튜토리얼을 넘는 운용 맥락 제공
- 여러 템플릿을 병렬로 띄워 테스트하는 실전 요령을 정리한 점

### [PChachu](https://github.com/YunanJeong/PChachu)
_Java_
> DB 과제 안드로이드

**목적:** PC방(PCcafe) 정보를 위치 기반으로 검색하고 상세 정보를 확인할 수 있는 Android 앱입니다. Google Places 자동완성으로 장소를 선택하면 해당 지역의 PC방 목록과 메뉴·이벤트 정보를 백엔드 API에서 받아 보여줍니다.

**주요 기능:**
- Google Places Autocomplete로 장소 선택 후 광역시도·시군구·읍면동 단위 PC방 검색
- 검색 결과를 RecyclerView CardView 리스트로 표시하고 항목 클릭 시 상세 화면으로 이동
- 상세 화면에서 좌석 수·사양 정보, 메뉴 목록, 이벤트 목록을 별도 RecyclerView로 렌더링
- GET/POST/PUT/DELETE 메서드를 포괄하는 HTTP 통신 유틸리티 클래스(ModelCommunication) 구현
- Jackson ObjectMapper로 서버 JSON 응답을 List<Map> 구조로 파싱
- 한국 주소 문자열을 국가·광역시도·시군구·읍면동으로 분리하는 ModelAddressParser 및 단위 테스트 작성

**사용 기술:** Java, Android SDK, RecyclerView, CardView, Google Places API, Jackson, AsyncTask, JUnit

**구현 특이점:**
- ModelCommunication 클래스가 GET·POST·PUT·DELETE를 각각 독립 메서드로 구현하고 InputStream/ErrorStream 분기 및 연결 해제를 finally 블록에서 처리해 네트워크 레이어를 일관되게 캡슐화했습니다.
- ModelAddressParser의 '구' 포함 여부를 기준으로 읍면동 토큰을 건너뛰는 로직을 JUnit 테스트 4개로 경계 케이스까지 검증했습니다.
- ActivitySearch·ActivityCafeDetail 모두 AsyncTask로 네트워크 요청을 백그라운드에 위임하고 onPostExecute에서만 UI를 갱신하는 구조를 유지했습니다.
- RecyclerView 어댑터를 검색 결과·메뉴·이벤트 세 가지로 분리해 각 데이터 타입에 맞는 카드 레이아웃을 독립적으로 구성했습니다.

### [PChachu_server](https://github.com/YunanJeong/PChachu_server)
_JavaScript_
> DB Final Project_Server Side

**목적:** PC방 정보 조회 서비스의 백엔드 서버로, 주소 조건에 따른 PC방 목록 및 상세 정보(사양, 좌석, 요금, 이벤트, 음식 메뉴)를 REST API로 제공합니다.

**주요 기능:**
- 주소 파라미터(1~3단계) 조합에 따라 PC방 목록을 동적으로 조회하는 엔드포인트 구현
- PC방 ID 기반으로 상세 정보(사양, 좌석 수, 요금, 주소) 조회
- PC방 별 진행 중인 이벤트 및 경품 정보 조회
- PC방 별 음식 메뉴와 가격 정보 조회
- MySQL 커넥션 풀을 모듈로 분리하여 DB 연결 관리

**사용 기술:** Node.js, Express, MySQL, body-parser, formidable, Jade, morgan

**구현 특이점:**
- 주소 입력이 1단계만 있는 경우, 1~2단계, 1~3단계 모두 있는 경우를 null 체크로 분기하여 하나의 엔드포인트(/get1)에서 다단계 주소 필터링을 처리한 점
- db.js에서 mysql.createPool을 connect/get으로 분리해 앱 초기화 시점에 풀을 생성하고 라우터에서 get()으로 재사용하는 구조로 모듈화
- PC방의 기본 정보, 이벤트, 음식 메뉴를 각각 별도 엔드포인트(get2~get4)로 분리해 클라이언트 측 선택적 조회가 가능하도록 설계

### [prom-proxy-test](https://github.com/YunanJeong/prom-proxy-test)
> Prometheus Proxy beyond firewall

**목적:** 방화벽 등 사설망 환경에서 Prometheus가 직접 접근할 수 없는 exporter를 prometheus-proxy/agent를 통해 우회 수집할 수 있도록 구성하는 레퍼런스 셋업이다. Pull 방식의 통신 방향을 역전시켜 보안 제약 환경에서도 메트릭 수집이 가능하게 한다.

**주요 기능:**
- prometheus-proxy와 prometheus-agent를 Docker Compose로 분리 배포하여 방화벽 경계를 gRPC(50051)로 연결
- Agent를 host 네트워크 모드로 실행해 사설망 내 exporter에 직접 접근 가능하도록 구성
- metrics_path 기반 job 분리로 단일 Proxy 인스턴스에서 다수의 exporter를 구분 수집
- Proxy 포트 다중 매핑(-p 9101:8080 등)을 통해 Grafana 대시보드 호환성을 높이는 포트 전략 정리
- kube-prometheus-stack Helm 차트를 Prometheus 전용(only_prom.yaml)과 node-exporter 전용(only_exporter.yaml)으로 분리 설치할 수 있도록 values 파일 구성
- quay.io 이미지 접근 불가 환경을 고려한 사설 저장소 수동 업로드 절차 안내 포함

**사용 기술:** Prometheus, prometheus-proxy, prometheus-agent, node-exporter, Docker, Docker Compose, Helm, kube-prometheus-stack, Kubernetes, gRPC

**구현 특이점:**
- Proxy 포트를 exporter 수만큼 8080으로 포워딩하는 방식을 명시적으로 정의하여, 포트 번호 기반 instance 구분이 가능하도록 설계 의도를 주석으로 문서화했다
- only_prom.yaml과 only_exporter.yaml을 완전히 분리하여 클러스터가 물리적으로 나뉜 환경에서 각각 독립 배포할 수 있는 구조로 설계했다
- only_exporter.yaml에서 kubernetesServiceMonitors를 false로 두면서도 개별 컴포넌트 항목을 true로 남겨 선택적 활성화 경로를 열어두었고, recording rule과의 불일치로 인한 부하 발생 가능성을 주석으로 명시했다
- Agent 컨테이너에 host 네트워크 모드를 적용한 이유(외부 Request 시 네트워크 범위 혼동 방지)를 설정 파일 내에 명확히 기술했다

### [python-tips](https://github.com/YunanJeong/python-tips)
_Python_
> python example, skill, and practice

**목적:** Python 개발 시 자주 마주치는 주제들(로깅, 메일 전송, 테스트, 패키지 관리 등)에 대한 실용적인 예제와 사용 패턴을 정리한 레퍼런스 모음 레포지토리입니다.

**주요 기능:**
- pytest와 unittest의 fixture/setUp 패턴을 동일 대상 함수에 대해 나란히 구현하여 두 프레임워크를 비교 가능하게 구성
- 커스텀 logging.StreamHandler를 상속한 AlertHandler를 작성해 WARNING 이상 로그 발생 시 MS Teams Webhook으로 자동 알림 전송
- SMTP 메일 전송 로직을 SmtpMailer 클래스로 추상화하고 환경변수로 자격증명을 분리하여 cron 스케줄 실행에 연동
- PEP 723 인라인 스크립트 의존성 선언 방식을 활용해 pyproject.toml 없이 단일 파일에서 외부 패키지를 격리 실행하는 예제 구현
- uv의 핵심 워크플로(프로젝트 생성, 버전 관리, 전역 툴, 기존 프로젝트 마이그레이션)를 단계별로 정리한 실용 가이드 작성
- pyodbc와 pymssql의 SQL Server 연결 방식 차이 및 자동화 적합성을 실무 관점에서 비교 정리

**사용 기술:** Python, pytest, unittest, smtplib, logging, pymsteams, httpx, rich, uv

**구현 특이점:**
- logging 핸들러를 StreamHandler 서브클래싱으로 확장해 Teams Webhook 알림을 로그 레벨 기반으로 트리거하는 구조를 직접 구현했으며, logger 레벨과 handler 레벨의 우선순위 관계를 코드 주석으로 명확히 기술
- SmtpMailer 클래스에서 To 헤더 표시용 문자열과 실제 sendmail 수신자 리스트를 분리하고, CC 포함 시 중복 주소를 set으로 제거하는 처리를 포함
- cron 환경에서 source 대신 POSIX 표준 dot(.)을 사용해 환경변수를 로드하고 로그 파일명에 연월을 동적으로 삽입하는 쉘 스크립트 구성
- pytest fixture의 scope 옵션(function/module/session)과 yield 기반 전후처리를 코드와 docstring으로 함께 설명하여 학습 참조용으로 활용하기 좋은 구성

### [redis-test](https://github.com/YunanJeong/redis-test)
> redis-test

**목적:** K3s 환경에서 Bitnami Helm 차트를 이용해 Redis를 배포하고, pub/sub 통신 방식 및 데이터 타입별 활용 패턴을 정리한 레퍼런스 레포지토리입니다.

**주요 기능:**
- Helm 커스텀 values 파일(custom.yaml)로 Redis 단독 마스터 구성 배포
- 마스터 서비스를 LoadBalancer 타입으로 외부 노출
- 레플리카 수를 0으로 설정해 standalone 모드로 운영
- Prometheus 메트릭 익스포터 활성화(포트 9121)
- 인증 비활성화 및 퍼시스턴스 비활성화로 테스트 환경 최적화
- redis-cli를 활용한 Key-Value, Hash, Pub/Sub 동작 검증 방법 문서화

**사용 기술:** Redis, Helm, K3s, Kubernetes, Bitnami Redis Chart, Prometheus

**구현 특이점:**
- custom.yaml에서 replica.replicaCount: 0과 master.service.type: LoadBalancer를 조합해 테스트 목적에 맞는 최소 구성을 명시적으로 선택한 점
- README에서 Redis pub/sub의 양방향 네트워크 인가 필요성과 구독자 재등록 시나리오를 실운영 관점에서 구체적으로 분석한 점
- Redis, Kafka, RabbitMQ의 설계 철학 차이(인메모리 vs 디스크 기반)를 근거로 도구 선택 기준을 서술한 점
- default.yaml 전체를 함께 관리해 차트 기본값과 커스텀 오버라이드 간 차이를 명확히 추적할 수 있도록 구성한 점

### [s3-athena-lambda-partitioner](https://github.com/YunanJeong/s3-athena-lambda-partitioner)
_Python_

**목적:** S3에 신규 객체가 적재될 때 Lambda를 트리거로 삼아 Athena 테이블에 날짜 기반 파티션을 자동 등록하는 서버리스 유틸리티입니다. 이를 통해 Data Lake의 쿼리 스캔 범위를 줄이고 비용 증가를 억제합니다.

**주요 기능:**
- S3 이벤트 레코드에서 버킷명과 객체 키를 파싱하여 연/월/일 파티션 값을 추출
- Athena ALTER TABLE ADD PARTITION 쿼리를 동적으로 생성하여 실행
- 환경 변수(ATHENA_DATABASE, ATHENA_TABLE, ATHENA_OUTPUT)로 대상 테이블과 출력 경로를 외부 설정화
- 복수 S3 레코드를 루프로 처리하여 배치 이벤트에도 대응

**사용 기술:** Python, AWS Lambda, Amazon S3, Amazon Athena, boto3

**구현 특이점:**
- ETL 수준의 데이터 변환 없이 파티션 메타데이터 등록만 수행하도록 책임을 명확히 한정하여, EL 단계와 Transform 단계의 관심사를 분리
- Lambda 환경 변수로 데이터베이스·테이블·결과 경로를 분리해 코드 변경 없이 다른 테이블에 재사용 가능한 구조
- S3 트리거 기반 이벤트 루프로 단일 Lambda 함수가 다수의 객체 생성 이벤트를 한 번에 처리

### [simple-kafka-deploy](https://github.com/YunanJeong/simple-kafka-deploy)
_Dockerfile_
> K8s-based Kafka with UI by Helm Chart

**목적:** Kubernetes 환경에서 Kafka 클러스터를 Helm Chart 한 줄 명령으로 배포할 수 있도록 구성한 도구입니다. Kafka 브로커, Kafka Connect, Kafka UI, Kubernetes 대시보드를 단일 릴리즈로 묶어 제공합니다.

**주요 기능:**
- 1노드 및 3노드 HA 구성을 위한 사전 정의된 values 파일 제공 (1node, 3node_HA, AD 변형 포함)
- KRaft 모드 기반 Kafka 클러스터 배포 (Zookeeper 미사용)
- auto discovery를 활용한 advertised.listeners 자동 구성 및 NodePort/LoadBalancer 외부 접근 설정
- Kafka Connect 플러그인을 initContainer와 emptyDir 볼륨으로 런타임 설치하는 패턴 구현
- JDK 버전 교체가 필요한 경우를 위한 멀티스테이지 Dockerfile 제공 (JDK 17 → JDK 11 교체)
- JMX Exporter 및 Prometheus ServiceMonitor 연동을 위한 values 파일 별도 제공

**사용 기술:** Helm, Kubernetes, Apache Kafka, Kafka Connect, bitnami/kafka, kafka-ui (kafbat), kubernetes-dashboard, Confluent Platform, Docker, Prometheus, JMX Exporter, K3s, Traefik

**구현 특이점:**
- auto discovery 활성화 여부에 따라 RBAC 및 ServiceAccount 설정이 달라지는 구조를 values 파일마다 명시적으로 분리하여 관리하고, 외부 클라이언트와 브로커 간 2단계 통신 흐름(LoadBalancer → advertised.listener)을 values 주석으로 상세히 문서화했습니다.
- connect-image-jdk11-kfk3/Dockerfile에서 Alpine 기반 fetch 스테이지로 JDK 11 바이너리를 가져온 뒤 bitnami Kafka 이미지의 /opt/bitnami/java 심볼릭 링크를 교체하는 방식으로 오프라인 환경에서도 JDK 버전을 제어합니다.
- 멀티노드 환경에서 StatefulSet PVC 이름 규칙(data-{ReleaseName}-kafka-controller-N)을 파악하여 사전 생성 PV/PVC와 동적 프로비저닝을 전환하는 방법을 kafka-multi-pvc.yaml에 구체적인 예시와 함께 제공합니다.
- skafka/values.yaml의 ui4kafka 섹션에서 yamlApplicationConfig를 false로 설정하고 myYamlApplicationConfig를 별도 키로 분리함으로써 Helm 내장 객체({{ .Release.Name }})를 kafka-ui 설정값 안에서 사용할 수 있도록 처리했습니다.

### [simple-parquet-reader](https://github.com/YunanJeong/simple-parquet-reader)
_Python_

**목적:** AWS S3 또는 로컬에 저장된 Parquet 파일을 빠르게 불러와 pandas DataFrame으로 조회할 수 있는 CLI 기반 뷰어 도구입니다. Jupyter 없이 터미널에서 바로 DataFrame을 탐색하고 간단한 Python 표현식을 실행할 수 있습니다.

**주요 기능:**
- S3 URI를 입력받아 awswrangler로 Parquet 파일을 DataFrame으로 로드
- 로컬 Parquet 파일 읽기 지원 구조 포함
- 인터랙티브 Python CLI 루프에서 DataFrame 표현식을 직접 실행
- 단축 커맨드(1~4)로 pandas display 옵션을 즉시 전환
- argparse로 필수·선택 인자(날짜 범위 등)를 받는 CLI 진입점 구성
- setuptools 기반 패키지 구조로 pip 설치 가능하도록 패키징

**사용 기술:** Python, pandas, awswrangler, setuptools, argparse, readline

**구현 특이점:**
- __main__.py를 통해 python -m 방식의 직접 실행을 지원하는 패키지 구조를 채택하여, 라이브러리 겸 실행 도구로 동작하도록 설계
- readline을 조건부로 import함으로써 Ubuntu/Windows 간 input() 동작 차이(방향키 히스토리)를 인식하고 플랫폼 호환성을 코드 주석 수준에서 명시
- parse_cmd에서 단축키를 pandas display 옵션 문자열로 매핑하는 방식으로, CLI 탐색 흐름에서 자주 쓰는 설정 변경을 단일 키 입력으로 처리
- version.py를 별도 파일로 분리하고 setup.py에서 파일 파싱으로 버전을 읽어 단일 소스 버전 관리 패턴을 적용

### [snakemake-template](https://github.com/YunanJeong/snakemake-template)
_Python_
> snakemake template, examples, test

**목적:** Snakemake 워크플로우를 빠르게 시작할 수 있도록 실행 커맨드, 로깅 전략, 설정 파일 구조를 정리한 템플릿 및 참고 예제 모음입니다.

**주요 기능:**
- 멀티코어 병렬 실행 및 재실행 시나리오별 커맨드 정리
- --rerun-triggers 옵션을 활용한 중간 지점 재처리 방법 제시
- snakemake 자동 로그(.snakemake/log/) 활용 가이드 작성
- log directive를 통한 job 단위 로그 파일 관리 방법 설명
- configfile을 통한 설정 오버라이딩 구조 예시 제공

**사용 기술:** Snakemake, Python, YAML

**구현 특이점:**
- --rerun-triggers mtime 활용 등 Snakemake 버전별 재실행 트리거 동작 차이를 파악하고 실무 대응 방법을 구체적으로 문서화한 점
- 멀티프로세싱 환경에서 exec 기반 로깅의 Read/Write 충돌 가능성을 인지하고 권장/비권장 방식을 명시적으로 구분한 점
- wildcard를 포함하는 rule에서 log directive 사용 시 발생하는 Syntax Error 조건을 구체적으로 기술한 점

### [strimzi-kafka](https://github.com/YunanJeong/strimzi-kafka)

**목적:** Strimzi 기반 Kubernetes 환경에서 Kafka를 운영하기 위한 설정 및 구성 자료를 정리한 레포지토리입니다.

**주요 기능:**
- Strimzi Operator를 활용한 Kafka 클러스터 구성 관리

**사용 기술:** Strimzi, Kafka, Kubernetes

**구현 특이점:**
- README 외 실질적인 파일 내용이 확인되지 않아 구체적인 구현 특징을 파악하기 어렵습니다

### [TripScanner-android](https://github.com/YunanJeong/TripScanner-android)
_Java_

**목적:** 여행 동행을 찾고 함께할 사람들을 연결해주는 Android 앱입니다. 사용자는 동행을 검색하고 참여하거나 직접 생성할 수 있으며, 동행 후 상대방에 대한 리뷰를 작성하고 조회할 수 있습니다.

**주요 기능:**
- Google Places Autocomplete와 날짜 범위 선택기를 조합하여 목적지·체크인·체크아웃 조건으로 동행 검색
- 동행 상세 화면에서 호스트 프로필 확인 및 참여 신청(JOIN) 처리
- 내가 생성한 동행, 참여한 동행 목록을 각각 별도 화면에서 조회
- 리뷰 작성 대기(Pending), 내가 쓴 리뷰, 특정 사용자가 받은 리뷰를 구분하여 열람
- 이메일·비밀번호 기반 회원가입 및 로그인, 인증 토큰을 SharedPreferences에 저장하여 세션 유지
- 프로필 정보 조회 및 수정(직업, 학교, 연락처, 소개 등)

**사용 기술:** Java, Android SDK, RecyclerView, CardView, NavigationView, CollapsingToolbarLayout, AppBarLayout, FloatingActionButton, Google Places API, SmoothDateRangePicker, Jackson, AsyncTask, SharedPreferences, HttpURLConnection

**구현 특이점:**
- CommunicationManager 클래스에 GET/POST/PUT/DELETE/QUERY 메서드를 집약하여 HTTP 통신 로직을 단일 책임으로 분리하고, 모든 API 요청에 X-User-Email·X-User-Token 헤더를 일관되게 주입
- BaseNaviActivity를 상속 계층의 기반으로 두어 Navigation Drawer 렌더링과 메뉴 라우팅 로직을 한 곳에서 관리하고 MainActivity가 이를 상속하는 구조를 채택
- RecyclerAdapter·ReviewRecyclerAdapter·PendingReviewRecyclerAdapter 각각에 inner AsyncTask(DownloadImageTask)를 내장하여 카드뷰 단위로 이미지를 비동기 로딩
- OwnedReviewActivity에서 Intent로 전달된 userId 유무에 따라 자신의 리뷰와 타인의 리뷰를 동일 화면에서 분기 처리하는 재사용 설계

### [what-i-did](https://github.com/YunanJeong/what-i-did)
_Python_
> 레포 분석 및 문서화

**목적:** GitHub 공개 계정의 레포지토리들을 실제 소스 파일 기반으로 분석해 포트폴리오 문서(Markdown + Word)를 자동 생성하는 CLI 도구다. README에 의존하지 않고 코드를 직접 LLM에 전달해 프로젝트 내용을 판단한다.

**주요 기능:**
- GitHub 사용자의 공개 레포지토리 목록을 비인증 REST API로 수집하고 git shallow clone으로 소스를 가져옴
- 레포별 분석 결과를 JSON 캐시로 저장해 재실행 시 LLM 재호출 없이 문서만 재생성
- Anthropic API와 AWS Bedrock 양쪽을 지원하는 LLM 클라이언트를 추상화해 동일한 분석 파이프라인 사용
- Anthropic JSON Schema output 모드로 LLM 응답 형식을 강제해 파싱 안정성 확보
- Markdown과 Word(.docx)를 pandoc 없이 동시 출력 (python-docx로 하이퍼링크 포함 직접 구성)
- 150K자 예산 내에서 README·manifest·엔트리포인트·소스 순으로 우선순위 파일을 선별해 컨텍스트 구성

**사용 기술:** Python, Anthropic, anthropic[bedrock], Typer, Rich, httpx, Pydantic, python-docx, pathspec, hatchling

**구현 특이점:**
- 시스템 프롬프트에 cache_control ephemeral을 걸어 레포 간 반복 호출 시 시스템 블록 캐시 히트를 유도하는 prompt caching 전략을 명시적으로 구현
- 파일 선별 로직에서 PRIORITY_FILES·ENTRYPOINT_STEMS·깊이 기반 우선순위 점수를 산출해 예산 초과 시 중요도 낮은 파일부터 잘리도록 정렬
- python-docx의 공개 API에 없는 하이퍼링크를 OOXML 관계(relationship) 등록 및 w:hyperlink 요소 직접 조립 방식으로 구현
- 캐시 파일 파싱 실패 시 예외를 조용히 삼키고 재분석을 유도하는 방어 패턴으로 스키마 변경에도 무중단 동작 보장

### [yunanjeong](https://github.com/YunanJeong/yunanjeong)

**목적:** GitHub 프로필 페이지에 표시되는 개인 소개 레포지토리로, 방문자에게 연락처 정보를 제공합니다.

**주요 기능:**
- LinkedIn 프로필 배지 링크 제공

**구현 특이점:**
- Shields.io 배지를 활용해 LinkedIn 링크를 시각적으로 표시

### [yunanjeong.github.io](https://github.com/YunanJeong/yunanjeong.github.io)

**목적:** GitHub Pages를 활용한 개인 프로필 또는 포트폴리오 사이트입니다.

**주요 기능:**
- GitHub Pages를 통한 정적 웹사이트 호스팅

**사용 기술:** GitHub Pages

**구현 특이점:**
- 레포지토리 자체가 GitHub 프로필 사이트 도메인(yunanjeong.github.io)과 직접 연결되어 있음

## 사이드 · 학습용 프로젝트

### [langchain-toy](https://github.com/YunanJeong/langchain-toy)

**목적:** LangChain, Streamlit, Hugging Face Transformers 등 LLM 활용 도구의 기본 사용법을 빠르게 파악하고, Prometheus 자연어 쿼리 에이전트 구현 가능성을 탐색하기 위한 학습 및 실험 공간입니다.

**주요 기능:**
- LangChain을 통한 LLM 통합 방식 정리
- Streamlit 기반 웹앱 프로토타입 구성 방법 탐색
- Hugging Face Transformers와 LangChain 연동 방안 검토
- Grafana 없이 Prometheus에 자연어 쿼리를 날리는 LangChain Agent 구현 시도

**사용 기술:** LangChain, Streamlit, Hugging Face Transformers, Python, OpenAI API

**구현 특이점:**
- Prometheus를 대상으로 자연어 기반 쿼리를 실행하는 LangChain Agent라는 구체적인 활용 목표를 설정하고, 기존 시도를 조사한 뒤 직접 구현을 계획한 점
- 각 라이브러리의 역할 경계(LangChain은 LLM 오케스트레이션, Streamlit은 UI 레이어, Hugging Face는 오픈소스 모델 공급)를 명확히 구분하여 스택을 구성한 점

### [python-package-template](https://github.com/YunanJeong/python-package-template)
_Python_
> practice. how to make python package

**목적:** Python 패키지를 직접 만들고 배포하는 방법을 익히기 위한 템플릿 레포지토리입니다. setuptools 기반의 설치 구조와 CLI 실행 가능한 패키지 골격을 제공합니다.

**주요 기능:**
- setuptools 기반 setup.py로 로컬 editable 설치 구성
- version.py 파일을 setup.py에서 동적으로 읽어 버전 관리
- argparse를 활용한 CLI 인자 처리 (필수 인자 및 선택 인자 구분)
- datetime 기본값 자동 할당 로직을 포함한 시간 인자 처리
- __main__.py를 통한 python -m 직접 실행 지원
- 패키지 구조(init, main, util, version)를 역할별로 분리

**사용 기술:** Python, setuptools, argparse

**구현 특이점:**
- version.py를 별도 파일로 분리하고 setup.py에서 파일 파싱으로 읽어오는 방식을 선택해, 버전 정보를 코드와 패키지 메타데이터 양쪽에서 일관되게 유지
- pip install -e . 의 editable 모드를 활용해 소스 수정 후 재설치 없이 바로 반영되는 개발 환경을 README에 명시적으로 안내
- setup.py 주석에서 PyPI 배포 목적이 아닌 소스코드 공유 시나리오로 용도를 명확히 한정해 사용 맥락을 구체화

## 기술 스택

- Kubernetes (15)
- Helm (14)
- Python (13)
- Docker (10)
- Java (8)
- Shell (8)
- HCL (7)
- AWS EC2 (6)
- K3s (6)
- Kafka Connect (6)
- Prometheus (6)
- Apache Kafka (5)
- Bash (5)
- Terraform (5)
- Grafana (4)
- jq (4)
- Kafka (4)
- Maven (4)
- YAML (4)
- AWS CLI (3)
- AWS Security Groups (3)
- Filebeat (3)
- Jackson (3)
- JUnit Jupiter (3)
- Kafka Streams (3)
- Loki (3)
- Redis (3)
- Traefik (3)
- Android SDK (2)
- apt (2)
- argparse (2)
- AsyncTask (2)
- bitnami/kafka (2)
- CardView (2)
- Confluent kafka-connect-storage-partitioner (2)
- Confluent Platform (2)
- curl (2)
- Docker Compose (2)
- Fluentd (2)
- Git (2)
- Google Places API (2)
- Gradle (2)
- httpx (2)
- JDBC Source Connector (2)
- k9s (2)
- Karpenter (2)
- kcat (2)
- kube-prometheus-stack (2)
- kubernetes-dashboard (2)
- Logback (2)
- MySQL (2)
- ncftp (2)
- node-exporter (2)
- OpenAI API (2)
- Packer (2)
- RecyclerView (2)
- requests (2)
- setuptools (2)
- Skaffold (2)
- SLF4J (2)
- Snakemake (2)
- systemd (2)
- Ubuntu (2)
- WSL2 (2)
- Alertmanager (1)
- Amazon Athena (1)
- Amazon EBS (1)
- Amazon EKS (1)
- Amazon S3 (1)
- Ansible (1)
- Anthropic (1)
- anthropic[bedrock] (1)
- Apache Commons Lang (1)
- Apache Flink (1)
- Apache Kafka Connect (1)
- AppBarLayout (1)
- AWS AMI (1)
- AWS Bedrock (1)
- AWS EKS (1)
- AWS IAM (1)
- AWS Lambda (1)
- AWS Load Balancer Controller (1)
- AWS NAT Gateway (1)
- AWS SNS (1)
- AWS VPC (1)
- awswrangler (1)
- Bitnami MySQL (1)
- Bitnami Redis Chart (1)
- body-parser (1)
- boto3 (1)
- CentOS (1)
- CollapsingToolbarLayout (1)
- commons-codec (1)
- crontab (1)
- DBeaver (1)
- Debezium (1)
- Docker Registry API v2 (1)
- dpkg (1)
- Elasticsearch (1)
- envsubst (1)
- Express (1)
- filebrowser (1)
- find (1)
- FloatingActionButton (1)
- Fluent Bit (1)
- fluent-plugin-beats (1)
- fluent-plugin-kafka (1)
- fluent-plugin-redis (1)
- formidable (1)
- ftplib (1)
- Gemini CLI (1)
- GitHub Pages (1)
- GitLab CE (1)
- gRPC (1)
- hatchling (1)
- HttpURLConnection (1)
- Hugging Face Transformers (1)
- IntelliJ IDEA (1)
- Jade (1)
- JMX Exporter (1)
- JUnit (1)
- Kafka UI (1)
- kafka-ui (1)
- kafka-ui (kafbat) (1)
- Kibana (1)
- kohya_ss (1)
- ksqlDB (1)
- LangChain (1)
- librdkafka (1)
- logging (1)
- Logitech G Hub (1)
- logstash-logback-encoder (1)
- Lua (1)
- mailutils (1)
- MariaDB (1)
- MetalLB (1)
- Microsoft SQL Server (1)
- morgan (1)
- NavigationView (1)
- Node.js (1)
- NVIDIA CUDA (1)
- Ollama (1)
- pandas (1)
- pathspec (1)
- PowerShell (1)
- Prometheus Operator (1)
- prometheus-agent (1)
- prometheus-proxy (1)
- Promtail (1)
- Pydantic (1)
- pymsteams (1)
- pytest (1)
- python-docx (1)
- PyYAML (1)
- rdkafka (1)
- readline (1)
- Rich (1)
- rich (1)
- S3 Sink Connector (1)
- sed (1)
- SharedPreferences (1)
- SmoothDateRangePicker (1)
- smtplib (1)
- Sonatype Nexus3 (1)
- SQL Server (1)
- Stable Diffusion WebUI (1)
- Streamlit (1)
- Strimzi (1)
- system-stubs-jupiter (1)
- T-SQL (1)
- td-agent (1)
- Typer (1)
- unittest (1)
- uv (1)
- vim (1)
- WinRM (1)
- WordPress (1)
- WSL (1)
- yq (1)

---
_생성 시각: 2026-05-06 06:00 UTC · 모델: global.anthropic.claude-sonnet-4-6_
