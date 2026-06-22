# 착수 프롬프트 — 1단계: 기존 자산 이식

> 이 프롬프트를 Claude Code 또는 Cursor에 붙여넣어 작업을 시작한다.
> `PROJECT.md`와 `AGENTS.md`가 같은 저장소에 있어야 한다.

---

`PROJECT.md`와 `AGENTS.md`를 먼저 읽어줘.

이번 세션에서는 `PROJECT.md` §9 로드맵의 **1단계(기존 자산 이식)** 까지만 진행한다.
2단계(찬양예배 PPT) 이후는 다음 세션에서 별도로 진행할 거니까 이번엔 손대지 마.

## 이번 세션 목표

1. `PROJECT.md` §6 디렉토리 구조대로 프로젝트 골격을 만든다.
2. 아래 "내가 가진 것" 항목을 확인하고, 기존 코드가 있으면 그대로 `app/engines/`에
  배치해서 재사용한다. 없으면 `PROJECT.md` §3.1, §3.2의 설명대로 새로 작성한다.
3. 한글 주보 생성(`/api/bulletin/hwp`)과 주일낮예배 PPT 생성(`/api/bulletin/ppt/day`)
  API를 동작하게 만든다.
4. `AGENTS.md` §2에 따라 구역 마커 정의는 `app/section_config/sunday_day.json`으로
  분리한다.
5. 최소한의 프런트엔드(주보/PPT 생성 화면 — `PROJECT.md` §2.3)를 Bootstrap +
  Pretendard로 만들어서, 폼 입력 → API 호출 → 결과 다운로드까지 한 번에 테스트해볼
   수 있게 한다. 디자인 디테일은 나중에 다듬을 거니까 이번엔 동작 위주로.

## 내가 가진 것 (작업 시작 전 직접 채워 넣을 것)

- [ ] 기존 `hwp_engine.py` 코드: (있음 / 없음 — 첨부 또는 경로 기재)
- [ ] 기존 `ppt_engine.py` 코드: (있음 / 없음 — 첨부 또는 경로 기재)
- [ ] 주보 hwpx 템플릿 파일: (경로: C:\Users\churchCom\Documents\churchCloud\교회 문서\03 주보\광주새백성교회_주보_2026_메일머지.hwpx)
- [ ] 주일낮예배 pptx 템플릿 파일 (구역 마커 포함): (경로 : C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\주일낮예배-2026-템플릿.pptx)
- [ ] 메일머지 필드 전체 목록 (60여 개, `F_`/`R_A_` 등 접두사): (C:\Users\churchCom\Documents\churchCloud\교회 문서\03 주보\주보_메일머지필드.xlsx)
- [ ] 찬송가 PPT 폴더 경로 및 실제 파일명 샘플 몇 개: (C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\찬송가 PPT\찬001_만복의근원하나님.pptx)
- [ ] 개발/테스트할 PC 환경: (Windows + 한글/PowerPoint 설치 여부 확인)

## 막히면

`AGENTS.md` §0, §1에 따라 — 메일머지 필드명이나 파일명 규칙이 불확실하면 추측해서
진행하지 말고 나한테 먼저 물어봐.

win32com 코드는 이 작업 환경에서 직접 실행 검증이 안 되니까, 코드 작성 후 "실제
Windows PC에서 이렇게 테스트해보세요" 형태로 검증 방법을 같이 알려줘.