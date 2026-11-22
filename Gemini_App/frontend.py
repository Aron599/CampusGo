import streamlit as st
import requests

# Oldal beállítása mobilbarát nézetre
st.set_page_config(
    page_title="CampusGo",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Kompakt mobilbarát CSS finomhangolás
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 480px; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; }
        .stButton > button { width: 100%; border-radius: 12px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Munkamenet (Session State) inicializálása
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000"


def api_request(method: str, endpoint: str, json_data=None, files=None, params=None):
    """Központi API hívó függvény a FastAPI backendhez."""
    url = f"{st.session_state.api_url.rstrip('/')}{endpoint}"
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            files=files,
            params=params,
            timeout=10
        )
        if resp.status_code == 401 and endpoint != "/api/auth/login":
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

        data = resp.json() if resp.content else {}
        if not resp.ok:
            return None, data.get("detail", f"Szerverhiba ({resp.status_code})")
        return data, None
    except requests.exceptions.ConnectionError:
        return None, "Nem érhető el a backend szerver! Ellenőrizd, hogy fut-e."
    except Exception as e:
        return None, f"Hiba történt: {str(e)}"


def refresh_profile():
    """Felhasználói adatok (szint, XP, coin) frissítése."""
    user_data, err = api_request("GET", "/api/auth/me")
    if user_data:
        st.session_state.user = user_data


# ================= HITELESÍTÉS (BEJELENTKEZÉS / REGISZTRÁCIÓ) =================
if not st.session_state.token:
    st.title("🎓 CampusGo")
    st.caption("Teljesíts egyetemi küldetéseket és váltsd be a pontjaidat!")

    tab_login, tab_reg = st.tabs(["Bejelentkezés", "Regisztráció"])

    with tab_login:
        with st.form("login_form"):
            neptun = st.text_input("Neptun-kód", max_chars=6, placeholder="ABC123").upper()
            password = st.text_input("Jelszó", type="password")
            submitted = st.form_submit_button("Belépés", type="primary")

            if submitted:
                data, err = api_request("POST", "/api/auth/login", json_data={
                    "neptun_code": neptun.strip(),
                    "password": password
                })
                if err:
                    st.error(err)
                else:
                    st.session_state.token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.rerun()

    with tab_reg:
        with st.form("register_form"):
            reg_name = st.text_input("Teljes név", placeholder="Teszt Elek")
            reg_neptun = st.text_input("Neptun-kód", max_chars=6, placeholder="ABC123").upper()
            reg_email = st.text_input("E-mail cím", placeholder="hallgato@egyetem.hu")
            reg_pass = st.text_input("Jelszó", type="password")
            reg_sub = st.form_submit_button("Fiók létrehozása", type="primary")

            if reg_sub:
                data, err = api_request("POST", "/api/auth/register", json_data={
                    "name": reg_name.strip(),
                    "neptun_code": reg_neptun.strip(),
                    "email": reg_email.strip(),
                    "password": reg_pass
                })
                if err:
                    st.error(err)
                else:
                    st.success("Sikeres regisztráció! Most már bejelentkezhetsz.")

    with st.expander("⚙️ Szerver beállítások"):
        st.session_state.api_url = st.text_input("Backend API URL", value=st.session_state.api_url)

    st.stop()


# ================= FŐ ALKALMAZÁS (BEJELENTKEZVE) =================
user = st.session_state.user

# Fejléc és kilépés gomb
col_title, col_logout = st.columns([3, 1])
with col_title:
    st.subheader(f"👋 {user['name']}")
    st.caption(f"Neptun: **{user['neptun_code']}**")
