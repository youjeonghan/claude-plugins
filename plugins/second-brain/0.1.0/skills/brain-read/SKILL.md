---
name: brain-read
description: Second Brain 볼트에서 문서를 검색·참조한다. description 프론트매터 인덱스를 우선 grep해 관련 파일만 선별적으로 읽어 응답 효율을 높인다.
---

# Brain Read 스킬

볼트에서 관련 문서를 찾아 읽고 요약한다.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json`을 Read해 `vault.path`를 가져온다.

## Step 1: description 인덱스 검색

볼트 전체에서 `description:` 프론트매터 필드를 grep해 후보 파일 목록 생성:

```
Grep(pattern="^description:", path="{vault_path}", glob="**/*.md", output_mode="content")
```

결과 예시:
```
Projects/눕/아이템_시스템_설계.md:description: 눕 게임의 아이템 드롭, 등급, 강화 시스템 전반 설계
Resources/게임 개발/인벤토리_패턴.md:description: 게임 인벤토리 구현 패턴 및 데이터 구조 비교
```

## Step 2: 관련 파일 선별

사용자 쿼리와 description을 비교해 관련성 높은 파일 **최대 5개**만 선별.

description만으로 판단이 어려우면 `type`, `tags`, `domain` 필드도 참고:

```
Grep(pattern="^(type|tags|domain|project):", path="{vault_path}", glob="**/*.md")
```

## Step 3: 선별된 파일 전체 읽기

선별된 파일만 Read로 전체 내용 읽기. 관련 없는 파일은 읽지 않는다.

## Step 4: 응답

- 핵심 내용 요약
- 관련 `[[WikiLinks]]` 안내
- 파일 절대 경로 함께 표기 (Cmd+클릭 이동용)
- 추가로 봐야 할 연관 문서가 있으면 언급

## 주의

- description 필드가 없는 파일은 파일명과 tags로 판단
- 검색 결과가 없으면 "관련 문서가 없습니다. brain-write로 새로 작성할까요?" 제안
- 한국어로 응답
