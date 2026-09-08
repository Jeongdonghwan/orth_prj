# Cafe24 배포 순서 (211.45.175.195, 멀티사이트 서버)

- 배포 경로 `/var/www/ortho`, 서비스 `ortho.service`, 포트 **8036** (다른 포트를 쓰면 `ortho.service`·`nginx.conf`의 8036 을 함께 바꾼다)
- 사용자는 MobaXterm 으로 root 접속. 아래 블록을 순서대로 붙여넣는다.

## 1. 포트 확인 + 코드 + venv + .env + systemd

```bash
ss -tlnp | grep ':8036 ' && echo "!! 8036 사용중" || echo "8036 비어있음 OK"

cd /var/www && git clone https://github.com/Jeongdonghwan/orth_prj.git ortho && cd ortho
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt

cp .env.example .env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 24)|" .env
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=|" .env
sed -i "s|^DB_NAME=.*|DB_NAME=ortho|" .env
sed -i "s|^DB_USER=.*|DB_USER=ortho|" .env
sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=1234|" .env
sed -i "s|^ADMIN_ID=.*|ADMIN_ID=admin|" .env
sed -i "s|^ADMIN_PW=.*|ADMIN_PW=1234|" .env
sed -i "s|^SITE_URL=.*|SITE_URL=http://211.45.175.195:8036|" .env
# 카카오맵·좌표·네이버 인증값은 받는 대로:
# sed -i "s|^KAKAO_JS_KEY=.*|KAKAO_JS_KEY=xxxx|; s|^CLINIC_LAT=.*|CLINIC_LAT=37.xxxx|; s|^CLINIC_LNG=.*|CLINIC_LNG=127.xxxx|" .env
cat .env

cp deploy/ortho.service /etc/systemd/system/ortho.service
systemctl daemon-reload
```

## 2. DB (root 비밀번호 입력 필요)

```bash
cd /var/www/ortho && mysql -u root -p < deploy/schema.sql
mysql -u root -p -e "CREATE USER IF NOT EXISTS 'ortho'@'localhost'; ALTER USER 'ortho'@'localhost' IDENTIFIED BY '1234'; GRANT ALL PRIVILEGES ON ortho.* TO 'ortho'@'localhost'; FLUSH PRIVILEGES;"
mysql -u ortho -p1234 -e "USE ortho; SHOW TABLES;"
```

기대 출력: `inquiries` 테이블 표시.

## 3. 기동·검증

```bash
systemctl enable --now ortho && systemctl status ortho --no-pager
curl -s http://127.0.0.1:8036/ | grep -o "<title>[^<]*</title>"
curl -s -o /dev/null -w "admin:%{http_code}\n" http://127.0.0.1:8036/admin/inquiries
curl -s http://127.0.0.1:8036/robots.txt
ufw status | head -1
```

기대 출력: `active (running)` / `<title>운남튼튼정형외과의원 …</title>` / `admin:401` / robots 내용.
`ufw` 가 active 면 `ufw allow 8036/tcp`. 실패 시 `journalctl -u ortho -n 30 --no-pager`.

## 4. 도메인 연결 (도메인 확정 후)

```bash
dig +short DOMAIN     # 211.45.175.195 이어야 함

sed "s/DOMAIN/실제도메인/g" /var/www/ortho/deploy/nginx.conf > /etc/nginx/sites-available/ortho
ln -sf /etc/nginx/sites-available/ortho /etc/nginx/sites-enabled/ortho
nginx -t && systemctl reload nginx

apt install -y certbot python3-certbot-nginx
certbot --nginx -d DOMAIN -d www.DOMAIN --agree-tos -m 메일주소 --redirect -n

cd /var/www/ortho && sed -i "s|^SITE_URL=.*|SITE_URL=https://DOMAIN|" .env && systemctl restart ortho
ufw delete allow 8036/tcp   # 프록시 뒤로 숨김
curl -sI https://DOMAIN | head -3
```

`SITE_URL` 이 canonical·OG·sitemap 에 그대로 들어가므로 도메인 연결 후 반드시 바꾼다.

## 5. 업데이트

```bash
cd /var/www/ortho && git pull && ./venv/bin/pip install -r requirements.txt -q && systemctl restart ortho && systemctl status ortho --no-pager
```

정적 파일만 바뀐 경우 브라우저 Ctrl+F5 (nginx 30일 캐시).

## 6. 실사진 교체

1. `docs/03` 체크리스트 파일명 그대로 `app/static/img/` 에 덮어쓰기 (git push → 업데이트 배포).
2. 용량이 크면 `python scripts/convert_webp.py --max 1600` 으로 webp 생성 후, nginx `location /static/img/` 에 아래를 추가하면 jpg 요청에 webp 를 대신 준다.

```nginx
location /static/img/ {
    alias /var/www/ortho/app/static/img/;
    expires 30d;
    set $webp "";
    if ($http_accept ~* "webp") { set $webp ".webp"; }
    try_files $uri$webp $uri =404;
}
```

## 7. 네이버·구글 등록

- 네이버 서치어드바이저 → 사이트 등록 → HTML 태그 인증값을 `.env` `NAVER_SITE_VERIFICATION=` 에 넣고 재시작 → 사이트맵 `https://DOMAIN/sitemap.xml` 제출.
- 구글 서치콘솔도 같은 sitemap 제출.

## 보안 메모

- `ADMIN_PW=1234` 는 임시. 공개 후 반드시 변경 (`sed -i "s|^ADMIN_PW=.*|ADMIN_PW=새비밀번호|" .env && systemctl restart ortho`).
- 관리자 페이지는 HTTPS 뒤에서만 쓰는 것을 권장 (Basic Auth 는 평문).
