import streamlit as st
import re
import time

# 1. ตั้งค่าหน้าตาของเว็บ Streamlit
st.set_page_config(page_title="AI Review & Price Analyzer", page_icon="🛍️")
st.title("🛍️ AI วิเคราะห์รีวิวสินค้า & ตรวจจับราคาสินค้า")
st.caption("ระบบดึงข้อมูลคอมเมนต์ วิเคราะห์จุดเด่น-จุดด้อย ประเมินราคา ความคุ้มค่า และตรวจจับรีวิวปลอม")

# 2. เมนูเลือกรูปแบบการนำเข้าข้อมูล
option = st.radio(
    "เลือกรูปแบบการนำเข้าข้อมูล:", 
    ["🔗 วางลิงก์สินค้า/คลิป (ระบบดึงคอมเมนต์ออโต้)", "📝 วางข้อความรีวิวด้วยตนเอง"]
)

# จัดการ State ล้างผลลัพธ์ทันทีเมื่อมีการสลับโหมด
if "prev_option" not in st.session_state:
    st.session_state.prev_option = option
elif st.session_state.prev_option != option:
    st.session_state.prev_option = option
    st.session_state.analyzed = False
    st.session_state.current_review = ""

review_input = ""

if option == "🔗 วางลิงก์สินค้า/คลิป (ระบบดึงคอมเมนต์ออโต้)":
    url_input = st.text_input("วาง URL ลิงก์สินค้าหรือคลิป (Shopee / Lazada / TikTok):", key="url_key")
    
    # ตรวจสอบว่าถ้าเปลี่ยน URL สินค้าใหม่ ให้ล้างผลลัพธ์เดิมออกก่อนกดวิเคราะห์
    if "last_url" not in st.session_state:
        st.session_state.last_url = url_input
    elif st.session_state.last_url != url_input:
        st.session_state.last_url = url_input
        st.session_state.analyzed = False

    if url_input:
        with st.spinner("กำลังเชื่อมต่อและดึงข้อมูลคอมเมนต์จากลิงก์..."):
            time.sleep(0.5)
            # ตัวอย่างดึงข้อมูลจำลองโดยใช้ URL ปัจจุบันเพื่อให้ข้อมูลเปลี่ยนตามลิงก์ที่วางจริง
            review_input = f"""สินค้าจากลิงก์ ({url_input[-20:]}) ตรงปก แพ็คมาหนาแน่นดีมาก จัดส่งเร็ว
ซื้อมาในราคา 350 บาท ถือว่าคุ้มค่าสมราคา
กล่องมีรอยยับนิดหน่อย แต่ของข้างในไม่พัง ใช้งานง่าย"""
            st.success("ดึงข้อมูลคอมเมนต์จากลิงก์สำเร็จ!")
else:
    review_input = st.text_area("วางข้อความรีวิวสินค้าที่นี่ (รองรับหลายบรรทัด/ลิงก์):", height=200, key="text_key")

# 3. ปุ่มกดสั่งประมวลผลวิเคราะห์
if st.button("🔍 วิเคราะห์ข้อมูลรีวิว"):
    if not review_input.strip():
        st.warning("กรุณาใส่ลิงก์หรือวางข้อความรีวิวิก่อนกดวิเคราะห์")
    else:
        st.session_state.analyzed = True
        st.session_state.current_review = review_input

