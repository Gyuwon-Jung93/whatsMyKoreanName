#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국 여자아이 출생신고 이름 랭킹 분석 (2008-2025)
Excel 파일들을 통합하여 전체 기간 동안의 이름 랭킹을 생성합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import re
warnings.filterwarnings('ignore')

# 한글 폰트 설정 (matplotlib)
plt.rcParams['font.family'] = ['Malgun Gothic', 'AppleGothic', 'Noto Sans CJK KR']
plt.rcParams['axes.unicode_minus'] = False

class KoreanGirlsNamesAnalyzer:
    def __init__(self):
        # 데이터 파일들이 위치한 기본 디렉터리 (프로젝트 구조에 맞게 수정)
        # 예: /Users/jacob/Desktop/SelfStudy/KoreanName/backend/data/KoreaData/girls
        self.base_dir = Path(__file__).parent / "data" / "KoreaData" / "girls"

        # 실제 파일 이름 목록 (디렉터리 경로는 base_dir로 통일)
        self.file_list = [
            '상위 출생신고이름현황(2008~2009) 여.xls',
            '상위 출생신고이름현황(2010~2011) 여.xls',
            '상위 출생신고이름현황(2012~2013) 여.xls', 
            '상위 출생신고이름현황(2014~2015) 여.xls',
            '상위 출생신고이름현황(2016~2017) 여.xls',
            '상위 출생신고이름현황(2018~2019) 여.xls',
            '상위 출생신고이름현황(2020~2021) 여.xls',
            '상위 출생신고이름현황(2022~2023) 여.xls',
            '상위 출생신고이름현황(2024~2025) 여.xls'
        ]
        self.all_data = []
        
    def read_excel_file(self, file_path):
        """
        Excel 파일을 읽고 데이터를 정리합니다.
        """
        try:
            # Excel 파일 읽기
            df = pd.read_excel(file_path, engine='xlrd')
            
            # 첫 번째 행이 헤더가 아닐 수 있으므로 확인
            if df.iloc[0, 0] != '순위':
                # 헤더 행 찾기
                header_row = None
                for i in range(min(10, len(df))):
                    if '순위' in str(df.iloc[i, 0]):
                        header_row = i
                        break
                
                if header_row is not None:
                    df = pd.read_excel(file_path, header=header_row, engine='xlrd')
            
            # 컬럼명 정리
            df.columns = ['순위', '이름', '전체비율', '건수']
            
            # 데이터 정리
            df = self.clean_data(df)
            
            # 연도 정보 추가
            year_range = self.extract_year_from_filename(file_path)
            df['연도범위'] = year_range
            
            return df
            
        except Exception as e:
            print(f"파일 읽기 오류 {file_path}: {e}")
            return None
    
    def clean_data(self, df):
        """
        데이터를 정리합니다.
        """
        # 빈 행 제거
        df = df.dropna(subset=['이름'])
        
        # '기타', '합계' 등 불필요한 행 제거
        df = df[~df['이름'].str.contains('기타|합계|전체', na=False)]
        
        # 순위가 숫자가 아닌 행 제거
        df = df[pd.to_numeric(df['순위'], errors='coerce').notna()]
        
        # 건수 컬럼을 숫자로 변환
        df['건수'] = pd.to_numeric(df['건수'], errors='coerce')
        
        # 전체비율에서 괄호 제거하고 숫자로 변환
        if '전체비율' in df.columns:
            df['전체비율'] = df['전체비율'].str.extract(r'(\d+\.?\d*)').astype(float)
        
        return df
    
    def extract_year_from_filename(self, filename):
        """
        파일명에서 연도 범위를 추출합니다.
        """
        filename = str(filename)
        # (2020~2021) 혹은 (2020-2021) 형태 추출
        m = re.search(r"\((\d{4})[~\-](\d{4})\)", filename)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        # 백업: 20202021 연속 문자열 형태도 지원
        m2 = re.search(r"(\d{4})(\d{4})", filename)
        if m2:
            return f"{m2.group(1)}-{m2.group(2)}"
        return 'Unknown'
    
    def load_all_files(self):
        """
        모든 Excel 파일을 읽어서 통합합니다.
        """
        print("Excel 파일들을 읽는 중...")
        
        # base_dir 내부의 모든 .xls 및 .xlsx 파일 검색
        for file_path in sorted(self.base_dir.glob("*.xls*")):
            if file_path.exists():
                df = self.read_excel_file(file_path)
                if df is not None and not df.empty:
                    self.all_data.append(df)
                    print(f"✓ {file_path} 읽기 완료: {len(df)}개 이름")
                else:
                    print(f"✗ {file_path} 읽기 실패 또는 빈 데이터")
            else:
                print(f"✗ {file_path} 파일을 찾을 수 없습니다")
        
        if not self.all_data:
            raise ValueError("읽을 수 있는 파일이 없습니다. 파일 경로를 확인해주세요.")
        
        # 모든 데이터 통합
        self.combined_data = pd.concat(self.all_data, ignore_index=True)
        print(f"\n총 {len(self.combined_data)}개의 데이터를 통합했습니다.")
        
    def create_overall_ranking(self):
        """
        전체 기간 동안의 이름 랭킹을 생성합니다.
        """
        print("\n전체 기간 랭킹을 생성하는 중...")
        
        # 이름별 총 건수 계산
        name_totals = self.combined_data.groupby('이름')['건수'].sum().reset_index()
        name_totals = name_totals.sort_values('건수', ascending=False).reset_index(drop=True)
        name_totals['전체순위'] = range(1, len(name_totals) + 1)
        
        # 전체 비율 계산
        total_count = name_totals['건수'].sum()
        name_totals['전체비율'] = (name_totals['건수'] / total_count * 100).round(2)
        
        self.overall_ranking = name_totals
        return name_totals
    
    def create_period_analysis(self):
        """
        시기별 이름 트렌드를 분석합니다.
        """
        print("시기별 트렌드를 분석하는 중...")
        
        # 각 시기별 상위 이름들
        period_rankings = {}
        
        for period in self.combined_data['연도범위'].unique():
            period_data = self.combined_data[self.combined_data['연도범위'] == period]
            period_ranking = period_data.groupby('이름')['건수'].sum().reset_index()
            period_ranking = period_ranking.sort_values('건수', ascending=False)
            period_rankings[period] = period_ranking
        
        self.period_rankings = period_rankings
        return period_rankings
    
    def save_results(self, output_file='korean_girls_names_ranking_2008_2025.xlsx'):
        """
        결과를 Excel 파일로 저장합니다.
        """
        print(f"\n결과를 {output_file}에 저장하는 중...")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 전체 랭킹
            self.overall_ranking.to_excel(writer, sheet_name='전체랭킹(2008-2025)', index=False)
            
            # 시기별 랭킹
            for period, ranking in self.period_rankings.items():
                sheet_name = f'랭킹_{period}'
                ranking.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 원본 데이터
            self.combined_data.to_excel(writer, sheet_name='원본데이터', index=False)
        
        print(f"✓ 결과가 {output_file}에 저장되었습니다.")
    
    def create_visualizations(self):
        """
        데이터 시각화를 생성합니다.
        """
        print("\n시각화를 생성하는 중...")
        
        # 1. 전체 상위 20개 이름 바차트
        plt.figure(figsize=(12, 8))
        top_20 = self.overall_ranking.head(20)
        
        plt.barh(range(len(top_20)), top_20['건수'])
        plt.yticks(range(len(top_20)), top_20['이름'])
        plt.xlabel('총 건수')
        plt.title('한국 여자아이 이름 Top 20 (2008-2025)', fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # 값 표시
        for i, v in enumerate(top_20['건수']):
            plt.text(v + max(top_20['건수']) * 0.01, i, f'{v:,}', 
                    verticalalignment='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('korean_girls_names_top20_2008_2025.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. 시기별 상위 5개 이름 트렌드
        plt.figure(figsize=(14, 8))
        
        # 전체 기간 상위 10개 이름 선택
        top_names = self.overall_ranking.head(10)['이름'].tolist()
        
        trend_data = []
        periods = sorted(self.period_rankings.keys())
        
        for name in top_names:
            name_trend = []
            for period in periods:
                period_data = self.period_rankings[period]
                if name in period_data['이름'].values:
                    count = period_data[period_data['이름'] == name]['건수'].iloc[0]
                else:
                    count = 0
                name_trend.append(count)
            trend_data.append(name_trend)
        
        # 라인 플롯
        for i, name in enumerate(top_names):
            plt.plot(periods, trend_data[i], marker='o', label=name, linewidth=2)
        
        plt.xlabel('연도 범위')
        plt.ylabel('건수')
        plt.title('인기 여자아이 이름 트렌드 (2008-2025)', fontsize=16, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('korean_girls_names_trend_2008_2025.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_summary(self):
        """
        분석 결과 요약을 출력합니다.
        """
        print("\n" + "="*60)
        print("한국 여자아이 이름 랭킹 분석 결과 (2008-2025)")
        print("="*60)
        
        print(f"\n📊 전체 통계:")
        print(f"• 총 분석 기간: 2008-2025년")
        print(f"• 총 데이터 수: {len(self.combined_data):,}개")
        print(f"• 고유 이름 수: {len(self.overall_ranking):,}개")
        print(f"• 총 출생신고 건수: {self.overall_ranking['건수'].sum():,}건")
        
        print(f"\n🏆 상위 10개 이름:")
        for i, row in self.overall_ranking.head(10).iterrows():
            print(f"{row['전체순위']:2d}. {row['이름']:4s}: {row['건수']:6,}건 ({row['전체비율']:4.1f}%)")
        
        print(f"\n📈 시기별 1위 이름:")
        for period in sorted(self.period_rankings.keys()):
            top_name = self.period_rankings[period].iloc[0]
            print(f"• {period}: {top_name['이름']} ({top_name['건수']:,}건)")

def main():
    """
    메인 실행 함수
    """
    analyzer = KoreanGirlsNamesAnalyzer()
    
    try:
        # 1. 데이터 로드
        analyzer.load_all_files()
        
        # 2. 전체 랭킹 생성
        analyzer.create_overall_ranking()
        
        # 3. 시기별 분석
        analyzer.create_period_analysis()
        
        # 4. 결과 저장
        analyzer.save_results()
        
        # 5. 시각화 생성
        analyzer.create_visualizations()
        
        # 6. 결과 요약 출력
        analyzer.print_summary()
        
        print("\n✅ 분석이 완료되었습니다!")
        print("📁 생성된 파일:")
        print("  • korean_girls_names_ranking_2008_2025.xlsx")
        print("  • korean_girls_names_top20_2008_2025.png")
        print("  • korean_girls_names_trend_2008_2025.png")
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        print("파일 경로와 형식을 확인해주세요.")

if __name__ == "__main__":
    main()