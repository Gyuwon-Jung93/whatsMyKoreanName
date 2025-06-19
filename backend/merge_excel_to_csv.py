"""
Korea/UK boys·girls 연도별 Excel → 통합 CSV 생성
output : data/names_dataset.csv (english_name,korean_name,gender,region,year)
"""
import os, glob, re, pandas as pd
OUT = "data/names_dataset.csv"
# 데이터가 위치한 디렉터리 (backend/data/...)
BASES = ["data/KoreaData", "data/UKData"]
pattern = re.compile(r"(Korea|UK).*?/(boys|girls)/.*?(\\d{4})")

rows = []
for base in BASES:
    for path in glob.glob(os.path.join(base, "**/*.xls*"), recursive=True):
        m = pattern.search(path.replace("\\", "/"))
        if not m:
            continue
        region, gender, year = m.groups()
        df = pd.read_excel(path, engine="openpyxl" if path.endswith("x") else None)
        if df.shape[1] < 2:       # 최소 두 컬럼
            continue
        en_col, ko_col = df.columns[:2]
        for en, ko in zip(df[en_col], df[ko_col]):
            if pd.isna(en) or pd.isna(ko):
                continue
            rows.append({
                "english_name": str(en).strip(),
                "korean_name" : str(ko).strip(),
                "gender"      : gender,
                "region"      : region,
                "year"        : int(year),
            })

pd.DataFrame(rows).to_csv(OUT, index=False)
print(f"[DONE] {len(rows):,} rows saved → {OUT}")