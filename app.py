from flask import Flask, request, render_template_string, redirect, url_for, session
import joblib
from urllib.parse import urlparse
import ipaddress
import re
import socket

from cao import TitleScraper
from underthesea import word_tokenize


app = Flask(__name__)
# Khóa bí mật đơn giản để dùng session (flash dữ liệu kết quả 1 lần)
app.secret_key = "change-this-to-a-random-secret-key"

# ----- Cấu hình Threshold -----
# Threshold: Ngưỡng xác suất để chọn nhãn (0.0 - 1.0)
# - Giá trị thấp (0.1-0.2): Chọn nhiều nhãn hơn, dễ bị dự đoán sai
# - Giá trị cao (0.4-0.6): Chọn ít nhãn hơn, chính xác hơn nhưng có thể bỏ sót
# - Giá trị rất cao (>0.7): Chỉ chọn nhãn rất chắc chắn, có thể không có nhãn nào được chọn
THRESHOLD = 0.3  

# ----- Load models -----
MODEL_NB_PATH = "model_phanloai_drama_nb.pkl"  # Naive Bayes model
MODEL_RNN_PATH = "model_phanloai_drama_rnn.pkl"  # RNN model 
# Load Naive Bayes model
model_nb = None
mlb_nb = None
categories_nb = []
try:
    model_nb, mlb_nb = joblib.load(MODEL_NB_PATH)
    categories_nb = mlb_nb.classes_
    print(f"✅ Đã load Naive Bayes model: {MODEL_NB_PATH}")
except Exception as e:
    print(f"⚠️  Không load được Naive Bayes model từ '{MODEL_NB_PATH}': {e}")

# Load RNN model
model_rnn = None
mlb_rnn = None
categories_rnn = []
try:
    model_rnn, mlb_rnn = joblib.load(MODEL_RNN_PATH)
    categories_rnn = mlb_rnn.classes_
    print(f"✅ Đã load RNN model: {MODEL_RNN_PATH}")
except Exception as e:
    print(f"⚠️  Không load được RNN model từ '{MODEL_RNN_PATH}': {e} (có thể chưa train)")


# ----- Tiền xử lý giống khi train -----
def preprocess_drama(text: str) -> str:
    tokens = word_tokenize(text.lower(), format="text")
    return tokens


def _format_scraper_error(msg: str) -> str:
    """
    Rút gọn message lỗi trả về từ TitleScraper để hiển thị đẹp trên web.

    Ví dụ:
    - "Lỗi: HTTPError 404: 404 Client Error: Not Found for url: https://..."
      -> "Not Found for url: https://..."
    - "Lỗi: SSLError: <chi tiết>" -> "SSLError: <chi tiết>"
    """
    if not msg:
        return "Lỗi: Không rõ lý do."

    text = msg.strip()

    # Nếu là HTTPError có đoạn "Client Error:" thì chỉ lấy phần sau đó,
    # và thêm tiền tố "Lỗi: " cho rõ ràng.
    marker = "Client Error:"
    if marker in text:
        try:
            _, after = text.split(marker, 1)
            after = after.strip()
            if after:
                return f"Lỗi: {after}"
        except ValueError:
            pass

    # Ngược lại giữ nguyên thông báo gốc
    return text

_HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")


