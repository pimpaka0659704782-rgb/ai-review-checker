import streamlit as st
import re

# ตั้งค่าหน้าตาของเว็บ
st.set_page_config(page_title="AI Review & Highlight Analyzer", page_icon="🛍️")
st.title("🛍️ AI วิเคราะห์รีวิวสินค้า & ตรวจจับรีวิวปลอม")
st.caption("ระบบวิเคราะห์จุดเด่น-จุดด้อย ประเมินความพึงพอใจ และตรวจสอบความน่าเชื่อถือของรีวิว")

# ช่องวางข้อความรีวิว
review_input = st.text_area("วางข้อความรีวิวสินค้าที่นี่ (รองรับหลายบรรทัด/ลิงก์):", height=200)

if st.button("🔍 วิเคราะห์รีวิว"):
    if not review_input.strip():
        st.warning("กรุณากรอกข้อความรีวิวิก่อนกดวิเคราะห์")
    else:
        # 1. คลังคำศัพท์คัดกรอง "จุดเด่น" (Highlights / Pros) - รวมคำเดิม + คำเพิ่มใหม่
        highlight_keywords = [
            "ดี", "ชอบ", "ส่งไว", "คุ้ม", "ตรงปก", "ใช้งานง่าย", "สวย", "เยี่ยม", "ประทับใจ",
            "แพ็คมาดี", "จัดส่งเร็ว", "ของแท้", "คุณภาพดี", "แข็งแรง", "ทนทาน", "ราคาถูก",
            "สมราคา", "น่ารัก", "บริการดี", "ตอบไว", "หอม", "นุ่ม", "อร่อย", "ใช้ดี", "แนะนำ",
            "งานดี", "เนียบ", "พกพาง่าย", "เบา", "จับถนัด", "คุ้มค่า", "แพ็คหนาแน่น", "กันกระแทกดี",
            "กล่องไม่บุบ", "ส่งตรงเวลา", "งานประณีต", "เนื้อผ้าดี", "ตรงตามที่สั่ง", "ตรงปกไม่จกตา",
            "สีสวยตรงรูป", "ประหยัดไฟ", "ตอบโจทย์", "คุ้มค่าเกินราคา", "แอดมินตอบเร็ว", "ดูแลดี"
        ]

        # 2. คลังคำศัพท์คัดกรอง "จุดด้อย" (Weaknesses / Cons) - รวมคำเดิม + คำเพิ่มใหม่
        weakness_keywords = [
            "แย่", "ช้า", "พัง", "ไม่ตรงปก", "แพง", "ห่วย", "ชำรุด", "เสียหาย", "รอย",
            "ส่งช้า", "รอนาน", "แตก", "หัก", "หลุด", "ใช้ไม่ได้", "ของปลอม", "ก๊องแก๊ง",
            "เสียความรู้สึก", "อย่าซื้อ", "รอยถลอก", "ไม่แนะนำ", "ผิดหวัง", "ช้ามาก",
            "ไม่คุ้ม", "ยับ", "ขาด", "กล่องบุบ", "แพ็คไม่ดี", "หนัก", "หลวม", "กาวหลุด",
            "แพ็คมาลวกๆ", "ไม่มีกันกระแทก", "ส่งผิดรุ่น", "ส่งผิดสี", "ส่งไม่ครบ", "ดองของ",
            "สีดรอป", "สีไม่เหมือนในรูป", "มีกลิ่นอับ", "งานไม่เนียบ", "มีรอยตำหนิ", "ใช้ยาก",
            "เสียงดัง", "ร้อนไว", "แบตหมดเร็ว", "ตอบแชทช้า", "บริการแย่", "ไม่รับผิดชอบ"
        ]

        # 3. สัญญาณรีวิวปลอม / สแปม (Spam & Fake Review Patterns)
        fake_patterns = [
            r"https?://\S+",             # ลิงก์ภายนอก เช่น tiktok/shopee/lazada
            r"(.)\1{3,}",                # ตัวอักษรซ้ำเกิน 3 ตัว เช่น ดีมากกกกกก
            r"10/10", r"100/10",         # คำอวยเวอร์เกินจริง
            r"แนะนำร้านนี้", r"กดลิงก์"
        ]

        lines = [line.strip() for line in review_input.split("\n") if line.strip()]
        
        found_pros = []
        found_cons = []
        fake_warnings = []

        # สแกนวิเคราะห์ข้อความทีละบรรทัด
        for line in lines:
            has_pos = any(w in line for w in highlight_keywords)
            has_neg = any(w in line for w in weakness_keywords)

            if has_pos and not has_neg:
                found_pros.append(line)
            elif has_neg:
                found_cons.append(line)

            # ตรวจสอบรูปแบบสแปมหรือรีวิวปลอม
            for pattern in fake_patterns:
                if re.search(pattern, line):
                    fake_warnings.append(f"พบรูปแบบต้องสงสัยในข้อความ: '{line[:30]}...'")
                    break

        # --- คำนวณคะแนน ---
        total_pos = len(found_pros)
        total_neg = len(found_cons)
        total_found = total_pos + total_neg

        # คะแนนความพึงพอใจ (Sentiment Score)
        if total_found > 0:
            sentiment_score = int((total_pos / total_found) * 100)
        else:
            sentiment_score = 50

        # คะแนนความน่าเชื่อถือ (Trust Score) - หักคะแนนตามสแปมที่พบ
        spam_penalty = len(fake_warnings) * 25
        trust_score = max(10, 100 - spam_penalty)

        # --- ส่วนแสดงผลลัพธ์บนหน้าเว็บ ---
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

        # แสดงส่วน จุดเด่น (สีเขียว) และ จุดด้อย (สีแดง)
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

        # แสดงกล่องเตือนหากพบสัญญาณรีวิวปลอม/สแปม
        if fake_warnings:
            st.divider()
            st.warning("⚠️ **ตรวจพบสัญญาณต้องสงสัย (อาจเป็นรีวิวปลอม/สแปม):**")
            for w in fake_warnings:
                st.write(f"- {w}")
