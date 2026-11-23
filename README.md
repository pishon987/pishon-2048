# 2048 (안드로이드)

스와이프로 숫자를 합쳐 2048을 만드는 단순 퍼즐 게임의 안드로이드 앱입니다.
게임 로직과 화면은 앱에 내장된 HTML 한 장(`app/src/main/assets/index.html`)에서 돌아가고,
안드로이드 쪽은 그 화면을 띄우는 얇은 껍데기(WebView)입니다.

- 패키지: `com.pishon.game2048`
- minSdk 24 (Android 7.0) / targetSdk 35 / compileSdk 35
- 권한 요청 없음, `INTERNET` 권한조차 없음 → 완전 오프라인
- 세로 화면 고정

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
2. 개인정보처리방침 URL: <https://pishon987.github.io/pishon-2048/privacy.html>
3. 데이터 보안 양식: "수집하거나 공유하는 데이터 없음"으로 응답합니다 (앱이 실제로 아무것도 수집하지 않습니다).
4. 콘텐츠 등급 설문: 폭력·성·도박·광고 없음.

## 문서 페이지 (GitHub Pages)

- 게임 소개: <https://pishon987.github.io/pishon-2048/>
- 웹에서 해보기: <https://pishon987.github.io/pishon-2048/play.html>
- 개인정보처리방침: <https://pishon987.github.io/pishon-2048/privacy.html>

`docs/play.html` 은 `app/src/main/assets/index.html` 과 같은 게임의 사본입니다.
게임을 고칠 때는 `assets/index.html` 을 고친 뒤 `docs/play.html` 로 복사합니다.
