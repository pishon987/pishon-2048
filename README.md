# 크리스마스 2048 (안드로이드)

스와이프로 숫자를 합쳐 2048을 만드는 단순 퍼즐 게임의 안드로이드 앱입니다.
2026년 12월 시즌에 맞춰 **크리스마스 테마**(눈 내리는 성탄 밤, 에메랄드·레드·골드,
타일별 크리스마스 심볼)로 꾸몄고, 게임 규칙은 그대로입니다.

게임 로직과 화면은 앱에 내장된 HTML 한 장(`app/src/main/assets/index.html`)에서 돌아가고,
안드로이드 쪽은 그 화면을 띄우는 얇은 껍데기(WebView)입니다.

- 패키지: `com.pishon.game2048` (변경 없음 — 덮어쓰기 설치·Play Console 호환)
- 버전: `versionCode 2` / `versionName 1.1.0`
- minSdk 24 (Android 7.0) / targetSdk 35 / compileSdk 35
- 권한 요청 없음, `INTERNET` 권한조차 없음 → 완전 오프라인
- 세로 화면 고정

## 크리스마스 테마

| 요소 | 내용 |
| --- | --- |
| 색 | 깊은 성탄 밤(거의 검정에 가까운 솔잎빛) 위에 에메랄드·레드·골드 |
| 눈 | 화면 뒤 canvas에 흩날리는 눈송이. 60fps를 해치지 않도록 20~46개, 그림자·블러 없음, 앱이 백그라운드로 가면 정지 |
| 타일 심볼 | `2❄️ → 4🧦 → 8🍬 → 16🔔 → 32🕯️ → 64⛄ → 128🦌 → 256🎄 → 512🎁 → 1024⭐ → 2048🎅` (2048 초과는 ✨) |
| 숫자 | 심볼은 CSS로 얹고 타일의 글자는 숫자 그대로 → 2048 규칙이 헷갈리지 않음 |
| 아이콘 | 크리스마스 트리 + 별 + `2048` (적응형 아이콘 + 레거시 mipmap). 재생성: `tools/make_icon.py` |

## 기능

| 기능 | 설명 |
| --- | --- |
| 4×4 스와이프 | 화면 스와이프, 방향키, WASD 모두 지원 |
| 타일 애니메이션 | 이동은 슬라이드, 합쳐질 때는 팝(pop) 효과 |
| 점수 / 최고 점수 | 기기 로컬 스토리지에 저장, 앱을 다시 열어도 유지 |
| 이어하기 | 앱을 닫아도 진행 중이던 게임판을 복원 |
| 되돌리기 | 직전 한 수만 되돌림 (1회) |
| 새 게임 | 즉시 새 판 시작 |
| 2048 달성 / 게임 오버 | 오버레이 안내, "계속하기" 또는 "새 게임" |

## GitHub Actions

`.github/workflows/build.yml` 이 `main` 브랜치에 푸시될 때마다 실행되어 다음을 만듭니다.

- `app-debug.apk` — 서명된 디버그 APK (갤럭시에 바로 설치해 테스트)
- `app-release.aab` — 릴리스 키스토어로 서명된 Play Store 제출용 App Bundle

두 파일은 실행 결과 페이지 하단의 **Artifacts** 에서 내려받습니다
(`app-debug-apk`, `app-release-aab`).

### 릴리스 서명

키스토어 파일과 비밀번호는 저장소에 커밋하지 않습니다. 다음 4개의 저장소 시크릿으로만 전달됩니다.

| 시크릿 | 값 |
| --- | --- |
| `ANDROID_KEYSTORE_BASE64` | 릴리스 `.jks` 파일을 base64로 인코딩한 문자열 |
| `ANDROID_KEYSTORE_PASSWORD` | 키스토어 비밀번호 |
| `ANDROID_KEY_ALIAS` | 키 별칭 |
| `ANDROID_KEY_PASSWORD` | 키 비밀번호 |

워크플로는 시크릿을 디코드해 `$RUNNER_TEMP/release.jks` 로 만들고, Gradle이 환경변수
`ANDROID_KEYSTORE_PATH` 를 통해 그 파일로 `bundleRelease` 에 서명합니다.
시크릿이 없으면 릴리스 번들은 서명 없이 만들어지고 워크플로에 경고가 남습니다.

시크릿을 갱신하려면:

```bash
base64 -w0 release.jks | gh secret set ANDROID_KEYSTORE_BASE64 -R pishon987/pishon-2048
gh secret set ANDROID_KEYSTORE_PASSWORD -R pishon987/pishon-2048
gh secret set ANDROID_KEY_ALIAS -R pishon987/pishon-2048
gh secret set ANDROID_KEY_PASSWORD -R pishon987/pishon-2048
```

> 키스토어 원본과 비밀번호는 별도로 백업해 두어야 합니다. Play Console에 새 버전을 올릴 때
> 같은 키로 서명해야 하며, 분실하면 기존 앱을 업데이트할 수 없습니다.

## 테스트

```bash
python3 tests/test_game_logic.py
```

QuickJS에 `assets/index.html`의 스크립트를 그대로 올리고, 독립적으로 작성한 2048 규칙 구현과
600수 난수 대국의 판·점수를 매 수 비교합니다. 여기에 더해 크리스마스 테마(타일 심볼·색·앱 이름·
버전·권한 없음)와 `docs/play.html` 동기화까지 함께 확인합니다.

## 로컬 빌드

```bash
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_KEYSTORE_PATH=/absolute/path/to/release.jks
export ANDROID_KEYSTORE_PASSWORD=...
export ANDROID_KEY_ALIAS=...
export ANDROID_KEY_PASSWORD=...
./gradlew assembleDebug bundleRelease
```

산출물:

- `app/build/outputs/apk/debug/app-debug.apk`
- `app/build/outputs/bundle/release/app-release.aab`

## 테스트 설치 (갤럭시)

1. Actions 실행에서 `app-debug-apk` 아티팩트를 내려받아 압축을 풉니다.
2. 휴대폰으로 옮긴 뒤 파일을 열고 "출처를 알 수 없는 앱 설치"를 허용합니다.
3. 또는 USB 디버깅 상태에서:

```bash
adb install -r app-debug.apk
```

## Play Store 제출

1. Play Console에서 앱을 만들고 `app-release.aab` 를 업로드합니다.
2. 앱 이름: **크리스마스 2048** · 아이콘: 512×512 PNG (Play Console 등록용)
3. 개인정보처리방침 URL: <https://pishon987.github.io/pishon-2048/privacy.html>
4. 데이터 보안 양식: "수집하거나 공유하는 데이터 없음"으로 응답합니다 (앱이 실제로 아무것도 수집하지 않습니다).
5. 콘텐츠 등급 설문: 폭력·성·도박·광고 없음.

## 문서 페이지 (GitHub Pages)

- 게임 소개: <https://pishon987.github.io/pishon-2048/>
- 웹에서 해보기: <https://pishon987.github.io/pishon-2048/play.html>
- 개인정보처리방침: <https://pishon987.github.io/pishon-2048/privacy.html>

`docs/play.html` 은 `app/src/main/assets/index.html` 과 같은 게임의 사본입니다.
게임을 고칠 때는 `assets/index.html` 을 고친 뒤 `docs/play.html` 로 복사합니다.
