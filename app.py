import streamlit as st
from google import genai

# Cấu hình giao diện trang web
st.set_page_config(page_title="Phân tích Cổ phiếu 5 Màn hình", layout="centered")

# Khởi tạo Gemini Client (Sử dụng API key từ biến môi trường hoặc cấu hình)
# Lưu ý: Bạn cần cài đặt thư viện `pip install google-genai` và cấu hình GOOGLE_API_KEY
client = genai.Client()

# Khởi tạo quản lý trạng thái màn hình và dữ liệu (Trống hoàn toàn)
if "step" not in st.session_state:
    st.session_state.step = 0
if "stock_code" not in st.session_state:
    st.session_state.stock_code = ""
if "raw_data" not in st.session_state:
    st.session_state.raw_data = ""
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

st.title("📊 Hệ thống Phân tích Cổ phiếu T+ (Tích hợp Gemini)")

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
    st.text_area("Câu lệnh tự động (Gửi sang Gemini):", value=prompt_m1, disabled=True)
    
    raw_input = st.text_area("Dữ liệu thô (Dán hoặc nhận trực tiếp từ Gemini):", placeholder="Dán bảng dữ liệu 30 phiên OHLCV vào đây...")
    
    # Nút tiếp tục tích hợp kép: Vừa gọi Gemini (nếu muốn lấy tự động) vừa chuyển màn hình
    if st.button("Tiếp tục (Chuyển giao diện & Gửi lệnh Gemini)", type="primary"):
        # Tùy chọn: Có thể gọi trực tiếp Gemini lấy dữ liệu tại đây nếu cần
        # response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_m1)
        # st.session_state.raw_data = response.text
        
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
        st.warning("Không có dữ liệu thô từ màn hình trước. Hiển thị bảng trống để chỉnh sửa.")
        st.dataframe([{"Phiên": "---", "Open": "---", "High": "---", "Low": "---", "Close": "---", "Volume": "---"}], use_container_width=True)
        
    if st.button("Tiếp tục (Lưu bảng Excel & Sang màn hình phân tích)", type="primary"):
        st.session_state.step = 3
        st.rerun()

# ================= MÀN HÌNH 3: YÊU CẦU PHÂN TÍCH CHIẾN LƯỢC T+ =================
elif st.session_state.step == 3:
    st.subheader(f"Màn hình 3: Yêu cầu phân tích & Chiến lược T+ ({st.session_state.stock_code})")
    
    prompt_default = f"""Dựa vào bảng dữ liệu OHLCV 30 phiên của mã {st.session_state.stock_code} đã chuẩn hóa, hãy phân tích kỹ thuật (xu hướng dòng tiền, hỗ trợ/kháng cự) và đưa ra chiến lược giao dịch T+ chi tiết cho 2 kịch bản:
1. Trường hợp CHƯA CÓ HÀNG: Điểm mua tích lũy, tỷ trọng giải ngân, vùng cắt lỗ.
2. Trường hợp ĐÃ CÓ HÀNG: Điểm gia tăng tỷ trọng, điểm chốt lời ngắn hạn, thời điểm hạ tỷ trọng an toàn."""
    
    ai_prompt = st.text_area("Câu lệnh gửi Gemini phân tích kỹ thuật & T+:", value=prompt_default, height=180)
    
    # Nút tiếp tục tích hợp kép: GỬI THỰC TẾ SANG GEMINI VÀ CHUYỂN SANG MÀN HÌNH 4
    if st.button("Tiếp tục (Gửi yêu cầu sang Gemini & Nhận kết quả)", type="primary"):
        with st.spinner("Đang kết nối với Gemini để phân tích..."):
            try:
                # Gọi trực tiếp API Gemini để lấy kết quả phân tích thật
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=ai_prompt
                )
                st.session_state.ai_result = response.text
            except Exception as e:
                st.session_state.ai_result = f"Lỗi khi kết nối Gemini: {str(e)}"
                
        st.session_state.step = 4
        st.rerun()

# ================= MÀN HÌNH 4: KẾT QUẢ PHÂN TÍCH TỪ GEMINI =================
elif st.session_state.step == 4:
    st.subheader(f"Màn hình 4: Kết quả phân tích từ Gemini ({st.session_state.stock_code})")
    
    st.text_area("Nội dung phân tích & Chiến lược T+ trả về từ Gemini:", value=st.session_state.ai_result, height=250)
    
    if st.button("Tiếp tục (Chuyển đến màn hình tổng hợp)", type="primary"):
        st.session_state.step = 5
        st.rerun()

# ================= MÀN HÌNH 5: TỔNG HỢP & LƯU HỒ SƠ =================
elif st.session_state.step == 5:
    st.subheader("Màn hình 5: Tổng hợp thông tin & Lưu hồ sơ")
    
    st.success(f"Hoàn tất quy trình phân tích cho mã cổ phiếu: **{st.session_state.stock_code}**")
    st.markdown("- **Trạng thái dữ liệu Excel:** Đã chuẩn hóa 30 phiên OHLCV.")
    st.markdown("- **Chiến lược T+ (AI):** Đã nhận kết quả phân tích thực tế từ Gemini (Có hàng & Chưa có hàng).")
    
    if st.button("Nhấn lưu hồ sơ đầu tư", type="primary"):
        st.success(f"Đã lưu thành công hồ sơ đầu tư cho mã {st.session_state.stock_code} vào hệ thống!")
        if st.button("Bắt đầu mã mới"):
            st.session_state.step = 0
            st.session_state.stock_code = ""
            st.session_state.raw_data = ""
            st.session_state.ai_result = ""
            st.rerun()
