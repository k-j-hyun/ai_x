-- [III] join : 2개 이상의 테이블을 연결하여 데이터를 검색하는 방법
SELECT * FROM EMP WHERE ENAME = 'SCOTT'; -- 1행(직원정보)
SELECT * FROM DEPT;                      -- 4행(부서정보)
-- CROSS JOIN
SELECT * 
    FROM EMP, DEPT
    WHERE ENAME = 'SCOTT'; -- 1(EMP갯수) * 4(DEPT갯수) => 4행
-- ★ 1. EQUI JOIN(공통필드 값이 일치되는 조건만 JOIN)
    SELECT EMPNO NO, ENAME, JOB, MGR, HIREDATE, SAL COMM, DEPT.DEPTNO, DNAME, LOC
        FROM EMP, DEPT
        WHERE ENAME = 'SCOTT' AND EMP.DEPTNO = DEPT.DEPTNO;
    SELECT EMPNO NO, ENAME, JOB, MGR, HIREDATE, SAL COMM, D.DEPTNO, DNAME, LOC -- (3)순서
        FROM EMP E, DEPT D                             -- (1)순서
        WHERE ENAME = 'SCOTT' AND E.DEPTNO = D.DEPTNO  -- (2)순서 테이블 별칭만 사용 가능
        ORDER BY NO;                                   -- (4)순서
    -- EX1. 모든 사원의 사번, 이름, JOB, 상사사번, 부서번호, 부서명, 근무지
    SELECT EMPNO, ENAME, JOB, MGR, D.DEPTNO, DNAME, LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO;
    -- EX2. 급여(SAL)가 2000이상인 직원의 이름, JOB, 급여, 부서명, 근무지
    SELECT ENAME, JOB, SAL, DNAME, LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND SAL >= 2000;
    -- EX3. 근무지(LOC)가 'CHICAGO'인 직원의 이름,JOB,급여,부서번호 출력
    SELECT ENAME, JOB, SAL, D.DEPTNO
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND D.LOC = 'CHICAGO';
    -- EX4. 82년도에 입사한 10,20번 부서 직원의 이름, 급여, 근무지(급여순) 출력
    SELECT ENAME, SAL, D.LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND 
        TO_CHAR(HIREDATE, 'RR') = 82 AND D.DEPTNO IN (10,20)
        ORDER BY SAL; 
    -- EX5. JOB이 'SALESMAN'이거나 'MANAGER'인 사원의 
    -- 이름,급여,상여,연봉(SAL+COMM)*12,부서명,근무지(연봉이 큰 순) 출력
    SELECT ENAME, SAL, COMM, (SAL+NVL(COMM, 0))*12 연봉, DNAME, LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        JOB IN ('SALESMAN', 'MANAGER')
        ORDER BY 연봉 DESC;
    -- EX6. COMM이 NULL이고, SAL이 2000대인 사원의 
    -- 이름,급여,입사일,부서번호,부서명 (부서명순, 급여순) 출력
    SELECT ENAME, SAL, HIREDATE, D.DEPTNO, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        COMM IS NULL AND SAL BETWEEN 2000 AND 2999
        ORDER BY D.DEPTNO, SAL;
        
-- ★ 2. NON-EQUI JOIN
    SELECT * FROM EMP WHERE ENAME='SCOTT'; -- 직원정보
    SELECT GRADE, LOSAL, HISAL FROM SALGRADE; -- 급여등급 정보
    SELECT * FROM EMP, SALGRADE WHERE ENAME='SCOTT' AND
    SAL BETWEEN LOSAL AND HISAL;;
    -- EX1. 모든 사원의 사번, 이름, JOB, 상사사번, 급여, 급여등급(1등급,2등급,..)
    SELECT EMPNO, ENAME, JOB, MGR, SAL, GRADE||'등급' GRADE
        FROM EMP, SALGRADE
        WHERE SAL BETWEEN LOSAL AND HISAL;
    -- EX2. 모든 사원의 사번,이름,JOB,상사사번,급여,급여등급,부서명
    SELECT EMPNO, ENAME, JOB, MGR, SAL, GRADE||'등급' GRADE, DNAME
        FROM EMP E, SALGRADE, DEPT D
        WHERE SAL BETWEEN LOSAL AND HISAL
        AND E.DEPTNO = D.DEPTNO;    

