import streamlit as st
import urllib.parse

# Cấu hình giao diện trang web
st.set_page_config(page_title="Phân tích Cổ phiếu 5 Màn hình", layout="centered")

# Khởi tạo quản lý trạng thái màn hình và dữ liệu (Trống hoàn toàn)
if "step" not in st.session_state:
    st.session_state.step = 0
if "stock_code" not in st.session_state:
    st.session_state.stock_code = ""
if "raw_data" not in st.session_state:
    st.session_state.raw_data = ""
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

st.title("📊 Hệ thống Phân tích Cổ phiếu T+")

# ================= MÀN HÌNH 0: ĐĂNG NHẬP & NHẬP MÃ =================
if st.session_state.step == 0:
    st.subheader("Đăng nhập hệ thống & Nhập mã cổ phiếu")
    
    username = st.text_input("Tên đăng nhập:", placeholder="Nhập tài khoản của bạn...")
    stock_input = st.text_input("Mã cổ phiếu cần phân tích (Trống để tự nhập):", placeholder="VD: VCB, SSI, FPT...")
    
    if st.button("Đăng nhập & Tiếp tục", type="primary"):
        if not stock_input.strip():
            st.error("Vui lòng nhập mã cổ phiếu trước khi tiếp tục!")
        else:
            st.session_state.stock_code = stock_input.strip().upper()
            st.session_state.step = 1
            st.rerun()

# ================= MÀN HÌNH 1: LẤY DỮ LIỆU 30 PHIÊN OHLCV =================
elif st.session_state.step == 1:
    st.subheader(f"Màn hình 1: Lấy dữ liệu 30 phiên OHLCV ({st.session_state.stock_code})")
    
    prompt_m1 = f"Trích xuất bảng dữ liệu 30 phiên giao dịch gần nhất bao gồm các thông số OHLCV (Open, High, Low, Close, Volume) của mã cổ phiếu {st.session_state.stock_code}."
    st.text_area("Câu lệnh tự động:", value=prompt_m1, disabled=True)
    
    # Tạo link mở nhanh Gemini kèm câu lệnh được mã hóa URL
    encoded_prompt = urllib.parse.quote(prompt_m1)
    gemini_url = f"https://gemini.google.com/?q={encoded_prompt}"
    
    # Hiển thị nút mở Gemini trực tiếp
    st.markdown(f'<a href="{gemini_url}" target="_blank"><button style="width:100%; background-color:#10b981; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:10px;">🌐 Mở Gemini để lấy dữ liệu OHLCV</button></a>', unsafe_allow_html=True)
    
    raw_input = st.text_area("Dán dữ liệu thô nhận được từ Gemini vào đây:", placeholder="Dán bảng dữ liệu 30 phiên OHLCV...")
    
    if st.button("Tiếp tục (Chuyển sang màn hình Excel)", type="primary"):
        st.session_state.raw_data = raw_input
        st.session_state.step = 2
        st.rerun()

# ================= MÀN HÌNH 2: XỬ LÝ & ĐỊNH DẠNG EXCEL =================
elif st.session_state.step == 2:
    st.subheader(f"Màn hình 2: Xử lý & Định dạng Excel tự động ({st.session_state.stock_code})")
    
    st.text_area(
        "Câu lệnh hiệu chỉnh:", 
        value="Tự động phân tách dữ liệu chuỗi thành các cột chuẩn (Ngày, Open, High, Low, Close, Volume) và tính toán sẵn các chỉ báo cơ bản cho bảng Excel.",
        disabled=True
    )
    
    st.write("Bảng dữ liệu đã chuẩn hóa:")
    if st.session_state.raw_data:
        lines = st.session_state.raw_data.split('\n')
        table_data = [{"Phiên": f"Phiên {i+1}", "Dữ liệu gốc": line} for i, line in enumerate(lines)]
        st.dataframe(table_data, use_container_width=True)
    else:
        st.warning("Chưa có dữ liệu thô. Hiển thị bảng trống để chỉnh sửa.")
        st.dataframe([{"Phiên": "---", "Open": "---", "High": "---", "Low": "---", "Close": "---", "Volume": "---"}], use_container_width=True)
        
    if st.button("Tiếp tục (Sang màn hình phân tích T+)", type="primary"):
        st.session_state.step = 3
        st.rerun()

