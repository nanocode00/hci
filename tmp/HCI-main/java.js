document.addEventListener('DOMContentLoaded', () => {
  initSearchCategoryDropdown();

  initNewsList();

  initResearchList();
});


// 검색창 드롭다운
function initSearchCategoryDropdown() {

  // 검색 카테고리 요소 찾기
  const category = document.querySelector('.search-category');
  if (!category) return;  // 이 페이지에 없으면 그냥 종료

  const toggleBtn = category.querySelector('.search-category-toggle');
  const menu = category.querySelector('.search-category-menu');

  // 버튼 클릭 -> 메뉴 열기/닫기
  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();   // 이벤트 버블링 방지 (바깥 클릭 처리와 충돌 방지)
    category.classList.toggle('open');
  });

  // 메뉴 항목 클릭 -> 선택 적용
  menu.addEventListener('click', (e) => {
    if (e.target.tagName.toLowerCase() !== 'li') return;

    const selected = e.target.dataset.value;
    toggleBtn.textContent = selected;   // 버튼 글자 변경
    category.classList.remove('open');  // 메뉴 닫기

    console.log("선택한 검색 카테고리:", selected);
  });

  // 바깥 영역 클릭하면 닫기
  document.addEventListener('click', (event) => {
    if (!category.contains(event.target)) {
      category.classList.remove('open');
    }
  });
}


//news.html과 연결되는 js 뉴스 리스트 자동 추가

function initNewsList() {
  const listEl = document.getElementById('news-list');
  if (!listEl) return;  // 이 페이지가 아니면 그냥 패스

  fetch('news_sample.csv')
    .then(res => res.text())
    .then(text => {
      const rows = parseCSV(text);

      // 카드들 생성
      rows.forEach(row => {

        console.log('row.url =',row.url);

        const card = document.createElement('div');
        card.className = 'card';
        card.style.marginBottom = '12px';

        card.innerHTML = `
          <div style="font-size:15px; font-weight:600; margin-bottom:4px;">
            <a href="${row.url}" target="_blank">
              ${row.title}
            </a>
          </div>
          <div style="font-size:12px; color:#6b7280; margin-bottom:6px;">
            ${row.press} | ${row.date}
          </div>
        `;

        listEl.appendChild(card);
      });
    })
    .catch(err => {
      console.error('뉴스 CSV 로드 에러:', err);
    });
  }

  //CSV를 json 형식으로 파싱
  function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(',');

  const rows = lines.slice(1).map(line => {
    const cols = line.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h] = cols[i];
    });
    return obj;
  });

  return rows;
}

//research1.html과 연결되는 js 리서치 리스트 자동 추가
function initResearchList() {
  const listEl = document.getElementById('research-list');
  if (!listEl) return;  // 이 페이지가 아니면 그냥 패스

  fetch('research_sample.csv')
    .then(res => res.text())
    .then(text => {
      const rows = parseCSV(text);

      // 카드들 생성
      rows.forEach(row => {

        console.log('row.url =',row.url);

        const card = document.createElement('div');
        card.className = 'card';
        card.style.marginBottom = '12px';

        card.innerHTML = `
          <div style="font-size:13px; margin-bottom:4px;">
            ${row.stock}
          </div> 
          <div style="font-size:15px; font-weight:600; margin-bottom:4px;">
            <a href="${row.url}" target="_blank">
              ${row.title}
            </a>
          </div>
          <div style="font-size:12px; color:#6b7280; margin-bottom:6px;">
            ${row.broker} | ${row.date} | ${row.rating}
          </div>
        `;

        listEl.appendChild(card);
      });
    })
    .catch(err => {
      console.error('뉴스 CSV 로드 에러:', err);
    });
  }