def normalize_and_validate_public_url(raw_url: str) -> tuple[str | None, str | None]:
    """
    Normalize + validate URL để dùng được trên Internet công cộng.

    Trả về: (url_đã_chuẩn_hoá, lỗi). Nếu hợp lệ thì lỗi = None.
    """
    url = (raw_url or "").strip()
    if not url:
        return None, "Vui lòng nhập URL bài báo."

    parsed = urlparse(url)

    # Nếu người dùng quên http/https, tự thêm để tiện lợi
    if not parsed.scheme:
        url = "http://" + url
        parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None, "URL không hợp lệ: chỉ hỗ trợ http/https."

    if not parsed.netloc:
        return None, "URL không hợp lệ: thiếu tên miền (domain)."

    host = parsed.hostname
    if not host:
        return None, "URL không hợp lệ: không đọc được hostname."

    host = host.strip().lower()

    # Chặn localhost / host nội bộ phổ biến
    if host in ("localhost",):
        return None, "URL không hợp lệ: hostname 'localhost' không dùng được trên Internet công cộng."
    if host.endswith(".local"):
        return None, "URL không hợp lệ: domain '.local' là domain nội bộ, không dùng trên Internet công cộng."

    # Host phải có ký tự hợp lệ
    if not _HOST_RE.match(host):
        return None, "URL không hợp lệ: hostname chứa ký tự không hợp lệ."

    # Nếu là IP thì phải là public IP
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            return None, "URL không hợp lệ: IP không phải public (private/loopback/link-local)."
        return url, None
    except ValueError:
        pass  # không phải IP -> tiếp tục check domain

    # Domain công cộng thường phải có dấu chấm (vd: vnexpress.net)
    if "." not in host:
        return None, "URL không hợp lệ: domain phải có dạng public (ví dụ: vnexpress.net)."

    # Thử resolve DNS để biết domain có tồn tại công khai hay không
    try:
        socket.setdefaulttimeout(3.0)
        addrinfos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return None, "URL không hợp lệ: không phân giải được DNS (domain không tồn tại hoặc không truy cập được)."
    except Exception as e:
        return None, f"URL không hợp lệ: lỗi khi kiểm tra DNS ({type(e).__name__}: {e})."

    # Nếu resolve ra toàn IP private/loopback -> coi như không public
    resolved_ips = []
    for info in addrinfos:
        try:
            resolved_ips.append(info[4][0])
        except Exception:
            continue

    if resolved_ips:
        any_global = False
        for ip_s in set(resolved_ips):
            try:
                if ipaddress.ip_address(ip_s).is_global:
                    any_global = True
                    break
            except Exception:
                continue
        if not any_global:
            return None, "URL không hợp lệ: domain resolve về IP không public."

    return url, None


