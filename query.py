# query_3nf.py
from sqlalchemy import select
from db import (
    SessionLocal, Stock, Broker, Author, Report
)


# 공통 출력 포맷
def print_report(r: Report):
    stock = r.stock
    broker = r.broker
    author = r.author
    rating = r.rating

    print(f"[ID: {r.id}] {r.written_date} | {stock.stock_name} ({stock.stock_code})")
    print(f"- 제목: {r.title}")
    print(f"- 현재가: {r.current_price} | 목표가: {r.fair_price} | 기대수익률: {r.expected_return}")
    print(f"- 평가의견: {rating.code if rating else None}")
    print(f"- 애널리스트: {author.name if author else None} | 증권사: {broker.name if broker else None}")
    print(f"- 기업정보: {stock.company_info_url}")
    print(f"- 첨부파일: {r.attachment_url}")
    print("-" * 80)


# 1) 최신순 전체 리포트 출력
def show_all_reports():
    with SessionLocal() as session:
        results = (
            session.query(Report)
            .order_by(Report.written_date.desc(), Report.id.desc())
            .all()
        )

        print(f"\n=== 전체 리포트 ({len(results)}건) ===\n")
        for r in results:
            print_report(r)


# 2) 종목명 검색 (전부)
def search_by_stock_name(name: str):
    with SessionLocal() as session:
        results = (
            session.query(Report)
            .join(Report.stock)
            .filter(Stock.stock_name.like(f"%{name}%"))
            .order_by(Report.written_date.desc())
            .all()
        )

        print(f"\n=== 종목명 검색: '{name}' ({len(results)}건) ===\n")
        for r in results:
            print_report(r)


# 3) 증권사 검색 (전부)
def search_by_broker(name: str):
    with SessionLocal() as session:
        results = (
            session.query(Report)
            .join(Report.broker)
            .filter(Broker.name.like(f"%{name}%"))
            .order_by(Report.written_date.desc())
            .all()
        )

        print(f"\n=== 증권사 검색: '{name}' ({len(results)}건) ===\n")
        for r in results:
            print_report(r)


# 4) 애널리스트 검색 (전부)
def search_by_author(name: str):
    with SessionLocal() as session:
        results = (
            session.query(Report)
            .join(Report.author)
            .filter(Author.name.like(f"%{name}%"))
            .order_by(Report.written_date.desc())
            .all()
        )

        print(f"\n=== 애널리스트 검색: '{name}' ({len(results)}건) ===\n")
        for r in results:
            print_report(r)


# 5) 평가의견 검색 (전부)
def search_by_rating(code: str):
    with SessionLocal() as session:
        results = (
            session.query(Report)
            .filter(Report.rating_code == code)
            .order_by(Report.written_date.desc())
            .all()
        )

        print(f"\n=== 평가의견 검색: '{code}' ({len(results)}건) ===\n")
        for r in results:
            print_report(r)


if __name__ == "__main__":
    show_all_reports()

    search_by_stock_name("삼양식품")
    search_by_broker("메리츠")
    search_by_author("전유진")
    search_by_rating("Buy")