-----------------------
-- ★ 3. SELF JOIN ★ --
-----------------------
SELECT * FROM EMP WHERE ENAME = 'SMITH';
SELECT EMPNO, ENAME FROM EMP WHERE EMPNO = 7902;
SELECT WORKER.EMPNO, WORKER.ENAME, WORKER.MGR, MANAGER.EMPNO, MANAGER.ENAME
    FROM EMP WORKER, EMP MANAGER
    WHERE WORKER.ENAME = 'SMITH' AND
    WORKER.MGR = MANAGER.EMPNO;
    -- EX1. 모든 사원의 사번, 이름, 상사의 사번, 상사이름
    SELECT W.EMPNO, W.ENAME, W.MGR, M.ENAME
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO;
    -- EX2. 'SMITH의 상사는 JONES이다' 포멧으로 출력
    SELECT W.ENAME || '의 상사는 ' || M.ENAME || '이다' MESSAGE
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO;
        
------------------------
-- ★ 4. OUTER JOIN ★ -- 
------------------------
-- SELF JOIN, EQUI JOIN시 조건이 만족하지 않는 행까지 나타나게 하는 JOIN
-- 배제된 행을 결과에 포함시킬 경우 (+)기호를 정보가 부족한 컬럼이름 뒤에 덧붙힘
-- (1) SELF JOIN에서의 OUTER JOIN 
    SELECT W.EMPNO, W.ENAME, W.MGR, M.EMPNO, M.ENAME
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO(+);
        -- EX1. 모든 사원에 대해 'SMITH의 상사는 FORD다'...'KING의 상사는 NVL(NULL, 없)다'
        SELECT W.ENAME || '의 상사는 ' || NVL(M.ENAME, '없') || '다' MESSAGE
            FROM EMP W, EMP M
            WHERE W.MGR = M.EMPNO(+);
        -- 부족하지 않은 쪽에 (+)를 붙힐 경우
        -- 말단 직원
        SELECT W.ENAME, M.ENAME
            FROM EMP W, EMP M
            WHERE W.MGR(+) = M.EMPNO AND W.ENAME IS NULL;
            
-- (2) EQUI JOIN에서의 OUTER JOIN
    SELECT * FROM DEPT; -- DEPTNO : 10, 20, 30, 40
    SELECT * FROM EMP;  -- DEPTNO : 10, 20, 30
    SELECT ENAME, E.DEPTNO, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO(+) = D.DEPTNO;


    
-- 연습문제 (EQUI JOIN)
-- 탄탄1 뉴욕에서 근무하는 사원의 이름과 급여를 출력하시오
    SELECT ENAME, SAL
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        LOC = 'NEW YORK';
-- 탄탄2	ACCOUNTING 부서 소속 사원의 이름과 입사일을 출력하시오
    SELECT ENAME, HIREDATE
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        DNAME = 'ACCOUNTING';
-- 탄탄3 직급이 MANAGER인 사원의 이름, 부서명을 출력하시오
    SELECT ENAME, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        JOB = 'MANAGER';
-- 탄탄4	Comm이 null이 아닌 사원의 이름, 급여, 부서코드, 근무지를 출력하시오.
    SELECT ENAME, SAL, D.DEPTNO, LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        COMM IS NOT NULL;

-- 연습문제(NON-EQUI JOIN)
-- 탄탄5 Comm이 null이 아닌 사원의 이름, 급여, 등급, 부서번호, 부서이름, 근무지를 
-- 출력하시오.
    SELECT ENAME, SAL, GRADE||'등급' GRADE, D.DEPTNO, DNAME, LOC
        FROM EMP E, DEPT D, SALGRADE S
        WHERE E.DEPTNO = D.DEPTNO AND
        SAL BETWEEN LOSAL AND HISAL AND
        COMM IS NOT NULL;