with col_logout:
    if st.button("Kilépés"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

# Státusz kártyák (Szint, XP, Coin)
c1, c2, c3 = st.columns(3)
c1.metric("Szint", user["level"])
c2.metric("XP", user["xp"])
c3.metric("Coin", f"{user['coins']} 🪙")

st.divider()

# Fő navigációs fülek
tab_quests, tab_qr, tab_shop = st.tabs(["🗺️ Küldetések", "📷 QR Olvasó", "🛍️ Bolt & Kuponok"])


def redeem_qr_token(token_str: str):
    """Közös beváltó függvény a QR-kódhoz."""
    if not token_str or not token_str.strip():
        st.error("Üres QR-kód!")
        return
    res, err = api_request("POST", "/api/quests/redeem-qr", json_data={"qr_token": token_str.strip()})
    if err:
        st.error(err)
    else:
        st.success(f"{res['message']} (+{res['rewards']['xp']} XP, +{res['rewards']['coins']} Coin)")
        refresh_profile()
        st.rerun()


# --- 1. KÜLDETÉSEK FÜL ---
with tab_quests:
    if st.button("🔄 Küldetések frissítése"):
        st.rerun()

    quests, err = api_request("GET", "/api/quests/")
    if err:
        st.error(err)
    elif not quests:
        st.info("🎉 Minden elérhető küldetést teljesítettél!")
    else:
        for q in quests:
            with st.container(border=True):
                st.markdown(f"**{q['title']}** `{q['type']}`")
                st.write(q["description"])
                st.caption(f"Jutalom: **+{q['xp_reward']} XP** | **+{q['coin_reward']} 🪙**")


# --- 2. QR OLVASÓ FÜL ---
with tab_qr:
    st.markdown("#### QR-kód beolvasása")

    # 1. Mobil kamera fotó -> backend dekódolás (/qr/scan-upload) -> beváltás
    cam_image = st.camera_input("Készíts fotót a QR-kódról")
    if cam_image is not None:
        if st.button("📸 Fotó feldolgozása és beváltása", type="primary"):
            files = {"file": ("camera.jpg", cam_image.getvalue(), "image/jpeg")}
            scan_res, err = api_request("POST", "/qr/scan-upload", files=files)
            if err:
                st.error(err)
            else:
                redeem_qr_token(scan_res["qr_data"])

    st.divider()

    # 2. Képfeltöltés galériából
    uploaded_file = st.file_uploader("Vagy tölts fel egy QR-kódot tartalmazó képet", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        if st.button("🖼️ Feltöltött kép beváltása"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            scan_res, err = api_request("POST", "/qr/scan-upload", files=files)
            if err:
                st.error(err)
            else:
                redeem_qr_token(scan_res["qr_data"])

    # 3. Manuális kód és Mock teszt
    with st.expander("🧪 Manuális kód / Mock QR teszt"):
        manual_code = st.text_input("QR token kézi beírása")
        if st.button("Kód beváltása"):
            redeem_qr_token(manual_code)

        if st.button("Mock QR teszt (/qr/scan-mock)"):
            scan_res, err = api_request("GET", "/qr/scan-mock")
            if err:
                st.error(err)
            else:
                redeem_qr_token(scan_res["qr_data"])


# --- 3. BOLT ÉS KUPONOK FÜL ---
with tab_shop:
    col_shop_title, col_dev = st.columns([2, 1])
    with col_shop_title:
        st.markdown("#### Elérhető jutalmak")
    with col_dev:
        if st.button("+100 Teszt Coin"):
            res, err = api_request("POST", "/api/shop/dev/add-coins", params={"amount": 100})
            if res:
                refresh_profile()
                st.rerun()

    items, err = api_request("GET", "/api/shop/items")
    if err:
        st.error(err)
    elif not items:
        st.info("Jelenleg nincs elérhető termék a boltban.")
    else:
        for item in items:
            with st.container(border=True):
                c_info, c_btn = st.columns([2, 1])
                with c_info:
                    st.markdown(f"**{item['name']}**")
                    if item.get("description"):
                        st.caption(item["description"])
                    if item.get("stock") is not None:
                        st.caption(f"Készlet: {item['stock']} db")
                with c_btn:
                    out_of_stock = item.get("stock") is not None and item["stock"] <= 0
                    label = "Elfogyott" if out_of_stock else f"{item['price']} 🪙"
                    if st.button(label, key=f"buy_{item['id']}", disabled=out_of_stock, type="primary"):
                        buy_res, buy_err = api_request("POST", f"/api/shop/buy/{item['id']}")
                        if buy_err:
                            st.error(buy_err)
                        else:
                            st.success(f"Sikeres vásárlás! Kupon: **{buy_res['coupon_code']}**")
                            refresh_profile()
                            st.rerun()

    st.divider()
    st.markdown("#### 🎟️ Megvásárolt kuponjaim")
    purchases, p_err = api_request("GET", "/api/shop/my-purchases")
    if p_err:
        st.error(p_err)
    elif not purchases:
        st.caption("Még nincs megvásárolt kuponod.")
    else:
        for p in purchases:
            with st.container(border=True):
                st.markdown(f"**{p['item_name']}** — Kód: `{p['coupon_code']}`")
                st.caption(f"Ár: {p['price_paid']} coin | Időpont: {p['purchased_at'][:16].replace('T', ' ')}")
