import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LottoCrawler:
    def __init__(self, csv_path="data/lotto_numbers.csv"):
        self.csv_path = csv_path
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }
        
    def get_latest_draw_no(self):
        """최신 회차 번호 가져오기"""
        try:
            url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
            res = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 최신 회차 번호가 들어있는 태그 선택
            latest_no_tag = soup.select_one(".nums > strong")
            if latest_no_tag:
                return int(latest_no_tag.text.strip())
            else:
                logger.warning("최신 회차를 가져올 수 없어 기본값 사용")
                return 1175  # 기본값
                
        except Exception as e:
            logger.error(f"최신 회차 조회 실패: {e}")
            return 1175  # 기본값

    def get_lotto_numbers(self, draw_no):
        """특정 회차의 로또 번호 가져오기"""
        try:
            url = f"https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={draw_no}"
            res = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 당첨 번호 6개
            win_nums = soup.select(".win_result .nums span.ball_645")
            # 보너스 번호
            bonus_num = soup.select_one(".win_result .bonus span.ball_645")
            
            if len(win_nums) < 6 or bonus_num is None:
                logger.warning(f"[{draw_no}회] 데이터 부족. 건너뜀.")
                return None
                
            win_nums = [int(num.text) for num in win_nums]
            bonus = int(bonus_num.text)
            
            return {
                "회차": draw_no,
                "번호1": win_nums[0],
                "번호2": win_nums[1], 
                "번호3": win_nums[2],
                "번호4": win_nums[3],
                "번호5": win_nums[4],
                "번호6": win_nums[5],
                "보너스": bonus
            }
            
        except Exception as e:
            logger.error(f"[{draw_no}회] 크롤링 오류: {e}")
            return "error"

    def crawl_all_data(self, start_no=1, end_no=None, progress_callback=None):
        """전체 데이터 크롤링"""
        if end_no is None:
            end_no = self.get_latest_draw_no()
            
        logger.info(f"크롤링 시작: {start_no}회 ~ {end_no}회")
        
        all_data = []
        fail_list = []
        total = end_no - start_no + 1
        
        for i in range(start_no, end_no + 1):
            result = self.get_lotto_numbers(i)
            
            if result == "error":
                fail_list.append(i)
            elif result:
                all_data.append(result)
                
            # 진행률 계산 및 콜백 호출
            progress = ((i - start_no + 1) / total) * 100
            if progress_callback:
                progress_callback(progress, i, total + start_no - 1)
                
            logger.info(f"진행률: {progress:.1f}% ({i} / {end_no})")
            time.sleep(0.3)  # 서버 부하 방지
        
        # 실패한 회차 재시도
        if fail_list:
            logger.info(f"실패한 {len(fail_list)}개 회차 재시도 중...")
            retry_list = []
            
            for i in fail_list:
                time.sleep(1)
                result = self.get_lotto_numbers(i)
                if result == "error":
                    retry_list.append(i)
                elif result:
                    all_data.append(result)
                    
            if retry_list:
                logger.warning(f"최종 실패한 회차: {retry_list}")
        
        return all_data, fail_list

    def update_data(self, progress_callback=None):
        """기존 데이터 업데이트"""
        try:
            # 기존 데이터 확인
            if os.path.exists(self.csv_path):
                df_existing = pd.read_csv(self.csv_path)
                start_no = df_existing["회차"].max() + 1
                logger.info(f"기존 데이터 발견. {start_no}회부터 업데이트 시작")
            else:
                df_existing = pd.DataFrame()
                start_no = 1
                logger.info("기존 데이터 없음. 전체 크롤링 시작")
            
            # 최신 회차 확인
            latest_no = self.get_latest_draw_no()
            
            if start_no > latest_no:
                logger.info("이미 최신 데이터입니다.")
                return {
                    "success": True,
                    "message": "이미 최신 데이터입니다.",
                    "total_draws": len(df_existing),
                    "latest_draw": latest_no
                }
            
            # 새 데이터 크롤링
            new_data, fail_list = self.crawl_all_data(
                start_no, latest_no, progress_callback
            )
            
            if not new_data and not df_existing.empty:
                return {
                    "success": True,
                    "message": "새로운 데이터가 없습니다.",
                    "total_draws": len(df_existing),
                    "latest_draw": latest_no
                }
            
            # 데이터 합치기
            if not df_existing.empty:
                df_new = pd.DataFrame(new_data)
                df_all = pd.concat([df_existing, df_new], ignore_index=True)
                df_all = df_all.drop_duplicates(subset="회차").sort_values("회차")
            else:
                df_all = pd.DataFrame(new_data)
                df_all = df_all.sort_values("회차")
            
            # CSV 저장
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            df_all.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"✅ 데이터 저장 완료: 총 {len(df_all)}회차")
            
            return {
                "success": True,
                "message": f"데이터 업데이트 완료! 새로 추가된 회차: {len(new_data)}개",
                "total_draws": len(df_all),
                "latest_draw": latest_no,
                "new_draws": len(new_data),
                "failed_draws": len(fail_list)
            }
            
        except Exception as e:
            logger.error(f"데이터 업데이트 실패: {e}")
            return {
                "success": False,
                "message": f"데이터 업데이트 실패: {str(e)}",
                "error": str(e)
            }

    def get_data_info(self):
        """현재 데이터 정보 반환"""
        try:
            if not os.path.exists(self.csv_path):
                return {
                    "exists": False,
                    "total_draws": 0,
                    "latest_draw": 0,
                    "file_size": 0
                }
            
            df = pd.read_csv(self.csv_path)
            file_size = os.path.getsize(self.csv_path)
            
            return {
                "exists": True,
                "total_draws": len(df),
                "latest_draw": df['회차'].max() if '회차' in df.columns else 0,
                "file_size": file_size,
                "last_modified": datetime.fromtimestamp(
                    os.path.getmtime(self.csv_path)
                ).isoformat()
            }
            
        except Exception as e:
            logger.error(f"데이터 정보 조회 실패: {e}")
            return {
                "exists": False,
                "error": str(e)
            }

# 테스트용 메인 함수
if __name__ == "__main__":
    crawler = LottoCrawler()
    
    def progress_callback(progress, current, total):
        print(f"\r진행률: {progress:.1f}% ({current}/{total})", end="", flush=True)
    
    result = crawler.update_data(progress_callback)
    print(f"\n결과: {result}")