-- 탄탄6 이름, 급여, 입사일, 급여등급
    SELECT ENAME, SAL, HIREDATE, GRADE||'등급' GRADE
        FROM EMP E, SALGRADE S
        WHERE SAL BETWEEN LOSAL AND HISAL;
-- 탄탄7 이름, 급여, 급여등급, 연봉, 부서명을 부서명순으로 정렬하여 출력. 
-- 부서가 같으면 연봉순. 연봉=(sal+comm)*12 comm이 null이면 0
    SELECT ENAME, SAL, S.GRADE||'등급' GRADE, (SAL+NVL(COMM, 0))*12 연봉, D.DNAME
        FROM EMP E, DEPT D, SALGRADE S
        WHERE E.DEPTNO = D.DEPTNO AND SAL BETWEEN LOSAL AND HISAL
        ORDER BY D.DNAME, (SAL+NVL(COMM, 0))*12;
        
-- 탄탄8 이름, 업무, 급여, 등급, 부서코드, 부서명 출력. 
-- 급여가 1000~3000사이. 정렬조건 : 부서별, 부서같으면 업무별, 
-- 업무같으면 급여 큰순
    SELECT ENAME, JOB, SAL, S.GRADE||'등급' GRADE, D.DEPTNO, D.DNAME
        FROM EMP E, DEPT D, SALGRADE S
        WHERE E.DEPTNO = D.DEPTNO AND
        SAL BETWEEN LOSAL AND HISAL AND
        SAL BETWEEN 1000 AND 3000
        ORDER BY D.DNAME, JOB, SAL DESC;
        
-- 탄탄9 이름, 급여, 등급, 입사일, 근무지. 81년에 입사한 사람. 등급 큰순
    SELECT ENAME, SAL, S.GRADE||'등급' GRADE, HIREDATE, LOC
        FROM EMP E, DEPT D, SALGRADE S
        WHERE E.DEPTNO = D.DEPTNO AND
        SAL BETWEEN LOSAL AND HISAL AND
        TO_CHAR(HIREDATE, 'RR')=81
        ORDER BY S.GRADE DESC;
        
        
        
-- 탄탄10 매니저가 KING인 사원들의 이름과 직급을 출력하시오.
    SELECT WORKER.ENAME, WORKER.JOB
        FROM EMP WORKER, EMP MANAGER
        WHERE WORKER.MGR=MANAGER.EMPNO AND MANAGER.ENAME='KING';
    SELECT EMPNO FROM EMP WHERE ENAME = 'KING';
    -- 서브 쿼리 이용 --
    SELECT ENAME, JOB
        FROM EMP
        WHERE MGR = (SELECT EMPNO FROM EMP WHERE ENAME = 'KING');
-- 탄탄11 SCOTT과 동일한 부서번호에서 근무하는 사원의 이름을 출력하시오
    SELECT ENAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        D.DEPTNO = 20
        AND ENAME ^= 'SCOTT';
    -- SELF JOIN 이용 --
    SELECT E2.ENAME
        FROM EMP E1, EMP E2
        WHERE E1.ENAME = 'SCOTT' 
            AND E1.DEPTNO = E2.DEPTNO
            AND E2.ENAME <> 'SCOTT';
    -- SUBQUERY 이용 --
    SELECT ENAME FROM EMP
        WHERE DEPTNO = (SELECT DEPTNO FROM EMP WHERE ENAME='SCOTT')
        AND ENAME ^= 'SCOTT';
-- 탄탄12 SCOTT과 동일한 근무지에서 근무하는 사원의 이름을 출력하시오
-- (2단계 최종문제) – 6장 수업후 subquery 사용 추천



-- ★ <셤 연습문제>
-- Part1
--1. 모든 사원에 대한 이름, 부서번호, 부서명을 출력하는 SELECT 문장을 작성하여라.
    SELECT ENAME, D.DEPTNO, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO;
    
