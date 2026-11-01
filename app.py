import streamlit as st

st.set_page_config(page_title="Review Analyzer (No API)", page_icon="🛍️")
st.title("🛍️ เครื่องมือสรุปรีวิวสินค้า (ไม่ต้องใช้ API Key)")

review_input = st.text_area("วางข้อความรีวิวสินค้าที่นี่:", height=200)

if st.button("🔍 วิเคราะห์รีวิว"):
    if not review_input.strip():
        st.warning("กรุณาใส่ข้อความรีวิวก่อนกดวิเคราะห์")
    else:
        # กำหนดคำค้นหาข้อดี / ข้อเสีย / สัญญาณรีวิวปลอม
        positive_keywords = ["ดี", "ชอบ", "ส่งไว", "คุ้ม", "ตรงปก", "ใช้งานง่าย", "สวย"]
        negative_keywords = ["แย่", "ช้า", "พัง", "ไม่ตรงปก", "แพง", "ห่วย", "ชำรุด"]
        fake_signals = ["ดีมากๆๆๆ", "ส่งไวมากๆๆๆ", "แนะนำร้านนี้", "10/10"]

        lines = review_input.split("\n")
        pros = [line for line in lines if any(k in line for k in positive_keywords)]
        cons = [line for line in lines if any(k in line for k in negative_keywords)]
        
        # คำนวณคะแนนความน่าเชื่อถือแบบคร่าวๆ
        spam_count = sum(1 for k in fake_signals if k in review_input)
        trust_score = max(30, 100 - (spam_count * 20))

        st.subheader("🛡️ คะแนนความน่าเชื่อถือ (Trust Score)")
        st.progress(trust_score / 100)
        st.write(f"คะแนนประเมิน: **{trust_score}%**")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.write("### 🟢 ข้อดีประเมินได้")
            for p in pros:
                st.write(f"- {p}")
            if not pros:
                st.write("- ไม่พบข้อความเชิงบวกชัดเจน")
        with col2:
            st.write("### 🔴 ข้อเสียประเมินได้")
            for c in cons:
                st.write(f"- {c}")
            if not cons:
                st.write("- ไม่พบข้อความเชิงลบชัดเจน")
