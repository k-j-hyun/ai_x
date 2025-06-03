-- [ IV ] DDL, DCL, DML
/* SQL
 - DCL
    사용자 계정 생성 CREATE USER, 권한부여 GRANT, 
    권한박탈 REVOKE,사용자계정삭제 DROP USER 트렌젝션 명령어
 - DDL
    테이블생성 CREATE TABLE, 테이블구조변경 ALTER TABLE,
    테이블삭제 DROP TABLE
 - DML
    INSERT, SELECT, UPDATE, DELETE - DML은 취소 가능
*/
--------------------------
-------- ★ DDL ★ --------
--------------------------
-- 1. 테이블 생성(CREATE TABLE 테이블명) : 테이블 구조를 정의
CREATE TABLE BOOK(
    BOOKID    NUMBER(4),      -- BOOKID 필드의 타입은 숫자 4자리
    BOOKNAME  VARCHAR2(20),   -- BOOKNAME필드의 타입은 문자 20BYTE
    PUBLISHER VARCHAR2(20),
    RDATE     DATE,           -- RDATE 필드의 타입은 DATE형
    PRICE     NUMBER(8,2),    -- PRICE 필드의 타입은 숫자천체 8자리중 소숫점 2자리
    PRIMARY KEY(BOOKID)       -- 제약조건 선언 : BOOKID를 PRIMARY KEY 필드로(NOT NULL, UNIQUE)
    );
SELECT * FROM BOOK;
DESC BOOK;

-- 2. 테이블 삭제(DROP TABLE 테이블명) : 테이블 삭제
DROP TABLE BOOK;

CREATE TABLE BOOK(
    BID NUMBER(4) PRIMARY KEY,
    BNAME VARCHAR2(20),
    PUBLISHER VARCHAR2(20),
    RDATE DATE,
    PRICE NUMBER(8)
    );

    -- EX1. DEPT01 (DEPTNO(숫자2;PK), DNAME(문자14), LOC(문자13)
    CREATE TABLE DEPT01(
        DEPTNO NUMBER(2),
        DNAME VARCHAR2(14),
        LOC VARCHAR2(13),
        PRIMARY KEY(DEPTNO)
        );
    SELECT * FROM DEPT01;
    SELECT * FROM DEPT; -- 10, 20, 30, 40
    SELECT DISTINCT DEPTNO FROM EMP; -- 10, 20, 30

-- 3. INSERT INTO 테이블명 (COLUMNS) VALUES (EMPTY, '홍')
INSERT INTO EMP (EMPNO, ENAME, DEPTNO) VALUES (9999, 'HONG', 40);
SELECT * FROM EMP;

-- 4. ROLLBACK; : DML 취소 / 트랜젝션 명령어
ROLLBACK;
SELECT * FROM EMP;
SELECT * FROM DEPT01;

-- 5. EMP테이블과 유사한 EMP01 테이블 생성 : 
--              EMPNO(숫자4;PK),ENAME(문자10자리),SAL(숫자7,2),DEPTNO(숫자2-FK)
-- REFERENCES : FK(퍼링키) 제약조건
CREATE TABLE EMP01(
    EMPNO NUMBER(4) PRIMARY KEY,
    ENAME VARCHAR2(10),
    SAL NUMBER(7,2),
    DEPTNO NUMBER(2) REFERENCES DEPT01(DEPTNO)
    );

DROP TABLE EMP01; -- 테이블 삭제
CREATE TABLE EMP01(
    EMPNO NUMBER(4),
    ENAME VARCHAR2(10),
    SAL NUMBER(7,2),
    DEPTNO NUMBER(2),
    PRIMARY KEY(EMPNO),
    FOREIGN KEY(DEPTNO) REFERENCES DEPT01(DEPTNO)
    );
    
--------------------------
-------- ★ DML ★ --------
--------------------------
-- 1. INSERT INTO 테이블명 (필드명1, 필드명2,...) VALUES (값1, 값2,...);
--    INSERT INTO 테이블명 VALUES (값1,값2,값3,...값N);
DROP TABLE DEPT01;
SELECT * FROM DEPT01;
INSERT INTO DEPT01 VALUES (50, 'ACCOUNTING', 'SEOUL');
INSERT INTO DEPT01 (DEPTNO, DNAME, LOC) VALUES (51, '전산', '신림');
INSERT INTO DEPT01 (DNAME, LOC, DEPTNO) VALUES ('영업', '봉천', 52);
SELECT * FROM DEPT01;
-- 명시적으로 NULL 입력
INSERT INTO DEPT01 (DEPTNO, DNAME, LOC) VALUES (53, '연구', NULL);
-- LOC : 묵시적으로 NULL 입력
INSERT INTO DEPT01 (DEPTNO, DNAME) VALUES (60, '설계');

-- COMMIT; : 트렌젝션 영역에 쌓여 있는 DML 명령어 일괄 실행
COMMIT;

-- 서브쿼리(SUB QUERY)를 이용한 INSERT
    -- EX1. DEPT 테이블에서 10~30 부서의 내용을 DEPT01 테이블에 INSERT
    INSERT INTO DEPT01 SELECT * FROM DEPT WHERE DEPTNO < 40;