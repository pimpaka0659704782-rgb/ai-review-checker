import streamlit as st
import re

st.set_page_config(page_title="Advanced Review Analyzer", page_icon="🛍️")
st.title("🛍️ เครื่องมือวิเคราะห์รีวิวสินค้า (ขยายคลังคำศัพท์ & คิดคะแนนละเอียด)")

review_input = st.text_area("วางข้อความรีวิวสินค้าที่นี่ (รองรับหลายบรรทัด/ลิงก์):", height=200)

if st.button("🔍 วิเคราะห์รีวิว"):
    if not review_input.strip():
        st.warning("กรุณากรอกข้อความรีวิวก่อนกดวิเคราะห์")
    else:
        # 1. คลังคำศัพท์เชิงบวก (Positive Keywords)
        pos_words = [
            "ดี", "ชอบ", "ส่งไว", "คุ้ม", "ตรงปก", "ใช้งานง่าย", "สวย", "เยี่ยม", "ประทับใจ",
            "ตรงตามปก", "แพ็คมาดี", "จัดส่งเร็ว", "ของแท้", "คุณภาพดี", "แข็งแรง", "ทนทาน",
            "ราคาถูก", "แถม", "น่ารัก", "สมราคา", "แม่ค้าน่ารัก", "บริการดี", "ตอบไว",
            "เนียน", "หอม", "นุ่ม", "อร่อย", "ใช้ดี", "แนะนำ", "งานดี", "เนียบ"
        ]

        # 2. คลังคำศัพท์เชิงลบ (Negative Keywords)
        neg_words = [
            "แย่", "ช้า", "พัง", "ไม่ตรงปก", "แพง", "ห่วย", "ชำรุด", "เสียหาย", "รอย",
            "ส่งช้า", "รอนาน", "แตก", "หัก", "หลุด", "ใช้ไม่ได้", "ของปลอม", "ก๊องแก๊ง",
            "เสียความรู้สึก", "อย่าซื้อ", "ปลอม", "รอยถลอก", "ไม่แนะนำ", "ผิดหวัง", "ช้ามาก",
            "ไม่คุ้ม", "ยับ", "ขาด", "กล่องบุบ", "แพ็คไม่ดี"
        ]

        # 3. สัญญาณรีวิวปลอม / สแปม (Spam / Fake Signals)
        fake_patterns = [
            r"https?://\S+",             # ลิงก์ภายนอก เช่น tiktok/shopee
            r"(.)\1{3,}",                # ตัวอักษรซ้ำเกิน 3 ตัว เช่น ดีมากกกกกก
            r"10/10", r"100/10",         # คำอวยเวอร์เกินไป
            r"แนะนำร้านนี้", r"กดลิงก์"
        ]

        lines = [line.strip() for line in review_input.split("\n") if line.strip()]
        
        found_pros = []
        found_cons = []
        fake_warnings = []

        # วิเคราะห์ทีละบรรทัด
        for line in lines:
            has_pos = any(w in line for w in pos_words)
            has_neg = any(w in line for w in neg_words)

            if has_pos and not has_neg:
                found_pros.append(line)
            elif has_neg:
                found_cons.append(line)

            # ตรวจสอบสแปม
            for pattern in fake_patterns:
                if re.search(pattern, line):
                    fake_warnings.append(f"พบรูปแบบต้องสงสัยในข้อความ: '{line[:30]}...'")
                    break

        # คำนวณคะแนน
        total_pos = len(found_pros)
        total_neg = len(found_cons)
        total_found = total_pos + total_neg

        # คะแนนความพึงพอใจ (Sentiment Score)
        if total_found > 0:
            sentiment_score = int((total_pos / total_found) * 100)
        else:
            sentiment_score = 50  # ค่าเริ่มต้นกรณีคำไม่เข้าเงื่อนไข

        # คะแนนความน่าเชื่อถือ (Trust Score)
        spam_penalty = len(fake_warnings) * 25
        trust_score = max(10, 100 - spam_penalty)

        # --- แสดงผลบนหน้าเว็บ ---
        st.divider()
        col_score1, col_score2 = st.columns(2)
        
        with col_score1:
            st.subheader("📊 คะแนนความพึงพอใจ")
            st.progress(sentiment_score / 100)
            st.write(f"เชิงบวก: **{sentiment_score}%**")

        with col_score2:
            st.subheader("🛡️ คะแนนความน่าเชื่อถือ")
            st.progress(trust_score / 100)
            st.write(f"ความน่าเชื่อถือ: **{trust_score}%**")

        st.divider()

        # แสดงข้อดี / ข้อเสีย
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 🟢 ข้อดีที่ตรวจพบ")
            if found_pros:
                for p in found_pros:
                    st.write(f"- {p}")
            else:
                st.write("- ไม่พบข้อความเชิงบวกชัดเจน")

        with col2:
            st.write("### 🔴 ข้อเสียที่ตรวจพบ")
            if found_cons:
                for c in found_cons:
                    st.write(f"- {c}")
            else:
                st.write("- ไม่พบข้อความเชิงลบชัดเจน")

        # แสดงการแจ้งเตือนสแปม
        if fake_warnings:
            st.warning("⚠️ **ตรวจพบสัญญาณต้องสงสัย (อาจเป็นรีวิวปลอม/สแปม):**")
            for w in fake_warnings:
                st.write(f"- {w}")