# ----- Web template đơn giản -----
PAGE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Phân loại bài báo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: radial-gradient(circle at top left, #1e3a8a 0%, #2563eb 40%, #0ea5e9 75%, #e0f2fe 100%);
            min-height: 100vh;
            padding: 24px;
            color: #0b2c5f;
        }

        .container {
            max-width: 760px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.97);
            padding: 40px 44px;
            border-radius: 26px;
            box-shadow: 0 24px 70px rgba(37, 99, 235, 0.35);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(191, 219, 254, 0.9);
        }

        h1 {
            margin-bottom: 8px;
            text-align: center;
            color: #0f172a;
            font-size: 32px;
            font-weight: 750;
            letter-spacing: -0.04em;
        }

        form {
            margin-top: 25px;
        }

        label {
            font-weight: 600;
            color: #0f172a;
            display: block;
            margin-bottom: 10px;
            font-size: 15px;
        }

        input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            margin-bottom: 18px;
            border-radius: 14px;
            border: 2px solid #bfdbfe;
            font-size: 15px;
            background: #eff6ff;
            color: #0f172a;
            transition: all 0.25s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #2563eb;
            background: #ffffff;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.18);
        }

        input[type="text"]::placeholder {
            color: #93c5fd;
        }

        /* Áp dụng style chung cho cả select và input threshold */
        select,
        input[type="number"] {
            width: 100%;
            padding: 12px 14px;
            margin-bottom: 18px;
            border-radius: 12px;
            border: 2px solid #bfdbfe;
            font-size: 15px;
            background: #eff6ff;
            color: #0f172a;
            transition: all 0.25s ease;
            cursor: pointer;
        }

        select:focus,
        input[type="number"]:focus {
            outline: none;
            border-color: #2563eb;
            background: #ffffff;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.18);
        }

        button {
            width: 100%;
            padding: 14px 24px;
            background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
            border: none;
            border-radius: 999px;
            color: #f9fafb;
            font-weight: 700;
            cursor: pointer;
            font-size: 15px;
            transition: all 0.25s ease;
            box-shadow: 0 10px 28px rgba(37, 99, 235, 0.55);
        }

        button:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%);
            transform: translateY(-2px);
            box-shadow: 0 14px 36px rgba(37, 99, 235, 0.7);
        }

        button:active {
            transform: translateY(0);
            box-shadow: 0 6px 15px rgba(13, 154, 143, 0.3);
        }

        .result {
            margin-top: 30px;
            padding: 24px;
            border-radius: 18px;
            background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
            border: 2px solid #bfdbfe;
            animation: slideIn 0.4s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .error {
            margin-top: 20px;
            padding: 16px 20px;
            border-radius: 14px;
            background: #fef2f2;
            border: 2px solid #fecaca;
            color: #b91c1c;
            font-weight: 600;
            line-height: 1.6;
            box-shadow: 0 10px 24px rgba(248, 113, 113, 0.35);
            overflow-wrap: anywhere;
            word-break: break-word;
            animation: slideIn 0.4s ease;
        }

        .tag-pill {
            display: inline-block;
            padding: 8px 16px;
            margin: 6px 8px 6px 0;
            border-radius: 20px;
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            color: #1d4ed8;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
            transition: all 0.3s ease;
        }

        .tag-pill:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.3);
        }

        .title {
            font-weight: 700;
            color: #0d7a73;
            margin-bottom: 10px;
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        small {
            color: #7ab5ad;
            font-size: 12px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            padding: 12px 14px;
            border-bottom: 1px solid #b3e5de;
            text-align: left;
            font-size: 14px;
        }

        th {
            background: linear-gradient(135deg, #d4f1f4 0%, #c8ebf0 100%);
            font-weight: 700;
            color: #0d7a73;
        }

        td {
            color: #1a5f5a;
        }

        tr:hover {
            background: rgba(13, 154, 143, 0.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Phân loại bài báo</h1>
        <form method="post">
            <label for="url">Nhập đường link bài báo:</label>
            <input type="text" id="url" name="url" placeholder="https://..." value="{{ url or '' }}" required>

            <label for="model_type" style="margin-top: 8px;">Chọn model:</label>
            <select id="model_type" name="model_type" required>
                <option value="nb" {% if model_type == 'nb' or not model_type %}selected{% endif %}>
                    Naive Bayes {% if not model_nb_available %}(Không có sẵn){% endif %}
                </option>
                <option value="rnn" {% if model_type == 'rnn' %}selected{% endif %}>
                    RNN {% if not model_rnn_available %}(Không có sẵn){% endif %}
                </option>
            </select>

            <label for="threshold" style="margin-top: 8px;">Ngưỡng xác suất (threshold) để chọn nhãn (%):</label>
            <input
                type="number"
                id="threshold"
                name="threshold"
                min="1"
                max="99"
                step="1"
                value="{{ threshold_percent or 30 }}"
            >

            <button type="submit">Phân loại</button>
        </form>

        {% if error %}
            <div class="error">{{ error|safe }}</div>
        {% endif %}

        {% if title %}
            <div class="result">
                <div class="title">Tiêu đề lấy được:</div>
                <div>{{ title }}</div>
                {% if model_type %}
                    <div style="margin-top: 8px; font-size: 13px; color: #6b7280;">
                        <strong>Model sử dụng:</strong> {{ 'RNN' if model_type == 'rnn' else 'Naive Bayes' }}
                    </div>
                {% endif %}
                {% if labels %}
                    <div style="margin-top: 12px;">
                        <div class="title">Chủ đề dự đoán:</div>
                        {% for t in labels %}
                            <span class="tag-pill">{{ t }}</span>
                        {% endfor %}
                    </div>
                {% endif %}
                {% if prob_table %}
                    <div style="margin-top: 12px;">
                        <div class="title">Xác suất dự đoán:</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Nhãn</th>
                                    <th>Xác suất</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in prob_table %}
                                    <tr>
                                        <td>{{ row.label }}</td>
                                        <td>{{ row.prob }}%</td>
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


scraper = TitleScraper()


@app.route("/", methods=["GET", "POST"])
def index():
    # Mặc định các giá trị rỗng
    error = None
    title = None
    labels = None
    prob_table = None
    url_display = ""  # luôn reset ô input sau khi submit / reload
    threshold_percent = None  # giá trị hiển thị lại trên form
    model_type = "nb"  # mặc định chọn Naive Bayes

    if request.method == "POST":
        raw_url = request.form.get("url", "")
        raw_threshold = request.form.get("threshold", "").strip()
        model_type = request.form.get("model_type", "nb").strip().lower()

        # Xử lý threshold người dùng nhập (theo %)
        used_threshold = THRESHOLD
        if raw_threshold:
            try:
                tp = float(raw_threshold)
                # Giới hạn hợp lý 1% - 99%
                if 1 <= tp <= 99:
                    used_threshold = tp / 100.0
                    threshold_percent = tp
            except ValueError:
                # Nếu nhập không đúng số thì giữ nguyên THRESHOLD mặc định
                pass

        # Chọn model dựa trên lựa chọn của người dùng
        selected_model = None
        selected_mlb = None
        selected_categories = []
        
        if model_type == "nb":
            selected_model = model_nb
            selected_mlb = mlb_nb
            selected_categories = categories_nb
            if not selected_model or not selected_mlb:
                error = "Model Naive Bayes chưa được load. Hãy chắc chắn đã train và lưu model_phanloai_drama_nb.pkl."
        elif model_type == "rnn":
            selected_model = model_rnn
            selected_mlb = mlb_rnn
            selected_categories = categories_rnn
            if not selected_model or not selected_mlb:
                error = "Model RNN chưa được load. Hãy chắc chắn đã train và lưu model_phanloai_drama_rnn.pkl."
        else:
            error = f"Loại model không hợp lệ: {model_type}"

        url, url_error = normalize_and_validate_public_url(raw_url)
        if url_error:
            error = url_error

        # 3. Cào tiêu đề nếu mọi thứ hợp lệ
        if not error:
            title = scraper.get_title(url)

            if title.startswith("Lỗi"):
                reason = _format_scraper_error(title)
                error = f"Không thể lấy tiêu đề từ URL:<br>{reason}"
                title = None
            elif title == "Không tìm thấy tiêu đề":
                error = "Không tìm thấy tiêu đề trong trang này. Vui lòng kiểm tra lại link hoặc thử link khác."
                title = None

        # 4. Nếu không có lỗi thì tiến hành phân loại
        if not error and title and selected_model:
            processed = preprocess_drama(title)
            
            # Dự đoán với model đã chọn
            try:
                proba = selected_model.predict_proba([processed])[0]
            except Exception as e:
                error = f"Lỗi khi dự đoán với model {model_type.upper()}: {str(e)}"
                title = None
                proba = None

            if proba is not None:
                # Sử dụng threshold đã cấu hình (mặc định hoặc người dùng nhập)
                chosen_indices = [i for i, p in enumerate(proba) if p >= used_threshold]
                if not chosen_indices:
                    chosen_indices = [int(proba.argmax())]

                labels = [selected_categories[i] for i in chosen_indices]
                prob_table = [
                    {
                        "label": selected_categories[i],
                        "prob": round(float(proba[i] * 100), 2),
                    }
                    for i in chosen_indices
                ]

        # Lưu kết quả 1 lần vào session và redirect (Post-Redirect-Get)
        session["last_result"] = {
            "error": error,
            "title": title,
            "labels": labels,
            "prob_table": prob_table,
            "model_type": model_type,
            "threshold_percent": threshold_percent,
        }
        return redirect(url_for("index"))

    # GET: lấy kết quả từ session (nếu có) rồi xóa, để reload là trang trống
    data = session.pop("last_result", None) or {}
    error = data.get("error")
    title = data.get("title")
    labels = data.get("labels")
    prob_table = data.get("prob_table")
    model_type = data.get("model_type", "nb")
    threshold_percent = data.get("threshold_percent")

    # Kiểm tra model có sẵn để hiển thị trên dropdown
    model_nb_available = model_nb is not None and mlb_nb is not None
    model_rnn_available = model_rnn is not None and mlb_rnn is not None

    return render_template_string(
        PAGE_HTML,
        error=error,
        url=url_display,
        threshold_percent=threshold_percent,
        model_type=model_type,
        model_nb_available=model_nb_available,
        model_rnn_available=model_rnn_available,
        title=title,
        labels=labels,
        prob_table=prob_table,
    )


if __name__ == "__main__":
    # Chạy trên localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)