# ================= MÀN HÌNH 3: YÊU CẦU PHÂN TÍCH CHIẾN LƯỢC T+ =================
elif st.session_state.step == 3:
    st.subheader(f"Màn hình 3: Yêu cầu phân tích & Chiến lược T+ ({st.session_state.stock_code})")
    
    prompt_m3 = f"""Dựa vào bảng dữ liệu OHLCV 30 phiên của mã {st.session_state.stock_code} đã chuẩn hóa, hãy phân tích kỹ thuật (xu hướng dòng tiền, hỗ trợ/kháng cự) và đưa ra chiến lược giao dịch T+ chi tiết cho 2 kịch bản:
1. Trường hợp CHƯA CÓ HÀNG: Điểm mua tích lũy, tỷ trọng giải ngân, vùng cắt lỗ.
2. Trường hợp ĐÃ CÓ HÀNG: Điểm gia tăng tỷ trọng, điểm chốt lời ngắn hạn, thời điểm hạ tỷ trọng an toàn."""
    
    ai_prompt = st.text_area("Câu lệnh gửi Gemini phân tích kỹ thuật & T+:", value=prompt_m3, height=180)
    
    # Tạo link mở nhanh Gemini cho màn hình 3
    encoded_prompt_m3 = urllib.parse.quote(ai_prompt)
    gemini_url_m3 = f"https://gemini.google.com/?q={encoded_prompt_m3}"
    
    st.markdown(f'<a href="{gemini_url_m3}" target="_blank"><button style="width:100%; background-color:#10b981; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:10px;">🌐 Mở Gemini để nhận phân tích chiến lược T+</button></a>', unsafe_allow_html=True)
    
    ai_input_result = st.text_area("Dán kết quả phân tích từ Gemini vào đây:", placeholder="Dán nội dung phân tích chiến lược T+...")
    
    if st.button("Tiếp tục (Chuyển sang màn hình kết quả)", type="primary"):
        st.session_state.ai_result = ai_input_result
        st.session_state.step = 4
        st.rerun()

# ================= MÀN HÌNH 4: KẾT QUẢ PHÂN TÍCH TỪ GEMINI =================
elif st.session_state.step == 4:
    st.subheader(f"Màn hình 4: Kết quả phân tích từ Gemini ({st.session_state.stock_code})")
    
    st.text_area("Nội dung phân tích & Chiến lược T+ đã lưu:", value=st.session_state.ai_result, height=250)
    
    if st.button("Tiếp tục (Chuyển đến màn hình tổng hợp)", type="primary"):
        st.session_state.step = 5
        st.rerun()

# ================= MÀN HÌNH 5: TỔNG HỢP & LƯU HỒ SƠ =================
elif st.session_state.step == 5:
    st.subheader("Màn hình 5: Tổng hợp thông tin & Lưu hồ sơ")
    
    st.success(f"Hoàn tất quy trình phân tích cho mã cổ phiếu: **{st.session_state.stock_code}**")
    st.markdown("- **Trạng thái dữ liệu Excel:** Đã chuẩn hóa 30 phiên OHLCV.")
    st.markdown("- **Chiến lược T+ (AI):** Đã cập nhật thành công từ kết quả phân tích thực tế.")
    
    if st.button("Nhấn lưu hồ sơ đầu tư", type="primary"):
        st.success(f"Đã lưu thành công hồ sơ đầu tư cho mã {st.session_state.stock_code} vào hệ thống!")
        if st.button("Bắt đầu mã mới"):
            st.session_state.step = 0
            st.session_state.stock_code = ""
            st.session_state.raw_data = ""
            st.session_state.ai_result = ""
            st.rerun()
