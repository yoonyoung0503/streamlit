import streamlit as st
import sqlite3
import pandas as pd

# ── 페이지 설정 ────────────────────────────────────────────────
st.set_page_config(
    page_title="SQL 교육자료 | 주택금융",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 공통 스타일 ────────────────────────────────────────────────
st.markdown("""
<style>
    .section-header {
        font-size: 1.7rem; font-weight: 800;
        color: #1a1a2e;
        border-bottom: 3px solid #1565C0;
        padding-bottom: 0.4rem; margin-bottom: 1.2rem;
    }
    .sub-header {
        font-size: 1.15rem; font-weight: 700;
        color: #1565C0; margin: 1.2rem 0 0.4rem;
    }
    .tip-box {
        background: #E3F2FD; border-left: 4px solid #1565C0;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
    }
    .warn-box {
        background: #FFF8E1; border-left: 4px solid #F9A825;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
    }
    .good-box {
        background: #E8F5E9; border-left: 4px solid #2E7D32;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
    }
    .syntax-box {
        background: #F3E5F5; border-left: 4px solid #6A1B9A;
        padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.6rem 0;
        font-family: monospace; font-size: 0.95rem;
    }
    .step-badge {
        display: inline-block;
        background: #1565C0; color: white;
        border-radius: 50%; width: 28px; height: 28px;
        text-align: center; line-height: 28px;
        font-weight: 700; margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DB 초기화 — 주택금융 테마 샘플 데이터
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript("""
        -- 지역 마스터
        CREATE TABLE regions (
            region_id   INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL,
            region_type TEXT  -- 수도권 / 지방
        );

        -- 주택보증 공급 현황
        CREATE TABLE loan_guarantee (
            guarantee_id     INTEGER PRIMARY KEY,
            guarantee_no     TEXT NOT NULL,       -- 보증번호
            base_year        INTEGER NOT NULL,    -- 기준연도
            region_id        INTEGER,
            product_type     TEXT,                -- 상품유형 (전세/구입/중도금/전세대출)
            supply_count     INTEGER,             -- 공급건수
            guarantee_amount REAL,               -- 보증금액 (억원)
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );

        -- 주택연금 현황
        CREATE TABLE housing_pension (
            pension_id      INTEGER PRIMARY KEY,
            base_year       INTEGER NOT NULL,    -- 기준연도
            region_id       INTEGER,
            join_count      INTEGER,             -- 가입건수
            pension_payment REAL,               -- 연금지급액 (억원)
            avg_house_price REAL,               -- 평균주택가격 (억원)
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );

        -- 지역 데이터
        INSERT INTO regions VALUES
            (1, '서울', '수도권'),
            (2, '경기', '수도권'),
            (3, '인천', '수도권'),
            (4, '부산', '지방'),
            (5, '대구', '지방'),
            (6, '광주', '지방'),
            (7, '대전', '지방'),
            (8, '강원', '지방');

        -- 주택보증 데이터 (2020~2023, 지역별, 상품별)
        INSERT INTO loan_guarantee VALUES
            (1,  'G-2020-0001', 2020, 1, '전세',     12400, 1850.5),
            (2,  'G-2020-0002', 2020, 1, '구입',      8200, 3120.0),
            (3,  'G-2020-0003', 2020, 1, '중도금',    5100, 2340.0),
            (4,  'G-2020-0004', 2020, 2, '전세',     18700, 2100.0),
            (5,  'G-2020-0005', 2020, 2, '구입',     11500, 4200.0),
            (6,  'G-2020-0006', 2020, 3, '전세',      5800,  980.0),
            (7,  'G-2020-0007', 2020, 4, '전세',      4200,  540.0),
            (8,  'G-2020-0008', 2020, 4, '구입',      2900,  870.0),
            (9,  'G-2021-0001', 2021, 1, '전세',     13200, 2050.0),
            (10, 'G-2021-0002', 2021, 1, '구입',      9100, 3560.0),
            (11, 'G-2021-0003', 2021, 1, '전세대출', 22000, 4100.0),
            (12, 'G-2021-0004', 2021, 2, '전세',     20100, 2450.0),
            (13, 'G-2021-0005', 2021, 2, '구입',     13200, 5100.0),
            (14, 'G-2021-0006', 2021, 3, '전세',      6400, 1100.0),
            (15, 'G-2021-0007', 2021, 5, '전세',      3100,  420.0),
            (16, 'G-2021-0008', 2021, 6, '구입',      1800,  510.0),
            (17, 'G-2022-0001', 2022, 1, '전세',     11800, 1920.0),
            (18, 'G-2022-0002', 2022, 1, '구입',      8600, 3300.0),
            (19, 'G-2022-0003', 2022, 1, '전세대출', 25000, 4800.0),
            (20, 'G-2022-0004', 2022, 2, '전세',     19200, 2280.0),
            (21, 'G-2022-0005', 2022, 2, '중도금',    8400, 3100.0),
            (22, 'G-2022-0006', 2022, 4, '전세',      4500,  580.0),
            (23, 'G-2022-0007', 2022, 7, '전세',      2100,  310.0),
            (24, 'G-2022-0008', 2022, 8, '구입',       980,  220.0),
            (25, 'G-2023-0001', 2023, 1, '전세',     10500, 1750.0),
            (26, 'G-2023-0002', 2023, 1, '구입',      7800, 3050.0),
            (27, 'G-2023-0003', 2023, 1, '전세대출', 27500, 5200.0),
            (28, 'G-2023-0004', 2023, 2, '전세',     17900, 2100.0),
            (29, 'G-2023-0005', 2023, 2, '구입',     12100, 4800.0),
            (30, 'G-2023-0006', 2023, 3, '전세',      5200,  920.0),
            (31, 'G-2023-0007', 2023, 5, '구입',      2400,  680.0),
            (32, 'G-2023-0008', 2023, 6, '전세',      1900,  280.0);

        -- 주택연금 데이터 (2020~2023, 지역별)
        INSERT INTO housing_pension VALUES
            (1,  2020, 1, 18200,  9840.0, 4.2),
            (2,  2020, 2, 12400,  5210.0, 3.1),
            (3,  2020, 3,  4100,  1580.0, 2.4),
            (4,  2020, 4,  5800,  1940.0, 2.1),
            (5,  2020, 5,  3200,   980.0, 1.9),
            (6,  2020, 6,  2100,   620.0, 1.7),
            (7,  2021, 1, 21500, 12100.0, 4.5),
            (8,  2021, 2, 15100,  6540.0, 3.4),
            (9,  2021, 3,  5200,  2010.0, 2.6),
            (10, 2021, 4,  6700,  2340.0, 2.2),
            (11, 2021, 5,  3800,  1180.0, 2.0),
            (12, 2021, 7,  2900,   890.0, 1.8),
            (13, 2022, 1, 24100, 14200.0, 4.8),
            (14, 2022, 2, 17800,  7900.0, 3.7),
            (15, 2022, 3,  6100,  2480.0, 2.8),
            (16, 2022, 4,  7500,  2710.0, 2.3),
            (17, 2022, 6,  2500,   760.0, 1.8),
            (18, 2022, 8,  1200,   350.0, 1.5),
            (19, 2023, 1, 26800, 16500.0, 5.1),
            (20, 2023, 2, 19500,  9100.0, 3.9),
            (21, 2023, 3,  6900,  2850.0, 3.0),
            (22, 2023, 4,  8200,  3020.0, 2.5),
            (23, 2023, 5,  4500,  1420.0, 2.1),
            (24, 2023, 7,  3100,   980.0, 1.9);
    """)
    conn.commit()
    return conn


def run_sql(conn, sql):
    try:
        df = pd.read_sql_query(sql, conn)
        return df, None
    except Exception as e:
        return None, str(e)


def show_result(conn, sql, key):
    """실행 버튼 + 결과 출력 공통 함수"""
    if st.button("▶ 실행", key=key):
        df, err = run_sql(conn, sql)
        if err:
            st.error(f"오류: {err}")
        else:
            st.success(f"✅ {len(df)}행 반환")
            st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# 사이드바 네비게이션
# ══════════════════════════════════════════════════════════════
SECTIONS = [
    "🏠 개요 & 학습 순서",
    "📖 SQL 기본 문법",
    "🛠️ 실습 환경 구축",
    "① SELECT — 데이터 조회",
    "② WHERE — 조건 필터",
    "③ LIKE — 패턴 검색",
    "④ ORDER BY — 정렬",
    "⑤ GROUP BY — 집계",
    "⑥ JOIN — 테이블 결합",
    "🚀 복합 쿼리 실전",
    "✏️ 직접 실습",
]

with st.sidebar:
    st.title("🏠 SQL 교육자료")
    st.caption("주택금융 데이터로 배우는 ANSI SQL")
    st.divider()

    # 학습 진행 단계 표시
    st.markdown("**📚 학습 단계**")
    st.markdown("""
<small>
<b>STEP 1.</b> 개요 & 기본 문법<br>
<b>STEP 2.</b> 실습 환경 구축<br>
<b>STEP 3.</b> SELECT → WHERE → LIKE<br>
<b>STEP 4.</b> ORDER BY → GROUP BY → JOIN<br>
<b>STEP 5.</b> 복합 쿼리 & 자유 실습
</small>
""", unsafe_allow_html=True)
    st.divider()

    section = st.radio("단원 선택", SECTIONS, label_visibility="collapsed")
    st.divider()
    st.caption("실습 DB: SQLite (인메모리)\nregions / loan_guarantee / housing_pension")

conn = get_db()


# ══════════════════════════════════════════════════════════════
# 0. 개요
# ══════════════════════════════════════════════════════════════
if section == SECTIONS[0]:
    st.markdown('<div class="section-header">🏠 SQL 교육자료 — 주택금융 데이터로 배우는 ANSI SQL</div>', unsafe_allow_html=True)

    st.markdown("""
    이 교육자료는 **주택금융 업무 데이터**를 예시로 SQL 쿼리 작성 능력을 단계별로 익힙니다.  
    실제 업무에서 자주 다루는 **기준연도, 보증번호, 공급건수, 연금지급액** 등의 컬럼을 활용합니다.
    """)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📋 학습 순서")
        st.markdown("""
| 단계 | 내용 |
|------|------|
| **STEP 1** | SQL이란? 기본 문법 구조 이해 |
| **STEP 2** | 실습 환경(DB·테이블) 구축 및 데이터 확인 |
| **STEP 3** | SELECT / WHERE / LIKE |
| **STEP 4** | ORDER BY / GROUP BY / JOIN |
| **STEP 5** | 복합 쿼리 실전 & 자유 실습 |
        """)

    with col2:
        st.markdown("### 🗂️ 실습 데이터 주제")
        st.markdown("""
| 테이블 | 내용 |
|--------|------|
| `regions` | 지역 마스터 (서울·경기 등) |
| `loan_guarantee` | 주택보증 공급 현황 (기준연도·보증번호·공급건수·보증금액) |
| `housing_pension` | 주택연금 현황 (기준연도·가입건수·연금지급액) |
        """)

    st.divider()
    st.markdown("### 🔑 핵심 SQL 키워드 한눈에 보기")

    kw_cols = st.columns(6)
    keywords = ["SELECT", "WHERE", "LIKE", "ORDER BY", "GROUP BY", "JOIN"]
    descs = ["조회", "조건", "패턴", "정렬", "집계", "결합"]
    colors = ["#1565C0","#2E7D32","#6A1B9A","#E65100","#AD1457","#00695C"]
    for col, kw, desc, color in zip(kw_cols, keywords, descs, colors):
        col.markdown(f"""
        <div style="background:{color};color:white;border-radius:10px;
                    padding:18px 8px;text-align:center;margin:4px 0;">
            <div style="font-size:1rem;font-weight:700;">{kw}</div>
            <div style="font-size:0.8rem;opacity:0.9;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div class="tip-box">
    💡 <b>이 자료 활용법</b><br>
    왼쪽 사이드바에서 단원을 순서대로 학습하세요.  
    각 예제의 <b>▶ 실행</b> 버튼을 눌러 결과를 직접 확인하고,  
    마지막 <b>✏️ 직접 실습</b> 탭에서 자유롭게 쿼리를 작성해보세요.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 1. SQL 기본 문법
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[1]:
    st.markdown('<div class="section-header">📖 SQL 기본 문법</div>', unsafe_allow_html=True)

    # ── SQL이란 ──
    st.markdown("## SQL이란?")
    st.markdown("""
    **SQL (Structured Query Language)** 은 관계형 데이터베이스(RDBMS)에서 데이터를 조회·삽입·수정·삭제하기 위한 표준 언어입니다.
    - 1970년대 IBM에서 개발, ANSI/ISO 표준으로 채택
    - Oracle, MySQL, PostgreSQL, SQL Server, SQLite 등 거의 모든 RDBMS에서 사용
    - 업무 데이터 분석의 필수 도구
    """)

    st.divider()

    # ── SQL 분류 ──
    st.markdown("## SQL 명령어 분류")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#E3F2FD;border-radius:10px;padding:16px;">
        <b>📥 DML (데이터 조작)</b><br>
        Data Manipulation Language<br><br>
        • <code>SELECT</code> — 조회<br>
        • <code>INSERT</code> — 삽입<br>
        • <code>UPDATE</code> — 수정<br>
        • <code>DELETE</code> — 삭제<br><br>
        <small>⭐ 이 자료에서 집중적으로 다룹니다</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#F3E5F5;border-radius:10px;padding:16px;">
        <b>🏗️ DDL (데이터 정의)</b><br>
        Data Definition Language<br><br>
        • <code>CREATE</code> — 테이블 생성<br>
        • <code>ALTER</code> — 구조 변경<br>
        • <code>DROP</code> — 삭제<br>
        • <code>TRUNCATE</code> — 전체 삭제<br>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#E8F5E9;border-radius:10px;padding:16px;">
        <b>🔐 DCL (데이터 제어)</b><br>
        Data Control Language<br><br>
        • <code>GRANT</code> — 권한 부여<br>
        • <code>REVOKE</code> — 권한 회수<br>
        • <code>COMMIT</code> — 트랜잭션 확정<br>
        • <code>ROLLBACK</code> — 트랜잭션 취소<br>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── 전체 SELECT 문법 구조 ──
    st.markdown("## SELECT 전체 문법 구조")
    st.markdown("""
    <div class="tip-box">
    💡 SQL 키워드는 대소문자를 구분하지 않습니다. 관례상 키워드는 <b>대문자</b>, 컬럼·테이블명은 <b>소문자</b>로 작성합니다.
    </div>
    """, unsafe_allow_html=True)

    st.code("""-- SELECT 전체 문법 ([ ] 는 선택 요소)
SELECT   [DISTINCT] column1, column2, 집계함수, ...
FROM     table_name  [AS alias]
[JOIN    other_table ON 조인조건]
[WHERE   행 필터 조건]
[GROUP BY 그룹 기준 컬럼]
[HAVING  집계 결과 필터 조건]
[ORDER BY 정렬 컬럼 [ASC|DESC]]
[LIMIT   n];""", language="sql")

    st.markdown("### ⚙️ SQL 실행 순서 (작성 순서 ≠ 실행 순서)")
    st.markdown("""
    <div class="warn-box">
    ⚠️ SQL은 <b>작성 순서</b>와 <b>실행 순서</b>가 다릅니다. 이를 이해해야 WHERE/HAVING 혼동을 피할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    exec_cols = st.columns(7)
    steps = [
        ("①", "FROM", "테이블 로드"),
        ("②", "JOIN", "테이블 결합"),
        ("③", "WHERE", "행 필터"),
        ("④", "GROUP BY", "그룹화"),
        ("⑤", "HAVING", "집계 필터"),
        ("⑥", "SELECT", "컬럼 선택"),
        ("⑦", "ORDER BY", "정렬"),
    ]
    bg_colors = ["#E8EAF6","#E3F2FD","#F3E5F5","#E8F5E9","#FFF8E1","#FCE4EC","#E0F7FA"]
    for col, (num, kw, desc), bg in zip(exec_cols, steps, bg_colors):
        col.markdown(f"""
        <div style="background:{bg};border-radius:8px;padding:12px 6px;text-align:center;">
        <div style="font-size:1.2rem;font-weight:700;">{num}</div>
        <div style="font-size:0.85rem;font-weight:700;color:#1a1a2e;">{kw}</div>
        <div style="font-size:0.72rem;color:#555;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── 데이터 타입 ──
    st.markdown("## 주요 데이터 타입")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
| 타입 | 설명 | 예시 |
|------|------|------|
| `INTEGER` | 정수 | 공급건수, 기준연도 |
| `REAL` / `FLOAT` | 실수 | 보증금액, 연금지급액 |
| `TEXT` / `VARCHAR` | 문자열 | 보증번호, 지역명 |
| `DATE` | 날짜 | '2023-01-01' |
        """)
    with col2:
        st.markdown("""
| 개념 | 설명 |
|------|------|
| `NULL` | 값이 없음 (0이나 빈 문자열과 다름) |
| `PRIMARY KEY` | 행을 유일하게 식별하는 컬럼 |
| `FOREIGN KEY` | 다른 테이블을 참조하는 컬럼 |
| `NOT NULL` | 반드시 값이 있어야 하는 제약 |
        """)

    st.divider()

    # ── 연산자 ──
    st.markdown("## 연산자 정리")
    tab1, tab2, tab3 = st.tabs(["비교 연산자", "논리 연산자", "집계 함수"])
    with tab1:
        st.markdown("""
| 연산자 | 의미 | 예시 |
|--------|------|------|
| `=` | 같다 | `base_year = 2023` |
| `<>` 또는 `!=` | 다르다 | `product_type <> '전세'` |
| `>` / `<` | 크다 / 작다 | `supply_count > 10000` |
| `>=` / `<=` | 이상 / 이하 | `base_year >= 2022` |
| `BETWEEN a AND b` | a 이상 b 이하 (양 끝 포함) | `supply_count BETWEEN 5000 AND 15000` |
| `IN (...)` | 목록 중 하나 | `product_type IN ('전세', '구입')` |
| `IS NULL` | 값이 NULL | `region_id IS NULL` |
| `IS NOT NULL` | 값이 NULL이 아님 | `pension_payment IS NOT NULL` |
        """)
    with tab2:
        st.markdown("""
| 연산자 | 의미 | 예시 |
|--------|------|------|
| `AND` | 두 조건 모두 참 | `base_year = 2023 AND supply_count > 5000` |
| `OR` | 둘 중 하나 참 | `product_type = '전세' OR product_type = '구입'` |
| `NOT` | 조건 부정 | `NOT product_type = '중도금'` |
| `LIKE` | 패턴 매칭 | `guarantee_no LIKE 'G-2023%'` |
        """)
    with tab3:
        st.markdown("""
| 함수 | 설명 | 예시 |
|------|------|------|
| `COUNT(*)` | 전체 행 수 | `COUNT(*)` |
| `COUNT(col)` | NULL 제외 행 수 | `COUNT(supply_count)` |
| `SUM(col)` | 합계 | `SUM(supply_count)` |
| `AVG(col)` | 평균 | `AVG(guarantee_amount)` |
| `MAX(col)` | 최댓값 | `MAX(pension_payment)` |
| `MIN(col)` | 최솟값 | `MIN(supply_count)` |
| `ROUND(val, n)` | 반올림 | `ROUND(AVG(guarantee_amount), 1)` |
        """)

    st.divider()
    st.markdown("""
    <div class="good-box">
    ✅ <b>다음 단계</b>: 사이드바에서 <b>🛠️ 실습 환경 구축</b>으로 이동해 실제 데이터를 확인하세요.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 2. 실습 환경 구축
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[2]:
    st.markdown('<div class="section-header">🛠️ 실습 환경 구축</div>', unsafe_allow_html=True)

    st.markdown("## Python + SQLite 환경 설정")
    st.markdown("""
    이 교육자료는 **Python의 내장 모듈 `sqlite3`** 와 **`pandas`** 를 활용합니다.  
    별도의 DB 서버 없이 로컬에서 즉시 실행 가능합니다.
    """)

    st.markdown("### 패키지 설치")
    st.code("pip install streamlit pandas", language="bash")

    st.markdown("### 실습 DB 구성 코드")
    st.code("""import sqlite3
import pandas as pd

# 인메모리 DB 생성 (앱 종료 시 삭제됨)
conn = sqlite3.connect(":memory:")

# 파일로 저장하려면:
# conn = sqlite3.connect("housing_finance.db")

def run(sql):
    \"\"\"SQL 실행 → DataFrame 반환\"\"\"
    return pd.read_sql_query(sql, conn)
""", language="python")

    st.divider()
    st.markdown("## 📊 실습 테이블 구조 (ERD)")

    st.code("""regions (지역 마스터)
┌─────────────┬─────────┬─────────────┐
│ region_id PK│region_name│ region_type│
│  INTEGER    │  TEXT    │    TEXT     │
└──────┬──────┴──────────┴─────────────┘
       │ 1:N                        1:N │
       ▼                               ▼
loan_guarantee (주택보증)     housing_pension (주택연금)
┌──────────────────────┐      ┌──────────────────────┐
│ guarantee_id  PK     │      │ pension_id  PK        │
│ guarantee_no (보증번호)│      │ base_year  (기준연도)  │
│ base_year (기준연도)  │      │ region_id  FK        │
│ region_id  FK        │      │ join_count (가입건수)  │
│ product_type (상품유형)│      │ pension_payment(연금지급액)│
│ supply_count (공급건수)│      │ avg_house_price(평균주택가)│
│ guarantee_amount(보증금액)│   └──────────────────────┘
└──────────────────────┘""", language="text")

    st.divider()
    st.markdown("## 📋 테이블 데이터 미리보기")

    tab1, tab2, tab3 = st.tabs(["regions (지역)", "loan_guarantee (주택보증)", "housing_pension (주택연금)"])

    with tab1:
        df, _ = run_sql(conn, "SELECT * FROM regions")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"총 {len(df)}개 지역 | region_type: 수도권 / 지방")

    with tab2:
        df, _ = run_sql(conn, "SELECT * FROM loan_guarantee ORDER BY base_year, region_id")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"총 {len(df)}건 | 기준연도: 2020~2023 | 상품유형: 전세/구입/중도금/전세대출 | 보증금액 단위: 억원")

    with tab3:
        df, _ = run_sql(conn, "SELECT * FROM housing_pension ORDER BY base_year, region_id")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"총 {len(df)}건 | 기준연도: 2020~2023 | 연금지급액·평균주택가격 단위: 억원")

    st.divider()
    st.markdown("""
    <div class="good-box">
    ✅ 환경 구축 완료! 이제 <b>① SELECT</b> 부터 순서대로 실습을 시작하세요.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 3. SELECT
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[3]:
    st.markdown('<div class="section-header">① SELECT — 데이터 조회</div>', unsafe_allow_html=True)

    st.markdown("""
    `SELECT` 는 SQL의 가장 기본적인 명령으로, **테이블에서 원하는 데이터를 읽어오는** 구문입니다.
    """)

    st.markdown("""
    <div class="syntax-box">
    SELECT  [DISTINCT] 컬럼1, 컬럼2, ...  &nbsp;&nbsp;← 조회할 컬럼 (* = 전체)<br>
    FROM    테이블명;                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;← 대상 테이블
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    examples = [
        {
            "title": "예제 1 — 전체 컬럼 조회 (`SELECT *`)",
            "desc": "테이블의 모든 컬럼을 조회합니다. 탐색·확인 단계에서 사용하세요.",
            "sql": "SELECT *\nFROM   loan_guarantee;",
            "warn": "⚠️ 실무에서는 <code>SELECT *</code> 대신 필요한 컬럼만 명시하세요. 불필요한 데이터 전송이 줄어 성능이 향상됩니다.",
        },
        {
            "title": "예제 2 — 특정 컬럼만 조회",
            "desc": "보증번호·기준연도·공급건수 3개 컬럼만 가져옵니다.",
            "sql": "SELECT guarantee_no, base_year, supply_count\nFROM   loan_guarantee;",
        },
        {
            "title": "예제 3 — 컬럼 별칭(AS) + 산술 연산",
            "desc": "`AS`로 컬럼에 한글 별칭을 붙이고, 보증금액을 조 단위로 환산합니다.",
            "sql": """SELECT
    guarantee_no            AS 보증번호,
    base_year               AS 기준연도,
    supply_count            AS 공급건수,
    guarantee_amount        AS "보증금액(억원)",
    ROUND(guarantee_amount / 10000.0, 4) AS "보증금액(조원)"
FROM loan_guarantee;""",
        },
        {
            "title": "예제 4 — DISTINCT로 중복 제거",
            "desc": "어떤 상품유형이 존재하는지 유니크한 값만 확인합니다.",
            "sql": "SELECT DISTINCT product_type AS 상품유형\nFROM   loan_guarantee;",
        },
        {
            "title": "예제 5 — LIMIT으로 상위 N행만 조회",
            "desc": "데이터가 많을 때 처음 5행만 빠르게 확인합니다.",
            "sql": "SELECT guarantee_no, base_year, supply_count\nFROM   loan_guarantee\nLIMIT  5;",
            "tip": "💡 대용량 테이블을 처음 탐색할 때 항상 LIMIT을 붙이는 습관을 들이세요.",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            if ex.get("warn"):
                st.markdown(f'<div class="warn-box">{ex["warn"]}</div>', unsafe_allow_html=True)
            if ex.get("tip"):
                st.markdown(f'<div class="tip-box">{ex["tip"]}</div>', unsafe_allow_html=True)
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"sel_{ex['title']}")


# ══════════════════════════════════════════════════════════════
# 4. WHERE
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[4]:
    st.markdown('<div class="section-header">② WHERE — 조건 필터</div>', unsafe_allow_html=True)

    st.markdown("`WHERE` 절은 SELECT로 가져올 행을 **조건에 따라 필터링**합니다. GROUP BY 이전에 실행됩니다.")

    st.markdown("""
    <div class="syntax-box">
    SELECT 컬럼 FROM 테이블<br>
    WHERE  <b>조건식</b>;   ← 참(TRUE)인 행만 반환
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    examples = [
        {
            "title": "예제 1 — 단순 조건 (특정 연도만)",
            "desc": "2023년 기준 보증 데이터만 조회합니다.",
            "sql": "SELECT guarantee_no, base_year, product_type, supply_count\nFROM   loan_guarantee\nWHERE  base_year = 2023;",
        },
        {
            "title": "예제 2 — 비교 연산자 (공급건수 1만 건 이상)",
            "desc": "공급건수가 10,000건 이상인 대규모 보증 건만 조회합니다.",
            "sql": "SELECT guarantee_no, base_year, supply_count, guarantee_amount\nFROM   loan_guarantee\nWHERE  supply_count >= 10000;",
        },
        {
            "title": "예제 3 — AND 복합 조건",
            "desc": "2023년이면서 공급건수 5,000건 이상인 건",
            "sql": """SELECT guarantee_no, base_year, product_type, supply_count
FROM   loan_guarantee
WHERE  base_year = 2023
  AND  supply_count >= 5000;""",
        },
        {
            "title": "예제 4 — IN 목록 조건 (상품유형 2개)",
            "desc": "전세 또는 구입 상품만 필터링합니다.",
            "sql": """SELECT guarantee_no, product_type, supply_count
FROM   loan_guarantee
WHERE  product_type IN ('전세', '구입')
ORDER BY supply_count DESC;""",
        },
        {
            "title": "예제 5 — BETWEEN 범위 조건 (연도 범위)",
            "desc": "2021~2022년 데이터만 조회합니다. 양 끝값 포함입니다.",
            "sql": """SELECT guarantee_no, base_year, supply_count
FROM   loan_guarantee
WHERE  base_year BETWEEN 2021 AND 2022;""",
            "tip": "💡 BETWEEN a AND b 는 a ≤ 값 ≤ b (양 끝 포함)",
        },
        {
            "title": "예제 6 — IS NULL (지역 미배정 데이터 탐색)",
            "desc": "region_id가 NULL인 데이터를 찾습니다. (현재 예시 데이터에는 없음)",
            "sql": """SELECT guarantee_no, base_year, region_id
FROM   loan_guarantee
WHERE  region_id IS NULL;""",
            "warn": "⚠️ NULL 비교는 반드시 <code>IS NULL</code> 사용. <code>= NULL</code>은 항상 FALSE를 반환합니다.",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            if ex.get("warn"):
                st.markdown(f'<div class="warn-box">{ex["warn"]}</div>', unsafe_allow_html=True)
            if ex.get("tip"):
                st.markdown(f'<div class="tip-box">{ex["tip"]}</div>', unsafe_allow_html=True)
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"where_{ex['title']}")


# ══════════════════════════════════════════════════════════════
# 5. LIKE
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[5]:
    st.markdown('<div class="section-header">③ LIKE — 패턴 검색</div>', unsafe_allow_html=True)

    st.markdown("`LIKE` 는 문자열 컬럼에서 **특정 패턴에 맞는 값**을 검색합니다.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="syntax-box">
        WHERE 컬럼 LIKE '패턴'<br><br>
        % : 0개 이상의 임의 문자<br>
        _ : 정확히 1개의 임의 문자
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
| 패턴 | 의미 | 보증번호 예시 |
|------|------|------|
| `'G-2023%'` | G-2023으로 시작 | G-2023-0001 ✅ |
| `'%0005'` | 0005로 끝남 | G-2021-0005 ✅ |
| `'G-____-%'` | G- + 4글자 + - | 모든 보증번호 ✅ |
| `'%-000_'` | -000 + 1글자 | G-2020-0001 ✅ |
        """)

    st.divider()

    examples = [
        {
            "title": "예제 1 — 특정 연도 보증번호 검색 (`%` 앞부분 고정)",
            "desc": "보증번호가 'G-2023'으로 시작하는 건만 조회합니다.",
            "sql": """SELECT guarantee_no, base_year, product_type, supply_count
FROM   loan_guarantee
WHERE  guarantee_no LIKE 'G-2023%';""",
            "tip": "💡 앞이 고정된 LIKE '값%' 패턴은 인덱스를 활용할 수 있어 성능이 좋습니다.",
        },
        {
            "title": "예제 2 — 특정 번호로 끝나는 보증 검색",
            "desc": "보증 일련번호가 0005로 끝나는 건을 조회합니다.",
            "sql": """SELECT guarantee_no, base_year, supply_count
FROM   loan_guarantee
WHERE  guarantee_no LIKE '%-0005';""",
        },
        {
            "title": "예제 3 — 포함 검색 (상품유형에 '전세' 포함)",
            "desc": "'전세' 문자가 포함된 모든 상품유형(전세, 전세대출)을 조회합니다.",
            "sql": """SELECT DISTINCT product_type FROM loan_guarantee
WHERE product_type LIKE '%전세%';""",
        },
        {
            "title": "예제 4 — `_` 와일드카드 (글자 수 고정)",
            "desc": "보증번호 형식 'G-YYYY-NNNN' 에서 연도가 4자리인지 검증",
            "sql": """SELECT guarantee_no
FROM   loan_guarantee
WHERE  guarantee_no LIKE 'G-____-____';""",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            if ex.get("tip"):
                st.markdown(f'<div class="tip-box">{ex["tip"]}</div>', unsafe_allow_html=True)
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"like_{ex['title']}")

    st.markdown("""
    <div class="warn-box">
    ⚠️ <b>LIKE 성능 주의</b><br>
    <code>LIKE '%검색어%'</code> (앞에 %) 패턴은 인덱스를 사용하지 못해 <b>Full Table Scan</b>이 발생합니다.<br>
    대용량 테이블에서 전문 검색이 필요하다면 <b>Full-Text Index</b> 도입을 검토하세요.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 6. ORDER BY
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[6]:
    st.markdown('<div class="section-header">④ ORDER BY — 정렬</div>', unsafe_allow_html=True)

    st.markdown("`ORDER BY` 는 결과를 원하는 기준으로 **정렬**합니다. SQL 실행 순서상 가장 마지막에 적용됩니다.")

    st.markdown("""
    <div class="syntax-box">
    SELECT 컬럼 FROM 테이블<br>
    ORDER BY 컬럼1 [ASC|DESC], 컬럼2 [ASC|DESC];<br><br>
    ASC  : 오름차순 (작 → 큰, 기본값 — 생략 가능)<br>
    DESC : 내림차순 (큰 → 작)
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    examples = [
        {
            "title": "예제 1 — 공급건수 내림차순 (공급 많은 순)",
            "sql": """SELECT guarantee_no, base_year, product_type, supply_count
FROM   loan_guarantee
ORDER BY supply_count DESC;""",
        },
        {
            "title": "예제 2 — 기준연도 오름차순 → 보증금액 내림차순 (다중 정렬)",
            "desc": "연도 순서대로 보되, 같은 연도 안에서는 보증금액이 큰 순으로 정렬합니다.",
            "sql": """SELECT base_year, product_type, supply_count, guarantee_amount
FROM   loan_guarantee
ORDER BY base_year ASC, guarantee_amount DESC;""",
        },
        {
            "title": "예제 3 — 주택연금 지급액 내림차순",
            "sql": """SELECT base_year, region_id, join_count, pension_payment
FROM   housing_pension
ORDER BY pension_payment DESC;""",
        },
        {
            "title": "예제 4 — WHERE + ORDER BY 조합",
            "desc": "2023년 보증 데이터를 공급건수 높은 순으로 정렬합니다.",
            "sql": """SELECT guarantee_no, product_type, supply_count, guarantee_amount
FROM   loan_guarantee
WHERE  base_year = 2023
ORDER BY supply_count DESC;""",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"ord_{ex['title']}")


# ══════════════════════════════════════════════════════════════
# 7. GROUP BY
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[7]:
    st.markdown('<div class="section-header">⑤ GROUP BY — 집계</div>', unsafe_allow_html=True)

    st.markdown("`GROUP BY` 는 특정 컬럼의 값을 기준으로 **행을 그룹화**하고, 각 그룹에 집계 함수를 적용합니다.")

    st.markdown("""
    <div class="syntax-box">
    SELECT   그룹컬럼, 집계함수(컬럼)<br>
    FROM     테이블<br>
    [WHERE   집계 전 조건]<br>
    GROUP BY 그룹컬럼<br>
    [HAVING  집계 후 조건]<br>
    [ORDER BY ...];
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**WHERE vs HAVING**")
        st.markdown("""
| | WHERE | HAVING |
|---|---|---|
| 적용 시점 | GROUP BY **이전** | GROUP BY **이후** |
| 대상 | 개별 행 | 그룹(집계 결과) |
| 집계함수 사용 | ❌ 불가 | ✅ 가능 |
        """)
    with col2:
        st.markdown("**집계 함수**")
        st.markdown("""
| 함수 | 설명 |
|------|------|
| `COUNT(*)` | 행 수 |
| `SUM(col)` | 합계 |
| `AVG(col)` | 평균 |
| `MAX(col)` | 최댓값 |
| `MIN(col)` | 최솟값 |
        """)

    st.divider()

    examples = [
        {
            "title": "예제 1 — 기준연도별 총 공급건수",
            "desc": "연도별로 전체 보증 공급건수를 합산합니다.",
            "sql": """SELECT
    base_year           AS 기준연도,
    COUNT(*)            AS 보증건수,
    SUM(supply_count)   AS 총공급건수,
    ROUND(SUM(guarantee_amount), 1) AS "총보증금액(억원)"
FROM   loan_guarantee
GROUP BY base_year
ORDER BY base_year;""",
        },
        {
            "title": "예제 2 — 상품유형별 평균·최대 공급건수",
            "sql": """SELECT
    product_type                   AS 상품유형,
    COUNT(*)                       AS 데이터건수,
    ROUND(AVG(supply_count), 0)    AS 평균공급건수,
    MAX(supply_count)              AS 최대공급건수,
    MIN(supply_count)              AS 최소공급건수
FROM   loan_guarantee
GROUP BY product_type
ORDER BY 평균공급건수 DESC;""",
        },
        {
            "title": "예제 3 — HAVING (평균 공급건수 5,000 이상 상품만)",
            "desc": "GROUP BY 후 평균 공급건수가 5,000건 이상인 상품유형만 필터링합니다.",
            "sql": """SELECT
    product_type,
    ROUND(AVG(supply_count), 0) AS 평균공급건수
FROM   loan_guarantee
GROUP BY product_type
HAVING AVG(supply_count) >= 5000
ORDER BY 평균공급건수 DESC;""",
        },
        {
            "title": "예제 4 — WHERE + GROUP BY + HAVING 조합",
            "desc": "2022년 이후 데이터 중, 지역별 연금지급액 합계가 2,000억 이상인 지역",
            "sql": """SELECT
    region_id,
    SUM(join_count)       AS 총가입건수,
    SUM(pension_payment)  AS "총연금지급액(억원)"
FROM   housing_pension
WHERE  base_year >= 2022
GROUP BY region_id
HAVING SUM(pension_payment) >= 2000
ORDER BY "총연금지급액(억원)" DESC;""",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"grp_{ex['title']}")

    st.markdown("""
    <div class="warn-box">
    ⚠️ <b>GROUP BY 규칙</b>: SELECT에 나오는 컬럼 중 집계함수로 감싸지 않은 컬럼은 반드시 GROUP BY에 포함해야 합니다.<br>
    예) <code>SELECT base_year, product_type, COUNT(*) FROM ... GROUP BY base_year, product_type</code>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 8. JOIN
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[8]:
    st.markdown('<div class="section-header">⑥ JOIN — 테이블 결합</div>', unsafe_allow_html=True)

    st.markdown("`JOIN` 은 **공통 컬럼(키)** 을 기준으로 두 개 이상의 테이블을 합쳐서 조회합니다.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="syntax-box">
        SELECT a.컬럼, b.컬럼<br>
        FROM   테이블A  a<br>
        [JOIN 종류] 테이블B  b<br>
        ON     a.키 = b.키;
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
| JOIN 종류 | 결과 |
|-----------|------|
| `INNER JOIN` | 양쪽 모두 매칭되는 행만 |
| `LEFT JOIN` | 왼쪽 전체 + 오른쪽 매칭 (없으면 NULL) |
| `RIGHT JOIN` | 오른쪽 전체 + 왼쪽 매칭 |
| `FULL OUTER JOIN` | 양쪽 전체 |
        """)

    st.divider()

    examples = [
        {
            "title": "예제 1 — INNER JOIN (보증 + 지역명)",
            "desc": "region_id 대신 실제 지역명(region_name)을 함께 조회합니다.",
            "sql": """SELECT
    lg.guarantee_no  AS 보증번호,
    lg.base_year     AS 기준연도,
    r.region_name    AS 지역명,
    lg.product_type  AS 상품유형,
    lg.supply_count  AS 공급건수
FROM loan_guarantee lg
INNER JOIN regions r ON lg.region_id = r.region_id
ORDER BY lg.base_year, r.region_name;""",
            "tip": "💡 테이블 별칭(lg, r)을 쓰면 쿼리가 짧아지고 가독성이 높아집니다.",
        },
        {
            "title": "예제 2 — LEFT JOIN (모든 지역 포함, 데이터 없으면 NULL)",
            "desc": "보증 데이터가 없는 지역도 포함해서 조회합니다.",
            "sql": """SELECT
    r.region_name    AS 지역명,
    r.region_type    AS 구분,
    lg.base_year     AS 기준연도,
    lg.supply_count  AS 공급건수
FROM regions r
LEFT JOIN loan_guarantee lg ON r.region_id = lg.region_id
ORDER BY r.region_name, lg.base_year;""",
        },
        {
            "title": "예제 3 — JOIN + WHERE + ORDER BY",
            "desc": "수도권 지역의 2023년 보증 현황을 지역별로 조회합니다.",
            "sql": """SELECT
    r.region_name    AS 지역명,
    lg.product_type  AS 상품유형,
    lg.supply_count  AS 공급건수,
    lg.guarantee_amount AS "보증금액(억원)"
FROM loan_guarantee lg
INNER JOIN regions r ON lg.region_id = r.region_id
WHERE  r.region_type = '수도권'
  AND  lg.base_year = 2023
ORDER BY lg.supply_count DESC;""",
        },
        {
            "title": "예제 4 — 3테이블 JOIN (보증 + 연금 + 지역 동시 조회)",
            "desc": "같은 연도·지역의 보증 공급건수와 연금 가입건수를 나란히 비교합니다.",
            "sql": """SELECT
    r.region_name       AS 지역명,
    lg.base_year        AS 기준연도,
    SUM(lg.supply_count) AS 보증공급건수,
    hp.join_count        AS 연금가입건수,
    hp.pension_payment   AS "연금지급액(억원)"
FROM loan_guarantee lg
JOIN regions        r  ON lg.region_id = r.region_id
JOIN housing_pension hp ON lg.region_id = hp.region_id
                        AND lg.base_year = hp.base_year
GROUP BY r.region_name, lg.base_year, hp.join_count, hp.pension_payment
ORDER BY lg.base_year, 보증공급건수 DESC;""",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            if ex.get("tip"):
                st.markdown(f'<div class="tip-box">{ex["tip"]}</div>', unsafe_allow_html=True)
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"join_{ex['title']}")


# ══════════════════════════════════════════════════════════════
# 9. 복합 쿼리 실전
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[9]:
    st.markdown('<div class="section-header">🚀 복합 쿼리 실전</div>', unsafe_allow_html=True)
    st.markdown("지금까지 배운 모든 키워드를 조합한 실전 분석 쿼리입니다.")

    examples = [
        {
            "title": "실전 1 — 연도·지역별 주택보증 현황 리포트",
            "desc": "기준연도·지역명·상품유형별 공급건수 합계와 보증금액을 한 번에",
            "sql": """SELECT
    lg.base_year                        AS 기준연도,
    r.region_name                       AS 지역명,
    r.region_type                       AS 수도권구분,
    lg.product_type                     AS 상품유형,
    SUM(lg.supply_count)                AS 총공급건수,
    ROUND(SUM(lg.guarantee_amount), 1)  AS "총보증금액(억원)"
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
GROUP BY lg.base_year, r.region_name, r.region_type, lg.product_type
ORDER BY lg.base_year DESC, 총공급건수 DESC;""",
        },
        {
            "title": "실전 2 — 연도별 연금 성장률 분석 (서브쿼리)",
            "desc": "전체 평균보다 연금지급액이 높은 연도·지역 조합만 필터링",
            "sql": """SELECT
    hp.base_year,
    r.region_name,
    hp.pension_payment AS "연금지급액(억원)"
FROM housing_pension hp
JOIN regions r ON hp.region_id = r.region_id
WHERE hp.pension_payment > (
    SELECT AVG(pension_payment) FROM housing_pension
)
ORDER BY hp.pension_payment DESC;""",
        },
        {
            "title": "실전 3 — 수도권 vs 지방 보증 공급 비교 (CASE WHEN)",
            "desc": "수도권·지방 구분별로 연도별 보증 공급건수 합계를 비교합니다.",
            "sql": """SELECT
    lg.base_year AS 기준연도,
    SUM(CASE WHEN r.region_type = '수도권' THEN lg.supply_count ELSE 0 END) AS 수도권공급건수,
    SUM(CASE WHEN r.region_type = '지방'   THEN lg.supply_count ELSE 0 END) AS 지방공급건수,
    SUM(lg.supply_count) AS 전국공급건수
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
GROUP BY lg.base_year
ORDER BY lg.base_year;""",
        },
        {
            "title": "실전 4 — 보증번호 패턴 + 조건 + 집계 조합",
            "desc": "2022~2023년 전세 관련 상품(LIKE 활용)의 지역별 공급 현황",
            "sql": """SELECT
    r.region_name  AS 지역명,
    lg.product_type AS 상품유형,
    SUM(lg.supply_count) AS 총공급건수
FROM loan_guarantee lg
JOIN regions r ON lg.region_id = r.region_id
WHERE lg.base_year BETWEEN 2022 AND 2023
  AND lg.product_type LIKE '%전세%'
GROUP BY r.region_name, lg.product_type
HAVING SUM(lg.supply_count) >= 5000
ORDER BY 총공급건수 DESC;""",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"], expanded=True):
            st.caption(ex.get("desc", ""))
            st.code(ex["sql"], language="sql")
            show_result(conn, ex["sql"], f"adv_{ex['title']}")


# ══════════════════════════════════════════════════════════════
# 10. 직접 실습
# ══════════════════════════════════════════════════════════════
elif section == SECTIONS[10]:
    st.markdown('<div class="section-header">✏️ 직접 실습</div>', unsafe_allow_html=True)
    st.caption("자유롭게 SQL을 작성하고 실행해보세요.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📋 테이블 컬럼 목록**")
        st.markdown("""
- `regions` : region_id, region_name, region_type
- `loan_guarantee` : guarantee_id, guarantee_no, base_year, region_id, product_type, supply_count, guarantee_amount
- `housing_pension` : pension_id, base_year, region_id, join_count, pension_payment, avg_house_price
        """)
    with col2:
        st.markdown("**⚡ 빠른 참조**")
        st.code("""-- 집계
SELECT col, COUNT(*), SUM(col), AVG(col)
FROM t GROUP BY col HAVING 조건;

-- 조건
WHERE col BETWEEN a AND b
WHERE col IN ('A','B')
WHERE col IS NULL
WHERE col LIKE 'G-2023%'

-- JOIN
FROM a JOIN b ON a.key = b.key""", language="sql")

    presets = [
        "직접 입력",
        "SELECT * FROM regions",
        "SELECT * FROM loan_guarantee LIMIT 10",
        "SELECT * FROM housing_pension ORDER BY pension_payment DESC",
        "SELECT base_year, SUM(supply_count) AS 총공급건수 FROM loan_guarantee GROUP BY base_year ORDER BY base_year",
        "SELECT lg.guarantee_no, r.region_name, lg.product_type, lg.supply_count FROM loan_guarantee lg JOIN regions r ON lg.region_id = r.region_id WHERE lg.base_year = 2023",
    ]

    preset = st.selectbox("예제 불러오기", presets)
    default = "" if preset == "직접 입력" else preset
    user_sql = st.text_area("SQL 입력", value=default, height=160, placeholder="SELECT ...")

    if st.button("▶ 실행", type="primary"):
        if user_sql.strip():
            df, err = run_sql(conn, user_sql)
            if err:
                st.error(f"오류: {err}")
            else:
                st.success(f"✅ {len(df)}행 반환")
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("SQL을 입력해주세요.")

    st.divider()
    st.markdown("### 🎯 연습 과제")
    st.markdown("""
    아래 과제를 직접 풀어보세요.

    1. `loan_guarantee` 에서 **2023년** 보증 데이터를 **보증금액 내림차순**으로 조회하세요.
    2. 보증번호가 `'G-2022'` 로 시작하는 건의 **공급건수 합계**를 구하세요.
    3. **기준연도별**로 주택연금 **총 가입건수**와 **총 연금지급액**을 조회하세요.
    4. `loan_guarantee` 와 `regions` 를 JOIN 하여 **수도권** 지역의 **2023년** 전세 공급건수를 조회하세요.
    5. 연도·지역별 **연금지급액 평균보다 높은** 데이터만 서브쿼리로 필터링하세요.
    """)

    st.divider()
    st.markdown("""
    <div class="tip-box">
    ✅ <b>실수 방지 체크리스트</b><br>
    • NULL 비교 → <code>IS NULL</code> 사용 (<code>= NULL</code> 은 항상 FALSE)<br>
    • 집계 조건 → <code>WHERE</code> 가 아닌 <code>HAVING</code><br>
    • GROUP BY → SELECT의 비집계 컬럼 모두 포함<br>
    • JOIN → <code>ON</code> 조건 누락 시 카테시안 곱 발생<br>
    • LIKE <code>'%값%'</code> → 대용량 테이블에서 Full Scan 주의
    </div>
    """, unsafe_allow_html=True)
