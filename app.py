import streamlit as st
import json
import re
from google import genai

# ตั้งค่าหน้าตาเว็บ
st.set_page_config(page_title="AI Consumer Review", page_icon="🛍️")
st.title("🛍️ AI สรุปรีวิวสินค้า & ตรวจจับรีวิวปลอม")

# แถบข้างสำหรับใส่ API Key
api_key = st.sidebar.text_input("กรอก Gemini API Key:", type="password")
review_input = st.text_area("วางข้อความรีวิวสินค้าที่ต้องการวิเคราะห์ที่นี่:", height=200)

if st.button("🔍 วิเคราะห์รีวิว"):
    if not api_key:
        st.error("กรุณากรอก Gemini API Key ที่แถบด้านข้างก่อนครับ")
    elif not review_input.strip():
        st.warning("กรุณากรอกข้อความรีวิวก่อนกดวิเคราะห์")
    else:
        with st.spinner("AI กำลังวิเคราะห์..."):
            try:
                # เรียกใช้ Google GenAI SDK
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                คุณคือ AI ผู้เชี่ยวชาญด้านการวิเคราะห์รีวิวสินค้า จงวิเคราะห์ข้อความต่อไปนี้:
                <reviews>
                {review_input}
                </reviews>

                ตอบกลับเป็นรูปแบบ JSON โครงสร้างนี้เท่านั้น:
                {{
                  "trust_score": 85,
                  "fake_warning": "ข้อสังเกตรีวิวปลอม (ถ้าไม่มีใส่ 'ไม่พบสัญญาณรีวิวปลอม')",
                  "pros": ["ข้อดี 1", "ข้อดี 2", "ข้อดี 3"],
                  "cons": ["ข้อเสีย 1", "ข้อเสีย 2", "ข้อเสีย 3"]
                }}
                """

                # ส่งคำสั่งประมวลผลไปยังโมเดล
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )

                # ดึง JSON ออกจากคำตอบของ AI
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))

                    # แสดงคะแนนความน่าเชื่อถือ
                    score = data.get("trust_score", 0)
                    st.subheader("🛡️ คะแนนความน่าเชื่อถือ (Trust Score)")
                    st.progress(score / 100)
                    st.write(f"ความน่าเชื่อถือ: **{score}%** — {data.get('fake_warning')}")
                    st.divider()

                    # แสดงข้อดี-ข้อเสีย
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### 🟢 ข้อดี (Pros)")
                        for pro in data.get("pros", []):
                            st.write(f"- {pro}")
                    with col2:
                        st.write("### 🔴 ข้อเสีย (Cons)")
                        for con in data.get("cons", []):
                            st.write(f"- {con}")

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")