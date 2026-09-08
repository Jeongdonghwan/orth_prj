(() => {
  const body = document.body;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- 헤더: 스크롤 시 축소/그림자 ----
  const onScroll = () => body.classList.toggle('scrolled', scrollY > 60);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // ---- 모바일 햄버거 ----
  const ham = document.querySelector('.ham'), mnav = document.querySelector('.mnav');
  if (ham && mnav) {
    ham.addEventListener('click', () => {
      const on = mnav.classList.toggle('on');
      ham.setAttribute('aria-expanded', on ? 'true' : 'false');
    });
  }

  // ---- 스크롤 리빌 ----
  const stagger = ['.clinics > a', '.steps .grid > .step', '.surg .grid > .ph', '.thumbs > .ph', '.kw > li', '.park .grid > .card2', '.panel .steps-in > .step'];
  stagger.forEach(sel => document.querySelectorAll(sel).forEach((el, i) => { el.classList.add('rv'); el.style.setProperty('--i', i); }));
  document.querySelectorAll('main section > .wrap > *:not(.tabs):not(.slider), main .loc .split > *, main .doctor .wrap > *').forEach(el => {
    if (!el.classList.contains('rv') && !el.querySelector('.rv')) el.classList.add('rv');
  });
  // 스태거 자식을 가진 컨테이너는 자신은 리빌하지 않음(자식이 함)
  if ('IntersectionObserver' in window && !reduced) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.rv').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.rv').forEach(el => el.classList.add('in'));
  }

  // ---- 히어로 슬라이더 (크로스페이드 + 켄번즈) ----
  const slides = document.querySelectorAll('.hero .slide');
  if (slides.length > 1) {
    const dotsBox = document.querySelector('.hero .dots');
    let cur = 0, timer;
    const show = n => {
      cur = (n + slides.length) % slides.length;
      slides.forEach((s, i) => s.classList.toggle('on', i === cur));
      if (dotsBox) dotsBox.querySelectorAll('button').forEach((d, i) => d.classList.toggle('on', i === cur));
    };
    const start = () => { if (!reduced) timer = setInterval(() => show(cur + 1), 6500); };
    if (dotsBox) {
      slides.forEach((_, i) => {
        const d = document.createElement('button'); d.type = 'button'; d.setAttribute('aria-label', `${i + 1}번 슬라이드`);
        d.addEventListener('click', () => { clearInterval(timer); show(i); start(); });
        dotsBox.appendChild(d);
      });
    }
    show(0);
    // 2·3번 슬라이드 이미지는 첫 화면 이후 로드 (LCP 보호)
    const lazyLoad = () => slides.forEach(sl => { const im = sl.querySelector('img[data-src]'); if (!im) return;
      im.src = (innerWidth <= 640 && im.dataset.srcM) ? im.dataset.srcM : im.dataset.src; im.removeAttribute('data-src'); });
    if (document.readyState === 'complete') setTimeout(lazyLoad, 800); else addEventListener('load', () => setTimeout(lazyLoad, 800));
    start();
  }

  // ---- 탭 (?tab= 초기값 + 클리닉 페이지 디스크 섹션 연동) ----
  const tabBtns = document.querySelectorAll('.tabs [data-tab]');
  const onlyTab = document.querySelector('[data-only-tab]');
  const activate = (id, push) => {
    const panel = document.getElementById(id);
    if (!panel) return;
    tabBtns.forEach(x => { const on = x.dataset.tab === id; x.classList.toggle('on', on); x.setAttribute('aria-selected', on); });
    document.querySelectorAll('.panel').forEach(x => x.classList.toggle('on', x.id === id));
    if (onlyTab) onlyTab.hidden = onlyTab.dataset.onlyTab !== id;
    if (push && history.replaceState) {
      const u = new URL(location.href); u.searchParams.set('tab', id); history.replaceState(null, '', u);
    }
  };
  tabBtns.forEach(b => b.addEventListener('click', () => activate(b.dataset.tab, body.dataset.page === 'clinic')));
  if (body.dataset.activeTab) activate(body.dataset.activeTab, false);

  // ---- 카드 슬라이드 ----
  const t = document.querySelector('.track');
  if (t) {
    const cards = t.children, n = cards.length; let i = 0;
    const per = () => innerWidth <= 640 ? 1 : innerWidth <= 1024 ? 2 : 3;
    const go = d => { i = Math.max(0, Math.min(n - per(), i + d)); const w = cards[0].getBoundingClientRect().width + 20; t.style.transform = `translateX(-${i * w}px)`; };
    document.querySelector('.arr.l').onclick = () => go(-1);
    document.querySelector('.arr.r').onclick = () => go(1);
    let sx = 0;
    t.addEventListener('pointerdown', e => sx = e.clientX);
    t.addEventListener('pointerup', e => { const d = e.clientX - sx; if (Math.abs(d) > 40) go(d < 0 ? 1 : -1); });
    addEventListener('resize', () => go(0));
  }

  // ---- 병원 둘러보기 썸네일 → 대표 사진 교체 ----
  const thumbs = document.querySelectorAll('.thumbs .ph');
  const mainPh = document.querySelector('.tour .main');
  if (thumbs.length && mainPh) {
    const pick = th => {
      const main = mainPh.querySelector('img'), im = th.querySelector('img');
      if (!main || !im) return;
      thumbs.forEach(x => x.classList.toggle('on', x === th));
      mainPh.classList.remove('sw'); void mainPh.offsetWidth; mainPh.classList.add('sw');
      main.src = im.src; main.alt = im.alt; mainPh.dataset.name = th.dataset.name || '';
    };
    thumbs.forEach(th => {
      th.addEventListener('click', () => pick(th));
      th.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(th); } });
    });
  }

  // ---- TOP ----
  document.querySelectorAll('a[href="#top"]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); scrollTo({ top: 0, behavior: 'smooth' }); }));

  // ---- 상담 예약 모달 ----
  const modal = document.getElementById('inqModal');
  if (modal) {
    const open = e => { e.preventDefault(); modal.classList.add('on'); const f = modal.querySelector('input[name="name"]'); if (f) f.focus(); };
    const close = () => modal.classList.remove('on');
    document.querySelectorAll('[data-open-inquiry]').forEach(a => a.addEventListener('click', open));
    modal.querySelector('.x').addEventListener('click', close);
    modal.addEventListener('click', e => { if (e.target === modal) close(); });
    addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  }

  // ---- 상담 문의 폼 → POST /api/inquiry ----
  const digits = s => (s || '').replace(/[^0-9]/g, '');
  document.querySelectorAll('.inq-form').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const msg = f.querySelector('.msg'), btn = f.querySelector('button[type="submit"]');
    const data = {
      name: f.name.value.trim(), phone: f.phone.value.trim(), part: f.part.value,
      message: f.message.value.trim(), agree: f.agree.checked, website: f.website.value
    };
    msg.className = 'msg';
    if (data.name.length < 2) { msg.textContent = '이름을 입력해 주세요.'; msg.classList.add('err'); return; }
    if (digits(data.phone).length < 9) { msg.textContent = '연락처를 확인해 주세요.'; msg.classList.add('err'); return; }
    if (!data.agree) { msg.textContent = '개인정보 수집·이용에 동의해 주세요.'; msg.classList.add('err'); return; }
    btn.disabled = true; msg.textContent = '접수 중…';
    try {
      const r = await fetch('/api/inquiry', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j.ok) { msg.textContent = j.message || '접수되었습니다. 확인 후 연락드리겠습니다.'; f.reset(); }
      else { msg.textContent = j.message || '접수에 실패했습니다. 전화로 문의해 주세요.'; msg.classList.add('err'); }
    } catch (_) {
      msg.textContent = '네트워크 오류입니다. 잠시 후 다시 시도해 주세요.'; msg.classList.add('err');
    }
    btn.disabled = false;
  }));

  // ---- 카카오맵 ----
  const mapEl = document.getElementById('map');
  if (mapEl && mapEl.dataset.lat && window.kakao && kakao.maps && kakao.maps.load) {
    kakao.maps.load(() => {
      const pos = new kakao.maps.LatLng(parseFloat(mapEl.dataset.lat), parseFloat(mapEl.dataset.lng));
      const map = new kakao.maps.Map(mapEl, { center: pos, level: 3 });
      const marker = new kakao.maps.Marker({ position: pos, map });
      const iw = new kakao.maps.InfoWindow({ content: '<div style="padding:6px 12px;font-size:13px;font-weight:600;white-space:nowrap">' + mapEl.dataset.name + '</div>' });
      iw.open(map, marker);
      map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
      const ph = mapEl.querySelector('.ph'); if (ph) ph.remove();
    });
  }
})();