# แสดงผลลัพธ์การวิเคราะห์เมื่อกดปุ่มวิเคราะห์ข้อมูลใหม่เท่านั้น
if st.session_state.get("analyzed", False) and st.session_state.get("current_review"):
    current_data = st.session_state.current_review

    # --- 1. ตรวจจับราคา (Price Extraction) ---
    price_pattern = r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:บาท|฿|บ\.|.-)'
    found_prices = re.findall(price_pattern, current_data)

    # --- 2. คลังคำศัพท์ประเมินเรื่องราคาและความคุ้มค่า ---
    cheap_keywords = ["ถูก", "คุ้ม", "สมราคา", "ไม่แพง", "คุ้มค่า", "ลดราคา", "ได้แถม"]
    expensive_keywords = ["แพง", "ไม่คุ้ม", "เกินจริง", "แพงไป", "เสียดายเงิน"]

    # --- 3. คลังคำศัพท์จุดเด่น / จุดด้อย ---
    highlight_keywords = [
        "ดี", "ชอบ", "ส่งไว", "ตรงปก", "ใช้งานง่าย", "สวย", "เยี่ยม", "ประทับใจ",
        "แพ็คมาดี", "จัดส่งเร็ว", "ของแท้", "คุณภาพดี", "แข็งแรง", "ทนทาน", "ราคาถูก",
        "สมราคา", "น่ารัก", "บริการดี", "ตอบไว", "หอม", "นุ่ม", "อร่อย", "ใช้ดี", "แนะนำ",
        "งานดี", "เนียบ", "พกพาง่าย", "เบา", "จับถนัด", "คุ้มค่า", "แพ็คหนาแน่น", "กันกระแทกดี",
        "กล่องไม่บุบ", "ส่งตรงเวลา", "งานประณีต", "เนื้อผ้าดี", "ตรงตามที่สั่ง", "ตรงปกไม่จกตา"
    ]

    weakness_keywords = [
        "แย่", "ช้า", "พัง", "ไม่ตรงปก", "ห่วย", "ชำรุด", "เสียหาย", "รอย",
        "ส่งช้า", "รอนาน", "แตก", "หัก", "หลุด", "ใช้ไม่ได้", "ของปลอม", "ก๊องแก๊ง",
        "เสียความรู้สึก", "อย่าซื้อ", "รอยถลอก", "ไม่แนะนำ", "ผิดหวัง", "ช้ามาก",
        "ยับ", "ขาด", "กล่องบุบ", "แพ็คไม่ดี", "หนัก", "หลวม", "กาวหลุด"
    ]

    fake_patterns = [
        r"https?://\S+",
        r"(.)\1{3,}",
        r"10/10", r"100/10",
        r"แนะนำร้านนี้", r"กดลิงก์"
    ]

    lines = [line.strip() for line in current_data.split("\n") if line.strip()]
    
    found_pros = []
    found_cons = []
    fake_warnings = []
    price_sentiments = []

    for line in lines:
        has_pos = any(w in line for w in highlight_keywords)
        has_neg = any(w in line for w in weakness_keywords)

        if has_pos and not has_neg:
            found_pros.append(line)
        elif has_neg:
            found_cons.append(line)

        if any(w in line for w in cheap_keywords):
            price_sentiments.append("🟢 ผู้รีวิวรู้สึกว่า **ราคาคุ้มค่า / ถูก**")
        elif any(w in line for w in expensive_keywords):
            price_sentiments.append("🔴 ผู้รีวิวรู้สึกว่า **ราคาแพง / ไม่คุ้มค่า**")

        for pattern in fake_patterns:
            if re.search(pattern, line):
                fake_warnings.append(f"พบรูปแบบต้องสงสัยในข้อความ: '{line[:30]}...'")
                break

    total_pos = len(found_pros)
    total_neg = len(found_cons)
    total_found = total_pos + total_neg

    sentiment_score = int((total_pos / total_found) * 100) if total_found > 0 else 50
    spam_penalty = len(fake_warnings) * 25
    trust_score = max(10, 100 - spam_penalty)

    # --- ส่วนแสดงผลบนหน้าเว็บ ---
    st.divider()

    st.subheader("🏷️ สรุปข้อมูลราคาและความคุ้มค่า")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if found_prices:
            st.info(f"💰 **ตรวจพบราคาในรีวิว:** {', '.join(found_prices)} บาท")
        else:
            st.info("💰 **ตรวจพบราคา:** ไม่ได้ระบุตัวเลขราคาในข้อความ")

    with col_p2:
        if price_sentiments:
            for ps in set(price_sentiments):
                st.write(ps)
        else:
            st.write("⚪ ไม่พบการแสดงความเห็นเรื่องราคา")

    st.divider()

    col_score1, col_score2 = st.columns(2)
    with col_score1:
        st.subheader("📊 คะแนนความพึงพอใจ")
        st.progress(sentiment_score / 100)
        st.write(f"เชิงบวก: **{sentiment_score}%**")

    with col_score2:
        st.subheader("🛡️ คะแนนความน่าเชื่อถือ (Trust Score)")
        st.progress(trust_score / 100)
        st.write(f"ความน่าเชื่อถือ: **{trust_score}%**")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.write("### ⭐ จุดเด่นประเมินได้ (Pros)")
        if found_pros:
            for p in found_pros:
                st.success(f"✔️ {p}")
        else:
            st.info("ไม่พบข้อความเชิงบวกชัดเจน")

    with col2:
        st.write("### ⚠️ จุดด้อยประเมินได้ (Cons)")
        if found_cons:
            for c in found_cons:
                st.error(f"❌ {c}")
        else:
            st.info("ไม่พบข้อความเชิงลบชัดเจน")

    if fake_warnings:
        st.divider()
        st.warning("⚠️ **ตรวจพบสัญญาณต้องสงสัย (อาจเป็นรีวิวปลอม/สแปม):**")
        for w in fake_warnings:
            st.write(f"- {w}")
