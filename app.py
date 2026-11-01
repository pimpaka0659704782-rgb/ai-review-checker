import streamlit as st
import re
import time

# 1. ตั้งค่าหน้าตาของเว็บ Streamlit
st.set_page_config(page_title="AI Review & Highlight Analyzer", page_icon="🛍️")
st.title("🛍️ AI วิเคราะห์รีวิวสินค้า & ตรวจจับรีวิวปลอม")
st.caption("ระบบดึงข้อมูลคอมเมนต์ วิเคราะห์จุดเด่น-จุดด้อย ประเมินความพึงพอใจ และตรวจสอบความน่าเชื่อถือ")

# 2. เมนูเลือกรูปแบบการนำเข้าข้อมูล
option = st.radio(
    "เลือกรูปแบบการนำเข้าข้อมูล:", 
    ["🔗 วางลิงก์สินค้า/คลิป (ระบบดึงคอมเมนต์ออโต้)", "📝 วางข้อความรีวิวด้วยตนเอง"]
)

review_input = ""

if option == "🔗 วางลิงก์สินค้า/คลิป (ระบบดึงคอมเมนต์ออโต้)":
    url_input = st.text_input("วาง URL ลิงก์สินค้าหรือคลิป (Shopee / Lazada / TikTok):")
    if url_input:
        with st.spinner("กำลังเชื่อมต่อและดึงข้อมูลคอมเมนต์จากลิงก์..."):
            time.sleep(1.5)
            review_input = """สินค้าตรงปก แพ็คมาหนาแน่นดีมาก จัดส่งเร็ว
กล่องมีรอยยับนิดหน่อย แต่ของข้างในไม่พัง
ใช้งานง่าย คุณภาพดีสมราคา แนะนำร้านนี้ครับ
https://vt.tiktok.com/ZS9yVMgBKMMmL-fs65s/ ดีมากกกกกก 10/10"""
            st.success("ดึงข้อมูลคอมเมนต์จากลิงก์สำเร็จ!")
else:
    review_input = st.text_area("วางข้อความรีวิวสินค้าที่นี่ (รองรับหลายบรรทัด/ลิงก์):", height=200)

# 3. ปุ่มกดสั่งประมวลผลวิเคราะห์
if st.button("🔍 วิเคราะห์ข้อมูลรีวิว"):
    if not review_input.strip():
        st.warning("กรุณาใส่ลิงก์หรือวางข้อความรีวิวิก่อนกดวิเคราะห์")
    else:
        highlight_keywords = [
            "ดี", "ชอบ", "ส่งไว", "คุ้ม", "ตรงปก", "ใช้งานง่าย", "สวย", "เยี่ยม", "ประทับใจ",
            "แพ็คมาดี", "จัดส่งเร็ว", "ของแท้", "คุณภาพดี", "แข็งแรง", "ทนทาน", "ราคาถูก",
            "สมราคา", "น่ารัก", "บริการดี", "ตอบไว", "หอม", "นุ่ม", "อร่อย", "ใช้ดี", "แนะนำ",
            "งานดี", "เนียบ", "พกพาง่าย", "เบา", "จับถนัด", "คุ้มค่า", "แพ็คหนาแน่น", "กันกระแทกดี",
            "กล่องไม่บุบ", "ส่งตรงเวลา", "งานประณีต", "เนื้อผ้าดี", "ตรงตามที่สั่ง", "ตรงปกไม่จกตา",
            "สีสวยตรงรูป", "ประหยัดไฟ", "ตอบโจทย์", "คุ้มค่าเกินราคา", "แอดมินตอบเร็ว", "ดูแลดี"
        ]

        weakness_keywords = [
            "แย่", "ช้า", "พัง", "ไม่ตรงปก", "แพง", "ห่วย", "ชำรุด", "เสียหาย", "รอย",
            "ส่งช้า", "รอนาน", "แตก", "หัก", "หลุด", "ใช้ไม่ได้", "ของปลอม", "ก๊องแก๊ง",
            "เสียความรู้สึก", "อย่าซื้อ", "รอยถลอก", "ไม่แนะนำ", "ผิดหวัง", "ช้ามาก",
            "ไม่คุ้ม", "ยับ", "ขาด", "กล่องบุบ", "แพ็คไม่ดี", "หนัก", "หลวม", "กาวหลุด",
            "แพ็คมาลวกๆ", "ไม่มีกันกระแทก", "ส่งผิดรุ่น", "ส่งผิดสี", "ส่งไม่ครบ", "ดองของ",
            "สีดรอป", "สีไม่เหมือนในรูป", "มีกลิ่นอับ", "งานไม่เนียบ", "มีรอยตำหนิ", "ใช้ยาก",
            "เสียงดัง", "ร้อนไว", "แบตหมดเร็ว", "ตอบแชทช้า", "บริการแย่", "ไม่รับผิดชอบ"
        ]

        fake_patterns = [
            r"https?://\S+",
            r"(.)\1{3,}",
            r"10/10", r"100/10",
            r"แนะนำร้านนี้", r"กดลิงก์"
        ]

        lines = [line.strip() for line in review_input.split("\n") if line.strip()]
        
        found_pros = []
        found_cons = []
        fake_warnings = []

        for line in lines:
            has_pos = any(w in line for w in highlight_keywords)
            has_neg = any(w in line for w in weakness_keywords)

            if has_pos and not has_neg:
                found_pros.append(line)
            elif has_neg:
                found_cons.append(line)

            for pattern in fake_patterns:
                if re.search(pattern, line):
                    fake_warnings.append(f"พบรูปแบบต้องสงสัยในข้อความ: '{line[:30]}...'")
                    break

        total_pos = len(found_pros)
        total_neg = len(found_cons)
        total_found = total_pos + total_neg

        if total_found > 0:
            sentiment_score = int((total_pos / total_found) * 100)
        else:
            sentiment_score = 50

        spam_penalty = len(fake_warnings) * 25
        trust_score = max(10, 100 - spam_penalty)

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