--2. NEW YORK에서 근무하고 있는 사원에 대하여 이름, 업무, 급여, 부서명을 출력
    SELECT ENAME, JOB, SAL, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        LOC = 'NEW YORK';
--3. 보너스를 받는 사원에 대하여 이름,부서명,위치를 출력
    SELECT ENAME, DNAME, LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        COMM IS NOT NULL;
--4. 이름 중 L자가 있는 사원에 대하여 이름,업무,부서명,위치를 출력
    SELECT ENAME, JOB, DNAME, LOC
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        ENAME LIKE '%L%';
--5. 사번, 사원명, 부서코드, 부서명을 검색하라(단, 사원명기준으로 오름차순 정렬)
    SELECT EMPNO, ENAME, D.DEPTNO, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO
        ORDER BY ENAME DESC;
--6. 사번, 사원명, 급여, 부서명을 검색하라. 
--단 급여가 2000이상인 사원에 대하여 급여를 기준으로 내림차순으로 정렬하시오
    SELECT EMPNO, ENAME, SAL, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
        SAL >= 2000
        ORDER BY SAL;
--7. 사번, 사원명, 업무, 급여, 부서명을 검색하시오. 
-- 단 업무가 MANAGER이며 급여가 2500이상인
-- 사원에 대하여 사번을 기준으로 오름차순으로 정렬하시오.
    SELECT EMPNO, ENAME, JOB, SAL, DNAME
        FROM EMP E, DEPT D
        WHERE E.DEPTNO = D.DEPTNO AND
            JOB = 'MANAGER' AND
            SAL >= 2500
        ORDER BY EMPNO DESC;
--8. 사번, 사원명, 업무, 급여, 등급을 검색하시오(단, 급여기준 내림차순으로 정렬)
    SELECT EMPNO, ENAME, JOB, SAL, GRADE
        FROM EMP E, DEPT D, SALGRADE
        WHERE E.DEPTNO = D.DEPTNO AND
            SAL BETWEEN LOSAL AND HISAL
        ORDER BY GRADE;
        
        
        
-- Part2
--1. 이름, 직속상사명
    SELECT W.ENAME 이름, M.ENAME 직속상사
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO;
--2. 이름, 급여, 업무, 직속상사명
    SELECT 
            W.ENAME AS "이름", 
            W.SAL AS "급여", 
            W.JOB AS "직무", 
            M.ENAME AS "직속상사"
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO;
--3. 이름, 급여, 업무, 직속상사명 . (상사가 없는 직원까지 전체 직원 다 출력.
    --상사가 없을 시 '없음'으로 출력)
    SELECT 
            W.ENAME AS "이름", 
            W.SAL AS "급여", 
            W.JOB AS "직업", 
            NVL(M.ENAME, '없음') AS "직속상사"
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO(+);
--4. 이름, 급여, 부서명, 직속상사명
    SELECT W.ENAME AS "이름", 
            W.SAL AS "급여", 
            DNAME AS "부서명", 
            M.ENAME AS "직속상사"
        FROM EMP W, EMP M, DEPT D
        WHERE W.MGR = M.EMPNO(+);
--5. 상사가 없는 직원과 상사가 있는 직원 모두에 대해 
-- 이름, 급여, 부서코드, 부서명, 근무지, 직속상사명을 출력하시오
-- (단, 직속상사가 없을 경우 직속상사명에는 ‘없음’으로 대신 출력하시오)
    SELECT W.ENAME AS "이름", 
            W.SAL AS "급여",
            D.DEPTNO AS "부서코드",
            DNAME AS "부서명",
            D.LOC AS "근무지",
            NVL(M.ENAME, '없음') AS "직속상사"
        FROM EMP W, EMP M, DEPT D
        WHERE W.MGR = M.EMPNO(+);
--6. 이름, 급여, 등급, 부서명, 직속상사명. 급여가 2000이상인 사람
    SELECT W.ENAME AS "이름", 
            W.SAL AS "급여",
            S.GRADE AS "등급",
            D.DNAME AS "부서명",
            NVL(M.ENAME, '없음') AS "직속상사"
        FROM EMP W, EMP M, DEPT D, SALGRADE S
        WHERE W.MGR = M.EMPNO(+) AND
            W.SAL BETWEEN S.LOSAL AND S.HISAL AND
            W.SAL >= 2000;
--7. 이름, 급여, 등급, 부서명, 직속상사명, (직속상사가 없는 직원까지 전체직원 부서명 순 정렬)
    SELECT W.ENAME AS "이름", 
            W.SAL AS "급여",
            S.GRADE AS "등급",
            D.DNAME AS "부서명",
            NVL(M.ENAME, '없음') AS "직속상사"
        FROM EMP W, EMP M, DEPT D, SALGRADE S
        WHERE W.MGR = M.EMPNO(+) AND
            W.SAL BETWEEN S.LOSAL AND S.HISAL
        ORDER BY D.DNAME;
--8. 이름, 급여, 등급, 부서명, 연봉, 직속상사명. 연봉=(급여+comm)*12으로 계산
    SELECT W.ENAME AS "이름", 
            W.SAL AS "급여",
            S.GRADE AS "등급",
            D.DNAME AS "부서명",
            NVL(M.ENAME, '없음') AS "직속상사",
            (W.SAL+NVL(W.COMM, 0))*12 AS "연봉"
        FROM EMP W, EMP M, DEPT D, SALGRADE S
        WHERE W.MGR = M.EMPNO(+) AND
            W.SAL BETWEEN S.LOSAL AND S.HISAL;
--9. 8번을 부서명 순 부서가 같으면 급여가 큰 순 정렬
    SELECT W.ENAME AS "이름", 
            W.SAL AS "급여",
            S.GRADE AS "등급",
            D.DNAME AS "부서명",
            NVL(M.ENAME, '없음') AS "직속상사",
            (W.SAL+NVL(W.COMM, 0))*12 AS "연봉"
        FROM EMP W, EMP M, DEPT D, SALGRADE S
        WHERE W.MGR = M.EMPNO(+) AND
            W.SAL BETWEEN S.LOSAL AND S.HISAL
        ORDER BY D.DNAME, W.SAL DESC;
--10. 사원테이블에서 사원명, 사원의 상사를 검색하시오(상사가 없는 직원까지 전체).
    SELECT W.ENAME 사원명, NVL(M.ENAME, '없음') 직속상사
        FROM EMP W, EMP M
        WHERE W.MGR = M.EMPNO;
        
SELECT * FROM EMP;
--11. 사원명, 상사명, 상사의 상사명을 검색하시오(self join)
    SELECT 
            E.ENAME AS "사원명",
            NVL(M.ENAME, '상사 없음') AS "상사명",
            NVL(MM.ENAME, '상사의 상사 없음') AS "상사의 상사명"
        FROM 
            EMP E,      -- 사원
            EMP M,      -- E의 상사
            EMP MM      -- M의 상사
        WHERE 
            E.MGR = M.EMPNO     -- 사원의 상사
            AND M.MGR = MM.EMPNO; -- 상사의 상사
--12. 위의 결과에서 상위 상사가 없는 모든 직원의 이름도 출력되도록 수정하시오(outer join)
    SELECT 
            E.ENAME AS "사원명",
            NVL(M.ENAME, '상사 없음') AS "상사명",
            NVL(MM.ENAME, '상사의 상사 없음') AS "상사의 상사명"
        FROM 
            EMP E,   -- 사원
            EMP M,   -- 사원의 상사
            EMP MM   -- 상사의 상사
        WHERE 
            E.MGR = M.EMPNO(+)      -- E → M 외부조인 (상사가 없어도 출력)
            AND M.MGR = MM.EMPNO(+); -- M → MM 외부조인 (상사의 상사가 없어도 출력)

        