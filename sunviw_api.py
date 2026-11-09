# -*- coding: utf-8 -*-
"""
SUNVIW - API JSON.  SUN: 13 LOGIC DỰ ĐOÁN (SEQ13v6) dựa trên CHUỖI TÀI/XỈU + XÚC XẮC + TỔNG gần nhất (KHÔNG dùng MD5) · HITCLUB: 2 bàn (TX thường + TX MD5) dùng cùng bộ 13 logic

Chạy:
    pip install flask
    python sunviw_api.py                      # mặc định http://0.0.0.0:5000
    python sunviw_api.py --port 8080 --upstream https://xxx.trycloudflare.com/api/tx
    python sunviw_api.py --flip               # BẬT bẻ final của SUN (mặc định TẮT; hoặc SUNVIW_FLIP=1, hoặc sửa FLIP_FINAL_DEFAULT)
    python sunviw_api.py --wr-flip            # BẬT FLIP TRỌNG SỐ WR của SUN: ván CŨ nhất nặng nhất -> giảm dần tới ván MỚI nhất (--no-wr-flip = tắt; hoặc SUNVIW_WR_FLIP=1|0, hoặc sửa WR_FLIP_WEIGHT_DEFAULT)
    python sunviw_api.py --no-af              # TẮT AF của SUN (--af = bật · --af-low 37 / --af-high 63 = ngưỡng bẻ logic · --af-min 13 = số ván tối thiểu · --af-mode-window 7 / --af-mode-below 45 = bẻ theo WR chế độ · --af-flip / --af-no-flip = bẻ riêng AF)
                                              #           hoặc env SUNVIW_AF / SUNVIW_AF_LOW / SUNVIW_AF_HIGH / SUNVIW_AF_MIN / SUNVIW_AF_MODE_WINDOW / SUNVIW_AF_MODE_MIN / SUNVIW_AF_MODE_BELOW / SUNVIW_AF_MODE_FLIP (bước 3 bẻ chế độ, mặc định TẮT · --af-mode-flip / --af-no-mode-flip) / SUNVIW_AF_FLIP, hoặc sửa AF_*_DEFAULT ở khối "CONFIG AF"
    python sunviw_api.py --af-flip-ct         # CHỈ bẻ final của AF khi chế độ CAO/THẤP (chế độ ALL giữ nguyên; --af-no-flip-ct = tắt; hoặc SUNVIW_AF_FLIP_CT=1|0, hoặc sửa AF_FLIP_FINAL_CT_DEFAULT)
    python sunviw_api.py --af-flip-cao        # CHỈ bẻ final của AF khi chế độ CAO (THẤP + ALL giữ nguyên; --af-no-flip-cao = tắt; hoặc SUNVIW_AF_FLIP_CAO=1|0, hoặc sửa AF_FLIP_FINAL_CAO_DEFAULT)
    python sunviw_api.py --af-flip-thap       # CHỈ bẻ final của AF khi chế độ THẤP (CAO + ALL giữ nguyên; --af-no-flip-thap = tắt; hoặc SUNVIW_AF_FLIP_THAP=1|0, hoặc sửa AF_FLIP_FINAL_THAP_DEFAULT)
                                              #   ⇒ TÁCH RIÊNG: vd theo final CAO nhưng bẻ final THẤP  =  --af-flip-thap (không bật --af-flip-cao). --af-flip-ct = bật CẢ CAO + THẤP (giữ như cũ)
    python sunviw_api.py --af-flip-all        # CHỈ bẻ final của AF khi chế độ ALL (CAO/THẤP giữ nguyên; --af-no-flip-all = tắt; hoặc SUNVIW_AF_FLIP_ALL=1|0, hoặc sửa AF_FLIP_FINAL_ALL_DEFAULT)

Endpoint:
    GET /api/predictsun          -> [SUN] JSON dự đoán (đọc từ cache, trả về ngay). /api/predict = tên cũ, giữ để tool cũ không hỏng
    GET /api/predictsun?detail=1 -> thêm chi_tiet: vote từng logic + WR từng logic
    GET /api/predicthittxthuong  -> [HITCLUB · bàn TX THƯỜNG] JSON dự đoán, cùng cấu trúc /api/predictsun (game="hitclub", ban="hittxthuong"); cũng có ?hist=N · ?detail=1
    GET /api/predicthittxmd5     -> [HITCLUB · bàn TX MD5] như trên (ban="hittxmd5")
    ...?hist=N                   -> (mọi game) thêm lich_su: N ván đúng/sai gần nhất, mới -> cũ
    GET /api/predictlcmd5        -> [LC MD5] JSON dự đoán (game="lc79", ban="lcmd5"; tên cũ Tele68 MD5 — /api/predicttele68txmd5 vẫn chạy như alias); nguồn trả CẢ DANH SÁCH ~105 phiên, tool chỉ lưu thêm phiên chưa có, dự đoán phiên mới nhất + 1 và giữ tới khi API trả kết quả phiên đó (xem khối "CONFIG LC")
    GET /api/predictlchu         -> [LC HŨ] JSON dự đoán (game="lc79", ban="lchu"); nguồn https://wtx.tele68.com/v1/tx/sessions (cùng định dạng list với LC MD5), config + data RIÊNG (khối "CONFIG LC"). Key game LC79 dùng được cả 2 bàn LC
    GET /tool/autocuoc           -> [AUTO CƯỢC LC79] trang web điều khiển auto cược + auto rút (thay bot Telegram): đăng nhập LC79, bật/tắt từng luật (x2 thắng/thua, giảm cược, pause, mục tiêu lãi, tự rút Momo/Ngân hàng), biểu đồ lãi/lỗ. GIAO DIỆN BỊ ẨN: chỉ có ô nhập KEY AUTO CƯỢC LC (game "autolc", tiền tố AUTOLC-, tạo ở /api/admin); nhập đúng key mới nhận được giao diện, và MỖI request /tool/autocuoc/api/* (kể cả nhận dự đoán) đều phải kèm X-User-Key + X-HWID. Mỗi key chỉ thấy tài khoản LC79 của mình; key hết hạn -> phiên auto cược tự dừng. Chạy gunicorn --workers 1 (xem khối "AUTO CƯỢC LC79")
    GET /api/html                -> panel HTML theo dõi Sun + Hit, đổi qua lại, chọn số ván lịch sử. CHỈ MỞ KHI ADMIN CHÍNH DUYỆT THIẾT BỊ (HWID): máy lạ thấy bảng "Đang chờ admin duyệt", được duyệt thì tự mở, KHÔNG cần key, vào cả Sun + Hit
    GET /api/panel/status        -> panel hỏi trạng thái duyệt của thiết bị này (gửi yêu cầu lần đầu): {"status": "approved" | "pending" | "denied" | "limit"} (xem khối "DUYỆT THIẾT BỊ VÀO PANEL")
    GET /api/admin/panel (+ POST /approve · /deny · /remove · /ban · /unban) -> admin CHÍNH xem + duyệt / từ chối / gỡ quyền / BAN (danh sách đen: chặn cả IP + thiết bị khỏi /api/html, trả 404) thiết bị vào panel (mục "Duyệt thiết bị vào panel HTML" ở trang /api/admin)
    GET|POST /api/admin/offserver -> OFF SERVER (CHỈ admin chính, nút ở trang /api/admin): bật lên thì server + panel HTML vẫn chạy và cập nhật dự đoán bình thường (thiết bị đã duyệt / admin), còn TOOL NGOÀI gọi API dự đoán nhận 503 {"server_off": true} và không có tín hiệu. POST {"off": true|false}. Lưu file, còn sau restart (xem khối "OFF SERVER")
    GET /api/admin/cuocstatus    -> (admin CHÍNH) bảng TOÀN BỘ tài khoản đang / đã dùng auto cược; bấm 1 dòng xem hồ sơ: chiến thuật đã chọn, số dư, tổng lãi/lỗ, thắng/thua, tổng đã cược, log + ván gần nhất; POST /api/admin/cuocstatus/action {id, act: stop|remove}
    GET /health                  -> CÔNG KHAI, chỉ {"ok":true} (healthcheck). Health đầy đủ: GET /api/admin/health (admin chính, header X-Admin-Token)
    GET /api/admin               -> trang quản trị: MỘT ô nhập key, server tự nhận diện admin chính / admin phụ / key người dùng / key không tồn tại — tạo / xóa (tích chọn nhiều key) / xem key, MỌI key gắn HWID thiết bị (1 key dùng được N thiết bị), hiện lần dùng gần nhất, KHÔNG hiện ở trang chủ (xem khối "CONFIG KEY / ADMIN")
    POST /api/admin/keys/add-time -> CỘNG GIỜ cho key (nút "+1 giờ" ở trang /api/admin; admin chính + admin phụ): {"key"|"keys":[...], "amount": N, "unit": "hour"|"day"|"week"|"month"} (hoặc "hours": N kiểu cũ) · tối đa 365 ngày mỗi lần · admin phụ chỉ key mình tạo · key hết hạn được tính lại từ bây giờ
    POST /api/key/check          -> tool xác thực + GẮN THIẾT BỊ + KÍCH HOẠT (lần đầu dùng thành công mới bắt đầu tính hạn) cho key người dùng: {"key":"...","hwid":"..."} (hoặc header X-HWID) -> {"ok":true,"het_han":<epoch>,"con_lai_giay":N}
    POST /api/history/clear      -> XÓA LỊCH SỬ DỰ ĐOÁN hiển thị: {"game":"sun"|"hittxthuong"|"hittxmd5"|"hitclub"|"all"} (nút "Xóa lịch sử" ở panel /api/html). CHỈ ẩn lich_su + số liệu đúng/sai đã hiển thị bằng 1 mốc phiên (file riêng),
                                    KHÔNG xóa dữ liệu nào khác và KHÔNG ảnh hưởng các logic / WR / AF dự đoán (xem khối "CONFIG XÓA LỊCH SỬ"; tắt hẳn bằng SUNVIW_HIST_CLEAR=0)
    POST /api/history/wipe       -> XÓA SẠCH data của game: {"game":"sun"|"hittxthuong"|"hittxmd5"|"hitclub"|"lcmd5"|"lchu"|"all","confirm":true} (nút "☠ Xóa data game" ở panel; xóa thật lịch sử xúc xắc + ván đã chấm, không hoàn tác)
    POST /api/history/regrade    -> TÍNH LẠI đúng/sai TOÀN BỘ ván đã lưu theo CONFIG HIỆN TẠI: {"game":"sun"|"hittxthuong"|"hittxmd5"|"hitclub"|"lcmd5"|"lchu"|"all"} (nút "🔄 Tính lại theo config" ở panel /api/html). Giữ nguyên lịch sử, dùng lại votes đã lưu nên không phải đợi ván mới
    GET /api/ips                 -> (CHỈ panel đã duyệt / admin chính; key khách bị 403) DANH SÁCH IP đang dùng + đã từng dùng API (tab "IP" của panel đọc từ đây; có SUNVIW_ADMIN_KEY thì cần header X-Admin-Key hoặc ?key=)

JSON /api/predict:
    {
      "ok": true,
      "phien": 12346,            # phiên được dự đoán (n)
      "du_doan": "TÀI",          # TÀI | XỈU  (mặc định = final của 13 logic SUN; nếu BẬT bẻ final thì = đảo ngược final)
      "be_final": false,         # trạng thái bẻ final đang áp dụng (false = tắt, mặc định)
      "do_tin_cay": 58.4,        # % = trung bình WR CÓ TRỌNG SỐ của các logic đang dùng trong WR_WINDOW ván gần nhất (null nếu chưa chấm ván nào)
                                 #     trọng số: ván mới nhất = WR_WEIGHT_NEWEST (cao nhất), ván cũ giảm dần nhưng có sàn WR_FLOOR (xem "CONFIG WR CÓ TRỌNG SỐ")
      "phien_truoc": 12345,      # phiên mới nhất đã có kết quả (n-1)
      "xuc_xac": [3, 5, 4],      # xúc xắc của phien_truoc (dùng để tính dự đoán)
      "tong": 12,                # tổng xúc xắc của phien_truoc
      "ket_qua_truoc": "TÀI",
      "so_van_wr": 9,            # số ván thực tế đã dùng để tính WR / độ tin cậy
      "tool_dung_sai_10_van": {"dung": 6, "sai": 4, "tong": 10, "chuoi": "✅❌✅✅❌✅❌✅✅❌"},
                                 # đúng/sai của du_doan ở 10 phiên gần nhất (theo be_final hiện tại), chuoi: mới -> cũ, ✅ = đúng · ❌ = sai (đổi icon ở ICON_DUNG / ICON_SAI)
      "stale": false,            # true nếu lần quét upstream gần nhất bị lỗi (đang trả kết quả cũ)
      "cap_nhat": "2026-10-09 12:30:01"
    }

/api/predict?detail=1 -> chi_tiet có thêm:
      "final_goc": "XỈU"                                     # final trước khi bẻ (luôn là final gốc của các logic đang dùng)
      "tool_dung_sai_15_van": {"dung": 5, "tong": 9}         # đúng/sai ở WR_WINDOW ván gần nhất (tên khóa giữ nguyên cho tương thích)
      "trong_so_wr": {...}                                   # số ván xét + bảng trọng số (cũ nhất -> mới nhất) đang áp dụng


🧠 13 LOGIC CỦA SUN (SEQ13v6 · thuần chuỗi Tài/Xỉu + xúc xắc + tổng, KHÔNG dùng MD5, KHÔNG cần numpy):
    Mỗi logic là một thuật toán tự học ONLINE trên lịch sử các phiên đã quét (không dùng MD5, không dùng số phiên). Mỗi ván tính lại từ lịch sử, KHÔNG nhìn trước kết quả.
    ⚑ MỖI LOGIC CÓ CỬA SỔ DỮ LIỆU RIÊNG (LOGIC_WIN · env SUNVIW_WIN_<TÊN>): chỉ đọc đúng số ván GẦN NHẤT mà nó mạnh nhất, mọi ván trong cửa sổ trọng số NHƯ NHAU (không decay).
    ⚑ CẢ 13 LOGIC LUÔN BỎ PHIẾU (không cổng thống kê, không phiếu trắng) — co về 50% khi chuỗi ngẫu nhiên chứ không bịa cấu trúc.
      ── 7 logic giữ lại từ SEQ12v5 ──
        REGIME (250) nhịp đảo cầu: tỉ lệ đảo cầu 20 ván gần nhất chia 4 nhóm; học online P(ván sau ĐẢO | nhóm)
        KNNH   (200) láng giềng gần nhất MỜ: so 6/10/14 ván cuối với mọi đoạn cùng độ dài, 15 đoạn gần nhất bỏ phiếu
        SPARSE (500) 257 mô hình TRỄ THƯA (bitset + popcount), bắt cầu cách quãng / XOR lag
        BLKHAZ (400) hazard "bậc thang": (độ dài đợt đã xong k, số đợt liên tiếp cùng độ dài m, độ dài đợt hiện tại L) -> học "cầu 1-1 / 2-2 / 3-3 đã lặp m lần thì bẻ ở đâu". BẺ CẦU #3.
        BOCPD  (400) Bayesian Online Changepoint Detection trên chuỗi GIỐNG/KHÁC ván trước (có ngữ cảnh) — nhận ra đổi chế độ bệt <-> 1-1 nhanh. BỆT / ĐỔI CHẾ ĐỘ.
        GBS    (500) boosting stump trên ~12 đặc trưng cầu (bit cuối, độ dài đợt, chuỗi xen kẽ, cân bằng, tổng...) — phi tuyến nhưng mô hình CỘNG, lr nhỏ + lá tối thiểu nên co về 50% khi không có cấu trúc.
        AFM    (450) Markov bậc 1..4 × 4 hệ số QUÊN (0.90..1.0), trọng số theo log-loss tiên nghiệm gần đây — tự chọn tốc độ quên hợp với cầu.
      ── 6 logic MỚI ở SEQ13v6 (thay PPM6 · RUNCTX · TOTK · CAUTPL · FSHARE: PPM6 / RUNCTX / TOTK trùng phiếu quá nhiều với KNNH · AFM · BLKHAZ · GBS; CAUTPL / FSHARE quá kén cầu — chỉ trên 55% ở 2/8 kiểu cầu thử) ──
        CTW    (450) Context Tree Weighting (KT) độ sâu 8: trung bình Bayes của MỌI cây ngữ cảnh sâu <= 8 -> bắt cầu ngắn lẫn dài, tự co về bậc thấp khi ít mẫu. Yếu: coi cửa sổ là dừng, chậm theo kịp khi cầu đổi chế độ.
        MATCHR (450) khớp hậu tố DÀI NHẤT kiểu PPM*: mọi vị trí trùng ván cuối bỏ phiếu cho ván nằm sau, trọng số = (độ dài khớp)^2 × exp(-tuổi/150). Cực nhanh. Yếu: trùng phiếu với AFM · KNNH.
        FTRL   (450) hồi quy logistic ONLINE (FTRL-Proximal, phạt L1/L2) trên n-gram 1..8 + bit đơn lag 1..12 + độ dài đợt — học kiểu PHÂN BIỆT, khác kiểu ĐẾM của CTW · MATCHR · AFM. Yếu: nhạy tham số.
        ESN2   (300) Echo-State Network 24 nơ-ron (reservoir cố định, seed 7) + ridge readout — bộ nhớ động PHI TUYẾN, bắt cầu nghiêng / trôi chậm. Yếu: khó giải thích, chậm nhất nhóm mới (~15 ms/ván).
        RLS    (400) bộ lọc tuyến tính THÍCH NGHI: AR(6) cập nhật từng ván bằng Recursive Least Squares, hệ số quên 0.99 (nhớ hiệu dụng ~100 ván) — theo kịp đổi chế độ bệt <-> 1-1. Yếu: mù với cầu lag thưa.
        CMIXL  (500) Context Mixing Logistic kiểu PAQ: 9 mô hình con (bậc 1..8 · RUNCTX · tổng · match) trộn bằng hồi quy logistic ridge. HÀM CŨ CÓ SẴN (từng nằm trong SEQ13v4, bị bỏ ở SEQ12v5) — backtest cho thấy thuộc nhóm tốt nhất, nay đưa lại.
    ⚙ 13 là số LẺ: đa số tất cả logic KHÔNG bao giờ hoà; nhóm CAO/THẤP của AF vẫn có thể hoà -> phá hoà bằng phiếu SUN_TIE_LOGIC (mặc định AFM). WR không decay: WR_WEIGHT_NEWEST = WR_FLOOR = 1.0.
    ⚠ ĐỔI BỘ LOGIC -> SUN_SIG đổi thành SEQ13v6: các ván đã chấm của bộ cũ (file sun15_persist / hit15_*.json) bị bỏ khi load, WR / AF của mọi bàn bắt đầu lại từ các ván được chấm lại bằng bộ mới (rebuild từ lịch sử xúc xắc đang giữ).
    ⚠ Các hàm lg_ppm / lg_runctx / lg_totk / lg_cautpl / lg_fshare (5 logic bị bỏ ở SEQ13v6) và lg_blrev / lg_bal / lg_diemk / lg_spec / lg_hmm3 / lg_cpseg vẫn còn trong file nhưng KHÔNG nằm trong SUN_LOGICS (muốn dùng lại thì thêm vào SUN_LOGICS + LOGIC_WIN_DEFAULT).
    ⚠ Bộ mới được backtest walk-forward trên 306 phiên THẬT (khác nhau; data này gần như ngẫu nhiên nên KHÔNG phân biệt được logic nào hơn, sai số ±3%) + 9 kiểu cầu GIẢ LẬP × 6 seed (bỏ phiếu số đông: ~60.3% so với ~59.3% của bộ cũ, chênh +0.97 ± 0.33 — phần lớn đến từ cầu lag thưa). Trên RNG công bằng mọi logic ≈ 50%.
    Chưa đủ lịch sử cho một logic -> logic đó tạm theo kết quả ván trước. WR / AF / CAO-THẤP / bẻ final GIỮ NGUYÊN như bản trước.

🔀 AF = AUTO-FLIP + CAO/THẤP (port từ SUNVIW_9logics_autoflip_auto.html) — cách chốt final của SUN (mặc định BẬT · khối "CONFIG AF"):
    Bước 1 (bẻ logic):  WR có trọng số của từng logic (cùng WR_WINDOW ván / trọng số như cách cũ của SUN). WR < AF_FLIP_LOW (37%) hoặc > AF_FLIP_HIGH (63%) -> ĐẢO phiếu logic đó
                        (WR dùng = 100 − WR khi bị bẻ). Chưa đủ AF_MIN_GAMES ván -> không bẻ, vote tất cả logic.
                        ⚙ GIỚI HẠN VÙNG BẺ (AF_FLIP_BAND, mặc định BẬT): chỉ bẻ khi WR nằm TRONG vùng THẤP 32-40% hoặc vùng CAO 60-68% (gồm đầu mút); ngoài vùng (vd 29% / 41% / 59% / 69%) KHÔNG bẻ.
                        Vùng chỉnh bằng AF_FLIP_LOW_MIN/MAX · AF_FLIP_HIGH_MIN/MAX (env SUNVIW_AF_LOW_MIN... · cờ --af-low-min...) · tắt: --af-no-band hoặc SUNVIW_AF_BAND=0 (về ngưỡng 37/63 cũ)
    Bước 2 (CAO/THẤP):  ⚙ CHỈ logic ĐÃ BỊ BẺ (WR trong vùng bẻ) mới vào nhóm CAO/THẤP; logic không bẻ mặc định ALL (không thuộc nhóm nào) — AF_GROUP_FLIPPED_ONLY (--af-no-group-flipped = tắt).
                        ⚙ ĐỔI CHẾ ĐỘ DỄ HƠN (AF_SWITCH, mặc định BẬT · --af-no-switch = tắt): xoay quanh 3 chế độ ALL · THẤP · CAO. Mỗi logic bỏ 1 phiếu: nhóm CAO -> CAO · nhóm THẤP -> THẤP · logic không bẻ -> ALL (tổng 15 phiếu).
                        Tool NHỚ chế độ ván trước: chế độ KHÁC chỉ cần >= AF_SWITCH_NEED = 6/13 phiếu là đổi (bản gốc phải đa số 7/13). Đang ALL -> CAO / THẤP đủ 4 phiếu là sang · đang CAO -> ALL / THẤP đủ 4 phiếu là sang · đang THẤP -> ALL / CAO đủ 4 phiếu là sang.
                        Không chế độ khác nào đủ 4 phiếu -> giữ chế độ hiện tại · nhiều chế độ cùng đủ 4 -> lấy chế độ nhiều phiếu nhất (bằng nhau -> giữ chế độ hiện tại, tránh nhảy qua lại).
                        ⚙ ƯU TIÊN KHI 2 CHẾ ĐỘ CÒN LẠI CÙNG ĐỦ PHIẾU (AF_SWITCH_PRIO, mặc định BẬT · --af-no-switch-prio = tắt): không so số phiếu nữa mà theo chế độ VÁN TRƯỚC: ván trước ALL -> CAO · ván trước CAO -> ALL · ván trước THẤP -> CAO. Chỉ 1 chế độ đủ phiếu -> đổi sang chế độ đó như thường. Khi bật, AF_GROUP_NEED_MAJORITY (7/13) không còn tác dụng. --af-switch-need N đổi số phiếu.
                        ⚙ (Khi AF_SWITCH TẮT — cách gốc) Nhóm CAO/THẤP được chọn phải có >= ĐA SỐ toàn bộ logic (n//2+1 = 7/13); ít hơn -> dùng chế độ ALL — AF_GROUP_NEED_MAJORITY (--af-no-group-majority = tắt).
                        WR dùng > 50% -> nhóm CAO · < 50% -> nhóm THẤP. Nhóm nào ĐÔNG hơn thì chỉ vote trong nhóm đó (chế độ CAO / THẤP); bằng nhau -> vote tất cả (chế độ ALL).
    Bước 3 (bẻ chế độ): WR của CHẾ ĐỘ đang chạy trong AF_MODE_WINDOW (7) ván gần nhất của chế độ đó < AF_MODE_BELOW (45%) -> ĐẢO final (không theo đa số nữa);
                        từ 45% trở lên -> theo bình thường. Đang bẻ THẤP mà ván sau lên CAO thì xét lại WR của CAO. Chưa đủ AF_MODE_MIN ván của chế độ đó -> không bẻ.
                        ⛔ BƯỚC 3 ĐANG TẮT MẶC ĐỊNH (AF_MODE_FLIP_DEFAULT = False · env SUNVIW_AF_MODE_FLIP=1 / cờ --af-mode-flip để bật lại): final = kết quả sau bước 2, không đảo theo WR chế độ.
    Dữ liệu 2 chế độ: MỖI ván đã chấm lưu sẵn vote của nhóm CAO (hv) và của nhóm THẤP (lv) — cả khi tool đang chạy chế độ kia — nên WR 7 ván của cả 2 chế độ luôn có sẵn. (Bước 3 còn đo RIÊNG chế độ ALL: mỗi ván lưu thêm av = đa số tất cả logic sau bẻ logic.)
                      WR chế độ luôn đo trên vote GỐC (chưa bẻ chế độ) để bẻ xong WR không tăng lại rồi tắt bẻ (dao động).
    Ván do AF chốt KHÔNG bị bẻ bởi FLIP_FINAL chung (AF đã tự bẻ) — muốn bẻ riêng AF dùng AF_FLIP_FINAL (bẻ MỌI chế độ) · AF_FLIP_FINAL_CT (CHỈ bẻ khi chế độ CAO/THẤP, ALL giữ nguyên) · AF_FLIP_FINAL_ALL (CHỈ bẻ khi chế độ ALL, CAO/THẤP giữ nguyên). AF tắt (--no-af) -> quay về đúng cách cũ (WR có trọng số + nhóm THẤP/CAO + FLIP_FINAL).
    Thứ tự chốt của SUN:  AF  ->  cách cũ (khi tắt AF).   JSON thêm: "af", "che_do", "be_che_do", "du_doan_goc", "du_doan_truoc_be_che_do", "wr_che_do_hien_tai" (panel dùng để hiện đúng chế độ hiện tại); mỗi dòng lich_su có thêm "be_final" (ván đó có bị bẻ final theo cấu hình HIỆN TẠI không); ?detail=1 thêm chi_tiet.af (WR 2 chế độ, logic nào bị bẻ).

🌐 TAB IP (panel /api/html) — theo dõi ai đang gọi API:
    Mỗi request tới /api/predictsun · /api/predicthittxthuong · /api/predicthittxmd5 · /api/html được ghi lại IP của client (sau proxy Railway đọc X-Forwarded-For / X-Real-IP).
    Tab "IP" hiện: IP ĐANG DÙNG (có request trong IP_ACTIVE_SEC giây gần nhất) + IP ĐÃ TỪNG DÙNG (lưu file, còn sau khi restart) · lần đầu / gần nhất · số request · chia theo loại (sun · hit · panel) · User-Agent.
    Khối "CONFIG IP" ở gần đầu file. Nên đặt SUNVIW_ADMIN_KEY để chỉ bạn xem được danh sách IP (panel là trang công khai).

🔐 HWID (gắn key theo THIẾT BỊ, thay cho gắn theo IP mạng) — khối "CONFIG KEY / ADMIN":
    Mọi key (người dùng + admin phụ) đều gắn HWID. Mỗi key có số thiết bị tối đa (max_dev, chọn lúc tạo: 1-2-3-5-10-20-50): máy mới dùng key lần đầu tự được gắn nếu còn chỗ,
    đủ chỗ rồi thì máy khác bị chặn tới khi admin reset / gỡ thiết bị. Panel (/api/html, /api/admin) tự tạo HWID; tool tự viết gửi header X-HWID (hoặc ?hwid= / body {"hwid"}) cùng X-User-Key.
    Admin chính + admin phụ đều chọn được số thiết bị khi tạo key; admin phụ chỉ tạo được key người dùng. Trang admin hiện: số thiết bị đang gắn / tối đa · lần dùng gần nhất · từng thiết bị (có nút Gỡ)
    · tích chọn nhiều key để xóa một lượt.
    ⚑ KHÔNG BAO GIỜ chặn theo IP: đổi mạng / đổi IP không ảnh hưởng key, chỉ máy khác mới bị chặn. Mã thiết bị được giữ ổn định (lưu localStorage + cookie, dấu vân tay phần cứng không đổi theo UA / zoom / xoay màn hình),
    server học thêm mã phụ cho từng thiết bị (header X-HWID-ALT) để máy xoá dữ liệu trình duyệt vẫ được nhận lại thay vì chiếm thêm chỗ — chi tiết ở khối "CONFIG KEY / ADMIN".

🎯 HITCLUB (GAME 3 · 2 BÀN) — port từ hittxthuong.js / hittxmd5.js (khối "CONFIG HITCLUB" + phần "HITCLUB" ở giữa file):
    Bàn TX THƯỜNG (gid vgmn_100, cmd 1008 + 1003) và bàn TX MD5 (gid vgmn_101, cmd 2006): mỗi bàn một poller (mặc định 3s), tự tích lũy lịch sử xúc xắc.
    Dự đoán = bộ 13 logic SEQ13v6 + AF + WR có trọng số như SUN, nhưng mỗi bàn đọc CONFIG RIÊNG (HIT_TXTHUONG_CFG / HIT_TXMD5_CFG — hiện đang bằng mặc định của SUN) -> chỉnh bàn nào chỉ ảnh hưởng bàn đó.
    Data lưu RIÊNG: <DATA_DIR>/hit15_txthuong.json và <DATA_DIR>/hit15_txmd5.json (mỗi file = lịch sử xúc xắc + các ván đã chấm của bàn đó). Panel /api/html có thêm 2 tab "Hit Thường" · "Hit MD5".
    Tắt: HITCLUB=0 hoặc --no-hit. Đổi config không sửa file: biến môi trường HITTXTHUONG_<TÊN> / HITTXMD5_<TÊN> (vd. HITTXMD5_AF_ENABLED=0).

Server quét upstream nền mỗi POLL_SEC giây, chỉ tính lại khi có phiên mới -> request của HTML trả về tức thì.
"""
import argparse
import atexit
import base64
import hashlib
import hmac
import ipaddress
import json
import math
import os
import re
import secrets
import shutil
import sys
import threading
import time
import unicodedata
import urllib.request
from fractions import Fraction


# ═══════════════════════════════════════════════════════════════════════════
#  ⬆  KHỐI CONFIG AF CỦA SUN NẰM NGAY ĐÂY (đầu file) — sửa mọi thông số AF ở khối này, không cần tìm xuống dưới
# ═══════════════════════════════════════════════════════════════════════════

def _env_bool(name, default):
    """Đọc biến môi trường dạng bật/tắt; không đặt hoặc giá trị lạ -> dùng `default`."""
    v = os.environ.get(name, "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return default


def _env_num(name, default, cast):
    v = os.environ.get(name, "").strip()
    if not v:
        return default
    try:
        return cast(v)
    except ValueError:
        return default


# ═══════════════════════════════════════════════════════════════════════════
#  🔀  CONFIG AF (AUTO-FLIP + CAO/THẤP + BẺ THEO WR CHẾ ĐỘ) — CÁCH CHỐT FINAL CỦA SUN  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Port từ SUNVIW_9logics_autoflip_auto.html. WR từng logic = WR CÓ TRỌNG SỐ của SUN (WR_WINDOW / WR_DECAY / WR_FLOOR / WR_WEIGHT_NEWEST / WR_FLIP_WEIGHT).
#   Bước 1  bẻ logic     : WR < AF_FLIP_LOW -> đảo phiếu logic · WR > AF_FLIP_HIGH -> đảo phiếu logic (WR dùng = 100 − WR). Chưa đủ AF_MIN_GAMES ván -> không bẻ, vote tất cả.
#   Bước 2  CAO / THẤP   : WR dùng > 50% -> nhóm CAO · < 50% -> nhóm THẤP · nhóm đông hơn được vote (CHẾ ĐỘ CAO / THẤP) · bằng nhau -> vote tất cả (ALL) · pool hoà phiếu -> đa số tất cả logic.
#                          AF_SWITCH BẬT (mặc định): thay "nhóm đông hơn thắng + đa số 7/13" bằng ĐỔI CHẾ ĐỘ DỄ HƠN — nhớ chế độ ván trước, chế độ khác đủ AF_SWITCH_NEED (6/13) phiếu là đổi (xem khối ĐỔI CHẾ ĐỘ DỄ HƠN bên dưới).
#   Bước 3  bẻ chế độ    : WR của chế độ đang chạy trong AF_MODE_WINDOW ván gần nhất CỦA CHẾ ĐỘ ĐÓ < AF_MODE_BELOW -> đảo final · ≥ AF_MODE_BELOW -> theo bình thường.
#                          Cần đủ AF_MODE_MIN ván của chế độ đó mới xét bẻ. CAO / THẤP / ALL đều có chuỗi ván riêng (hv / lv / av lưu trong từng ván đã chấm) — WR của từng chế độ xét RIÊNG, chế độ nào < AF_MODE_BELOW thì chế độ đó bị bẻ khi được chọn.
#                          ⛔ MẶC ĐỊNH ĐANG TẮT (AF_MODE_FLIP_DEFAULT = False): bước 3 bị bỏ qua -> final = kết quả sau bước 2 (CAO / THẤP / ALL), không bị đảo theo WR chế độ.
#                          Bật lại: sửa AF_MODE_FLIP_DEFAULT = True · hoặc env SUNVIW_AF_MODE_FLIP=1 · hoặc cờ --af-mode-flip (--af-no-mode-flip = tắt).
#                          Khi TẮT: AF_MODE_WINDOW / AF_MODE_MIN / AF_MODE_BELOW không còn tác dụng; be_che_do luôn false; wr_che_do_hien_tai = null.
#   AF_ENABLED_DEFAULT    True = dùng AF · False = quay về cách cũ (wr_decision + FLIP_FINAL)
#   AF_FLIP_LOW/HIGH      ngưỡng bẻ logic (37 / 63 như file HTML)
#   AF_MIN_GAMES_DEFAULT  số ván đã chấm tối thiểu mới bẻ logic / chia nhóm (tự kẹp ≤ WR_WINDOW)
#   AF_MODE_WINDOW        số ván gần nhất của mỗi chế độ để tính WR chế độ (7)
#   AF_MODE_MIN           số ván tối thiểu của chế độ đó mới xét bẻ (7; tự kẹp ≤ AF_MODE_WINDOW)
#   AF_MODE_BELOW         WR chế độ dưới mức này (%) -> bẻ final (45)
#   AF_MODE_FLIP_DEFAULT  công tắc BƯỚC 3 (bẻ chế độ): False = TẮT (mặc định, theo yêu cầu) · True = bật như bản trước
#   AF_FLIP_FINAL_DEFAULT bẻ riêng kết quả AF (TÀI<->XỈU) ở MỌI chế độ (CAO · THẤP · ALL). Mặc định False vì AF đã tự bẻ; FLIP_FINAL chung KHÔNG áp lên ván do AF chốt.
#   AF_FLIP_FINAL_CT_DEFAULT  True = CHỈ bẻ final khi AF đang ở chế độ CAO / THẤP · final của chế độ ALL GIỮ NGUYÊN (không bẻ).
#   AF_FLIP_FINAL_ALL_DEFAULT True = CHỈ bẻ final khi AF đang ở chế độ ALL · final của chế độ CAO / THẤP GIỮ NGUYÊN (không bẻ).
#   AF_FLIP_FINAL_CAO_DEFAULT  True = CHỈ bẻ final khi AF đang ở chế độ CAO  · THẤP + ALL GIỮ NGUYÊN.   ┐ TÁCH RIÊNG CAO / THẤP: vd muốn THEO final CAO nhưng BẺ final THẤP
#   AF_FLIP_FINAL_THAP_DEFAULT True = CHỈ bẻ final khi AF đang ở chế độ THẤP · CAO + ALL GIỮ NGUYÊN.   ┘ -> CAO = False · THẤP = True (và _CT = False).
#       AF_FLIP_FINAL_CT (cũ) = công tắc GỘP: True = bẻ cả CAO lẫn THẤP (tương đương bật _CAO + _THAP). Tất cả công tắc là phép HOẶC.
#       Cả 3 công tắc (AF_FLIP_FINAL · _CT · _ALL) là phép HOẶC: ván thuộc chế độ nào có ÍT NHẤT 1 công tắc áp dụng thì bẻ ĐÚNG 1 lần (không bẻ đôi). Bật AF_FLIP_FINAL = bẻ hết, 2 công tắc kia khỏi cần.
#       Chọn 1 trong 2 (_CT hoặc _ALL) để bẻ có chọn lọc; bật cả 2 = giống bật AF_FLIP_FINAL. Bẻ này nằm SAU 'bẻ chế độ' (bước 3) nên chỉ là lớp bẻ thêm của riêng bạn.
#   Đổi mà không sửa file (ưu tiên: cờ dòng lệnh > biến môi trường > *_DEFAULT):
#       env  : SUNVIW_AF=1|0 · SUNVIW_AF_LOW · SUNVIW_AF_HIGH · SUNVIW_AF_MIN · SUNVIW_AF_MODE_WINDOW · SUNVIW_AF_MODE_MIN · SUNVIW_AF_MODE_BELOW · SUNVIW_AF_MODE_FLIP=1|0 · SUNVIW_AF_FLIP=1|0 · SUNVIW_AF_FLIP_CT=1|0 · SUNVIW_AF_FLIP_CAO=1|0 · SUNVIW_AF_FLIP_THAP=1|0 · SUNVIW_AF_FLIP_ALL=1|0
#       lệnh : --af / --no-af · --af-low X · --af-high X · --af-min N · --af-mode-window N · --af-mode-below X · --af-mode-flip / --af-no-mode-flip · --af-flip / --af-no-flip · --af-flip-ct / --af-no-flip-ct · --af-flip-cao / --af-no-flip-cao · --af-flip-thap / --af-no-flip-thap · --af-flip-all / --af-no-flip-all
AF_ENABLED_DEFAULT = True
AF_FLIP_LOW_DEFAULT = 37
AF_FLIP_HIGH_DEFAULT = 63
# ── GIỚI HẠN VÙNG BẺ LOGIC (Bước 1) — AF_FLIP_BAND ────────────────────────────────────────────────
#   BẬT (mặc định): CHỈ bẻ logic khi WR nằm TRONG vùng cho phép (gồm cả 2 đầu mút); ngoài vùng -> KHÔNG bẻ (giữ nguyên phiếu).
#       Vùng THẤP : AF_FLIP_LOW_MIN  <= WR <= AF_FLIP_LOW_MAX   (mặc định 32 - 40)  -> vd WR 29% KHÔNG bẻ · 32-40% bẻ · 41% KHÔNG bẻ
#       Vùng CAO  : AF_FLIP_HIGH_MIN <= WR <= AF_FLIP_HIGH_MAX  (mặc định 60 - 68)  -> vd WR 59% KHÔNG bẻ · 60-68% bẻ · 69% KHÔNG bẻ   (đối xứng vùng thấp qua 50%)
#       Khi BẬT: AF_FLIP_LOW / AF_FLIP_HIGH (37 / 63) bị bỏ qua — vùng mới thay thế ngưỡng cũ.
#   TẮT : quay về cách cũ (WR < AF_FLIP_LOW -> bẻ · WR > AF_FLIP_HIGH -> bẻ, không có cận dưới / cận trên).
#   Đổi mà không sửa file: env SUNVIW_AF_BAND=1|0 · SUNVIW_AF_LOW_MIN · SUNVIW_AF_LOW_MAX · SUNVIW_AF_HIGH_MIN · SUNVIW_AF_HIGH_MAX
#                          lệnh --af-band / --af-no-band · --af-low-min X · --af-low-max X · --af-high-min X · --af-high-max X
AF_FLIP_BAND_DEFAULT = True
AF_FLIP_LOW_MIN_DEFAULT = 30
AF_FLIP_LOW_MAX_DEFAULT = 45
AF_FLIP_HIGH_MIN_DEFAULT = 53
AF_FLIP_HIGH_MAX_DEFAULT = 65
# ── CHỈ LOGIC BỊ BẺ MỚI VÀO NHÓM CAO / THẤP (Bước 2) — AF_GROUP_FLIPPED_ONLY + AF_GROUP_NEED_MAJORITY ─────────────
#   AF_GROUP_FLIPPED_ONLY_DEFAULT  BẬT (mặc định): CHỈ logic ĐÃ BỊ BẺ (WR nằm TRONG vùng bẻ ở khối trên) mới được xếp vào nhóm CAO / THẤP
#       (theo WR dùng sau bẻ). Logic KHÔNG bẻ (WR ngoài vùng bẻ) KHÔNG thuộc nhóm nào — mặc định ở chế độ ALL (panel hiện nhãn ALL).
#       TẮT: như bản trước — mọi logic đều được chia CAO (WR dùng > 50%) / THẤP (< 50%).
#   AF_GROUP_NEED_MAJORITY_DEFAULT BẬT (mặc định): nhóm CAO / THẤP được chọn (nhóm đông hơn) phải có SỐ LOGIC >= ĐA SỐ của TOÀN BỘ logic
#       (n // 2 + 1 · vd 13 logic -> cần >= 7). Ít hơn đa số -> bỏ nhóm, dùng chế độ ALL (vote tất cả logic sau bẻ logic).
#       Vd ảnh panel: chỉ 4/13 logic bị bẻ (2 CAO + 2 THẤP) -> không nhóm nào đủ 7 logic -> chế độ ALL thay vì CAO.
#       TẮT: nhóm đông hơn luôn được chọn dù chỉ có 1-2 logic.
#   Đổi mà không sửa file: env SUNVIW_AF_GROUP_FLIPPED=1|0 · SUNVIW_AF_GROUP_MAJORITY=1|0
#                          lệnh --af-group-flipped / --af-no-group-flipped · --af-group-majority / --af-no-group-majority
AF_GROUP_FLIPPED_ONLY_DEFAULT = True
AF_GROUP_NEED_MAJORITY_DEFAULT = True
# ── ĐỔI CHẾ ĐỘ DỄ HƠN (Bước 2) — AF_SWITCH + AF_SWITCH_NEED ─────────────────────────────────────────────────
#   Xoay quanh 3 chế độ ALL · THẤP · CAO. Mỗi logic "bỏ phiếu" cho 1 chế độ: logic nhóm CAO -> phiếu CAO · nhóm THẤP -> phiếu THẤP · logic không thuộc nhóm nào (không bẻ) -> phiếu ALL.
#   Tổng luôn = số logic (vd 15): phiếu ALL + phiếu CAO + phiếu THẤP = 15.
#   AF_SWITCH_DEFAULT BẬT (mặc định): chế độ có NHỚ chế độ của ván trước (đang ALL / CAO / THẤP) rồi mới xét đổi:
#       · Chế độ KHÁC có >= AF_SWITCH_NEED phiếu (mặc định 6/13) -> ĐỔI sang chế độ đó (bản gốc phải 7/13 = đa số mới đổi sang CAO / THẤP).
#           vd đang ALL: CAO được 4 phiếu -> sang CAO · THẤP được 4 phiếu -> sang THẤP.   vd đang CAO: ALL hoặc THẤP được 4 phiếu -> sang ALL / THẤP.   (tương tự khi đang THẤP)
#       · Không chế độ khác nào đủ AF_SWITCH_NEED phiếu -> GIỮ chế độ hiện tại.
#       · Nhiều chế độ cùng đủ phiếu (kể cả chế độ hiện tại) -> chọn chế độ NHIỀU phiếu nhất (tránh nhảy qua nhảy lại mỗi ván); bằng nhau ở đầu bảng -> giữ chế độ hiện tại.
#       · Chế độ đang giữ là CAO / THẤP mà nhóm đó không còn logic nào -> không có ai để vote, tạm dùng ALL ván này.
#       Khi BẬT: AF_GROUP_NEED_MAJORITY (đa số 7/13) KHÔNG còn tác dụng — ngưỡng 6/13 thay cho nó.
#   TẮT : quay về cách gốc (không nhớ chế độ cũ · nhóm đông hơn thắng · nhóm CAO / THẤP phải >= đa số 7/13 nếu AF_GROUP_NEED_MAJORITY bật).
#   Ván đầu / ván cũ chưa lưu chế độ -> coi chế độ trước là ALL.
#   Đổi mà không sửa file: env SUNVIW_AF_SWITCH=1|0 · SUNVIW_AF_SWITCH_NEED     lệnh --af-switch / --af-no-switch · --af-switch-need N
#   AF_SWITCH_LEAD_DEFAULT = False (mặc định): chỉ cần chế độ khác đủ AF_SWITCH_NEED phiếu là đổi, KỂ CẢ khi chế độ đang chạy nhiều phiếu hơn (đúng ý "chỉ cần 6/13").
#       Hệ quả: khi cả 2 chế độ cùng >= AF_SWITCH_NEED phiếu thì ván sau có thể đổi ngược lại (vd ALL 9 · CAO 4: ALL -> CAO, rồi CAO -> ALL ...) — chế độ đổi nhiều hơn.
#       True = êm hơn: chế độ mới còn phải DẪN ĐẦU duy nhất (nhiều phiếu hơn cả chế độ đang chạy) mới đổi. Lưu ý: 13 logic chia cho 3 chế độ thì bên dẫn đầu luôn >= 5 phiếu,
#       nên với True mọi AF_SWITCH_NEED <= 5 cho kết quả GIỐNG HỆT nhau (6/13 không dễ hơn 7/15).   env SUNVIW_AF_SWITCH_LEAD · lệnh --af-switch-lead / --af-no-switch-lead
AF_SWITCH_DEFAULT = True
AF_SWITCH_NEED_DEFAULT = 6
AF_SWITCH_LEAD_DEFAULT = False
#   AF_SWITCH_PRIO_DEFAULT BẬT (mặc định): khi đang ở 1 chế độ mà CẢ 2 chế độ còn lại đều đủ AF_SWITCH_NEED phiếu (vd 6/13) thì chọn theo ƯU TIÊN dựa trên chế độ VÁN TRƯỚC (không so số phiếu):
#       · ván trước ALL  -> ưu tiên CAO      · ván trước CAO -> ưu tiên ALL      · ván trước THẤP -> ưu tiên CAO
#       Chỉ 1 chế độ đủ phiếu -> đổi sang chế độ đó như bình thường · không chế độ nào đủ -> giữ chế độ hiện tại.  Chỉ có tác dụng khi AF_SWITCH bật và AF_SWITCH_LEAD tắt.
#       TẮT: quay về cách cũ (cả 2 cùng đủ phiếu -> lấy chế độ nhiều phiếu hơn, bằng nhau -> giữ chế độ hiện tại).   env SUNVIW_AF_SWITCH_PRIO=1|0 · lệnh --af-switch-prio / --af-no-switch-prio
AF_SWITCH_PRIO_DEFAULT = True
AF_MIN_GAMES_DEFAULT = 7
AF_MODE_WINDOW_DEFAULT = 11
AF_MODE_MIN_DEFAULT = 7
AF_MODE_BELOW_DEFAULT = 45
AF_MODE_FLIP_DEFAULT = False          # BƯỚC 3 (bẻ final theo WR chế độ): False = TẮT · True = BẬT
AF_FLIP_FINAL_DEFAULT = False
AF_FLIP_FINAL_CT_DEFAULT = False       # True = bẻ final của chế độ CAO / THẤP  (BẬT theo yêu cầu: bẻ CAO/THẤP + bẻ ALL)
AF_FLIP_FINAL_CAO_DEFAULT = False      # True = CHỈ bẻ final của chế độ CAO   (TÁCH RIÊNG khỏi THẤP)
AF_FLIP_FINAL_THAP_DEFAULT = True     # True = CHỈ bẻ final của chế độ THẤP  (TÁCH RIÊNG khỏi CAO) — vd theo CAO nhưng bẻ THẤP: CAO=False · THAP=True
AF_FLIP_FINAL_ALL_DEFAULT = True      # True = bẻ final của chế độ ALL        (BẬT)

AF_ENABLED = _env_bool("SUNVIW_AF", AF_ENABLED_DEFAULT)
AF_FLIP_LOW = _env_num("SUNVIW_AF_LOW", AF_FLIP_LOW_DEFAULT, float)
AF_FLIP_HIGH = _env_num("SUNVIW_AF_HIGH", AF_FLIP_HIGH_DEFAULT, float)
AF_FLIP_BAND = _env_bool("SUNVIW_AF_BAND", AF_FLIP_BAND_DEFAULT)                          # giới hạn vùng bẻ logic (xem khối GIỚI HẠN VÙNG BẺ)
AF_FLIP_LOW_MIN = _env_num("SUNVIW_AF_LOW_MIN", AF_FLIP_LOW_MIN_DEFAULT, float)
AF_FLIP_LOW_MAX = _env_num("SUNVIW_AF_LOW_MAX", AF_FLIP_LOW_MAX_DEFAULT, float)
AF_FLIP_HIGH_MIN = _env_num("SUNVIW_AF_HIGH_MIN", AF_FLIP_HIGH_MIN_DEFAULT, float)
AF_FLIP_HIGH_MAX = _env_num("SUNVIW_AF_HIGH_MAX", AF_FLIP_HIGH_MAX_DEFAULT, float)
AF_GROUP_FLIPPED_ONLY = _env_bool("SUNVIW_AF_GROUP_FLIPPED", AF_GROUP_FLIPPED_ONLY_DEFAULT)      # chỉ logic bị bẻ mới vào nhóm CAO / THẤP
AF_GROUP_NEED_MAJORITY = _env_bool("SUNVIW_AF_GROUP_MAJORITY", AF_GROUP_NEED_MAJORITY_DEFAULT)   # nhóm chọn < đa số toàn bộ logic -> dùng ALL
AF_SWITCH = _env_bool("SUNVIW_AF_SWITCH", AF_SWITCH_DEFAULT)                                     # đổi chế độ ALL / CAO / THẤP dễ hơn: chỉ cần AF_SWITCH_NEED phiếu (thay vì đa số)
AF_SWITCH_LEAD = _env_bool("SUNVIW_AF_SWITCH_LEAD", AF_SWITCH_LEAD_DEFAULT)                      # True = chế độ mới còn phải dẫn đầu duy nhất mới đổi (êm hơn)
AF_SWITCH_PRIO = _env_bool("SUNVIW_AF_SWITCH_PRIO", AF_SWITCH_PRIO_DEFAULT)                      # True = 2 chế độ còn lại cùng đủ phiếu -> ưu tiên theo chế độ ván trước (ALL->CAO · CAO->ALL · THẤP->CAO)
AF_SWITCH_NEED = _env_num("SUNVIW_AF_SWITCH_NEED", AF_SWITCH_NEED_DEFAULT, int)                 # số phiếu (trên tổng số logic) để đổi sang chế độ khác (mặc định 6/13)
AF_MIN_GAMES =_env_num("SUNVIW_AF_MIN", AF_MIN_GAMES_DEFAULT, int)
AF_MODE_WINDOW = _env_num("SUNVIW_AF_MODE_WINDOW", AF_MODE_WINDOW_DEFAULT, int)
AF_MODE_MIN = _env_num("SUNVIW_AF_MODE_MIN", AF_MODE_MIN_DEFAULT, int)
AF_MODE_BELOW = _env_num("SUNVIW_AF_MODE_BELOW", AF_MODE_BELOW_DEFAULT, float)
AF_MODE_FLIP = _env_bool("SUNVIW_AF_MODE_FLIP", AF_MODE_FLIP_DEFAULT)            # bước 3: bẻ final theo WR chế độ
AF_FLIP_FINAL = _env_bool("SUNVIW_AF_FLIP", AF_FLIP_FINAL_DEFAULT)
AF_FLIP_FINAL_CT = _env_bool("SUNVIW_AF_FLIP_CT", AF_FLIP_FINAL_CT_DEFAULT)      # chỉ bẻ final khi chế độ CAO / THẤP
AF_FLIP_FINAL_CAO = _env_bool("SUNVIW_AF_FLIP_CAO", AF_FLIP_FINAL_CAO_DEFAULT)    # chỉ bẻ final khi chế độ CAO
AF_FLIP_FINAL_THAP = _env_bool("SUNVIW_AF_FLIP_THAP", AF_FLIP_FINAL_THAP_DEFAULT)  # chỉ bẻ final khi chế độ THẤP
AF_FLIP_FINAL_ALL = _env_bool("SUNVIW_AF_FLIP_ALL", AF_FLIP_FINAL_ALL_DEFAULT)   # chỉ bẻ final khi chế độ ALL


def af_apply_limits():
    """Chuẩn hoá tham số AF (gọi lúc import và sau khi đọc cờ dòng lệnh)."""
    global AF_FLIP_LOW, AF_FLIP_HIGH, AF_MIN_GAMES, AF_MODE_WINDOW, AF_MODE_MIN, AF_MODE_BELOW
    global AF_FLIP_LOW_MIN, AF_FLIP_LOW_MAX, AF_FLIP_HIGH_MIN, AF_FLIP_HIGH_MAX, AF_SWITCH_NEED
    AF_SWITCH_NEED = max(1, int(AF_SWITCH_NEED))
    AF_FLIP_LOW = min(max(0.0, float(AF_FLIP_LOW)), 50.0)
    AF_FLIP_HIGH = min(max(50.0, float(AF_FLIP_HIGH)), 100.0)
    lo_a, lo_b = sorted((min(max(0.0, float(AF_FLIP_LOW_MIN)), 50.0), min(max(0.0, float(AF_FLIP_LOW_MAX)), 50.0)))          # vùng thấp nằm trong 0-50 (tự đổi chỗ nếu gõ ngược)
    hi_a, hi_b = sorted((min(max(50.0, float(AF_FLIP_HIGH_MIN)), 100.0), min(max(50.0, float(AF_FLIP_HIGH_MAX)), 100.0)))   # vùng cao nằm trong 50-100
    AF_FLIP_LOW_MIN, AF_FLIP_LOW_MAX, AF_FLIP_HIGH_MIN, AF_FLIP_HIGH_MAX = lo_a, lo_b, hi_a, hi_b
    AF_MIN_GAMES = max(1, int(AF_MIN_GAMES))
    AF_MODE_WINDOW = max(1, int(AF_MODE_WINDOW))
    AF_MODE_MIN = max(1, min(int(AF_MODE_MIN), AF_MODE_WINDOW))
    AF_MODE_BELOW = min(max(0.0, float(AF_MODE_BELOW)), 100.0)


af_apply_limits()


# ─── CẤU HÌNH ────────────────────────────────────────────────────────────
# Upstream MỚI: /api/tx chỉ trả 1 PHIÊN MỚI NHẤT dạng 1 object:
#   {"ket_qua":"Tài","phien":3284075,"thoi_gian":"11-10-2026 13:50:38 UTC+7","tong":15,"xuc_xac_1":6,"xuc_xac_2":3,"xuc_xac_3":6}
# -> tool quét 1 phiên gần nhất mỗi lần, tự tích lũy vào lịch sử (HIST_PATH) để phần WR vẫn có ván để chấm.
UPSTREAM_URL = os.environ.get(
    "SUNVIW_UPSTREAM",
    "https://well-summary-oclc-invisible.trycloudflare.com/api/tx",
)
UPSTREAM_TIMEOUT = 9      # giây
# THƯ MỤC LƯU DỮ LIỆU BỀN: Railway gắn Volume thì tự đặt RAILWAY_VOLUME_MOUNT_PATH (vd. /data) -> mọi file lưu (lịch sử, graded, key, IP...)
# nằm trong Volume nên KHÔNG MẤT sau mỗi lần deploy / restart. Không có Volume (chạy máy local) -> dùng /tmp như cũ.
# Muốn tự chọn thư mục: đặt SUNVIW_DATA_DIR. Từng file vẫn ghi đè riêng được bằng SUNVIW_HIST / SUNVIW_PERSIST / SUNVIW_KEYS_PATH / SUNVIW_IPS_PATH.
ON_RAILWAY = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID") or os.environ.get("RAILWAY_SERVICE_ID"))
DATA_DIR = os.environ.get("SUNVIW_DATA_DIR") or os.environ.get("RAILWAY_VOLUME_MOUNT_PATH") or ""
if not DATA_DIR and ON_RAILWAY:                        # Railway nhưng chưa có biến Volume -> thử các điểm gắn ổ đĩa hay dùng (chỉ nhận nếu THẬT SỰ là ổ đĩa gắn riêng)
    for _cand in ("/data", "/app/data", "/mnt/data"):
        if os.path.ismount(_cand):
            DATA_DIR = _cand
            break
DATA_DIR = DATA_DIR or "/tmp"
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except OSError:
    DATA_DIR = "/tmp"
# Dữ liệu có BỀN qua redeploy không? /tmp (hoặc thư mục tạm) = KHÔNG. Chạy máy local thì ổ đĩa bình thường nên coi là bền, chỉ cảnh báo khi đang ở Railway.
DATA_PERSISTENT = (DATA_DIR == os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")) or not (DATA_DIR == "/tmp" or DATA_DIR.startswith("/tmp/")) or not ON_RAILWAY


def _data_path(name):
    return os.path.join(DATA_DIR, name)


BOOT_PATH = os.environ.get("SUNVIW_BOOT_PATH", _data_path("sunviw_boot.json"))


def _boot_mark():
    """Ghi mốc khởi động vào thư mục data: lần đầu (first) + số lần khởi động (count). Redeploy xong mà `first` vẫn cũ và `count` tăng = data đã được giữ lại.
    Ngược lại `first` = vừa mới => thư mục data đã bị xoá sạch (chưa gắn Volume)."""
    now = int(time.time())
    d = {"first": now, "count": 0}
    try:
        with open(BOOT_PATH, "r", encoding="utf-8") as f:
            o = json.load(f)
        if isinstance(o, dict) and o.get("first"):
            d["first"], d["count"] = int(o["first"]), int(o.get("count") or 0)
    except Exception:  # noqa: BLE001
        pass
    d["count"] += 1
    d["last"] = now
    try:
        tmp = BOOT_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f)
        os.replace(tmp, BOOT_PATH)
    except OSError:
        d["loi_ghi"] = True
    return d


BOOT_INFO = _boot_mark()


HIST_PATH = os.environ.get("SUNVIW_HIST", _data_path("sun15_hist.json"))   # lịch sử các phiên đã quét (tool tự tích lũy)
HIST_KEEP = int(os.environ.get("SUNVIW_HIST_KEEP", "600") or 600)   # CỬA SỔ TRƯỢT 600 VÁN: chỉ giữ 600 phiên GẦN NHẤT (RAM + file) — có phiên thứ 601 thì phiên cũ nhất bị bỏ. Mỗi logic đọc cửa sổ riêng LOGIC_WIN (≤ 500) trong số này. Đổi: env SUNVIW_HIST_KEEP
POLL_SEC = 3.0             # chu kỳ quét upstream (giống AUTO_INTERVAL_MS của HTML)
WR_MIN_GAMES = 1           # số ván đã chấm tối thiểu để dùng WR (dưới mức này -> đa số 21 logic)

# ═══════════════════════════════════════════════════════════════════════════
#  ⚙  CONFIG WR CÓ TRỌNG SỐ (KIỂU "PHẢN ỨNG NHANH + SÀN NHỚ CẦU CŨ")  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Ván MỚI NHẤT có trọng số = WR_WEIGHT_NEWEST (cao nhất). Ván càng cũ trọng số càng giảm theo hàm mũ NHƯNG không bao giờ
#   thấp hơn WR_FLOOR  ->  cầu mới đổi thì phản ứng nhanh (các ván mới chiếm phần lớn quyền), còn cầu cũ vẫn giữ
#   một phần quyền (không bị quên hẳn).
#
#       trọng số(ván tuổi a) = WR_FLOOR + (WR_WEIGHT_NEWEST - WR_FLOOR) * WR_DECAY ** a        (a = 0 là ván mới nhất -> đúng = WR_WEIGHT_NEWEST)
#
#   WR_WINDOW = số ván gần nhất được xét để tính WR
#   WR_DECAY  = tốc độ quên (0.75 = mỗi ván cũ hơn, phần "thưởng mới" giảm còn 75%). Nhỏ hơn -> phản ứng nhanh hơn.
#   WR_WEIGHT_NEWEST = trọng số của ván MỚI NHẤT (1.00 = bản gốc). Lớn hơn WR_FLOOR càng nhiều -> ván mới nhất càng nặng so với ván cũ.
#               Phải > WR_FLOOR (nếu <= thì ván mới không còn nặng hơn ván cũ). Đặt = WR_FLOOR -> mọi ván bằng nhau.
#   WR_FLOOR  = sàn trọng số của ván cũ (0.35 = ván cũ nhất vẫn nặng bằng 35% ván mới nhất khi NEWEST=1.00). Lớn hơn -> nhớ cầu cũ nhiều hơn.
#               (đặt WR_FLOOR = 1 -> mọi ván bằng nhau · đặt WR_FLOOR = 0 -> quên cầu cũ rất nhanh)
#
#   Với WINDOW=11 / DECAY=0.75 / FLOOR=0.35 / NEWEST=1.00, trọng số (cũ nhất -> mới nhất):
#       0.39 · 0.40 · 0.42 · 0.44 · 0.47 · 0.50 · 0.56 · 0.62 · 0.72 · 0.84 · 1.00
#   -> 3 ván mới nhất nắm ~40% quyền quyết định, 8 ván còn lại nắm ~60% (cũ nhất vẫn còn ~39% sức của ván mới nhất).
#   WR của 1 logic = tổng trọng số các ván logic đó đoán đúng / tổng trọng số các ván đang xét.
#
#   🔄 FLIP TRỌNG SỐ (WR_FLIP_WEIGHT_DEFAULT) — công tắc RIÊNG cho SUN:
#       False (mặc định) -> như trên: ván MỚI nhất nặng nhất, giảm dần về ván cũ nhất.
#       True             -> ĐẢO NGƯỢC bảng trọng số: ván CŨ nhất (trong WR_WINDOW) nặng nhất = WR_WEIGHT_NEWEST,
#                           giảm dần theo cùng công thức tới ván MỚI nhất (nhẹ nhất = tiến về WR_FLOOR).
#       Chỉ đảo thứ tự gán trọng số — DECAY / FLOOR / WEIGHT_NEWEST vẫn chỉnh như cũ (WEIGHT_NEWEST lúc này = trọng số CAO NHẤT).
#       Vd WINDOW=11 / DECAY=0.75 / FLOOR=0.35 / NEWEST=1.00, bật flip -> (cũ nhất -> mới nhất):
#           1.00 · 0.84 · 0.72 · 0.62 · 0.56 · 0.50 · 0.47 · 0.44 · 0.42 · 0.40 · 0.39
#       Muốn đổi mà không sửa file (ưu tiên: cờ dòng lệnh > biến môi trường > WR_FLIP_WEIGHT_DEFAULT):
#           biến môi trường :  SUNVIW_WR_FLIP=1 (bật) | SUNVIW_WR_FLIP=0 (tắt)
#           dòng lệnh       :  python sunviw_api.py --wr-flip  |  --no-wr-flip
#   Cách chia nhóm giữ nguyên: WR < 50% -> nhóm THẤP · WR ≥ 50% -> nhóm CAO, nhóm THẤP đông hơn thì theo nhóm THẤP,
#   còn lại theo nhóm CAO; nhóm được chọn hoà phiếu -> theo đa số tất cả logic.
WR_WINDOW = 13             # số ván gần nhất dùng để tính WR
WR_DECAY = 0.95           # (vô tác dụng khi WR_FLOOR = WR_WEIGHT_NEWEST)
WR_FLOOR = 1.0            # SEQ13v4: BỎ decay -> sàn = trọng số ván mới nhất = 1.0 => MỌI ván trong WR_WINDOW nặng như nhau (bản cũ: DECAY 0.95 · FLOOR 0.75 · NEWEST 1.4 — muốn bật lại: đặt 0.75 / 1.4 ở đây và ở các khối CONFIG từng bàn bên dưới)
WR_WEIGHT_NEWEST = 1.0    # trọng số ván mới nhất (= WR_FLOOR -> không decay)
# dạng Fraction để tính/so sánh chính xác (dùng trong wr_weights)
_W_DECAY = Fraction(str(WR_DECAY))
_W_FLOOR = Fraction(str(WR_FLOOR))
_W_NEWEST = Fraction(str(WR_WEIGHT_NEWEST))
WR_FLIP_WEIGHT_DEFAULT = False   # FLIP trọng số WR của SUN: True = ván CŨ nhất nặng nhất -> giảm dần tới ván MỚI nhất · False = ván mới nhất nặng nhất (mặc định)

# ═══════════════════════════════════════════════════════════════════════════
#  ⚙  CONFIG BẺ FINAL CỦA SUN  (bật / tắt)  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   FLIP_FINAL_DEFAULT = False  ->  TẮT (mặc định): du_doan = final của 21 logic, KHÔNG bẻ
#   FLIP_FINAL_DEFAULT = True   ->  BẬT : du_doan = đảo ngược final (TÀI <-> XỈU)
#
#  Muốn đổi mà không sửa file (ưu tiên: cờ dòng lệnh > biến môi trường > FLIP_FINAL_DEFAULT):
#     biến môi trường :  SUNVIW_FLIP=1  (bật)  |  SUNVIW_FLIP=0  (tắt)
#     dòng lệnh       :  python sunviw_api.py --flip      (bật)
#                        python sunviw_api.py --no-flip   (tắt)
FLIP_FINAL_DEFAULT = False


FLIP_FINAL = _env_bool("SUNVIW_FLIP", FLIP_FINAL_DEFAULT)
WR_FLIP_WEIGHT = _env_bool("SUNVIW_WR_FLIP", WR_FLIP_WEIGHT_DEFAULT)      # flip trọng số WR của SUN (xem CONFIG WR CÓ TRỌNG SỐ)

# ─── ĐÁNH GIÁ ĐÚNG/SAI ───────────────────────────────────────────────────
EVAL_WINDOW = 300           # số phiên gần nhất để đánh giá đúng/sai = WR 100 phiên (hiện thẳng trong /api/predict · tool_dung_sai_10_van) — cần PERSIST_KEEP >= EVAL_WINDOW mới đủ ván để tính
ICON_DUNG = "✅"            # icon hiện cho ván ĐOÁN ĐÚNG trong chuỗi "chuoi" của /api/predict
ICON_SAI = "❌"             # icon hiện cho ván ĐOÁN SAI

# ─── PERSISTENCE (lưu graded để Railway không mất sau restart) ───────────
PERSIST_PATH = os.environ.get("SUNVIW_PERSIST", _data_path("sun15_graded.json"))
PERSIST_KEEP = max(100, EVAL_WINDOW)   # giữ tối đa N graded entry trong file (100 ván; trước là 50 nên WR "100 phiên" thực chất chỉ đo được 50 ván). Tự nâng theo EVAL_WINDOW


SUN_REBUILD_MAX = PERSIST_KEEP   # chấm lại tối đa N ván gần nhất trong lịch sử: lần đầu (file graded trống) chấm đủ N ván; về sau chấm thêm ván MỚI hơn ván đã lưu, và chấm BÙ ván CŨ hơn nếu file chưa đủ PERSIST_KEEP ván


# ═══════════════════════════════════════════════════════════════════════════
#  🧩  CFG THEO BÀN — SUN và các bàn HITCLUB dùng CHUNG một bộ hàm AF / WR / chấm ván, mỗi nơi có config RIÊNG
# ═══════════════════════════════════════════════════════════════════════════
#   Các hàm af_decision / af_mode_wr / decide_final / rebuild_graded / build_result ... nhận tham số `cfg`.
#     · cfg = SUN (mặc định)  -> đọc THẲNG các biến global của SUN ở trên (AF_*, WR_*, FLIP_FINAL, EVAL_WINDOW ...), kể cả khi cờ dòng lệnh đổi chúng lúc chạy -> SUN giữ nguyên hành vi.
#     · cfg = TableCfg(...)    -> bộ config riêng của 1 bàn HITCLUB (khối "CONFIG HITCLUB" bên dưới). Sửa bàn này KHÔNG ảnh hưởng SUN và bàn kia.
class _SunCfg:
    """Proxy chỉ-đọc: cfg.X trả về biến global X của SUN tại thời điểm gọi."""
    _ALIAS = {"W_DECAY": "_W_DECAY", "W_FLOOR": "_W_FLOOR", "W_NEWEST": "_W_NEWEST",
              "REBUILD_MAX": "SUN_REBUILD_MAX", "TIE_LOGIC": "SUN_TIE_LOGIC"}

    def __getattr__(self, name):
        try:
            return globals()[self._ALIAS.get(name, name)]
        except KeyError:
            raise AttributeError(name) from None


SUN = _SunCfg()


class TableCfg:
    """Config đầy đủ của 1 bàn (thuộc tính trùng tên biến config của SUN). Tự chuẩn hoá giống af_apply_limits() của SUN."""

    def __init__(self, name, values):
        self.name = name
        self.__dict__.update(values)
        self.__dict__.setdefault("AF_FLIP_FINAL_CAO", False)    # công tắc bẻ final RIÊNG chế độ CAO (thiếu -> không bẻ)
        self.__dict__.setdefault("AF_FLIP_FINAL_THAP", False)   # công tắc bẻ final RIÊNG chế độ THẤP (thiếu -> không bẻ)
        self.__dict__.setdefault("AF_SWITCH", True)             # đổi chế độ ALL / CAO / THẤP dễ hơn (xem khối ĐỔI CHẾ ĐỘ DỄ HƠN)
        self.__dict__.setdefault("AF_SWITCH_NEED", 6)           # số phiếu để đổi sang chế độ khác (6/13)
        self.__dict__.setdefault("AF_SWITCH_PRIO", True)        # 2 chế độ còn lại cùng đủ phiếu -> ưu tiên theo chế độ ván trước (ALL->CAO · CAO->ALL · THẤP->CAO)
        self.__dict__.setdefault("AF_SWITCH_LEAD", False)       # True = chế độ mới còn phải dẫn đầu duy nhất mới đổi (êm hơn) · False = chỉ cần đủ AF_SWITCH_NEED phiếu
        self.normalize()

    def normalize(self):
        self.AF_FLIP_LOW = min(max(0.0, float(self.AF_FLIP_LOW)), 50.0)
        self.AF_FLIP_HIGH = min(max(50.0, float(self.AF_FLIP_HIGH)), 100.0)
        lo_a, lo_b = sorted((min(max(0.0, float(self.AF_FLIP_LOW_MIN)), 50.0), min(max(0.0, float(self.AF_FLIP_LOW_MAX)), 50.0)))
        hi_a, hi_b = sorted((min(max(50.0, float(self.AF_FLIP_HIGH_MIN)), 100.0), min(max(50.0, float(self.AF_FLIP_HIGH_MAX)), 100.0)))
        self.AF_FLIP_LOW_MIN, self.AF_FLIP_LOW_MAX, self.AF_FLIP_HIGH_MIN, self.AF_FLIP_HIGH_MAX = lo_a, lo_b, hi_a, hi_b
        self.WR_WINDOW = max(1, int(self.WR_WINDOW))
        self.WR_MIN_GAMES = max(1, int(self.WR_MIN_GAMES))
        self.AF_MIN_GAMES = max(1, int(self.AF_MIN_GAMES))
        self.AF_SWITCH_NEED = max(1, int(self.AF_SWITCH_NEED))
        self.AF_MODE_WINDOW = max(1, int(self.AF_MODE_WINDOW))
        self.AF_MODE_MIN = max(1, min(int(self.AF_MODE_MIN), self.AF_MODE_WINDOW))
        self.AF_MODE_BELOW = min(max(0.0, float(self.AF_MODE_BELOW)), 100.0)
        self.EVAL_WINDOW = max(1, int(self.EVAL_WINDOW))
        self.PERSIST_KEEP = max(100, self.EVAL_WINDOW, int(self.PERSIST_KEEP))
        self.REBUILD_MAX = self.PERSIST_KEEP
        self.HIST_KEEP = max(50, int(self.HIST_KEEP))
        self.POLL_SEC = max(1.0, float(self.POLL_SEC))
        self.W_DECAY, self.W_FLOOR, self.W_NEWEST = (Fraction(str(self.WR_DECAY)), Fraction(str(self.WR_FLOOR)), Fraction(str(self.WR_WEIGHT_NEWEST)))

    def as_dict(self):
        """Các tham số config (chỉ khoá IN HOA gốc, bỏ khoá phái sinh) — để hiển thị ở /health."""
        skip = {"W_DECAY", "W_FLOOR", "W_NEWEST", "REBUILD_MAX"}
        return {k: v for k, v in self.__dict__.items() if k.isupper() and k not in skip}


# ─── PANEL /api/html ─────────────────────────────────────────────────────
PANEL_DEFAULT_SHOW = 30    # số ván lịch sử panel hiện mặc định (đổi trực tiếp trên panel, trình duyệt nhớ lại)
HIST_MAX = 300             # trần số ván lịch sử cho ?hist=N và ô nhập trên panel

# ═══════════════════════════════════════════════════════════════════════════
#  🎯  CONFIG HITCLUB (GAME 3 · 2 BÀN)  —  MỖI BÀN MỘT BỘ CONFIG RIÊNG  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   2 bàn (port từ hittxthuong.js / hittxmd5.js):
#       TX THƯỜNG  gid=vgmn_100 · GET /api/predicthittxthuong · file data hit15_txthuong.json (lịch sử xúc xắc + các ván đã chấm của RIÊNG bàn này)
#       TX MD5     gid=vgmn_101 · GET /api/predicthittxmd5    · file data hit15_txmd5.json    (RIÊNG bàn này)
#   Nguồn = HTTP polling: quét API Hit mỗi POLL_SEC giây, tự tích lũy lịch sử (giống cách SUN tích lũy).
#       TX THƯỜNG : cmd 1008 nhả sid · cmd 1003 nhả xúc xắc -> ghép sid + xúc xắc (y như file JS)
#       TX MD5    : cmd 2006 nhả luôn sid + xúc xắc
#   Dự đoán = ĐÚNG bộ 13 logic SEQ13v6 + AF + WR có trọng số của SUN (dùng chung hàm), nhưng mỗi bàn ĐỌC CONFIG RIÊNG ở 2 khối dưới đây.
#   ► Hiện 2 khối đang BẰNG giá trị mặc định hiện tại của SUN (copy lúc ghép). Sửa khối bàn nào CHỈ ảnh hưởng bàn đó — không đụng SUN hay bàn còn lại.
#   ► Ý nghĩa từng thông số giống hệt tên ở các khối "CONFIG AF" · "CONFIG WR CÓ TRỌNG SỐ" · "CONFIG BẺ FINAL" phía trên (AF_* · WR_* · FLIP_FINAL · EVAL_WINDOW · PERSIST_KEEP).
#   Thông số riêng của bàn:
#       ENABLED       True/False  bật/tắt riêng bàn này
#       GID           mã bàn trên API Hit (vgmn_100 = thường · vgmn_101 = MD5)
#       POLL_SEC      chu kỳ quét API (giây)
#       HIST_KEEP     số phiên xúc xắc giữ lại (cửa sổ trượt, như HIST_KEEP của SUN)
#       TIE_LOGIC     logic phá hoà (như SUNVIW_TIE_LOGIC của SUN)
#       CONSEC_CHECK  True = chỉ chấm ván khi số phiên liền nhau (phiên n+1) · False = coi 2 phiên đứng cạnh nhau trong lịch sử là liền nhau
#                     (đặt False nếu số phiên của Hit không tăng đều 1 đơn vị -> không thì tool không chấm được ván nào)
#   Đổi mà không sửa file — biến môi trường <TIỀN TỐ><TÊN>, tiền tố HITTXTHUONG_ hoặc HITTXMD5_:
#       vd. HITTXMD5_AF_ENABLED=0 · HITTXTHUONG_WR_WINDOW=17 · HITTXMD5_FLIP_FINAL=1 · HITTXTHUONG_POLL_SEC=2
#   HITCLUB=0 (hoặc cờ --no-hit) tắt cả 2 bàn · HIT_API_URL đổi địa chỉ API ({GID} được thay bằng GID của bàn) · HITTXTHUONG_PATH / HITTXMD5_PATH đổi file lưu.
HIT_ENABLED = _env_bool("HITCLUB", True)
HIT_API_URL = os.environ.get("HIT_API_URL", "https://jakpotgwab.geightdors.net/glms/v1/notify/taixiu?platform_id=g8&gid={GID}")
HIT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HIT_TXTHUONG_PATH = os.environ.get("HITTXTHUONG_PATH", _data_path("hit15_txthuong.json"))
HIT_TXMD5_PATH = os.environ.get("HITTXMD5_PATH", _data_path("hit15_txmd5.json"))


def _hit_env(prefix, d):
    """Ghi đè giá trị config của 1 bàn từ biến môi trường <prefix><TÊN> (kiểu theo giá trị mặc định; giá trị lạ -> bỏ qua)."""
    out = dict(d)
    for k, v in d.items():
        raw = os.environ.get(prefix + k, "").strip()
        if not raw:
            continue
        try:
            if isinstance(v, bool):
                low = raw.lower()
                if low in ("1", "true", "yes", "on"):
                    out[k] = True
                elif low in ("0", "false", "no", "off"):
                    out[k] = False
            elif isinstance(v, (int, float)):
                out[k] = float(raw) if "." in raw else int(raw)
            else:
                out[k] = raw
        except ValueError:
            pass
    return out


# ─ BÀN 1: TX THƯỜNG (gid vgmn_100) — config RIÊNG, chỉnh ở đây ─
HIT_TXTHUONG_CFG = TableCfg("hittxthuong", _hit_env("HITTXTHUONG_", {
    "ENABLED": True,
    "GID": "vgmn_100",
    "POLL_SEC": 3.0,
    "HIST_KEEP": HIST_KEEP,
    "TIE_LOGIC": "AFM",
    "CONSEC_CHECK": True,
    # WR có trọng số
    "WR_WINDOW": 10, "WR_DECAY": 0.95, "WR_FLOOR": 1.0, "WR_WEIGHT_NEWEST": 1.0, "WR_FLIP_WEIGHT": False, "WR_MIN_GAMES": 1,
    # bẻ final (dùng khi AF tắt)
    "FLIP_FINAL": False,
    # AF: bước 1 bẻ logic
    "AF_ENABLED": True, "AF_FLIP_LOW": 37, "AF_FLIP_HIGH": 68,
    "AF_FLIP_BAND": True, "AF_FLIP_LOW_MIN": 0, "AF_FLIP_LOW_MAX": 40, "AF_FLIP_HIGH_MIN": 55, "AF_FLIP_HIGH_MAX": 80,
    "AF_MIN_GAMES": 7,
    # AF: bước 2 nhóm CAO/THẤP
    "AF_GROUP_FLIPPED_ONLY": True, "AF_GROUP_NEED_MAJORITY": True,
    "AF_SWITCH": True, "AF_SWITCH_NEED": 6, "AF_SWITCH_LEAD": False, "AF_SWITCH_PRIO": True,       # đổi chế độ ALL / CAO / THẤP chỉ cần 6/13 phiếu (thay vì đa số 7/13) — AF_SWITCH=False = về cách gốc · AF_SWITCH_LEAD=True = chế độ mới phải dẫn đầu mới đổi
    # AF: bước 3 bẻ theo WR chế độ (mặc định TẮT)
    "AF_MODE_FLIP": False, "AF_MODE_WINDOW": 13, "AF_MODE_MIN": 7, "AF_MODE_BELOW": 45,
    # AF: bẻ final riêng
    "AF_FLIP_FINAL": False, "AF_FLIP_FINAL_CT": False, "AF_FLIP_FINAL_CAO": False, "AF_FLIP_FINAL_THAP": False, "AF_FLIP_FINAL_ALL": True,   # CAO / THẤP tách riêng (đang bật cả 2 = giống _CT cũ)
    # đánh giá đúng/sai + số ván lưu
    "EVAL_WINDOW": 300, "PERSIST_KEEP": 100,
}))

# ─ BÀN 2: TX MD5 (gid vgmn_101) — config RIÊNG, chỉnh ở đây ─
HIT_TXMD5_CFG = TableCfg("hittxmd5", _hit_env("HITTXMD5_", {
    "ENABLED": True,
    "GID": "vgmn_101",
    "POLL_SEC": 3.0,
    "HIST_KEEP": HIST_KEEP,
    "TIE_LOGIC": "AFM",
    "CONSEC_CHECK": True,
    # WR có trọng số
    "WR_WINDOW": 7, "WR_DECAY": 0.95, "WR_FLOOR": 1.0, "WR_WEIGHT_NEWEST": 1.0, "WR_FLIP_WEIGHT": False, "WR_MIN_GAMES": 1,
    # bẻ final (dùng khi AF tắt)
    "FLIP_FINAL": False,
    # AF: bước 1 bẻ logic
    "AF_ENABLED": True, "AF_FLIP_LOW": 37, "AF_FLIP_HIGH": 63,
    "AF_FLIP_BAND": True, "AF_FLIP_LOW_MIN": 0, "AF_FLIP_LOW_MAX": 35, "AF_FLIP_HIGH_MIN": 55, "AF_FLIP_HIGH_MAX": 83,
    "AF_MIN_GAMES": 7,
    # AF: bước 2 nhóm CAO/THẤP
    "AF_GROUP_FLIPPED_ONLY": True, "AF_GROUP_NEED_MAJORITY": True,
    "AF_SWITCH": True, "AF_SWITCH_NEED": 6, "AF_SWITCH_LEAD": False, "AF_SWITCH_PRIO": True,       # đổi chế độ ALL / CAO / THẤP chỉ cần 6/13 phiếu (thay vì đa số 7/13) — AF_SWITCH=False = về cách gốc · AF_SWITCH_LEAD=True = chế độ mới phải dẫn đầu mới đổi
    # AF: bước 3 bẻ theo WR chế độ (mặc định TẮT)
    "AF_MODE_FLIP": False, "AF_MODE_WINDOW": 13, "AF_MODE_MIN": 7, "AF_MODE_BELOW": 45,
    # AF: bẻ final riêng
    "AF_FLIP_FINAL": False, "AF_FLIP_FINAL_CT": False, "AF_FLIP_FINAL_CAO": True, "AF_FLIP_FINAL_THAP": False, "AF_FLIP_FINAL_ALL": True,   # CAO / THẤP tách riêng (đang tắt cả 2 = giống cũ)
    # đánh giá đúng/sai + số ván lưu
    "EVAL_WINDOW": 300, "PERSIST_KEEP": 100,
}))


# ═══════════════════════════════════════════════════════════════════════════
#  🟣  CONFIG LC (GAME 4 · 2 BÀN: LC MD5 + LC HŨ)  —  MỖI BÀN MỘT BỘ CONFIG RIÊNG, DATA RIÊNG  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   2 bàn (key game "lc79", tiền tố LC79- — 1 key LC79 dùng được CẢ 2 bàn):
#       LC MD5 (tên cũ: Tele68 MD5) · GET /api/predictlcmd5 · file data tele68_txmd5.json (GIỮ tên file cũ để không mất lịch sử / WR đã học)
#                                     nguồn https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=<TOKEN>
#       LC HŨ                       · GET /api/predictlchu  · file data lc_hu.json
#                                     nguồn https://wtx.tele68.com/v1/tx/sessions?cp=R&cl=R&pf=web&at=<TOKEN>
#   Endpoint cũ /api/predicttele68txmd5 vẫn chạy (alias của /api/predictlcmd5) để tool đang gọi tên cũ không hỏng.
#   Cả 2 nguồn trả CẢ DANH SÁCH {"list":[{id, resultTruyenThong, dices:[a,b,c], point}, ...]} (~105 phiên, phiên ĐẦU = MỚI NHẤT) — khác các game kia chỉ trả 1 phiên mới nhất.
#   Cách tool làm (GIỐNG HỆT nhau ở 2 bàn):
#       · Mỗi lần quét: đọc TOÀN BỘ list, chỉ LƯU THÊM các phiên CHƯA có trong data (phiên đã học giữ nguyên) -> tích lũy tối đa HIST_KEEP phiên.
#       · Dự đoán = phiên MỚI NHẤT + 1 (bộ 13 logic SEQ13v6 + AF + WR như SUN/Hit, đọc config RIÊNG của bàn ở 2 khối dưới).
#       · Dự đoán được giữ trong file data (trường "pending") cho tới khi API trả ra kết quả đúng phiên đó -> khi phiên đó xuất hiện, tool so sánh & chấm ĐÚNG / SAI (vào lich_su + WR/AF).
#       · Tài/Xỉu tính theo TỔNG xúc xắc (>= 11 = Tài), không đọc resultTruyenThong.
#   Panel /api/html có 2 tab "LC MD5" · "LC Hũ" (mỗi tab có nút Xóa lịch sử / Tính lại theo config / Xóa data riêng).
#   Ý nghĩa thông số: giống các khối "CONFIG HITCLUB" / "CONFIG AF" / "CONFIG WR CÓ TRỌNG SỐ" phía trên. Sửa khối bàn nào CHỈ ảnh hưởng bàn đó.
#   ► Khối LC HŨ đang là BẢN SAO config của LC MD5 (chưa backtest riêng cho Hũ) — chỉnh riêng khi đã có số liệu.
#   Đổi mà không sửa file (env):
#       LC_ENABLED=0 (tắt cả 2 bàn; tên cũ TELE68_ENABLED vẫn nhận) · LC_MD5_API_URL (tên cũ TELE68_API_URL) · LC_HU_API_URL — dùng khi token `at=` đổi
#       LC_REFERER (tên cũ TELE68_REFERER; thêm header Referer/Origin nếu server đòi) · LC_MD5_PATH (tên cũ TELE68_TXMD5_PATH) · LC_HU_PATH đổi file lưu
#       LCMD5_<TÊN> / LCHU_<TÊN> ghi đè từng thông số của khối config (vd. LCMD5_AF_ENABLED=0 · LCHU_WR_WINDOW=17 · LCHU_POLL_SEC=2); tiền tố cũ TELE68TXMD5_ vẫn nhận cho LC MD5.
LC_ENABLED = _env_bool("LC_ENABLED", _env_bool("TELE68_ENABLED", True))
LC_MD5_API_URL = os.environ.get("LC_MD5_API_URL") or os.environ.get("TELE68_API_URL") or "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=6cd221bcc034632d6cb745a302c066c6"
LC_HU_API_URL = os.environ.get("LC_HU_API_URL") or "https://wtx.tele68.com/v1/tx/sessions?cp=R&cl=R&pf=web&at=ca2f3e546e6d4c9ea5736bdfba726929"
LC_REFERER = (os.environ.get("LC_REFERER") or os.environ.get("TELE68_REFERER") or "").strip()
LC_MD5_PATH = os.environ.get("LC_MD5_PATH") or os.environ.get("TELE68_TXMD5_PATH") or _data_path("tele68_txmd5.json")
LC_HU_PATH = os.environ.get("LC_HU_PATH") or _data_path("lc_hu.json")

# ─ BÀN 1: LC MD5 (tên cũ Tele68 MD5) — config RIÊNG, chỉnh ở đây ─
LC_MD5_CFG = TableCfg("lcmd5", _hit_env("LCMD5_", _hit_env("TELE68TXMD5_", {
    "ENABLED": True,
    "GID": "lc_md5",
    "POLL_SEC": 3.0,
    "HIST_KEEP": HIST_KEEP,
    "TIE_LOGIC": "AFM",
    "CONSEC_CHECK": True,
    # WR có trọng số
    "WR_WINDOW": 13, "WR_DECAY": 0.95, "WR_FLOOR": 1.0, "WR_WEIGHT_NEWEST": 1.0, "WR_FLIP_WEIGHT": False, "WR_MIN_GAMES": 1,
    # bẻ final (dùng khi AF tắt)
    "FLIP_FINAL": False,
    # AF: bước 1 bẻ logic
    "AF_ENABLED": True, "AF_FLIP_LOW": 37, "AF_FLIP_HIGH": 63,
    "AF_FLIP_BAND": True, "AF_FLIP_LOW_MIN": 0, "AF_FLIP_LOW_MAX": 40, "AF_FLIP_HIGH_MIN": 57, "AF_FLIP_HIGH_MAX": 100,
    "AF_MIN_GAMES": 8,
    # AF: bước 2 nhóm CAO/THẤP
    "AF_GROUP_FLIPPED_ONLY": True, "AF_GROUP_NEED_MAJORITY": True,
    "AF_SWITCH": True, "AF_SWITCH_NEED": 5, "AF_SWITCH_LEAD": False, "AF_SWITCH_PRIO": True,       # đổi chế độ ALL / CAO / THẤP chỉ cần N phiếu (thay vì đa số 7/13) — AF_SWITCH=False = về cách gốc · AF_SWITCH_LEAD=True = chế độ mới phải dẫn đầu mới đổi
    # AF: bước 3 bẻ theo WR chế độ (WR chế độ < AF_MODE_BELOW % -> đảo final TÀI<->XỈU)
    "AF_MODE_FLIP": False, "AF_MODE_WINDOW": 9, "AF_MODE_MIN": 7, "AF_MODE_BELOW": 45,
    # AF: bẻ final riêng
    "AF_FLIP_FINAL": False, "AF_FLIP_FINAL_CT": False, "AF_FLIP_FINAL_CAO": True, "AF_FLIP_FINAL_THAP": False, "AF_FLIP_FINAL_ALL": True,   # bộ backtest 300 ván (ALL cao nhất + ALL nhiều ván nhất): KHÔNG bẻ final chế độ nào
    # đánh giá đúng/sai + số ván lưu
    "EVAL_WINDOW": 500, "PERSIST_KEEP": 300,
})))

# ─ BÀN 2: LC HŨ — config RIÊNG, chỉnh ở đây (đang là bản sao config LC MD5) ─
LC_HU_CFG = TableCfg("lchu", _hit_env("LCHU_", {
    "ENABLED": True,
    "GID": "lc_hu",
    "POLL_SEC": 3.0,
    "HIST_KEEP": HIST_KEEP,
    "TIE_LOGIC": "AFM",
    "CONSEC_CHECK": True,
    # WR có trọng số
    "WR_WINDOW": 20, "WR_DECAY": 0.95, "WR_FLOOR": 1.0, "WR_WEIGHT_NEWEST": 1.0, "WR_FLIP_WEIGHT": False, "WR_MIN_GAMES": 1,
    # bẻ final (dùng khi AF tắt)
    "FLIP_FINAL": False,
    # AF: bước 1 bẻ logic
    "AF_ENABLED": True, "AF_FLIP_LOW": 37, "AF_FLIP_HIGH": 63,
    "AF_FLIP_BAND": True, "AF_FLIP_LOW_MIN": 20, "AF_FLIP_LOW_MAX": 47, "AF_FLIP_HIGH_MIN": 57, "AF_FLIP_HIGH_MAX": 75,
    "AF_MIN_GAMES": 8,
    # AF: bước 2 nhóm CAO/THẤP
    "AF_GROUP_FLIPPED_ONLY": True, "AF_GROUP_NEED_MAJORITY": True,
    "AF_SWITCH": True, "AF_SWITCH_NEED": 5, "AF_SWITCH_LEAD": False, "AF_SWITCH_PRIO": True,
    # AF: bước 3 bẻ theo WR chế độ (WR chế độ < AF_MODE_BELOW % -> đảo final TÀI<->XỈU)
    "AF_MODE_FLIP": False, "AF_MODE_WINDOW": 9, "AF_MODE_MIN": 7, "AF_MODE_BELOW": 45,
    # AF: bẻ final riêng
    "AF_FLIP_FINAL": False, "AF_FLIP_FINAL_CT": False, "AF_FLIP_FINAL_CAO": True, "AF_FLIP_FINAL_THAP": False, "AF_FLIP_FINAL_ALL": True,
    # đánh giá đúng/sai + số ván lưu
    "EVAL_WINDOW": 500, "PERSIST_KEEP": 300,
}))

# ═══════════════════════════════════════════════════════════════════════════
#  🗑  CONFIG XÓA LỊCH SỬ DỰ ĐOÁN (nút "Xóa lịch sử" ở panel /api/html)  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Nút này CHỈ làm sạch phần HIỂN THỊ: danh sách "lich_su" + số liệu đúng/sai (tool_dung_sai_*, % đúng, chuỗi ✅❌ trên panel).
#   Cách làm: lưu 1 MỐC phiên cho từng game (SUN / HIT thường / HIT MD5) — ván có phiên <= mốc bị ẩn khỏi lịch sử / thống kê hiển thị.
#   KHÔNG xóa / sửa bất cứ dữ liệu nào khác: lịch sử xúc xắc (hist) · các ván đã chấm + vote từng logic (graded) · key / IP / cấu hình.
#   -> 13 logic SUN (và các bàn Hit), WR có trọng số, AF (CAO/THẤP, WR chế độ), do_tin_cay, du_doan của phiên đang dự đoán: GIỮ NGUYÊN 100%, vì chúng vẫn đọc đủ dữ liệu cũ.
#   Mốc lưu file riêng nên còn sau khi restart / deploy (cần Volume như các file khác trên Railway).
#   HIST_CLEAR_ENABLED_DEFAULT  True = cho xóa · False = tắt hẳn tính năng (endpoint trả 403)  (env SUNVIW_HIST_CLEAR=1|0)
#   HIST_CLEAR_PATH             file lưu mốc (env SUNVIW_HISTCLEAR_PATH)
#   Endpoint: POST /api/history/clear  {"game": "sun" | "hittxthuong" | "hittxmd5" | "hitclub" | "all"}  (cần key người dùng; key chỉ xóa được lịch sử của game nó thuộc về)
HIST_CLEAR_ENABLED_DEFAULT = True
HIST_CLEAR_ENABLED = _env_bool("SUNVIW_HIST_CLEAR", HIST_CLEAR_ENABLED_DEFAULT)
HIST_CLEAR_PATH = os.environ.get("SUNVIW_HISTCLEAR_PATH", _data_path("sun15_histclear.json"))

# ═══════════════════════════════════════════════════════════════════════════
#  🌐  CONFIG IP — THEO DÕI IP TRUY CẬP (tab "IP" của panel /api/html)  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Mỗi request tới /api/predictsun · /api/predicthittxthuong · /api/predicthittxmd5 · /api/html được ghi lại IP client. /health, "/", /api/ips (chính tab IP) KHÔNG tính.
#   IP_TRACK_ENABLED_DEFAULT  True = theo dõi · False = tắt (env SUNVIW_IPS=1|0)
#   IP_ACTIVE_SEC             "đang dùng" = có request trong N giây gần nhất (env SUNVIW_IP_ACTIVE)
#   IP_KEEP                   giữ tối đa N IP (đầy thì xoá IP lâu không thấy nhất)
#   IP_PATH                   file lưu danh sách IP đã từng dùng (env SUNVIW_IPS_PATH). Railway nên trỏ vào ổ đĩa bền, không thì /tmp bị xoá mỗi lần deploy.
#   IP_TRUST_PROXY_DEFAULT    True = đọc IP thật từ X-Forwarded-For / X-Real-IP (đúng khi chạy sau Railway / Cloudflare / nginx) · False = chỉ dùng IP kết nối trực tiếp
#                             (env SUNVIW_IP_PROXY=1|0). Lưu ý: chạy KHÔNG qua proxy mà để True thì client tự đặt X-Forwarded-For giả được -> đặt False.
#   IP_HEADER                 (tuỳ chọn) ép đọc IP từ 1 header cụ thể, vd. CF-Connecting-IP (env SUNVIW_IP_HEADER)
#   IP_ADMIN_KEY              (khuyến nghị) đặt thì /api/ips và tab IP đòi key: header X-Admin-Key hoặc ?key=  (env SUNVIW_ADMIN_KEY). Để trống = ai mở panel cũng thấy danh sách IP.
IP_TRACK_ENABLED_DEFAULT = True
IP_ACTIVE_SEC = _env_num("SUNVIW_IP_ACTIVE", 60, int)
IP_KEEP = 500
IP_SAVE_SEC = 10.0         # ghi file tối đa mỗi N giây (IP mới xuất hiện thì ghi ngay)
IP_PATH = os.environ.get("SUNVIW_IPS_PATH", _data_path("sunviw_ips.json"))
IP_TRUST_PROXY_DEFAULT = True
IP_HEADER = os.environ.get("SUNVIW_IP_HEADER", "").strip()
IP_ADMIN_KEY = os.environ.get("SUNVIW_ADMIN_KEY", "")
IP_TRACK_ENABLED = _env_bool("SUNVIW_IPS", IP_TRACK_ENABLED_DEFAULT)
IP_TRUST_PROXY = _env_bool("SUNVIW_IP_PROXY", IP_TRUST_PROXY_DEFAULT)

TAI, XIU = "TÀI", "XỈU"

# ─── HELPERS ─────────────────────────────────────────────────────────────
def actual_of(total):
    return TAI if total >= 11 else XIU


def flip_pred(p):
    """Bẻ: đảo TÀI <-> XỈU (giá trị khác giữ nguyên)."""
    return XIU if p == TAI else TAI if p == XIU else p


def vote_result(preds):
    tai = sum(1 for x in preds if x == TAI)
    xiu = sum(1 for x in preds if x == XIU)
    if tai == xiu:
        return 'SKIP'
    return TAI if tai > xiu else XIU


def compute_all(hist):
    """Vote của 13 logic SUN (SEQ13v6) cho phiên KẾ TIẾP, từ lịch sử `hist` (cũ -> mới; mỗi phần tử có actual / total / d1 d2 d3 / phien). Thứ tự = SUN_NAMES.
    MỖI LOGIC CHỈ ĐỌC LOGIC_WIN[tên] VÁN GẦN NHẤT (cửa sổ mạnh nhất của logic đó, mọi ván trọng số như nhau). Cả 13 logic LUÔN bỏ phiếu (không cổng, không phiếu trắng):
    chưa đủ lịch sử cho một logic (hoặc logic lỗi) -> logic đó tạm theo kết quả ván trước."""
    S = {"y": [1 if r["actual"] == TAI else 0 for r in hist], "t": [int(r["total"]) for r in hist],
         "d": [(r["d1"], r["d2"], r["d3"]) for r in hist],
         "p": [int(r["phien"]) for r in hist]}              # số phiên
    n = len(S["y"])
    fb = S["y"][-1] if n else 0
    cache = {}
    out = []
    for nm, fn in SUN_LOGICS:
        W = LOGIC_WIN.get(nm, 0)
        if W and n > W:
            Sw = cache.get(W)
            if Sw is None:
                Sw = cache[W] = {k: v[-W:] for k, v in S.items()}
        else:
            Sw = S
        try:
            v = fn(Sw)
        except Exception:  # noqa: BLE001 - 1 logic lỗi không được làm sập cả dự đoán
            v = None
        out.append(TAI if (fb if v is None else v) == 1 else XIU)
    return out


# ─── 13 LOGIC CỦA SUN (thuần Python, tự học online từ lịch sử — mô tả ở docstring đầu file) ───
from collections import defaultdict


def _tb1(t):
    return 0 if t <= 7 else 1 if t <= 10 else 2 if t <= 13 else 3


def _vote01(n1, n0, fb):
    return 1 if n1 > n0 else 0 if n0 > n1 else fb


def _win_counts(n, keyfn, y, W, start):
    """Đếm (n0, n1) theo khoá keyfn(j) trên các bước j ∈ [max(start, n-W), n-1] (mục tiêu y[j])."""
    cnt = defaultdict(lambda: [0, 0])
    for j in range(max(start, n - W), n):
        cnt[keyfn(j)][y[j]] += 1
    return cnt


def lg_ppm(S, K, W, alpha):
    y = S["y"]
    n = len(y)
    if n <= K:
        return None
    s = 0.0
    for k in range(1, K + 1):
        key = lambda j, k=k: tuple(y[j - k:j])
        c = _win_counts(n, key, y, W, k)
        n0, n1 = c[key(n)] if key(n) in c else (0, 0)
        m = n0 + n1
        if m > 0:
            pr = (n1 + 0.5) / (m + 1.0)
            s += (k ** alpha) * (m / (m + 3.0)) * math.log(pr / (1 - pr))
    return 1 if s > 0 else 0 if s < 0 else y[-1]


# ── logic thêm ở bản SEQ14/SEQ13v4 (REGIME; LAGAC · SGDLR · ARSUM · EWMA · PERIOD đã bị loại). Trả 1 = TÀI · 0 = XỈU · None = bỏ phiếu trắng (compute_all -> theo kết quả ván trước) ──
def lg_regime(S, K=20, W=250, m=8.0):
    """REGIME: nhịp đảo cầu của K ván gần nhất chia 4 nhóm; học online P(ván sau ĐẢO | nhóm) trong W ván (co về 50%, m=8). Rate > 50% -> đảo cầu · < 50% -> bệt."""
    y = S["y"]
    n = len(y)
    if n < K + 40:
        return None
    a = [0] + [1 if y[i] != y[i - 1] else 0 for i in range(1, n)]
    c = [0]
    for v in a:
        c.append(c[-1] + v)                                 # c[i+1] = a[0..i]
    fr = lambda j: (c[j] - c[j - K + 1]) / (K - 1)          # nhịp đảo trong y[j-K .. j-1] (K-1 bước chuyển)
    bk = lambda r: 0 if r <= .35 else 1 if r <= .5 else 2 if r <= .65 else 3
    cnt = defaultdict(lambda: [0, 0])
    for j in range(max(K, n - W), n):
        k = bk(fr(j))
        cnt[k][1] += 1
        cnt[k][0] += a[j]
    kk = bk(fr(n))
    alt, tot = cnt[kk] if kk in cnt else (0, 0)
    rate = (alt + 0.5 * m) / (tot + m)
    if rate > 0.5:
        return 1 - y[-1]
    if rate < 0.5:
        return y[-1]
    return None


def _gj_solve(A, b):
    """Giải A x = b bằng Gauss–Jordan (pivot từng phần). Trả None nếu suy biến."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            return None
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        for j in range(c, n + 1):
            M[c][j] /= piv
        for r in range(n):
            if r != c and M[r][c] != 0.0:
                f = M[r][c]
                for j in range(c, n + 1):
                    M[r][j] -= f * M[c][j]
    return [M[i][n] for i in range(n)]


def lg_blrev(S, W=250, NL=8, iters=5):
    """BLREV: hồi quy logistic Bayes (Newton/IRLS) trên W ván gần nhất. Đặc trưng: bias (không phạt) · 8 kết quả gần nhất (±1) · 2 tổng gần nhất (chuẩn hoá) · độ dài đợt hiện tại có dấu.
    Hệ số phạt ridge α KHÔNG đặt tay mà tự chọn theo bằng chứng (MacKay: α = γ / |w|²) -> chuỗi ngẫu nhiên thì α lớn, hệ số co về 0, dự đoán ≈ theo thiên lệch chung; có cấu trúc thì α nhỏ lại.
    Nâng cấp của SGDLR (SGDLR cố định tốc độ học + L2 + 2 epoch). Luôn bỏ phiếu (logic THƯỜNG); thiếu dữ liệu -> None -> theo ván trước."""
    y, t = S["y"], S["t"]
    n = len(y)
    lo = max(NL + 3, n - W)
    if n - lo < 100:
        return None

    def feat(j):
        f = [2.0 * y[j - k] - 1.0 for k in range(1, NL + 1)]
        f += [(t[j - 1] - 10.5) / 3.0, (t[j - 2] - 10.5) / 3.0]
        r = 1
        while r < 8 and j - 1 - r >= 0 and y[j - 1 - r] == y[j - 1]:
            r += 1
        f.append((2.0 * y[j - 1] - 1.0) * r / 8.0)
        return f

    X = [[1.0] + feat(j) for j in range(lo, n)]
    Yv = y[lo:n]
    d = len(X[0])
    w = [0.0] * d
    alpha = 5.0
    for _ in range(iters):
        H = [[0.0] * d for _ in range(d)]
        g = [0.0] * d
        for x, yy in zip(X, Yv):
            z = max(-30.0, min(30.0, sum(a * b for a, b in zip(w, x))))
            p = 1.0 / (1.0 + math.exp(-z))
            sv = p * (1.0 - p)
            e = yy - p
            for a_ in range(d):
                xa = x[a_]
                g[a_] += e * xa
                sa = sv * xa
                Ha = H[a_]
                for b_ in range(a_, d):
                    Ha[b_] += sa * x[b_]
        for a_ in range(d):
            for b_ in range(a_):
                H[a_][b_] = H[b_][a_]
        for a_ in range(1, d):
            g[a_] -= alpha * w[a_]
            H[a_][a_] += alpha
        H[0][0] += 1e-6
        dw = _gj_solve(H, g)
        if dw is None:
            return None
        w = [wi + di for wi, di in zip(w, dw)]
        ww = sum(wi * wi for wi in w[1:])
        if ww > 1e-9:
            tr = sum(1.0 / H[a_][a_] for a_ in range(1, d))
            gamma = max(0.0, (d - 1) - alpha * tr)
            alpha = min(max(gamma / ww, 0.5), 2000.0)
    z = sum(a * b for a, b in zip(w, [1.0] + feat(n)))
    return 1 if z > 0 else 0 if z < 0 else None


# ── 4 logic giữ lại từ SEQ13v4 (KNNH · RUNCTX · DIEMK · BAL; TVBIAS · RLSFF đã bỏ ở SEQ13v4) ──────────────────────
# Nguyên tắc chung: cả 4 là logic THƯỜNG — LUÔN bỏ phiếu (không có cổng thống kê, không phiếu trắng). Thiếu bằng chứng -> mô hình tự co về prior rồi vẫn lấy dấu của xác suất;
# chỉ khi chưa đủ lịch sử (n < ~30-40 ván) mới trả None -> compute_all cho theo kết quả ván trước. Trên chuỗi ngẫu nhiên mọi logic ≈ 50% (không logic nào tạo lợi thế trên RNG công bằng).
def _sgn_vote(s, eps=1e-12):
    return 1 if s > eps else 0 if s < -eps else None


def lg_knnh(S, Ls=(6, 10, 14), K=15, W=200):
    """KNNH: láng giềng gần nhất MỜ trên chuỗi Tài/Xỉu. Với mỗi độ dài đoạn L ∈ (6, 10, 14): so L ván cuối với MỌI đoạn L ván trong cửa sổ bằng khoảng cách Hamming có trọng số
    (ván càng gần càng nặng; +0.5 nếu nhóm tổng ván trước khác), lấy K đoạn gần nhất, bỏ phiếu theo kết quả NGAY SAU mỗi đoạn với trọng số 1/(1+khoảng cách). Trung bình 3 độ dài -> dấu.
    Khớp MỜ (không đòi khớp chính xác) nên luôn có láng giềng để bỏ phiếu."""
    y, t = S["y"], S["t"]
    n = len(y)
    if n < 30:
        return None
    tq = _tb1(t[n - 1])
    tot, used = 0.0, 0
    for L in Ls:
        lo = max(L, n - W)
        if n - lo < 20:
            continue
        q = y[n - L:n]
        wp = [1.0 + i / float(L) for i in range(L)]                 # ván càng gần (cuối đoạn) trọng số càng cao
        cand = []
        for j in range(lo, n):
            d = 0.5 if _tb1(t[j - 1]) != tq else 0.0
            base = j - L
            for i in range(L):
                if y[base + i] != q[i]:
                    d += wp[i]
            cand.append((d, -j, y[j]))                              # hoà khoảng cách -> ưu tiên đoạn mới hơn
        cand.sort()
        sw = sv = 0.0
        for d, _nj, yy in cand[:K]:
            w = 1.0 / (1.0 + d)
            sw += w
            sv += w * (2 * yy - 1)
        if sw > 0:
            tot += sv / sw
            used += 1
    if not used:
        return None
    return _sgn_vote(tot)


def lg_runctx(S, cl=7, cp=4, m=4.0):
    """RUNCTX: mô hình hazard theo ĐỘ DÀI ĐỢT có ngữ cảnh. Mỗi bước trong lịch sử: 'đợt đang dài l ván (cắt ở 7), 2 đợt trước dài p1 / p2 (cắt ở 4)' -> đợt có KẾT THÚC ở bước này không.
    Hazard ước lượng theo 4 tầng back-off (l,p1,p2) -> (l,p1) -> (l) -> chung, mỗi tầng co về tầng dưới (m=4) nên ngữ cảnh ít mẫu tự dựa vào tầng thô hơn.
    P(đợt kết thúc ngay ván này) > 50% -> ĐẢO cầu, < 50% -> BỆT. Bắt cầu 1-1, 2-2, 1-2-1, 2-1-2… ở tầng độ dài đợt (PPM6 chỉ thấy 6 ký tự liền nhau)."""
    y = S["y"]
    n = len(y)
    if n < 30:
        return None
    runs = []
    for v in y:
        if runs and runs[-1][0] == v:
            runs[-1][1] += 1
        else:
            runs.append([v, 1])
    kl = len(runs) - 1
    c3 = defaultdict(lambda: [0, 0])
    c2 = defaultdict(lambda: [0, 0])
    c1 = defaultdict(lambda: [0, 0])
    c0 = [0, 0]
    for k, (_s, ln) in enumerate(runs):
        p1 = min(runs[k - 1][1], cp) if k >= 1 else 0
        p2 = min(runs[k - 2][1], cp) if k >= 2 else 0
        for l in range(1, ln + 1):
            if k == kl and l == ln:                                 # bước hiện tại của đợt đang chạy = câu hỏi, chưa có đáp án
                break
            e = 1 if l == ln else 0                                 # 1 = đợt kết thúc sau l ván
            lc = min(l, cl)
            c3[(lc, p1, p2)][e] += 1
            c2[(lc, p1)][e] += 1
            c1[lc][e] += 1
            c0[e] += 1
    p1q = min(runs[-2][1], cp) if len(runs) >= 2 else 0
    p2q = min(runs[-3][1], cp) if len(runs) >= 3 else 0
    lq = min(runs[-1][1], cl)
    h = (c0[1] + 1.0) / (c0[0] + c0[1] + 2.0)
    for tbl, key in ((c1, lq), (c2, (lq, p1q)), (c3, (lq, p1q, p2q))):
        a = tbl[key] if key in tbl else (0, 0)
        h = (a[1] + m * h) / (a[0] + a[1] + m)
    if h > 0.5:
        return 1 - y[-1]
    if h < 0.5:
        return y[-1]
    return None


def lg_diemk(S, W=200, m=6.0):
    """DIEMK: Markov mức TỪNG VIÊN xúc xắc. Mỗi viên (3 vị trí) có bảng 'mức viên đó ván trước (thấp 1-2 · giữa 3-4 · cao 5-6) -> phân phối mặt 1..6 ván sau', học trong W ván,
    làm mịn Dirichlet về phân phối chung của viên đó (m=6). Nhân chập 3 phân phối -> P(tổng >= 11). Đi đường KHÁC với CT2/CDT cũ (gom nhóm tổng làm mất thông tin từng viên)
    và với bản gom nhóm tổng cũ (mất thông tin từng viên)."""
    d = S["d"]
    n = len(d)
    if n < 30:
        return None
    try:
        lv = lambda v: 0 if v <= 2 else 1 if v <= 4 else 2
        lo = max(1, n - W)
        dists = []
        for k in range(3):
            cnt = [[0] * 7 for _ in range(3)]
            mg = [0] * 7
            for j in range(lo, n):
                v = int(d[j][k])
                if not 1 <= v <= 6:
                    return None
                cnt[lv(int(d[j - 1][k]))][v] += 1
                mg[v] += 1
            tm = float(sum(mg))
            mp = [(mg[v] + 1.0) / (tm + 6.0) for v in range(1, 7)]
            c = cnt[lv(int(d[n - 1][k]))]
            tc = float(sum(c))
            dists.append([(c[v] + m * mp[v - 1]) / (tc + m) for v in range(1, 7)])
    except (TypeError, ValueError, IndexError):
        return None
    pt = 0.0
    for a in range(6):
        for b in range(6):
            pab = dists[0][a] * dists[1][b]
            for c_ in range(6):
                if a + b + c_ + 3 >= 11:
                    pt += pab * dists[2][c_]
    return _sgn_vote(pt - 0.5, 1e-9)


def lg_bal(S, wins=(8, 16, 32, 64), minn=30):
    """BAL: 'cân cầu' — độ lệch Tài-Xỉu (z-score) trong cửa sổ 8 / 16 / 32 / 64 ván gần nhất. Với mỗi cửa sổ, học TRÊN LỊCH SỬ hệ số hồi quy ridge: độ lệch cửa sổ đó -> kết quả ván sau
    (hệ số âm = hồi quy về trung bình / nhà cái cân bằng, dương = đà tiếp tục). Điểm = Σ hệ số × độ lệch hiện tại -> dấu. Dấu của hệ số do dữ liệu quyết định, không đặt tay;
    RNG độc lập thì hệ số ≈ 0 và logic chỉ bỏ phiếu theo nhiễu nhỏ."""
    y = S["y"]
    n = len(y)
    if n < 40:
        return None
    c = [0]
    for v in y:
        c.append(c[-1] + v)
    score, used = 0.0, 0
    for w in wins:
        N = n - w
        if N < minn:
            continue
        sd = 0.5 * math.sqrt(w)
        f = [(c[j] - c[j - w] - w / 2.0) / sd for j in range(w, n)]
        tg = y[w:n]
        yb = sum(tg) / float(N)
        fb = sum(f) / float(N)                                      # TRUNG TÂM hoá cả độ lệch lẫn kết quả: logic chỉ đo 'lệch hơn mức thường lệ', thiên lệch cố định để các logic khác (CMIXL · SPARSE) lo
        sxy = sum((fi - fb) * (yy - yb) for fi, yy in zip(f, tg))
        sxx = sum((fi - fb) ** 2 for fi in f)
        beta = sxy / (sxx + 1.0 * N)                                # ridge: co hệ số về 0 khi tín hiệu yếu
        score += beta * ((c[n] - c[n - w] - w / 2.0) / sd - fb)
        used += 1
    if not used:
        return None
    return _sgn_vote(score, 1e-12)


# ── 6 logic MỚI ở bản SEQ13v4 (CMIXL · SPARSE · HMM3 · TOTK · SPEC · CPSEG) — thay CTW · SELKEY · LSM · DECAYMIX · CONV3 · TVBIAS · RLSFF ──────────────────────────────
# Nguyên tắc chung: (1) LUÔN bỏ phiếu (dấu của xác suất/dự báo, không cổng thống kê, không phiếu trắng) — chỉ khi chưa đủ lịch sử mới trả None -> theo ván trước;
# (2) mọi ván trong cửa sổ có TRỌNG SỐ NHƯ NHAU (không decay) — "cửa sổ" do LOGIC_WIN cắt trong compute_all (mỗi logic đọc đúng số ván mà nó mạnh nhất);
# (3) không đặt tay tham số nhạy: hệ số phạt / băng thông / bậc mô hình do DỮ LIỆU chọn (evidence · leave-one-out · log-likelihood) -> chuỗi ngẫu nhiên thì co về 50% chứ không bịa cấu trúc.
_pc = int.bit_count if hasattr(int, "bit_count") else (lambda x: bin(x).count("1"))      # popcount


def _loo_ll(n0, n1, a=1.0):
    """Log-likelihood LEAVE-ONE-OUT của 1 ngữ cảnh có n0 ván Xỉu / n1 ván Tài (bộ ước lượng Beta(a,a)): mỗi ván được dự đoán bằng phần còn lại của ngữ cảnh đó."""
    n = n0 + n1
    if n == 0:
        return 0.0
    den = n - 1.0 + 2.0 * a
    s = 0.0
    if n1:
        s += n1 * math.log((n1 - 1.0 + a) / den)
    if n0:
        s += n0 * math.log((n0 - 1.0 + a) / den)
    return s


def _ridge_logit(X, Yv, w0, iters=4, alpha0=5.0, a_min=0.5, a_max=2000.0):
    """Hồi quy logistic ridge (Newton/IRLS) với PRIOR TRUNG TÂM w0 (phạt α|w−w0|², bias w[0] không phạt). α tự chọn theo bằng chứng (MacKay: α = γ/|w−w0|²).
    Khác BLREV: hệ số co về w0 (vd. 'trung bình đều các mô hình') chứ không co về 0 -> không có bằng chứng thì kết quả = trung bình các đầu vào."""
    d = len(w0)
    w = list(w0)
    alpha = alpha0
    for _ in range(iters):
        H = [[0.0] * d for _ in range(d)]
        g = [0.0] * d
        for x, yy in zip(X, Yv):
            z = 0.0
            for a_ in range(d):
                z += w[a_] * x[a_]
            z = max(-30.0, min(30.0, z))
            p = 1.0 / (1.0 + math.exp(-z))
            sv = p * (1.0 - p)
            e = yy - p
            for a_ in range(d):
                xa = x[a_]
                g[a_] += e * xa
                sa = sv * xa
                Ha = H[a_]
                for b_ in range(a_, d):
                    Ha[b_] += sa * x[b_]
        for a_ in range(d):
            for b_ in range(a_):
                H[a_][b_] = H[b_][a_]
        for a_ in range(1, d):
            g[a_] -= alpha * (w[a_] - w0[a_])
            H[a_][a_] += alpha
        H[0][0] += 1e-6
        dw = _gj_solve(H, g)
        if dw is None:
            return None
        w = [wi + di for wi, di in zip(w, dw)]
        ww = sum((w[a_] - w0[a_]) ** 2 for a_ in range(1, d))
        if ww > 1e-9:
            tr = sum(1.0 / H[a_][a_] for a_ in range(1, d))
            gamma = max(0.0, (d - 1) - alpha * tr)
            alpha = min(max(gamma / ww, a_min), a_max)
    return w


# ── 1) CMIXL — Context Mixing Logistic (kiểu PAQ): nhiều mô hình ngữ cảnh + match model, trộn bằng hồi quy logistic ─────────────────────────────────────────────────────
def lg_cmixl(S, W=500, burn=60):
    """CMIXL: 'trộn ngữ cảnh' kiểu PAQ/cmix trên chuỗi Tài/Xỉu. 9 mô hình con, mỗi mô hình học ONLINE (đếm dần theo thứ tự thời gian, ván j chỉ thấy ván < j) rồi đưa ra stretch(P(Tài)):
    bậc 1 · 2 · 3 · 4 · 6 · 8 (ngữ cảnh = k kết quả gần nhất) · RUNCTX (ván trước + độ dài đợt hiện tại + độ dài đợt trước) · TỔNG (nhóm tổng 2 ván trước) · MATCH (tìm lần xuất hiện gần nhất của 12 ván cuối,
    dự đoán theo ván nằm sau nó; độ tin cậy theo độ dài khớp học online). Bộ trộn = hồi quy logistic ridge trên chính các dự đoán ĐÃ-LÀ-OUT-OF-SAMPLE đó (ván nào cũng nặng như nhau),
    hệ số co về TRUNG BÌNH ĐỀU 1/9 (không có bằng chứng thì ≈ trung bình các mô hình) và độ phạt α tự chọn theo bằng chứng MacKay. Cửa sổ 500 ván. Luôn bỏ phiếu.
    Mạnh: bắt cùng lúc cầu ngắn (bậc thấp) · cầu dài lặp (match/bậc 8) · nhịp đợt (RUNCTX) mà không phải đoán 'bậc nào đúng' — bộ trộn tự chọn. Yếu: nhiều mô hình -> cần ≥ 100 ván (tốt nhất ≥ 300) mới có bằng chứng; nguồn thật sự ngẫu nhiên thì ≈ 50%."""
    y, t = S["y"], S["t"]
    n = len(y)
    if n < 100:
        return None
    burn = min(burn, max(20, n // 8))
    J0 = 12
    ORD = (1, 2, 3, 4, 6, 8)
    cn1 = [[0] * (1 << k) for k in ORD]
    cn0 = [[0] * (1 << k) for k in ORD]
    masks = [(1 << k) - 1 for k in ORD]
    rc = {}                                                     # RUNCTX: (ván trước, độ dài đợt cắt 8, độ dài đợt trước cắt 4) -> [n0, n1]
    tc = {}                                                     # TỔNG: nhóm tổng 2 ván trước -> [n0, n1]
    tb = [_tb1(v) for v in t]
    last = {}                                                   # 12 ván cuối (số nguyên 12 bit) -> chỉ số ván nằm NGAY SAU lần xuất hiện gần nhất
    mh = [0] * 10
    mt = [0] * 10
    h = 0
    run, prun = 0, 0
    for i in range(J0):
        h = (h << 1) | y[i]
        if i and y[i] == y[i - 1]:
            run += 1
        else:
            prun, run = run, 1
    X, Yv = [], []
    feats = None
    for j in range(J0, n + 1):
        f = [1.0]
        for oi in range(6):
            cx = h & masks[oi]
            f.append(math.log((cn1[oi][cx] + 1.0) / (cn0[oi][cx] + 1.0)))
        rk = (y[j - 1], run if run < 8 else 8, prun if prun < 4 else 4)
        r = rc.get(rk)
        f.append(math.log((r[1] + 1.0) / (r[0] + 1.0)) if r else 0.0)
        tk = tb[j - 1] * 4 + tb[j - 2]
        r = tc.get(tk)
        f.append(math.log((r[1] + 1.0) / (r[0] + 1.0)) if r else 0.0)
        p = last.get(h)
        pred, mb = -1, 0
        if p is not None:
            ln_ = 12
            while ln_ < 32 and p - 1 - ln_ >= 0 and y[p - 1 - ln_] == y[j - 1 - ln_]:
                ln_ += 1
            mb = ln_ >> 2
            pred = y[p]
            rr = (mh[mb] + 1.0) / (mt[mb] + 2.0)
            sv = math.log(rr / (1.0 - rr))
            f.append(sv if pred else -sv)
        else:
            f.append(0.0)
        if j == n:
            feats = f
            break
        yy = y[j]
        if j >= J0 + burn:
            X.append(f)
            Yv.append(yy)
        for oi in range(6):
            cx = h & masks[oi]
            if yy:
                cn1[oi][cx] += 1
            else:
                cn0[oi][cx] += 1
        r = rc.get(rk)
        if r is None:
            r = rc[rk] = [0, 0]
        r[yy] += 1
        r = tc.get(tk)
        if r is None:
            r = tc[tk] = [0, 0]
        r[yy] += 1
        if pred >= 0:
            mt[mb] += 1
            if pred == yy:
                mh[mb] += 1
        last[h] = j
        h = ((h << 1) | yy) & 0xFFF
        if yy == y[j - 1]:
            run += 1
        else:
            prun, run = run, 1
    if len(X) < 50 or feats is None:
        return None
    d = len(feats)
    w0 = [0.0] + [1.0 / (d - 1)] * (d - 1)
    w = _ridge_logit(X, Yv, w0)
    if w is None:
        return None
    return _sgn_vote(sum(a * b for a, b in zip(w, feats)), 1e-12)


# ── 2) SPARSE — mô hình trễ THƯA, trung bình Bayes (BMA) bằng bitset + popcount ───────────────────────────────────────────────────────────────────────────────────────────
def lg_sparse(S, W=500, L1=16, L3=10, a=1.0):
    """SPARSE: thay vì ngữ cảnh 'k ván liền nhau' (PPM) — xét mọi tập TRỄ THƯA: 1 trễ ∈ 1..16 (16 mô hình) · 2 trễ ∈ 1..16 (120) · 3 trễ ∈ 1..10 (120) + mô hình rỗng (tỉ lệ chung) = 257 mô hình.
    Ví dụ {2,5}: 'ván cách 2 và cách 5 ván trước -> ván này' (bắt cầu có nhịp cách quãng / chu kỳ mà PPM không thấy vì bị ván xen giữa che). Mỗi mô hình = bảng đếm Tài/Xỉu theo giá trị các trễ đó trong W=500 ván
    (đếm bằng bitset + popcount nên cả 257 mô hình chỉ vài ms). Bằng chứng mỗi mô hình = log-likelihood LEAVE-ONE-OUT (đã tự phạt độ phức tạp: mô hình nhiều ngữ cảnh mà chỉ khớp nhiễu sẽ bị trừ điểm);
    prior chia ĐỀU theo số trễ (rỗng / 1 / 2 / 3 trễ mỗi nhóm 1/4, rồi chia đều trong nhóm). Dự đoán = trung bình Bayes P(Tài) theo trọng số exp(bằng chứng). Luôn bỏ phiếu (dấu của P − 0.5).
    Mạnh: bắt chu kỳ/nhịp cách quãng, bù cho PPM6 (liền kề) và RUNCTX (độ dài đợt). Yếu: trên nguồn ngẫu nhiên vẫn có 'người thắng do may' trong 257 mô hình — LOO + prior nhóm chỉ giảm chứ không loại bỏ."""
    y = S["y"]
    n = len(y)
    lo = max(L1, n - W)
    N = n - lo
    if N < 80:
        return None
    full = (1 << N) - 1
    mk = lambda seq: int("".join(map(str, seq)), 2)
    T = mk(y[lo:n])
    B = [None] * (L1 + 1)
    for l_ in range(1, L1 + 1):
        B[l_] = mk(y[lo - l_:n - l_])
    P1 = [None] + [(B[l_] ^ full, B[l_]) for l_ in range(1, L1 + 1)]       # P1[l][v] = tập vị trí mà ván cách l ván có giá trị v
    qb = [None] + [y[n - l_] for l_ in range(1, L1 + 1)]                    # giá trị các trễ tại thời điểm cần dự đoán
    a2 = 2.0 * a
    n1_all = _pc(T)
    n0_all = N - n1_all
    cand = [(math.log(0.25) + _loo_ll(n0_all, n1_all, a), (n1_all + a) / (N + a2))]
    g1 = float(L1)
    g2 = L1 * (L1 - 1) / 2.0
    g3 = L3 * (L3 - 1) * (L3 - 2) / 6.0
    lp1, lp2, lp3 = math.log(0.25 / g1), math.log(0.25 / g2), math.log(0.25 / g3)

    for l1 in range(1, L1 + 1):
        ll, pq = 0.0, 0.5
        for v in (0, 1):
            m = P1[l1][v]
            nn = _pc(m)
            k1 = _pc(m & T)
            ll += _loo_ll(nn - k1, k1, a)
            if v == qb[l1]:
                pq = (k1 + a) / (nn + a2)
        cand.append((lp1 + ll, pq))
        for l2 in range(l1 + 1, L1 + 1):
            sets2 = []
            ll, pq = 0.0, 0.5
            for v1 in (0, 1):
                for v2 in (0, 1):
                    m = P1[l1][v1] & P1[l2][v2]
                    sets2.append(m)
                    nn = _pc(m)
                    k1 = _pc(m & T)
                    ll += _loo_ll(nn - k1, k1, a)
                    if v1 == qb[l1] and v2 == qb[l2]:
                        pq = (k1 + a) / (nn + a2)
            cand.append((lp2 + ll, pq))
            if l2 <= L3:
                for l3 in range(l2 + 1, L3 + 1):
                    ll, pq = 0.0, 0.5
                    for i4 in range(4):
                        m4 = sets2[i4]
                        for v3 in (0, 1):
                            m = m4 & P1[l3][v3]
                            nn = _pc(m)
                            k1 = _pc(m & T)
                            ll += _loo_ll(nn - k1, k1, a)
                            if (i4 >> 1) == qb[l1] and (i4 & 1) == qb[l2] and v3 == qb[l3]:
                                pq = (k1 + a) / (nn + a2)
                    cand.append((lp3 + ll, pq))
    mx = max(c[0] for c in cand)
    sw = sq = 0.0
    for lw, pq in cand:
        wgt = math.exp(lw - mx)
        sw += wgt
        sq += wgt * pq
    return _sgn_vote(sq / sw - 0.5, 1e-12)


# ── 3) HMM3 — Hidden Markov 3 trạng thái (Baum–Welch, MAP) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _hmm_forward(ys, A, e):
    """Forward có chuẩn hoá. Trả (list alpha-chuẩn-hoá, list hệ số c, log-likelihood)."""
    a00, a01, a02, a10, a11, a12, a20, a21, a22 = A[0][0], A[0][1], A[0][2], A[1][0], A[1][1], A[1][2], A[2][0], A[2][1], A[2][2]
    e0, e1, e2 = e
    q0, q1, q2 = 1.0 - e0, 1.0 - e1, 1.0 - e2
    y0 = ys[0]
    f0 = (e0 if y0 else q0) / 3.0
    f1 = (e1 if y0 else q1) / 3.0
    f2 = (e2 if y0 else q2) / 3.0
    c = f0 + f1 + f2
    f0, f1, f2 = f0 / c, f1 / c, f2 / c
    al = [(f0, f1, f2)]
    cs = [c]
    ll = math.log(c)
    for t in range(1, len(ys)):
        yy = ys[t]
        g0 = (f0 * a00 + f1 * a10 + f2 * a20) * (e0 if yy else q0)
        g1 = (f0 * a01 + f1 * a11 + f2 * a21) * (e1 if yy else q1)
        g2 = (f0 * a02 + f1 * a12 + f2 * a22) * (e2 if yy else q2)
        c = g0 + g1 + g2
        if c < 1e-300:
            c = 1e-300
        f0, f1, f2 = g0 / c, g1 / c, g2 / c
        al.append((f0, f1, f2))
        cs.append(c)
        ll += math.log(c)
    return al, cs, ll


def _hmm_fit(ys, A, e, iters, tol=0.01):
    """Baum–Welch MAP: prior Dirichlet(1) cho từng hàng chuyển trạng thái (+1 giả-đếm) và Beta(2,2) cho xác suất phát Tài (+1/+1) -> không bao giờ suy biến về 0/1."""
    T = len(ys)
    A = [r[:] for r in A]
    e = list(e)
    prev = -1e300
    al = cs = None
    ll = prev
    for _ in range(iters):
        al, cs, ll = _hmm_forward(ys, A, e)
        if ll - prev < tol:
            break
        prev = ll
        a00, a01, a02, a10, a11, a12, a20, a21, a22 = A[0][0], A[0][1], A[0][2], A[1][0], A[1][1], A[1][2], A[2][0], A[2][1], A[2][2]
        e0, e1, e2 = e
        q0, q1, q2 = 1.0 - e0, 1.0 - e1, 1.0 - e2
        b0 = b1 = b2 = 1.0                                      # beta chuẩn hoá của bước cuối
        x00 = x01 = x02 = x10 = x11 = x12 = x20 = x21 = x22 = 0.0
        sg0 = sg1 = sg2 = 0.0
        sy0 = sy1 = sy2 = 0.0
        yy = ys[T - 1]
        f0, f1, f2 = al[T - 1]
        sg0 += f0
        sg1 += f1
        sg2 += f2
        if yy:
            sy0 += f0
            sy1 += f1
            sy2 += f2
        for t in range(T - 2, -1, -1):
            yn = ys[t + 1]
            c = cs[t + 1]
            u0 = (e0 if yn else q0) * b0 / c
            u1 = (e1 if yn else q1) * b1 / c
            u2 = (e2 if yn else q2) * b2 / c
            f0, f1, f2 = al[t]
            x00 += f0 * u0
            x01 += f0 * u1
            x02 += f0 * u2
            x10 += f1 * u0
            x11 += f1 * u1
            x12 += f1 * u2
            x20 += f2 * u0
            x21 += f2 * u1
            x22 += f2 * u2
            b0 = a00 * u0 + a01 * u1 + a02 * u2
            b1 = a10 * u0 + a11 * u1 + a12 * u2
            b2 = a20 * u0 + a21 * u1 + a22 * u2
            g0, g1, g2 = f0 * b0, f1 * b1, f2 * b2
            sg0 += g0
            sg1 += g1
            sg2 += g2
            if ys[t]:
                sy0 += g0
                sy1 += g1
                sy2 += g2
        X = ((x00 * a00, x01 * a01, x02 * a02), (x10 * a10, x11 * a11, x12 * a12), (x20 * a20, x21 * a21, x22 * a22))
        A = []
        for r in X:
            s = r[0] + r[1] + r[2] + 3.0
            A.append([(r[0] + 1.0) / s, (r[1] + 1.0) / s, (r[2] + 1.0) / s])
        e = [(sy0 + 1.0) / (sg0 + 2.0), (sy1 + 1.0) / (sg1 + 2.0), (sy2 + 1.0) / (sg2 + 2.0)]
    al, cs, ll = _hmm_forward(ys, A, e)
    return A, e, al, ll


def lg_hmm3(S, W=400, iters=10):
    """HMM3: mô hình Markov ẩn 3 trạng thái (mỗi trạng thái có xác suất ra Tài riêng + ma trận chuyển trạng thái 3x3), học bằng Baum–Welch MAP trên W=400 ván (mọi ván trọng số như nhau).
    2 điểm khởi tạo CỐ ĐỊNH (deterministic): (a) 'chế độ dính' — 3 trạng thái nghiêng Xỉu / giữa / nghiêng Tài, ở lâu trong mỗi trạng thái; (b) 'chu trình' — 3 trạng thái luân phiên theo vòng (bắt cầu 1-1 / nhịp 3);
    lấy cái có likelihood cao hơn. Dự đoán = lọc forward ra phân phối trạng thái hiện tại -> chuyển 1 bước -> P(Tài) -> dấu của P − 0.5. Luôn bỏ phiếu.
    Mạnh: bắt 'chế độ' ẩn thay đổi (lúc bệt, lúc đảo, lúc lệch Tài…) mà các mô hình ngữ cảnh cố định không có khái niệm 'đang ở chế độ nào'; prior MAP nên không suy biến. Yếu: EM có thể kẹt cực trị địa phương
    (đã giảm bằng 2 khởi tạo) và trên nguồn ngẫu nhiên 3 trạng thái chỉ fit nhiễu -> ≈ 50%."""
    y = S["y"]
    n = len(y)
    if n < 100:
        return None
    best = None
    for A0, e0 in (([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]], (0.3, 0.5, 0.7)),
                   ([[0.15, 0.7, 0.15], [0.15, 0.15, 0.7], [0.7, 0.15, 0.15]], (0.2, 0.8, 0.5))):
        r = _hmm_fit(y, A0, e0, iters)
        if best is None or r[3] > best[3]:
            best = r
    A, e, al, _ll = best
    f = al[-1]
    p = 0.0
    for j in range(3):
        p += e[j] * (f[0] * A[0][j] + f[1] * A[1][j] + f[2] * A[2][j])
    return _sgn_vote(p - 0.5, 1e-12)


# ── 4) TOTK — hồi quy hạt nhân (Nadaraya–Watson) trên TỔNG xúc xắc, băng thông chọn bằng LOO + BMA ───────────────────────────────────────────────────────────────────────────
def _smooth1d(arr, ker):
    V = len(arr)
    R = len(ker) - 1
    out = [0.0] * V
    for c in range(V):
        s = 0.0
        for d_ in range(-R, R + 1):
            i = c + d_
            if 0 <= i < V:
                s += ker[abs(d_)] * arr[i]
        out[c] = s
    return out


def lg_totk(S, W=400, m=2.0):
    """TOTK: hồi quy hạt nhân trên TỔNG xúc xắc (3..18) — 'tổng gần đây ở gần mức nào thì ván sau hay ra Tài hay Xỉu', dùng thông tin mà nhị phân Tài/Xỉu (PPM/CMIXL) vứt đi (tổng 10 và 3 cùng là Xỉu).
    3 bộ đặc trưng: (a) tổng ván trước · (b) cặp (tổng ván trước, tổng ván trước nữa) · (c) tổng 3 ván gần nhất. Mỗi bộ x 4 băng thông Gauss (hẹp -> rộng ≈ tỉ lệ chung) = 12 ước lượng NW:
    P(Tài | ngữ cảnh) = (Σ K·y + m·p0)/(Σ K + m), m = 2 co về tỉ lệ chung p0. Băng thông KHÔNG đặt tay: bằng chứng mỗi ước lượng = log-likelihood LEAVE-ONE-OUT trên W=400 ván (công thức đóng, ván nào cũng nặng như nhau),
    dự đoán = trung bình Bayes theo exp(bằng chứng). Luôn bỏ phiếu. Mạnh: dùng được cả độ lớn tổng (nguồn có 'đà' theo mức tổng); LOO tự chọn băng thông. Yếu: nếu cầu chỉ phụ thuộc Tài/Xỉu thì chẳng thêm gì so với PPM6."""
    y, t = S["y"], S["t"]
    n = len(y)
    if n < 60:
        return None
    tt = [min(18, max(3, int(v))) - 3 for v in t]               # 0..15
    j0 = 3
    N = n - j0
    n1_all = sum(y[j0:n])
    p0 = (n1_all + 1.0) / (N + 2.0)
    V1, V3 = 16, 46
    # đếm ô
    g1_n, g1_1 = [0.0] * V1, [0.0] * V1
    g2_n = [[0.0] * V1 for _ in range(V1)]
    g2_1 = [[0.0] * V1 for _ in range(V1)]
    g3_n, g3_1 = [0.0] * V3, [0.0] * V3
    for j in range(j0, n):
        yy = y[j]
        a_, b_ = tt[j - 1], tt[j - 2]
        s3 = a_ + b_ + tt[j - 3]
        g1_n[a_] += 1.0
        g2_n[a_][b_] += 1.0
        g3_n[s3] += 1.0
        if yy:
            g1_1[a_] += 1.0
            g2_1[a_][b_] += 1.0
            g3_1[s3] += 1.0
    qa, qb_ = tt[n - 1], tt[n - 2]
    qs = qa + qb_ + tt[n - 3]

    def kern(h, V):
        R = min(V - 1, int(math.ceil(3.0 * h)))
        return [math.exp(-0.5 * (i / h) ** 2) for i in range(R + 1)]

    def loo_cells(cells, p0_, m_):
        """cells: list (n_c, n1_c, S_c, S1_c) -> LOO log-lik của ước lượng NW (đã bỏ chính ván đó khỏi tổng hạt nhân: S-1, S1-y)."""
        ll = 0.0
        for nc, k1, Sc, S1c in cells:
            if nc <= 0.0:
                continue
            den = Sc - 1.0 + m_
            if k1 > 0.0:
                ll += k1 * math.log((S1c - 1.0 + m_ * p0_) / den)
            k0 = nc - k1
            if k0 > 0.0:
                ll += k0 * math.log(((Sc - S1c) - 1.0 + m_ * (1.0 - p0_)) / den)
        return ll

    cand = []
    for h in (0.6, 1.2, 2.5, 6.0):
        ker = kern(h, V1)
        # (a) 1D tổng ván trước
        S_n, S_1 = _smooth1d(g1_n, ker), _smooth1d(g1_1, ker)
        ll = loo_cells([(g1_n[c], g1_1[c], S_n[c], S_1[c]) for c in range(V1)], p0, m)
        cand.append((ll, (S_1[qa] + m * p0) / (S_n[qa] + m)))
        # (b) 2D (tổng ván trước, tổng ván trước nữa) — tách biến: làm mịn theo hàng rồi theo cột
        r_n = [_smooth1d(row, ker) for row in g2_n]
        r_1 = [_smooth1d(row, ker) for row in g2_1]
        cols_n = [_smooth1d([r_n[a][b] for a in range(V1)], ker) for b in range(V1)]     # cols_n[b][a]
        cols_1 = [_smooth1d([r_1[a][b] for a in range(V1)], ker) for b in range(V1)]
        cells = []
        for a in range(V1):
            for b in range(V1):
                if g2_n[a][b] > 0.0:
                    cells.append((g2_n[a][b], g2_1[a][b], cols_n[b][a], cols_1[b][a]))
        ll = loo_cells(cells, p0, m)
        cand.append((ll, (cols_1[qb_][qa] + m * p0) / (cols_n[qb_][qa] + m)))
        # (c) 1D tổng 3 ván (đơn vị lớn hơn ≈ √3 lần)
        ker3 = kern(h * 1.7, V3)
        S_n, S_1 = _smooth1d(g3_n, ker3), _smooth1d(g3_1, ker3)
        ll = loo_cells([(g3_n[c], g3_1[c], S_n[c], S_1[c]) for c in range(V3)], p0, m)
        cand.append((ll, (S_1[qs] + m * p0) / (S_n[qs] + m)))
    mx = max(c[0] for c in cand)
    sw = sq = 0.0
    for ll, q in cand:
        wgt = math.exp(ll - mx)
        sw += wgt
        sq += wgt * q
    return _sgn_vote(sq / sw - 0.5, 1e-12)


# ── 5) SPEC — ngoại suy phổ DFT (chu kỳ ẩn) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_FFT_TW = {}


def _fft(a):
    """FFT radix-2 lặp tại chỗ (len(a) là luỹ thừa của 2), thuần Python."""
    n = len(a)
    tw = _FFT_TW.get(n)
    if tw is None:
        tw = _FFT_TW[n] = [complex(math.cos(-2.0 * math.pi * k / n), math.sin(-2.0 * math.pi * k / n)) for k in range(n // 2)]
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    ln_ = 2
    while ln_ <= n:
        half = ln_ >> 1
        step = n // ln_
        for i in range(0, n, ln_):
            k = 0
            for q in range(i, i + half):
                u = a[q]
                v = a[q + half] * tw[k]
                a[q] = u + v
                a[q + half] = u - v
                k += step
        ln_ <<= 1
    return a


def lg_spec(S, W=400, K=3):
    """SPEC: tìm chu kỳ ẩn bằng phổ Fourier. Lấy W=400 ván (Tài=+1/Xỉu=−1, trừ trung bình), DFT có đệm 0 (kích thước luỹ thừa 2 ≥ 2W), lấy K=3 đỉnh phổ mạnh nhất có chu kỳ 2..W/3 (≥ 3 chu kỳ trong cửa sổ, nên không nhầm xu hướng với chu kỳ),
    tinh chỉnh tần số bằng nội suy parabol quanh đỉnh rồi ước lượng biên độ + pha đúng tại tần số đó (Goertzel), cộng K sóng sin NGOẠI SUY tới ván kế tiếp -> dấu. Luôn bỏ phiếu (dấu của tổng sóng).
    Mạnh: bắt chu kỳ cố định (bệt 3 – đảo 3, nhịp 7/11/13 ván…) kể cả khi bị nhiễu chen — thứ mà mô hình ngữ cảnh (PPM/CMIXL) không tổng quát hoá được. Yếu: nguồn ngẫu nhiên thì đỉnh phổ chỉ là nhiễu
    (K đỉnh lớn nhất của nhiễu luôn tồn tại) -> ≈ 50%; chu kỳ trôi pha / đổi giữa chừng thì ngoại suy sai."""
    y = S["y"]
    n = len(y)
    if n < 60:
        return None
    mu = sum(y) / float(n)
    x = [v - mu for v in y]
    M = 1
    while M < 2 * n:
        M <<= 1
    a = [complex(v, 0.0) for v in x] + [0j] * (M - n)
    X = _fft(a)
    half = M // 2
    Pw = [X[k].real * X[k].real + X[k].imag * X[k].imag for k in range(half)]
    kmin = max(2, int(math.ceil(3.0 * M / n)))
    peaks = [k for k in range(kmin, half - 1) if Pw[k] >= Pw[k - 1] and Pw[k] > Pw[k + 1]]
    if not peaks:
        return None
    peaks.sort(key=lambda k: -Pw[k])
    xhat = 0.0
    for k in peaks[:K]:
        m1, m0, p1 = math.sqrt(Pw[k - 1]), math.sqrt(Pw[k]), math.sqrt(Pw[k + 1])
        den = m1 - 2.0 * m0 + p1
        dl = 0.5 * (m1 - p1) / den if den < -1e-12 else 0.0
        f = (k + max(-0.5, min(0.5, dl))) / M
        rot = complex(math.cos(-2.0 * math.pi * f), math.sin(-2.0 * math.pi * f))
        cur = 1.0 + 0j
        z = 0j
        for v in x:
            z += v * cur
            cur *= rot
        th = 2.0 * math.pi * f * n
        xhat += (2.0 / n) * (z * complex(math.cos(th), math.sin(th))).real
    return _sgn_vote(xhat, 1e-12)


# ── 6) CPSEG — phát hiện điểm đổi chế độ + Markov bậc 2 co phân cấp ────────────────────────────────────────────────────────────────────────────────────────────────────────
def _bern_ll(k, m):
    """Log-likelihood cực đại của m phép thử Bernoulli có k lần '1'."""
    if m <= 0 or k <= 0 or k >= m:
        return 0.0
    return k * math.log(k / m) + (m - k) * math.log((m - k) / m)


def _binseg(c, a, b, minseg, pen, out):
    """Phân đoạn nhị phân trên chuỗi 0/1 có prefix-sum c (c[i] = tổng x[0..i-1]): tìm điểm cắt s ∈ [a+minseg, b−minseg] tối đa hoá LR Bernoulli; nhận nếu LR > pen rồi đệ quy 2 nửa."""
    stack = [(a, b)]
    while stack:
        lo, hi = stack.pop()
        if hi - lo < 2 * minseg:
            continue
        whole = _bern_ll(c[hi] - c[lo], hi - lo)
        best, bs = 0.0, -1
        for s in range(lo + minseg, hi - minseg + 1):
            g = _bern_ll(c[s] - c[lo], s - lo) + _bern_ll(c[hi] - c[s], hi - s) - whole
            if g > best:
                best, bs = g, s
        if bs >= 0 and best > pen:
            out.append(bs)
            stack.append((lo, bs))
            stack.append((bs, hi))


def lg_cpseg(S, W=300, minseg=20, m=4.0):
    """CPSEG: 'chế độ' đổi thì chỉ phần SAU điểm đổi mới có giá trị. Bước 1: phân đoạn nhị phân tìm điểm đổi chế độ trên 2 chuỗi — (i) Tài/Xỉu (tỉ lệ Tài đổi) và (ii) chỉ báo ĐẢO CẦU (nhịp đảo đổi) —
    nhận điểm cắt khi tỉ số likelihood Bernoulli > 3·ln(W) (phạt kiểu BIC cho 2 tham số thêm), đoạn tối thiểu 20 ván; lấy điểm đổi MỚI NHẤT. Bước 2: Markov bậc 2 trên đoạn hiện tại với CO PHÂN CẤP:
    đoạn hiện tại (ngữ cảnh 2 ván) -> toàn cửa sổ W=300 (ngữ cảnh 2 ván) -> toàn cửa sổ (ngữ cảnh 1 ván) -> tỉ lệ chung (mỗi tầng co về tầng trên với giả-đếm m=4), nên đoạn ngắn tự dựa vào thống kê cả cửa sổ.
    Luôn bỏ phiếu. Mạnh: phản ứng nhanh khi nguồn đổi chế độ nhưng KHÔNG vứt dữ liệu cũ một cách mù quáng (shrink); là logic duy nhất tự nhận biết 'đã đổi chế độ' bằng kiểm định. Yếu: điểm đổi cuối cửa sổ (< 20 ván) chưa phát hiện được."""
    y = S["y"]
    n = len(y)
    if n < 80:
        return None
    pen = 3.0 * math.log(n)
    cps = []
    c = [0]
    for v in y:
        c.append(c[-1] + v)
    _binseg(c, 0, n, minseg, pen, cps)
    alt = [0] + [1 if y[i] != y[i - 1] else 0 for i in range(1, n)]
    c2 = [0]
    for v in alt:
        c2.append(c2[-1] + v)
    _binseg(c2, 1, n, minseg, pen, cps)
    st = max(cps) if cps else 0
    st = max(st, 2)
    # đếm
    w2 = [[0, 0] for _ in range(4)]
    w1 = [[0, 0] for _ in range(2)]
    s2 = [[0, 0] for _ in range(4)]
    g0 = g1 = 0
    for j in range(2, n):
        yy = y[j]
        k2 = 2 * y[j - 2] + y[j - 1]
        w2[k2][yy] += 1
        w1[y[j - 1]][yy] += 1
        if j >= st:
            s2[k2][yy] += 1
        if yy:
            g1 += 1
        else:
            g0 += 1
    pg = (g1 + 1.0) / (g0 + g1 + 2.0)
    q1 = y[n - 1]
    q2 = 2 * y[n - 2] + y[n - 1]
    p1 = (w1[q1][1] + m * pg) / (w1[q1][0] + w1[q1][1] + m)
    p2 = (w2[q2][1] + m * p1) / (w2[q2][0] + w2[q2][1] + m)
    ps = (s2[q2][1] + m * p2) / (s2[q2][0] + s2[q2][1] + m)
    return _sgn_vote(ps - 0.5, 1e-12)


# ─── 6 LOGIC MỚI CỦA SEQ12v5 (thuần Python, KHÔNG cần numpy) ─────────────────────────────────────────────
# CAUTPL · FSHARE · BLKHAZ · BOCPD · GBS · AFM — mỗi logic nhận S (y / t / d / p đã cắt đúng cửa sổ của nó) và trả 1 = TÀI · 0 = XỈU · None = chưa đủ ván (compute_all -> theo ván trước).
def _n_runs(y):
    """RLE: [[giá trị, độ dài], ...]"""
    r = []
    for v in y:
        if r and r[-1][0] == v:
            r[-1][1] += 1
        else:
            r.append([v, 1])
    return r


def _n_cont_vote(p_cont, y):
    """p_cont = P(ván sau GIỐNG ván trước) -> phiếu."""
    last = y[-1]
    if p_cont > 0.5:
        return last
    if p_cont < 0.5:
        return 1 - last
    return last


# ── CAUTPL: HMM "cầu mẫu" (bệt · 1-1 · 2-2 · 3-3 · 1-2 · 2-1 · 1-2-3 · 3-2-1 · 1-2-1 ...) + trạng thái "không có cầu" ──
def _build_tpl():
    tuples = [(1,), (2,), (3,), (4,), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2),
              (1, 1, 2), (1, 2, 1), (2, 1, 1), (1, 2, 3), (3, 2, 1), (2, 2, 1), (2, 1, 2), (1, 2, 2), (3, 3, 1), (1, 1, 3)]
    seen, seqs = set(), []
    for t in tuples:
        for c0 in (0, 1):
            bits, c = [], c0
            for _ in range(2 if len(t) % 2 == 1 else 1):        # số khối lẻ -> lặp 2 lần để quay về cùng màu
                for L in t:
                    bits += [c] * L
                    c = 1 - c
            key = tuple(bits)
            if key not in seen:
                seen.add(key)
                seqs.append(key)
    seqs.append((0,))
    seqs.append((1,))                                           # bệt
    return seqs


_TPL = _build_tpl()
_TPL_BIT, _TPL_ADV, _TPL_SKIP = [], [], []
for _s in _TPL:
    _b0 = len(_TPL_BIT)
    _P = len(_s)
    for _ph in range(_P):
        _TPL_BIT.append(_s[_ph])
        _TPL_ADV.append(_b0 + (_ph + 1) % _P)
        _TPL_SKIP.append(_b0 + (_ph + 2) % _P)
_TPL_NT = len(_TPL_BIT)
_TPL_STICKY = (0.5, 0.7, 0.85, 0.3)       # P(giống ván trước) của 4 trạng thái không chu kỳ: ngẫu nhiên · bệt dính 70% · bệt dính 85% · hay đảo
_TPL_N = _TPL_NT + len(_TPL_STICKY)
# (eta nhảy mẫu, sigma trượt pha, eps nhiễu phát xạ) — 3 bộ, chọn bộ có likelihood biên cao nhất
_TPL_PARAMS = ((0.02, 0.02, 0.08), (0.05, 0.03, 0.15), (0.10, 0.04, 0.28))


def _tpl_emit(eps):
    E = [[None, None], [None, None]]                            # E[obs][prev] = danh sách P(obs | prev, state)
    for obs in (0, 1):
        for prev in (0, 1):
            row = [(1 - eps) if b == obs else eps for b in _TPL_BIT]
            row += [q if obs == prev else 1 - q for q in _TPL_STICKY]
            E[obs][prev] = row
    return E


_TPL_E = [_tpl_emit(p[2]) for p in _TPL_PARAMS]


def lg_cautpl(S, W=150):
    y = S["y"][-W:]
    n = len(y)
    if n < 12:
        return None
    N, NT = _TPL_N, _TPL_NT
    best = None
    for (eta, sig, _eps), E in zip(_TPL_PARAMS, _TPL_E):
        a_adv, a_stay = 1 - eta - 2 * sig, sig
        a = [1.0 / N] * N
        ll = 0.0
        for j in range(1, n):
            jump = eta / N                                      # tổng a = 1 -> khối nhảy mẫu chia đều
            nw = [jump] * N
            for s in range(NT):
                x = a[s]
                nw[_TPL_ADV[s]] += x * a_adv
                nw[s] += x * a_stay
                nw[_TPL_SKIP[s]] += x * a_stay
            for k in range(NT, N):
                nw[k] += a[k] * (1 - eta)
            e = E[y[j]][y[j - 1]]
            a = [nw[i] * e[i] for i in range(N)]
            sm = sum(a)
            ll += math.log(sm)
            a = [v / sm for v in a]
        jump = eta / N
        nw = [jump] * N
        for s in range(NT):
            x = a[s]
            nw[_TPL_ADV[s]] += x * a_adv
            nw[s] += x * a_stay
            nw[_TPL_SKIP[s]] += x * a_stay
        for k in range(NT, N):
            nw[k] += a[k] * (1 - eta)
        e1 = E[1][y[-1]]
        p1 = sum(nw[i] * e1[i] for i in range(N))
        if best is None or ll > best[0]:
            best = (ll, p1)
    p1 = best[1]
    return 1 if p1 > 0.5 else 0 if p1 < 0.5 else y[-1]


# ── FSHARE: Fixed-share Hedge trên ~25 "chuyên gia cầu" ──
def _fs_experts(y, j):
    last = y[j - 1]
    L = 1
    while L < j and y[j - 1 - L] == last:
        L += 1
    a = 0
    while a < j - 1 and y[j - 1 - a] != y[j - 2 - a]:
        a += 1
    e = [last, 1 - last, y[j - 2], y[j - 3], y[j - 4], y[j - 6]]
    for k in (2, 3, 4, 5, 6):
        e.append(last if L < k else 1 - last)                   # theo bệt tới k rồi bẻ
    for k in (3, 4, 5, 6, 7):
        e.append(1 - last if a < k else last)                   # theo 1-1 tới k rồi bẻ
    for k in (2, 3, 4):
        e.append(1 - last if L < k else last)                   # bẻ sớm, bệt k thì theo
    s5 = sum(y[j - 5:j])
    s9 = sum(y[j - 9:j]) if j >= 9 else s5 * 9 / 5.0
    e += [1 if s5 >= 3 else 0, 1 if s9 >= 4.5 else 0, 0 if s5 >= 3 else 1, 0 if s9 >= 4.5 else 1]
    return e


def lg_fshare(S, W=300, eta=1.0, alpha=0.05):
    y = S["y"][-W:]
    n = len(y)
    if n < 15:
        return None
    N = len(_fs_experts(y, 10))
    w = [1.0 / N] * N
    ex = math.exp(-eta)
    for j in range(10, n):
        e = _fs_experts(y, j)
        yj = y[j]
        w = [w[i] * (ex if e[i] != yj else 1.0) for i in range(N)]
        sm = sum(w)
        w = [(1 - alpha) * v / sm + alpha / N for v in w]
    e = _fs_experts(y, n)
    sc = sum(w[i] * (2 * e[i] - 1) for i in range(N))
    return 1 if sc > 0 else 0 if sc < 0 else y[-1]


# ── BLKHAZ: hazard "bậc thang" (độ dài đợt trước k · số đợt liên tiếp cùng độ dài m · độ dài hiện tại L) ──
def lg_blkhaz(S, W=400, m=6.0):
    y = S["y"][-W:]
    n = len(y)
    if n < 30:
        return None
    c3, c2, c1 = {}, {}, {}
    runs, cur = [], 1

    def state():
        if runs:
            k = runs[-1]
            mm = 1
            for i in range(len(runs) - 2, -1, -1):
                if runs[i] == k:
                    mm += 1
                else:
                    break
        else:
            k, mm = 0, 0
        return (min(k, 5), min(mm, 6), min(cur, 8))

    for j in range(1, n):
        st = state()
        cont = 1 if y[j] == y[j - 1] else 0
        c3.setdefault(st, [0, 0])[cont] += 1
        c2.setdefault((st[0], st[2]), [0, 0])[cont] += 1
        c1.setdefault(st[2], [0, 0])[cont] += 1
        if cont:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    st = state()
    b1, a1 = c1.get(st[2], (0, 0))
    p1 = (a1 + 1.0) / (a1 + b1 + 2.0)
    b2, a2 = c2.get((st[0], st[2]), (0, 0))
    p2 = (a2 + m * p1) / (a2 + b2 + m)
    b3, a3 = c3.get(st, (0, 0))
    p3 = (a3 + m * p2) / (a3 + b3 + m)
    return _n_cont_vote(p3, y)


# ── BOCPD: Bayesian Online Changepoint Detection trên chuỗi GIỐNG/KHÁC ván trước (có ngữ cảnh z ván trước) ──
def lg_bocpd(S, W=400, hz=1 / 50.0, maxh=100):
    y = S["y"][-W:]
    n = len(y)
    if n < 20:
        return None
    z = [1 if y[j] == y[j - 1] else 0 for j in range(1, n)]
    w = [1.0]
    cnt = [[0, 0, 0, 0]]                                        # cnt[r][ctx*2 + obs]
    for j in range(1, len(z)):
        ctx, obs = z[j - 1], z[j]
        i0, i1 = ctx * 2, ctx * 2 + 1
        pr = [(c[ctx * 2 + obs] + 1.0) / (c[i0] + c[i1] + 2.0) for c in cnt]
        g = [w[r] * pr[r] * (1 - hz) for r in range(len(w))]
        cp = sum(w[r] * pr[r] for r in range(len(w))) * hz
        w = [cp] + g
        cnt = [[0, 0, 0, 0]] + cnt
        for r in range(1, len(cnt)):
            cnt[r][ctx * 2 + obs] += 1
        sm = sum(w)
        if sm > 0:
            w = [v / sm for v in w]
        else:
            w = [1.0 / len(w)] * len(w)
        if len(w) > maxh:
            keep = sorted(sorted(range(len(w)), key=lambda r: -w[r])[:maxh])
            w = [w[r] for r in keep]
            cnt = [cnt[r] for r in keep]
            sm = sum(w)
            w = [v / sm for v in w]
    ctx = z[-1]
    i0, i1 = ctx * 2, ctx * 2 + 1
    p_stay = (1 - hz) * sum(w[r] * (cnt[r][i1] + 1.0) / (cnt[r][i0] + cnt[r][i1] + 2.0) for r in range(len(w))) + hz * 0.5
    return _n_cont_vote(p_stay, y)


# ── GBS: boosting cây gốc (stump) log-loss trên ~12 đặc trưng cầu — mô hình CỘNG, co mạnh về 50% khi không có cấu trúc ──
def _gbs_feats(y, t, j):
    last = y[j - 1]
    L = 1
    while L < j and y[j - 1 - L] == last:
        L += 1
    pl = 0
    if L < j:
        pl = 1
        while L + pl < j and y[j - 1 - L - pl] == y[j - 1 - L]:
            pl += 1
    a = 0
    while a < j - 1 and y[j - 1 - a] != y[j - 2 - a]:
        a += 1
    b8 = sum(y[j - 8:j]) if j >= 8 else 4
    b24 = sum(y[max(0, j - 24):j]) * 24 // max(1, min(24, j)) // 3
    sw10 = sum(1 for i in range(max(1, j - 10), j) if y[i] != y[i - 1])
    return [y[j - 1], y[j - 2], y[j - 3], y[j - 4], min(L, 12), min(pl, 8), min(a, 12), b8, b24, t[j - 1], (t[j - 1] + t[j - 2]) // 3, sw10]


def lg_gbs(S, W=500, rounds=30, lr=0.12, lam=8.0, minh=6.0):
    y = S["y"][-W:]
    t = S["t"][-W:]
    n = len(y)
    if n < 80:
        return None
    X = [_gbs_feats(y, t, j) for j in range(12, n)]
    Y = y[12:]
    xc = _gbs_feats(y, t, n)
    m = len(Y)
    nf = len(xc)
    cols = [[X[i][f] for i in range(m)] for f in range(nf)]
    vals = [sorted(set(c)) for c in cols]
    pos = [{v: k for k, v in enumerate(vs)} for vs in vals]
    idx = [[pos[f][v] for v in cols[f]] for f in range(nf)]    # chỉ số giá trị của từng mẫu theo từng đặc trưng
    F = [0.0] * m
    Fc = 0.0
    for _ in range(rounds):
        p = [1.0 / (1.0 + math.exp(-v)) for v in F]
        g = [Y[i] - p[i] for i in range(m)]
        h = [p[i] * (1 - p[i]) for i in range(m)]
        Gt, Ht = sum(g), sum(h)
        best = None
        for f in range(nf):
            k = len(vals[f])
            if k < 2:
                continue
            G = [0.0] * k
            H = [0.0] * k
            ix = idx[f]
            for i in range(m):
                v = ix[i]
                G[v] += g[i]
                H[v] += h[i]
            Gl = Hl = 0.0
            for q in range(k - 1):
                Gl += G[q]
                Hl += H[q]
                Gr, Hr = Gt - Gl, Ht - Hl
                if Hl < minh or Hr < minh:
                    continue
                gain = Gl * Gl / (Hl + lam) + Gr * Gr / (Hr + lam)
                if best is None or gain > best[0]:
                    best = (gain, f, q, Gl / (Hl + lam), Gr / (Hr + lam))
        if best is None:
            break
        _, f, q, vl, vr = best
        ix = idx[f]
        for i in range(m):
            F[i] += lr * (vl if ix[i] <= q else vr)
        # giá trị chưa từng gặp trong cửa sổ: so với ngưỡng bằng số thật
        thr_val = vals[f][q]
        Fc += lr * (vl if xc[f] <= thr_val else vr)
    return 1 if Fc > 0 else 0 if Fc < 0 else y[-1]


# ── AFM: Markov bậc 1..4 × 4 hệ số QUÊN, trọng số theo log-loss tiên nghiệm gần đây ──
def lg_afm(S, W=450, orders=(1, 2, 3, 4), lams=(0.90, 0.96, 0.99, 1.0), ld=0.97, beta=1.0):
    y = S["y"][-W:]
    n = len(y)
    if n < 40:
        return None
    exps = [(o, l) for o in orders for l in lams]
    cnt = [dict() for _ in exps]
    loss = [0.0] * len(exps)
    omax = max(orders)

    def pred(i, ctx, j):
        l = exps[i][1]
        c = cnt[i].get(ctx)
        if c is None:
            return 0.5, 0.0, 0.0
        n0, n1, t0 = c
        if l < 1.0 and t0 != j:
            f = l ** (j - t0)
            n0 *= f
            n1 *= f
        return (n1 + 0.5) / (n0 + n1 + 1.0), n0, n1

    for j in range(omax, n):
        yj = y[j]
        for i, (o, l) in enumerate(exps):
            ctx = tuple(y[j - o:j])
            p, n0, n1 = pred(i, ctx, j)
            pp = p if yj == 1 else 1 - p
            loss[i] = ld * loss[i] - math.log(max(pp, 1e-6))
            if yj == 1:
                n1 += 1
            else:
                n0 += 1
            cnt[i][ctx] = (n0, n1, j)
    lo = min(loss)
    wts = [math.exp(-beta * (v - lo)) for v in loss]
    sw = sum(wts)
    ps = 0.0
    for i, (o, l) in enumerate(exps):
        p, _, _ = pred(i, tuple(y[n - o:n]), n)
        ps += wts[i] / sw * p
    return 1 if ps > 0.5 else 0 if ps < 0.5 else y[-1]


# ─── 5 LOGIC MỚI Ở SEQ13v6 (thuần Python, KHÔNG cần numpy) — CTW · MATCHR · FTRL · ESN2 · RLS (+ CMIXL là hàm cũ có sẵn ở trên, nay đưa lại vào SUN_LOGICS) ─────────────────
# Mỗi logic nhận S (y / t / d / p đã cắt đúng cửa sổ của nó) và trả 1 = TÀI · 0 = XỈU · None = chưa đủ ván (compute_all -> theo ván trước). Cả 5 luôn bỏ phiếu khi đủ ván (không cổng thống kê).

# ── CTW: Context Tree Weighting (ước lượng KT) — trộn Bayes TẤT CẢ cây ngữ cảnh độ sâu <= D ──
def _ctw_lae(a, b):
    m = a if a > b else b
    return m + math.log1p(math.exp(-abs(a - b)))


def _ctw_path(y, i, D):
    """Khoá nút từ gốc tới độ sâu D của ván i: (độ sâu, ngữ cảnh = D ván gần nhất trước i, trước 0 coi là 0)."""
    ks = [(0, 0)]
    c = 0
    for d in range(1, D + 1):
        b = y[i - d] if i - d >= 0 else 0
        c |= b << (d - 1)
        ks.append((d, c))
    return ks


def _ctw_upd(nodes, ks, D, x, commit):
    """Cập nhật các nút trên đường ks bằng ký hiệu x; trả log xác suất có trọng số ở gốc. commit=False -> chỉ tính thử, không ghi."""
    lw_child = 0.0
    for d in range(D, -1, -1):
        key = ks[d]
        nd = nodes.get(key)
        if nd is None:
            a = b = 0
            lpe = 0.0
        else:
            a, b, lpe, _ = nd
        if x:
            lpe += math.log((b + 0.5) / (a + b + 1.0))
            b += 1
        else:
            lpe += math.log((a + 0.5) / (a + b + 1.0))
            a += 1
        if d == D:
            lpw = lpe
        else:
            sn = nodes.get((d + 1, ks[d + 1][1] ^ (1 << d)))
            lsib = sn[3] if sn is not None else 0.0
            lpw = _ctw_lae(math.log(0.5) + lpe, math.log(0.5) + lw_child + lsib)
        lw_child = lpw
        if commit:
            nodes[key] = [a, b, lpe, lpw]
    return lw_child


def lg_ctw(S, D=8):
    """CTW: Context Tree Weighting (Willems–Shtarkov–Tjalkens) với ước lượng KT, độ sâu D=8. Mỗi ván trong cửa sổ cập nhật 9 nút (ngữ cảnh 0..8 ván trước); mỗi nút giữ 'bằng chứng' của chính nó
    và của việc CHIA nhỏ ngữ cảnh -> gốc là TRUNG BÌNH BAYES của mọi cây ngữ cảnh có độ sâu <= 8 (không phải đoán 'bậc nào đúng'). Dự đoán = so xác suất có trọng số khi nối thêm Tài với nối thêm Xỉu. Luôn bỏ phiếu.
    Mạnh: bắt được cầu ngắn lẫn dài, tự co về bậc thấp khi ít mẫu, co về 50% khi chuỗi ngẫu nhiên (không bịa cấu trúc); chặt về lý thuyết (tối ưu cho nguồn cây ngữ cảnh). Yếu: coi cửa sổ là DỪNG nên chậm theo kịp khi
    cầu đổi chế độ giữa chừng (REGIME · BOCPD · RLS bù chỗ này); chỉ nhìn Tài/Xỉu, không dùng tổng."""
    y = S["y"]
    n = len(y)
    if n < 20:
        return None
    nodes = {}
    for i in range(n):
        _ctw_upd(nodes, _ctw_path(y, i, D), D, y[i], True)
    ks = _ctw_path(y, n, D)
    l1 = _ctw_upd(nodes, ks, D, 1, False)
    l0 = _ctw_upd(nodes, ks, D, 0, False)
    return 1 if l1 > l0 + 1e-12 else 0 if l0 > l1 + 1e-12 else None


# ── MATCHR: khớp hậu tố DÀI NHẤT (kiểu PPM*) có ưu tiên ván gần ──
def lg_matchr(S, Lmax=32, pw=2.0, tau=150.0):
    """MATCHR: mọi vị trí j trong cửa sổ mà ván j-1 trùng ván cuối đều là 1 'ứng viên'; độ dài khớp L = số ván liền trước chung với hậu tố hiện tại (tối đa 32). Mỗi ứng viên bỏ phiếu cho ván y[j] đứng NGAY SAU nó
    với trọng số L^2 × exp(-tuổi/150) (khớp càng dài và càng gần thì càng nặng). Tổng phiếu có dấu > 0 -> TÀI. Luôn bỏ phiếu.
    Mạnh: bậc tự thích nghi theo độ dài khớp — cầu lặp dài thì khớp dài thắng, không có thì rơi về bậc 1 (≈ Markov bậc 1); không có tham số 'bậc'; cực nhanh (<1 ms). Yếu: gần như TRÙNG phiếu AFM · KNNH (cùng họ 'tìm đoạn giống');
    khớp ngẫu nhiên ở L ngắn là nhiễu; không học được quy luật không nằm trong chuỗi liền kề (SPARSE · CMIXL bù chỗ này)."""
    y = S["y"]
    n = len(y)
    if n < 30:
        return None
    s = 0.0
    last = y[n - 1]
    for j in range(1, n):
        if y[j - 1] != last:
            continue
        L = 1
        while L < Lmax and j - 1 - L >= 0 and y[j - 1 - L] == y[n - 1 - L]:
            L += 1
        s += (L ** pw) * math.exp(-(n - j) / tau) * (1 if y[j] else -1)
    return 1 if s > 0 else 0 if s < 0 else None


# ── FTRL: hồi quy logistic ONLINE (FTRL-Proximal) trên đặc trưng n-gram + lag đơn + độ dài đợt ──
def _ftrl_feats(y, i, kmax, lagmax):
    f = [("b",)]
    c = 0
    for k in range(1, kmax + 1):
        if i - k < 0:
            break
        c = c * 2 + y[i - k]
        f.append(("g", k, c))
    for j in range(1, lagmax + 1):
        if i - j < 0:
            break
        f.append(("l", j, y[i - j]))
    if i >= 1:
        r = 1
        while i - 1 - r >= 0 and y[i - 1 - r] == y[i - 1] and r < 12:
            r += 1
        f.append(("r", r, y[i - 1]))
    return f


def lg_ftrl(S, kmax=8, lagmax=12, alpha=0.15, beta=1.0, l1=0.2, l2=1.0, epochs=1):
    """FTRL: hồi quy logistic học ONLINE bằng FTRL-Proximal (tốc độ học riêng từng đặc trưng + phạt L1/L2) trên ~22 đặc trưng thưa của mỗi ván: n-gram độ dài 1..8, bit đơn ở lag 1..12, (độ dài đợt hiện tại, ván trước).
    Duyệt 1 lượt theo thứ tự thời gian (ván j chỉ thấy ván < j) rồi dự đoán ván kế. Luôn bỏ phiếu. Mạnh: học kiểu PHÂN BIỆT (các đặc trưng cạnh tranh trọng số trong 1 mô hình logistic) khác hẳn kiểu ĐẾM của CTW · MATCHR · AFM;
    phạt L1 làm đặc trưng ồn về 0 nên co về 50% khi không có cấu trúc. Yếu: nhạy tham số (alpha / l1); hơi kém khi cầu thưa lag xa; các đặc trưng chồng lấn nên 'chia' trọng số thiếu ổn định khi ít ván."""
    y = S["y"]
    n = len(y)
    if n < 60:
        return None
    z = {}
    nn = {}

    def wt(k):
        zz = z.get(k, 0.0)
        if abs(zz) <= l1:
            return 0.0
        return -(zz - (l1 if zz > 0 else -l1)) / ((beta + math.sqrt(nn.get(k, 0.0))) / alpha + l2)

    for _ in range(epochs):
        for i in range(2, n):
            fs = _ftrl_feats(y, i, kmax, lagmax)
            ws = [wt(k) for k in fs]
            s = max(-30.0, min(30.0, sum(ws)))
            g = 1.0 / (1.0 + math.exp(-s)) - y[i]
            for k, w in zip(fs, ws):
                n0 = nn.get(k, 0.0)
                z[k] = z.get(k, 0.0) + g - (math.sqrt(n0 + g * g) - math.sqrt(n0)) / alpha * w
                nn[k] = n0 + g * g
    s = sum(wt(k) for k in _ftrl_feats(y, n, kmax, lagmax))
    return 1 if s > 0 else 0 if s < 0 else None


# ── ESN2: Echo-State Network nhỏ (reservoir ngẫu nhiên CỐ ĐỊNH) + ridge readout ──
_ESN_NETS = {}


def _esn_net(R, seed=7):
    k = (R, seed)
    net = _ESN_NETS.get(k)
    if net is not None:
        return net
    import random
    rnd = random.Random(seed)
    W = [[(rnd.uniform(-1, 1) if rnd.random() < 0.25 else 0.0) for _ in range(R)] for _ in range(R)]
    v = [1.0] * R
    nm = 1.0
    for _ in range(40):                                         # power iteration -> bán kính phổ ≈ 0.9
        u = [sum(W[i][j] * v[j] for j in range(R)) for i in range(R)]
        nm = math.sqrt(sum(a * a for a in u)) or 1.0
        v = [a / nm for a in u]
    W = [[0.9 * w / nm for w in row] for row in W]
    Win = [rnd.uniform(-1, 1) for _ in range(R)]
    net = _ESN_NETS[k] = (W, Win)
    return net


def _esn_solve(A, b):
    n = len(A)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        d = M[c][c]
        if abs(d) < 1e-12:
            continue
        for j in range(c, n + 1):
            M[c][j] /= d
        for r in range(n):
            if r != c and M[r][c] != 0.0:
                f = M[r][c]
                for j in range(c, n + 1):
                    M[r][j] -= f * M[c][j]
    return [M[i][n] for i in range(n)]


def lg_esn2(S, R=24, leak=0.3, lam=10.0, wash=20):
    """ESN2: Echo-State Network — reservoir 24 nơ-ron tanh (kết nối thưa, bán kính phổ 0.9, seed cố định = kết quả lặp lại được) chạy dọc cửa sổ 300 ván làm 'bộ nhớ động' phi tuyến của chuỗi ±1; chỉ lớp ĐỌC RA
    (ridge λ=10, 25 trọng số) được học: trạng thái hiện tại -> ván kế. Dấu của đầu ra = phiếu. Luôn bỏ phiếu. Mạnh: mô hình PHI TUYẾN có bộ nhớ liên tục — khác hẳn các logic đếm ngữ cảnh rời rạc (trùng phiếu thấp nhất trong nhóm mới);
    bắt tốt cầu nghiêng / trôi chậm và đổi chế độ mượt. Yếu: khó giải thích; có thể 'học' nhiễu (ridge λ lớn + cửa sổ 300 ván chỉ hạn chế chứ không loại bỏ); chậm nhất nhóm mới (~15 ms)."""
    y = S["y"]
    n = len(y)
    if n < 80:
        return None
    W, Win = _esn_net(R)
    x = [0.0] * R
    X = []
    for i in range(n):
        u = 2 * y[i] - 1
        nx = []
        for r in range(R):
            a = Win[r] * u
            Wr = W[r]
            for j in range(R):
                if Wr[j] != 0.0:
                    a += Wr[j] * x[j]
            nx.append((1 - leak) * x[r] + leak * math.tanh(a))
        x = nx
        X.append(x + [1.0])
    D = R + 1
    A = [[0.0] * D for _ in range(D)]
    bv = [0.0] * D
    for i in range(wash, n - 1):
        xi = X[i]
        tgt = 2 * y[i + 1] - 1
        for a in range(D):
            xa = xi[a]
            bv[a] += xa * tgt
            Aa = A[a]
            for c in range(D):
                Aa[c] += xa * xi[c]
    for a in range(D):
        A[a][a] += lam
    w = _esn_solve(A, bv)
    f = sum(w[a] * X[n - 1][a] for a in range(D))
    return 1 if f > 0 else 0 if f < 0 else None


# ── RLS: bộ lọc tuyến tính THÍCH NGHI (Recursive Least Squares, hệ số quên λ) ──
def lg_rlsar(S, p=6, lam=0.99, delta=50.0):
    """RLS: hồi quy tự hồi quy bậc 6 trên chuỗi ±1 (có hằng số), hệ số cập nhật từng ván bằng Recursive Least Squares với hệ số QUÊN λ=0.99 (trí nhớ hiệu dụng ~100 ván) -> dự đoán tuyến tính ván kế từ 6 ván cuối. Dấu = phiếu.
    Luôn bỏ phiếu. Mạnh: THEO KỊP cầu đổi chế độ (bệt <-> 1-1 <-> ngẫu nhiên) nhanh hơn các logic học cố định cả cửa sổ; rất nhẹ (~5 ms). Yếu: chỉ thấy quan hệ TUYẾN TÍNH ở 6 ván liền kề —
    mù với cầu lag thưa / XOR (SPARSE · CMIXL bù); trí nhớ ngắn nên hệ số ồn khi chuỗi ngẫu nhiên (≈ 50%, không hơn)."""
    y = S["y"]
    n = len(y)
    if n < 40:
        return None
    x = [2.0 * v - 1.0 for v in y]
    d = p + 1
    w = [0.0] * d
    P = [[delta if i == j else 0.0 for j in range(d)] for i in range(d)]
    for i in range(p, n):
        u = [1.0] + [x[i - 1 - k] for k in range(p)]
        Pu = [sum(P[a][b] * u[b] for b in range(d)) for a in range(d)]
        den = lam + sum(u[a] * Pu[a] for a in range(d))
        kk = [v / den for v in Pu]
        e = x[i] - sum(w[a] * u[a] for a in range(d))
        w = [w[a] + kk[a] * e for a in range(d)]
        P = [[(P[a][b] - kk[a] * Pu[b]) / lam for b in range(d)] for a in range(d)]
    u = [1.0] + [x[n - 1 - k] for k in range(p)]
    f = sum(w[a] * u[a] for a in range(d))
    return 1 if f > 0 else 0 if f < 0 else None


# ── CỬA SỔ DỮ LIỆU RIÊNG CỦA TỪNG LOGIC (SEQ13v6): mỗi logic CHỈ ĐỌC đúng số ván GẦN NHẤT mà nó mạnh nhất (compute_all cắt lịch sử trước khi gọi) ───────────────────────────────
# Lý do: logic nhẹ/ngắn hạn (KNNH · REGIME · RLS…) càng đọc nhiều ván cũ càng bị pha loãng bởi chế độ cũ; logic mô hình-dày (CMIXL · SPARSE · CTW) cần nhiều ván mới đủ bằng chứng.
# Mọi ván trong cửa sổ có trọng số NHƯ NHAU (không decay). Đổi từng logic bằng env SUNVIW_WIN_<TÊN> (vd. SUNVIW_WIN_CTW=300); chạy tune_windows.py trên data thật để tìm cửa sổ tốt nhất cho từng logic.
# Lịch sử tool giữ HIST_KEEP (mặc định 600) ván — cửa sổ lớn hơn số ván đang có thì logic đọc hết số ván đang có.
LOGIC_WIN_DEFAULT = (("REGIME", 250), ("KNNH", 200), ("SPARSE", 500), ("BLKHAZ", 400), ("BOCPD", 400), ("GBS", 500), ("AFM", 450),
                     ("CTW", 450), ("MATCHR", 450), ("FTRL", 450), ("ESN2", 300), ("RLS", 400), ("CMIXL", 500))
LOGIC_WIN = {_nm: max(40, _env_num("SUNVIW_WIN_" + _nm, _w, int)) for _nm, _w in LOGIC_WIN_DEFAULT}


SUN_LOGICS = [
    ("REGIME", lambda S: lg_regime(S, 20, 250)),
    ("KNNH", lambda S: lg_knnh(S)),
    ("SPARSE", lambda S: lg_sparse(S)),
    ("BLKHAZ", lambda S: lg_blkhaz(S)),
    ("BOCPD", lambda S: lg_bocpd(S)),
    ("GBS", lambda S: lg_gbs(S)),
    ("AFM", lambda S: lg_afm(S)),
    ("CTW", lambda S: lg_ctw(S, 8)),
    ("MATCHR", lambda S: lg_matchr(S)),
    ("FTRL", lambda S: lg_ftrl(S)),
    ("ESN2", lambda S: lg_esn2(S)),
    ("RLS", lambda S: lg_rlsar(S, 6, 0.99)),
    ("CMIXL", lambda S: lg_cmixl(S)),
]


SUN_NAMES = [n for n, _ in SUN_LOGICS]
SUN_SIG = "SEQ13v6:" + ",".join(SUN_NAMES)         # dấu vân tay bộ logic SUN (bỏ dữ liệu graded của bộ logic cũ -> không lẫn data bộ 13 logic SEQ13v6)

# 13 logic là số LẺ nên đa số tất cả logic không bao giờ hoà, nhưng NHÓM CAO/THẤP của AF (kích thước bất kỳ) vẫn có thể hoà -> phiếu phá hoà: lấy phiếu của logic này (mặc định AFM; env SUNVIW_TIE_LOGIC).
SUN_TIE_LOGIC = os.environ.get("SUNVIW_TIE_LOGIC", "AFM")
if SUN_TIE_LOGIC not in SUN_NAMES:
    SUN_TIE_LOGIC = "AFM" if "AFM" in SUN_NAMES else SUN_NAMES[0]


def _sun_tiebreak(votes, cfg=SUN):
    """Phiếu phá hoà của SUN: phiếu của logic SUN_TIE_LOGIC."""
    i = SUN_NAMES.index(cfg.TIE_LOGIC if cfg.TIE_LOGIC in SUN_NAMES else SUN_TIE_LOGIC)
    return votes[i] if i < len(votes) else votes[0]


# ─── WR · QUYẾT ĐỊNH CUỐI · ĐỘ TIN CẬY ───────────────────────────────────
def wr_weights(n, decay=None, floor=None, newest=None, flip=None):
    """Trọng số của n ván gần nhất, thứ tự cũ nhất -> mới nhất (kiểu Fraction = chính xác tuyệt đối khi so với 50%).
    Mặc định: trọng số(tuổi a) = WR_FLOOR + (WR_WEIGHT_NEWEST - WR_FLOOR) * WR_DECAY ** a, a = 0 là ván mới nhất (= WR_WEIGHT_NEWEST).
    Vd n=11, DECAY=0.75, FLOOR=0.35, NEWEST=1.00 -> [0.39, 0.40, 0.42, 0.44, 0.47, 0.50, 0.56, 0.62, 0.72, 0.84, 1.00].
    flip=True (WR_FLIP_WEIGHT) -> ĐẢO NGƯỢC bảng: ván CŨ nhất nặng nhất, giảm dần tới ván MỚI nhất
    -> [1.00, 0.84, 0.72, 0.62, 0.56, 0.50, 0.47, 0.44, 0.42, 0.40, 0.39]."""
    decay = _W_DECAY if decay is None else decay      # None -> config Sun; LC truyền config riêng
    floor = _W_FLOOR if floor is None else floor
    newest = _W_NEWEST if newest is None else newest
    flip = WR_FLIP_WEIGHT if flip is None else flip   # None -> công tắc flip của Sun; LC truyền công tắc riêng
    w = [floor + (newest - floor) * decay ** (n - 1 - k) for k in range(n)]
    return w[::-1] if flip else w


def wr_weights_full():
    """Bảng trọng số đầy đủ của SUN (cũ nhất -> mới nhất, đã tính flip nếu đang bật) - chỉ để hiển thị ở /health và khi khởi động."""
    return [round(float(w), 4) for w in wr_weights(WR_WINDOW)]


def wr_decision(votes, graded, window=None, decay=None, floor=None, min_games=None, newest=None, flip=None):
    """Giống wrDecision() trong HTML + thêm avg (độ tin cậy = TB WR của các logic đang dùng, 0-100).
    CHỈ KHÁC bản gốc ở chỗ WR có TRỌNG SỐ: ván mới nhất = WR_WEIGHT_NEWEST, ván cũ giảm theo hàm mũ nhưng không thấp hơn
    WR_FLOOR (xem CONFIG WR CÓ TRỌNG SỐ). Nếu flip bật thì đảo ngược: ván CŨ nhất nặng nhất -> giảm dần tới ván MỚI nhất.
    Cách chia nhóm / chọn nhóm / hoà phiếu giữ NGUYÊN như bản gốc."""
    all_vote = vote_result(votes)
    flip = WR_FLIP_WEIGHT if flip is None else flip        # None -> công tắc flip của Sun; LC truyền công tắc riêng
    window = WR_WINDOW if window is None else window        # None -> config Sun; LC truyền config riêng
    min_games = WR_MIN_GAMES if min_games is None else min_games
    win = graded[-window:]                            # cũ -> mới
    n = len(win)
    if n < min_games:
        return {"mode": "ALL", "n": n, "final": all_vote, "wins": [], "low": [], "high": [],
                "gT": 0, "gX": 0, "tie": False, "avg": None, "wsum": 0.0, "weights": [], "flip": flip}
    weights = wr_weights(n, decay, floor, newest, flip)
    wsum = sum(weights)                               # tổng trọng số (mẫu số của WR)
    # wins[i] = tổng trọng số các ván logic i đoán đúng (Fraction -> so với 50% chính xác, không sai số float)
    wins = [sum((wt for wt, g in zip(weights, win) if g["votes"][i] == g["actual"]), Fraction(0))
            for i in range(len(votes))]
    low, high = [], []
    for i, w in enumerate(wins):
        (low if w * 2 < wsum else high).append(i)    # WR <50% -> thấp · WR ≥50% -> cao (WR có trọng số)
    use_low = len(low) > len(high)
    idx = low if use_low else high
    gv = [votes[i] for i in idx]
    gT = sum(1 for x in gv if x == TAI)
    gX = len(gv) - gT
    final, tie = vote_result(gv), False
    if final == 'SKIP':
        final, tie = all_vote, True
    avg = float(sum(wins) / (len(wins) * wsum) * 100)  # TB WR có trọng số của các logic đang dùng
    return {"mode": "LOW" if use_low else "HIGH", "n": n, "final": final, "wins": [float(w) for w in wins],
            "low": low, "high": high, "gT": gT, "gX": gX, "tie": tie, "avg": avg,
            "wsum": float(wsum), "weights": [float(w) for w in weights], "flip": flip}


def _wr_decision_cfg(votes, graded, cfg=SUN):
    """wr_decision (cách chốt cũ / dự phòng) với tham số WR của `cfg`. cfg = SUN -> y hệt wr_decision(votes, graded)."""
    return wr_decision(votes, graded, cfg.WR_WINDOW, cfg.W_DECAY, cfg.W_FLOOR, cfg.WR_MIN_GAMES, cfg.W_NEWEST, cfg.WR_FLIP_WEIGHT)


def af_mode_wr(graded, cfg=SUN):
    """WR của 3 chế độ CAO / THẤP / ALL trên AF_MODE_WINDOW ván gần nhất CỦA CHẾ ĐỘ ĐÓ — mỗi chế độ được xét RIÊNG.
    Dữ liệu = vote gốc của nhóm CAO (hv) / nhóm THẤP (lv) / pool ALL = đa số tất cả logic sau bẻ logic (av) đã LƯU trong từng ván đã chấm (cả khi tool đang chạy chế độ khác),
    chấm với kết quả thật. Ván không có vote của chế độ đó (nhóm rỗng / hoà phiếu / chưa đủ ván / ván cũ chưa lưu av) thì bỏ qua.
    Trả {"CAO": {...}, "THAP": {...}, "ALL": {...}}, mỗi chế độ có: n · w (số ván đúng) · need · wr (% hoặc None nếu chưa đủ ván) · flip (True = WR < AF_MODE_BELOW) · chuoi (cũ -> mới, True = đúng)."""
    need = max(1, min(cfg.AF_MODE_MIN, cfg.AF_MODE_WINDOW))
    out = {}
    for mode, key in (("CAO", "hv"), ("THAP", "lv"), ("ALL", "av")):
        rows = []
        for g in reversed(graded):                       # đi từ ván mới nhất lùi về, lấy đủ AF_MODE_WINDOW ván có vote của chế độ này
            v = g.get(key)
            if v in (TAI, XIU):
                rows.append(v == g["actual"])
                if len(rows) >= cfg.AF_MODE_WINDOW:
                    break
        rows.reverse()
        n, w = len(rows), sum(rows)
        ready = n >= need
        out[mode] = {"n": n, "w": w, "need": need, "wr": (w * 100.0 / n) if ready else None,
                     "flip": bool(cfg.AF_MODE_FLIP and ready and w * 100 < cfg.AF_MODE_BELOW * n), "chuoi": rows}   # AF_MODE_FLIP tắt -> flip luôn False (không bẻ chế độ)
    return out


def _af_prev_mode(graded):
    """Chế độ (ALL | CAO | THAP) của ván đã chấm GẦN NHẤT — dùng để xét đổi chế độ. Ván đầu / ván cũ chưa lưu chế độ (AF tắt lúc đó) -> ALL."""
    if graded:
        m = graded[-1].get("mode")
        if m in ("ALL", "CAO", "THAP"):
            return m
    return "ALL"


AF_SWITCH_PRIO_ORDER = {"ALL": "CAO", "CAO": "ALL", "THAP": "CAO"}   # ván trước ở chế độ nào -> khi 2 chế độ còn lại cùng đủ phiếu thì ưu tiên chế độ này


def _af_pick_mode(mvotes, cur, need, lead=False, prio=False):
    """ĐỔI CHẾ ĐỘ DỄ HƠN (AF_SWITCH): từ chế độ hiện tại `cur`, chọn chế độ cho ván này theo phiếu của 3 chế độ `mvotes` ({"ALL","CAO","THAP"} -> số logic).
    lead=False (mặc định, đúng ý "chỉ cần N phiếu"): chế độ KHÁC có >= `need` phiếu (vd 6/13; bản gốc phải đa số 7/13) là ĐỔI, kể cả khi chế độ hiện tại đang nhiều phiếu hơn.
        Nhiều chế độ khác cùng đủ `need` -> lấy chế độ nhiều phiếu nhất; bằng nhau ở đầu bảng, hoặc không chế độ khác nào đủ `need` -> GIỮ `cur`.
        prio=True (AF_SWITCH_PRIO): khi CẢ 2 chế độ còn lại cùng đủ `need` phiếu thì KHÔNG so số phiếu nữa mà ưu tiên theo chế độ ván trước:
            đang ALL -> ưu tiên CAO · đang CAO -> ưu tiên ALL · đang THẤP -> ưu tiên CAO (xem AF_SWITCH_PRIO_ORDER). Chỉ 1 chế độ đủ phiếu -> đổi sang chế độ đó như thường.
    lead=True (êm hơn): chế độ mới còn phải DẪN ĐẦU DUY NHẤT (nhiều phiếu hơn mọi chế độ khác, kể cả chế độ đang chạy) mới đổi.
        Lưu ý: 13 logic chia cho 3 chế độ thì bên dẫn đầu luôn >= 5 phiếu nên với lead=True mọi `need` <= 5 cho kết quả y hệt nhau."""
    if lead:
        ok = {m: c for m, c in mvotes.items() if c >= need}
        if not ok:
            return cur
        best = max(ok.values())
        top = [m for m, c in ok.items() if c == best]
        if cur in top or len(top) != 1:
            return cur
        return top[0]
    cand = {m: c for m, c in mvotes.items() if m != cur and c >= need}
    if not cand:
        return cur
    if prio and len(cand) >= 2:                           # cả 2 chế độ còn lại đều đủ phiếu -> ưu tiên theo chế độ ván trước
        pm = AF_SWITCH_PRIO_ORDER.get(cur)
        if pm in cand:
            return pm
    best = max(cand.values())
    top = [m for m, c in cand.items() if c == best]
    return top[0] if len(top) == 1 else cur


def af_decision(votes, graded, cfg=SUN):
    """AF (auto-flip + CAO/THẤP + bẻ theo WR chế độ) của SUN — port từ SUNVIW_9logics_autoflip_auto.html (xem khối CONFIG AF).
    Trả dict: mode (CAO | THAP | ALL) · final (SAU bẻ chế độ) · base (TRƯỚC bẻ chế độ) · mflip (đã bẻ chế độ) · tie (pool hoà phiếu -> dùng đa số tất cả logic)
    preds (phiếu sau bẻ logic) · flips[i] (LOW | HIGH | None) · wins / wsum (trọng số) · eff[i] (WR dùng, 0-100) · group[i] (CAO | THAP | None) · hi / lo (chỉ số logic mỗi nhóm)
    hv / lv / av (vote gốc của nhóm CAO / nhóm THẤP / pool ALL — LƯU vào ván đã chấm) · gT / gX (phiếu TÀI / XỈU trong pool) · avg (TB WR dùng của pool, độ tin cậy) · mw (WR 3 chế độ CAO / THAP / ALL)
    demoted (True = nhóm CAO / THẤP được chọn ít hơn đa số toàn bộ logic -> đã hạ về ALL) · need_maj (số logic tối thiểu để một nhóm được dùng).
    prev (chế độ ván trước) · mvotes (phiếu 3 chế độ: ALL = logic không thuộc nhóm nào · CAO · THAP) · sw_need (số phiếu để đổi chế độ, AF_SWITCH_NEED) · switched (True = chế độ ván này khác ván trước).
    AF_SWITCH bật: chế độ NHỚ ván trước, chế độ khác đủ sw_need phiếu (6/13) là đổi (xem _af_pick_mode); AF_SWITCH tắt: nhóm đông hơn thắng + đa số 7/13 như bản gốc.
    AF_GROUP_FLIPPED_ONLY: chỉ logic bị bẻ mới có group (CAO | THAP); logic không bẻ -> group None = mặc định ALL."""
    nl = len(votes)
    all_vote = vote_result(votes)
    win = graded[-cfg.WR_WINDOW:]                             # cũ -> mới (cùng cửa sổ WR với cách cũ của SUN)
    n = len(win)
    need = max(1, min(cfg.AF_MIN_GAMES, cfg.WR_WINDOW))
    mw = af_mode_wr(graded, cfg)
    out = {"mode": "ALL", "n": n, "need": need, "final": all_vote, "base": all_vote, "mflip": False, "tie": False, "demoted": False,
           "need_maj": nl // 2 + 1,
           "prev": _af_prev_mode(graded), "mvotes": {"ALL": nl, "CAO": 0, "THAP": 0}, "sw_need": max(1, min(int(cfg.AF_SWITCH_NEED), nl)),     # chưa đủ ván -> chưa chia nhóm: mọi logic = phiếu ALL
           "switched": _af_prev_mode(graded) != "ALL",
           "preds": list(votes), "flips": [None] * nl, "wins": [], "wsum": 0.0, "weights": [], "eff": [None] * nl,
           "group": [None] * nl, "hi": [], "lo": [], "hv": None, "lv": None, "av": all_vote if all_vote in (TAI, XIU) else None, "pool": list(range(nl)),     # pool = logic THỰC SỰ tham gia vote ván này (chưa đủ ván -> vote tất cả)
           "gT": sum(1 for v in votes if v == TAI), "gX": sum(1 for v in votes if v == XIU), "avg": None, "mw": mw}
    if n < need:                                          # chưa đủ ván -> không bẻ, vote tất cả (như file HTML)
        return out
    weights = wr_weights(n, cfg.W_DECAY, cfg.W_FLOOR, cfg.W_NEWEST, cfg.WR_FLIP_WEIGHT)                               # trọng số WR của SUN (cũ nhất -> mới nhất)
    wsum = sum(weights)
    wins = [sum((wt for wt, g in zip(weights, win) if g["votes"][i] == g["actual"]), Fraction(0)) for i in range(nl)]
    thr_lo, thr_hi = Fraction(str(cfg.AF_FLIP_LOW)), Fraction(str(cfg.AF_FLIP_HIGH))
    b_lo = (Fraction(str(cfg.AF_FLIP_LOW_MIN)), Fraction(str(cfg.AF_FLIP_LOW_MAX)))                       # vùng bẻ THẤP [min, max] (%)
    b_hi = (Fraction(str(cfg.AF_FLIP_HIGH_MIN)), Fraction(str(cfg.AF_FLIP_HIGH_MAX)))                     # vùng bẻ CAO  [min, max] (%)

    def _flip_kind(w):
        x = w * 100                                                                               # so với (% × tổng trọng số) -> chính xác, không sai số float
        if cfg.AF_FLIP_BAND:                                                                          # chỉ bẻ khi WR nằm TRONG vùng (gồm đầu mút); ngoài vùng -> không bẻ
            if b_lo[0] * wsum <= x <= b_lo[1] * wsum:
                return "LOW"
            if b_hi[0] * wsum <= x <= b_hi[1] * wsum:
                return "HIGH"
            return None
        return "LOW" if x < thr_lo * wsum else ("HIGH" if x > thr_hi * wsum else None)             # cách cũ: không có cận

    preds, flips, effw, group = [], [], [], []
    for i, w in enumerate(wins):
        f = _flip_kind(w)                                                                         # Bước 1: bẻ logic
        e = (wsum - w) if f else w                        # trọng số đúng SAU bẻ -> WR dùng = 100 − WR gốc khi bị bẻ
        preds.append(flip_pred(votes[i]) if f else votes[i])
        flips.append(f)
        effw.append(e)
        if cfg.AF_GROUP_FLIPPED_ONLY and not f:                                                         # Bước 2: logic KHÔNG bẻ (WR ngoài vùng bẻ) -> không thuộc nhóm nào = mặc định ALL
            group.append(None)
        else:                                                                                         # nhóm theo WR dùng (sau bẻ)
            group.append("CAO" if e * 2 > wsum else ("THAP" if e * 2 < wsum else None))
    hi = [i for i, g in enumerate(group) if g == "CAO"]
    lo = [i for i, g in enumerate(group) if g == "THAP"]
    need_maj = nl // 2 + 1                                # đa số của TOÀN BỘ logic (12 -> 7)

    def _pv(idx):
        return vote_result([preds[i] for i in idx]) if idx else None

    hv, lv = _pv(hi), _pv(lo)
    av = vote_result(preds)                               # vote gốc của pool ALL (đa số tất cả logic sau bẻ logic) — lưu để đo WR riêng của chế độ ALL
    mvotes = {"ALL": nl - len(hi) - len(lo), "CAO": len(hi), "THAP": len(lo)}    # "phiếu chọn chế độ" của từng logic: nhóm CAO -> CAO · nhóm THẤP -> THẤP · không thuộc nhóm nào -> ALL
    prev_mode = _af_prev_mode(graded)                     # chế độ của ván trước (ván đầu / ván cũ chưa lưu -> ALL)
    sw_need = max(1, min(int(cfg.AF_SWITCH_NEED), nl))
    demoted = False
    if cfg.AF_SWITCH:                                     # ĐỔI CHẾ ĐỘ DỄ HƠN: chế độ khác đủ sw_need phiếu (mặc định 6/13) là đổi, thay vì phải đa số 7/13
        mode = _af_pick_mode(mvotes, prev_mode, sw_need, bool(cfg.AF_SWITCH_LEAD), bool(cfg.AF_SWITCH_PRIO))
        if mode == "CAO":
            pool, base = hi, hv
        elif mode == "THAP":
            pool, base = lo, lv
        else:
            pool, base = list(range(nl)), vote_result(preds)
        if mode != "ALL" and not pool:                    # đang giữ CAO / THẤP mà nhóm hết logic -> không ai vote, tạm dùng ALL ván này
            demoted = True
            mode, pool, base = "ALL", list(range(nl)), vote_result(preds)
    else:                                                 # cách gốc: nhóm đông hơn thắng · nhóm CAO / THẤP phải >= đa số (7/13) nếu AF_GROUP_NEED_MAJORITY
        if len(hi) > len(lo):
            mode, pool, base = "CAO", hi, hv
        elif len(lo) > len(hi):
            mode, pool, base = "THAP", lo, lv
        else:
            mode, pool = "ALL", list(range(nl))
            base = vote_result(preds)
        if cfg.AF_GROUP_NEED_MAJORITY and mode != "ALL" and len(pool) < need_maj:    # nhóm được chọn ít hơn đa số của pool ALL -> bỏ nhóm, dùng ALL
            demoted = True
            mode, pool = "ALL", list(range(nl))
            base = vote_result(preds)
    tie = False
    if base == "SKIP":                                    # pool hoà phiếu -> đa số tất cả logic (đã bẻ logic); vẫn hoà -> đa số gốc (như cách cũ)
        tie = True
        base = vote_result(preds)
        if base == "SKIP":
            base = all_vote
    mflip, final = False, base
    if cfg.AF_MODE_FLIP and not tie and mw[mode]["flip"]:    # Bước 3: bẻ theo WR RIÊNG của chế độ đang chạy (CAO / THẤP / ALL — chỉ khi AF_MODE_FLIP bật)
        mflip, final = True, flip_pred(base)
    pv = [preds[i] for i in pool]
    vpool = list(range(nl)) if tie else list(pool)         # logic THAM GIA vote ván này (nhóm hoà phiếu -> thực tế dùng pool ALL) — panel hiện "logic đang dự đoán"
    out.update(mode=mode, final=final, base=base, mflip=mflip, tie=tie, demoted=demoted, need_maj=need_maj, pool=vpool, preds=preds, flips=flips,
               prev=prev_mode, mvotes=mvotes, sw_need=sw_need, switched=(mode != prev_mode),
               wins=[float(w) for w in wins], wsum=float(wsum), weights=[float(w) for w in weights],
               eff=[float(e / wsum * 100) for e in effw], group=group, hi=hi, lo=lo,
               hv=hv if hv in (TAI, XIU) else None, lv=lv if lv in (TAI, XIU) else None, av=av if av in (TAI, XIU) else None,
               gT=sum(1 for x in pv if x == TAI), gX=sum(1 for x in pv if x == XIU),
               avg=(float(sum(effw[i] for i in pool) / (len(pool) * wsum) * 100) if pool else None))
    return out


def decide_final(votes, graded, dec_wr=None, cfg=SUN):
    """Chốt final của SUN: AF (nếu bật) -> cách cũ (wr_decision). Trả (final, af). `af` = dict của af_decision khi final do AF chốt, không thì None.
    `dec_wr` truyền sẵn thì không tính lại wr_decision; chỉ tính khi thật sự cần quay về cách cũ (AF tắt)."""
    if cfg.AF_ENABLED:
        af = af_decision(votes, graded, cfg)
        if af["final"] not in (TAI, XIU):                 # hoà tới tận bước cuối (nhóm CAO/THẤP có thể chẵn) -> phá hoà, không để 'SKIP' lọt ra API
            tb = _sun_tiebreak(votes, cfg)
            af["final"] = tb
            if af["base"] not in (TAI, XIU):
                af["base"] = tb
        return af["final"], af
    if dec_wr is None:
        dec_wr = _wr_decision_cfg(votes, graded, cfg)
    fin = dec_wr["final"]
    if fin not in (TAI, XIU):
        fin = _sun_tiebreak(votes, cfg)
    return fin, None


def af_flip_applies(mode, cfg=SUN):
    """Final của ván AF ở chế độ `mode` (CAO | THAP | ALL) có bị bẻ thêm không.
    AF_FLIP_FINAL = bẻ mọi chế độ · AF_FLIP_FINAL_CAO = chỉ CAO · AF_FLIP_FINAL_THAP = chỉ THẤP · AF_FLIP_FINAL_CT = gộp CAO + THẤP (ALL giữ nguyên) · AF_FLIP_FINAL_ALL = chỉ ALL (CAO/THẤP giữ nguyên).
    Phép HOẶC: có ít nhất 1 công tắc áp dụng cho chế độ đó thì bẻ ĐÚNG 1 lần."""
    if cfg.AF_FLIP_FINAL:
        return True
    if mode == "ALL":
        return bool(cfg.AF_FLIP_FINAL_ALL)
    if mode == "CAO":
        return bool(cfg.AF_FLIP_FINAL_CAO or cfg.AF_FLIP_FINAL_CT)
    if mode == "THAP":
        return bool(cfg.AF_FLIP_FINAL_THAP or cfg.AF_FLIP_FINAL_CT)
    return False


def out_final_sun(final, used_af=False, mode=None, cfg=SUN):
    """Final SUN đã đưa ra API. Ván do AF chốt: bẻ theo af_flip_applies(mode) — AF_FLIP_FINAL (mọi chế độ) / AF_FLIP_FINAL_CT (chỉ CAO/THẤP) / AF_FLIP_FINAL_ALL (chỉ ALL)
    (KHÔNG dính FLIP_FINAL chung — AF đã tự bẻ logic + chế độ). Ván quay về cách cũ (AF tắt): bẻ theo FLIP_FINAL như trước."""
    if used_af:
        return flip_pred(final) if af_flip_applies(mode, cfg) else final
    return flip_pred(final) if cfg.FLIP_FINAL else final


def out_final_g(g, cfg=SUN):
    """Final đã đưa ra API của 1 ván đã chấm (entry không có khoá 'af' = ván chốt bằng cách cũ; entry AF có 'mode' = CAO | THAP | ALL)."""
    return out_final_sun(g["final"], g.get("af", False), g.get("mode"), cfg)


def be_final_g(g, cfg=SUN):
    """Ván đã chấm này có bị bẻ final (theo cấu hình HIỆN TẠI: AF_FLIP_FINAL / _CT / _ALL · cách cũ -> FLIP_FINAL) khi đưa ra API không."""
    return af_flip_applies(g.get("mode"), cfg) if g.get("af", False) else bool(cfg.FLIP_FINAL)


# ─── LỊCH SỬ UPSTREAM ────────────────────────────────────────────────────
def _parse_int(v):
    m = re.match(r"\s*[+-]?\d+", str(v))
    return int(m.group()) if m else None


def norm_kq(s):
    t = unicodedata.normalize("NFD", str(s or ""))
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn").lower()
    if "tai" in t:
        return TAI
    if "xiu" in t:
        return XIU
    return None


def parse_history(data):
    if isinstance(data, list):
        arr = data
    elif isinstance(data, dict) and isinstance(data.get("history"), list):
        arr = data["history"]
    elif isinstance(data, dict) and "phien" in data:          # API /api/tx: 1 object = 1 phiên mới nhất
        arr = [data]
    else:
        arr = []
    m = {}
    for r in arr:
        if not isinstance(r, dict):
            continue
        phien = _parse_int(r.get("phien"))
        d1 = _parse_int(r.get("xuc_xac_1"))
        d2 = _parse_int(r.get("xuc_xac_2"))
        d3 = _parse_int(r.get("xuc_xac_3"))
        if None in (phien, d1, d2, d3):
            continue
        if any(d < 1 or d > 6 for d in (d1, d2, d3)):
            continue
        total = d1 + d2 + d3
        m[phien] = {"phien": phien, "d1": d1, "d2": d2, "d3": d3, "total": total,
                    "actual": norm_kq(r.get("ket_qua")) or actual_of(total),
                    "time": r.get("thoi_gian") or ""}
    return [m[k] for k in sorted(m)]            # cũ -> mới


_hist_store = {}            # phien -> record (các phiên đã quét được, tool tự tích lũy vì upstream chỉ trả 1 phiên)
_hist_loaded = False


def hist_update(records):
    """Gộp các phiên vừa quét vào lịch sử (nạp từ HIST_PATH lần đầu, lưu lại sau mỗi lần), trả về list cũ -> mới.
    Chỉ gọi trong refresh() (đã có _refresh_lock)."""
    global _hist_loaded
    if not _hist_loaded:
        _hist_loaded = True
        try:
            with open(HIST_PATH, "r", encoding="utf-8") as f:
                for r in json.load(f):
                    if isinstance(r, dict) and all(k in r for k in ("phien", "d1", "d2", "d3", "total", "actual")):
                        _hist_store[r["phien"]] = r
        except Exception:  # noqa: BLE001
            pass
    for r in records:
        _hist_store[r["phien"]] = r
    for k in sorted(_hist_store)[:-HIST_KEEP]:
        del _hist_store[k]
    out = [_hist_store[k] for k in sorted(_hist_store)]
    try:
        tmp = HIST_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        os.replace(tmp, HIST_PATH)
    except Exception:  # noqa: BLE001
        pass
    return out


def persist_load():
    """Load danh sách graded đã lưu từ file JSON. Trả về [] nếu không có / lỗi."""
    try:
        with open(PERSIST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            # bỏ entry lưu từ bộ logic khác (vd. file cũ dùng logic MD5) -> tránh lệch chỉ số vote
            return [g for g in data if isinstance(g, dict) and g.get("sig") == SUN_SIG]
    except Exception:  # noqa: BLE001
        pass
    return []


def persist_save(graded):
    """Ghi tối đa PERSIST_KEEP entry cuối vào file JSON (atomic write)."""
    try:
        chunk = graded[-PERSIST_KEEP:]
        tmp = PERSIST_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False)
        os.replace(tmp, PERSIST_PATH)
    except Exception:  # noqa: BLE001
        pass


def merge_graded(saved, fresh):
    """Ghép saved (từ file) + fresh (rebuild từ hist hiện tại), dedup + sort theo session.
    fresh luôn được ưu tiên (overwrite saved nếu trùng session)."""
    by_sess = {g["session"]: g for g in saved}
    for g in fresh:
        by_sess[g["session"]] = g
    return [by_sess[k] for k in sorted(by_sess)]


def rebuild_graded(hist, saved_graded=None, cfg=SUN):
    """Chấm lại lịch sử: dự đoán phiên k+1 từ LỊCH SỬ tới phiên k (13 logic SEQ13v6 cần cả chuỗi chứ không chỉ xúc xắc phiên k), chấm bằng kết quả thật.
    Ván ĐÃ lưu trong saved_graded giữ nguyên, không tính lại -> nhanh và dự đoán đã đưa ra không đổi; chỉ chấm thêm các ván MỚI hơn ván đã lưu (file trống: tối đa SUN_REBUILD_MAX ván gần nhất)."""
    fresh = []
    seed = list(saved_graded) if saved_graded else []
    newest = max((g["session"] for g in seed), default=-1)
    oldest = min((g["session"] for g in seed), default=None)
    backfill = oldest is not None and len(seed) < cfg.PERSIST_KEEP     # file chưa đủ PERSIST_KEEP ván (vd. file cũ chỉ có 50) -> chấm BÙ các ván CŨ hơn ván cũ nhất đã lưu
    for i in range(max(0, len(hist) - 1 - cfg.REBUILD_MAX), len(hist) - 1):
        cur, nxt = hist[i], hist[i + 1]
        if getattr(cfg, "CONSEC_CHECK", True) and nxt["phien"] != cur["phien"] + 1:
            continue
        if not (nxt["phien"] > newest or (backfill and nxt["phien"] < oldest)):    # chỉ ván MỚI hơn ván đã lưu, hoặc (khi chấm bù) ván CŨ hơn ván cũ nhất đã lưu
            continue
        votes = compute_all(hist[:i + 1])
        # Chỉ dùng các ván đã chấm TRƯỚC phiên nxt (seed có thể chứa ván mới hơn -> nhìn trước đáp án, làm lệch đánh giá)
        combined = [g for g in merge_graded(seed, fresh) if g["session"] < nxt["phien"]]
        final, af = decide_final(votes, combined, None, cfg)                          # AF -> cách cũ
        entry = {"session": nxt["phien"], "total": nxt["total"], "actual": nxt["actual"],
                 "votes": votes, "final": final, "ok": final == nxt["actual"],
                 "sig": SUN_SIG}
        if af is not None:                                                # lưu dữ liệu 3 chế độ: vote gốc của nhóm CAO (hv) · nhóm THẤP (lv) · pool ALL (av) của ván này
            entry.update(af=True, mode=af["mode"], mflip=af["mflip"], hv=af["hv"], lv=af["lv"], av=af["av"])
        fresh.append(entry)
    return merge_graded(seed, fresh)


def regrade_graded(graded, cfg=SUN):
    """CHẤM LẠI toàn bộ các ván đã lưu theo CONFIG HIỆN TẠI (ngưỡng AF · vùng bẻ · bẻ final · WR_*...).
    Dùng lại `votes` (13 logic) đã lưu trong từng ván -> KHÔNG chạy lại compute_all nên rất nhanh (vài trăm ms thay vì phải đợi ván mới chạy tới).
    Đi từ ván cũ -> mới: ván k được chốt bằng WR của các ván đã chấm lại TRƯỚC nó (y hệt lúc chạy live, không nhìn trước đáp án).
    Giữ nguyên phiên · tổng · kết quả thật · votes; chỉ tính lại final / ok / af / mode / mflip / hv / lv / av. Ván không có votes thì giữ nguyên."""
    out = []
    for g in graded:
        votes = g.get("votes")
        if not isinstance(votes, list) or not votes or g.get("actual") not in (TAI, XIU):
            out.append(g)
            continue
        final, af = decide_final(votes, out, None, cfg)
        e = {k: v for k, v in g.items() if k not in ("af", "mode", "mflip", "hv", "lv", "av")}
        e.update(final=final, ok=final == g["actual"])
        if af is not None:
            e.update(af=True, mode=af["mode"], mflip=af["mflip"], hv=af["hv"], lv=af["lv"], av=af["av"])
        out.append(e)
    return out


def _regrade_report(before, after, cfg):
    """So sánh trước / sau khi chấm lại: số ván đổi dự đoán + đúng/sai trong EVAL_WINDOW ván gần nhất."""
    changed = sum(1 for a, b in zip(before, after) if out_final_g(a, cfg) != out_final_g(b, cfg))
    ba, aa = _recent_accuracy(before, cfg.EVAL_WINDOW, cfg=cfg), _recent_accuracy(after, cfg.EVAL_WINDOW, cfg=cfg)
    return {"so_van": len(after), "doi_du_doan": changed,
            "truoc": {"dung": ba["dung"], "tong": ba["tong"]}, "sau": {"dung": aa["dung"], "tong": aa["tong"]}}


def sun_regrade():
    """Nút \"Tính lại theo config\" của SUN: chấm lại file graded bằng config hiện tại rồi dựng lại kết quả hiển thị. Giữ nguyên lịch sử."""
    with _refresh_lock:
        saved = persist_load()
        if not saved:
            return {"so_van": 0, "doi_du_doan": 0, "truoc": {"dung": 0, "tong": 0}, "sau": {"dung": 0, "tong": 0}}
        new = regrade_graded(saved, SUN)
        rep = _regrade_report(saved, new, SUN)
        persist_save(new)
        hist = [_hist_store[k] for k in sorted(_hist_store)]
        if hist:
            res = build_result(hist)                      # dựng lại dự đoán + lich_su từ graded đã chấm lại (không có ván mới nên rất nhanh)
            with _state_lock:
                _state.update(result=res, latest=hist[-1]["phien"], updated=_now())
        return rep


def build_result(hist, cfg=SUN, persist=None):
    """Từ lịch sử (cũ -> mới) -> dict kết quả dự đoán cho phiên kế tiếp.
    cfg = SUN (mặc định) hoặc TableCfg của 1 bàn HITCLUB · persist = (load, save) nơi lưu các ván đã chấm (None -> file graded của SUN)."""
    latest = hist[-1]
    load, save = persist if persist else (persist_load, persist_save)
    saved = load()
    graded = rebuild_graded(hist, saved_graded=saved, cfg=cfg)
    save(graded)
    votes = compute_all(hist)
    dec = _wr_decision_cfg(votes, graded, cfg)                                   # cách chốt cũ: luôn tính (phương án dự phòng + hiển thị WR cũ)
    final, af = decide_final(votes, graded, dec, cfg)                       # AF -> cách cũ
    used_af = af is not None
    avg = af["avg"] if used_af else dec["avg"]
    mwc = af["mw"].get(af["mode"]) if used_af and cfg.AF_MODE_FLIP and af["mode"] in ("CAO", "THAP", "ALL") else None     # WR RIÊNG của CHẾ ĐỘ đang chạy (CAO / THAP / ALL · AF_MODE_FLIP tắt -> None, panel ẩn dòng này)
    base = {
        "ok": True,
        "phien": latest["phien"] + 1,
        "du_doan": out_final_sun(final, used_af, af["mode"] if used_af else None, cfg),
        "be_final": af_flip_applies(af["mode"], cfg) if used_af else cfg.FLIP_FINAL,   # bẻ ĐANG ÁP DỤNG cho ván này (AF -> theo chế độ: AF_FLIP_FINAL / _CT / _ALL · cách cũ -> FLIP_FINAL)
        "af": used_af,                                                 # True = final ván này do AF chốt (auto-flip + CAO/THẤP + bẻ chế độ)
        "che_do": af["mode"] if used_af else None,                     # CAO | THAP | ALL (chỉ khi AF chốt)
        "be_che_do": af["mflip"] if used_af else False,                # True = ván này đã bẻ theo WR chế độ (WR 7 ván của chế độ đang chạy < 45%)
        "du_doan_goc": final,                                          # final SAU bẻ chế độ, TRƯỚC bẻ final (AF_FLIP_FINAL / _CT / _ALL) — panel dùng để hiện chuỗi gốc -> bẻ
        "du_doan_truoc_be_che_do": af["base"] if used_af else None,    # final TRƯỚC bẻ chế độ (chỉ khi AF chốt)
        "wr_che_do_hien_tai": None if mwc is None else {               # WR 7 ván của chế độ đang chạy (CAO | THAP) -> panel hiện "vì sao bẻ / không bẻ chế độ"
            "che_do": af["mode"], "so_van": mwc["n"], "dung": mwc["w"], "van_toi_thieu": mwc["need"],
            "wr": None if mwc["wr"] is None else round(mwc["wr"], 1),
            "cua_so": cfg.AF_MODE_WINDOW, "nguong_be": cfg.AF_MODE_BELOW, "se_be": mwc["flip"]},
        "do_tin_cay": None if avg is None else round(avg, 1),
        "phien_truoc": latest["phien"],
        "xuc_xac": [latest["d1"], latest["d2"], latest["d3"]],
        "tong": latest["total"],
        "ket_qua_truoc": latest["actual"],
        "so_van_wr": af["n"] if used_af else dec["n"],
        "tool_dung_sai_10_van": _recent_accuracy(graded, cfg.EVAL_WINDOW, with_chuoi=True, cfg=cfg),
    }
    tai = sum(1 for v in votes if v == TAI)
    detail = {
        "vote_21": {"TÀI": tai, "XỈU": len(votes) - tai},        # tên khóa giữ nguyên cho tương thích; giờ đếm trên các logic đang dùng
        "so_logic": len(votes),
        "bo_logic": "SEQ13v6 (chuoi + xuc xac + tong + so phien, khong dung MD5)",
        "nhom_theo": ({"ALL": "AF · da so", "CAO": "AF · WR cao", "THAP": "AF · WR thap"}[af["mode"]] if used_af
                      else {"ALL": "da so", "LOW": "WR thap", "HIGH": "WR cao"}[dec["mode"]]),
        "nhom_tai_xiu": ({"TÀI": af["gT"], "XỈU": af["gX"]} if used_af else {"TÀI": dec["gT"], "XỈU": dec["gX"]}),
        "hoa_dung_da_so_21": dec["tie"],
        "af": {                                                    # AF (auto-flip + CAO/THẤP + bẻ theo WR chế độ) — xem khối CONFIG AF
            "bat": cfg.AF_ENABLED,
            "dang_dung": used_af,                                  # True = final ván này do AF chốt
            "bat_be_che_do": cfg.AF_MODE_FLIP,                         # công tắc bước 3 (bẻ chế độ): False = TẮT (mặc định)
            "che_do": af["mode"] if used_af else None,             # CAO | THAP | ALL
            "be_che_do": af["mflip"] if used_af else False,        # True = đã bẻ theo WR chế độ ở ván này
            "final_truoc_be_che_do": af["base"] if used_af else None,
            "hoa_phieu_nhom": af["tie"] if used_af else False,     # True = nhóm được chọn hoà phiếu -> dùng đa số tất cả logic
            "so_van_wr": af["n"] if used_af else None,
            "van_toi_thieu": max(1, min(cfg.AF_MIN_GAMES, cfg.WR_WINDOW)),
            "nguong_be_logic": {"thap": cfg.AF_FLIP_LOW, "cao": cfg.AF_FLIP_HIGH},
            "gioi_han_vung_be": {                                  # chỉ bẻ logic khi WR nằm TRONG vùng (bat=False -> dùng nguong_be_logic như cũ)
                "bat": cfg.AF_FLIP_BAND,
                "thap": [cfg.AF_FLIP_LOW_MIN, cfg.AF_FLIP_LOW_MAX],
                "cao": [cfg.AF_FLIP_HIGH_MIN, cfg.AF_FLIP_HIGH_MAX]},
            "so_logic_nhom": {"CAO": len(af["hi"]), "THAP": len(af["lo"])} if used_af else None,
            "logic_du_doan": [SUN_NAMES[i] for i in af["pool"]] if used_af else [],      # logic THAM GIA vote ván này 
            "chi_be_vao_nhom": cfg.AF_GROUP_FLIPPED_ONLY,              # True = chỉ logic ĐÃ BỊ BẺ mới vào nhóm CAO / THẤP, logic không bẻ mặc định ALL
            "can_da_so_nhom": cfg.AF_GROUP_NEED_MAJORITY,              # True = nhóm CAO / THẤP phải có >= đa số toàn bộ logic, không thì dùng ALL
            "da_so_toi_thieu": af["need_maj"] if used_af else (len(votes) // 2 + 1),
            "ha_xuong_all": af["demoted"] if used_af else False,   # True = nhóm CAO / THẤP chọn được ít hơn đa số -> đã hạ về ALL ở ván này
            "uu_tien_doi_che_do": cfg.AF_SWITCH_PRIO,                   # True = 2 chế độ còn lại cùng đủ phiếu -> ưu tiên theo chế độ ván trước (ALL->CAO · CAO->ALL · THẤP->CAO)
            "doi_che_do_de": cfg.AF_SWITCH,                            # True = đổi chế độ ALL / CAO / THẤP chỉ cần `phieu_doi_che_do` phiếu (thay vì đa số 7/13)
            "phieu_doi_che_do": af["sw_need"] if used_af else max(1, min(int(cfg.AF_SWITCH_NEED), len(votes))),
            "che_do_truoc": af["prev"] if used_af else None,           # chế độ của ván trước (cơ sở để xét đổi chế độ)
            "phieu_che_do": af["mvotes"] if used_af else None,         # số logic bỏ phiếu cho từng chế độ: ALL (không bẻ) · CAO · THAP
            "da_doi_che_do": af["switched"] if used_af else False,     # True = chế độ ván này khác ván trước
            "logic_bi_be": [SUN_NAMES[i] for i, f in enumerate(af["flips"]) if f] if used_af else [],
            "wr_che_do": {                                         # WR của từng chế độ trên AF_MODE_WINDOW ván gần nhất CỦA CHẾ ĐỘ ĐÓ (vote gốc, chưa bẻ chế độ)
                m: {"so_van": x["n"], "dung": x["w"], "wr": None if x["wr"] is None else round(x["wr"], 1),
                    "be": x["flip"],                               # True = WR < AF_MODE_BELOW -> chế độ này sẽ bị bẻ khi được chọn
                    "chuoi": "".join(ICON_DUNG if ok else ICON_SAI for ok in reversed(x["chuoi"]))}   # mới -> cũ
                for m, x in (af["mw"] if used_af else af_mode_wr(graded, cfg)).items()},
            "cua_so_che_do": cfg.AF_MODE_WINDOW,
            "van_toi_thieu_che_do": max(1, min(cfg.AF_MODE_MIN, cfg.AF_MODE_WINDOW)),
            "nguong_be_che_do": cfg.AF_MODE_BELOW,
            "be_final_af": cfg.AF_FLIP_FINAL,                          # bẻ final của AF ở MỌI chế độ
            "be_final_cao_thap": cfg.AF_FLIP_FINAL_CT,                 # công tắc GỘP: bẻ final cả CAO lẫn THẤP (ALL giữ nguyên)
            "be_final_cao": cfg.AF_FLIP_FINAL_CAO,                     # CHỈ bẻ final khi chế độ CAO (THẤP / ALL giữ nguyên)
            "be_final_thap": cfg.AF_FLIP_FINAL_THAP,                   # CHỈ bẻ final khi chế độ THẤP (CAO / ALL giữ nguyên)
            "be_final_all": cfg.AF_FLIP_FINAL_ALL,                     # CHỈ bẻ final khi chế độ ALL (CAO / THẤP giữ nguyên)
        },
        "trong_so_wr": {                                          # cơ chế WR có trọng số (cách cũ / dự phòng)
            "so_van": dec["n"],
            "trong_so": dec["weights"],                           # cũ nhất -> mới nhất (đã tính flip nếu bật)
            "flip_trong_so": dec["flip"],                         # True = ván CŨ nhất nặng nhất -> giảm dần tới ván MỚI nhất
            "van_moi_nhat": cfg.WR_WEIGHT_NEWEST,                     # trọng số CAO NHẤT (WR_WEIGHT_NEWEST; gán cho ván mới nhất, hoặc ván cũ nhất nếu flip)
            "he_so_giam": cfg.WR_DECAY,                               # WR_DECAY: tốc độ quên ván cũ
            "san_trong_so": cfg.WR_FLOOR,                             # WR_FLOOR: sàn trọng số ván cũ
        },
        "logic": [
            {"ten": SUN_NAMES[i], "du_doan": votes[i],
             "wr": (round(dec["wins"][i] / dec["wsum"] * 100, 1) if dec["wins"] else None),       # WR có trọng số (cách cũ)
             "nhom": (None if not dec["wins"] else ("THAP" if i in dec["low"] else "CAO")),
             "af_be": (af["flips"][i] if used_af else None),                                         # LOW | HIGH | None: logic có bị bẻ ở bước 1 của AF không
             "af_du_doan": (af["preds"][i] if used_af else None),                                    # phiếu SAU khi bẻ logic
             "af_wr": (round(af["eff"][i], 1) if used_af and af["eff"][i] is not None else None),    # WR dùng (100 − WR gốc nếu bị bẻ)
             "af_nhom": (af["group"][i] if used_af else None),                                       # CAO | THAP | None
             "af_vote": ((i in af["pool"]) if used_af else None)}                                    # True = logic THAM GIA vote ván này (nằm trong nhóm / pool được chọn)
            for i in range(len(votes))
        ],
        "final_goc": final,                                       # final trước khi bẻ chung (của AF nếu AF chốt (đã gồm bẻ logic + bẻ chế độ) · không thì của cách cũ)
        "tool_dung_sai_15_van": _recent_accuracy(graded, cfg.WR_WINDOW, cfg=cfg),
    }
    hist_rows = [{"phien": g["session"], "du_doan": out_final_g(g, cfg), "ket_qua": g["actual"], "tong": g.get("total"),
                  "dung": out_final_g(g, cfg) == g["actual"],
                  "af": g.get("af", False), "che_do": g.get("mode"), "be_che_do": g.get("mflip", False),
                  "be_final": be_final_g(g, cfg)} for g in reversed(graded[-HIST_MAX:])]   # mới -> cũ
    return {"base": base, "detail": detail, "hist": hist_rows}


def _recent_accuracy(graded, size, with_chuoi=False, cfg=SUN):
    """Đúng/sai của final ĐÃ ĐƯA RA API (sau bẻ nếu đang bật) ở `size` ván gần nhất."""
    win = graded[-size:]
    oks = [out_final_g(g, cfg) == g["actual"] for g in win]
    out = {"dung": sum(oks), "tong": len(win)}
    if with_chuoi:
        out = {"dung": out["dung"], "sai": len(win) - out["dung"], "tong": len(win),
               "chuoi": "".join(ICON_DUNG if ok else ICON_SAI for ok in reversed(oks))}     # mới -> cũ
    return out


# ─── TRẠNG THÁI NỀN + QUÉT UPSTREAM ──────────────────────────────────────
_state = {"result": None, "latest": None, "error": None, "updated": None, "checked": None, "polls": 0}
_state_lock = threading.Lock()
_refresh_lock = threading.Lock()
_poller_started = False


def _fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; SUNVIW-API/1.0)",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
    })
    with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def refresh():
    """Lấy upstream; chỉ tính lại khi có phiên mới. Ném exception nếu lỗi (poller sẽ ghi lại)."""
    with _refresh_lock:
        recs = parse_history(_fetch_json(UPSTREAM_URL))
        if not recs:
            raise ValueError("upstream khong co phien hop le (can phien + xuc_xac_1..3)")
        hist = hist_update(recs)                      # upstream chỉ trả 1 phiên mới nhất -> gộp vào lịch sử tích lũy
        latest = hist[-1]["phien"]
        with _state_lock:
            same = _state["result"] is not None and _state["latest"] == latest
        if same:
            with _state_lock:
                _state["error"] = None
                _state["checked"] = _now()
            return
        res = build_result(hist)
        with _state_lock:
            _state.update(result=res, latest=latest, error=None, updated=_now(), checked=_now())


def _poll_loop():
    while True:
        try:
            refresh()
        except Exception as e:  # noqa: BLE001 - giữ poller sống dù upstream lỗi
            with _state_lock:
                _state["error"] = f"{type(e).__name__}: {e}"
                _state["checked"] = _now()
        with _state_lock:
            _state["polls"] += 1
        time.sleep(POLL_SEC)


def ensure_poller():
    global _poller_started
    if _poller_started:
        return
    _poller_started = True
    threading.Thread(target=_poll_loop, daemon=True, name="sunviw-poller").start()
    hit_ensure_pollers()                          # HITCLUB: bật poller 2 bàn (TX thường + TX MD5)
    _ab_boot = globals().get("ab_boot")           # AUTO CƯỢC LC79: nạp phiên đã lưu (khối định nghĩa ở gần cuối file)
    if _ab_boot:
        _ab_boot()


def _acc_rows(rows, n=10):
    w = rows[:n]
    dung = sum(1 for r in w if r["dung"])
    return {"dung": dung, "sai": len(w) - dung, "tong": len(w),
            "chuoi": "".join(ICON_DUNG if r["dung"] else ICON_SAI for r in w)}      # mới -> cũ


# ─── HITCLUB (GAME 3): 2 BÀN · HTTP POLLING · MỖI BÀN MỘT FILE DATA RIÊNG ───
# Port từ hittxthuong.js / hittxmd5.js. Mỗi bàn = 1 HitTable: poller riêng + config riêng (xem CONFIG HITCLUB) + file riêng (hit15_txthuong.json / hit15_txmd5.json
# chứa lịch sử xúc xắc + các ván đã chấm). Dự đoán dùng bộ 13 logic SEQ13v6 / AF / WR của SUN qua build_result(hist, cfg, persist).
def _hit_fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": HIT_UA, "Accept": "application/json", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def _hit_rec(sid, d1, d2, d3):
    """1 phiên hợp lệ (xúc xắc 1..6) -> record như hist của SUN; không hợp lệ -> None. Tổng >= 11 = Tài (như file JS)."""
    p = _parse_int(sid)
    ds = [_parse_int(x) for x in (d1, d2, d3)]
    if p is None or None in ds or any(d < 1 or d > 6 for d in ds):
        return None
    tot = sum(ds)
    return {"phien": p, "d1": ds[0], "d2": ds[1], "d3": ds[2], "total": tot, "actual": actual_of(tot), "time": _now()}


def _hit_cmd(g):
    return _parse_int(g.get("cmd")) if isinstance(g, dict) else None


def _hit_parse_md5(tb, data):
    """TX MD5 (gid vgmn_101): mục cmd 2006 có sid + d1 d2 d3. Lấy MỌI mục hợp lệ trong payload (bản JS chỉ giữ mục cuối)."""
    out = {}
    for g in data:
        if _hit_cmd(g) == 2006:
            r = _hit_rec(g.get("sid"), g.get("d1"), g.get("d2"), g.get("d3"))
            if r:
                out[r["phien"]] = r
    return list(out.values())


def _hit_parse_thuong(tb, data):
    """TX THƯỜNG (gid vgmn_100): cmd 1008 nhả sid (nhớ lại qua các lần quét) · cmd 1003 nhả xúc xắc -> ghép sid + xúc xắc. Mỗi sid chỉ ghi 1 lần (y như file JS)."""
    for g in data:
        if _hit_cmd(g) == 1008 and g.get("sid"):
            p = _parse_int(g["sid"])
            if p is not None:
                tb.pending_sid = p
    out = {}
    for g in data:
        if _hit_cmd(g) == 1003 and g.get("d1") is not None and tb.pending_sid is not None:
            sid = tb.pending_sid
            if sid != tb.last_sid and sid not in tb.hist and sid not in out:
                r = _hit_rec(sid, g.get("d1"), g.get("d2"), g.get("d3"))
                if r:
                    out[sid] = r
                    tb.last_sid = sid
    return list(out.values())


class HitTable:
    """1 bàn HitClub: quét API nền, tích lũy lịch sử, tính dự đoán bằng config RIÊNG (self.cfg), lưu data vào file RIÊNG (self.path)."""

    def __init__(self, key, label, cfg, path, parser):
        self.key, self.label, self.cfg, self.path, self.parse = key, label, cfg, path, parser
        self.url = HIT_API_URL.replace("{GID}", cfg.GID)
        self.rlock = threading.RLock()                 # tuần tự hoá refresh()
        self.slock = threading.Lock()                  # bảo vệ self.state (giữ ngắn)
        self.state = {"result": None, "latest": None, "error": None, "updated": None, "checked": None, "polls": 0}
        self.hist = {}                                 # phien -> record xúc xắc
        self.graded = []                               # các ván đã chấm (cũ -> mới)
        self.loaded = False
        self.pending_sid = None                        # TX THƯỜNG: sid mới nhất từ cmd 1008
        self.last_sid = None
        self.started = False
        self.dbg = {}                                  # tóm tắt payload quét gần nhất (để /health chẩn đoán)

    game = "hitclub"            # giá trị trường "game" trong JSON
    kgame = "hit"               # game của KEY được phép dùng bàn này
    pending = None              # dự đoán đang chờ kết quả: {"phien": n, "du_doan": "TÀI"|"XỈU"}

    def _fetch_items(self):
        data = _hit_fetch_json(self.url)
        if not isinstance(data, dict) or data.get("status") != "OK" or not isinstance(data.get("data"), list):
            raise ValueError("API Hit tra ve khong hop le (status != OK hoac thieu data)")
        return data["data"]

    @property
    def active(self):
        return bool(HIT_ENABLED and self.cfg.ENABLED)

    # ── file data riêng của bàn ──
    def _load(self):
        if self.loaded:
            return
        self.loaded = True
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:  # noqa: BLE001
            return
        if not isinstance(d, dict):
            return
        for r in d.get("hist") or []:
            if isinstance(r, dict) and all(k in r for k in ("phien", "d1", "d2", "d3", "total", "actual")):
                self.hist[r["phien"]] = r
        for k in sorted(self.hist)[:-self.cfg.HIST_KEEP]:
            del self.hist[k]
        self.graded = [g for g in (d.get("graded") or []) if isinstance(g, dict) and g.get("sig") == SUN_SIG]   # bỏ ván của bộ logic khác
        if self.hist:
            self.last_sid = max(self.hist)
        pd = d.get("pending")
        if isinstance(pd, dict) and isinstance(pd.get("phien"), int):
            self.pending = pd

    def _write(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"ban": self.key, "gid": self.cfg.GID, "luu_luc": _now(),
                           "pending": self.pending,
                           "hist": [self.hist[k] for k in sorted(self.hist)],
                           "graded": self.graded[-self.cfg.PERSIST_KEEP:]}, f, ensure_ascii=False)
            os.replace(tmp, self.path)
        except Exception:  # noqa: BLE001
            pass

    def _graded_load(self):
        return list(self.graded)

    def _graded_save(self, graded):
        self.graded = list(graded[-self.cfg.PERSIST_KEEP:])      # ghi file 1 lần sau build_result (_write), không ghi ở đây

    # ── quét API + tính lại khi có phiên mới ──
    def refresh(self):
        with self.rlock:
            self._load()
            items = self._fetch_items()
            cmds = {}
            for g in items:
                c = _hit_cmd(g)
                if c is not None:
                    cmds[c] = cmds.get(c, 0) + 1
            self.dbg = {"so_muc": len(items), "cmd": cmds, "pending_sid": self.pending_sid}
            recs = self.parse(self, items)
            new = [r for r in recs if r["phien"] not in self.hist]
            for r in new:
                self.hist[r["phien"]] = r
            for k in sorted(self.hist)[:-self.cfg.HIST_KEEP]:
                del self.hist[k]
            if not self.hist:                           # API trả hợp lệ nhưng chưa có kết quả phiên nào
                with self.slock:
                    self.state.update(error=None, checked=_now())
                return
            hist = [self.hist[k] for k in sorted(self.hist)]
            latest = hist[-1]["phien"]
            with self.slock:
                same = self.state["result"] is not None and self.state["latest"] == latest
            if same:
                if new:                                 # chỉ lấp phiên cũ còn thiếu -> lưu lại, không tính lại
                    self._write()
                with self.slock:
                    self.state.update(error=None, checked=_now())
                return
            res = build_result(hist, self.cfg, (self._graded_load, self._graded_save))
            self.pending = {"phien": res["base"]["phien"], "du_doan": res["base"]["du_doan"]}   # dự đoán phiên kế tiếp, giữ tới khi API trả kết quả phiên đó
            self._write()                               # 1 lần ghi: lịch sử xúc xắc + ván đã chấm + dự đoán đang chờ
            with self.slock:
                self.state.update(result=res, latest=latest, error=None, updated=_now(), checked=_now())

    def wipe(self):
        """XÓA SẠCH data của bàn này (lịch sử xúc xắc + ván đã chấm + dự đoán chờ) rồi ghi file rỗng. Poller quét lại API và tích lũy lại từ đầu."""
        with self.rlock:
            self._load()
            n = len(self.hist)
            self.hist.clear()
            self.graded = []
            self.pending = None
            self.last_sid = None
            self._write()
            hist_unhide(self.key)
            with self.slock:
                self.state.update(result=None, latest=None)
            return {"phien_da_xoa": n}

    def regrade(self):
        """Nút \"Tính lại theo config\": chấm lại các ván đã lưu của bàn này bằng config HIỆN TẠI (giữ nguyên lịch sử xúc xắc + ván đã chấm)."""
        with self.rlock:
            self._load()
            if not self.graded:
                return {"so_van": 0, "doi_du_doan": 0, "truoc": {"dung": 0, "tong": 0}, "sau": {"dung": 0, "tong": 0}}
            before = list(self.graded)
            self.graded = regrade_graded(before, self.cfg)[-self.cfg.PERSIST_KEEP:]
            rep = _regrade_report(before, self.graded, self.cfg)
            hist = [self.hist[k] for k in sorted(self.hist)]
            if hist:
                res = build_result(hist, self.cfg, (self._graded_load, self._graded_save))
                self.pending = {"phien": res["base"]["phien"], "du_doan": res["base"]["du_doan"]}
                with self.slock:
                    self.state.update(result=res, latest=hist[-1]["phien"], updated=_now())
            self._write()
            return rep

    def _loop(self):
        while True:
            try:
                self.refresh()
            except Exception as e:  # noqa: BLE001 - giữ poller sống dù API lỗi
                with self.slock:
                    self.state["error"] = f"{type(e).__name__}: {e}"
                    self.state["checked"] = _now()
            with self.slock:
                self.state["polls"] += 1
            time.sleep(self.cfg.POLL_SEC)

    def start(self):
        with self.slock:
            if self.started or not self.active:
                return
            self.started = True
        threading.Thread(target=self._loop, daemon=True, name=f"hit-{self.key}").start()

    def health(self):
        with self.slock:
            st = {k: self.state[k] for k in ("latest", "error", "updated", "checked", "polls")}
        c = self.cfg
        st.update(ok=st["error"] is None and st["latest"] is not None, bat=self.active, ten=self.label, gid=c.GID, file=self.path,
                  so_phien_luu=len(self.hist), so_van_cham=len(self.graded), poll_sec=c.POLL_SEC, hist_keep=c.HIST_KEEP,
                  an_den_phien=hist_hidden_upto(self.key), payload_cuoi=self.dbg, du_doan_cho_ket_qua=self.pending, config=c.as_dict())
        return st



def _lc_parse(tb, data):
    """LC MD5 + LC HŨ (nguồn tele68): {"list":[{id, resultTruyenThong, dices:[a,b,c], point}, ...]} (phiên đầu = mới nhất). Lấy MỌI phiên hợp lệ; HitTable.refresh chỉ lưu thêm phiên CHƯA có."""
    out = {}
    for g in data:
        if not isinstance(g, dict):
            continue
        d = g.get("dices")
        if not isinstance(d, (list, tuple)) or len(d) != 3:
            continue
        r = _hit_rec(g.get("id"), d[0], d[1], d[2])
        if r:
            out[r["phien"]] = r
    return list(out.values())


class LcTable(HitTable):
    """Bàn LC (LC MD5 + LC HŨ): cùng cơ chế HitTable (poller riêng · config riêng · file riêng), chỉ khác cách đọc API (list nhiều phiên) và URL nguồn riêng của từng bàn."""
    game = "lc79"
    kgame = "lc79"              # key game LC79 dùng được cả 2 bàn LC

    def __init__(self, key, label, cfg, path, parser, url):
        super().__init__(key, label, cfg, path, parser)
        self.url = url

    @property
    def active(self):
        return bool(LC_ENABLED and self.cfg.ENABLED)

    def _fetch_items(self):
        h = {"User-Agent": HIT_UA, "Accept": "application/json", "Cache-Control": "no-cache"}
        if LC_REFERER:
            h["Referer"] = LC_REFERER
            h["Origin"] = LC_REFERER.rstrip("/")
        req = urllib.request.Request(self.url, headers=h)
        with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
        lst = data.get("list") if isinstance(data, dict) else data
        if not isinstance(lst, list):
            raise ValueError(f"API LC ({self.key}) tra ve khong hop le (thieu 'list') - kiem tra token at= trong URL nguon cua ban nay")
        return lst


HIT_TABLES = {
    "hittxthuong": HitTable("hittxthuong", "TX Thường", HIT_TXTHUONG_CFG, HIT_TXTHUONG_PATH, _hit_parse_thuong),
    "hittxmd5": HitTable("hittxmd5", "TX MD5", HIT_TXMD5_CFG, HIT_TXMD5_PATH, _hit_parse_md5),
    "lcmd5": LcTable("lcmd5", "LC MD5", LC_MD5_CFG, LC_MD5_PATH, _lc_parse, LC_MD5_API_URL),
    "lchu": LcTable("lchu", "LC Hũ", LC_HU_CFG, LC_HU_PATH, _lc_parse, LC_HU_API_URL),
}


def hit_ensure_pollers():
    for tb in HIT_TABLES.values():
        tb.start()


# ─── XÓA LỊCH SỬ DỰ ĐOÁN (chỉ ẩn phần hiển thị — xem khối CONFIG XÓA LỊCH SỬ) ───
_hc_lock = threading.Lock()
_hc = {"loaded": False, "d": {"sun": {"den": 0, "luc": None},
                              "hittxthuong": {"den": 0, "luc": None}, "hittxmd5": {"den": 0, "luc": None},
                              "lcmd5": {"den": 0, "luc": None}, "lchu": {"den": 0, "luc": None}}}


def _hc_load_locked():
    """Nạp mốc đã lưu (1 lần). Gọi trong _hc_lock."""
    if _hc["loaded"]:
        return
    _hc["loaded"] = True
    try:
        with open(HIST_CLEAR_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for g in list(_hc["d"]):
            r = data.get(g) if isinstance(data, dict) else None
            if r is None and g == "lcmd5" and isinstance(data, dict):
                r = data.get("tele68txmd5")                      # mốc cũ của bàn Tele68 MD5 (đã đổi tên thành LC MD5)
            if isinstance(r, dict) and isinstance(r.get("den"), int) and r["den"] > 0:
                _hc["d"][g] = {"den": r["den"], "luc": r.get("luc")}
    except Exception:  # noqa: BLE001
        pass


def hist_hidden_upto(game):
    """Mốc phiên: ván có phiên <= mốc bị ẩn khỏi lịch sử hiển thị (0 = chưa xóa lần nào)."""
    with _hc_lock:
        _hc_load_locked()
        return _hc["d"][game]["den"]


def hist_clear(game, upto):
    """Đặt mốc xóa lịch sử của `game` = `upto` (chỉ tiến, không lùi). Chỉ ghi file mốc riêng — KHÔNG đụng dữ liệu nào khác. Trả mốc mới."""
    with _hc_lock:
        _hc_load_locked()
        cur = _hc["d"][game]
        if upto > cur["den"]:
            cur["den"] = int(upto)
            cur["luc"] = _now()
        try:
            tmp = HIST_CLEAR_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(_hc["d"], f, ensure_ascii=False)
            os.replace(tmp, HIST_CLEAR_PATH)
        except Exception:  # noqa: BLE001
            pass
        return cur["den"]


def hist_unhide(game):
    """Đặt lại mốc \"Xóa lịch sử\" của `game` về 0 (dùng khi XÓA SẠCH data của game để đếm lại từ đầu)."""
    with _hc_lock:
        _hc_load_locked()
        _hc["d"][game] = {"den": 0, "luc": None}
        try:
            tmp = HIST_CLEAR_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(_hc["d"], f, ensure_ascii=False)
            os.replace(tmp, HIST_CLEAR_PATH)
        except Exception:  # noqa: BLE001
            pass


def sun_wipe():
    """XÓA SẠCH data của SUN: lịch sử xúc xắc + các ván đã chấm + kết quả đang giữ. Tool tự quét lại từ upstream và tích lũy lại từ đầu."""
    global _hist_loaded
    with _refresh_lock:
        n = len(_hist_store)
        _hist_store.clear()
        _hist_loaded = True                                # không nạp lại file cũ
        for path in (HIST_PATH, PERSIST_PATH):
            try:
                os.remove(path)
            except OSError:
                pass
        hist_unhide("sun")
        with _state_lock:
            _state.update(result=None, latest=None)
        return {"phien_da_xoa": n}


# ─── PANEL HTML (/api/html) ──────────────────────────────────────────────
HWID_JS = r"""
function _hw128(s){let a=1779033703,b=3144134277,c=1013904242,d=2773480762;for(let i=0,k;i<s.length;i++){k=s.charCodeAt(i);a=b^Math.imul(a^k,597399067);b=c^Math.imul(b^k,2869860233);c=d^Math.imul(c^k,951274213);d=a^Math.imul(d^k,2716044179)}
  a=Math.imul(c^(a>>>18),597399067);b=Math.imul(d^(b>>>19),2869860233);c=Math.imul(a^(c>>>17),951274213);d=Math.imul(b^(d>>>19),2716044179);a^=(b^c^d);b^=a;c^=a;d^=a;
  return[a,b,c,d].map(x=>(x>>>0).toString(16).padStart(8,'0')).join('')}
/* HWID = mã thiết bị, KHÔNG liên quan IP / mạng. Cách làm (đổi Wi-Fi <-> 4G <-> VPN không đổi mã):
   1) Mã đã lưu (localStorage + cookie dự phòng, lưu 2 năm; mất 1 trong 2 thì tự phục hồi từ cái còn lại) được dùng TRƯỚC.
   2) Chưa có mã -> tính từ dấu vân tay PHẦN CỨNG ổn định (bỏ UA / ngôn ngữ / múi giờ / zoom / xoay màn hình / canvas là các thứ hay đổi) -> cùng máy xoá dữ liệu trình duyệt vẫn ra đúng mã cũ.
   3) HWID_ALT = mã phụ của CHÍNH máy này để server nhận ra máy khi công thức / bộ nhớ thay đổi: bình thường là mã phần cứng ổn định; máy vừa mất bộ nhớ (HWID_FRESH) thì là mã theo công thức cũ. */
const HWID_ALT=[];
let HWID_FRESH=false;
const HWID=(function(){
  const RX=/^[0-9a-f]{32}$/,n=navigator,s=screen;
  const rdLS=()=>{try{return localStorage.getItem('hwid')||''}catch(e){return ''}};
  const rdCK=()=>{try{const m=document.cookie.match(/(?:^|;\s*)hwid=([0-9a-f]{32})(?:;|$)/);return m?m[1]:''}catch(e){return ''}};
  const save=h=>{
    try{localStorage.setItem('hwid',h)}catch(e){}
    try{document.cookie='hwid='+h+'; max-age=63072000; path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':'')}catch(e){}};
  let gpu='';
  try{const g=document.createElement('canvas').getContext('webgl');if(g){const x=g.getExtension('WEBGL_debug_renderer_info');gpu=String(x?g.getParameter(x.UNMASKED_VENDOR_WEBGL)+'|'+g.getParameter(x.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER))}}catch(e){}
  let stable='';
  try{const sp=[n.platform,n.hardwareConcurrency,n.deviceMemory,n.maxTouchPoints,Math.max(s.width,s.height)+'x'+Math.min(s.width,s.height),s.colorDepth,gpu];
    if(sp.join('').length>=12)stable=_hw128('v2||'+sp.join('||'))}catch(e){}
  let legacy='';
  try{const p=[];
    try{p.push(n.userAgent,n.platform,n.hardwareConcurrency,n.deviceMemory,n.language,n.maxTouchPoints,s.width+'x'+s.height,s.colorDepth,devicePixelRatio,Intl.DateTimeFormat().resolvedOptions().timeZone)}catch(e){}
    if(gpu)p.push(gpu);
    try{const cv=document.createElement('canvas');cv.width=220;cv.height=40;const x=cv.getContext('2d');x.textBaseline='top';x.font='14px Arial';x.fillStyle='#f60';x.fillRect(100,1,60,20);x.fillStyle='#069';x.fillText('SUNVIW hwid Cwm fjord',2,10);p.push(cv.toDataURL())}catch(e){}
    if(p.join('').length>=40)legacy=_hw128(p.join('||'))}catch(e){}
  let id=rdLS();if(!RX.test(id))id=rdCK();if(!RX.test(id))id='';
  HWID_FRESH=!id;
  if(!id)id=stable||legacy||_hw128('r'+Math.random()+Date.now()+String(n.userAgent||''));
  save(id);
  const alt=HWID_FRESH?legacy:stable;
  if(alt&&alt!==id)HWID_ALT.push(alt);
  return id})();
const HWID_HDR=Object.assign({'X-HWID':HWID},HWID_ALT.length?{'X-HWID-ALT':HWID_ALT.join(',')}:{},HWID_FRESH?{'X-HWID-FRESH':'1'}:{});
""".strip()


PANEL_HTML = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>SUNVIW · Radar Tài Xỉu</title>
<meta name="theme-color" content="#07080d">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;800&display=swap" media="print" onload="this.media='all'">
<style>
/* Font tải NỀN (media=print → all): lỗi mạng / bị chặn Google Fonts cũng KHÔNG làm trắng trang như bản cũ. */
:root{
  --bg:#07080d;--s1:#0e1018;--s2:#151824;--s3:#1c2030;--ln:rgba(255,255,255,.075);--ln2:rgba(255,255,255,.15);
  --tx:#f3f5fa;--mu:#8d94ab;--mu2:#5d647d;
  --tai:#ff6a3d;--tai2:#ffb02e;--xiu:#2f86ff;--xiu2:#1fe0ff;
  --ok:#34e3a0;--no:#ff4f6d;--warn:#ffc53d;--lime:#c6ff3d;--cao:#c4a3ff;--thap:#ffa45c;
  --r:22px;color-scheme:dark;
  --f:"Lexend","Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,Roboto,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Consolas,Menlo,monospace}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{background:var(--bg);scrollbar-color:#2b3046 transparent}
body{margin:0;min-height:100vh;color:var(--tx);font:400 14px/1.5 var(--f);font-variant-numeric:tabular-nums;overflow-x:hidden}
button{font:inherit;color:inherit;cursor:pointer}
input{font:inherit;color:inherit}
[hidden]{display:none!important}
::selection{background:rgba(198,255,61,.3)}
b,strong{font-weight:700}
.mu{color:var(--mu)}.tai{color:#ff9467}.xiu{color:#6cbcff}.okc{color:var(--ok)}.noc{color:var(--no)}

/* ── nền phát sáng theo dự đoán ── */
.amb{position:fixed;inset:0;z-index:-1;pointer-events:none;background:var(--bg);overflow:hidden}
.amb i{position:absolute;inset:0;opacity:0;transition:opacity .9s ease}
.amb .n{opacity:1;background:radial-gradient(900px 520px at 12% -12%,rgba(198,255,61,.08),transparent 62%)}
.amb .t{background:radial-gradient(860px 540px at 72% -10%,rgba(255,106,61,.24),transparent 62%),radial-gradient(640px 420px at -4% 104%,rgba(255,176,46,.10),transparent 62%)}
.amb .x{background:radial-gradient(860px 540px at 72% -10%,rgba(47,134,255,.26),transparent 62%),radial-gradient(640px 420px at -4% 104%,rgba(31,224,255,.10),transparent 62%)}
body.ft .amb .t{opacity:1}body.fx .amb .x{opacity:1}
.amb:after{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px);background-size:46px 46px;-webkit-mask-image:radial-gradient(ellipse at 50% 0,#000,transparent 72%);mask-image:radial-gradient(ellipse at 50% 0,#000,transparent 72%)}

/* ── khung ── */
.app{display:grid;grid-template-columns:276px minmax(0,1fr);gap:30px;max-width:1300px;margin:0 auto;padding:24px 24px 48px}
.side{position:sticky;top:24px;align-self:start;display:flex;flex-direction:column;gap:18px;max-height:calc(100vh - 48px)}
.brand{display:flex;align-items:center;gap:13px}
.logo{width:48px;height:48px;flex:none;filter:drop-shadow(0 10px 22px rgba(150,255,60,.32))}
.bn b{display:block;font:800 22px/1.05 var(--f);letter-spacing:.05em}
.bn span{font-size:10.5px;color:var(--mu);letter-spacing:.2em;text-transform:uppercase}
.live{display:flex;align-items:center;gap:9px;padding:10px 14px;border-radius:15px;background:var(--s1);border:1px solid var(--ln);font-size:12.5px;color:var(--mu);white-space:nowrap}
.live i{width:8px;height:8px;border-radius:50%;background:var(--ok);flex:none;animation:ping 1.9s infinite}
.live.bad i{background:var(--no);animation:none}.live.idle i{background:var(--warn);animation:none}
.live em{margin-left:auto;font-style:normal;font-weight:800;color:var(--no);font-size:10.5px;letter-spacing:.08em;padding:2px 7px;border-radius:99px;background:rgba(255,79,109,.14)}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(52,227,160,.55)}70%,100%{box-shadow:0 0 0 9px rgba(52,227,160,0)}}
.navh{font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--mu2);margin:2px 10px -6px}
.nav{display:flex;flex-direction:column;gap:6px}
.ni{display:flex;align-items:center;gap:12px;width:100%;padding:10px 12px;border:1px solid transparent;border-radius:17px;background:transparent;text-align:left;transition:background .15s,border-color .15s}
.ni:hover{background:rgba(255,255,255,.045)}
.ni.on{background:var(--s2);border-color:var(--ln2);box-shadow:inset 3px 0 0 var(--gc),0 14px 30px -18px #000}
.ni-ic{width:40px;height:40px;border-radius:13px;display:grid;place-items:center;font:800 12.5px var(--f);letter-spacing:.04em;color:var(--gc);background:rgba(255,255,255,.05);box-shadow:inset 0 0 0 1px rgba(255,255,255,.06);flex:none;transition:background .2s,color .2s}
.ni.on .ni-ic{background:var(--gc);color:#0b0d12}
.ni-t{flex:1;min-width:0;line-height:1.25}.ni-t b{display:block;font-weight:600;font-size:14px}.ni-t small{color:var(--mu);font-size:11.5px}
.pp{font:800 11px var(--f);letter-spacing:.06em;padding:4px 10px;border-radius:99px;flex:none;min-width:38px;text-align:center}
.pp.tai{color:#ffb28b;background:rgba(255,106,61,.15);box-shadow:inset 0 0 0 1px rgba(255,106,61,.35)}
.pp.xiu{color:#9bd6ff;background:rgba(47,134,255,.17);box-shadow:inset 0 0 0 1px rgba(47,134,255,.42)}
.pp.no{color:var(--mu2);background:rgba(255,255,255,.05)}
.sfoot{margin-top:auto;font-size:11.5px;color:var(--mu2);line-height:1.7;padding:0 10px}
.sfoot b{color:var(--mu);font:600 11.5px var(--mono)}
.main{min-width:0}
#banner{display:flex;flex-direction:column;gap:8px;margin-bottom:14px}
#banner:empty{display:none}
.bnr{display:flex;gap:11px;align-items:flex-start;padding:12px 16px;border-radius:16px;font-size:13px;border:1px solid var(--ln2);background:var(--s1)}
.bnr.bad{background:rgba(255,79,109,.1);border-color:rgba(255,79,109,.4);color:#ffc0cb}
.bnr.warn{background:rgba(255,197,61,.09);border-color:rgba(255,197,61,.35);color:#ffe1a1}
.bnr button{margin-left:auto;flex:none;border:1px solid currentColor;background:none;border-radius:10px;padding:3px 12px;font-size:12px;color:inherit}

/* ── thẻ ── */
.card{background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.015));border:1px solid var(--ln);border-radius:var(--r);box-shadow:0 26px 60px -34px #000}
.pill{display:inline-flex;align-items:center;justify-content:center;min-width:56px;padding:3px 13px;border-radius:99px;font-weight:700;font-size:12.5px;letter-spacing:.05em;white-space:nowrap}
.pill.tai{color:#ffb28b;background:rgba(255,106,61,.15);box-shadow:inset 0 0 0 1px rgba(255,106,61,.38)}
.pill.xiu{color:#9bd6ff;background:rgba(47,134,255,.17);box-shadow:inset 0 0 0 1px rgba(47,134,255,.45)}
.bd{display:inline-flex;align-items:center;gap:5px;padding:2px 10px;border-radius:99px;font-size:11.5px;font-weight:600;color:var(--mu);background:rgba(255,255,255,.05);box-shadow:inset 0 0 0 1px var(--ln2);white-space:nowrap}
.bd:before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.bd.ALL{color:#dfe3f1}.bd.CAO{color:var(--cao);background:rgba(196,163,255,.12);box-shadow:inset 0 0 0 1px rgba(196,163,255,.4)}
.bd.THAP{color:var(--thap);background:rgba(255,164,92,.12);box-shadow:inset 0 0 0 1px rgba(255,164,92,.4)}
.bd.flip{color:var(--no);background:rgba(255,79,109,.12);box-shadow:inset 0 0 0 1px rgba(255,79,109,.4)}
.bd.off{opacity:.55}.bd.live2{color:var(--lime);background:rgba(198,255,61,.1);box-shadow:inset 0 0 0 1px rgba(198,255,61,.35)}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.note{font-size:12.5px;color:var(--mu);line-height:1.55}

/* ── sân khấu dự đoán ── */
.stage{display:grid;grid-template-columns:auto minmax(0,1fr) 240px;gap:30px;align-items:center;padding:28px 30px;position:relative;overflow:hidden}
.stage:before{content:"";position:absolute;inset:0;background:radial-gradient(560px 320px at 16% 50%,var(--glow,rgba(198,255,61,.05)),transparent 70%);pointer-events:none}
.stage.t{--c1:#ff4a36;--c2:#ffb52e;--glow:rgba(255,106,61,.22)}
.stage.x{--c1:#1d63ff;--c2:#1fe0ff;--glow:rgba(47,134,255,.24)}
.stage>*{position:relative}
.orb{position:relative;width:216px;height:216px;border-radius:50%;display:grid;place-items:center;flex:none;isolation:isolate}
.orb:before{content:"";position:absolute;inset:-9px;border-radius:50%;z-index:-1;background:conic-gradient(from 0deg,var(--c1,#555),transparent 28%,var(--c2,#888) 52%,transparent 78%,var(--c1,#555));animation:spin 7s linear infinite;-webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 4px),#000 calc(100% - 3px));mask:radial-gradient(farthest-side,transparent calc(100% - 4px),#000 calc(100% - 3px))}
.orb:after{content:"";position:absolute;inset:-34px;border-radius:50%;z-index:-2;background:radial-gradient(circle,var(--glow,transparent),transparent 66%)}
.orb-core{position:absolute;inset:7px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;background:radial-gradient(circle at 32% 24%,var(--c2,#444),var(--c1,#222) 62%);box-shadow:inset 0 -18px 34px rgba(0,0,0,.32),inset 0 12px 24px rgba(255,255,255,.3),0 34px 80px -22px var(--c1,#000)}
.orb-core small{font-size:10.5px;letter-spacing:.3em;text-transform:uppercase;color:rgba(255,255,255,.78);font-weight:600}
.orb-core b{font:800 clamp(40px,5.4vw,56px)/1 var(--f);letter-spacing:.02em;color:#fff;text-shadow:0 5px 26px rgba(0,0,0,.4)}
.orb-core span{font-size:12px;color:rgba(255,255,255,.86);font-weight:500}
.orb.none .orb-core{background:radial-gradient(circle at 32% 24%,#2c3146,#161a28 70%);box-shadow:inset 0 0 0 1px var(--ln2)}
@keyframes spin{to{transform:rotate(360deg)}}
.eyebrow{display:flex;align-items:center;gap:10px;font-size:12.5px;color:var(--mu);margin-bottom:14px;flex-wrap:wrap}
.eyebrow b{color:var(--tx);font-size:15px;letter-spacing:.02em}
.eyebrow .gtag{padding:2px 11px;border-radius:99px;background:rgba(255,255,255,.06);font-weight:600;color:var(--gc,var(--lime));font-size:11.5px}
.conf-h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px}
.conf-h span{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--mu)}
.conf-h b{font:800 30px/1 var(--f);letter-spacing:-.01em}
.bar{position:relative;height:12px;border-radius:99px;background:rgba(255,255,255,.07);overflow:hidden}
.bar i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--c1,#7be83a),var(--c2,#c6ff3d));box-shadow:0 0 18px -2px var(--c1,#7be83a);transition:width .6s cubic-bezier(.2,.8,.2,1)}
.bar:after{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;background:rgba(255,255,255,.28)}
.bar.sm{height:7px}.bar.sm:after{display:none}
.stage .chips{margin-top:14px}
.stage .note{margin-top:10px}
.prev{padding:18px;border-radius:20px;background:rgba(5,6,10,.5);border:1px solid var(--ln);text-align:center}
.prev>small{display:block;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--mu)}
.prev .dice{display:flex;justify-content:center;gap:9px;margin:14px 0 12px}
.die{width:46px;height:46px;filter:drop-shadow(0 8px 10px rgba(0,0,0,.55))}
.prev .sum{font:800 34px/1 var(--f)}.prev .sum small{font-size:12px;color:var(--mu);font-weight:500;margin-right:4px}
.prev .pill{margin-top:10px}

/* ── KPI ── */
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:16px}
.kpi{padding:16px 18px;display:flex;align-items:center;gap:14px;min-width:0}
.kpi .v{font:800 30px/1 var(--f);letter-spacing:-.01em}
.kpi small{display:block;font-size:11.5px;color:var(--mu);margin-top:5px;line-height:1.3}
.ring{position:relative;width:64px;height:64px;border-radius:50%;flex:none;background:conic-gradient(var(--rc,var(--ok)) calc(var(--p,0)*1%),rgba(255,255,255,.09) 0)}
.ring:before{content:"";position:absolute;inset:7px;border-radius:50%;background:#0d0f17}
.ring b{position:absolute;inset:0;display:grid;place-items:center;font-size:14px}
.kpi .ic{width:46px;height:46px;border-radius:15px;display:grid;place-items:center;font-size:20px;flex:none}
.ic.g{background:rgba(52,227,160,.13);color:var(--ok)}.ic.r{background:rgba(255,79,109,.13);color:var(--no)}.ic.f{background:rgba(255,197,61,.13);color:var(--warn)}

/* ── dòng ván ── */
.road{margin-top:16px;padding:18px 20px;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:26px;align-items:center}
.road h3,.sec h3{margin:0 0 12px;font:600 12px var(--f);letter-spacing:.16em;text-transform:uppercase;color:var(--mu);display:flex;justify-content:space-between;gap:10px}
.road h3 span,.sec h3 span{letter-spacing:.02em;text-transform:none;font-weight:400}
.beads{display:flex;flex-wrap:wrap;gap:6px}
.bead{width:25px;height:25px;border-radius:50%;display:grid;place-items:center;font-size:12px;font-weight:800;color:#04140d;transition:transform .12s}
.bead:hover{transform:scale(1.25)}
.bead.ok{background:linear-gradient(180deg,#6af0bf,var(--ok))}.bead.no{background:linear-gradient(180deg,#ff8aa0,var(--no));color:#fff}
.bead.m-CAO{box-shadow:0 0 0 2px #0d0f17,0 0 0 3.5px var(--cao)}.bead.m-THAP{box-shadow:0 0 0 2px #0d0f17,0 0 0 3.5px var(--thap)}
.spark{width:100%;height:96px;display:block;overflow:visible}
.spk-s{display:flex;justify-content:space-between;font-size:11.5px;color:var(--mu);margin-top:6px}
.spk-s b{color:var(--tx)}

/* ── tab ngăn ── */
.pbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;margin:22px 0 4px}
.seg{display:inline-flex;gap:2px;padding:4px;border-radius:16px;background:var(--s1);border:1px solid var(--ln)}
.seg button{border:0;background:none;padding:8px 16px;border-radius:12px;color:var(--mu);font-weight:500;font-size:13px;white-space:nowrap;transition:all .15s}
.seg button:hover{color:var(--tx)}
.seg button.on{background:var(--lime);color:#10160a;font-weight:700;box-shadow:0 8px 22px -8px rgba(198,255,61,.65)}
.seg button em{font-style:normal;font-size:11px;margin-left:5px;opacity:.7}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:9px 16px;border-radius:13px;border:1px solid var(--ln2);background:var(--s2);color:var(--tx);font-size:13px;font-weight:500;transition:all .15s}
.btn:hover{border-color:rgba(255,255,255,.34);background:var(--s3)}
.btn:disabled{opacity:.5;cursor:wait}
.btn.pri{background:var(--lime);color:#10160a;border-color:transparent;font-weight:700}.btn.pri:hover{filter:brightness(1.08)}
.btn.dng{color:#ff8da1;border-color:rgba(255,79,109,.42);background:rgba(255,79,109,.06)}.btn.dng:hover{background:rgba(255,79,109,.15)}
.btn.dng.solid{background:var(--no);color:#fff;border-color:transparent}
.btn.sm{padding:6px 12px;font-size:12px;border-radius:11px}
.hbar{display:flex;flex-wrap:wrap;gap:12px 18px;align-items:center;justify-content:space-between;margin:14px 0 12px}
.hbar .grp{display:flex;flex-wrap:wrap;align-items:center;gap:7px}
.hbar label{font-size:12px;color:var(--mu);margin-right:3px}
.hbar input{width:74px;padding:7px 10px;border-radius:11px;border:1px solid var(--ln2);background:var(--s1);outline:0;text-align:center}
.hbar input:focus{border-color:var(--lime);box-shadow:0 0 0 3px rgba(198,255,61,.14)}
.cx{border:1px solid var(--ln2);background:var(--s1);padding:6px 13px;border-radius:99px;font-size:12.5px;color:var(--mu);display:inline-flex;gap:6px;align-items:baseline;transition:all .15s}
.cx:hover{color:var(--tx);border-color:rgba(255,255,255,.34)}
.cx.on{background:rgba(198,255,61,.12);border-color:var(--lime);color:var(--lime);font-weight:600}
.cx b{font-weight:700}.cx.CAO b{color:var(--cao)}.cx.THAP b{color:var(--thap)}.cx.CAO.on,.cx.THAP.on{color:var(--tx)}
.hint{font-size:12px;color:var(--mu2);margin:0 2px 12px}

/* ── lịch sử ── */
.hl{display:flex;flex-direction:column;gap:6px}
.hh,.hr{display:grid;grid-template-columns:104px minmax(0,1fr) minmax(0,1fr) 44px;gap:12px;align-items:center}
.hh{padding:0 16px;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--mu2)}
.hr{padding:10px 16px 10px 18px;border-radius:15px;background:var(--s1);border:1px solid var(--ln);position:relative;overflow:hidden;transition:background .12s}
.hr:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--ok)}
.hr.no:before{background:var(--no)}
.hr:hover{background:var(--s2)}
.hr-id{font:600 13px var(--mono);color:#b8bfd6;line-height:1.3}
.hr-id span{display:flex;flex-wrap:wrap;gap:4px;margin-top:3px}
.hr-id .bd{font:600 10px var(--f);padding:1px 7px}
.hr-r{display:flex;align-items:center;gap:9px;min-width:0}
.hr-r small{color:var(--mu);font-size:12px}
.hr-k{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:15px;justify-self:end}
.hr.ok .hr-k{background:rgba(52,227,160,.15);color:var(--ok)}.hr.no .hr-k{background:rgba(255,79,109,.15);color:var(--no)}
.legend{font-size:12px;color:var(--mu2);margin-top:12px;line-height:1.6}
.empty{padding:34px 20px;text-align:center;color:var(--mu);border:1px dashed var(--ln2);border-radius:18px;background:rgba(255,255,255,.015)}

/* ── logic ── */
.vs{display:flex;gap:4px;height:38px;margin:14px 0}
.vs div{display:flex;align-items:center;padding:0 16px;font-weight:700;font-size:13px;min-width:0;white-space:nowrap;overflow:hidden;transition:flex .5s}
.vs .a{border-radius:14px 6px 6px 14px;background:linear-gradient(90deg,#ff4a36,#ff9a2e);color:#2a0d05}
.vs .b{border-radius:6px 14px 14px 6px;background:linear-gradient(90deg,#1d63ff,#1fe0ff);color:#021326;justify-content:flex-end}
.vs .a:empty,.vs .b:empty{display:none}
.callout{padding:13px 16px;border-radius:16px;background:var(--s1);border:1px solid var(--ln);display:flex;flex-direction:column;gap:5px;margin-bottom:14px}
.callout p{margin:0;font-size:12.5px;color:var(--mu);padding-left:14px;position:relative}
.callout p:before{content:"";position:absolute;left:0;top:.62em;width:6px;height:6px;border-radius:2px;background:var(--lime);transform:rotate(45deg)}
.lg{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:10px}
.lc{padding:14px 15px;border-radius:17px;background:var(--s1);border:1px solid var(--ln);display:flex;flex-direction:column;gap:10px;transition:border-color .15s,transform .15s}
.lc:hover{border-color:var(--ln2);transform:translateY(-2px)}
.lc.out{opacity:.5}
.lc-h{display:flex;justify-content:space-between;align-items:center;gap:8px}
.lc-h b{font-weight:600;font-size:13.5px;min-width:0;overflow:hidden;text-overflow:ellipsis}
.lc-wr{display:flex;align-items:center;gap:10px;font-size:12.5px;font-weight:600}
.lc-wr .bar{flex:1}.lc-wr em{font-style:normal;color:var(--no);margin-left:4px;font-weight:500}
.lc-wr .bar i{background:linear-gradient(90deg,#3d4766,#a9b4d8);box-shadow:none}
.lc-f{display:flex;flex-wrap:wrap;gap:6px;min-height:22px;align-items:center;font-size:11.5px}
.was{text-decoration:line-through;opacity:.75}

/* ── công cụ ── */
.tl-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px;margin-top:14px;padding:16px 18px}
.tl-head h4{margin:0;font-size:15px;font-weight:600}
.tl-head p{margin:4px 0 0;font-size:12.5px;color:var(--mu);line-height:1.55}
.tl-list{display:flex;flex-direction:column;gap:10px;margin-top:12px}
.tl{display:grid;grid-template-columns:48px minmax(0,1fr) auto;gap:16px;align-items:center;padding:16px 18px}
.tl .ti{width:48px;height:48px;border-radius:15px;display:grid;place-items:center;font-size:22px;background:rgba(255,255,255,.06)}
.tl h5{margin:0;font-size:14.5px;font-weight:600;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tl h5 em{font-style:normal;font-size:10.5px;font-weight:700;padding:2px 9px;border-radius:99px;background:rgba(198,255,61,.14);color:var(--lime)}
.tl p{margin:4px 0 0;font-size:12.5px;color:var(--mu);line-height:1.6}
.tl p b{color:var(--tx);font-weight:600}
.tl .btn{min-width:158px;padding:11px 18px;font-size:13.5px}
.tl.rec{border-color:rgba(198,255,61,.34)}
.tl.danger{border-color:rgba(255,79,109,.3);background:linear-gradient(180deg,rgba(255,79,109,.06),rgba(255,79,109,.02))}
.tl-zone{margin:20px 4px 0;font:700 11px var(--f);letter-spacing:.09em;text-transform:uppercase;color:var(--mu)}
.tl-zone.dz{color:#ff8da1}
.tl-res{margin-top:12px;padding:14px 18px;border-left:4px solid var(--ok)}
.tl-res.bad{border-left-color:var(--no)}
.tl-res b{display:block;font-size:13.5px}
.tl-res small{color:var(--mu);font-size:11.5px;font-weight:400;margin-left:6px}
.tl-res ul{margin:8px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:3px;font-size:12.5px;color:var(--mu)}
.tl-res li b{display:inline;color:var(--tx);font-weight:600;font-size:12.5px}
.mbox input.mi{width:100%;margin:-6px 0 18px;padding:11px 14px;border-radius:13px;border:1px solid var(--ln2);background:var(--s1);color:var(--tx);outline:0;font:600 14px var(--mono);letter-spacing:.06em;text-transform:uppercase}
.mbox input.mi:focus{border-color:var(--no)}
.btn:disabled.dng.solid{opacity:.35}
@media(max-width:700px){.tl{grid-template-columns:44px minmax(0,1fr);gap:12px}.tl .ti{width:44px;height:44px;font-size:20px}.tl .btn{grid-column:1/-1;width:100%}}

/* ── IP ── */
.ipstat{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.ipstat .card{padding:18px 20px}.ipstat .v{font:800 34px/1 var(--f)}.ipstat small{display:block;color:var(--mu);font-size:12px;margin-top:6px}
.ipl{display:flex;flex-direction:column;gap:7px;margin-top:16px}
.ipr{display:grid;grid-template-columns:18px minmax(0,1.6fr) minmax(0,1fr) 84px;gap:14px;align-items:center;padding:12px 18px;border-radius:16px;background:var(--s1);border:1px solid var(--ln)}
.ipr .dot{width:10px;height:10px;border-radius:50%;background:#3a4058}.ipr.on .dot{background:var(--ok);box-shadow:0 0 12px var(--ok)}
.ipr b{font:600 14px var(--mono);word-break:break-all}.ipr small{display:block;color:var(--mu);font-size:11.5px;line-height:1.45;margin-top:2px}
.ipr .rq{text-align:right;font:700 17px var(--f)}.ipr .rq small{font-weight:400}
.lock{padding:30px;text-align:center}.lock form,.lock .row{display:flex;gap:10px;justify-content:center;margin-top:16px;flex-wrap:wrap}
.lock input{width:240px;max-width:100%;padding:10px 14px;border-radius:13px;border:1px solid var(--ln2);background:var(--s1);outline:0}
.lock input:focus{border-color:var(--lime)}

/* ── khung chờ / lỗi ── */
.sk{border-radius:16px;background:linear-gradient(100deg,rgba(255,255,255,.04) 30%,rgba(255,255,255,.1) 50%,rgba(255,255,255,.04) 70%);background-size:220% 100%;animation:sh 1.5s linear infinite}
@keyframes sh{to{background-position:-220% 0}}
.skel{display:grid;grid-template-columns:216px 1fr 220px;gap:30px;align-items:center;padding:28px 30px}
.skel .o{width:216px;height:216px;border-radius:50%}
.state{padding:56px 28px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px}
.state .em{font-size:40px;line-height:1}
.state h3{margin:6px 0 0;font:700 19px var(--f)}
.state p{margin:0;color:var(--mu);max-width:520px;font-size:13px}
.state code{display:block;margin-top:6px;padding:8px 14px;border-radius:12px;background:var(--s1);border:1px solid var(--ln);font:12px var(--mono);color:#ffb6c2;max-width:100%;word-break:break-word}
.spin{width:44px;height:44px;border-radius:50%;border:3px solid rgba(255,255,255,.1);border-top-color:var(--lime);border-right-color:var(--lime);animation:spin 1s linear infinite}

/* ── dock di động ── */
.dock{display:none}

/* ── cổng duyệt thiết bị ── */
.gate{position:fixed;inset:0;z-index:100;display:none;place-items:center;padding:20px;background:rgba(5,6,10,.78);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px)}
.gate.on{display:grid}
.gbox{width:100%;max-width:410px;text-align:center;padding:34px 28px 28px;border-radius:28px;background:linear-gradient(180deg,#171b2a,#0f121c);border:1px solid var(--ln2);box-shadow:0 40px 100px -30px #000}
.gic{width:84px;height:84px;margin:0 auto 20px;border-radius:50%;display:grid;place-items:center;font-size:34px;position:relative;background:rgba(255,255,255,.05)}
.gic.scan:before,.gic.scan:after{content:"";position:absolute;inset:-6px;border-radius:50%;border:2px solid var(--lime);opacity:0;animation:rad 2.2s ease-out infinite}
.gic.scan:after{animation-delay:1.1s}
@keyframes rad{0%{transform:scale(.8);opacity:.9}100%{transform:scale(1.45);opacity:0}}
.gbox h2{margin:0 0 8px;font:700 20px var(--f)}.gbox p{margin:0;color:var(--mu);font-size:13px;line-height:1.65}
.gcode{margin:20px 0;padding:11px 14px;border-radius:14px;background:rgba(0,0,0,.35);border:1px solid var(--ln);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mu)}
.gcode b{display:block;margin-top:3px;font:700 14px var(--mono);letter-spacing:.06em;color:var(--tx);text-transform:none}
.gbox .btn{width:100%;padding:12px}

/* ── hộp thoại + toast ── */
.modal{position:fixed;inset:0;z-index:90;display:grid;place-items:center;padding:20px;background:rgba(4,5,9,.72);-webkit-backdrop-filter:blur(7px);backdrop-filter:blur(7px)}
.mbox{width:100%;max-width:410px;padding:26px;border-radius:24px;background:linear-gradient(180deg,#171b2a,#0f121c);border:1px solid var(--ln2);box-shadow:0 40px 100px -30px #000;animation:up .22s ease-out}
.mbox h3{margin:0 0 8px;font:700 18px var(--f)}.mbox p{margin:0 0 20px;color:var(--mu);font-size:13px;line-height:1.65;white-space:pre-line}
.mbox .row{display:flex;gap:10px;justify-content:flex-end}
#toasts{position:fixed;right:20px;bottom:20px;z-index:95;display:flex;flex-direction:column;gap:10px;align-items:flex-end;pointer-events:none}
.toast{pointer-events:auto;max-width:380px;padding:13px 18px;border-radius:16px;background:#1a1f2f;border:1px solid var(--ln2);box-shadow:0 20px 50px -14px #000;font-size:13px;line-height:1.55;animation:up .25s ease-out;border-left:4px solid var(--lime);white-space:pre-line}
.toast.bad{border-left-color:var(--no)}
@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.pop>*{animation:up .38s ease-out both}

@media(max-width:1080px){
  .stage{grid-template-columns:auto minmax(0,1fr);}
  .stage .prev{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;gap:16px;text-align:left}
  .stage .prev .dice{margin:0}.stage .prev>div{display:flex;align-items:center;gap:18px}
  .kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  .road{grid-template-columns:1fr}
}
@media(max-width:980px){
  .app{grid-template-columns:1fr;gap:16px;padding:14px 14px 110px}
  .side{position:static;max-height:none;flex-direction:row;align-items:center;justify-content:space-between;flex-wrap:wrap}
  .side .navh,.side .nav,.side .sfoot{display:none}
  .dock{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));position:fixed;left:10px;right:10px;bottom:calc(10px + env(safe-area-inset-bottom));z-index:30;padding:6px;border-radius:24px;background:rgba(14,16,24,.9);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);border:1px solid var(--ln2);box-shadow:0 20px 50px -10px #000}
  .dk{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;padding:8px 2px 7px;border:0;background:none;border-radius:18px;font-size:10px;color:var(--mu);min-width:0;line-height:1.1}
  .dk span{width:30px;height:30px;border-radius:10px;display:grid;place-items:center;font:800 10.5px var(--f);color:var(--gc);background:rgba(255,255,255,.05)}
  .dk.on{background:rgba(255,255,255,.08);color:var(--tx)}.dk.on span{background:var(--gc);color:#0b0d12}
  .dk i{position:absolute;top:6px;right:calc(50% - 22px);width:9px;height:9px;border-radius:50%;border:2px solid #0e1018}
  .dk i.tai{background:var(--tai)}.dk i.xiu{background:var(--xiu)}
  #toasts{right:12px;left:12px;bottom:100px;align-items:stretch}.toast{max-width:none}
}
@media(max-width:700px){
  .stage{grid-template-columns:1fr;justify-items:center;text-align:center;padding:24px 18px;gap:22px}
  .stage .chips{justify-content:center}.eyebrow{justify-content:center}
  .stage>div:nth-child(2){width:100%}
  .orb{width:190px;height:190px}
  .prev{width:100%}
  .skel{grid-template-columns:1fr;justify-items:center}
  .ipstat{grid-template-columns:1fr}
  .hh{display:none}
  .hh,.hr{grid-template-columns:78px minmax(0,1fr) minmax(0,1fr) 34px;gap:8px}
  .hr{padding:10px 12px 10px 14px}
  .hr-r{flex-direction:column;align-items:flex-start;gap:3px}
  .ipr{grid-template-columns:14px minmax(0,1fr) 64px}.ipr>div:nth-child(3){display:none}
  .pbar{margin-top:18px}
  .seg button{padding:8px 12px}
}
@media(max-width:420px){.kpi{padding:14px 12px;gap:10px}.kpi .v{font-size:25px}.ring{width:54px;height:54px}.ring:before{inset:6px}.kpi .ic{width:38px;height:38px;font-size:17px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style></head><body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="dg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffdf5"/><stop offset="1" stop-color="#ddd8c7"/></linearGradient><linearGradient id="lg1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2ff6b"/><stop offset="1" stop-color="#6fe03a"/></linearGradient></defs></svg>
<div class="amb"><i class="n"></i><i class="t"></i><i class="x"></i></div>

<div class="app">
  <aside class="side">
    <div class="brand">
      <svg class="logo" viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="14" fill="url(#lg1)"/><g fill="#0c1206"><circle cx="15.5" cy="15.5" r="3.7"/><circle cx="32.5" cy="15.5" r="3.7"/><circle cx="24" cy="24" r="3.7"/><circle cx="15.5" cy="32.5" r="3.7"/><circle cx="32.5" cy="32.5" r="3.7"/></g></svg>
      <div class="bn"><b>SUNVIW</b><span>Radar Tài Xỉu</span></div>
    </div>
    <div class="live idle" id="live"><i></i><span>Đang khởi động…</span></div>
    <div class="navh">Bàn theo dõi</div>
    <nav class="nav" id="nav"></nav>
    <div class="sfoot" id="sfoot"></div>
  </aside>
  <main class="main">
    <div id="banner"></div>
    <div id="view"></div>
  </main>
</div>
<nav class="dock" id="dock"></nav>
<div id="toasts"></div>
<div class="modal" id="modal" hidden></div>
<div class="gate on" id="gate"><div class="gbox" id="gbox"><div class="gic scan"><div class="spin" style="width:34px;height:34px"></div></div><h2>Đang kiểm tra quyền truy cập…</h2><p>Chờ một chút, panel đang hỏi server về thiết bị này.</p></div></div>
<noscript><div style="position:fixed;inset:0;display:grid;place-items:center;background:#07080d;color:#fff;z-index:200;padding:20px;text-align:center">Panel cần bật JavaScript để hoạt động.</div></noscript>

<script>
/*__HWID_JS__*/
</script>
<script>
"use strict";
/* ════════════════════════════════════════════════════════════════════════════════════════════════
   PANEL SUNVIW — bản dựng lại hoàn toàn.
   VÌ SAO BẢN CŨ HAY TRẮNG TRANG: nó chờ Promise.all(IP + cả 5 bàn, mỗi bàn hist=300) xong mới vẽ lần đầu, và cờ LOADING không bao giờ
   được thả nếu 1 request treo -> chỉ cần 1 bàn chậm / nguồn chết là cả panel trống và đứng luôn.
   BẢN MỚI: · vẽ khung (menu + skeleton) NGAY khi mở trang, trước mọi request
            · mỗi bàn có vòng poll RIÊNG (không bàn nào chờ bàn nào), mỗi request có timeout + AbortController
            · bàn đang xem poll 3s (đủ lịch sử + chi tiết), các bàn khác chỉ lấy bản nhẹ (hist=0) 9s/lần
            · lỗi mạng thoáng qua KHÔNG khóa panel và KHÔNG xóa dữ liệu đang hiển thị — chỉ hiện banner "dữ liệu cũ"
            · mọi phần vẽ chạy trong try/catch riêng: 1 phần lỗi không kéo sập phần còn lại
   ════════════════════════════════════════════════════════════════════════════════════════════════ */
const HDR=(typeof HWID_HDR!=='undefined')?HWID_HDR:{};
const DEVID=(typeof HWID!=='undefined')?HWID:'unknown';
const MAXN=__MAX__,POLL=3000,POLL_BG=9000,TMO=12000;
const G=[
  {k:'sun', n:'Sun',       sn:'Sun',    s:'SU',u:'/api/predictsun',         g:'sun',        c:'#ffd23f'},
  {k:'hitt',n:'Hit Thường',sn:'Hit TT', s:'HT',u:'/api/predicthittxthuong', g:'hittxthuong',c:'#ff7ad9'},
  {k:'hitm',n:'Hit MD5',   sn:'Hit MD5',s:'HM',u:'/api/predicthittxmd5',    g:'hittxmd5',   c:'#a78bfa'},
  {k:'lcm', n:'LC MD5',    sn:'LC MD5', s:'LM',u:'/api/predictlcmd5',       g:'lcmd5',      c:'#2dd4bf'},
  {k:'lch', n:'LC Hũ',     sn:'LC Hũ',  s:'LH',u:'/api/predictlchu',        g:'lchu',       c:'#94e04a'}];
const GM={};G.forEach(x=>GM[x.k]=x);
const IPC='#8d94ab';
const MN={ALL:'ALL',CAO:'CAO',THAP:'THẤP'},MS=['ALL','CAO','THAP'];
const MTIP={ALL:'Không chia nhóm: vote tất cả logic',CAO:'Nhóm logic WR cao đông hơn → chỉ vote nhóm CAO',THAP:'Nhóm logic WR thấp đông hơn → chỉ vote nhóm THẤP'};

const $=(s,r)=>(r||document).querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cl=v=>v==='TÀI'?'tai':v==='XỈU'?'xiu':'';
const ls={g:k=>{try{return localStorage.getItem(k)}catch(e){return null}},s:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}};
const clampN=v=>Math.max(1,Math.min(Math.floor(+v)||1,MAXN));
const pc=v=>Math.max(0,Math.min(100,+v||0));
const ago=ms=>{const s=Math.max(0,Math.round(ms/1000));return s<60?s+'s':s<3600?Math.floor(s/60)+'p':s<86400?Math.floor(s/3600)+'g':Math.floor(s/86400)+'n'};
const agoSec=s=>ago(s*1000);

/* ── trạng thái ── */
const S={};G.forEach(x=>S[x.k]={d:null,err:'',t:0,fails:0,busy:false,full:false,seq:0,ctl:null});
let IPD=null,ipErr='',ipT=0,ipBusy=false;
let ACC=false,banned=false,accBusy=false,accFails=0,GV='';
let cur=(ls.g('g')==='ip'||GM[ls.g('g')])?ls.g('g'):'sun';
let N=clampN(ls.g('n')||__SHOW__);
let MF=MS.includes(ls.g('mf'))?ls.g('mf'):'';
let pane=['hist','logic','tools'].includes(ls.g('pane'))?ls.g('pane'):'hist';
let shell='';
let TS=ls.g('ts')==='all'?'all':'one',ACTB='',TRES=null;   /* tab Công cụ: phạm vi (1 bàn / cả 5 bàn) · thao tác đang chạy · kết quả lần chạy gần nhất */

/* ── gọi API: luôn kèm HWID, có timeout, không bao giờ treo vô hạn ── */
async function api(url,o){
  o=o||{};
  const ctl=o.ctl||new AbortController(),tm=o.timeout||TMO,to=setTimeout(()=>{ctl.__to=1;ctl.abort()},tm);
  try{
    const r=await fetch(url,{method:o.method||'GET',cache:'no-store',signal:ctl.signal,
      headers:Object.assign({},HDR,o.json?{'Content-Type':'application/json'}:{},o.headers||{}),
      body:o.json?JSON.stringify(o.json):undefined});
    let j=null;try{j=await r.json()}catch(e){}
    if(r.status===401&&ACC&&url.indexOf('/api/panel/')!==0){ACC=false;GV='';access()}   /* bị gỡ quyền giữa chừng → kiểm tra lại ngay */
    return{status:r.status,j};
  }finally{clearTimeout(to)}
}

/* ── ghi DOM chỉ khi nội dung đổi (không giật, giữ cuộn, không đè ô đang gõ) ── */
const LAST=new WeakMap();
function put(sel,html){
  const el=typeof sel==='string'?$(sel):sel;if(!el)return false;
  if(LAST.get(el)===html)return false;
  const a=document.activeElement;
  if(a&&el.contains(a)&&/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName))return false;
  LAST.set(el,html);
  const y=window.scrollY;el.innerHTML=html;
  if(window.scrollY!==y)window.scrollTo(0,y);
  return true;
}
function pop(el){el=el||$('#view');if(!el)return;el.classList.remove('pop');void el.offsetWidth;el.classList.add('pop')}
function safe(fn,label){try{return fn()}catch(e){console.error(label,e);return `<div class="empty" style="margin:10px 0">⚠ Lỗi hiển thị mục “${esc(label)}”: ${esc(e&&e.message||e)}</div>`}}
let rq=0;
function paint(){if(rq)return;rq=requestAnimationFrame(()=>{rq=0;try{draw()}catch(e){console.error(e)}})}

/* ── dữ liệu & tính toán ── */
function acc(d){
  const h=d&&d.lich_su;
  if(Array.isArray(h)){const k=h.filter(x=>x.dung).length;return{k,t:h.length,p:h.length?Math.round(k*100/h.length):null,full:true}}
  const t=d&&d.tool_dung_sai_10_van;
  if(t&&t.tong)return{k:t.dung,t:t.tong,p:Math.round(t.dung*100/t.tong),full:false};
  return{k:0,t:0,p:null,full:false};
}
const modeAcc=(h,m)=>{const r=h.filter(x=>x.che_do===m),k=r.filter(x=>x.dung).length;return{k,t:r.length,p:r.length?Math.round(k*100/r.length):null}};
function streak(h){if(!h||!h.length)return null;const f=!!h[0].dung;let n=0;for(const x of h){if(!!x.dung===f)n++;else break}return{ok:f,n}}
const P={1:[[20,20]],2:[[11,11],[29,29]],3:[[11,11],[20,20],[29,29]],4:[[11,11],[29,11],[11,29],[29,29]],5:[[11,11],[29,11],[20,20],[11,29],[29,29]],6:[[11,10],[29,10],[11,20],[29,20],[11,30],[29,30]]};
const die=n=>`<svg class="die" viewBox="0 0 40 40" aria-hidden="true"><rect x="1.5" y="1.5" width="37" height="37" rx="10" fill="url(#dg)"/><rect x="1.5" y="1.5" width="37" height="37" rx="10" fill="none" stroke="rgba(0,0,0,.18)"/>${(P[n]||[]).map(([x,y])=>`<circle cx="${x}" cy="${y}" r="${n===1?6:3.7}" fill="${n===1?'#e5384f':'#1b2036'}"/>`).join('')}</svg>`;
const bd=(c,t,tip)=>`<span class="bd ${c}"${tip?` title="${esc(tip)}"`:''}>${t}</span>`;

/* ── vẽ: menu bàn ── */
function navHtml(dock){
  const items=G.map(g=>({k:g.k,n:g.n,sn:g.sn,s:g.s,c:g.c})).concat([{k:'ip',n:'IP truy cập',sn:'IP',s:'IP',c:IPC}]);
  return items.map(g=>{
    const on=g.k===cur;let pred='',sub='',cls='';
    if(g.k==='ip'){sub=IPD&&IPD.ok?`${IPD.dang_dung} online · ${IPD.tong} IP`:(IPD&&IPD.khoa?'🔒 cần admin key':'Theo dõi thiết bị');if(IPD&&IPD.ok&&IPD.dang_dung)pred='on'}
    else{const st=S[g.k],d=st.d,a=acc(d);cls=d?cl(d.du_doan):'';sub=d?(a.p===null?'Chưa có thống kê':`${a.p}% đúng · ${a.t} ván`):(st.err?'Chưa có dữ liệu':'Đang tải…');pred=d?d.du_doan:''}
    if(dock)return `<button class="dk${on?' on':''}" data-g="${g.k}" style="--gc:${g.c}" aria-label="${esc(g.n)}"><span>${g.s}</span>${esc(g.sn)}${cls?`<i class="${cls}"></i>`:''}</button>`;
    const chip=g.k==='ip'?(pred?`<span class="pp xiu" style="color:var(--ok);background:rgba(52,227,160,.13);box-shadow:inset 0 0 0 1px rgba(52,227,160,.4)">${IPD.dang_dung}</span>`:''):`<span class="pp ${cls||'no'}">${pred?(pred==='TÀI'?'TÀI':'XỈU'):'···'}</span>`;
    return `<button class="ni${on?' on':''}" data-g="${g.k}" style="--gc:${g.c}"><span class="ni-ic">${g.s}</span><span class="ni-t"><b>${esc(g.n)}</b><small>${esc(sub)}</small></span>${chip}</button>`;
  }).join('');
}

/* ── vẽ: sân khấu dự đoán ── */
function modeInfo(d){
  if(!d.che_do)return d.be_final?`<div class="chips">${bd('flip','Đã bẻ final')}</div>`:'';
  const m=d.che_do,w=d.wr_che_do_hien_tai,goc=d.du_doan_goc||d.du_doan;
  const parts=[bd(m,'Chế độ '+MN[m],MTIP[m]),bd(d.be_final?'flip':'off','Bẻ final '+(d.be_final?'BẬT':'TẮT'),'Bẻ final theo cấu hình hiện tại, áp dụng cho chế độ '+MN[m])];
  if(m!=='ALL'||w)parts.push(bd(d.be_che_do?'flip':'off','Bẻ chế độ '+(d.be_che_do?'BẬT':'TẮT'),'Bẻ theo WR của chế độ đang chạy'));
  const ex=w?`<div class="note">WR chế độ ${MN[w.che_do]} (${w.cua_so} ván gần nhất của chế độ): ${w.wr==null?`chưa đủ ván (${w.so_van}/${w.van_toi_thieu})`:`<b>${w.dung}/${w.so_van} = ${w.wr}%</b> ${w.se_be?'&lt; '+w.nguong_be+'% → bẻ chế độ':'≥ '+w.nguong_be+'% → không bẻ chế độ'}`}</div>`:'';
  const seq=d.be_che_do&&d.du_doan_truoc_be_che_do?[d.du_doan_truoc_be_che_do,goc]:[goc];
  if(d.be_final)seq.push(d.du_doan);
  const how=[d.be_che_do?'bẻ chế độ':'',d.be_final?'bẻ final':''].filter(Boolean).join(' + ');
  const ch=seq.length>1?`<div class="note">Gốc ${seq.map(v=>`<b class="${cl(v)}">${esc(v)}</b>`).join(' → ')} <span>(${how})</span></div>`:'';
  return `<div class="chips">${parts.join('')}</div>${ex}${ch}`;
}
function prevHtml(d){
  if(d.phien_truoc==null)return `<div class="prev"><small>Phiên trước</small><div class="note" style="margin-top:12px">Chưa có kết quả phiên trước</div></div>`;
  const dc=Array.isArray(d.xuc_xac)?`<div class="dice">${d.xuc_xac.map(die).join('')}</div>`:'';
  return `<div class="prev"><small>Phiên trước · #${esc(d.phien_truoc)}</small>${dc}<div>${d.tong==null?'':`<span class="sum"><small>Tổng</small>${esc(d.tong)}</span>`}</div><span class="pill ${cl(d.ket_qua_truoc)}">${esc(d.ket_qua_truoc)}</span></div>`;
}
function stageHtml(g,d){
  const c=cl(d.du_doan),sd=c==='tai'?'t':c==='xiu'?'x':'',conf=d.do_tin_cay;
  return `<section class="card stage ${sd}" style="--gc:${g.c}">
    <div class="orb ${sd?'':'none'}"><div class="orb-core"><small>Dự đoán</small><b>${esc(d.du_doan)}</b><span>phiên #${esc(d.phien)}</span></div></div>
    <div>
      <div class="eyebrow"><span class="gtag">${esc(g.n)}</span><span>Phiên đang chờ <b>#${esc(d.phien)}</b></span></div>
      <div class="conf-h"><span>Độ tin cậy</span><b>${conf==null?'–':conf+'%'}</b></div>
      <div class="bar"><i style="width:${pc(conf)}%"></i></div>
      <div class="note" style="margin-top:8px">Trung bình WR có trọng số của các logic · xét ${esc(d.so_van_wr==null?'?':d.so_van_wr)} ván gần nhất</div>
      ${modeInfo(d)}
    </div>
    ${prevHtml(d)}
  </section>`;
}

/* ── vẽ: KPI + dòng ván ── */
function kpiHtml(d){
  const a=acc(d),st=streak(d.lich_su),lab=a.full?`ván trong ${a.t} ván hiển thị`:'ván (10 ván gần nhất)';
  const rc=a.p==null?'#555':a.p>=55?'var(--ok)':a.p>=45?'var(--warn)':'var(--no)';
  return `<div class="card kpi"><div class="ring" style="--p:${a.p||0};--rc:${rc}"><b>${a.p==null?'–':a.p+'%'}</b></div><div><div class="v">${a.p==null?'–':a.p+'%'}</div><small>Tỉ lệ đúng<br>${a.t} ván</small></div></div>
  <div class="card kpi"><div class="ic g">✓</div><div><div class="v okc">${a.k}</div><small>Ván đúng</small></div></div>
  <div class="card kpi"><div class="ic r">✕</div><div><div class="v noc">${a.t-a.k}</div><small>Ván sai</small></div></div>
  <div class="card kpi"><div class="ic f">${st?(st.ok?'▲':'▼'):'•'}</div><div><div class="v ${st?(st.ok?'okc':'noc'):''}">${st?st.n:'–'}</div><small>${st?(st.ok?'đúng liên tiếp':'sai liên tiếp'):'Chuỗi hiện tại'}</small></div></div>`;
}
function sparkHtml(h){
  const w=10,rows=h.slice().reverse();                 /* cũ → mới */
  if(rows.length<w+2)return '';
  const pts=[];for(let i=w-1;i<rows.length;i++){let k=0;for(let j=i-w+1;j<=i;j++)if(rows[j].dung)k++;pts.push(k*100/w)}
  const W=600,H=96,sx=W/Math.max(1,pts.length-1),y=v=>H-6-(v/100)*(H-12);
  const line=pts.map((v,i)=>(i?'L':'M')+(i*sx).toFixed(1)+' '+y(v).toFixed(1)).join(' ');
  const mn=Math.min(...pts),mx=Math.max(...pts),last=pts[pts.length-1];
  return `<div><h3>Tỉ lệ đúng trượt 10 ván<span>cũ → mới</span></h3>
  <svg class="spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="spf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c6ff3d" stop-opacity=".32"/><stop offset="1" stop-color="#c6ff3d" stop-opacity="0"/></linearGradient></defs>
  <line x1="0" x2="${W}" y1="${y(50)}" y2="${y(50)}" stroke="rgba(255,255,255,.22)" stroke-dasharray="4 5" vector-effect="non-scaling-stroke"/>
  <path d="${line} L${W} ${H} L0 ${H} Z" fill="url(#spf)"/><path d="${line}" fill="none" stroke="#c6ff3d" stroke-width="2.4" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>
  <div class="spk-s"><span>Thấp nhất <b>${Math.round(mn)}%</b></span><span>Hiện tại <b>${Math.round(last)}%</b></span><span>Cao nhất <b>${Math.round(mx)}%</b></span></div></div>`;
}
function roadHtml(d){
  const h=d.lich_su;
  if(!Array.isArray(h))return `<div class="card road"><div class="sk" style="height:70px"></div><div class="sk" style="height:70px"></div></div>`;
  if(!h.length)return '';
  const cap=84,beads=h.slice(0,cap).map(x=>`<span class="bead ${x.dung?'ok':'no'}${x.che_do?' m-'+x.che_do:''}" title="#${x.phien}${x.che_do?' · '+MN[x.che_do]:''}${x.be_final?' · bẻ final':''}">${x.dung?'✓':'✕'}</span>`).join('');
  const sp=sparkHtml(h);
  return `<div class="card road" style="${sp?'':'grid-template-columns:1fr'}"><div><h3>Dòng ván gần đây<span>mới nhất ở đầu${h.length>cap?` · ${cap}/${h.length}`:''}</span></h3><div class="beads">${beads}</div></div>${sp}</div>`;
}

/* ── vẽ: lịch sử ── */
function histBar(d){
  const h=d.lich_su;
  const pre=[10,20,50,100,300].filter(v=>v<=MAXN);
  let f='';
  if(Array.isArray(h)&&h.some(x=>x.che_do)){
    const a=acc(d);
    f=`<div class="grp"><button class="cx${MF===''?' on':''}" data-m=""><span>Tất cả</span><b>${a.k}/${a.t}</b></button>${MS.map(m=>{const s=modeAcc(h,m);return `<button class="cx ${m}${MF===m?' on':''}" data-m="${m}" title="${esc(MTIP[m])}"><span>${MN[m]}</span><b>${s.k}/${s.t}</b><span>${s.p==null?'–':s.p+'%'}</span>${d.che_do===m?'<span class="okc">●</span>':''}</button>`}).join('')}</div>`;
  }
  return `<div class="hbar"><div class="grp"><label for="n">Số ván</label>${pre.map(v=>`<button class="cx${N===v?' on':''}" data-n="${v}">${v}</button>`).join('')}<input id="n" type="number" min="1" max="${MAXN}" value="${N}" aria-label="Số ván lịch sử"></div>${f}</div>`;
}
function histHtml(d){
  const h=d.lich_su;
  if(!Array.isArray(h))return `<div class="hl">${'<div class="sk" style="height:54px"></div>'.repeat(6)}</div>`;
  const hm=h.some(x=>x.che_do),hv=(MF&&hm)?h.filter(x=>x.che_do===MF):h;
  if(!hv.length)return h.length?`<div class="empty">Không có ván nào ở chế độ ${MN[MF]||''} trong ${h.length} ván đang hiển thị — tăng số ván hoặc bấm “Tất cả”.</div>`:`<div class="empty">Chưa có ván nào được chấm.<br><span class="mu" style="font-size:12px">Tool lưu dự đoán rồi chờ kết quả phiên đó — kết quả lấy từ API của bàn.</span></div>`;
  const rows=hv.map(x=>{
    const tags=x.che_do?`<span>${bd(x.che_do,MN[x.che_do],MTIP[x.che_do])}${x.be_final?bd('flip','BẺ','Final bị bẻ theo cấu hình hiện tại'):''}${x.be_che_do?bd('flip','BẺ CĐ','Bẻ theo WR chế độ'):''}</span>`:'';
    return `<div class="hr ${x.dung?'ok':'no'}"><div class="hr-id">#${esc(x.phien)}${tags}</div><div class="hr-r"><span class="pill ${cl(x.du_doan)}">${esc(x.du_doan)}</span></div><div class="hr-r"><span class="pill ${cl(x.ket_qua)}">${esc(x.ket_qua)}</span>${x.tong==null?'':`<small>tổng ${esc(x.tong)}</small>`}</div><div class="hr-k" title="${x.dung?'Đúng':'Sai'}">${x.dung?'✓':'✕'}</div></div>`}).join('');
  return `<div class="hl"><div class="hh"><span>Phiên</span><span>Dự đoán</span><span>Kết quả</span><span></span></div>${rows}</div>${hm?'<div class="legend">BẺ = final bị bẻ theo cấu hình hiện tại · BẺ CĐ = bẻ theo WR chế độ · viền màu quanh dấu ✓/✕ ở “Dòng ván” = chế độ của ván.<br>Đúng/sai được tính lại theo cấu hình bẻ hiện tại · bấm một chế độ để lọc lịch sử.</div>':''}`;
}

/* ── vẽ: từng logic ── */
function logicHtml(d){
  const ct=d.chi_tiet,L=ct&&ct.logic;
  if(!ct)return `<div class="lg">${'<div class="sk" style="height:112px"></div>'.repeat(8)}</div>`;
  if(!L||!L.length)return `<div class="empty">Chưa có dữ liệu từng logic.</div>`;
  const A=ct.af,af=!!(A&&A.dang_dung),use=x=>af?x.af_du_doan:x.du_doan;
  const nT=L.filter(x=>use(x)==='TÀI').length,nX=L.filter(x=>use(x)==='XỈU').length;
  const notes=[];
  if(af){
    const v=A.gioi_han_vung_be,ng=A.nguong_be_logic;
    if(v&&v.bat)notes.push(`Chỉ bẻ logic khi WR trong vùng THẤP ${v.thap[0]}–${v.thap[1]}% hoặc CAO ${v.cao[0]}–${v.cao[1]}% · ngoài vùng không bẻ`);
    else if(ng)notes.push(`Bẻ logic khi WR < ${ng.thap}% hoặc > ${ng.cao}%`);
    if(A.chi_be_vao_nhom)notes.push('Chỉ logic đã bẻ mới vào nhóm CAO/THẤP, logic không bẻ = ALL');
    if(A.doi_che_do_de){const pv=A.phieu_che_do,pr=A.che_do_truoc;
      notes.push('Đổi chế độ chỉ cần ≥ '+A.phieu_doi_che_do+'/'+L.length+' phiếu'+(pv?` (phiếu: ALL ${pv.ALL} · CAO ${pv.CAO} · THẤP ${pv.THAP}${pr?' · ván trước: '+(MN[pr]||pr):''}${A.da_doi_che_do?' → ĐÃ ĐỔI':' → giữ chế độ'})`:''))}
    else if(A.can_da_so_nhom)notes.push('Nhóm CAO/THẤP cần ≥ '+A.da_so_toi_thieu+' logic (đa số), ít hơn → dùng ALL');
    if(A.ha_xuong_all)notes.push(A.doi_che_do_de?'Ván này: nhóm đang giữ hết logic → dùng ALL':'Ván này: nhóm chưa đủ đa số → ĐÃ HẠ VỀ ALL');
  }
  notes.push('WR = tỉ lệ đúng có trọng số trong '+(d.so_van_wr||'?')+' ván gần nhất'+(af?' · khi bị bẻ, “→ x%” là WR sau bẻ (100 − WR) · lá phiếu hiển thị là phiếu sau khi bẻ logic':''));
  const cards=L.map(x=>{
    const v=use(x),flipped=af&&!!x.af_be,grp=af?x.af_nhom:x.nhom,out=af&&x.af_vote===false;
    const eff=(flipped&&x.af_wr!=null)?x.af_wr:x.wr;
    return `<div class="lc${out?' out':''}"><div class="lc-h"><b title="${esc(x.ten)}">${esc(x.ten)}</b><span class="pill ${cl(v)}">${esc(v)}</span></div>
      <div class="lc-wr"><div class="bar sm"><i style="width:${pc(eff)}%"></i></div><span>${x.wr==null?'–':x.wr+'%'}${flipped&&x.af_wr!=null?`<em>→ ${x.af_wr}%</em>`:''}</span></div>
      <div class="lc-f">${flipped?bd('flip',x.af_be==='LOW'?'BẺ · WR thấp':'BẺ · WR cao','Phiếu gốc '+x.du_doan+' bị đảo ở bước 1 của AF')+`<span class="was ${cl(x.du_doan)}">gốc ${esc(x.du_doan)}</span>`:''}${grp?bd(grp,MN[grp]||grp):(af?bd('ALL','ALL','Không bẻ → mặc định chế độ ALL'):'')}${out?'<span class="mu">ngoài nhóm vote</span>':''}</div></div>`}).join('');
  return `<div class="vs"><div class="a" style="flex:${nT} 1 0">${nT?'TÀI '+nT:''}</div><div class="b" style="flex:${nX} 1 0">${nX?'XỈU '+nX:''}</div></div>
    <div class="callout">${notes.map(n=>`<p>${esc(n)}</p>`).join('')}</div><div class="lg">${cards}</div>`;
}

/* ── vẽ: công cụ ── */
function toolsHtml(g){
  const all=TS==='all',who=all?'cả 5 bàn':g.n,B=ACTB;
  const btn=(k,cls,label)=>`<button class="btn ${cls}" data-act="${k}"${B?' disabled':''}>${B===k?'⏳ Đang chạy…':label}</button>`;
  const res=TRES?`<div class="card tl-res${TRES.bad?' bad':''}"><b>${TRES.bad?'⚠ ':'✓ '}${esc(TRES.title)}<small>lúc ${esc(TRES.time)}</small></b>${TRES.lines.length?`<ul>${TRES.lines.map(l=>`<li>${l}</li>`).join('')}</ul>`:''}</div>`:'';
  return `<div class="card tl-head"><div><h4>Công cụ áp dụng cho: ${esc(who)}</h4><p>${all?'Mỗi thao tác bên dưới sẽ chạy cho <b>tất cả 5 bàn</b> cùng lúc.':'Chỉ tác động tới bàn <b>'+esc(g.n)+'</b>. Muốn làm cho mọi bàn, chọn “Cả 5 bàn”.'}</p></div>
      <div class="seg" role="tablist"><button class="${all?'':'on'}" data-ts="one">Bàn ${esc(g.sn)}</button><button class="${all?'on':''}" data-ts="all">Cả 5 bàn</button></div></div>
    ${res}
    <div class="tl-zone">An toàn — dùng thoải mái</div>
    <div class="tl-list">
      <div class="card tl rec"><div class="ti">🔄</div><div><h5>Tính lại đúng/sai <em>NÊN DÙNG</em></h5><p><b>Dùng khi:</b> vừa đổi config (ngưỡng AF, bẻ final, WR…) và muốn thấy kết quả mới ngay. Lịch sử vẫn giữ nguyên, chỉ chấm lại bằng config đang chạy — mất vài giây.</p></div>${btn('regrade','pri','Tính lại '+(all?'5 bàn':g.n))}</div>
      <div class="card tl"><div class="ti">🧹</div><div><h5>Xóa lịch sử hiển thị</h5><p><b>Dùng khi:</b> muốn bảng đúng/sai và thống kê đếm lại từ đầu. Chỉ ẩn danh sách đang hiển thị — <b>không</b> ảnh hưởng logic / WR dùng để dự đoán.</p></div>${btn('clear','','Xóa lịch sử '+(all?'5 bàn':g.n))}</div>
    </div>
    <div class="tl-zone dz">Nguy hiểm — không hoàn tác được</div>
    <div class="tl-list">
      <div class="card tl danger"><div class="ti">☠</div><div><h5>Xóa sạch data</h5><p><b>Dùng khi:</b> muốn làm lại từ số 0. Xóa <b>thật</b> lịch sử xúc xắc và mọi ván đã chấm của ${all?'<b>cả 5 bàn</b>':'bàn này'}; WR / AF / dự đoán đếm lại từ đầu. Cần gõ <b>XOA</b> để xác nhận.</p></div>${btn('wipe','dng','Xóa data '+(all?'5 bàn':g.n))}</div>
    </div>`;
}

/* ── vẽ: một bàn ── */
function ensureShell(name,html){
  const v=$('#view');
  if(shell!==name){shell=name;v.innerHTML=html;pop(v)}
}
function drawGame(){
  const g=GM[cur],st=S[cur],d=st.d;
  ensureShell('game:'+cur,`<div id="v-stage"></div><div class="kpis" id="v-kpi"></div><div id="v-road"></div><div class="pbar" id="v-pbar"></div><div id="v-pbar2"></div><div id="v-body"></div>`);
  if(!d){
    if(st.err){
      put('#v-stage',`<div class="card state"><div class="em">📡</div><h3>Chưa có dữ liệu dự đoán</h3><p>Panel chưa nhận được kết quả từ bàn <b>${esc(g.n)}</b>. Nếu tool vừa khởi động, server cần vài giây để quét phiên đầu tiên — panel sẽ tự thử lại mỗi ${POLL/1000}s.</p><code>${esc(st.err)}</code><button class="btn pri" data-retry="1" style="margin-top:8px">Thử lại ngay</button></div>`);
    }else{
      put('#v-stage',`<div class="card skel"><div class="sk o"></div><div style="display:flex;flex-direction:column;gap:14px;width:100%"><div class="sk" style="height:20px;width:46%"></div><div class="sk" style="height:34px"></div><div class="sk" style="height:12px"></div><div class="sk" style="height:26px;width:62%"></div></div><div class="sk" style="height:170px;width:100%"></div></div>`);
    }
    put('#v-kpi',`${'<div class="card kpi"><div class="sk" style="height:46px;width:100%"></div></div>'.repeat(4)}`);put('#v-road','');put('#v-pbar','');put('#v-pbar2','');put('#v-body','');
    return;
  }
  put('#v-stage',safe(()=>stageHtml(g,d),'dự đoán'));
  put('#v-kpi',safe(()=>kpiHtml(d),'thống kê'));
  put('#v-road',safe(()=>roadHtml(d),'dòng ván'));
  const nh=Array.isArray(d.lich_su)?d.lich_su.length:null,nl=d.chi_tiet&&d.chi_tiet.logic?d.chi_tiet.logic.length:null;
  put('#v-pbar',`<div class="seg" role="tablist"><button class="${pane==='hist'?'on':''}" data-pane="hist">Lịch sử${nh==null?'':`<em>${nh}</em>`}</button><button class="${pane==='logic'?'on':''}" data-pane="logic">Logic${nl==null?'':`<em>${nl}</em>`}</button><button class="${pane==='tools'?'on':''}" data-pane="tools">Công cụ</button></div><button class="btn sm" data-retry="1" title="Tải lại ngay">⟳ Làm mới</button>`);
  if(pane==='hist'){put('#v-pbar2',safe(()=>histBar(d),'thanh lịch sử'));put('#v-body',safe(()=>histHtml(d),'lịch sử'))}
  else if(pane==='logic'){put('#v-pbar2','');put('#v-body',safe(()=>logicHtml(d),'logic'))}
  else{put('#v-pbar2','');put('#v-body',safe(()=>toolsHtml(g),'công cụ'))}
}

/* ── vẽ: tab IP ── */
function ipHtml(){
  const d=IPD;
  if(!d)return `<div class="card state"><div class="spin"></div><h3>Đang tải danh sách IP…</h3></div>`;
  if(d.khoa)return `<div class="card lock"><div style="font-size:34px">🔒</div><h3 style="margin:8px 0 0;font:700 18px var(--f)">Cần admin key để xem danh sách IP</h3><p class="mu" style="margin:6px 0 0;font-size:13px">Nhập key một lần, trình duyệt sẽ nhớ.</p><div class="row"><input id="ak" type="password" placeholder="Admin key" autocomplete="off"><button class="btn pri" id="akb">Mở khóa</button></div></div>`;
  if(!d.ok)return `<div class="card state"><div class="em">⚠️</div><h3>Không tải được danh sách IP</h3><code>${esc(d.loi||'Lỗi không rõ')}</code><button class="btn pri" data-retry="1" style="margin-top:8px">Thử lại</button></div>`;
  const by=o=>Object.entries(o||{}).map(([k,v])=>k+' '+v).join(' · ');
  return `<div class="ipstat"><div class="card"><div class="v okc">${esc(d.dang_dung)}</div><small>đang dùng (trong ${esc(d.cua_so_giay)}s)</small></div><div class="card"><div class="v">${esc(d.tong)}</div><small>IP đã từng dùng</small></div><div class="card"><div class="v" style="font:700 17px var(--mono);word-break:break-all;padding-top:9px">${esc(d.ban||'?')}</div><small>IP của bạn</small></div></div>
  <div class="ipl">${(d.ips||[]).map(x=>`<div class="ipr${x.dang_dung?' on':''}"><span class="dot"></span><div><b title="${esc(x.ua||'')}">${esc(x.ip)}</b>${x.la_ban?' <span class="bd live2">bạn</span>':''}<small>${esc(by(x.theo_loai))}</small></div><div><small style="margin:0;color:${x.dang_dung?'var(--ok)':'var(--mu)'}">${x.dang_dung?'● đang dùng':'○ đã dùng'}</small><small>${esc(x.gan_nhat)} · ${agoSec(x.truoc_giay)} trước<br>từ ${esc(x.lan_dau)}</small></div><div class="rq">${esc(x.so_request)}<small>request</small></div></div>`).join('')}</div>`;
}
function drawIp(){
  ensureShell('ip','<div id="v-ip"></div>');
  put('#v-ip',safe(ipHtml,'danh sách IP'));
}

/* ── banner / trạng thái kết nối ── */
function bannerHtml(){
  if(!ACC)return '';
  const out=[];
  if(cur==='ip'){if(ipErr&&IPD&&IPD.ok)out.push(['bad',`Không cập nhật được danh sách IP: ${esc(ipErr)} — đang hiển thị dữ liệu cũ (${ago(Date.now()-ipT)} trước).`])}
  else{
    const st=S[cur],g=GM[cur];
    if(st.err&&st.d)out.push(['bad',`Bàn ${esc(g.n)} chưa cập nhật được: ${esc(st.err)}. Đang hiển thị dữ liệu cũ (${ago(Date.now()-st.t)} trước) — panel tự thử lại.`]);
    else if(st.d&&st.d.stale)out.push(['warn',`Nguồn dữ liệu của bàn ${esc(g.n)} đang lỗi${st.d.loi?': '+esc(st.d.loi):''} — dự đoán có thể chưa phải mới nhất.`]);
  }
  return out.map(([c,m])=>`<div class="bnr ${c}"><span>${c==='bad'?'📡':'⚠️'}</span><span>${m}</span><button data-retry="1">Thử lại</button></div>`).join('');
}
function liveTick(){
  const el=$('#live');if(!el)return;
  let cls='idle',txt='Đang chờ duyệt…',off=false;
  if(ACC){
    const st=cur==='ip'?null:S[cur];
    if(cur==='ip'){cls=ipErr&&!(IPD&&IPD.ok)?'bad':'';txt=ipT?'Cập nhật '+ago(Date.now()-ipT)+' trước':'Đang tải…'}
    else if(st.d){const bad=st.fails>=2||(st.err&&Date.now()-st.t>20000);cls=bad?'bad':'';txt=bad?'Mất kết nối · dữ liệu cũ '+ago(Date.now()-st.t):'LIVE · cập nhật '+ago(Date.now()-st.t)+' trước';off=!!st.d.off_server}
    else if(st.err){cls='bad';txt='Chưa nhận được dữ liệu'}
    else{cls='idle';txt='Đang kết nối…'}
  }
  const html=`<i></i><span>${esc(txt)}</span>${off?'<em title="Off server đang BẬT: tool ngoài không nhận được dự đoán, chỉ panel này còn nhận">OFF SERVER</em>':''}`;
  if(el.className!=='live '+cls)el.className='live '+cls;
  if(LAST.get(el)!==html){LAST.set(el,html);el.innerHTML=html}
  put('#banner',bannerHtml());
}
function draw(){
  const g=cur!=='ip'?GM[cur]:null,d=g?S[cur].d:null;
  document.body.classList.toggle('ft',!!d&&d.du_doan==='TÀI');document.body.classList.toggle('fx',!!d&&d.du_doan==='XỈU');
  put('#nav',safe(()=>navHtml(false),'menu'));put('#dock',safe(()=>navHtml(true),'menu'));
  if(cur==='ip')safe(drawIp,'IP');else safe(drawGame,'bàn');
  const t=d?`${d.du_doan} · #${d.phien} · ${g.n} — SUNVIW`:'SUNVIW · Radar Tài Xỉu';if(document.title!==t)document.title=t;
  put('#sfoot',`Thiết bị <b>${esc(DEVID.slice(0,6))}…${esc(DEVID.slice(-4))}</b>${d&&d.cap_nhat?`<br>Nguồn cập nhật <b>${esc(d.cap_nhat)}</b>`:''}`);
  liveTick();
}

/* ── tải dữ liệu: mỗi bàn một vòng riêng ── */
async function pull(k,full,force){
  const st=S[k],g=GM[k];if(!g||banned)return;
  if(st.busy&&!force&&!(full&&!st.full))return;                 /* đang bận: bỏ qua, trừ khi cần nâng lên bản đầy đủ */
  if(st.ctl){st.ctl.__sup=1;st.ctl.abort()}
  const my=++st.seq,ctl=new AbortController();st.ctl=ctl;st.busy=true;st.full=!!full;
  try{
    const r=await api(g.u+(full?`?hist=${N}&detail=1`:'?hist=0'),{ctl});
    if(my!==st.seq)return;
    const j=r.j;
    if(j&&j.ok!==false&&j.du_doan!=null){st.d=j;st.t=Date.now();st.err='';st.fails=0}
    else{st.err=(j&&j.loi)||('Server trả về HTTP '+r.status);st.fails++}
  }catch(e){
    if(my!==st.seq)return;
    st.err=ctl.__to?`Server phản hồi quá chậm (>${TMO/1000}s)`:'Mất kết nối tới server';st.fails++;
  }finally{if(my===st.seq){st.busy=false;st.ctl=null;paint()}}
}
async function pullIp(){
  if(ipBusy||banned)return;ipBusy=true;
  try{
    const k=ls.g('ak')||'';
    const r=await api('/api/ips',{headers:k?{'X-Admin-Key':k}:{}});
    if(r.j){IPD=r.j;ipT=Date.now();ipErr=''}
    else{ipErr='Server trả về HTTP '+r.status;if(!(IPD&&IPD.ok))IPD={ok:false,loi:ipErr}}
  }catch(e){ipErr=e&&e.name==='AbortError'?'Server phản hồi quá chậm':'Mất kết nối tới server';if(!(IPD&&IPD.ok))IPD={ok:false,loi:ipErr}}
  finally{ipBusy=false;paint()}
}
async function loop(k,first){
  if(banned)return;
  if(ACC&&!document.hidden)await pull(k,k===cur);
  setTimeout(()=>loop(k),k===cur?POLL:POLL_BG);
}
async function loopIp(){
  if(banned)return;
  if(ACC&&!document.hidden&&(cur==='ip'||!ipT))await pullIp();
  setTimeout(loopIp,5000);
}
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&ACC){cur==='ip'?pullIp():pull(cur,true)}});

/* ── cổng duyệt thiết bị (HWID) ── */
function gate(st,msg){
  const key=st+'|'+(msg||''),el=$('#gate');
  if(GV===key&&el.classList.contains('on'))return;GV=key;
  const T={
    checking:['<div class="spin" style="width:34px;height:34px"></div>','scan','Đang kiểm tra quyền truy cập…','Chờ một chút, panel đang hỏi server về thiết bị này.'],
    pending:['<div class="spin" style="width:34px;height:34px"></div>','scan','Đang chờ admin duyệt','Yêu cầu truy cập của thiết bị này đã được gửi tới admin chính. Trang sẽ tự mở ngay khi được duyệt — không cần nhập key, không cần tải lại.'],
    denied:['⛔','','Thiết bị bị từ chối','Admin chính đã từ chối thiết bị này. Hãy liên hệ admin nếu cần được cấp quyền.'],
    limit:['⚠️','','Quá nhiều yêu cầu chờ duyệt','Mạng này đã gửi quá nhiều yêu cầu. Hãy nhờ admin xử lý bớt rồi bấm kiểm tra lại.'],
    error:['📡','','Chưa kết nối được',msg||'Đang thử lại…']}[st]||['⚠️','','Chưa vào được',msg||''];
  $('#gbox').innerHTML=`<div class="gic ${T[1]}">${T[0]}</div><h2>${esc(T[2])}</h2><p>${esc(T[3])}</p><div class="gcode">Mã thiết bị<b>${esc(DEVID.slice(0,8))}…${esc(DEVID.slice(-4))}</b></div><button class="btn pri" id="gre" type="button">Kiểm tra lại</button>`;
  el.classList.add('on');
}
function fake404(){   /* thiết bị / IP bị ban → giả như trang không tồn tại (đúng ý server) */
  banned=true;ACC=false;
  document.open();
  document.write('<!doctype html>\n<html lang=en>\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>\n');
  document.close();
}
async function access(){
  if(banned||accBusy)return;accBusy=true;
  try{
    const r=await api('/api/panel/status',{timeout:8000});
    if(r.status===404){fake404();return}
    const j=r.j||{};accFails=0;
    if(j.status==='approved'){
      if(!ACC){ACC=true;GV='';$('#gate').classList.remove('on');pull(cur,true,true);if(cur==='ip')pullIp()}
      return;
    }
    ACC=false;gate(['pending','denied','limit'].includes(j.status)?j.status:'error',j.loi||(r.j?'':'Server trả về HTTP '+r.status));
  }catch(e){
    accFails++;
    if(ACC)return;                                    /* đã vào rồi: rớt mạng thoáng qua KHÔNG khóa lại panel (bản cũ khóa luôn) */
    gate('error',ctlMsg(e));
  }finally{accBusy=false;paint()}
}
const ctlMsg=e=>e&&e.name==='AbortError'?'Server phản hồi quá chậm — đang thử lại…':'Mất kết nối tới server — đang thử lại…';

/* ── hộp thoại + thông báo ── */
function toast(m,bad){const t=document.createElement('div');t.className='toast'+(bad?' bad':'');t.textContent=m;$('#toasts').appendChild(t);setTimeout(()=>{t.style.transition='opacity .3s';t.style.opacity='0';setTimeout(()=>t.remove(),320)},bad?6500:4800)}
function ask(o){
  return new Promise(res=>{
    const m=$('#modal');
    m.innerHTML=`<div class="mbox" role="dialog" aria-modal="true"><h3>${esc(o.title)}</h3><p>${esc(o.body)}</p>${o.type?`<input class="mi" id="mi" type="text" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="Gõ ${esc(o.type)} để xác nhận" aria-label="Gõ ${esc(o.type)} để xác nhận">`:''}<div class="row"><button class="btn" data-mo="0">Hủy</button><button class="btn ${o.danger?'dng solid':'pri'}" data-mo="1"${o.type?' disabled':''}>${esc(o.ok||'Xác nhận')}</button></div></div>`;
    m.hidden=false;
    const done=v=>{m.hidden=true;m.innerHTML='';m.onclick=null;document.removeEventListener('keydown',kd);res(v)};
    const kd=e=>{if(e.key==='Escape')done(false)};
    document.addEventListener('keydown',kd);
    m.onclick=e=>{const b=e.target.closest('[data-mo]');if(b){if(b.dataset.mo==='1'&&b.disabled)return;done(b.dataset.mo==='1')}else if(e.target===m)done(false)};
    const b=m.querySelector('[data-mo="1"]'),inp=m.querySelector('#mi');
    if(inp&&b){inp.oninput=()=>{b.disabled=inp.value.trim().toUpperCase()!==String(o.type).toUpperCase()};inp.onkeydown=e=>{if(e.key==='Enter'&&!b.disabled)done(true)};inp.focus()}
    else if(b)b.focus();
  });
}
async function act(kind){
  const g=GM[cur];if(!g||ACTB)return;
  const all=TS==='all',gg=all?'all':g.g,who=all?'CẢ 5 BÀN':g.n;
  const GN={};G.forEach(x=>GN[x.g]=x.n);const nm=k=>esc(GN[k]||k);
  const run=async(url,json,tm)=>{ACTB=kind;paint();try{return await api(url,{method:'POST',json,timeout:tm})}finally{ACTB='';paint()}};
  const fin=(title,lines,bad)=>{
    TRES={title,lines:lines||[],bad:!!bad,time:new Date().toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit',second:'2-digit'})};
    toast(title+(lines&&lines.length?'\n'+lines.map(l=>l.replace(/<[^>]+>/g,'')).join('\n'):''),bad);paint();
  };
  const bad=(r,def)=>{if(r.status!==401)fin((r.j&&r.j.loi)||def,[],1)};
  try{
    if(kind==='clear'){
      if(!await ask({title:'Xóa lịch sử '+who+'?',body:'Chỉ ẩn danh sách đúng/sai và số liệu thống kê đang hiển thị (từ nay đếm lại từ đầu).\nKhông xóa dữ liệu nào khác và không ảnh hưởng các logic / WR dùng để dự đoán.',ok:'Xóa lịch sử'}))return;
      const r=await run('/api/history/clear',{game:gg},30000);
      if(!r.j||r.j.ok===false){bad(r,'Không xóa được lịch sử');return}
      const da=r.j.da_xoa||{};
      fin('Đã xóa lịch sử '+who+'.',Object.keys(da).map(k=>`<b>${nm(k)}</b>: ẩn ${esc(da[k])} ván`));
    }else if(kind==='regrade'){
      if(!await ask({title:'Tính lại đúng/sai của '+who+'?',body:'Lịch sử vẫn được giữ nguyên. Tool chấm lại toàn bộ ván đã lưu bằng ngưỡng / bẻ / WR đang chạy (chỉ vài giây), không cần đợi ván mới.',ok:'Tính lại'}))return;
      const r=await run('/api/history/regrade',{game:gg},90000);
      if(!r.j||r.j.ok===false){bad(r,'Không tính lại được');return}
      const kq=r.j.ket_qua||{},ks=Object.keys(kq);
      fin('Đã chấm lại theo config hiện tại.',ks.map(k=>{const x=kq[k]||{};
        if(!x.truoc||!x.sau)return `<b>${nm(k)}</b>: xong`;
        return `<b>${nm(k)}</b>: ${esc(x.so_van)} ván · đổi dự đoán ${esc(x.doi_du_doan)} · đúng/sai ${esc(x.truoc.dung)}/${esc(x.truoc.tong)} → ${esc(x.sau.dung)}/${esc(x.sau.tong)}`}));
    }else if(kind==='wipe'){
      if(!await ask({title:'XÓA SẠCH DATA '+who+'?',body:'Xóa thật toàn bộ lịch sử xúc xắc + các ván đã chấm của '+(all?'cả 5 bàn':'bàn này')+'. WR / AF / dự đoán sẽ bắt đầu lại từ đầu.\nKHÔNG hoàn tác được.',ok:'Xóa vĩnh viễn',danger:true,type:'XOA'}))return;
      const r=await run('/api/history/wipe',{game:gg,confirm:true},60000);
      if(!r.j||r.j.ok===false){bad(r,'Không xóa được data');return}
      const da=r.j.da_xoa||{};
      fin('Đã xóa sạch data '+who+'. Tool sẽ quét lại từ đầu.',Object.keys(da).map(k=>{const x=da[k];
        return `<b>${nm(k)}</b>: đã xóa`+(x&&typeof x==='object'&&x.phien_da_xoa!=null?` ${esc(x.phien_da_xoa)} phiên`:'')}));
    }
  }catch(e){fin(e&&e.name==='AbortError'?'Server phản hồi quá chậm — thao tác có thể vẫn đang chạy, hãy làm mới sau ít giây.':'Mất kết nối tới server',[],1);return}
  if(all)G.forEach(x=>pull(x.k,true,true));else pull(cur,true,true);
}

/* ── sự kiện ── */
function go(k){if(k===cur)return;cur=k;ls.s('g',k);shell='';paint();if(k==='ip')pullIp();else pull(k,true)}
function setN(v){N=clampN(v);ls.s('n',N);const a=document.activeElement;if(a&&a.id==='n')a.blur();paint();pull(cur,true,true)}
document.addEventListener('click',e=>{
  const t=e.target;if(!t||!t.closest)return;let b;
  if((b=t.closest('[data-g]'))){go(b.dataset.g);return}
  if((b=t.closest('[data-pane]'))){pane=b.dataset.pane;ls.s('pane',pane);pop($('#v-body'));paint();return}
  if((b=t.closest('[data-m]'))){MF=(b.dataset.m===MF)?'':b.dataset.m;ls.s('mf',MF);paint();return}
  if((b=t.closest('[data-n]'))){setN(b.dataset.n);return}
  if((b=t.closest('[data-ts]'))){TS=b.dataset.ts==='all'?'all':'one';ls.s('ts',TS);paint();return}
  if((b=t.closest('[data-act]'))){act(b.dataset.act);return}
  if(t.closest('[data-retry]')){cur==='ip'?pullIp():pull(cur,true,true);return}
  if(t.closest('#akb')){const v=$('#ak');ls.s('ak',v?v.value.trim():'');pullIp();return}
  if(t.closest('#gre')){GV='';gate('checking');access()}
});
document.addEventListener('change',e=>{if(e.target&&e.target.id==='n')setN(e.target.value)});
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target){if(e.target.id==='n')setN(e.target.value);else if(e.target.id==='ak'){const v=e.target.value.trim();ls.s('ak',v);pullIp()}}});

/* ── khởi động: vẽ khung NGAY, rồi mới hỏi server ── */
draw();
access();setInterval(access,3000);setInterval(liveTick,1000);
[cur,...G.map(x=>x.k).filter(k=>k!==cur&&k!=='ip')].filter(k=>GM[k]).forEach((k,i)=>setTimeout(()=>loop(k),600+i*350));
loopIp();
</script></body></html>
"""


# ─── THEO DÕI IP TRUY CẬP (tab "IP" của panel) — xem khối CONFIG IP ──────────
_ip_lock = threading.Lock()
_ip_store = {}              # ip -> {"ip","first","last","hits","by":{loại: số request},"ua"}
_ip_state = {"loaded": False, "saved": 0.0, "dirty": False}


def ip_kind(path):
    """Loại request được tính vào danh sách IP (None = không tính: /health, /, /api/ips ...)."""
    if path in ("/api/predictsun", "/api/predict"):
        return "sun"
    if path in ("/api/predicthittxthuong", "/api/predicthittxmd5", "/api/predictlcmd5", "/api/predictlchu", "/api/predicttele68txmd5"):
        return "hit"
    if path == "/api/html":
        return "panel"
    return None


def _fmt_ts(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def _ip_load_locked():
    """Nạp danh sách IP đã lưu (1 lần). Gọi trong _ip_lock."""
    if _ip_state["loaded"]:
        return
    _ip_state["loaded"] = True
    try:
        with open(IP_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:  # noqa: BLE001
        return
    for r in data if isinstance(data, list) else []:
        try:
            ip = str(r.get("ip", ""))
            if ip != "unknown":
                ip = str(ipaddress.ip_address(ip))
            by = {str(k): int(v) for k, v in (r.get("by") or {}).items()}
            _ip_store[ip] = {"ip": ip, "first": float(r["first"]), "last": float(r["last"]),
                             "hits": int(r.get("hits", 0)), "by": by, "ua": str(r.get("ua", ""))[:120]}
        except Exception:  # noqa: BLE001
            continue


def _ip_save_locked(now):
    """Ghi danh sách IP ra file (atomic). Gọi trong _ip_lock."""
    try:
        tmp = IP_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(sorted(_ip_store.values(), key=lambda r: r["first"]), f, ensure_ascii=False)
        os.replace(tmp, IP_PATH)
        _ip_state["saved"] = now
        _ip_state["dirty"] = False
    except Exception:  # noqa: BLE001
        pass


def ip_flush():
    """Ghi nốt các request chưa kịp lưu (gọi khi tắt server) để không mất tối đa IP_SAVE_SEC giây dữ liệu."""
    with _ip_lock:
        if _ip_state["loaded"] and _ip_state["dirty"]:
            _ip_save_locked(time.time())


atexit.register(ip_flush)


def ip_touch(ip, kind, ua=""):
    """Ghi 1 request của `ip` (loại `kind`). IP mới -> ghi file ngay; IP cũ -> ghi file tối đa mỗi IP_SAVE_SEC giây."""
    now = time.time()
    ua = re.sub(r"[\x00-\x1f\x7f]", " ", str(ua or ""))[:120]
    with _ip_lock:
        _ip_load_locked()
        r = _ip_store.get(ip)
        is_new = r is None
        if is_new:
            r = _ip_store[ip] = {"ip": ip, "first": now, "last": now, "hits": 0, "by": {}, "ua": ""}
            while len(_ip_store) > IP_KEEP:                       # đầy -> bỏ IP lâu không thấy nhất
                del _ip_store[min(_ip_store, key=lambda k: _ip_store[k]["last"])]
        r["last"] = now
        r["hits"] += 1
        r["by"][kind] = r["by"].get(kind, 0) + 1
        if ua:
            r["ua"] = ua
        _ip_state["dirty"] = True
        if is_new or now - _ip_state["saved"] >= IP_SAVE_SEC:
            _ip_save_locked(now)


def ip_snapshot(me=None):
    """Danh sách IP cho /api/ips: đang dùng trước, rồi tới các IP đã từng dùng. Trong mỗi nhóm sắp theo LẦN ĐẦU XUẤT HIỆN (mới xuất hiện nằm trên) — thứ tự này không đổi theo
    mỗi request nên danh sách trên panel KHÔNG bị xáo / nhảy hàng mỗi lần tool gọi API (trước đây sắp theo \"request gần nhất\" nên hàng nhảy liên tục)."""
    now = time.time()
    with _ip_lock:
        _ip_load_locked()
        rows = [dict(r, by=dict(r["by"])) for r in _ip_store.values()]
    rows.sort(key=lambda r: (-r["first"], r["ip"]))
    out = []
    for r in rows:
        age = max(0.0, now - r["last"])
        out.append({"ip": r["ip"], "dang_dung": age <= IP_ACTIVE_SEC, "lan_dau": _fmt_ts(r["first"]), "gan_nhat": _fmt_ts(r["last"]),
                    "truoc_giay": int(age), "so_request": r["hits"], "theo_loai": r["by"], "ua": r.get("ua", ""), "la_ban": r["ip"] == me})
    out.sort(key=lambda x: not x["dang_dung"])           # sort ổn định -> chỉ tách nhóm đang dùng / đã dùng, giữ nguyên thứ tự lần đầu xuất hiện
    return {"ok": True, "tong": len(out), "dang_dung": sum(1 for x in out if x["dang_dung"]),
            "cua_so_giay": IP_ACTIVE_SEC, "ban": me, "ips": out}


def ip_health():
    with _ip_lock:
        _ip_load_locked()
        n = len(_ip_store)
    return dict(bat=IP_TRACK_ENABLED, tong=n, active_sec=IP_ACTIVE_SEC, khoa=bool(IP_ADMIN_KEY), tin_proxy=IP_TRUST_PROXY)


# ─── FLASK ────────────────────────────────────────────────────────────────
from flask import Flask, Response, abort, request  # noqa: E402
from flask import g as flask_g  # noqa: E402  (đặt tên khác vì nhiều hàm dùng biến cục bộ `g`)

os.umask(0o077)                                    # file dữ liệu (key / thiết bị / phiên) chỉ chủ tiến trình đọc được
app = Flask(__name__, static_folder=None)           # KHÔNG mở route /static -> không ai kéo file qua đường tĩnh
app.config.update(PROPAGATE_EXCEPTIONS=False, MAX_CONTENT_LENGTH=256 * 1024)   # lỗi không bay ra ngoài · body tối đa 256 KB


def _json(obj, status=200):
    return Response(json.dumps(obj, ensure_ascii=False), status=status,
                    content_type="application/json; charset=utf-8")


import collections as _collections  # noqa: E402
from werkzeug.exceptions import HTTPException as _HTTPExc  # noqa: E402

# ═══════════════════════════════════════════════════════════════════════════
#  🛡  LỚP BẢO MẬT (SEC)  —  env chỉnh được
# ═══════════════════════════════════════════════════════════════════════════
#   SUNVIW_PROXY_HOPS   số proxy tin cậy đứng TRƯỚC app (mặc định 1 = Railway). IP thật = phần tử thứ N TÍNH TỪ CUỐI của X-Forwarded-For
#                       (phần đầu do CLIENT tự điền nên KHÔNG tin được). Nếu thêm Cloudflare trước Railway -> đặt 2.
#   SUNVIW_IP_HEADER    (tuỳ chọn) header IP do proxy ĐÁNG TIN ghi đè, vd CF-Connecting-IP — có đặt thì dùng nó thay cho X-Forwarded-For.
#   SUNVIW_IP_PROXY=0   KHÔNG đứng sau proxy (chạy trực tiếp ra internet) -> chỉ dùng remote_addr.
#   SUNVIW_RATE_TOOL    request / phút / KEY cho endpoint dự đoán (mặc định 90) · SUNVIW_RATE_IP / phút / IP (300) · SUNVIW_RATE_BADKEY key sai / phút / IP (20) · SUNVIW_RATE_PANEL / phút / thiết bị panel (900)
#   SUNVIW_TOOL_HIST_MAX  ?hist=N tối đa cho tool khách (mặc định 60); panel / admin vẫn dùng HIST_MAX.
#   SUNVIW_DEV_TOKEN_STRICT=1  thiết bị panel ĐÃ DUYỆT từ trước bản vá mà chưa có token thì KHÔNG còn được vào (phải gỡ + duyệt lại). Mặc định 0 = tự gắn token ở lần mở panel đầu tiên.
IP_PROXY_HOPS = max(1, _env_num("SUNVIW_PROXY_HOPS", 1, int))
RATE_TOOL_KEY = _env_num("SUNVIW_RATE_TOOL", 90, int)
RATE_IP = _env_num("SUNVIW_RATE_IP", 300, int)
RATE_BADKEY = _env_num("SUNVIW_RATE_BADKEY", 20, int)
RATE_PANEL = _env_num("SUNVIW_RATE_PANEL", 900, int)
TOOL_HIST_MAX = _env_num("SUNVIW_TOOL_HIST_MAX", 60, int)
DEV_TOKEN_STRICT = _env_bool("SUNVIW_DEV_TOKEN_STRICT", True)
DEV_COOKIE = "sv_dt"                                  # cookie HttpOnly chứa token thiết bị do SERVER cấp (JS không đọc được)

_rate_hits = {}
_rate_lock = threading.Lock()


def _rate_ok(bucket, limit, window=60.0):
    """Cửa sổ trượt: True nếu `bucket` còn dưới `limit` lần trong `window` giây (và ghi nhận 1 lần). limit <= 0 = không giới hạn."""
    if limit <= 0:
        return True
    now = time.time()
    with _rate_lock:
        if len(_rate_hits) > 20000:
            cut_t = now - 300
            for b in [b for b, dq in _rate_hits.items() if not dq or dq[-1] < cut_t]:
                del _rate_hits[b]
            if len(_rate_hits) > 20000:
                _rate_hits.clear()
        dq = _rate_hits.get(bucket)
        if dq is None:
            dq = _rate_hits[bucket] = _collections.deque()
        lim = now - window
        while dq and dq[0] <= lim:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True


def _too_many(msg="qua nhieu request, thu lai sau it giay", sec=20):
    r = _json({"ok": False, "rate_limited": True, "loi": msg}, 429)
    r.headers["Retry-After"] = str(sec)
    return r


def _err500(e, where=""):
    """Lỗi nội bộ: chi tiết chỉ ghi log server, KHÔNG trả ra ngoài (tên lỗi / đường dẫn / URL upstream đều không lộ)."""
    try:
        import traceback
        print(f"[ERR] {where} {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
    except Exception:  # noqa: BLE001
        pass
    return _json({"ok": False, "loi": "loi may chu"}, 500)


def _is_panel():
    """Request này đến từ panel đã duyệt / admin chính (được xem chi tiết) — cờ do _gate_key đặt."""
    return bool(getattr(flask_g, "panel", False))


def _pub_err(err, dflt):
    """Chuỗi lỗi chỉ cho panel/admin xem; tool khách chỉ nhận câu chung (lỗi gốc có thể chứa URL upstream / tên exception)."""
    return (err or dflt) if _is_panel() else dflt


_CORS_EXACT = {"/", "/health", "/api/key/check", "/api/predictsun", "/api/predict", "/api/predicthittxthuong", "/api/predicthittxmd5",
               "/api/predictlcmd5", "/api/predictlchu", "/api/predicttele68txmd5"}
_NOFRAME_PREFIX = ("/api/admin", "/tool/autocuoc", "/api/autocuoc", "/autocuoc")


def _is_https():
    return request.is_secure or request.headers.get("X-Forwarded-Proto", "").split(",")[-1].strip().lower() == "https"


@app.after_request
def _cors(resp):
    p = request.path
    if p in _CORS_EXACT:                                # CORS CHỈ cho endpoint dự đoán / key-check (xác thực bằng header key, không bằng cookie). Admin / panel / history / ips: KHÔNG mở CORS
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = request.headers.get("Access-Control-Request-Headers") or "Content-Type, X-User-Key, X-HWID, X-HWID-ALT, X-HWID-FRESH, X-Device-Token"
        resp.headers["Access-Control-Max-Age"] = "600"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["Server"] = "web"                      # không lộ Werkzeug / gunicorn / phiên bản Python
    if "Content-Security-Policy" not in resp.headers:
        resp.headers["Content-Security-Policy"] = "frame-ancestors 'none'; base-uri 'none'; object-src 'none'; form-action 'self'"
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Resource-Policy"] = "same-origin" if p not in _CORS_EXACT else "cross-origin"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    if _is_https():
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if p.startswith(_NOFRAME_PREFIX):
        resp.headers["X-Frame-Options"] = "DENY"        # chống clickjacking trang admin / auto cược
    tok = getattr(flask_g, "_new_dev_tok", None)
    if tok:                                             # cấp token thiết bị (xem _panel_access)
        resp.set_cookie(DEV_COOKIE, tok, max_age=2 * 365 * 86400, httponly=True, samesite="Lax", secure=_is_https(), path="/")
    return resp


def _ip_parse(v):
    v = (v or "").split(",")[0].strip()
    if v.startswith("["):
        v = v[1:].split("]")[0]
    elif v.count(":") == 1:                             # IPv4:port
        v = v.split(":")[0]
    if not v:
        return None
    try:
        return str(ipaddress.ip_address(v))
    except ValueError:
        return None


def client_ip():
    """IP của client. Sau proxy: lấy phần tử thứ IP_PROXY_HOPS TÍNH TỪ CUỐI của X-Forwarded-For (proxy tin cậy là bên THÊM vào cuối; phần đầu client tự điền được -> không tin).
    SUNVIW_IP_HEADER đặt thì dùng header đó (proxy phải ghi đè). Không hợp lệ -> IP kết nối trực tiếp (remote_addr)."""
    if IP_TRUST_PROXY:
        if IP_HEADER:
            v = _ip_parse(request.headers.get(IP_HEADER, ""))
            if v:
                return v
        else:
            parts = [x.strip() for x in request.headers.get("X-Forwarded-For", "").split(",") if x.strip()]
            if len(parts) >= IP_PROXY_HOPS:
                v = _ip_parse(parts[-IP_PROXY_HOPS])
                if v:
                    return v
    return _ip_parse(request.remote_addr or "") or "unknown"


# ─ chặn máy quét: dò .env / .git / *.py / wp-admin... hoặc dồn dập 404 -> tạm khoá IP (trả 404 như web không tồn tại) ─
PG_LIMIT, PG_WINDOW, PG_BLOCK = 10, 600.0, 900.0        # >= 10 điểm trong 10 phút -> khoá 15 phút
_pg = {}
_pg_lock = threading.Lock()
_PROBE_RE = re.compile(r"(?i)(\.env|\.git|\.svn|\.htaccess|\.ds_store|\.py($|[/?;])|\.pyc|\.bak|\.old|\.swp|\.sql|\.zip|\.tar|\.gz|\.log($|[/?;])|wp-(admin|login|content|includes)|phpmyadmin"
                       r"|/console|/actuator|/server-status|/__debug__|/debug|/static/|/proc/|/etc/passwd|\.\./|%2e%2e|%252e|\\x00|%00)")


def _pg_strike(ip, pts):
    if not ip or ip == "unknown":
        return
    now = time.time()
    with _pg_lock:
        if len(_pg) > 5000:
            for k in [k for k, v in _pg.items() if v[2] < now and now - v[1] > PG_WINDOW]:
                del _pg[k]
        r = _pg.get(ip)
        if r is None or (r[2] < now and now - r[1] > PG_WINDOW):
            r = _pg[ip] = [0, now, 0.0]
        r[0] += pts
        if r[0] >= PG_LIMIT and r[2] < now:
            r[2] = now + PG_BLOCK
            print(f"[SEC] khoa IP {ip} {PG_BLOCK:.0f}s (quet duong dan / loi lien tuc)", file=sys.stderr)


def _pg_blocked(ip):
    with _pg_lock:
        r = _pg.get(ip)
        return bool(r and r[2] > time.time())


@app.before_request
def _probe_guard():
    ip = client_ip()
    if _pg_blocked(ip):
        abort(404)
    if _PROBE_RE.search(request.path) or _PROBE_RE.search(request.query_string.decode("latin-1", "ignore")[:300]):
        _pg_strike(ip, 4)
        abort(404)
    return None


@app.before_request
def _csrf_origin():
    """POST / PUT / DELETE có Origin khác host (trang web lạ gọi chéo) -> 403, trừ các endpoint công khai dùng key (có CORS)."""
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and request.path not in _CORS_EXACT:
        o = request.headers.get("Origin", "")
        if o and o != "null":
            from urllib.parse import urlsplit
            if urlsplit(o).netloc.lower() != request.host.lower():
                _audit("csrf_block", origin=o[:80])
                return _json({"ok": False, "loi": "forbidden"}, 403)
        elif o == "null":
            return _json({"ok": False, "loi": "forbidden"}, 403)
    return None


@app.errorhandler(Exception)
def _on_exception(e):
    if isinstance(e, _HTTPExc):
        if e.code == 404 and request.path not in ("/api/html", "/api/html/ui", "/api/panel/status"):     # 2 đường này trả 404 có chủ ý cho thiết bị bị ban -> không tính là dò quét
            _pg_strike(client_ip(), 1)
        if e.code == 413:
            return _json({"ok": False, "loi": "payload qua lon"}, 413)
        return e
    return _err500(e, request.path)


@app.before_request
def _track_ip():
    """Ghi IP mọi request tới API / ws / panel. Không bao giờ được làm hỏng request."""
    if not IP_TRACK_ENABLED or request.method == "OPTIONS":
        return None
    try:
        kind = ip_kind(request.path)
        if kind:
            ip_touch(client_ip(), kind, request.headers.get("User-Agent", ""))
    except Exception:  # noqa: BLE001
        pass
    return None


# ─── KEY NGƯỜI DÙNG + TRANG ADMIN (/api/admin) ────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════
#  🔑  CONFIG KEY / ADMIN  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Trang quản trị: GET /api/admin  (KHÔNG hiện ở trang chủ "/").  CHỈ MỘT Ô NHẬP KEY — server tự phân loại:
#     · Admin chính : nhập MẬT KHẨU admin chính vào chính ô đó (kiểm tra Ở SERVER, trình duyệt / view-source KHÔNG chứa mật khẩu). Tạo key admin phụ + key người dùng (chọn số thiết bị tối đa cho từng key),
#                     xóa key (tích chọn nhiều key rồi xóa một lượt), xem mọi key (ai tạo, hạn, số thiết bị đang gắn, LẦN DÙNG GẦN NHẤT, từng thiết bị) và RESET / GỠ THIẾT BỊ.
#     · Admin phụ   : nhập key admin phụ (do admin chính tạo). Key chưa ai dùng -> nhập username (vd. Dark) -> key gắn với username đó VÀ gắn với HWID của thiết bị đăng nhập đầu tiên.
#                     Key dùng được tối đa N thiết bị (N do admin chính chọn lúc tạo key): máy thứ N+1 bị chặn cho tới khi admin chính reset / gỡ thiết bị.
#                     Admin phụ tạo / xóa KEY NGƯỜI DÙNG (chỉ key mình tạo; cũng chọn được số thiết bị tối đa, tích chọn xóa nhiều key, reset thiết bị key của mình) với hạn 1 ngày · 3 ngày · 1 tuần · 1 tháng · 2 tháng · 3 tháng.
#     · Key người dùng / key không tồn tại -> trang admin báo rõ là key người dùng (không phải admin) hoặc không tìm thấy key.
#   Người dùng nhập KEY NGƯỜI DÙNG ở panel /api/html (hoặc tool gọi POST /api/key/check {"key": "...", "hwid": "..."}).
#   HWID = mã thiết bị. KHÔNG dùng IP / mạng để chặn: đổi Wi-Fi <-> 4G <-> VPN, đổi IP thoải mái, cùng máy vẫn dùng bình thường (server chỉ GHI IP để admin xem). Chỉ MÁY KHÁC mới bị chặn khi key đã đủ thiết bị.
#   Panel tự tạo mã: ưu tiên mã đã lưu (localStorage + cookie dự phòng 2 năm, mất 1 trong 2 thì tự phục hồi từ cái còn lại); chưa có thì tính từ dấu vân tay PHẦN CỨNG ổn định (nền tảng, số nhân CPU, RAM,
#   cảm ứng, kích thước màn hình không phân biệt xoay ngang/dọc, GPU) — không dùng UA / ngôn ngữ / múi giờ / zoom / canvas vì các thứ này tự đổi, nên xoá dữ liệu trình duyệt rồi vào lại vẫn ra ĐÚNG mã cũ.
#   Panel còn gửi mã phụ của chính máy đó (header X-HWID-ALT; X-HWID-FRESH: 1 khi máy vừa mất bộ nhớ) -> server nhớ mã phụ cho từng thiết bị (_dev_learn) và tự nhận lại máy cũ khi công thức / bộ nhớ đổi.
#   Giới hạn không tránh được: trình duyệt không đọc được số serial phần cứng, nên 2 máy CÙNG ĐỜI y hệt nhau (vd. 2 iPhone cùng model) mà đều mới xoá sạch dữ liệu có thể ra cùng mã. Chặn chia sẻ key thông thường, không chống được người cố tình giả mạo.
#   Tool tự viết: gửi header X-HWID (hoặc ?hwid= / body {"hwid"}) = mã MÁY THẬT của tool (8-64 ký tự A-Z a-z 0-9 _ -), nên băm từ mã cài đặt hệ điều hành (Windows: HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid ·
#   Linux: /etc/machine-id · macOS: IOPlatformUUID) và TUYỆT ĐỐI KHÔNG dùng MAC / IP / tên mạng / SSID (các thứ này đổi khi đổi mạng hoặc cắm card mới -> chính là lỗi "đổi mạng là mất key").
#   Khi KEY_GATE_API bật: /api/predictsun · /api/predicthittxthuong · /api/predicthittxmd5 · /api/ips · /api/history/clear đòi key hợp lệ (header X-User-Key hoặc ?key=; riêng /api/ips chỉ nhận header).
#
#   🎮 KEY THEO GAME: mỗi KEY NGƯỜI DÙNG chỉ thuộc ĐÚNG 1 GAME, chọn lúc tạo ở trang admin (không có key gộp chung):
#       · key game SUN (tiền tố SUN-)  -> chỉ gọi được /api/predictsun (+ /api/predict tên cũ)
#       · key game HIT (tiền tố HIT-)  -> chỉ gọi được /api/predicthittxthuong + /api/predicthittxmd5 (cả 2 bàn Hit)
#       · dùng key sai game -> HTTP 403 {"sai_game":true,"game_can":"sun"|"hit"}; KHÔNG gắn thiết bị khi sai game. Panel /api/html tự chỉ hiện tab đúng game của key.
#       · /api/ips và /api/history/clear nhận mọi key hợp lệ; riêng xóa lịch sử chỉ xóa được game mà key thuộc về.
#       · POST /api/key/check trả thêm "game" của key; truyền {"game":"sun"|"hit"} (hoặc ?game=) để kiểm tra key có đúng game đó không.
#   KEY_LEGACY_GAME: key tạo TRƯỚC bản có chia game (không có trường game) -> "all" = vẫn dùng được mọi game (mặc định, không khóa ai) · "sun" / "hit" = gán luôn cho game đó (env SUNVIW_KEY_LEGACY_GAME).
#
#   SUNVIW_MAIN_PASS   (KHUYẾN NGHỊ) mật khẩu admin chính đặt ở biến môi trường Railway -> trong code không còn dấu vết mật khẩu nào. Không đặt = dùng hash mặc định trong code.
#   SUNVIW_KEYS_PATH   file lưu key (mặc định <DATA_DIR>/sunviw_keys.json; DATA_DIR = Volume Railway nếu có, không thì /tmp). Railway: PHẢI gắn Volume, không thì MẤT KEY mỗi lần deploy.
#   SUNVIW_SECRET      (tuỳ chọn) khoá ký phiên đăng nhập admin; không đặt = tự sinh và lưu chung file key.
#   SUNVIW_GATE_API    1 = bắt buộc key cho các endpoint ở trên (mặc định) · 0 = tắt (ai gọi API cũng được như trước)
#   SUNVIW_KEY_START_ON_ACTIVATE  1 = (mặc định) key mới tạo CHƯA tính hạn: hạn chỉ chạy từ lần dùng THÀNH CÔNG đầu tiên (key người dùng: lần gọi hợp lệ đầu tiên đúng game + gắn được thiết bị · key admin phụ: lần đăng nhập đầu tiên). 0 = tính hạn từ lúc tạo như cũ. Key tạo TRƯỚC bản này giữ nguyên hạn cũ.
#   SUNVIW_HWID_REQUIRED  1 = request dùng key người dùng mà KHÔNG kèm HWID bị từ chối (mặc định) · 0 = cho qua (không gắn thiết bị). Có gửi HWID thì luôn được kiểm tra + gắn thiết bị.
ADMIN_MAIN_NAME = "admin chính"
_ADMIN_SALT = b"sunviw-admin-v1:93eacb1bcbb59252"
ADMIN_PASS_HASH_DEFAULT = ""                          # SEC2: đã GỠ hash mặc định khỏi code (lộ file code không còn dò được mật khẩu offline). Đặt SUNVIW_MAIN_PASS ở Railway
KEYS_PATH = os.environ.get("SUNVIW_KEYS_PATH", _data_path("sunviw_keys.json"))
KEY_GATE_API = _env_bool("SUNVIW_GATE_API", True)
KEY_START_ON_ACTIVATE = _env_bool("SUNVIW_KEY_START_ON_ACTIVATE", True)   # True (mặc định) = key mới tạo CHƯA tính hạn; hạn chỉ bắt đầu chạy từ lần dùng THÀNH CÔNG đầu tiên (kích hoạt). False = như cũ (tính từ lúc tạo)
KEY_DAYS = (1, 3, 7, 30, 60, 90)                     # hạn key cho phép khi TẠO (ngày) = 1 ngày · 3 ngày · 1 tuần · 1 tháng · 2 tháng · 3 tháng. Key cũ có hạn khác (2/14/180/365 ngày) vẫn dùng + hiển thị bình thường
# 💰 GIÁ BÁN KEY (VNĐ) theo số ngày của gói — dùng để TỰ TÍNH DOANH THU khi key được KÍCH HOẠT (áp dụng cho cả key Sun · Hit · LC79).
#    Gói không có trong bảng (60 / 90 ngày, hoặc key cũ 2 / 14 / 180 / 365 ngày) = chưa có giá -> không tính vào doanh thu (chỉ đếm riêng ở "chưa có giá"). Muốn tính thêm gói nào thì thêm vào đây.
#    Giá được CHỐT vào sổ doanh thu ngay lúc kích hoạt -> sau này đổi bảng giá không làm đổi doanh thu cũ. Doanh thu chỉ ADMIN CHÍNH xem được (GET /api/admin/revenue + khối "Doanh thu" ở /api/admin).
KEY_PRICE = {1: 10000, 3: 25000, 7: 75000, 30: 250000}
REV_KEEP_SEC = 400 * 86400                            # sổ doanh thu giữ tối đa bấy lâu (đủ cho cửa sổ 1 ngày / 1 tuần / 1 tháng)
KEY_MAX_TOTAL = 5000                                  # trần số key lưu trong file
ADMIN_SESSION_SEC = 12 * 3600                         # phiên đăng nhập admin sống bao lâu
LOGIN_MAX_FAIL = 8                                    # sai quá N lần trong LOGIN_LOCK_SEC -> khóa IP đó LOGIN_LOCK_SEC giây
LOGIN_LOCK_SEC = 900
KEY_DEV_OPTIONS = (1, 2, 3, 5, 10, 20, 50)            # số thiết bị tối đa chọn được khi tạo key (1 key dùng được trên N thiết bị)
KEY_DEV_DEFAULT = 1                                   # mặc định (cũng là số thiết bị của key cũ tạo trước bản này)
KEY_GAMES = ("sun", "hit", "lc79", "autolc")                            # game gắn được vào key người dùng — MỖI KEY CHỈ THUỘC 1 GAME, không gộp chung
_KEY_DEAD_GAMES = ("gb68",)                          # game ĐÃ GỠ: key cũ của game này vẫn nằm trong file nhưng KHÔNG dùng được game nào (không biến thành key "mọi game")
KEY_GAME_LABEL = {"sun": "Sun", "hit": "Hit", "lc79": "LC79", "gb68": "68GB (đã gỡ)", "autolc": "Auto cược LC"}
KEY_PREFIX = {"sun": "SUN", "hit": "HIT", "lc79": "LC79", "autolc": "AUTOLC"}             # tiền tố key để nhìn là biết game: SUN-XXXX-... / HIT-XXXX-...
_lg = os.environ.get("SUNVIW_KEY_LEGACY_GAME", "all").strip().lower()
_lg = "lc79" if _lg == "tele68" else _lg
KEY_LEGACY_GAME = _lg if _lg in ("all", "sun", "hit", "lc79") else "all"   # game của key cũ chưa có trường game (xem khối CONFIG KEY / ADMIN)
HWID_REQUIRED = _env_bool("SUNVIW_HWID_REQUIRED", True)
HWID_TOUCH_SEC = 60                                   # ghi "lần dùng gần nhất" tối đa 1 lần / phút / thiết bị (đỡ ghi file mỗi lần panel poll)


def _pw_hash(pw):
    return hashlib.pbkdf2_hmac("sha256", str(pw).encode("utf-8"), _ADMIN_SALT, 200000).hex()


_ENV_MAIN_PASS = os.environ.get("SUNVIW_MAIN_PASS", "")
# SUNVIW_ALLOW_DEFAULT_PASS=0 (KHUYẾN NGHỊ sau khi đã đặt SUNVIW_MAIN_PASS): bỏ hẳn hash mặc định nằm trong code -> lộ file code cũng không dò được mật khẩu admin offline
ALLOW_DEFAULT_PASS = False
_TEMP_PASS = ""
if not _ENV_MAIN_PASS:                                # chưa đặt SUNVIW_MAIN_PASS -> mật khẩu TẠM ngẫu nhiên (chỉ sống tới lần restart, chỉ hiện trong log server riêng của bạn)
    _TEMP_PASS = secrets.token_urlsafe(18)
    print("[SEC] !!! SUNVIW_MAIN_PASS CHUA DAT. Mat khau admin TAM (het hieu luc khi restart): " + _TEMP_PASS + "  -> dat SUNVIW_MAIN_PASS (>= 16 ky tu) o Railway Variables", file=sys.stderr)
ADMIN_PASS_HASH = _pw_hash(_ENV_MAIN_PASS or _TEMP_PASS)
_MEM_SECRET = secrets.token_hex(32)
_kv_lock = threading.RLock()
_KEY_ALPHA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"        # bỏ 0/O/1/I cho dễ đọc


def _kv_load():
    for pth in (KEYS_PATH, KEYS_PATH + ".bak"):       # file chính hỏng / mất -> đọc bản sao .bak (tránh lần lưu sau ghi đè mất sạch key)
        try:
            with open(pth, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict) and isinstance(d.get("keys"), dict):
                return d
        except Exception:  # noqa: BLE001
            pass
    return {"secret": "", "keys": {}}


def _kv_save(d):
    if not d.get("secret"):
        d["secret"] = _MEM_SECRET
    tmp = KEYS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    try:
        if os.path.exists(KEYS_PATH) and os.path.getsize(KEYS_PATH) > 2:
            shutil.copyfile(KEYS_PATH, KEYS_PATH + ".bak")   # giữ bản trước đó
    except OSError:
        pass
    os.replace(tmp, KEYS_PATH)


def _secret_bytes():
    s = os.environ.get("SUNVIW_SECRET", "")
    if not s:
        with _kv_lock:
            d = _kv_load()
            if not d.get("secret"):
                try:
                    _kv_save(d)
                except OSError:
                    pass
            s = d.get("secret") or _MEM_SECRET
    return s.encode("utf-8")


def _norm_key(s):
    return re.sub(r"[^A-Za-z0-9-]", "", str(s or "")).upper()[:40]


def _new_key(prefix, keys):
    while True:
        k = prefix + "-" + "-".join("".join(secrets.choice(_KEY_ALPHA) for _ in range(4)) for _ in range(4))
        if k not in keys:
            return k


def _clean_username(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    if not 2 <= len(s) <= 20 or not all(c.isalnum() or c in " _.-" for c in s):
        return None
    if s.lower() in ("admin", "admin chính", "admin chinh", "main"):
        return None
    return s


def _norm_hwid(s):
    """HWID hợp lệ = 8-64 ký tự [A-Za-z0-9_-] (panel gửi 32 hex). Sai định dạng -> "". Luôn chữ thường để so khớp."""
    s = str(s or "").strip()
    return s.lower() if re.fullmatch(r"[A-Za-z0-9_-]{8,64}", s) else ""


DEV_ALIAS_MAX = 6                                     # số mã phụ tối đa nhớ cho 1 thiết bị (mã cũ nhất bị bỏ khi đầy)


def req_hw_ids(body=None):
    """Mã thiết bị của request -> (hw, alts, fresh).
       hw    : mã CHÍNH = header X-HWID · ?hwid= · body {"hwid"} · cookie "hwid" (cookie để mở thẳng link API trên trình duyệt vẫn nhận ra máy).
       alts  : mã PHỤ của CHÍNH máy đó (header X-HWID-ALT, cách nhau dấu phẩy · ?hwid_alt= · body {"hwid_alt": [...]}): dấu vân tay phần cứng ổn định / công thức cũ.
       fresh : client báo "vừa mất bộ nhớ, không còn mã cũ" (header X-HWID-FRESH: 1 · ?hwid_fresh=1 · body {"hwid_fresh": true}) -> alts được dùng để NHẬN LẠI máy cũ.
       Tool tự viết chỉ cần gửi X-HWID như trước (không cần alts / fresh)."""
    b = body if isinstance(body, dict) else {}
    hw = ""
    for c in (request.headers.get("X-HWID"), request.args.get("hwid"), b.get("hwid"), request.cookies.get("hwid")):
        hw = _norm_hwid(c)
        if hw:
            break
    alts = []
    for raw in (request.headers.get("X-HWID-ALT"), request.args.get("hwid_alt"), b.get("hwid_alt")):
        parts = raw if isinstance(raw, (list, tuple)) else re.split(r"[,\s]+", str(raw or ""))
        for x in parts[:6]:
            n = _norm_hwid(x)
            if n and n != hw and n not in alts:
                alts.append(n)
    fresh = str(request.headers.get("X-HWID-FRESH") or request.args.get("hwid_fresh") or b.get("hwid_fresh") or "").strip().lower() in ("1", "true", "yes")
    return hw, tuple(alts[:4]), fresh


def req_hwid(body=None):
    """HWID chính của thiết bị gọi request (giữ để tool cũ không hỏng) — xem req_hw_ids."""
    return req_hw_ids(body)[0]


def _activated(rec):
    """Key đã kích hoạt (đã bắt đầu tính hạn) chưa. Key tạo TRƯỚC bản này (không có trường "act") = coi như đã kích hoạt từ lúc tạo -> hạn cũ giữ nguyên."""
    return "act" not in rec or bool(rec.get("act"))


def _is_expired(rec, now):
    """Hết hạn chưa. Key chưa kích hoạt thì KHÔNG BAO GIỜ hết hạn (hạn chưa chạy)."""
    return _activated(rec) and int(rec.get("exp") or 0) <= now


ADD_UNITS = {"hour": 3600, "day": 86400, "week": 7 * 86400, "month": 30 * 86400, "gio": 3600, "ngay": 86400, "tuan": 7 * 86400, "thang": 30 * 86400}   # đơn vị cộng thời gian (tháng = 30 ngày)
ADD_MAX_SEC = 365 * 86400                             # tối đa cộng MỖI LẦN gọi
BONUS_MAX_SEC = 3650 * 86400                          # tổng giờ cộng thêm tối đa của 1 key


def _parse_dur(b, ak="amount", uk="unit", hk="hours"):
    """Đọc {"amount": N, "unit": hour|day|week|month} (hoặc {"hours": N} kiểu cũ) -> số GIÂY > 0, không hợp lệ -> 0. N = số nguyên 1..99999, tối đa ADD_MAX_SEC."""
    try:
        if b.get(ak) is not None:
            a, unit = b.get(ak), str(b.get(uk) or "hour").strip().lower()
        elif b.get(hk) is not None:
            a, unit = b.get(hk), "hour"
        else:
            return 0
        if isinstance(a, bool) or (isinstance(a, float) and a != int(a)):
            return 0
        a = int(a)
    except (TypeError, ValueError, OverflowError):
        return 0
    mul = ADD_UNITS.get(unit)
    if not mul or a <= 0 or a > 99999:
        return 0
    return a * mul if a * mul <= ADD_MAX_SEC else 0


def _bonus(rec):
    """Tổng số GIÂY đã cộng thêm cho key (nút +1 giờ / tặng giờ lúc tạo). Key cũ không có trường này = 0."""
    try:
        return max(0, int(rec.get("bonus") or 0))
    except (TypeError, ValueError):
        return 0


def _add_time(rec, secs, now):
    """Cộng `secs` giây cho key. Đã kích hoạt: dời hạn (key đã hết hạn thì tính từ bây giờ). Chưa kích hoạt: cộng dồn vào bonus, áp dụng khi kích hoạt."""
    rec["bonus"] = _bonus(rec) + int(secs)
    if _activated(rec):
        rec["exp"] = max(int(rec.get("exp") or 0), int(now)) + int(secs)


def _activate(rec, now):
    """Kích hoạt lần đầu: bắt đầu tính hạn từ `now` (exp = now + số ngày của gói). Trả True nếu VỪA kích hoạt (nơi gọi phải _kv_save)."""
    if _activated(rec):
        return False
    try:
        days = max(1, int(rec.get("days") or 1))
    except (TypeError, ValueError):
        days = 1
    rec["act"] = now
    rec["exp"] = now + days * 86400 + _bonus(rec)
    return True


def _left_sec(rec, now):
    """Số giây còn lại; key chưa kích hoạt = trọn gói (days * 86400)."""
    if _activated(rec):
        return max(0, int(rec.get("exp") or 0) - int(now))
    try:
        return max(0, int(rec.get("days") or 0)) * 86400 + _bonus(rec)
    except (TypeError, ValueError):
        return 0


def _max_dev(rec):
    """Số thiết bị tối đa của key (key cũ chưa có max_dev = KEY_DEV_DEFAULT)."""
    try:
        return max(1, int(rec.get("max_dev") or KEY_DEV_DEFAULT))
    except (TypeError, ValueError):
        return KEY_DEV_DEFAULT


def _dev_find(devs, hw, alts=(), fresh=False):
    """Khoá của thiết bị ĐÃ GẮN ứng với request, không có -> None. KHÔNG dùng IP.
       1) mã chính hw trùng khoá thiết bị, hoặc trùng 1 mã phụ máy đó đã được học  -> đúng máy.
       2) chỉ khi client báo fresh (máy vừa mất bộ nhớ nên không còn mã cũ): mã dự phòng alts trùng khoá / mã phụ -> nhận lại máy cũ.
          Máy KHÁC (còn mã riêng của nó) không bao giờ được nhận nhầm bằng alts."""
    if hw in devs:
        return hw
    for k, v in devs.items():
        if hw in (v.get("alt") or ()):
            return k
    if fresh:
        for a in alts:
            if a in devs:
                return a
        for k, v in devs.items():
            al = v.get("alt") or ()
            if any(a in al for a in alts):
                return k
    return None


def _dev_learn(dv, key, ids):
    """Nhớ thêm mã phụ cho thiết bị đã khớp (để lần sau mất bộ nhớ / đổi công thức vẫn nhận ra máy). Trả True nếu có thay đổi."""
    al = dv.get("alt")
    if not isinstance(al, list):
        al = dv["alt"] = []
    ch = False
    for i in ids:
        if i and i != key and i not in al:
            al.append(i)
            ch = True
    if len(al) > DEV_ALIAS_MAX:
        del al[:-DEV_ALIAS_MAX]
        ch = True
    return ch


def _dev_use(rec, hw, ip, ua, now, alts=(), fresh=False, bind=True):
    """Dùng key trên thiết bị hw: đã gắn -> cập nhật "lần dùng gần nhất" (tối đa 1 lần / HWID_TOUCH_SEC) + học mã phụ;
    chưa gắn -> gắn thêm nếu key còn chỗ (số thiết bị < max_dev) và bind=True. Gọi trong _kv_lock với rec lấy từ _kv_load().
    IP chỉ được GHI LẠI cho admin xem, KHÔNG bao giờ dùng để chặn -> đổi mạng / đổi IP không ảnh hưởng.
    Trả (ok, lỗi, changed): changed=True -> nơi gọi phải _kv_save."""
    devs = rec.get("devs")
    if not isinstance(devs, dict):
        devs = rec["devs"] = {}
    k = _dev_find(devs, hw, alts, fresh)
    if k is not None:
        dv = devs[k]
        ch = _dev_learn(dv, k, [hw] if fresh else [hw, *alts])
        if now - int(dv.get("last") or 0) >= HWID_TOUCH_SEC:
            dv["last"], dv["ip"] = now, ip
            rec["last"], rec["last_ip"] = now, ip
            ch = True
        return True, "", ch
    if not bind:
        return False, "thiet bi chua gan vao key", False
    cap = _max_dev(rec)
    if len(devs) >= cap:
        return False, (f"Key đã đủ {cap} thiết bị — thiết bị này chưa được gắn với key (đổi mạng / đổi IP KHÔNG ảnh hưởng, chỉ máy khác mới bị chặn). "
                       f"Nhờ admin reset / gỡ thiết bị cũ hoặc xin key có nhiều thiết bị hơn. Mã thiết bị của bạn: {hw[:8]}…{hw[-4:]}"), False
    dv = devs[hw] = {"first": now, "last": now, "ip": ip, "ua": str(ua or "")[:80]}
    if not fresh:
        _dev_learn(dv, hw, alts)
    rec["last"], rec["last_ip"] = now, ip
    return True, "", True


def _key_game(rec):
    """Game của key người dùng: "sun" | "hit"; key cũ chưa gán game -> KEY_LEGACY_GAME ("all" = mọi game)."""
    g = str(rec.get("game") or "").strip().lower()
    if g == "tele68":                                  # tên cũ -> LC79 (key TELE-... đã tạo trước vẫn dùng được, chỉ cho game LC79)
        g = "lc79"
    if g in _KEY_DEAD_GAMES:                           # game đã gỡ (68GB): key giữ nguyên game cũ -> không khớp endpoint nào, không lên quyền "mọi game"
        return g
    return g if g in KEY_GAMES else KEY_LEGACY_GAME


def _game_ok(kg, game):
    """Key thuộc game `kg` có được dùng cho `game` không (game None = endpoint không gắn game cụ thể -> mọi key hợp lệ)."""
    if kg == "autolc" or game == "autolc":                # key AUTO CƯỢC LC chỉ dùng cho /tool/autocuoc; key cũ "all" cũng KHÔNG vào được auto cược
        return kg == game
    return game is None or kg == "all" or kg == game


def _key_tables(kg):
    """Các khoá lịch sử (hist_clear) mà key thuộc game `kg` được thao tác."""
    out = set()
    if kg in ("all", "sun"):
        out.add("sun")
    for k, tb in HIT_TABLES.items():                   # mỗi bàn thuộc 1 game của key (Hit: 2 bàn · LC79: 2 bàn LC)
        if kg in ("all", tb.kgame):
            out.add(k)
    return out


def _path_game(p):
    """Game mà endpoint thuộc về (None = endpoint chung: mọi key hợp lệ đều gọi được)."""
    if p in ("/api/predictsun", "/api/predict"):
        return "sun"
    if p in ("/api/predicthittxthuong", "/api/predicthittxmd5"):
        return "hit"
    if p in ("/api/predictlcmd5", "/api/predictlchu", "/api/predicttele68txmd5"):
        return "lc79"
    return None


WRONG_GAME_MSG = "Key này chỉ dùng cho game"


def _own_user_key(s, r):
    """Admin phụ chỉ động được vào key NGƯỜI DÙNG do chính mình tạo; admin chính động được mọi key."""
    return s["r"] == "main" or (r.get("type") == "user" and r.get("by") == "sub" and r.get("by_name") == s["n"])


# ─ phiên đăng nhập admin (SEC2): token NGẪU NHIÊN 256-bit, server chỉ lưu SHA-256 của nó (không có khoá ký nào để lộ / giả mạo) ─
#   · mỗi phiên có thêm KHOÁ KÝ RIÊNG `sk` (chỉ trả 1 lần lúc đăng nhập). MỌI request admin phải kèm X-Ts + X-Nonce + X-Sig = HMAC-SHA256(sk, METHOD\nPATH?QUERY\nTS\nNONCE\nSHA256(body)).
#     -> chặn: chèn / sửa request giữa đường, phát lại (replay) request cũ, dùng token bị lộ trong log / Referer mà không có `sk`.
#   · nonce chỉ dùng 1 lần (cache 3 phút), lệch giờ tối đa SEC_SIGN_SKEW giây · phiên chết sau SESS_IDLE giây không hoạt động / SESS_ABS giây tuyệt đối · bị gắn với User-Agent đã đăng nhập.
#   · chạy đúng với gunicorn --workers 1 (đã bắt buộc bởi auto cược). Restart server = phiên admin mất, đăng nhập lại.
SESS_IDLE = _env_num("SUNVIW_SESS_IDLE", 30 * 60, int)
SESS_ABS = _env_num("SUNVIW_SESS_ABS", 8 * 3600, int)
SEC_SIGN_ADMIN = _env_bool("SUNVIW_SIGN_ADMIN", True)
SEC_SIGN_SKEW = _env_num("SUNVIW_SIGN_SKEW", 60, int)
_sess = {}
_sess_lock = threading.Lock()
_nonce_seen = {}
SESS_MAX = 200


def _sh(x):
    return hashlib.sha256(("sunviw-sess:" + str(x)).encode("utf-8")).hexdigest()


def _ua_h():
    return hashlib.sha256(request.headers.get("User-Agent", "").encode("utf-8", "ignore")).hexdigest()[:24]


def _tok_make(role, name, key="", hw=""):
    """Tạo phiên. Trả token (chuỗi). Khoá ký sk lấy bằng _tok_sk(token) ngay sau đó (chỉ 1 lần)."""
    sid, sk = secrets.token_urlsafe(32), secrets.token_hex(32)
    now = time.time()
    with _sess_lock:
        for h in [h for h, v in _sess.items() if v["abs"] < now or v["last"] + SESS_IDLE < now]:
            del _sess[h]
        if len(_sess) >= SESS_MAX:                       # đầy -> bỏ phiên cũ nhất
            del _sess[min(_sess, key=lambda h: _sess[h]["last"])]
        _sess[_sh(sid)] = {"r": role, "n": name, "k": key, "h": hw, "ua": _ua_h(), "ip": client_ip(), "sk": sk,
                           "t0": now, "last": now, "abs": now + SESS_ABS}
    flask_g._sk_once = sk
    return sid


def _tok_pair(role, name, key="", hw=""):
    t = _tok_make(role, name, key, hw)
    return {"token": t, "sk": flask_g._sk_once}


def _tok_kill(token):
    with _sess_lock:
        _sess.pop(_sh(token), None)


def _audit(ev, **kw):
    """Nhật ký bảo mật (JSON / dòng). KHÔNG bao giờ ghi key / mật khẩu / token."""
    try:
        rec = {"t": int(time.time()), "ev": ev, "ip": client_ip(), "path": request.path, "ua": request.headers.get("User-Agent", "")[:60]}
        rec.update(kw)
        pth = os.environ.get("SUNVIW_AUDIT_PATH", _data_path("sunviw_audit.log"))
        if os.path.exists(pth) and os.path.getsize(pth) > 2 * 1024 * 1024:
            os.replace(pth, pth + ".1")
        with open(pth, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        pass


def _sig_ok(sess):
    """Kiểm chữ ký request admin (xem khối trên). True nếu hợp lệ + nonce chưa dùng."""
    if not SEC_SIGN_ADMIN:
        return True
    ts, nonce, sig = request.headers.get("X-Ts", ""), request.headers.get("X-Nonce", ""), request.headers.get("X-Sig", "")
    if not (ts.isdigit() and 8 <= len(nonce) <= 64 and re.fullmatch(r"[A-Za-z0-9_-]+", nonce) and re.fullmatch(r"[0-9a-f]{64}", sig)):
        return False
    now = time.time()
    if abs(now - int(ts)) > SEC_SIGN_SKEW:
        return False
    qs = request.query_string.decode("latin-1")
    msg = "\n".join((request.method, request.path + ("?" + qs if qs else ""), ts, nonce, hashlib.sha256(request.get_data(cache=True)).hexdigest()))
    good = hmac.new(sess["sk"].encode(), msg.encode("utf-8", "ignore"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(good, sig):
        return False
    nk = sess["sid_h"] + ":" + nonce
    with _sess_lock:
        if len(_nonce_seen) > 20000:
            for k in [k for k, e in _nonce_seen.items() if e < now]:
                del _nonce_seen[k]
        if nk in _nonce_seen:                              # PHÁT LẠI request cũ -> từ chối
            return False
        _nonce_seen[nk] = now + 180
    return True


def _tok_check():
    """Trả {"r","n","k"} nếu X-Admin-Token + chữ ký hợp lệ, ngược lại None (kết quả cache trong 1 request — nonce chỉ dùng 1 lần).
    Admin phụ: key còn tồn tại + còn hạn + đúng THIẾT BỊ đã đăng nhập + máy đó vẫn gắn vào key (admin chính reset / gỡ / xóa key -> phiên chết ngay). Không xét IP."""
    c = getattr(flask_g, "_tok_res", False)
    if c is not False:
        return c
    flask_g._tok_res = None
    t = request.headers.get("X-Admin-Token", "")
    if not t or len(t) > 100:
        return None
    sh = _sh(t)
    now = time.time()
    with _sess_lock:
        v = _sess.get(sh)
        if v is None:
            return None
        if v["abs"] < now or v["last"] + SESS_IDLE < now:
            _sess.pop(sh, None)
            return None
        if not hmac.compare_digest(v["ua"], _ua_h()):      # khác thiết bị: từ chối nhưng KHÔNG huỷ phiên (kẻ cắp token không được phép đá admin thật ra)
            return None
        sess = dict(v, sid_h=sh)
    if not _sig_ok(sess):
        _audit("sig_fail", role=sess["r"])
        return None
    with _sess_lock:
        if sh in _sess:
            _sess[sh]["last"] = now
    try:
        if sess["r"] == "main":
            flask_g._tok_res = {"r": "main", "n": ADMIN_MAIN_NAME, "k": "", "sh": sh}
            return flask_g._tok_res
        if sess["r"] == "sub":
            hw, alts, hfresh = req_hw_ids()
            if not hw:
                return None
            inow = int(now)
            with _kv_lock:
                d = _kv_load()
                rec = d["keys"].get(sess["k"])
                if rec and rec.get("type") == "sub" and rec.get("owner") == sess["n"] and not _is_expired(rec, inow):
                    devs = rec.get("devs") if isinstance(rec.get("devs"), dict) else {}
                    kr = _dev_find(devs, hw, alts, hfresh)
                    if kr is not None and kr == _dev_find(devs, sess.get("h", "")):
                        _, _, ch = _dev_use(rec, hw, client_ip(), request.headers.get("User-Agent", ""), inow, alts, hfresh, bind=False)
                        if ch:
                            try:
                                _kv_save(d)
                            except OSError:
                                pass
                        flask_g._tok_res = {"r": "sub", "n": sess["n"], "k": sess["k"], "sh": sh}
                        return flask_g._tok_res
    except Exception:  # noqa: BLE001
        pass
    return None


# ─ chống dò mật khẩu / key: sai quá LOGIN_MAX_FAIL lần thì khóa IP ─
_rl = {}
_rl_lock = threading.Lock()


def _rl_wait(ip):
    with _rl_lock:
        r = _rl.get(ip)
        return max(0, int(r[2] - time.time())) if r else 0


def _rl_fail(ip):
    now = time.time()
    with _rl_lock:
        if len(_rl) > 5000:
            _rl.clear()
        r = _rl.get(ip)
        if not r or now - r[1] > LOGIN_LOCK_SEC:
            r = _rl[ip] = [0, now, 0.0]
        r[0] += 1
        if r[0] >= LOGIN_MAX_FAIL:
            r[2] = now + LOGIN_LOCK_SEC


def _rl_reset(ip):
    with _rl_lock:
        _rl.pop(ip, None)


def _key_price(days):
    """Giá bán (VNĐ) của gói `days` ngày; gói chưa có giá -> 0."""
    try:
        return int(KEY_PRICE.get(int(days), 0))
    except (TypeError, ValueError):
        return 0


def _rev_record(d, k, rec, now):
    """Ghi 1 key người dùng VỪA kích hoạt vào sổ doanh thu d["rev"] (nơi gọi tự _kv_save). Sổ độc lập với danh sách key -> xóa key / dọn key hết hạn KHÔNG làm mất doanh thu."""
    if rec.get("type") != "user":
        return
    rv = d.setdefault("rev", {})
    if not isinstance(rv, dict):
        rv = d["rev"] = {}
    rv[k] = {"t": int(now), "g": _key_game(rec), "d": int(rec.get("days") or 0), "p": _key_price(rec.get("days"))}
    cut = now - REV_KEEP_SEC
    for kk in [x for x, v in rv.items() if int((v or {}).get("t") or 0) < cut]:
        del rv[kk]


def _revenue_calc(d, now):
    """Doanh thu theo cửa sổ TRƯỢT 1 ngày (24 giờ) · 1 tuần (7 ngày) · 1 tháng (30 ngày) tính từ lúc KÍCH HOẠT key, tách theo game.
       Nguồn = sổ d["rev"] + các key người dùng ĐÃ kích hoạt từ trước bản này mà chưa có trong sổ (tính theo giá hiện tại, thời điểm = lúc kích hoạt; key cũ không có trường act = lúc tạo)."""
    ent = {}
    for k, v in (d.get("rev") or {}).items():
        if isinstance(v, dict):
            ent[k] = (int(v.get("t") or 0), str(v.get("g") or "all"), int(v.get("d") or 0), int(v.get("p") or 0))
    for k, r in (d.get("keys") or {}).items():
        if k in ent or r.get("type") != "user" or not _activated(r):
            continue
        t = int(r.get("act") or r.get("created") or 0)
        if t:
            ent[k] = (t, _key_game(r), int(r.get("days") or 0), _key_price(r.get("days")))
    wins = (("ngay", 86400), ("tuan", 7 * 86400), ("thang", 30 * 86400))
    games = list(KEY_GAMES) + ["all"] + [g for g in _KEY_DEAD_GAMES if any(e[1] == g for e in ent.values())]   # game đã gỡ chỉ hiện khi còn doanh thu cũ
    out = {w: {"tong": 0, "so_key": 0, "chua_co_gia": 0, "game": {g: {"tien": 0, "so_key": 0} for g in games}} for w, _ in wins}
    for t, g, days, price in ent.values():
        g = g if g in games else "all"
        for w, sec in wins:
            if now - sec <= t <= now + 60:
                o = out[w]
                if price > 0:
                    o["tong"] += price
                    o["so_key"] += 1
                    o["game"][g]["tien"] += price
                    o["game"][g]["so_key"] += 1
                else:
                    o["chua_co_gia"] += 1
    return out


def _check_user_key(k, hw=None, ip="", ua="", alts=(), fresh=False, game=None, bind=True):
    """(record, lỗi, đã_tồn_tại, game_của_key). Chỉ key loại 'user' còn hạn VÀ đúng game (nếu `game` được truyền) mới qua; sai game -> lỗi bắt đầu bằng WRONG_GAME_MSG, KHÔNG gắn thiết bị. Có HWID -> kiểm tra / gắn thiết bị (đủ chỗ mới gắn thêm) và ghi "lần dùng gần nhất";
    không có HWID mà HWID_REQUIRED bật -> từ chối. `ip` chỉ để ghi lại, không dùng để chặn."""
    k = _norm_key(k)
    if not k:
        return None, "thieu key", False, None
    with _kv_lock:
        d = _kv_load()
        r = d["keys"].get(k)
        if not r or r.get("type") != "user":
            return None, "key khong hop le", False, None
        now = int(time.time())
        kg = _key_game(r)
        if _is_expired(r, now):
            return None, "key da het han", True, kg
        if not _game_ok(kg, game):
            return None, (f"{WRONG_GAME_MSG} {KEY_GAME_LABEL.get(kg, kg)} — không dùng được cho game {KEY_GAME_LABEL.get(game, game)}. "
                          f"Hãy dùng key {KEY_GAME_LABEL.get(game, game)} (hoặc xin admin tạo key {KEY_GAME_LABEL.get(game, game)})."), True, kg
        if not bind:                                     # bind=False (auto cược LC): KHÔNG giới hạn / gắn thiết bị — điện thoại, máy tính, nhiều máy đều vào được bằng cùng 1 key
            ch = False
        elif hw:
            ok, err, ch = _dev_use(r, hw, ip, ua, now, alts, fresh)
            if not ok:
                return None, err, True, kg
        elif HWID_REQUIRED:
            return None, "Thiếu mã thiết bị (HWID) — gửi header X-HWID hoặc ?hwid= cùng key.", True, kg
        else:
            ch = False
        if _activate(r, now):                            # lần dùng THÀNH CÔNG đầu tiên (đúng game + gắn được thiết bị) -> bắt đầu tính hạn từ đây
            ch = True
            _rev_record(d, k, r, now)                    # ghi sổ doanh thu (giá chốt ngay lúc kích hoạt)
        if ch:
            try:
                _kv_save(d)
            except OSError:
                pass
        return r, "", True, kg


# ═══════════════════════════════════════════════════════════════════════════
#  🛂  DUYỆT THIẾT BỊ VÀO PANEL /api/html  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Panel /api/html KHÔNG còn ô nhập key. Ai mở trang cũng chỉ thấy bảng "Đang chờ admin duyệt": panel tự gửi yêu cầu (kèm HWID thiết bị) tới
#   POST/GET /api/panel/status -> thiết bị vào danh sách CHỜ DUYỆT. Admin CHÍNH vào /api/admin -> mục "Duyệt thiết bị vào panel HTML" -> Duyệt / Từ chối / Gỡ quyền.
#   Được duyệt xong, panel tự mở (không cần tải lại), KHÔNG cần key, và vào được CẢ SUN LẪN HIT (2 bàn).
#   Thiết bị đã duyệt cũng gọi thẳng được /api/predictsun · /api/predicthittxthuong · /api/predicthittxmd5 · /api/ips · /api/history/clear không cần key
#   (cổng _gate_key nhận HWID đã duyệt). Key người dùng + tool (X-User-Key + X-HWID) vẫn chạy y như trước, KHÔNG đổi.
#   Gỡ quyền / xóa thiết bị khỏi danh sách -> panel của máy đó bị khóa lại ngay (trong ~3 giây) và phải xin duyệt lại.
#   HWID nhận diện y như hệ key (mã đã lưu localStorage + cookie, mã phụ phần cứng): đổi mạng / đổi IP không ảnh hưởng, IP chỉ GHI LẠI để admin xem.
#   🚫 DANH SÁCH ĐEN (BAN): admin chính bấm "Ban" ở 1 thiết bị -> thiết bị đó (theo HWID) VÀ IP của nó bị chặn HOÀN TOÀN khỏi /api/html + /api/panel/status:
#      server trả HTTP 404 "Not Found" y như trang web không tồn tại / sập. Máy khác dùng cùng IP bị ban cũng 404. Ban KHÔNG ảnh hưởng tool: /api/predict* · /api/key/check ... vẫn chạy bình thường bằng key.
#      Bỏ ban: nút "Bỏ ban" ở tab "Danh sách đen" (gỡ cả thiết bị lẫn IP, máy đó phải xin duyệt lại từ đầu).
#   PANEL_DEV_PATH             file lưu danh sách thiết bị (env SUNVIW_PANEL_DEV_PATH; mặc định <DATA_DIR>/sunviw_panel_devices.json). Railway: nằm cùng Volume với file key.
#   PANEL_MAX_DEVICES          trần số thiết bị lưu (đầy -> bỏ yêu cầu CHỜ DUYỆT cũ nhất; thiết bị đã duyệt / từ chối không bị xóa tự động)
#   PANEL_MAX_PENDING_PER_IP   mỗi IP chỉ được có tối đa N yêu cầu đang chờ duyệt cùng lúc (chống spam HWID giả) — env SUNVIW_PANEL_PENDING_PER_IP
PANEL_DEV_PATH = os.environ.get("SUNVIW_PANEL_DEV_PATH", _data_path("sunviw_panel_devices.json"))
PANEL_MAX_DEVICES = 2000
PANEL_MAX_PENDING_PER_IP = _env_num("SUNVIW_PANEL_PENDING_PER_IP", 10, int)
PANEL_TOUCH_SEC = 60                                  # ghi "thấy lần cuối" tối đa 1 lần / phút / thiết bị
_pv_lock = threading.RLock()
_pv_cache = {"sig": None, "d": None}                  # cache theo (mtime, size) của file -> panel poll 3s/lần không đọc lại file; vẫn đúng khi nhiều worker cùng ghi


def _pv_load():
    """{"devs": {hwid: {"st": pending|approved|denied, "first", "last", "ip", "ua", "alt": [...], "dec_at", "dec_by"}}}. Gọi trong _pv_lock."""
    try:
        stt = os.stat(PANEL_DEV_PATH)
        sig = (stt.st_mtime_ns, stt.st_size)
    except OSError:
        return {"devs": {}}
    if _pv_cache["sig"] == sig and _pv_cache["d"] is not None:
        return _pv_cache["d"]
    try:
        with open(PANEL_DEV_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict) and isinstance(d.get("devs"), dict):
            _pv_cache.update(sig=sig, d=d)
            return d
    except Exception:  # noqa: BLE001
        pass
    return {"devs": {}}


def _pv_save(d):
    """Ghi file thiết bị (atomic). Trả True nếu ghi được. Gọi trong _pv_lock."""
    try:
        tmp = PANEL_DEV_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, PANEL_DEV_PATH)
        stt = os.stat(PANEL_DEV_PATH)
        _pv_cache.update(sig=(stt.st_mtime_ns, stt.st_size), d=d)
        return True
    except OSError:
        _pv_cache.update(sig=None, d=None)             # bỏ cache để lần sau đọc lại file thật (d có thể đã bị sửa dở)
        return False


def _tok_hash(t):
    return hashlib.sha256(("sunviw-devtok:" + str(t)).encode("utf-8")).hexdigest()


def _req_dev_token():
    """Token thiết bị: cookie HttpOnly `sv_dt` (panel tự gửi) hoặc header X-Device-Token (tool chạy trên máy đã duyệt)."""
    return (request.headers.get("X-Device-Token") or request.cookies.get(DEV_COOKIE) or "").strip()[:96]


def _tok_issue(dv):
    t = secrets.token_urlsafe(32)                       # 256-bit ngẫu nhiên; server chỉ lưu SHA-256
    dv["tok"] = _tok_hash(t)
    flask_g._new_dev_tok = t                            # _cors đặt cookie vào response
    return t


def _panel_access(hw, alts=(), fresh=False, ip="", ua="", create=True, bind=False):
    """Trạng thái của thiết bị với panel: 'approved' | 'pending' | 'denied' | 'limit' | 'none' (chưa có và create=False).
    ⚑ HWID do client tự gửi nên ai biết (hoặc đoán trùng) HWID của máy đã duyệt đều giả được -> mỗi thiết bị còn có TOKEN ngẫu nhiên do SERVER cấp (cookie HttpOnly).
       · token khớp 1 bản ghi -> chính là máy đó (token là thông tin xác thực chính).
       · HWID khớp bản ghi ĐÃ CÓ token nhưng request không mang token đúng -> KHÔNG phải máy đó (trùng / giả HWID): coi như thiết bị mới, tạo bản ghi riêng chờ duyệt.
       · bản ghi cũ (duyệt trước bản vá, chưa có token): bind=True (chỉ ở /api/panel/status, tức trình duyệt panel thật) thì gắn token ngay; DEV_TOKEN_STRICT bật thì chưa được vào tới khi admin gỡ + duyệt lại.
    create=True: thiết bị lạ -> tạo yêu cầu CHỜ DUYỆT. IP chỉ ghi lại, không dùng để chặn."""
    now = int(time.time())
    th = _tok_hash(_req_dev_token()) if _req_dev_token() else ""
    with _pv_lock:
        d = _pv_load()
        devs = d["devs"]
        k, legacy = None, False
        if th:
            for kk, vv in devs.items():
                if vv.get("tok") and hmac.compare_digest(str(vv["tok"]), th):
                    k = kk
                    break
        if k is None:
            k0 = _dev_find(devs, hw, alts, fresh)
            if k0 is not None and not devs[k0].get("tok"):
                k, legacy = k0, True
        if k is not None:
            dv = devs[k]
            st = dv.get("st") if dv.get("st") in ("approved", "pending", "denied", "banned") else "pending"
            ch = False
            if legacy:
                if st == "approved" and DEV_TOKEN_STRICT:
                    return "pending"                    # strict: máy cũ phải được admin gỡ + duyệt lại
                if bind:
                    _tok_issue(dv)
                    ch = True
            ch = _dev_learn(dv, k, [hw] if fresh else [hw, *alts]) or ch
            if now - int(dv.get("last") or 0) >= PANEL_TOUCH_SEC:
                dv["last"], dv["ip"], dv["ua"] = now, ip, str(ua or "")[:120]
                ch = True
            if ch:
                _pv_save(d)
            return st
        if not create:
            return "none"
        if sum(1 for v in devs.values() if v.get("st") == "pending" and v.get("ip") == ip) >= PANEL_MAX_PENDING_PER_IP:
            return "limit"
        if len(devs) >= PANEL_MAX_DEVICES:
            old = [x for x, v in devs.items() if v.get("st") == "pending"]
            if not old:
                return "limit"
            del devs[min(old, key=lambda x: devs[x].get("last") or 0)]
        key = hw
        while key in devs:                              # HWID này đã thuộc máy khác (có token riêng) -> bản ghi riêng cho máy này
            key = hw[:40] + "-" + secrets.token_hex(4)
        dv = devs[key] = {"st": "pending", "first": now, "last": now, "ip": ip, "ua": str(ua or "")[:120], "alt": []}
        _tok_issue(dv)
        if not fresh:
            _dev_learn(dv, key, alts)
        _pv_save(d)
        return "pending"


def _panel_approved(hw, alts=(), fresh=False, ip="", ua=""):
    """Thiết bị này đã được admin chính duyệt vào panel chưa (không tạo yêu cầu mới)."""
    return bool(hw) and _panel_access(hw, alts, fresh, ip, ua, create=False) == "approved"


def _panel_banned(hw, alts=(), fresh=False, ip=""):
    """Request này có bị BAN khỏi panel /api/html không: IP nằm trong danh sách đen HOẶC thiết bị (HWID) bị ban. Chỉ đọc, không tạo yêu cầu mới."""
    with _pv_lock:
        d = _pv_load()
        if ip and ip != "unknown" and ip in (d.get("bans") or {}):
            return True
        if hw:
            devs = d["devs"]
            k = _dev_find(devs, hw, alts, fresh)
            if k is not None and devs[k].get("st") == "banned":
                return True
        th = _tok_hash(_req_dev_token()) if _req_dev_token() else ""
        if th:                                          # thiết bị bị ban cũng bị nhận ra bằng token (đổi HWID không thoát ban)
            for v in d["devs"].values():
                if v.get("st") == "banned" and v.get("tok") and hmac.compare_digest(str(v["tok"]), th):
                    return True
    return False


def panel_health():
    with _pv_lock:
        d = _pv_load()
        devs = d["devs"]
        c = {"pending": 0, "approved": 0, "denied": 0, "banned": 0}
        for v in devs.values():
            if v.get("st") in c:
                c[v["st"]] += 1
        c["ip_banned"] = len(d.get("bans") or {})
    return dict(tong=len(devs), **c)


_PANEL_MSG = {"approved": "Thiết bị đã được duyệt.",
              "pending": "Đang chờ admin chính duyệt thiết bị này.",
              "denied": "Admin chính đã từ chối thiết bị này.",
              "limit": "Mạng này đã gửi quá nhiều yêu cầu chờ duyệt — nhờ admin xử lý bớt rồi thử lại."}


@app.route("/api/panel/status", methods=["GET", "POST"])
def api_panel_status():
    """Panel /api/html gọi 3 giây / lần: gửi yêu cầu duyệt (lần đầu) và hỏi trạng thái. Trả {"ok": true, "status": "approved"} khi đã được duyệt,
    còn lại "pending" | "denied" | "limit". Không cần key."""
    hw, alts, hfresh = req_hw_ids(request.get_json(silent=True) or {})
    if _panel_banned(hw, alts, hfresh, client_ip()):
        abort(404)                                      # bị ban -> giả như trang không tồn tại
    if not hw:
        return _json({"ok": False, "status": "error", "loi": "Thiếu mã thiết bị (HWID) — hãy mở panel bằng trình duyệt hoặc gửi header X-HWID."}, 400)
    if not _rate_ok(f"ps:{hw}:{client_ip()}", 90):
        return _too_many()
    st = _panel_access(hw, alts, hfresh, client_ip(), request.headers.get("User-Agent", ""), bind=True)
    return _json({"ok": st == "approved", "status": st, "loi": _PANEL_MSG.get(st, "")}, 429 if st == "limit" else 200)


_GATED_EXACT = {"/api/predictsun", "/api/predict", "/api/predicthittxthuong", "/api/predicthittxmd5", "/api/predictlcmd5", "/api/predictlchu", "/api/predicttele68txmd5", "/api/ips", "/api/history/clear", "/api/history/regrade", "/api/history/wipe"}


# ═══════════════════════════════════════════════════════════════════════════
#  🔌  OFF SERVER (công tắc ở trang /api/admin, CHỈ ADMIN CHÍNH bật/tắt)  —  CHỈNH Ở ĐÂY
# ═══════════════════════════════════════════════════════════════════════════
#   Bật OFF SERVER:  server VẪN chạy bình thường (poller quét API, 13 logic / WR / AF / lưu ván đã chấm không đổi) và panel HTML /api/html VẪN cập nhật dự đoán như thường,
#   NHƯNG các endpoint DỰ ĐOÁN (/api/predictsun · /api/predict · /api/predicthittxthuong · /api/predicthittxmd5 · /api/predictlcmd5 · /api/predictlchu · /api/predicttele68txmd5 [alias cũ])
#   chỉ trả dữ liệu cho thiết bị ĐÃ ĐƯỢC ADMIN CHÍNH DUYỆT vào panel (mục "Duyệt thiết bị vào panel HTML") và request đó KHÔNG gửi key (panel không bao giờ gửi key).
#   Admin muốn xem JSON / panel khi off: duyệt thiết bị của mình ở mục đó như mọi thiết bị khác.
#   Mọi tool ngoài (gọi bằng key người dùng, kể cả máy lạ / không HWID, kể cả tool chạy trên máy đã duyệt nhưng có gửi key) nhận HTTP 503 {"ok": false, "server_off": true, "loi": OFFSRV_MSG} -> KHÔNG nhận được dự đoán.
#   Request tool bị chặn TRƯỚC khi kiểm key -> không kích hoạt key / không gắn thiết bị / không tính vào "lần dùng gần nhất". Hạn key đã kích hoạt vẫn chạy bình thường trong lúc off.
#   Không chặn: /api/panel/status · /api/html · /api/key/check · /health · /api/admin* (nên vẫn bật lại được).
#   Trạng thái lưu trong file riêng (OFFSRV_PATH, nằm cùng Volume) -> còn nguyên sau restart / deploy, đồng bộ giữa nhiều worker gunicorn (đọc theo mtime file, cache).
#   OFFSRV_DEFAULT  trạng thái khi CHƯA có file (env SUNVIW_OFFSRV=1 -> khởi động ở chế độ off server) · OFFSRV_PATH (env SUNVIW_OFFSRV_PATH) · OFFSRV_MSG thông báo tool nhận được.
#   Endpoint: GET /api/admin/offserver (xem) · POST /api/admin/offserver {"off": true|false} (bật / tắt) — cần phiên admin CHÍNH.
OFFSRV_PATH = os.environ.get("SUNVIW_OFFSRV_PATH", _data_path("sunviw_offserver.json"))
OFFSRV_DEFAULT = _env_bool("SUNVIW_OFFSRV", False)
OFFSRV_MSG = "Server đang OFF — tạm ngừng cấp dự đoán cho tool. Vui lòng thử lại sau."
OFFSRV_PATHS = {"/api/predictsun", "/api/predict", "/api/predicthittxthuong", "/api/predicthittxmd5", "/api/predictlcmd5", "/api/predictlchu", "/api/predicttele68txmd5"}
_os_lock = threading.Lock()
_os_cache = {"sig": None, "d": None}                   # cache theo (mtime, size) của file -> mỗi request chỉ tốn 1 lần os.stat


def offsrv_state():
    """{"off": bool, "at": epoch|None, "by": str|None}. Chưa có file / file hỏng -> OFFSRV_DEFAULT."""
    dflt = {"off": OFFSRV_DEFAULT, "at": None, "by": None}
    try:
        stt = os.stat(OFFSRV_PATH)
        sig = (stt.st_mtime_ns, stt.st_size)
    except OSError:
        return dflt
    with _os_lock:
        if _os_cache["sig"] == sig and _os_cache["d"] is not None:
            return _os_cache["d"]
    try:
        with open(OFFSRV_PATH, "r", encoding="utf-8") as f:
            o = json.load(f)
        d = {"off": bool(o.get("off")), "at": o.get("at"), "by": o.get("by")}
    except Exception:  # noqa: BLE001
        return dflt
    with _os_lock:
        _os_cache.update(sig=sig, d=d)
    return d


def offsrv_set(off, by):
    """Ghi trạng thái off server (atomic). Ném OSError nếu không ghi được."""
    d = {"off": bool(off), "at": int(time.time()), "by": str(by or "")}
    tmp = OFFSRV_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(tmp, OFFSRV_PATH)
    with _os_lock:
        _os_cache.update(sig=None, d=None)              # bỏ cache -> lần đọc sau lấy đúng file mới
    return d


@app.before_request
def _gate_offserver():
    """OFF SERVER bật -> chỉ panel (thiết bị admin chính đã duyệt vào panel, request KHÔNG gửi key) nhận được dự đoán; tool ngoài nhận 503. Chạy TRƯỚC _gate_key."""
    if request.method == "OPTIONS" or request.path not in OFFSRV_PATHS:
        return None
    if not offsrv_state()["off"]:
        return None
    if request.headers.get("X-Admin-Token"):
        _s = _tok_check()
        if _s and _s["r"] == "main":
            return None
    k = request.headers.get("X-User-Key") or request.args.get("key", "")
    hw, alts, hfresh = req_hw_ids()
    if not k and hw and _panel_approved(hw, alts, hfresh, client_ip(), request.headers.get("User-Agent", "")):
        return None                                                            # panel của thiết bị đã duyệt (panel không bao giờ gửi key)
    return _json({"ok": False, "server_off": True, "loi": OFFSRV_MSG}, 503)


@app.route("/api/admin/offserver", methods=["GET", "POST"])
def api_admin_offserver():
    """Xem / bật / tắt OFF SERVER. CHỈ admin chính. POST {"off": true|false}."""
    s, err = _need_admin()
    if err:
        return err
    if s["r"] != "main":
        return _json({"ok": False, "loi": "chi admin chinh moi bat / tat duoc off server"}, 403)
    if request.method == "POST":
        b = request.get_json(silent=True) or {}
        if not isinstance(b.get("off"), bool):
            return _json({"ok": False, "loi": 'can {"off": true|false}'}, 400)
        try:
            d = offsrv_set(b["off"], s["n"])
        except OSError as e:
            return _json({"ok": False, "loi": f"khong ghi duoc file off server: {e}"}, 500)
    else:
        d = offsrv_state()
    return _json({"ok": True, "off": d["off"], "luc": d["at"], "boi": d["by"]})


_PANEL_ONLY = {"/api/ips", "/api/history/clear", "/api/history/regrade", "/api/history/wipe"}   # CHỈ panel đã duyệt / admin chính — key khách KHÔNG bao giờ được gọi


@app.before_request
def _gate_key():
    """Cổng cho endpoint dữ liệu.
    1) Admin chính (X-Admin-Token) hoặc thiết bị panel ĐÃ DUYỆT (HWID + token server cấp) -> panel=True (được ?detail=1, mọi trường).
    2) _PANEL_ONLY (ips / history clear·regrade·wipe): ngoài (1) -> 403, key khách không được đụng.
    3) Còn lại cần key người dùng hợp lệ + HWID (KEY_GATE_API) và bị giới hạn tốc độ theo IP / key / số lần sai key."""
    p = request.path
    if request.method == "OPTIONS" or p not in _GATED_EXACT:
        return None
    ip = client_ip()
    ua = request.headers.get("User-Agent", "")
    hw, alts, hfresh = req_hw_ids()
    panel = False
    if request.headers.get("X-Admin-Token"):
        _s = _tok_check()
        if _s and _s["r"] == "main":
            panel = True
    if not panel and hw and _panel_approved(hw, alts, hfresh, ip, ua):
        panel = True
    if panel:
        if not _rate_ok(f"pn:{hw or ip}", RATE_PANEL):
            return _too_many()
        flask_g.key_game = "all"                        # vào cả SUN + HIT + LC, không cần key
        flask_g.panel = True
        return None
    if p in _PANEL_ONLY:
        return _json({"ok": False, "loi": "forbidden"}, 403)
    if not KEY_GATE_API:
        return None
    if not _rate_ok(f"ip:{ip}", RATE_IP):
        return _too_many()
    k = request.headers.get("X-User-Key", "")
    if not k:
        k = request.args.get("key", "")
    nk = _norm_key(k)
    if nk and not _rate_ok(f"key:{nk}", RATE_TOOL_KEY):
        return _too_many()
    rec, err, _, kg = _check_user_key(k, hw, ip, ua, alts, hfresh, _path_game(p))
    if rec:
        flask_g.key_game = kg                           # game của key
        return None
    if err.startswith(WRONG_GAME_MSG):                 # key hợp lệ nhưng thuộc game khác
        return _json({"ok": False, "sai_game": True, "game_can": kg, "game": _path_game(p), "loi": err}, 403)
    if not _rate_ok(f"bad:{ip}", RATE_BADKEY):          # dò key / thử bừa: quá RATE_BADKEY lần sai / phút -> 429
        return _too_many("qua nhieu lan sai key, thu lai sau", 60)
    hint = " (gui header X-User-Key)" if err in ("thieu key", "key khong hop le") else ""
    return _json({"ok": False, "can_key": True, "dev_locked": err.startswith("Key đã đủ"), "loi": err + hint}, 401)


@app.route("/api/key/check", methods=["GET", "POST"])
def api_key_check():
    """Tool / panel xác thực key người dùng + gắn thiết bị: POST {"key": "...", "hwid": "..."} hoặc GET ?key=...&hwid=... (hoặc header X-User-Key / X-HWID)."""
    ip = client_ip()
    w = _rl_wait(ip)
    if w:
        return _json({"ok": False, "loi": f"nhap sai qua nhieu, thu lai sau {w}s"}, 429)
    if not _rate_ok(f"kc:{ip}", 30):
        return _too_many()
    b = request.get_json(silent=True) or {}
    k = b.get("key") or request.headers.get("X-User-Key") or request.args.get("key", "")
    hw, alts, hfresh = req_hw_ids(b)
    gm = str(b.get("game") or request.args.get("game") or "").strip().lower()    # (tuỳ chọn) kiểm tra key có đúng game này không
    gm = "lc79" if gm == "tele68" else gm
    gm = gm if gm in KEY_GAMES else None
    rec, err, exists, kg = _check_user_key(k, hw, ip, request.headers.get("User-Agent", ""), alts, hfresh, gm)
    if not rec:
        if not exists:
            _rl_fail(ip)
        if err.startswith(WRONG_GAME_MSG):
            return _json({"ok": False, "sai_game": True, "game_can": kg, "loi": err}, 403)
        return _json({"ok": False, "dev_locked": err.startswith("Key đã đủ"), "loi": err}, 401)
    _rl_reset(ip)
    return _json({"ok": True, "het_han": rec["exp"], "con_lai_giay": _left_sec(rec, time.time()), "kich_hoat": rec.get("act") or None,
                  "game": kg, "game_ten": KEY_GAME_LABEL.get(kg, "Mọi game"),
                  "so_dev": len(rec.get("devs") or {}), "max_dev": _max_dev(rec)})


ADMIN_CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
             "connect-src 'self'; img-src data:; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'none'")


@app.route("/api/admin")
def api_admin_page():
    resp = Response(ADMIN_HTML, content_type="text/html; charset=utf-8")
    resp.headers["Content-Security-Policy"] = ADMIN_CSP
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    """Đăng nhập admin bằng MỘT ô key: {"key": "..."} (+ "username" khi key admin phụ chưa ai dùng) + HWID thiết bị (header X-HWID hoặc "hwid" trong body).
       Server tự phân loại: key admin phụ · key người dùng (không vào được trang admin) · mật khẩu admin chính · không tồn tại.
       Trả luôn "kind": main | sub | user | none | locked. (Còn nhận cả {"password"} cũ cho tool đã viết từ trước.)
       Admin chính (mật khẩu) không cần HWID. Key admin phụ: gắn thêm thiết bị nếu còn chỗ (max_dev), đủ chỗ rồi -> dev_locked."""
    ip = client_ip()
    w = _rl_wait(ip)
    if w:
        return _json({"ok": False, "kind": "locked", "loi": f"Nhập sai quá nhiều, thử lại sau {w} giây."}, 429)
    if not _rate_ok(f"adm-ip:{ip}", 20) or not _rate_ok("adm-all", 1200):      # PBKDF2 200k vòng / lần -> chặn dội login làm cạn CPU (theo IP + toàn cục)
        return _json({"ok": False, "kind": "locked", "loi": "Quá nhiều lần đăng nhập, thử lại sau ít phút."}, 429)
    b = request.get_json(silent=True) or {}
    raw = str(b.get("key") or b.get("password") or "")[:128]
    k = _norm_key(raw)
    hw, alts, hfresh = req_hw_ids(b)
    ua = request.headers.get("User-Agent", "")
    now = int(time.time())
    with _kv_lock:
        d = _kv_load()
        rec = d["keys"].get(k) if k else None
        if rec:                                          # key có trong file -> phân loại theo type
            if _is_expired(rec, now):
                return _json({"ok": False, "kind": rec.get("type"), "loi": "Key này đã hết hạn."}, 403)
            if rec.get("type") != "sub":
                return _json({"ok": False, "kind": "user", "loi": "Key hợp lệ nhưng chỉ dùng để vào tool ở panel /api/html, không phải key admin."}, 403)
            if not hw:
                return _json({"ok": False, "kind": "sub", "loi": "Thiếu mã thiết bị (HWID) — hãy mở trang /api/admin bằng trình duyệt, hoặc tool phải gửi header X-HWID."}, 400)
            fresh = False
            if not rec.get("owner"):                     # key admin phụ chưa ai dùng -> nhập username, gắn username + thiết bị đầu tiên
                if not str(b.get("username") or "").strip():
                    return _json({"ok": False, "kind": "sub", "need_username": True, "loi": "Nhập username để kích hoạt. Key sẽ gắn với username này và thiết bị (HWID) bạn đang dùng."})
                name = _clean_username(b.get("username"))
                if not name:
                    return _json({"ok": False, "kind": "sub", "need_username": True, "loi": "Username 2-20 ký tự (chữ, số, dấu cách . _ -), không dùng 'admin'."}, 400)
                if any(r.get("type") == "sub" and str(r.get("owner") or "").lower() == name.lower() for r in d["keys"].values()):
                    return _json({"ok": False, "kind": "sub", "need_username": True, "loi": "Username này đã có người dùng, chọn tên khác."}, 400)
                rec["owner"], rec["bound"] = name, now
                fresh = True
            ok, err, ch = _dev_use(rec, hw, ip, ua, now, alts, hfresh)  # thiết bị đã gắn -> cho vào · chưa gắn mà còn chỗ -> gắn thêm · hết chỗ -> chặn tới khi admin chính reset
            if not ok:
                _rl_fail(ip)
                return _json({"ok": False, "kind": "sub", "dev_locked": True, "loi": err}, 403)
            if _activate(rec, now):                      # đăng nhập thành công lần đầu -> bắt đầu tính hạn key admin phụ
                ch = True
            if ch or fresh:
                try:
                    _kv_save(d)
                except OSError as e:
                    return _json({"ok": False, "kind": "sub", "loi": f"Không ghi được file key: {e}"}, 500)
            name = rec["owner"]
            _rl_reset(ip)
            return _json({"ok": True, "kind": "sub", "role": "sub", "name": name, "dev": len(rec.get("devs") or {}), "max_dev": _max_dev(rec),
                          **_tok_pair("sub", name, k, hw)})
    if raw and ADMIN_PASS_HASH and hmac.compare_digest(_pw_hash(raw), ADMIN_PASS_HASH):   # không phải key trong file -> thử mật khẩu admin chính
        _rl_reset(ip)
        _audit("login_main_ok")
        return _json({"ok": True, "kind": "main", "role": "main", "name": ADMIN_MAIN_NAME, **_tok_pair("main", ADMIN_MAIN_NAME)})
    _rl_fail(ip)
    _audit("login_fail")
    return _json({"ok": False, "kind": "none", "loi": "Không có key nào khớp (hoặc sai mật khẩu admin chính)."}, 403)


@app.route("/api/admin/logout", methods=["POST"])
def api_admin_logout():
    s = _tok_check()
    if s:
        with _sess_lock:
            _sess.pop(s["sh"], None)
        _audit("logout", role=s["r"])
    return _json({"ok": True})


def _need_admin():
    s = _tok_check()
    return s, (None if s else _json({"ok": False, "loi": "chua dang nhap / phien het han"}, 401))


@app.route("/api/admin/keys")
def api_admin_keys():
    s, err = _need_admin()
    if err:
        return err
    now = time.time()
    keys = _kv_load()["keys"]
    made = {}
    for r in keys.values():
        if r.get("by") == "sub":
            made[r.get("by_name")] = made.get(r.get("by_name"), 0) + 1
    rows = []
    for k, r in keys.items():
        if s["r"] != "main" and not _own_user_key(s, r):
            continue                                    # admin phụ chỉ thấy key người dùng do chính mình tạo
        devs = r.get("devs") if isinstance(r.get("devs"), dict) else {}
        tb = sorted(({"hw": h, "lan_dau": v.get("first"), "gan_nhat": v.get("last"), "ip": v.get("ip"), "ua": v.get("ua", "")} for h, v in devs.items()),
                    key=lambda x: -(x["gan_nhat"] or 0))
        act = _activated(r)
        rows.append({"key": k, "loai": r.get("type"), "nguoi_tao": r.get("by_name"), "tao_luc": r.get("created"), "het_han": (r["exp"] if act else None),
                     "con_lai": _left_sec(r, now), "het": _is_expired(r, now), "ngay": r.get("days"), "ghi_chu": r.get("note", ""), "cong_gio": _bonus(r),
                     "kich_hoat": act, "kich_hoat_luc": (r.get("act") or None),               # kich_hoat=False: chưa ai dùng -> hạn chưa chạy
                     "dung_boi": r.get("owner"), "da_tao": made.get(r.get("owner"), 0) if r.get("type") == "sub" else None,
                     "max_dev": _max_dev(r), "so_dev": len(devs), "dung_luc": r.get("last"), "ip_cuoi": r.get("last_ip"), "thiet_bi": tb,
                     "game": _key_game(r) if r.get("type") == "user" else None,                                   # sun | hit | all (key cũ chưa gán game)
                     "game_cu": r.get("type") == "user" and str(r.get("game") or "").lower() not in KEY_GAMES + _KEY_DEAD_GAMES})   # True = key tạo trước khi có chia game
    rows.sort(key=lambda x: -(x["tao_luc"] or 0))
    return _json({"ok": True, "role": s["r"], "name": s["n"], "ngay": list(KEY_DAYS), "so_tb": list(KEY_DEV_OPTIONS),
                  "games": [{"id": g, "ten": KEY_GAME_LABEL[g]} for g in KEY_GAMES], "keys": rows})


@app.route("/api/admin/revenue")
def api_admin_revenue():
    """Doanh thu tự tính theo giá KEY_PRICE khi key được kích hoạt (Sun · Hit · LC79): 1 ngày / 1 tuần / 1 tháng. CHỈ ADMIN CHÍNH — admin phụ và key người dùng đều bị từ chối."""
    s, err = _need_admin()
    if err:
        return err
    if s["r"] != "main":
        return _json({"ok": False, "loi": "chi admin chinh moi xem duoc doanh thu"}, 403)
    now = int(time.time())
    with _kv_lock:
        d = _kv_load()
    return _json({"ok": True, "don_vi": "VND", "bang_gia": {str(k): v for k, v in sorted(KEY_PRICE.items())},
                  "games": [{"id": g, "ten": KEY_GAME_LABEL[g]} for g in KEY_GAMES], "doanh_thu": _revenue_calc(d, now)})


@app.route("/api/admin/keys/create", methods=["POST"])
def api_admin_keys_create():
    s, err = _need_admin()
    if err:
        return err
    b = request.get_json(silent=True) or {}
    kind = "sub" if b.get("type") == "sub" else "user"
    if kind == "sub" and s["r"] != "main":
        return _json({"ok": False, "loi": "chi admin chinh moi tao duoc key admin phu"}, 403)
    game = str(b.get("game") or "").strip().lower()
    game = "lc79" if game == "tele68" else game
    if kind == "user" and game not in KEY_GAMES:       # key người dùng PHẢI chọn đúng 1 game (không có key gộp chung)
        return _json({"ok": False, "loi": "chua chon game cho key (sun, hit, lc79 hoac autolc)"}, 400)
    try:
        days = int(b.get("days"))
    except (TypeError, ValueError):
        days = 0
    if days not in KEY_DAYS:
        return _json({"ok": False, "loi": "han key khong hop le"}, 400)
    try:
        mdev = int(b.get("max_dev", KEY_DEV_DEFAULT))
    except (TypeError, ValueError):
        mdev = 0
    if mdev not in KEY_DEV_OPTIONS:
        return _json({"ok": False, "loi": "so thiet bi khong hop le"}, 400)
    try:
        cnt = max(1, min(int(b.get("count", 1)), 20))
    except (TypeError, ValueError):
        cnt = 1
    note = re.sub(r"[\x00-\x1f\x7f]", " ", str(b.get("note") or "")).strip()[:40]
    bonus = _parse_dur(b, "bonus_amount", "bonus_unit", "bonus_hours")      # tặng thêm thời gian ngay lúc tạo (cộng vào hạn khi key kích hoạt)
    if (b.get("bonus_amount") or b.get("bonus_hours")) and not bonus:
        return _json({"ok": False, "loi": "thoi gian tang them khong hop le"}, 400)
    now = int(time.time())
    with _kv_lock:
        d = _kv_load()
        if len(d["keys"]) + cnt > KEY_MAX_TOTAL:
            return _json({"ok": False, "loi": "day file key, xoa bot key het han"}, 400)
        made = []
        for _ in range(cnt):
            k = _new_key("AD" if kind == "sub" else KEY_PREFIX[game], d["keys"])
            d["keys"][k] = {"type": kind, "by": s["r"], "by_name": s["n"], "created": now, "exp": (0 if KEY_START_ON_ACTIVATE else now + days * 86400 + bonus),
                            "days": days, "note": note, "owner": None, "max_dev": mdev, "devs": {}}
            if bonus:
                d["keys"][k]["bonus"] = bonus
            if KEY_START_ON_ACTIVATE:
                d["keys"][k]["act"] = 0                  # 0 = CHƯA KÍCH HOẠT: hạn (exp) chỉ được tính khi key được dùng thành công lần đầu
            if kind == "user":
                d["keys"][k]["game"] = game
            made.append(k)
        try:
            _kv_save(d)
        except OSError as e:
            return _json({"ok": False, "loi": f"khong ghi duoc file key: {e}"}, 500)
    return _json({"ok": True, "keys": made, "het_han": (None if KEY_START_ON_ACTIVATE else now + days * 86400), "tinh_han_tu_kich_hoat": KEY_START_ON_ACTIVATE, "ngay": days, "max_dev": mdev, "game": game if kind == "user" else None})


@app.route("/api/admin/keys/delete", methods=["POST"])
def api_admin_keys_delete():
    """Xóa 1 key {"key": "..."} · NHIỀU key {"keys": ["...", ...]} (admin phụ: key không phải của mình bị bỏ qua, đếm ở "bo_qua") · {"expired": true} (admin chính: dọn key hết hạn)."""
    s, err = _need_admin()
    if err:
        return err
    b = request.get_json(silent=True) or {}
    now = time.time()
    skipped = 0
    with _kv_lock:
        d = _kv_load()
        keys = d["keys"]
        if b.get("expired") and s["r"] == "main":        # dọn mọi key hết hạn
            dead = [k for k, r in keys.items() if _is_expired(r, now)]
        else:
            lst = b.get("keys") if isinstance(b.get("keys"), list) else [b.get("key")]
            want = list(dict.fromkeys(x for x in (_norm_key(v) for v in lst[:KEY_MAX_TOTAL]) if x))
            if not want:
                return _json({"ok": False, "loi": "chua chon key nao"}, 400)
            dead, miss, denied = [], 0, 0
            for k in want:
                r = keys.get(k)
                if not r:
                    miss += 1
                elif not _own_user_key(s, r):
                    denied += 1
                else:
                    dead.append(k)
            skipped = miss + denied
            if not dead:
                return (_json({"ok": False, "loi": "chi xoa duoc key do ban tao"}, 403) if denied
                        else _json({"ok": False, "loi": "khong thay key"}, 404))
        for k in dead:
            keys.pop(k, None)
        try:
            _kv_save(d)
        except OSError as e:
            return _json({"ok": False, "loi": f"khong ghi duoc file key: {e}"}, 500)
    return _json({"ok": True, "da_xoa": len(dead), "bo_qua": skipped})


@app.route("/api/admin/keys/reset-dev", methods=["POST"])
@app.route("/api/admin/keys/reset-ip", methods=["POST"])    # tên cũ — giữ để tool đã viết từ trước không hỏng
def api_admin_keys_reset_dev():
    """Gỡ thiết bị đã gắn của 1 key: {"key": "..."} = gỡ TOÀN BỘ (máy nào dùng key trước sẽ được gắn lại) · thêm "hwid" = chỉ gỡ thiết bị đó.
    Admin chính: mọi key · admin phụ: key người dùng do mình tạo. Phiên admin phụ chạy trên thiết bị bị gỡ chết ngay vì _tok_check đòi HWID vẫn đang gắn."""
    s, err = _need_admin()
    if err:
        return err
    b = request.get_json(silent=True) or {}
    k = _norm_key(b.get("key"))
    hw = ""
    if b.get("hwid"):
        hw = _norm_hwid(b.get("hwid"))
        if not hw:
            return _json({"ok": False, "loi": "hwid khong hop le"}, 400)
    with _kv_lock:
        d = _kv_load()
        rec = d["keys"].get(k)
        if not rec:
            return _json({"ok": False, "loi": "khong thay key"}, 404)
        if not _own_user_key(s, rec):
            return _json({"ok": False, "loi": "chi reset duoc key do ban tao"}, 403)
        devs = rec.get("devs") if isinstance(rec.get("devs"), dict) else {}
        if hw:
            if hw not in devs:
                return _json({"ok": False, "loi": "khong thay thiet bi nay trong key"}, 404)
            devs.pop(hw)
            n = 1
        else:
            n = len(devs)
            devs = {}
        rec["devs"] = devs
        rec.pop("ip", None)                              # dọn trường IP của bản cũ (gắn theo IP mạng)
        rec.pop("ip_at", None)
        rec["dev_reset"] = int(time.time())
        try:
            _kv_save(d)
        except OSError as e:
            return _json({"ok": False, "loi": f"khong ghi duoc file key: {e}"}, 500)
    return _json({"ok": True, "da_go": n})


@app.route("/api/admin/keys/add-time", methods=["POST"])
def api_admin_keys_add_time():
    """CỘNG GIỜ cho key: {"key": "..."} hoặc {"keys": [...]} + {"amount": N, "unit": "hour"|"day"|"week"|"month"} (tháng = 30 ngày; "hours": N vẫn nhận).
    Admin chính: mọi key (kể cả key admin phụ) · admin phụ: key người dùng do chính mình tạo. Key đã hết hạn được tính lại từ bây giờ.
    Key chưa kích hoạt: giờ cộng được giữ lại và áp dụng khi key kích hoạt. Không đổi doanh thu (giá đã chốt lúc kích hoạt)."""
    s, err = _need_admin()
    if err:
        return err
    b = request.get_json(silent=True) or {}
    if b.get("amount") is None and b.get("hours") is None:
        b = dict(b, hours=1)
    secs = _parse_dur(b)
    if not secs:
        return _json({"ok": False, "loi": f"thoi gian khong hop le (so nguyen duong + don vi hour|day|week|month, toi da {ADD_MAX_SEC // 86400} ngay moi lan)"}, 400)
    lst = b.get("keys") if isinstance(b.get("keys"), list) else [b.get("key")]
    want = list(dict.fromkeys(x for x in (_norm_key(v) for v in lst[:KEY_MAX_TOTAL]) if x))
    if not want:
        return _json({"ok": False, "loi": "chua chon key nao"}, 400)
    now = int(time.time())
    out, skipped = {}, 0
    with _kv_lock:
        d = _kv_load()
        for k in want:
            r = d["keys"].get(k)
            if not r or not _own_user_key(s, r):
                skipped += 1
                continue
            if _bonus(r) + secs > BONUS_MAX_SEC:
                skipped += 1
                continue
            _add_time(r, secs, now)
            act = _activated(r)
            out[k] = {"het_han": (int(r["exp"]) if act else None), "con_lai": _left_sec(r, now), "het": _is_expired(r, now), "kich_hoat": act, "cong_gio": _bonus(r)}
        if not out:
            return _json({"ok": False, "loi": "khong cong gio duoc (chi cong cho key do ban tao)"}, 403 if skipped else 404)
        try:
            _kv_save(d)
        except OSError as e:
            return _json({"ok": False, "loi": f"khong ghi duoc file key: {e}"}, 500)
    _audit("add_time", role=s["r"], n=len(out), giay=secs)
    return _json({"ok": True, "da_cong": len(out), "bo_qua": skipped, "giay": secs, "ket_qua": out})


# ─ DUYỆT THIẾT BỊ VÀO PANEL /api/html — CHỈ ADMIN CHÍNH (xem khối "DUYỆT THIẾT BỊ VÀO PANEL" ở trên) ─
def _need_main():
    s, err = _need_admin()
    if err:
        return None, err
    if s["r"] != "main":
        return None, _json({"ok": False, "loi": "chi admin chinh moi duyet duoc thiet bi vao panel"}, 403)
    return s, None


@app.route("/api/admin/panel")
def api_admin_panel():
    """Danh sách thiết bị đã xin vào panel: chờ duyệt (lên đầu) · đã duyệt · từ chối."""
    s, err = _need_main()
    if err:
        return err
    with _pv_lock:
        _d = _pv_load()
        devs, bans = _d["devs"], _d.get("bans") or {}
        rows = [{"hw": h, "trang_thai": v.get("st"), "lan_dau": v.get("first"), "gan_nhat": v.get("last"), "ip": v.get("ip"), "ua": v.get("ua", ""),
                 "duyet_luc": v.get("dec_at"), "duyet_boi": v.get("dec_by"),
                 "ip_chan": [i for i, b in (bans or {}).items() if b.get("hw") == h]} for h, v in devs.items()]
    order = {"pending": 0, "approved": 1, "denied": 2, "banned": 3}
    rows.sort(key=lambda r: (order.get(r["trang_thai"], 9), -(r["gan_nhat"] or 0)))
    return _json({"ok": True, "devices": rows})


def _panel_admin_act(act):
    """approve / deny / remove cho 1 thiết bị {"hwid": "..."} hoặc nhiều {"hwids": [...]}. remove = xóa khỏi danh sách (đang được duyệt thì mất quyền ngay, phải xin lại)."""
    s, err = _need_main()
    if err:
        return err
    b = request.get_json(silent=True) or {}
    lst = b.get("hwids") if isinstance(b.get("hwids"), list) else [b.get("hwid")]
    want = list(dict.fromkeys(x for x in (_norm_hwid(v) for v in lst[:500]) if x))
    if not want:
        return _json({"ok": False, "loi": "hwid khong hop le"}, 400)
    now = int(time.time())
    done = 0
    ipn = 0
    with _pv_lock:
        d = _pv_load()
        devs = d["devs"]
        for h in want:
            rec = devs.get(h)
            if not rec:
                continue
            if act in ("remove", "unban"):
                bans = d.get("bans")
                if isinstance(bans, dict):                      # gỡ luôn IP đã bị ban cùng thiết bị này
                    for i in [i for i, b in bans.items() if b.get("hw") == h or i == rec.get("ip")]:
                        del bans[i]
                        ipn += 1
                del devs[h]
            elif act == "ban":
                rec["st"] = "banned"
                rec["dec_at"], rec["dec_by"] = now, s["n"]
                ip = str(rec.get("ip") or "")
                if ip and ip != "unknown":                      # không ban IP "unknown" (sẽ chặn nhầm tất cả)
                    d.setdefault("bans", {})[ip] = {"at": now, "by": s["n"], "hw": h}
                    ipn += 1
            else:
                rec["st"] = "approved" if act == "approve" else "denied"
                rec["dec_at"], rec["dec_by"] = now, s["n"]
            done += 1
        if not done:
            return _json({"ok": False, "loi": "khong thay thiet bi"}, 404)
        if not _pv_save(d):
            return _json({"ok": False, "loi": "khong ghi duoc file thiet bi panel"}, 500)
    return _json({"ok": True, "da_xu_ly": done, "ip_da_xu_ly": ipn})


@app.route("/api/admin/panel/approve", methods=["POST"])
def api_admin_panel_approve():
    return _panel_admin_act("approve")


@app.route("/api/admin/panel/deny", methods=["POST"])
def api_admin_panel_deny():
    return _panel_admin_act("deny")


@app.route("/api/admin/panel/remove", methods=["POST"])
def api_admin_panel_remove():
    return _panel_admin_act("remove")


@app.route("/api/admin/panel/ban", methods=["POST"])
def api_admin_panel_ban():
    return _panel_admin_act("ban")


@app.route("/api/admin/panel/unban", methods=["POST"])
def api_admin_panel_unban():
    return _panel_admin_act("unban")


ADMIN_HTML = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#2540ff">
<title>SUNVIW Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#eceff6;--pn:#fff;--pn2:#f4f6fb;--ink:#10121c;--mu:#626b82;--ln:#dde1ec;--ac:#2540ff;--ac2:#e5e9ff;--on:#fff;--ok:#0c9a6b;--wa:#c97a00;--no:#dc3550;color-scheme:light}
:root[data-t=d]{--bg:#0c0e16;--pn:#151824;--pn2:#1c2030;--ink:#eef0fa;--mu:#8f97b3;--ln:#272c42;--ac:#8d9cff;--ac2:#222850;--on:#0c0e16;--ok:#3ccf9c;--wa:#f0a63a;--no:#ff6a80;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.5 "Be Vietnam Pro",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
button,input,select{font:inherit;color:inherit}button{cursor:pointer}:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
.mono{font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace}.mu{color:var(--mu)}.s{font-size:12.5px}b{font-weight:600}
svg{vertical-align:middle;flex:none}
/* khung */
#sh{display:grid;grid-template-columns:208px minmax(0,1fr);min-height:100vh}
nav{position:sticky;top:0;height:100vh;padding:18px 12px;background:var(--pn);border-right:1px solid var(--ln);display:flex;flex-direction:column;gap:4px}
.lg{display:flex;align-items:center;gap:10px;padding:2px 8px 16px;font-weight:800;font-size:17px;letter-spacing:-.01em}
.lg i{width:30px;height:30px;border-radius:9px;background:var(--ac);color:var(--on);display:grid;place-items:center;font-style:normal}
nav button.n{display:flex;align-items:center;gap:10px;height:42px;padding:0 12px;border:0;border-radius:11px;background:none;color:var(--mu);text-align:left;font-weight:500}
nav button.n:hover{background:var(--pn2);color:var(--ink)}nav button.n.on{background:var(--ac2);color:var(--ac);font-weight:600}
nav .bg{margin-left:auto;min-width:20px;height:20px;padding:0 6px;border-radius:99px;background:var(--no);color:#fff;font-size:11.5px;font-weight:700;display:grid;place-items:center}
nav .sp{flex:1}
main{padding:0 22px 90px;min-width:0}
.tp{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:10px;padding:14px 0;background:var(--bg)}
.tp h1{margin:0;font-size:21px;font-weight:800;letter-spacing:-.02em;flex:1}
.ch{display:inline-flex;align-items:center;height:32px;padding:0 12px;border-radius:99px;background:var(--pn);border:1px solid var(--ln);font-size:12.5px;font-weight:600}
.ib,.gh{display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 12px;border-radius:10px;border:1px solid var(--ln);background:var(--pn);transition:border-color .12s}
.ib{width:36px;padding:0;justify-content:center}.gh:hover,.ib:hover{border-color:var(--mu)}.gh.dg{color:var(--no)}.gh.dg:hover{border-color:var(--no)}
.pr{display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 16px;border-radius:10px;border:0;background:var(--ac);color:var(--on);font-weight:600}
.pr:hover{filter:brightness(1.1)}.pr:disabled{opacity:.55}.pr.sm{height:30px;padding:0 11px;font-size:13px}
.sw{position:relative;width:46px;height:26px;border-radius:99px;border:0;background:var(--ln);padding:0;transition:background .15s}
.sw::after{content:"";position:absolute;top:3px;left:3px;width:20px;height:20px;border-radius:50%;background:#fff;transition:transform .15s}.sw.on{background:var(--no)}.sw.on::after{transform:translateX(20px)}
.cd{background:var(--pn);border:1px solid var(--ln);border-radius:16px;padding:18px;margin-bottom:14px}
.cd h2{margin:0 0 12px;font-size:15.5px;font-weight:800}.hd{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px}.hd h2{margin:0;flex:1}
.gd{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.st{background:var(--pn);border:1px solid var(--ln);border-radius:14px;padding:14px 16px}.st b{display:block;font-size:28px;line-height:1.15;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums}.st span{color:var(--mu);font-size:12.5px}
.okc{color:var(--ok)}.noc{color:var(--no)}
.bd{display:inline-flex;align-items:center;gap:5px;height:21px;padding:0 8px;border-radius:99px;font-size:11.5px;font-weight:600;background:var(--pn2);color:var(--mu);white-space:nowrap}
.bd.ok{background:color-mix(in srgb,var(--ok) 16%,transparent);color:var(--ok)}.bd.soon,.bd.wait{background:color-mix(in srgb,var(--wa) 18%,transparent);color:var(--wa)}.bd.ex{background:color-mix(in srgb,var(--no) 16%,transparent);color:var(--no)}
.g::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--gc,var(--mu))}.g-sun{--gc:#e0a100}.g-hit{--gc:#1f9bd1}.g-lc79{--gc:#d6458f}.g-autolc{--gc:#8a5cf5}
/* danh sách key */
.tb{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}.in{height:38px;padding:0 12px;border-radius:10px;border:1px solid var(--ln);background:var(--pn);min-width:0}.in:focus{outline:0;border-color:var(--ac)}.tb .in.q{flex:1 1 220px}
.cp{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}.cp button{height:32px;padding:0 12px;border-radius:99px;border:1px solid var(--ln);background:var(--pn);color:var(--mu);font-size:13px}.cp button.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.sb{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:9px 12px;margin-bottom:8px;border-radius:12px;background:var(--ac2);color:var(--ac)}.sb .sp{flex:1}
.rw{display:grid;grid-template-columns:22px minmax(0,1.6fr) minmax(0,1.2fr) minmax(0,.8fr) auto;gap:6px 16px;align-items:center;padding:12px 8px;border-top:1px solid var(--ln);border-radius:0}
.rw.fl{animation:fl 1.4s ease-out}@keyframes fl{0%{background:color-mix(in srgb,var(--ok) 28%,transparent)}100%{background:transparent}}
.rw input[type=checkbox]{width:17px;height:17px;accent-color:var(--ac);margin:0}
.kc{display:flex;align-items:center;gap:7px;flex-wrap:wrap}.kc .mono{font-size:13px;font-weight:700;letter-spacing:.02em;word-break:break-all}
.ga{height:6px;border-radius:6px;background:var(--pn2);overflow:hidden;margin-bottom:4px}.ga i{display:block;height:100%;border-radius:6px;background:var(--ok);transition:width .5s}.ga i.soon{background:var(--wa)}.ga i.ex{background:var(--no)}
.ra{display:flex;gap:6px;justify-content:flex-end}.em{padding:36px 0;text-align:center;color:var(--mu)}
.pl{display:flex;flex-wrap:wrap;gap:8px}.pl button{height:38px;padding:0 15px;border-radius:11px;border:1px solid var(--ln);background:var(--pn2);color:var(--mu)}.pl button.on{background:var(--ac);color:var(--on);border-color:var(--ac);font-weight:600}
.lb{margin:16px 0 7px;font-weight:600;font-size:13px}.nk{margin-top:14px;padding:6px 12px;border-radius:12px;border:1.5px dashed var(--ok)}.nk div{display:flex;align-items:center;gap:10px;justify-content:space-between;padding:7px 0}
.dr{display:flex;align-items:center;gap:8px 14px;flex-wrap:wrap;padding:8px 10px;margin-top:6px;border-radius:10px;background:var(--pn2)}.dr .mu{flex:1 1 200px}
dialog{border:1px solid var(--ln);border-radius:18px;background:var(--pn);color:var(--ink);padding:0;width:min(560px,94vw);max-height:90vh}dialog::backdrop{background:rgba(5,8,20,.6)}
.di{padding:20px;max-height:88vh;overflow:auto}.di h3{margin:0;font-size:17px;font-weight:800}.di h4{margin:16px 0 8px;font-size:13px;color:var(--mu);font-weight:600}.da{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
.tw{overflow-x:auto;border:1px solid var(--ln);border-radius:12px}table{width:100%;border-collapse:collapse;min-width:620px}th{text-align:left;font-size:12px;color:var(--mu);font-weight:600;padding:9px 12px;border-bottom:1px solid var(--ln)}td{padding:10px 12px;border-bottom:1px solid var(--ln)}tr[data-id]{cursor:pointer}tr[data-id]:hover{background:var(--pn2)}td.r,th.r{text-align:right}
.lo{max-width:420px;margin:12vh auto 0;padding:0 16px}.lo h1{font-size:28px;margin:18px 0 6px;letter-spacing:-.02em}.lo .in{width:100%;height:52px;font-size:16px;margin-top:12px}.lo .pr{width:100%;height:50px;margin-top:12px;justify-content:center;font-size:16px}
.rs{margin-top:14px;padding:12px 14px;border-radius:12px;border:1px solid var(--ln);background:var(--pn)}.rs.bad{border-color:var(--no)}.rs.good{border-color:var(--ok)}.rs.warn{border-color:var(--wa)}
#ts{position:fixed;left:0;right:0;bottom:84px;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:none;z-index:20}#ts div{background:var(--ink);color:var(--bg);border-radius:11px;padding:9px 16px;font-size:13.5px;animation:up .18s ease-out}#ts div.e{background:var(--no);color:#fff}@keyframes up{from{opacity:0;transform:translateY(6px)}}
@media(max-width:860px){#sh{grid-template-columns:1fr}nav{position:fixed;top:auto;bottom:0;left:0;right:0;z-index:8;height:auto;flex-direction:row;padding:6px 6px calc(6px + env(safe-area-inset-bottom));border:0;border-top:1px solid var(--ln);justify-content:space-around;gap:0}
nav .lg,nav .sp{display:none}nav button.n{flex-direction:column;gap:1px;height:50px;padding:0 6px;font-size:10.5px;flex:1;justify-content:center;position:relative}nav .bg{position:absolute;top:2px;right:18%;margin:0}
main{padding:0 14px 90px}.rw{grid-template-columns:22px minmax(0,1fr) auto}.rw>:nth-child(3),.rw>:nth-child(4){grid-column:2/-1}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body>
<div id="app"></div><dialog id="dg"></dialog><div id="ts"></div>
<script>
/*__HWID_JS__*/
const $=s=>document.querySelector(s),esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=t=>t?new Date(t*1000).toLocaleString('vi-VN'):'—',now=()=>Date.now()/1000;
const left=s=>{if(s<=0)return'đã hết hạn';const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return'còn '+(d?d+' ngày '+h+' giờ':h?h+' giờ '+m+' phút':m+' phút')};
const ago=t=>{const s=Math.max(0,now()-t|0);return s<60?'vừa xong':s<3600?(s/60|0)+' phút trước':s<86400?(s/3600|0)+' giờ trước':(s/86400|0)+' ngày trước'};
const shw=h=>String(h).length>14?h.slice(0,8)+'…'+h.slice(-4):h,vnd=n=>Number(n||0).toLocaleString('vi-VN')+' đ',fN=n=>Number(n||0).toLocaleString('vi-VN'),fNet=n=>(n>=0?'+':'')+fN(n);
const GL={sun:'Sun',hit:'Hit',lc79:'LC79',autolc:'Auto cược LC',gb68:'68GB',all:'Mọi game'},DL={1:'1 ngày',2:'2 ngày',3:'3 ngày',7:'1 tuần',14:'2 tuần',30:'1 tháng',60:'2 tháng',90:'3 tháng',180:'6 tháng',365:'1 năm'};
const ic=p=>`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
const I={home:ic('<path d="M3 11 12 3l9 8M5 10v10h14V10"/>'),key:ic('<circle cx="8" cy="15" r="4"/><path d="M10.8 12.2 20 3m-4 4 3 3"/>'),plus:ic('<path d="M12 5v14M5 12h14"/>'),dev:ic('<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>'),bet:ic('<path d="M3 17l6-6 4 4 8-8M14 7h7v7"/>'),rev:ic('<path d="M12 2v20M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
 cp:ic('<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>'),del:ic('<path d="M4 7h16M10 11v6m4-6v6M6 7l1 13h10l1-13M9 7V4h6v3"/>'),rf:ic('<path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7"/>'),out:ic('<path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4M16 8l4 4-4 4M20 12H9"/>'),mo:ic('<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>'),th:ic('<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>'),clk:ic('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>')};
let S=null;try{S=JSON.parse(sessionStorage.getItem('as')||'null')}catch(e){}
let V='ov',KEYS=[],DAYS=[1,3,7,30,60,90],DEVO=[1,2,3,5,10,20,50],GAMES=[{id:'sun'},{id:'hit'},{id:'lc79'},{id:'autolc'}],NEW=[],FL=new Set(),SEL=new Set(),F={t:'all',s:'new',q:''},CF={type:'user',game:'sun',days:30,dev:1,n:1,ba:0,bu:'hour'},PV=[],PF='pending',OS=null,RV=null,AC=null,ACF='all',busy=false,need=false,lastT=0;
const isM=()=>S&&S.role==='main',sleep=ms=>new Promise(r=>setTimeout(r,ms));
function toast(m,bad){const e=document.createElement('div');if(bad)e.className='e';e.textContent=m;$('#ts').appendChild(e);setTimeout(()=>e.remove(),2600)}
function ask(msg,ok){return new Promise(r=>{const d=$('#dg');d.innerHTML=`<div class="di"><p style="margin:0">${esc(msg)}</p><div class="da"><button class="gh" data-x="no">Hủy</button><button class="pr" data-x="ok">${esc(ok||'Xác nhận')}</button></div></div>`;d.onclose=null;d.dataset.ask=1;d.dataset.k='';d._r=r;d.showModal()})}
$('#dg').addEventListener('click',e=>{const d=$('#dg'),x=e.target.dataset&&e.target.dataset.x;if(d.dataset.ask&&x){d.dataset.ask='';d.close();d._r(x==='ok')}else if(e.target===d){const w=d.dataset.ask;d.close();if(w){d.dataset.ask='';d._r(false)}}});
const _hex=b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join(''),_sha=async m=>_hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(m)));
async function _hmac(k,m){const e=new TextEncoder(),ck=await crypto.subtle.importKey('raw',e.encode(k),{name:'HMAC',hash:'SHA-256'},false,['sign']);return _hex(await crypto.subtle.sign('HMAC',ck,e.encode(m)))}
async function api(p,body){
  const s0=S,o={headers:Object.assign({'Content-Type':'application/json'},HWID_HDR)};
  if(s0)o.headers['X-Admin-Token']=s0.token;
  if(body!==undefined){o.method='POST';o.body=JSON.stringify(body)}
  if(s0&&s0.sk){try{const u=new URL(p,location.origin),ts=String(Math.floor(Date.now()/1000)),nn=_hex(crypto.getRandomValues(new Uint8Array(16)));o.headers['X-Ts']=ts;o.headers['X-Nonce']=nn;o.headers['X-Sig']=await _hmac(s0.sk,[(o.method||'GET'),u.pathname+u.search,ts,nn,await _sha(o.body||'')].join('\n'))}catch(e){return{ok:false,loi:'Trình duyệt không hỗ trợ ký request (cần HTTPS).'}}}
  let r,j={};try{r=await fetch(p,o);j=await r.json()}catch(e){j={ok:false,loi:'Không kết nối được server'}}
  if(r&&r.status===401&&S){S=null;sessionStorage.removeItem('as');login0('Phiên đã hết hạn hoặc thiết bị đã bị gỡ khỏi key — nhập key lại.')}
  return j}
/* ── đăng nhập ── */
function res(c,t,d){$('#res').innerHTML=t?`<div class="rs ${c}"><b>${esc(t)}</b>${d?`<div class="mu s">${esc(d)}</div>`:''}</div>`:''}
function login0(msg){need=false;$('#app').innerHTML=`<div class="lo"><div class="lg" style="padding:0"><i>${I.key}</i>SUNVIW Console</div><h1>Đăng nhập quản trị</h1><div class="mu">Một ô duy nhất — hệ thống tự nhận admin chính, admin phụ hay key không hợp lệ.</div>
<input class="in" id="k" type="password" autocomplete="off" spellcheck="false" placeholder="Dán key hoặc mật khẩu admin" autofocus>
<input class="in" id="un" maxlength="20" placeholder="Username cho key admin phụ mới (vd: Dark)" hidden><button class="pr" id="go">Vào console</button><div id="res"></div></div>`;if(msg)res('warn',msg)}
async function login(){
  if(busy)return;const k=$('#k').value.trim();if(!k)return res('bad','Chưa nhập key','Dán key vào ô rồi bấm Vào.');
  busy=true;const b=$('#go');b.disabled=true;const body={key:k};if(need)body.username=$('#un').value.trim();
  const j=await api('/api/admin/login',body);busy=false;b.disabled=false;
  if(j.ok){res('good',j.role==='main'?'Admin chính':'Admin phụ · '+j.name,j.role==='sub'?'Thiết bị gắn key: '+j.dev+'/'+j.max_dev:'');await sleep(400);S={token:j.token,sk:j.sk,role:j.role,name:j.name};sessionStorage.setItem('as',JSON.stringify(S));return boot()}
  if(j.need_username){need=true;$('#un').hidden=false;$('#un').focus();return res('warn','Key admin phụ mới',j.loi)}
  if(j.dev_locked)return res('bad','Key đã đủ số thiết bị',j.loi);
  res(j.kind==='user'?'warn':'bad',{user:'Đây là key người dùng',none:'Không tìm thấy key',locked:'Tạm khóa do nhập sai nhiều lần'}[j.kind]||'Không vào được',j.loi||'')}
/* ── dữ liệu ── */
async function boot(){shell();await loadKeys();if(isM()){loadPv();loadOs();loadRv();loadAc()}}
async function loadKeys(){const j=await api('/api/admin/keys');if(!S)return;if(j.ok){KEYS=j.keys;lastT=now();DAYS=j.ngay||DAYS;DEVO=j.so_tb||DEVO;GAMES=j.games||GAMES;const h=new Set(KEYS.map(r=>r.key));SEL=new Set([...SEL].filter(k=>h.has(k)))}paint()}
async function loadPv(){const j=await api('/api/admin/panel');if(S&&j.ok){PV=j.devices;paint()}}
async function loadOs(){const j=await api('/api/admin/offserver');if(S&&j.ok){OS=j;paint()}}
async function loadRv(){const j=await api('/api/admin/revenue');if(S&&j.ok){RV=j;paint()}}
async function loadAc(){const j=await api('/api/admin/cuocstatus');if(S&&j.ok){AC=j;paint()}}
/* ── helpers key ── */
const lf=r=>r.kich_hoat===false?r.con_lai:Math.max(0,r.het_han-now());
const stt=r=>r.kich_hoat===false?['wait','Chờ kích hoạt']:lf(r)<=0?['ex','Hết hạn']:lf(r)<86400?['soon','Sắp hết']:['ok','Còn hạn'];
const gb=r=>r.loai==='user'?`<span class="bd g g-${esc(r.game)}">${esc(GL[r.game]||r.game)}</span>`:`<span class="bd">Admin phụ</span>`;
function vis(){const q=F.q.toLowerCase();let a=KEYS.filter(r=>{const s=stt(r)[0],t=F.t;
  const m=t==='all'||(t==='live'?s!=='ex':t==='soon'?s==='soon':t==='exp'?s==='ex':t==='wait'?s==='wait':t==='user'||t==='sub'?r.loai===t:r.loai==='user'&&(r.game===t||r.game==='all'));
  return m&&(!q||[r.key,r.nguoi_tao,r.ghi_chu,r.dung_boi,r.ip_cuoi].join(' ').toLowerCase().includes(q))});
  return a.sort(F.s==='soon'?(x,y)=>lf(x)-lf(y):F.s==='used'?(x,y)=>(y.dung_luc||0)-(x.dung_luc||0):(x,y)=>(y.tao_luc||0)-(x.tao_luc||0))}
function row(r){const[s,l]=stt(r),tot=(r.ngay||1)*86400+(r.cong_gio||0),p=Math.min(100,lf(r)/tot*100);
 const tm=r.kich_hoat===false?`<div class="ga"><i style="width:100%"></i></div><span class="s mu">Gói ${DL[r.ngay]||r.ngay+' ngày'} · tính hạn từ lần dùng đầu</span>`:`<div class="ga"><i class="${s==='ok'?'':s}" style="width:${p}%"></i></div><span class="s" data-l="${r.het_han}">${esc(left(lf(r)))}</span> <span class="s mu">· ${esc(fmt(r.het_han))}</span>`;
 return `<div class="rw${FL.has(r.key)?' fl':''}"><input type="checkbox" data-sel="${esc(r.key)}"${SEL.has(r.key)?' checked':''} aria-label="Chọn key">
 <div><div class="kc"><span class="mono">${esc(r.key)}</span></div><div class="kc" style="margin-top:4px">${gb(r)}<span class="bd ${s}">${l}</span>${r.cong_gio?`<span class="bd ok">+${+(r.cong_gio/3600).toFixed(1)} giờ</span>`:''}</div></div>
 <div>${tm}</div><div class="s"><span class="bd">${r.so_dev}/${r.max_dev} máy</span><div class="mu">${r.dung_luc?esc(ago(r.dung_luc)):'chưa dùng'}</div></div>
 <div class="ra"><button class="pr sm" data-a="add" data-k="${esc(r.key)}" data-h="1" title="Cộng thêm 1 giờ">${I.clk} +1 giờ</button><button class="ib" data-a="open" data-k="${esc(r.key)}" aria-label="Chi tiết">${I.mo}</button></div></div>`}
function renderKeys(){const a=vis(),n=SEL.size,m=isM(),c=(f,t)=>`<button data-f="${f}" class="${F.t===f?'on':''}">${t}</button>`;
 const live=KEYS.filter(r=>stt(r)[0]!=='ex').length;
 return `<div class="tb"><input class="in q" id="fq" placeholder="Tìm key, ghi chú, người tạo…  ( / )" value="${esc(F.q)}"><select class="in" id="fs"><option value="new">Mới tạo trước</option><option value="soon"${F.s==='soon'?' selected':''}>Sắp hết hạn trước</option><option value="used"${F.s==='used'?' selected':''}>Dùng gần nhất</option></select><button class="gh" data-a="rf">${I.rf}</button><button class="gh" data-a="csv">Xuất CSV</button>${m?`<button class="gh dg" data-a="clean">${I.del} Dọn key hết hạn</button>`:''}</div>
 <div class="cp">${c('all','Tất cả '+KEYS.length)}${c('live','Còn hạn '+live)}${c('soon','Sắp hết (&lt;24h)')}${c('exp','Hết hạn')}${c('wait','Chờ kích hoạt')}${GAMES.map(g=>c(g.id,esc(GL[g.id]||g.id))).join('')}${m?c('user','Key người dùng')+c('sub','Admin phụ'):''}</div>
 <div class="sb"><label><input type="checkbox" id="sa"${a.length&&a.every(r=>SEL.has(r.key))?' checked':''}> Chọn ${a.length} key đang hiện</label><span class="sp"></span>${n?`<b>${n} đã chọn</b><button class="pr sm" data-a="badd" data-h="1">${I.clk} +1 giờ</button><button class="gh" data-a="baddc">${I.clk} Cộng tùy chọn…</button><button class="gh" data-a="bcp">${I.cp}</button><button class="gh dg" data-a="bdel">${I.del} Xóa</button>`:'<span class="s">Tích chọn nhiều key để cộng giờ / xóa hàng loạt</span>'}</div>
 <div class="cd" style="padding:4px 10px">${a.length?a.map(row).join(''):`<div class="em">${KEYS.length?'Không có key khớp bộ lọc.':'Chưa có key. Sang tab Tạo key.'}</div>`}</div>`}
function openKey(k){const r=KEYS.find(x=>x.key===k);if(!r)return;const d=$('#dg'),[s,l]=stt(r);d.dataset.ask='';d.dataset.k=k;
 d.innerHTML=`<div class="di"><div class="hd"><h3 class="mono" style="word-break:break-all">${esc(r.key)}</h3><button class="ib" data-x="c">✕</button></div><div class="kc">${gb(r)}<span class="bd ${s}">${l}</span><span class="bd">${r.so_dev}/${r.max_dev} máy</span></div>
 <p class="s" style="margin:10px 0 0">${r.kich_hoat===false?'Chưa kích hoạt — hạn '+(DL[r.ngay]||r.ngay+' ngày')+' tính từ lần dùng đầu.':'<b>'+esc(left(lf(r)))+'</b> · hết hạn '+esc(fmt(r.het_han))}${r.cong_gio?`<br><span class="okc">Đã cộng tổng ${+(r.cong_gio/3600).toFixed(1)} giờ.</span>`:''}</p>
 <p class="s mu" style="margin:4px 0 0">${isM()&&r.nguoi_tao?'Tạo bởi '+esc(r.nguoi_tao)+' · ':''}tạo ${esc(fmt(r.tao_luc))}${r.dung_boi?' · dùng bởi '+esc(r.dung_boi):''}${r.ghi_chu?' · “'+esc(r.ghi_chu)+'”':''}</p>
 <h4>Cộng thời gian</h4><div class="pl">${[[1,'hour','giờ'],[6,'hour','giờ'],[1,'day','ngày'],[1,'week','tuần'],[1,'month','tháng']].map(q=>`<button data-a="add" data-k="${esc(r.key)}" data-h="${q[0]}" data-u="${q[1]}">+${q[0]} ${q[2]}</button>`).join('')}<button class="pr" data-a="addc" data-k="${esc(r.key)}">Tùy chọn…</button></div>
 <h4>Thiết bị đã gắn (${r.so_dev}/${r.max_dev})</h4>${(r.thiet_bi||[]).map(t=>`<div class="dr"><span class="mono s" title="${esc(t.hw)}">${esc(shw(t.hw))}</span><span class="mu s">IP ${esc(t.ip||'?')} · dùng ${esc(ago(t.gan_nhat))}</span><button class="gh dg" data-a="rd" data-k="${esc(r.key)}" data-w="${esc(t.hw)}">Gỡ</button></div>`).join('')||'<div class="s mu">Chưa có thiết bị.</div>'}
 <div class="da" style="justify-content:flex-start;flex-wrap:wrap"><button class="gh" data-a="cp" data-v="${esc(r.key)}">${I.cp} Sao chép</button>${r.so_dev?`<button class="gh" data-a="rs" data-k="${esc(r.key)}">Reset thiết bị</button>`:''}<button class="gh dg" data-a="del" data-k="${esc(r.key)}">${I.del} Xóa key</button></div></div>`;
 if(!d.open)d.showModal()}
/* ── view ── */
function vOv(){const live=KEYS.filter(r=>stt(r)[0]!=='ex').length,soon=KEYS.filter(r=>stt(r)[0]==='soon').sort((a,b)=>lf(a)-lf(b)),pend=PV.filter(x=>x.trang_thai==='pending').length,dv=KEYS.reduce((n,r)=>n+r.so_dev,0);
 const by=g=>KEYS.filter(r=>r.loai==='user'&&r.game===g).length;
 return `<div class="gd"><div class="st"><b>${live}</b><span>Key còn hạn / ${KEYS.length}</span></div><div class="st"><b class="${soon.length?'noc':''}">${soon.length}</b><span>Sắp hết hạn (&lt;24h)</span></div><div class="st"><b>${dv}</b><span>Thiết bị đang gắn</span></div>${isM()?`<div class="st"><b class="${pend?'noc':''}">${pend}</b><span>Thiết bị chờ duyệt</span></div>`:''}</div>
 <div class="cd"><div class="hd"><h2>Cần gia hạn ngay</h2>${soon.length?`<button class="pr sm" data-a="allsoon">${I.clk} +1 giờ cho cả ${soon.length} key</button>`:''}</div>${soon.length?soon.slice(0,8).map(row).join(''):'<div class="em">Không có key nào sắp hết hạn.</div>'}</div>
 <div class="cd"><h2>Key theo game</h2><div class="pl">${GAMES.map(g=>`<span class="bd g g-${esc(g.id)}" style="height:30px;padding:0 12px;font-size:13px">${esc(GL[g.id]||g.id)} · ${by(g.id)}</span>`).join('')}</div></div>
 ${isM()&&RV?`<div class="cd"><h2>Doanh thu</h2><div class="gd" style="margin:0">${[['ngay','24 giờ'],['tuan','7 ngày'],['thang','30 ngày']].map(([k,t])=>`<div class="st"><b style="font-size:21px">${vnd(RV.doanh_thu[k].tong)}</b><span>${t} · ${RV.doanh_thu[k].so_key} key</span></div>`).join('')}</div></div>`:''}`}
function vMk(){const m=isM(),pb=(id,arr,cur,lab)=>`<div class="pl" id="${id}">${arr.map(v=>`<button data-c="${id}" data-v="${esc(v)}" class="${v==cur?'on':''}">${esc(lab(v))}</button>`).join('')}</div>`;
 return `<div class="cd"><h2>Tạo key mới</h2>${m?`<div class="lb">Loại key</div>${pb('type',['user','sub'],CF.type,v=>v==='user'?'Key người dùng':'Key admin phụ')}`:''}
 ${CF.type==='user'?`<div class="lb">Game <span class="mu s">— mỗi key chỉ dùng cho 1 game</span></div>${pb('game',GAMES.map(g=>g.id),CF.game,v=>GL[v]||v)}`:''}
 <div class="lb">Thời hạn <span class="mu s">— tính từ lần dùng đầu tiên</span></div>${pb('days',DAYS,CF.days,v=>DL[v]||v+' ngày')}
 <div class="lb">Tặng thêm thời gian <span class="mu s">— cộng vào hạn khi key được kích hoạt</span></div><div class="tb" style="margin:0"><input class="in" id="cba" type="number" min="0" max="99999" value="${CF.ba}" style="width:110px"><select class="in" id="cbu">${Object.keys(UL).map(u=>`<option value="${u}"${CF.bu===u?' selected':''}>${UL[u]}</option>`).join('')}</select><span class="s mu" id="cbp" style="align-self:center">${CF.ba>0?'= '+norm(CF.ba*UN[CF.bu]):'Không tặng thêm'}</span></div>
 <div class="lb">Số thiết bị tối đa</div>${pb('dev',DEVO,CF.dev,v=>v+' máy')}
 <div class="tb" style="margin-top:16px"><div class="pl" style="align-items:center"><button class="ib" data-a="n" data-v="-1">−</button><b id="cn" style="min-width:28px;text-align:center">${CF.n}</b><button class="ib" data-a="n" data-v="1">+</button></div><input class="in q" id="cnote" maxlength="40" placeholder="Ghi chú (vd: khách A)"><button class="pr" data-a="mk">Tạo ${CF.n} key</button></div>
 ${NEW.length?`<div class="nk">${NEW.map(k=>`<div><span class="mono">${esc(k)}</span><button class="gh" data-a="cp" data-v="${esc(k)}">${I.cp}</button></div>`).join('')}<div><span class="mu">Cả ${NEW.length} key</span><button class="gh" data-a="cp" data-v="${esc(NEW.join('\n'))}">${I.cp} Sao chép hết</button></div></div>`:''}</div>`}
function pvRow(x){const st=x.trang_thai,bl={pending:'Chờ duyệt',approved:'Đã duyệt',denied:'Từ chối',banned:'Bị ban'}[st]||st,h=esc(x.hw),b=(a,t,c)=>`<button class="${c||'gh'}" data-a="${a}" data-w="${h}">${t}</button>`;
 const act=st==='banned'?b('pu','Bỏ ban'):(st!=='approved'?b('pa','Duyệt','pr sm'):'')+(st==='pending'?b('pd','Từ chối','gh dg'):b('pr','Gỡ quyền','gh dg'))+b('pb','Ban','gh dg');
 return `<div class="rw" style="grid-template-columns:minmax(0,1.4fr) minmax(0,1fr) auto"><div><span class="mono s">${esc(shw(x.hw))}</span> <span class="bd ${st==='approved'?'ok':st==='pending'?'wait':'ex'}">${bl}</span><div class="s mu">${esc((x.ua||'').slice(0,40))} · IP ${esc(x.ip||'?')}</div></div><div class="s"><div>Gửi ${esc(fmt(x.lan_dau))}</div><div class="mu">Thấy ${esc(ago(x.gan_nhat))}</div></div><div class="ra">${act}</div></div>`}
function vPv(){const cnt=s=>PV.filter(x=>x.trang_thai===s).length,rows=PV.filter(x=>PF==='all'||x.trang_thai===PF),p=cnt('pending');
 return `<div class="cd"><div class="hd"><h2>Duyệt thiết bị vào panel HTML</h2>${p?`<button class="pr sm" data-a="pall">Duyệt cả ${p} máy chờ</button>`:''}<button class="gh" data-a="pvrf">${I.rf}</button></div><div class="cp">${['pending','approved','denied','banned','all'].map(f=>`<button data-pf="${f}" class="${PF===f?'on':''}">${{pending:'Chờ duyệt',approved:'Đã duyệt',denied:'Từ chối',banned:'Danh sách đen',all:'Tất cả'}[f]} ${f==='all'?PV.length:cnt(f)}</button>`).join('')}</div>${rows.length?rows.map(pvRow).join(''):'<div class="em">Không có thiết bị ở mục này.</div>'}</div>`}
const ACL={running:'Đang cược',paused:'Pause',hold:'Tạm dừng',ready:'Sẵn sàng',stopped:'Đã dừng',target:'Đạt mục tiêu',nofund:'Hết số dư',wd_stop:'Đã rút',error:'Lỗi',restart:'Cần đăng nhập',expired:'Key hết hạn'};
function vAc(){const all=(AC&&AC.sessions)||[],run=all.filter(s=>s.alive),rows=ACF==='run'?run:ACF==='stop'?all.filter(s=>!s.alive):all,tn=all.reduce((n,s)=>n+s.net,0);
 return `<div class="gd"><div class="st"><b>${all.length}</b><span>Tài khoản</span></div><div class="st"><b>${run.length}</b><span>Đang cược</span></div><div class="st"><b>${fN(all.reduce((n,s)=>n+s.balance,0))}</b><span>Tổng số dư</span></div><div class="st"><b class="${tn>=0?'okc':'noc'}">${fNet(tn)}</b><span>Tổng lãi / lỗ</span></div></div>
 <div class="cd"><div class="hd"><h2>Auto cược LC79</h2><button class="gh" data-a="acrf">${I.rf}</button></div><div class="cp">${[['all','Tất cả'],['run','Đang cược'],['stop','Đã dừng']].map(([f,t])=>`<button data-acf="${f}" class="${ACF===f?'on':''}">${t}</button>`).join('')}</div>
 ${rows.length?`<div class="tw"><table><thead><tr><th>Tài khoản</th><th>Trạng thái</th><th class="r">Số dư</th><th class="r">Lãi / lỗ</th><th class="r">Thắng / thua</th></tr></thead><tbody>${rows.map(s=>`<tr data-id="${esc(s.id)}"><td><b>${esc(s.nick||s.username)}</b><div class="s mu">@${esc(s.username)}</div></td><td><span class="bd ${s.alive?'ok':'ex'}">${esc(ACL[s.status]||s.status)}</span></td><td class="r">${fN(s.balance)}</td><td class="r ${s.net>=0?'okc':'noc'}"><b>${fNet(s.net)}</b></td><td class="r">${s.wins} / ${s.losses}</td></tr>`).join('')}</tbody></table></div>`:`<div class="em">${AC&&!AC.bat?'Auto cược đang tắt.':'Chưa có tài khoản nào.'}</div>`}</div>`}
function openAc(id){const s=((AC&&AC.sessions)||[]).find(x=>x.id===id);if(!s)return;const d=$('#dg');d.dataset.ask='';d.dataset.k='';const c=(v,l,k)=>`<div class="st"><b style="font-size:19px" class="${k||''}">${v}</b><span>${l}</span></div>`;
 d.innerHTML=`<div class="di"><div class="hd"><h3>${esc(s.nick||s.username)}</h3><span class="bd ${s.alive?'ok':'ex'}">${esc(ACL[s.status]||s.status)}</span><button class="ib" data-x="c">✕</button></div><div class="s mu">@${esc(s.username)} · key ${esc(acKey(s.owner))}</div>
 <div class="gd" style="margin-top:12px">${c(fN(s.balance),'Số dư')}${c(fNet(s.net),'Lãi / lỗ',s.net>=0?'okc':'noc')}${c(s.wins+' / '+s.losses,'Thắng / thua')}${c(fN(s.total_bet),'Tổng đã cược')}</div>
 <h4>Chiến thuật</h4><div><b>${esc(s.ten)}</b></div><ul class="s" style="margin:6px 0;padding-left:18px">${(s.chien_thuat||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
 <div class="da" style="justify-content:flex-start">${s.alive?`<button class="gh dg" data-a="acs" data-v="${esc(s.id)}">Dừng auto cược</button>`:''}<button class="gh dg" data-a="acx" data-v="${esc(s.id)}">Xóa tài khoản</button></div></div>`;if(!d.open)d.showModal()}
function vRv(){if(!RV)return'<div class="em">Đang tải…</div>';const W=[['ngay','1 ngày','24 giờ gần nhất'],['tuan','1 tuần','7 ngày gần nhất'],['thang','1 tháng','30 ngày gần nhất']];
 return `<div class="gd">${W.map(([k,t,sub])=>`<div class="st"><b style="font-size:23px">${vnd(RV.doanh_thu[k].tong)}</b><span>${t} · ${RV.doanh_thu[k].so_key} key<br>${sub}</span></div>`).join('')}</div>
 <div class="cd"><div class="hd"><h2>Theo game</h2><button class="gh" data-a="rvrf">${I.rf}</button></div>${W.map(([k,t])=>{const o=RV.doanh_thu[k];return `<p style="margin:6px 0"><b>${t}:</b> ${Object.keys(o.game).filter(g=>g!=='all'||o.game[g].so_key).map(g=>`<span class="bd g g-${esc(g)}">${esc(GL[g]||g)}</span> ${vnd(o.game[g].tien)} <span class="mu s">(${o.game[g].so_key} key)</span>`).join(' &nbsp; ')}</p>`}).join('')}<div class="s mu" style="margin-top:8px">Bảng giá: ${Object.entries(RV.bang_gia).map(([d,p])=>(DL[d]||d+' ngày')+' = '+vnd(p)).join(' · ')}. Giờ cộng thêm không tính vào doanh thu.</div></div>`}
const TABS=[['ov','Tổng quan','home'],['keys','Key','key'],['mk','Tạo key','plus'],['pv','Thiết bị','dev',1],['ac','Auto cược','bet',1],['rv','Doanh thu','rev',1]];
function shell(){const m=isM(),tabs=TABS.filter(t=>m||!t[3]);if(!tabs.some(t=>t[0]===V))V='ov';
 $('#app').innerHTML=`<div id="sh"><nav><div class="lg"><i>${I.key}</i>SUNVIW</div>${tabs.map(t=>`<button class="n${V===t[0]?' on':''}" data-v="${t[0]}">${I[t[2]]}<span>${t[1]}</span>${t[0]==='pv'?'<span class="bg" id="pvb" hidden></span>':''}</button>`).join('')}<div class="sp"></div><button class="n" data-a="th">${I.th}<span>Giao diện</span></button><button class="n" data-a="out">${I.out}<span>Đăng xuất</span></button></nav>
 <main><div class="tp"><h1 id="ttl"></h1>${m?`<span class="s mu" id="osl"></span><button class="sw" id="sw" data-a="os" aria-label="Off server"></button>`:''}<span class="ch">${m?'Admin chính':esc(S.name)}</span></div><div id="vw"></div></main></div>`}
function paint(){if(!$('#vw'))return;const t=TABS.find(x=>x[0]===V);$('#ttl').textContent=t?t[1]:'';
 document.querySelectorAll('nav button.n[data-v]').forEach(b=>b.classList.toggle('on',b.dataset.v===V));
 const pend=PV.filter(x=>x.trang_thai==='pending').length,pb=$('#pvb');if(pb){pb.hidden=!pend;pb.textContent=pend}
 const sw=$('#sw');if(sw&&OS){sw.classList.toggle('on',OS.off);$('#osl').textContent=OS.off?'Off server: tool ngoài bị chặn':'Server online'}
 const f=document.activeElement,keep=f&&f.id==='fq'?f.selectionStart:-1;
 $('#vw').innerHTML=({ov:vOv,keys:renderKeys,mk:vMk,pv:vPv,ac:vAc,rv:vRv}[V]||vOv)();FL=new Set();
 if(keep>=0){const q=$('#fq');if(q){q.focus();q.setSelectionRange(keep,keep)}}}
/* ── thao tác ── */
const UN={hour:3600,day:86400,week:604800,month:2592000},UL={hour:'giờ',day:'ngày',week:'tuần',month:'tháng'},acKey=k=>k?(k.length>16?k.slice(0,7)+'…'+k.slice(-4):k):'—';
let ADDK=[];
const norm=s=>{const p=[];for(const[u,n]of[['month',2592000],['week',604800],['day',86400],['hour',3600]]){const q=Math.floor(s/n);if(q){p.push(q+' '+UL[u]);s-=q*n}}return p.join(' ')||'0'};
function prev(){const el=$('#ap'),a=+($('#aq')||{}).value,u=($('#au')||{}).value;if(!el)return;const s=a*UN[u];
 if(!(Number.isInteger(a)&&a>0&&a<=99999&&s<=31536000)){el.innerHTML='<span class="noc">Nhập số nguyên dương, tối đa 365 ngày mỗi lần.</span>';return}
 const t=norm(s),o=a+' '+UL[u];el.innerHTML='Quy đổi: <b>'+(t===o?o:o+' = '+t)+'</b>';
 if(ADDK.length===1){const r=KEYS.find(x=>x.key===ADDK[0]);if(r&&r.kich_hoat!==false)el.innerHTML+='<br>Hạn mới: <b>'+esc(fmt(Math.max(r.het_han,now())+s))+'</b>'}}
function openAdd(keys){ADDK=keys;const d=$('#dg');d.dataset.ask='';d.dataset.k='';
 d.innerHTML=`<div class="di"><div class="hd"><h3>Cộng thời gian</h3><button class="ib" data-x="c">✕</button></div><div class="s mu">${keys.length===1?'Key '+esc(keys[0]):keys.length+' key đã chọn'}</div>
 <div class="tb" style="margin-top:12px"><input class="in" id="aq" type="number" min="1" max="99999" value="1" style="width:120px"><select class="in" id="au">${Object.keys(UL).map(u=>`<option value="${u}">${UL[u]}</option>`).join('')}</select></div><div class="s" id="ap" style="min-height:42px"></div>
 <div class="da"><button class="gh" data-x="c">Hủy</button><button class="pr" data-a="addgo">Cộng thời gian</button></div></div>`;if(!d.open)d.showModal();prev()}
function cbPrev(){const a=+($('#cba')||{}).value||0,u=$('#cbu').value;CF.ba=a;CF.bu=u;const e=$('#cbp');if(e)e.textContent=a>0?'= '+norm(a*UN[u]):'Không tặng thêm'}
async function addT(keys,amount,unit){const j=await api('/api/admin/keys/add-time',{keys,amount,unit});
 if(j.ok){for(const k in j.ket_qua){const r=KEYS.find(x=>x.key===k);if(r)Object.assign(r,j.ket_qua[k])}FL=new Set(Object.keys(j.ket_qua));paint();toast('Đã cộng '+norm(j.giay)+' cho '+j.da_cong+' key'+(j.bo_qua?' (bỏ qua '+j.bo_qua+')':''));return true}toast(j.loi||'Lỗi',1);return false}
async function act(b){const d=b.dataset,a=d.a,k=d.k,w=d.w,v=d.v;
 if(a==='add'){const ok=await addT([k],+d.h,d.u||'hour'),dl=$('#dg');if(ok&&dl.open&&dl.dataset.k===k)openKey(k);return}
 if(a==='badd')return addT([...SEL],1,'hour');
 if(a==='addc')return openAdd([k]);if(a==='baddc')return openAdd([...SEL]);
 if(a==='addgo'){const ok=await addT(ADDK,+$('#aq').value,$('#au').value);if(ok){if(ADDK.length===1)openKey(ADDK[0]);else $('#dg').close()}return}
 if(a==='allsoon')return addT(KEYS.filter(r=>stt(r)[0]==='soon').map(r=>r.key),1,'hour');
 if(a==='open')return openKey(k);
 if(a==='cp'){try{await navigator.clipboard.writeText(v);toast('Đã sao chép')}catch(e){prompt('Sao chép:',v)}return}
 if(a==='bcp'){try{await navigator.clipboard.writeText([...SEL].join('\n'));toast('Đã sao chép '+SEL.size+' key')}catch(e){}return}
 if(a==='rf'){await loadKeys();return toast('Đã làm mới')}
 if(a==='csv'){const rows=[['key','loai','game','trang_thai','het_han','so_thiet_bi','ghi_chu']].concat(vis().map(r=>[r.key,r.loai,r.game||'',stt(r)[1],r.het_han?new Date(r.het_han*1000).toISOString():'',r.so_dev+'/'+r.max_dev,r.ghi_chu||'']));const u=URL.createObjectURL(new Blob(['\ufeff'+rows.map(x=>x.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\n')],{type:'text/csv'})),l=document.createElement('a');l.href=u;l.download='keys.csv';l.click();return}
 if(a==='n'){CF.n=Math.max(1,Math.min(20,CF.n+(+v)));paint();return}
 if(a==='mk'){const j=await api('/api/admin/keys/create',{type:isM()?CF.type:'user',game:CF.game,days:CF.days,count:CF.n,max_dev:CF.dev,bonus_amount:CF.ba,bonus_unit:CF.bu,note:($('#cnote')||{}).value||''});if(j.ok){NEW=j.keys;await loadKeys();toast('Đã tạo '+j.keys.length+' key')}else toast(j.loi||'Lỗi',1);return}
 if(a==='del'){if(!await ask('Xóa key '+k+'? Người đang dùng sẽ bị đăng xuất ngay.','Xóa key'))return;const j=await api('/api/admin/keys/delete',{key:k});if(j.ok){$('#dg').close();NEW=NEW.filter(x=>x!==k);await loadKeys();toast('Đã xóa key')}else toast(j.loi||'Lỗi',1);return}
 if(a==='bdel'){const ks=[...SEL];if(!await ask('Xóa '+ks.length+' key đã chọn?','Xóa '+ks.length+' key'))return;const j=await api('/api/admin/keys/delete',{keys:ks});if(j.ok){SEL.clear();await loadKeys();toast('Đã xóa '+j.da_xoa+' key')}else toast(j.loi||'Lỗi',1);return}
 if(a==='clean'){if(!await ask('Xóa toàn bộ key đã hết hạn?','Xóa hết'))return;const j=await api('/api/admin/keys/delete',{expired:true});if(j.ok){await loadKeys();toast('Đã xóa '+j.da_xoa+' key')}else toast(j.loi||'Lỗi',1);return}
 if(a==='rs'||a==='rd'){if(!await ask(a==='rs'?'Reset toàn bộ thiết bị của key này?':'Gỡ thiết bị '+shw(w)+' khỏi key?','Gỡ'))return;const j=await api('/api/admin/keys/reset-dev',a==='rs'?{key:k}:{key:k,hwid:w});if(j.ok){await loadKeys();openKey(k);toast('Đã gỡ '+j.da_go+' thiết bị')}else toast(j.loi||'Lỗi',1);return}
 if(a==='pvrf'){await loadPv();return toast('Đã làm mới')}
 if(a==='pall'){const hs=PV.filter(x=>x.trang_thai==='pending').map(x=>x.hw);const j=await api('/api/admin/panel/approve',{hwids:hs});if(j.ok){await loadPv();toast('Đã duyệt '+j.da_xu_ly+' thiết bị')}else toast(j.loi||'Lỗi',1);return}
 if(['pa','pd','pr','pb','pu'].includes(a)){const M={pa:['approve',''],pd:['deny','Từ chối thiết bị này?'],pr:['remove','Gỡ quyền / xóa thiết bị này?'],pb:['ban','Ban thiết bị VÀ IP của nó khỏi /api/html (báo 404)?'],pu:['unban','Bỏ ban thiết bị + IP? Máy phải xin duyệt lại.']}[a];if(M[1]&&!await ask(M[1],'Xác nhận'))return;const j=await api('/api/admin/panel/'+M[0],{hwid:w});if(j.ok){if(a==='pb')PF='banned';await loadPv();toast('Đã xử lý')}else toast(j.loi||'Lỗi',1);return}
 if(a==='os'){const want=!OS.off;if(!await ask(want?'BẬT off server? Tool ngoài sẽ không nhận được dự đoán; panel đã duyệt vẫn chạy.':'TẮT off server? Tool ngoài dùng lại bình thường.','Xác nhận'))return;const j=await api('/api/admin/offserver',{off:want});if(j.ok){OS=j;paint();toast(want?'Đã BẬT off server':'Đã TẮT off server')}else toast(j.loi||'Lỗi',1);return}
 if(a==='rvrf'){await loadRv();return toast('Đã làm mới')}if(a==='acrf'){await loadAc();return toast('Đã làm mới')}
 if(a==='acs'||a==='acx'){if(!await ask(a==='acs'?'Dừng auto cược tài khoản này?':'Xóa tài khoản này khỏi danh sách?','Xác nhận'))return;const j=await api('/api/admin/cuocstatus/action',{id:v,act:a==='acs'?'stop':'remove'});if(j.ok){$('#dg').close();await loadAc();toast('Xong')}else toast(j.loi||'Lỗi',1);return}
 if(a==='th'){const t=document.documentElement.dataset.t==='d'?'l':'d';document.documentElement.dataset.t=t;try{localStorage.setItem('th',t)}catch(e){}return}
 if(a==='out'){try{await api('/api/admin/logout',{})}catch(e){}S=null;sessionStorage.removeItem('as');NEW=[];return login0()}}
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const d=b.dataset;
 if(b.id==='go')return login();if(d.x==='c')return $('#dg').close();
 if(d.v&&b.classList.contains('n')){V=d.v;paint();scrollTo(0,0);return}
 if(d.c){const m={type:'type',game:'game',days:'days',dev:'dev'}[d.c],val=isNaN(d.v)?d.v:+d.v;CF[m]=val;paint();return}
 if(d.f){F.t=d.f;paint();return}if(d.pf){PF=d.pf;paint();return}if(d.acf){ACF=d.acf;paint();return}
 if(d.a)act(b)});
document.addEventListener('click',e=>{const t=e.target.closest('tr[data-id]');if(t)openAc(t.dataset.id)});
document.addEventListener('input',e=>{if(e.target.id==='fq'){F.q=e.target.value;paint()}if(e.target.id==='aq')prev();if(e.target.id==='cba')cbPrev()});
document.addEventListener('change',e=>{const t=e.target;
 if(t.dataset&&t.dataset.sel){t.checked?SEL.add(t.dataset.sel):SEL.delete(t.dataset.sel);paint();return}
 if(t.id==='sa'){vis().forEach(r=>t.checked?SEL.add(r.key):SEL.delete(r.key));paint();return}
 if(t.id==='fs'){F.s=t.value;paint();return}
 if(t.id==='au')prev();if(t.id==='cbu')cbPrev()});
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&['k','un'].includes(e.target.id))login();if(e.key==='/'&&$('#fq')&&!/INPUT|SELECT/.test(document.activeElement.tagName)){e.preventDefault();$('#fq').focus()}});
try{document.documentElement.dataset.t=localStorage.getItem('th')||(matchMedia('(prefers-color-scheme:dark)').matches?'d':'l')}catch(e){}
setInterval(()=>{if(!S||!$('#vw'))return;document.querySelectorAll('[data-l]').forEach(e=>{e.textContent=left(Math.max(0,+e.dataset.l-now()))})},15000);
setInterval(()=>{if(S&&$('#vw')&&!document.hidden)loadKeys()},60000);
setInterval(()=>{if(S&&isM()&&$('#vw')&&!document.hidden){loadPv();loadOs();if(V==='ac')loadAc()}},6000);
if(S)boot();else login0();
</script></body></html>
"""
ADMIN_HTML = ADMIN_HTML.replace("/*__HWID_JS__*/", HWID_JS)


@app.route("/api/ips")
def api_ips():
    """Danh sách IP đang dùng + đã từng dùng (tab IP của panel). Có SUNVIW_ADMIN_KEY thì cần header X-Admin-Key hoặc ?key=."""
    if IP_ADMIN_KEY:
        k = request.headers.get("X-Admin-Key", "")          # chỉ header (không để key trên URL -> khỏi lọt vào log / Referer)
        if not hmac.compare_digest(str(k).encode("utf-8"), IP_ADMIN_KEY.encode("utf-8")):
            return _json({"ok": False, "khoa": True, "loi": "can admin key (header X-Admin-Key hoac ?key=)"}, 403)
    return _json(ip_snapshot(client_ip()))


def _hist_n():
    """?hist=N -> trả thêm lich_su (N ván đúng/sai gần nhất, mới -> cũ). 0 / không truyền = không trả."""
    try:
        return max(0, min(int(request.args.get("hist", 0)), HIST_MAX if _is_panel() else min(HIST_MAX, TOOL_HIST_MAX)))
    except ValueError:
        return 0



# ───────────────────────── 16. PANEL: /api/html chỉ là VỎ; giao diện đầy đủ chỉ cho thiết bị ĐÃ DUYỆT ─────────────────────────
PANEL_SHELL = r'''<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#07080d">
<title>SUNVIW</title>
<style>
html{background:#07080d}body{margin:0;min-height:100vh;display:grid;place-items:center;color:#e8eaf3;font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.b{max-width:380px;text-align:center;padding:28px}.gi{font-size:34px;margin-bottom:8px}.mu{color:#8a90a8}.c{margin-top:16px;font-size:13px;color:#8a90a8}
.sp{width:30px;height:30px;border:3px solid #2a3050;border-top-color:#f2b33d;border-radius:50%;margin:0 auto 14px;animation:r 1s linear infinite}@keyframes r{to{transform:rotate(360deg)}}
</style></head><body><div class="b" id="b"><div class="sp"></div></div>
<script>
(function(){
/*__HWID_JS__*/
const B=document.getElementById('b');let done=false,busy=false,last='';
const M={pending:['<div class="sp"></div>','Đang chờ admin duyệt','Yêu cầu truy cập của thiết bị này đã được gửi tới admin. Trang tự mở ngay khi được duyệt.'],
 denied:['<div class="gi">⛔</div>','Thiết bị bị từ chối','Admin đã từ chối thiết bị này.'],
 limit:['<div class="gi">⚠️</div>','Quá nhiều yêu cầu chờ duyệt','Mạng này đã gửi quá nhiều yêu cầu. Hãy nhờ admin xử lý bớt rồi thử lại.'],
 error:['<div class="gi">⚠️</div>','Chưa kết nối được','Đang thử lại…']};
function view(st){const k=M[st]?st:'error';if(last===k)return;last=k;const t=M[k];B.innerHTML=t[0]+'<b>'+t[1]+'</b><p class="mu">'+t[2]+'</p><div class="c">Mã thiết bị: '+HWID.slice(0,8)+'…'+HWID.slice(-4)+'</div>'}
function fake404(){done=true;document.open();document.write('<!doctype html>\n<html lang=en>\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>\n');document.close()}
async function tick(){
  if(done||busy)return;busy=true;
  try{
    const r=await fetch('/api/panel/status',{cache:'no-store',headers:HWID_HDR,credentials:'same-origin'});
    if(r.status===404){fake404();return}
    const j=await r.json().catch(()=>({}));
    if(j.status==='approved'){done=true;location.replace('/api/html/ui');return}
    view(j.status);
  }catch(e){view('error')}finally{busy=false}
}
tick();setInterval(tick,3000);
})();
</script></body></html>
'''
PANEL_SHELL = PANEL_SHELL.replace("/*__HWID_JS__*/", HWID_JS)


@app.route("/api/html")
def api_html():
    """VỎ công khai: chỉ có khung chờ duyệt + mã thiết bị. KHÔNG chứa giao diện / cơ chế / nhãn của panel (trước đây ai mở URL cũng đọc được toàn bộ JS panel).
    Duyệt xong, vỏ tự chuyển sang /api/html/ui (giao diện đầy đủ — chỉ phát cho thiết bị đã duyệt)."""
    hw, alts, hfresh = req_hw_ids()
    if _panel_banned(hw, alts, hfresh, client_ip()):
        abort(404)                                      # IP / thiết bị bị ban -> 404 Not Found như web sập
    return Response(PANEL_SHELL, content_type="text/html; charset=utf-8")


@app.route("/api/html/ui")
def api_html_ui():
    """Giao diện panel ĐẦY ĐỦ. Chỉ thiết bị đã được admin duyệt (token cookie do server cấp) mới nhận; còn lại 404 như trang không tồn tại."""
    hw, alts, hfresh = req_hw_ids()
    ip = client_ip()
    if _panel_banned(hw, alts, hfresh, ip):
        abort(404)
    if not _rate_ok(f"ui:{hw}:{ip}", 30):
        return _too_many()
    if _panel_access(hw or "0" * 32, alts, hfresh, ip, request.headers.get("User-Agent", ""), create=False) != "approved":
        abort(404)
    page = PANEL_HTML.replace("__SHOW__", str(PANEL_DEFAULT_SHOW)).replace("__MAX__", str(HIST_MAX)).replace("/*__HWID_JS__*/", HWID_JS)
    return Response(page, content_type="text/html; charset=utf-8")


@app.route("/api/predictsun")
@app.route("/api/predict")                        # tên cũ, giữ để tool đang chạy không bị hỏng
def api_predict():
    ensure_poller()
    with _state_lock:
        have = _state["result"] is not None
    if not have:                                  # request đầu tiên, poller chưa kịp quét xong
        try:
            refresh()
        except Exception as e:  # noqa: BLE001
            with _state_lock:
                _state["error"] = f"{type(e).__name__}: {e}"
    with _state_lock:
        res, err, upd = _state["result"], _state["error"], _state["updated"]
    if res is None:
        return _json({"ok": False, "loi": _pub_err(err, "chua co du lieu")}, 503)
    return _json(_predict_out(res, err, upd, "sun", "sun", SUN))


_TOOL_OUT_KEYS = ("ok", "phien", "du_doan", "do_tin_cay", "phien_truoc", "xuc_xac", "tong", "ket_qua_truoc", "tool_dung_sai_10_van", "stale", "cap_nhat", "game", "ban", "ten_ban")
if _env_bool("SUNVIW_TOOL_SHOW_WRN", False):         # mặc định ẨN so_van_wr (= cỡ cửa sổ WR, tham số thuật toán). Tool cũ cần trường này -> đặt =1
    _TOOL_OUT_KEYS = _TOOL_OUT_KEYS + ("so_van_wr",)
_TOOL_HIST_KEYS = ("phien", "du_doan", "ket_qua", "tong", "dung")


def _tool_view(out):
    """Danh sách trắng cho tool khách (key người dùng): chỉ phần đã công bố trong tài liệu API; mọi thứ nội bộ bị loại."""
    o = {k: out[k] for k in _TOOL_OUT_KEYS if k in out}
    if isinstance(o.get("do_tin_cay"), (int, float)):
        o["do_tin_cay"] = int(round(o["do_tin_cay"] / 5.0) * 5)      # làm tròn 5% -> không dùng để dò ngược WR từng logic
    if "lich_su" in out:
        o["lich_su"] = [{k: r.get(k) for k in _TOOL_HIST_KEYS} for r in out["lich_su"]]
    return o


def _predict_out(res, err, upd, game, hc_key, cfg, extra=None):
    """JSON dự đoán dùng chung cho SUN và các bàn HITCLUB (cùng cấu trúc). hc_key = khoá mốc xóa lịch sử · cfg = config của bàn đó."""
    out = dict(res["base"])
    out["game"] = game
    if extra:
        out.update(extra)
    out["stale"] = bool(err)
    if err:
        out["loi"] = err
    out["cap_nhat"] = upd
    if offsrv_state()["off"]:
        out["off_server"] = True                     # chỉ xuất hiện khi OFF SERVER bật (lúc đó chỉ panel / admin mới nhận được JSON này) -> panel hiện badge
    hist_rows, detail = res["hist"], res["detail"]
    hide = hist_hidden_upto(hc_key)               # đã bấm "Xóa lịch sử" -> chỉ ẩn khỏi phần hiển thị; WR / AF / vote logic vẫn đọc đủ dữ liệu cũ
    if hide:
        hist_rows = [r for r in hist_rows if r["phien"] > hide]
        out["tool_dung_sai_10_van"] = _acc_rows(hist_rows, cfg.EVAL_WINDOW)
        w = hist_rows[:cfg.WR_WINDOW]
        detail = dict(detail, tool_dung_sai_15_van={"dung": sum(1 for r in w if r["dung"]), "tong": len(w)})
    n = _hist_n()
    if n:
        out["lich_su"] = hist_rows[:n]
    if _is_panel():                              # panel đã duyệt / admin chính: đủ trường + ?detail=1
        if request.args.get("detail") in ("1", "true", "yes"):
            out["chi_tiet"] = detail
        return out
    return _tool_view(out)                       # tool khách: KHÔNG chi_tiet, KHÔNG trạng thái AF / bẻ / chế độ / WR từng logic / lỗi upstream


def _hit_predict(tb):
    """Handler chung của 2 bàn HITCLUB (cùng cấu trúc JSON với /api/predictsun, game="hitclub", thêm ban / ten_ban)."""
    ensure_poller()
    if not tb.active:
        return _json({"ok": False, "game": tb.game, "ban": tb.key, "loi": _pub_err("ban dang tat (HITCLUB=0 / LC_ENABLED=0 / ENABLED=False)", "ban dang tat")}, 503)
    with tb.slock:
        have = tb.state["result"] is not None
    if not have:                                  # request đầu tiên, poller chưa kịp quét xong
        try:
            tb.refresh()
        except Exception as e:  # noqa: BLE001
            with tb.slock:
                tb.state["error"] = f"{type(e).__name__}: {e}"
    with tb.slock:
        res, err, upd = tb.state["result"], tb.state["error"], tb.state["updated"]
    if res is None:
        return _json({"ok": False, "game": tb.game, "ban": tb.key,
                      "loi": _pub_err(err or "dang cho phien dau tien tu API Hit (can it nhat 1 phien co ket qua)", "dang cho du lieu")}, 503)
    return _json(_predict_out(res, err, upd, tb.game, tb.key, tb.cfg, {"ban": tb.key, "ten_ban": tb.label}))


@app.route("/api/predicthittxthuong")
def api_predict_hit_thuong():
    """[HITCLUB · TX THƯỜNG] — config riêng HIT_TXTHUONG_CFG · data riêng hit15_txthuong.json."""
    return _hit_predict(HIT_TABLES["hittxthuong"])


@app.route("/api/predicthittxmd5")
def api_predict_hit_md5():
    """[HITCLUB · TX MD5] — config riêng HIT_TXMD5_CFG · data riêng hit15_txmd5.json."""
    return _hit_predict(HIT_TABLES["hittxmd5"])


@app.route("/api/predictlcmd5")
@app.route("/api/predicttele68txmd5")          # tên cũ (alias) — tool đang gọi tên cũ vẫn chạy
def api_predict_lc_md5():
    """[LC · MD5] — config riêng LC_MD5_CFG · data riêng tele68_txmd5.json · nguồn: list ~105 phiên, chỉ lưu thêm phiên chưa có."""
    return _hit_predict(HIT_TABLES["lcmd5"])


@app.route("/api/predictlchu")
def api_predict_lc_hu():
    """[LC · HŨ] — config riêng LC_HU_CFG · data riêng lc_hu.json · nguồn: https://wtx.tele68.com/v1/tx/sessions (cùng định dạng list với LC MD5)."""
    return _hit_predict(HIT_TABLES["lchu"])


@app.route("/api/history/clear", methods=["POST"])
def api_history_clear():
    """Xóa LỊCH SỬ DỰ ĐOÁN hiển thị: {"game": "sun" | "hittxthuong" | "hittxmd5" | "hitclub" (cả 2 bàn Hit) | "all"}. Chỉ đặt mốc ẩn (xem khối CONFIG XÓA LỊCH SỬ) —
    KHÔNG xóa dữ liệu nào khác và KHÔNG ảnh hưởng logic / WR / AF dự đoán. Trả {"ok":true,"da_xoa":{"sun":N,"hittxthuong":M}} (N, M = số ván vừa ẩn). Key chỉ xóa được game mà nó thuộc về."""
    if not HIST_CLEAR_ENABLED:
        return _json({"ok": False, "loi": "tinh nang xoa lich su dang tat (SUNVIW_HIST_CLEAR=0)"}, 403)
    ensure_poller()
    b = request.get_json(silent=True) or {}
    g = str(b.get("game") or "").strip().lower()
    if g not in ("sun", "hittxthuong", "hittxmd5", "hitclub", "lcmd5", "lchu", "lc", "tele68txmd5", "tele68", "all"):
        return _json({"ok": False, "loi": 'game phai la "sun", "hittxthuong", "hittxmd5", "hitclub", "lcmd5", "lchu" hoac "all"'}, 400)
    allow = _key_tables(getattr(flask_g, "key_game", "all"))      # key game Sun -> chỉ {"sun"} · key game Hit -> 2 bàn Hit · KEY_GATE_API tắt -> tất cả
    want = {"sun": {"sun"}, "hittxthuong": {"hittxthuong"}, "hittxmd5": {"hittxmd5"}, "hitclub": {"hittxthuong", "hittxmd5"}, "lcmd5": {"lcmd5"}, "lchu": {"lchu"}, "lc": {"lcmd5", "lchu"}, "tele68txmd5": {"lcmd5"}, "tele68": {"lcmd5"}, "all": {"sun"} | set(HIT_TABLES)}[g]
    if not (want & allow):
        return _json({"ok": False, "sai_game": True, "loi": "key cua ban khong thuoc game nay, khong xoa duoc lich su game do"}, 403)
    want &= allow                                                 # "all" / "hitclub" với key 1 game -> chỉ xóa phần game của key
    done = {}
    if "sun" in want:
        with _state_lock:
            res = _state["result"]
        rows = res["hist"] if res else []                 # mới -> cũ: ván đầu = ván đã chấm mới nhất đang hiển thị
        hide = hist_hidden_upto("sun")
        shown = [r for r in rows if r["phien"] > hide]
        if shown:
            hist_clear("sun", shown[0]["phien"])
        done["sun"] = len(shown)
    for key, tb in HIT_TABLES.items():                    # 2 bàn HITCLUB: mỗi bàn một mốc riêng
        if key in want:
            with tb.slock:
                res = tb.state["result"]
            rows = res["hist"] if res else []
            hide = hist_hidden_upto(key)
            shown = [r for r in rows if r["phien"] > hide]
            if shown:
                hist_clear(key, shown[0]["phien"])
            done[key] = len(shown)
    return _json({"ok": True, "da_xoa": done})


@app.route("/api/history/regrade", methods=["POST"])
def api_history_regrade():
    """TÍNH LẠI đúng/sai của TOÀN BỘ ván đã lưu theo CONFIG HIỆN TẠI: {"game": "sun" | "hittxthuong" | "hittxmd5" | "hitclub" | "lcmd5" | "lchu" | "all"}.
    Dùng khi vừa đổi config (ngưỡng AF · bẻ final · WR...) rồi khởi động lại tool: lịch sử vẫn giữ, nhưng đúng/sai được chấm lại bằng config mới ngay,
    không phải đợi ván mới. Không chạy lại 13 logic (dùng votes đã lưu) nên nhanh. Không đụng mốc \"Xóa lịch sử\".
    Trả {"ok":true,"ket_qua":{"sun":{"so_van":N,"doi_du_doan":M,"truoc":{"dung","tong"},"sau":{"dung","tong"}}}}."""
    ensure_poller()
    b = request.get_json(silent=True) or {}
    g = str(b.get("game") or "").strip().lower()
    if g not in ("sun", "hittxthuong", "hittxmd5", "hitclub", "lcmd5", "lchu", "lc", "tele68txmd5", "tele68", "all"):
        return _json({"ok": False, "loi": 'game phai la "sun", "hittxthuong", "hittxmd5", "hitclub", "lcmd5", "lchu" hoac "all"'}, 400)
    allow = _key_tables(getattr(flask_g, "key_game", "all"))
    want = {"sun": {"sun"}, "hittxthuong": {"hittxthuong"}, "hittxmd5": {"hittxmd5"}, "hitclub": {"hittxthuong", "hittxmd5"}, "lcmd5": {"lcmd5"}, "lchu": {"lchu"}, "lc": {"lcmd5", "lchu"}, "tele68txmd5": {"lcmd5"}, "tele68": {"lcmd5"}, "all": {"sun"} | set(HIT_TABLES)}[g]
    if not (want & allow):
        return _json({"ok": False, "sai_game": True, "loi": "key cua ban khong thuoc game nay"}, 403)
    want &= allow
    done = {}
    try:
        if "sun" in want:
            with _state_lock:
                have = _state["result"] is not None
            if not have:
                try:
                    refresh()
                except Exception:  # noqa: BLE001
                    pass
            done["sun"] = sun_regrade()
        for key, tb in HIT_TABLES.items():
            if key in want and tb.active:
                done[key] = tb.regrade()
    except Exception as e:  # noqa: BLE001
        return _err500(e, request.path)
    return _json({"ok": True, "ket_qua": done})


@app.route("/api/history/wipe", methods=["POST"])
def api_history_wipe():
    """XÓA SẠCH DATA của game: {"game": "sun" | "hittxthuong" | "hittxmd5" | "hitclub" | "lcmd5" | "lchu" | "all", "confirm": true}.
    Khác \"Xóa lịch sử\" (chỉ ẩn): lệnh này xóa thật lịch sử xúc xắc + ván đã chấm + mốc ẩn của game đó, rồi tool đếm lại từ đầu (WR / AF cũng bắt đầu lại).
    Bắt buộc \"confirm\": true. Không hoàn tác được."""
    if not HIST_CLEAR_ENABLED:
        return _json({"ok": False, "loi": "tinh nang xoa dang tat (SUNVIW_HIST_CLEAR=0)"}, 403)
    ensure_poller()
    b = request.get_json(silent=True) or {}
    if b.get("confirm") is not True:
        return _json({"ok": False, "loi": 'can {"confirm": true}'}, 400)
    g = str(b.get("game") or "").strip().lower()
    if g not in ("sun", "hittxthuong", "hittxmd5", "hitclub", "lcmd5", "lchu", "lc", "tele68txmd5", "tele68", "all"):
        return _json({"ok": False, "loi": 'game phai la "sun", "hittxthuong", "hittxmd5", "hitclub", "lcmd5", "lchu" hoac "all"'}, 400)
    allow = _key_tables(getattr(flask_g, "key_game", "all"))
    want = {"sun": {"sun"}, "hittxthuong": {"hittxthuong"}, "hittxmd5": {"hittxmd5"}, "hitclub": {"hittxthuong", "hittxmd5"}, "lcmd5": {"lcmd5"}, "lchu": {"lchu"}, "lc": {"lcmd5", "lchu"}, "tele68txmd5": {"lcmd5"}, "tele68": {"lcmd5"}, "all": {"sun"} | set(HIT_TABLES)}[g]
    if not (want & allow):
        return _json({"ok": False, "sai_game": True, "loi": "key cua ban khong thuoc game nay"}, 403)
    want &= allow
    done = {}
    try:
        if "sun" in want:
            done["sun"] = sun_wipe()
        for key, tb in HIT_TABLES.items():
            if key in want:
                done[key] = tb.wipe()
    except Exception as e:  # noqa: BLE001
        return _err500(e, request.path)
    return _json({"ok": True, "da_xoa": done})


@app.route("/health")
def health_public():
    """Công khai (healthcheck / uptime monitor): CHỈ báo sống. Không lộ logic, cấu hình, đường dẫn, upstream, dự đoán chờ."""
    ensure_poller()
    return _json({"ok": True})


def _scrub_pub(o):
    """Ẩn URL nguồn dữ liệu + đường dẫn file khỏi dữ liệu chẩn đoán trả ra (không lộ nơi lưu / nguồn kể cả với admin)."""
    if isinstance(o, dict):
        return {k: _scrub_pub(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_scrub_pub(v) for v in o]
    if isinstance(o, str):
        o = re.sub(r"https?://\S+", "[da an]", o)
        return o.replace(DATA_DIR, "<data>") if DATA_DIR else o
    return o


@app.route("/api/admin/health")
def health():
    """Health ĐẦY ĐỦ (bộ logic, ngưỡng AF, config bàn, upstream, file) — CHỈ admin chính."""
    _s, _e = _need_main()
    if _e:
        return _e
    ensure_poller()
    with _state_lock:
        s = {k: _state[k] for k in ("latest", "error", "updated", "checked", "polls")}
    s.update(ok=s["error"] is None and s["latest"] is not None, upstream=UPSTREAM_URL,
             poll_sec=POLL_SEC, wr_window=WR_WINDOW, be_final=FLIP_FINAL,
             wr_weights=wr_weights_full(), wr_flip=WR_FLIP_WEIGHT, wr_decay=WR_DECAY, wr_floor=WR_FLOOR, wr_newest=WR_WEIGHT_NEWEST,       # trọng số cũ nhất -> mới nhất
             hist_keep=HIST_KEEP, persist_keep=PERSIST_KEEP, bo_logic=SUN_NAMES,
             af=dict(bat=AF_ENABLED, chi_be_vao_nhom=AF_GROUP_FLIPPED_ONLY, can_da_so_nhom=AF_GROUP_NEED_MAJORITY, doi_che_do_de=AF_SWITCH, phieu_doi_che_do=AF_SWITCH_NEED, flip_low=AF_FLIP_LOW, flip_high=AF_FLIP_HIGH, min_games=AF_MIN_GAMES, mode_window=AF_MODE_WINDOW,
                     vung_be=dict(bat=AF_FLIP_BAND, thap=[AF_FLIP_LOW_MIN, AF_FLIP_LOW_MAX], cao=[AF_FLIP_HIGH_MIN, AF_FLIP_HIGH_MAX]),
                     mode_min=AF_MODE_MIN, mode_below=AF_MODE_BELOW, be_che_do=AF_MODE_FLIP, be_final_af=AF_FLIP_FINAL,
                     be_final_cao_thap=AF_FLIP_FINAL_CT, be_final_cao=AF_FLIP_FINAL_CAO, be_final_thap=AF_FLIP_FINAL_THAP, be_final_all=AF_FLIP_FINAL_ALL),
             xoa_lich_su=dict(bat=HIST_CLEAR_ENABLED, sun_an_den_phien=hist_hidden_upto("sun")),
             ips=ip_health(), panel_duyet=panel_health(), off_server=offsrv_state()["off"],
             luu_tru=dict(thu_muc=DATA_DIR, ben=DATA_PERSISTENT, tren_railway=ON_RAILWAY, file_key=KEYS_PATH, key_tinh_han_tu_kich_hoat=KEY_START_ON_ACTIVATE,
                          khoi_dong_dau=BOOT_INFO.get("first"), so_lan_khoi_dong=BOOT_INFO.get("count"),
                          canh_bao=(None if DATA_PERSISTENT else "Dang chay tren Railway nhung CHUA co Volume -> key / lich su game se MAT sau moi lan deploy. Gan Volume (mount path /data) cho service.")))
    s["hitclub"] = {"bat": HIT_ENABLED, "ban": {k: tb.health() for k, tb in HIT_TABLES.items() if tb.kgame == "hit"}}
    s["lc79"] = {"bat": LC_ENABLED, "ban": {k: tb.health() for k, tb in HIT_TABLES.items() if tb.kgame == "lc79"}}
    s["autobet"] = ab_health()
    return _json(_scrub_pub(s))


# ═══════════════════════════════════════════════════════════════════════════
#  🤖  AUTO CƯỢC + AUTO RÚT LC79  (tách từ bot_lc79_v25.py — bản WEB, không còn Telegram)
# ═══════════════════════════════════════════════════════════════════════════
#   Trang điều khiển:  GET /tool/autocuoc   (cùng cơ chế DUYỆT THIẾT BỊ như /api/html: máy lạ thấy bảng "đang chờ admin duyệt")
#   Nguồn dự đoán:    bàn LC MD5 (HIT_TABLES["lcmd5"]) — dùng ĐÚNG dự đoán final mà /api/predictlcmd5 đang trả.
#                     Mỗi phiên mới có dự đoán (tb.pending) -> đặt cược tự động · khi API trả kết quả phiên đó -> chấm thắng/thua rồi tính tiền cược phiên kế.
#   Mỗi tài khoản LC79 = 1 phiên auto cược chạy luồng riêng (nhiều tài khoản chạy song song). Tất cả tính năng bật / tắt ngay trên trang, đổi khi đang chạy cũng được:
#     · Khi THUA: giữ nguyên / reset về gốc / x2 (Martingale)  ·  x2 sau chuỗi N ván thua (một lần)  ·  giảm cược sau N ván thua liên tiếp
#     · Khi THẮNG: giữ nguyên / reset về gốc / x2 sau N ván thắng liên tiếp (về gốc hoặc giữ x2 tới khi thua)
#     · Pause khi thua liên tiếp N ván (vẫn theo dõi ảo) -> tự cược lại khi thắng M ván liên tiếp  ·  Dừng khi lãi đạt mục tiêu
#     · Dừng khi đạt lãi + (tuỳ chọn) TỰ RÚT: quét số dư thật thấy lãi ≥ mục tiêu -> dừng toàn bộ cược rồi gửi lệnh rút đúng số tiền ngưỡng về Momo / Ngân hàng đã chọn (JWT hết hạn tự đăng nhập lại 1 lần)
#   Biến môi trường:  AUTOBET=0 (tắt hẳn) · AUTOBET_PATH (file lưu phiên) · AUTOBET_SAVE_PW=1 (lưu mật khẩu LC79 vào file để tự chạy lại sau restart — MẶC ĐỊNH TẮT, mật khẩu chỉ nằm trong RAM)
#   ⚠ Auto cược chạy trong tiến trình server ⇒ chạy gunicorn với 1 WORKER (vd:  gunicorn sunviw_api:app --workers 1 --threads 8). Có khoá file chống 2 worker cùng đặt cược 1 ván.
import urllib.error  # noqa: E402
import urllib.parse  # noqa: E402

try:
    import fcntl  # noqa: E402
except ImportError:  # Windows
    fcntl = None

AB_ENABLED = _env_bool("AUTOBET", True)
AB_FEED_KEY = "lcmd5"            # bàn nguồn dự đoán
AB_MULTI = 1.98                        # hệ số nhân tiền thắng
AB_PATH = os.environ.get("AUTOBET_PATH", _data_path("autobet_sessions.json"))
AB_LOCK_PATH = AB_PATH + ".lock"
AB_SAVE_PW = _env_bool("AUTOBET_SAVE_PW", False)
AB_SYNC_DELAY = 2.0                     # giây chờ sau khi CÓ KẾT QUẢ ván rồi mới quét số dư thật (chỉ quét theo sự kiện: sau khi đặt cược + sau kết quả, KHÔNG quét định kỳ)
AB_TICK = 1.5                          # giây giữa 2 lần kiểm tra phiên mới / kết quả
AB_SERIES_KEEP = 1500                  # số ván giữ cho biểu đồ
AB_LOG_KEEP = 80
AB_MAX_SESSIONS = 20
AB_KEY_RECHECK = 30                     # giây giữa 2 lần kiểm tra key chủ của phiên đang chạy (hết hạn -> tự dừng)
AB_BET_RETRY = 3                       # nhà cái từ chối rõ ràng (HTTP lỗi) thì thử lại tối đa N lần trong cùng phiên

AB_ORIGIN = os.environ.get("AUTOBET_ORIGIN", "https://play.lc79x.bet").strip().rstrip("/")   # web LC79 hiện tại (trước là tele68.com)
AB_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": AB_ORIGIN,
    "Referer": AB_ORIGIN + "/",
}
AB_P = {"cp": "R", "cl": "R", "pf": "web"}

# ── Auto rút: hạn mức / mệnh giá (sửa cho khớp LC79) ──
_AB_AT_DEFAULT = ["ef1824c574ee1af6051d14ba998ceb9d", "4ae3141f18b0b121291eac1dddf10f44"]      # dự phòng — nên đặt AUTOBET_AT_TOKENS (cách nhau dấu phẩy) rồi xoá 2 giá trị này khỏi code
AB_AT_TOKENS = [t.strip() for t in os.environ.get("AUTOBET_AT_TOKENS", "").split(",") if t.strip()] or _AB_AT_DEFAULT
_ab_at = {"v": AB_AT_TOKENS[0]}
AB_MOMO_AMOUNTS = [100_000, 200_000, 300_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000]
AB_MOMO_MIN, AB_MOMO_MAX = 200_000, 1_000_000
AB_BANK_AMOUNTS = list(AB_MOMO_AMOUNTS)   # chưa rõ mệnh giá ngân hàng thật của LC79 -> để giống Momo cho an toàn
AB_BANK_MIN, AB_BANK_MAX = 200_000, 1_000_000
AB_WD_COOLDOWN = 60                       # rút lỗi -> chờ N giây mới thử lại
AB_WD_MAX_FAILS = 3                       # lỗi liên tiếp N lần -> tự tắt auto rút


def _ab_req(method, url, params=None, jwt=None, body=None, timeout=12):
    """HTTP (urllib, không cần thư viện ngoài) -> (status, json|None, raw_text). Lỗi mạng / timeout thì ném exception."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    h = dict(AB_HEADERS)
    if jwt:
        h["Authorization"] = "Bearer " + jwt
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            st, raw = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        st = e.code
        try:
            raw = e.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            raw = ""
    try:
        js = json.loads(raw) if raw else None
    except ValueError:
        js = None
    return st, js, raw


def ab_login(username, password):
    """Đăng nhập LC79 -> (jwt, balance, nick, loi). jwt = None nếu thất bại."""
    pw_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    access_token, nick = "", username
    try:                                                    # BƯỚC 1: lấy accessToken + nickName
        st, g, _ = _ab_req("GET", "https://apifo88daigia.tele68.com/api",
                           {"c": "3", "un": username, "pw": pw_md5, **AB_P, "at": ""}, timeout=12)
        if st == 200 and isinstance(g, dict):
            access_token = g.get("accessToken") or ""
            sk = g.get("sessionKey") or ""
            if sk:
                try:
                    dec = base64.b64decode(sk + "=" * (-len(sk) % 4)).decode("utf-8", errors="ignore")
                    m = re.search(r'"nicknam[eE]"\s*:\s*"([^"]+)"', dec, re.I)
                    if m:
                        nick = m.group(1)
                except Exception:  # noqa: BLE001
                    pass
            if nick == username:
                nick = g.get("nickName") or g.get("username") or username
    except Exception:  # noqa: BLE001
        pass
    full = {"username": username, "password": password, "nickName": nick,
            "accessToken": access_token, "isLogin": bool(access_token), "money": 0}
    bodies = ([{"nickName": nick, "accessToken": access_token}] if access_token else []) + [full]   # web LC79 hiện chỉ gửi nickName + accessToken
    d = None
    for body in bodies:                                     # BƯỚC 2: JWT (sống expiresIn = 28800s = 8 giờ)
        try:
            st, dd, _ = _ab_req("POST", "https://wlb.tele68.com/v1/lobby/auth/login", {**AB_P, "at": ""}, body=body, timeout=12)
        except Exception as e:  # noqa: BLE001
            return None, 0, nick, f"Không kết nối được LC79 ({type(e).__name__})"
        if st == 200 and isinstance(dd, dict) and dd.get("token"):
            d = dd
            break
    if d is None:
        return None, 0, nick, "Sai tên đăng nhập / mật khẩu (hoặc LC79 từ chối đăng nhập)"
    remote = d.get("remoteLoginResp") or {}
    money = int(remote.get("money") or 0)
    if money <= 0:                                          # login không còn trả số dư -> hỏi API số dư riêng
        real = ab_fetch_balance(d["token"])
        if real is not None:
            money = real
    return d["token"], money, remote.get("nickName", nick), ""


def _ab_jwt_exp(jwt):
    """Thời điểm (epoch) JWT hết hạn, đọc từ claim exp; không đọc được -> 0."""
    try:
        p = jwt.split(".")[1]
        return int(json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4))).get("exp") or 0)
    except Exception:  # noqa: BLE001
        return 0


def _ab_pick_money(d):
    """Tìm số dư trong JSON LC79 — chấp nhận cả số dư = 0 (trước đây `or` coi 0 là 'không có' -> báo nhầm JWT hết hạn)."""
    if not isinstance(d, dict):
        return None
    for o in (d, d.get("data"), d.get("remoteLoginResp"), d.get("user")):
        if isinstance(o, dict):
            for k in ("money", "balance", "gold", "coin"):
                v = o.get(k)
                if v is not None and not isinstance(v, bool):
                    try:
                        return int(float(v))
                    except (TypeError, ValueError):
                        pass
    return None


def ab_fetch_balance(jwt):
    """Số dư thật từ server LC79 (0 là số dư hợp lệ). None = JWT hết hạn (401/403) hoặc không đọc được."""
    if not jwt:
        return None
    for url in ("https://wlb.tele68.com/v1/lobby/user/info", "https://wlb.tele68.com/v1/lobby/wallet/balance"):
        try:
            st, d, _ = _ab_req("GET", url, AB_P, jwt=jwt, timeout=10)
        except Exception:  # noqa: BLE001
            continue
        if st in (401, 403):
            return None
        if st == 200:
            m = _ab_pick_money(d)
            if m is not None:
                return m
    return None


# ── Auto cược qua WebSocket Socket.IO (namespace /txmd5) — thay cho POST REST cũ ──
#   Nghe:  42/txmd5,["tick-update", {id, tick, subTick, state, data, timestamp}]
#          state == BETTING -> MỞ cược (chỉ POST cược khi có state này) · các state khác (RESULT, ...) -> KHÔNG cược
#   Gửi:   khi state == BETTING -> emit qua WS:  42/txmd5,<ackId>["bet", {"type": "XIU"|"TAI", "amount": 1000}]   (server trả ack 43/txmd5,<ackId>[...] -> ghi vào nhật ký)
#          WS không nghe được / chế độ http (AUTOBET_BET_MODE=http) -> POST HTTP {"type","amount"} + Authorization: Bearer <jwt> tới AUTOBET_BET_URL (mặc định thử wtxmd52 rồi wlb)
#   Env:   AUTOBET_WS_URL (URL websocket, mặc định wss://wtxmd52.tele68.com/txmd5/?EIO=4&transport=websocket — copy từ DevTools > Network > WS) · AUTOBET_WS_NS (mặc định /txmd5)
#          AUTOBET_BET_URL (URL POST cược dự phòng) · AUTOBET_BET_MODE (ws | http) · AUTOBET_WS_BET_STATES (mặc định BETTING, nhiều state cách nhau dấu phẩy) · AUTOBET_WS_AUTH (json auth gửi kèm packet connect, mặc định {"token": "<jwt>"})
#          AUTOBET_WS_FALLBACK (mặc định 1: WS không nghe được state thì vẫn POST cược ngay khi có dự đoán như bot_lc79_v23.py · 0 = bắt buộc phải có state BETTING mới cược)
#   Lỗi WS (thiếu thư viện, sai URL, namespace từ chối, mất tick...) được ghi vào NHẬT KÝ phiên auto cược + trường "ws" trong JSON phiên.
#   Cần: pip install websocket-client
_AB_WS_URL_ENV = os.environ.get("AUTOBET_WS_URL", "").strip()
AB_WS_URLS = [_AB_WS_URL_ENV] if _AB_WS_URL_ENV else [         # URL WS thật copy từ DevTools (path là /txmd5/, KHÔNG phải /socket.io/); đặt AUTOBET_WS_URL để đổi. Các URL sau chỉ là dự phòng nếu URL đầu nối lỗi
    "wss://wtxmd52.tele68.com/txmd5/?EIO=4&transport=websocket",
    "wss://wtxmd52.tele68.com/txmd5/?EIO=4&transport=websocket&cp=R&cl=R&pf=web",
    "wss://wlb.tele68.com/socket.io/?EIO=4&transport=websocket&cp=R&cl=R&pf=web",
]
AB_WS_URL = AB_WS_URLS[0]
AB_WS_NS = os.environ.get("AUTOBET_WS_NS", "/txmd5")
AB_WS_BET_STATES = {x.strip().upper() for x in os.environ.get("AUTOBET_WS_BET_STATES", "BETTING").split(",") if x.strip()}
_AB_BET_URL_ENV = os.environ.get("AUTOBET_BET_URL", "").strip()
AB_BET_URLS = [_AB_BET_URL_ENV] if _AB_BET_URL_ENV else [      # URL POST cược DỰ PHÒNG (wlb.tele68.com/v1/txmd5/bet của bot_lc79_v23.py đã trả 404) — chỉ 404 mới thử URL kế
    "https://wtxmd52.tele68.com/v1/txmd5/bet",
    "https://wlb.tele68.com/v1/txmd5/bet",
]
AB_BET_URL = AB_BET_URLS[0]
AB_BET_MODE = os.environ.get("AUTOBET_BET_MODE", "ws").strip().lower()   # "ws" (mặc định): WS khoẻ + state BETTING -> emit event "bet" qua WS (như bản gốc), WS hỏng -> POST HTTP · "http": luôn POST HTTP
AB_BET_TIMEOUT = 8.0
AB_WS_STALE = 15.0          # quá N giây không nhận tick-update -> coi như mất đồng bộ
AB_WS_FALLBACK = _env_bool("AUTOBET_WS_FALLBACK", True)   # WS không nghe được state (chưa cài thư viện / sai URL / mất kết nối) -> vẫn POST cược ngay khi có dự đoán phiên mới, y như bot_lc79_v23.py (đặt AUTOBET_WS_FALLBACK=0 để BẮT BUỘC có state BETTING mới cược)


def _ab_url_host(u):
    try:
        return urllib.parse.urlsplit(u).netloc or u[:40]
    except Exception:  # noqa: BLE001
        return u[:40]


class AbWs:
    """Kết nối Socket.IO (Engine.IO v4) tới namespace /txmd5 cho 1 tài khoản: NGHE tick-update (state) để biết lúc nào mở cược.
    Lỗi kết nối được ghi thẳng vào nhật ký phiên (không còn im lặng); nối lỗi thì tự thử URL kế tiếp / vào namespace không kèm token."""

    def __init__(self, sess):
        self.sess = sess
        self.ws = None
        self.stop_flag = False
        self.connected = False          # đã vào namespace
        self.state = ""
        self.round_id = 0
        self.tick = 0
        self.last_tick_t = 0.0
        self.bet_round = 0              # round id đã gửi cược (chặn cược đôi cùng 1 ván)
        self.thread = None
        self.last_err = ""
        self._tick_logged = False
        self._ack_id = 0                # số ack tăng dần cho event bet
        self._bet_url_i = 0             # URL POST đang dùng được
        self._ev_budget = 10            # số event KHÁC tick-update được ghi vào nhật ký (để thấy server phản hồi cược thế nào)
        self._url_i = 0                 # chỉ số URL đang thử
        self._noauth = False            # True: vào namespace KHÔNG kèm token (chỉ nghe state thì không cần đăng nhập)
        self._t_conn = 0.0              # lúc mở kết nối gần nhất
        self._logged = {}               # chống spam nhật ký: nội dung -> lần ghi gần nhất

    # ── tiện ích ──
    def _log_once(self, kind, msg, every=60.0):
        now = time.time()
        if now - self._logged.get(msg, 0.0) < every:
            return
        self._logged[msg] = now
        if len(self._logged) > 30:
            self._logged.clear()
        try:
            self.sess.log(kind, msg)
        except Exception:  # noqa: BLE001
            pass

    def healthy(self):
        """True = đang nhận tick-update đều (WS dùng được)."""
        return bool(self.connected and self.last_tick_t and time.time() - self.last_tick_t < AB_WS_STALE)

    def info(self):
        return {"ok": self.healthy(), "state": self.state or None, "err": self.last_err or None,
                "age": (round(time.time() - self.last_tick_t, 1) if self.last_tick_t else None),
                "fallback": bool(AB_WS_FALLBACK and not self.healthy())}

    def watchdog(self):
        """Session gọi mỗi nhịp: WS không khoẻ thì báo lý do vào nhật ký (tối đa 1 lần / 90s) và ép nối lại bằng URL / kiểu auth khác."""
        if self.stop_flag or self.healthy():
            return
        reason = self.last_err or ("đã nối nhưng chưa nhận tick-update" if self.connected else "chưa kết nối được")
        tail = "đang cược bằng POST ngay khi có dự đoán (không cần state)" if AB_WS_FALLBACK else "chưa thể cược (AUTOBET_WS_FALLBACK=0)"
        self._log_once("warn", f"WS chưa nghe được state ({reason}) — {tail}", every=90.0)
        if self._t_conn and time.time() - self._t_conn > 20 and self.ws is not None:   # nối >20s mà không có tick -> đóng để vòng lặp thử URL / auth kế
            try:
                self.ws.close()
            except Exception:  # noqa: BLE001
                pass

    # ── vòng đời ──
    def start(self):
        if self.thread and self.thread.is_alive():
            return
        try:
            import websocket  # noqa: F401
        except ImportError:
            self.last_err = "thiếu thư viện websocket-client"
            tail = "tạm cược bằng POST ngay khi có dự đoán (không cần state)" if AB_WS_FALLBACK else "sẽ KHÔNG cược được"
            self._log_once("warn", f"KHÔNG nghe được WS: server chưa cài thư viện websocket-client (pip install websocket-client rồi khởi động lại) — {tail}", every=3600.0)
            return
        self.stop_flag = False
        self.thread = threading.Thread(target=self._loop, daemon=True, name=f"abws-{self.sess.sid}")
        self.thread.start()

    def close(self):
        self.stop_flag = True
        self.connected = False
        try:
            if self.ws:
                self.ws.close()
        except Exception:  # noqa: BLE001
            pass

    def restart(self):
        """Đổi JWT (đăng nhập lại) -> đóng để vòng lặp tự nối lại với token mới."""
        try:
            if self.ws:
                self.ws.close()
        except Exception:  # noqa: BLE001
            pass

    # ── cược ──
    def can_bet(self):
        if self.healthy():                                                 # nghe được WS -> CHỈ cược khi state == BETTING, mỗi ván 1 lần
            return self.state in AB_WS_BET_STATES and bool(self.round_id) and self.bet_round != self.round_id
        return bool(AB_WS_FALLBACK and self.sess.jwt)                      # WS không nghe được -> cược như bot_lc79_v23.py (POST ngay khi có dự đoán phiên mới)

    def _bet_http(self, side, amount):
        """POST HTTP dự phòng. Chỉ khi 404 (sai đường dẫn) mới thử URL kế. Lỗi mạng / timeout -> ném exception."""
        last = (False, 0, "")
        n = len(AB_BET_URLS)
        for k in range(n):
            i = (self._bet_url_i + k) % n
            st, _js, raw = _ab_req("POST", AB_BET_URLS[i], AB_P, jwt=self.sess.jwt,
                                   body={"type": side, "amount": int(amount)}, timeout=AB_BET_TIMEOUT)
            if st in (200, 201):
                self._bet_url_i = i
                return True, st, raw[:120]
            last = (False, st, f"HTTP {st} {_ab_url_host(AB_BET_URLS[i])}: {raw[:100]}")
            if st != 404:
                break
        return last

    def send_bet(self, side, amount):
        """Gửi cược. WS khoẻ + state BETTING -> emit event "bet" qua WS (đúng như bản gốc của tool); WS hỏng / chế độ http -> POST HTTP.
        Trả (ok, status, raw). ok=False + status=0 nghĩa là CHẮC CHẮN chưa gửi. Lỗi mạng / timeout HTTP -> ném exception (không rõ nhà cái nhận chưa) để phía gọi KHÔNG thử lại, tránh cược đôi."""
        if not self.can_bet():
            return False, 0, f"chưa mở cược (state={self.state or '?'})"
        if not self.sess.jwt:
            return False, 0, "chưa có JWT"
        ws_mode = self.healthy()
        rid = self.round_id if ws_mode else 0
        if ws_mode:
            self.bet_round = rid                                           # khoá ván này TRƯỚC khi gửi -> không cược đôi cùng 1 ván
        else:
            self._log_once("info", "Cược KHÔNG theo state WS (WS chưa nghe được) — POST HTTP ngay khi có dự đoán", every=300.0)
        if ws_mode and AB_BET_MODE != "http" and not self._noauth and self.ws is not None:
            self._ack_id += 1
            pkt = "42" + AB_WS_NS + "," + str(self._ack_id) + json.dumps(["bet", {"type": side, "amount": int(amount)}], separators=(",", ":"))
            try:
                self.ws.send(pkt)
            except Exception as e:  # noqa: BLE001 - chưa gửi được -> thử HTTP ngay
                self._log_once("warn", f"Gửi cược qua WS lỗi ({type(e).__name__}) — thử POST HTTP", every=30.0)
            else:
                self._ev_budget = 6                                        # ghi vài event server trả về ngay sau khi cược
                self._log_once("info", 'Cược gửi bằng WS event "bet"', every=300.0)
                return True, 200, pkt
        ok, st, raw = self._bet_http(side, amount)
        if not ok and ws_mode and self.bet_round == rid:
            self.bet_round = 0                                             # bị từ chối rõ ràng -> cho thử lại trong cùng ván
        return ok, st, raw

    # ── kết nối ──
    def _loop(self):
        import inspect
        import websocket
        kw = {}
        try:
            if "reconnect" in inspect.signature(websocket.WebSocketApp.run_forever).parameters:   # bản websocket-client cũ không có tham số này
                kw["reconnect"] = 0
        except Exception:  # noqa: BLE001
            pass
        fails = 0
        while not self.stop_flag and self.sess.alive:
            self.connected = False
            self._tick_logged = False
            url = AB_WS_URLS[self._url_i % len(AB_WS_URLS)]
            tick_before = self.last_tick_t
            self._t_conn = time.time()
            try:
                hdr = ["User-Agent: " + AB_HEADERS["User-Agent"]]            # KHÔNG đưa Origin vào header: websocket-client tự thêm Origin -> gửi trùng 2 Origin thì server trả 400 lúc bắt tay
                if self.sess.jwt and not self._noauth:
                    hdr.append("Authorization: Bearer " + self.sess.jwt)
                self._log_once("info", f"WS đang kết nối {_ab_url_host(url)}{' (không kèm token)' if self._noauth else ''}", every=300.0)
                self.ws = websocket.WebSocketApp(url, header=hdr, on_message=self._on_msg, on_error=self._on_err, on_close=self._on_close)
                self.ws.run_forever(ping_interval=0, origin=AB_ORIGIN, **kw)   # Origin truyền qua tham số origin (không trùng)
            except Exception as e:  # noqa: BLE001
                self.last_err = f"{type(e).__name__}: {e}"[:120]
                self._log_once("warn", f"WS lỗi: {self.last_err}")
            self.connected = False
            if self.stop_flag or not self.sess.alive:
                break
            if self.last_tick_t > tick_before:                             # lần nối này có nhận tick -> giữ nguyên URL / auth đang chạy tốt
                fails = 0
            else:                                                          # chưa nhận tick nào -> thử URL kế; hết vòng URL thì đổi kiểu auth
                fails += 1
                self._url_i += 1
                if self._url_i % len(AB_WS_URLS) == 0:
                    self._noauth = not self._noauth
            time.sleep(min(2.0 + fails, 10.0))                             # nối lại

    def _on_err(self, *a):
        e = a[-1] if a else ""
        self.last_err = f"{type(e).__name__}: {e}"[:120] if isinstance(e, BaseException) else str(e)[:120]
        self._log_once("warn", f"WS lỗi: {self.last_err}")

    def _on_close(self, *a):
        self.connected = False
        extra = ""
        if len(a) >= 3 and (a[1] or a[2]):
            extra = f" (code={a[1]} {str(a[2] or '')[:60]})"
        if not self.stop_flag:
            self._log_once("info", f"WS đóng kết nối{extra} — tự nối lại", every=120.0)

    def _on_msg(self, *a):
        msg = a[-1] if a else None
        ws = a[0] if len(a) > 1 else self.ws
        if not isinstance(msg, str) or not msg:
            return
        t = msg[0]
        if t == "0":                                                        # Engine.IO open -> vào namespace (kèm token, hoặc không kèm khi _noauth)
            if self._noauth:
                ws.send("40" + AB_WS_NS + ",")
            else:
                auth = os.environ.get("AUTOBET_WS_AUTH")
                try:
                    auth = json.loads(auth.replace("<jwt>", self.sess.jwt)) if auth else {"token": self.sess.jwt}
                except ValueError:
                    auth = {"token": self.sess.jwt}
                ws.send("40" + AB_WS_NS + "," + json.dumps(auth, separators=(",", ":")))
        elif t == "2":                                                      # ping -> pong
            ws.send("3")
        elif msg.startswith("40"):                                          # đã vào namespace (hoặc namespace mặc định)
            if msg.startswith("40" + AB_WS_NS) or msg.startswith("40{") or msg == "40":
                self.connected = True
                self.last_err = ""
                self._log_once("info", f"WS đã vào namespace {AB_WS_NS}", every=600.0)
        elif msg.startswith("44"):                                          # connect_error -> đóng để thử lại (đổi kiểu auth)
            self.connected = False
            self.last_err = "namespace từ chối: " + msg[:100]
            self._log_once("warn", f"WS {self.last_err}")
            try:
                ws.close()
            except Exception:  # noqa: BLE001
                pass
        elif msg.startswith("43"):                                          # ack của event ta gửi (bet) -> ghi lại để biết server trả lời gì
            body = msg[2:]
            if body.startswith(AB_WS_NS + ","):
                body = body[len(AB_WS_NS) + 1:]
            self.sess.log("info", f"Server trả lời cược: {body[:150]}")
        elif msg.startswith("42"):
            body = msg[2:]
            if body.startswith(AB_WS_NS + ","):
                body = body[len(AB_WS_NS) + 1:]
            body = body.lstrip("0123456789")
            try:
                ev = json.loads(body)
            except ValueError:
                return
            if not (isinstance(ev, list) and ev):
                return
            if ev[0] == "tick-update" and len(ev) > 1 and isinstance(ev[1], dict):
                d = ev[1]
                self.state = str(d.get("state") or "").upper()
                self.round_id = int(d.get("id") or 0)
                self.tick = int(d.get("tick") or 0)
                self.last_tick_t = time.time()
                self.last_err = ""
                if not self._tick_logged:
                    self._tick_logged = True
                    self.sess.log("info", f"WS đã nhận tick-update (state={self.state}, ván {self.round_id}) — cược khi state = {'/'.join(sorted(AB_WS_BET_STATES))}")
                self.connected = True
            elif ev[0] in ("bet-error", "error", "bet-failed") and len(ev) > 1:
                self.sess.log("warn", f"Server báo lỗi cược: {str(ev[1])[:120]}")
            elif ev[0] != "tick-update" and self._ev_budget > 0:
                self._ev_budget -= 1
                self.sess.log("info", f"WS event {str(ev[0])[:30]}: {json.dumps(ev[1:], ensure_ascii=False)[:150]}")


def _ab_wd_limits(kind):
    return (AB_BANK_AMOUNTS, AB_BANK_MIN, AB_BANK_MAX) if kind == "bank" else (AB_MOMO_AMOUNTS, AB_MOMO_MIN, AB_MOMO_MAX)


def _ab_wd_label(kind, code, number):
    return f"{(code or 'Ngân hàng').upper()} {number}" if kind == "bank" else f"Momo {number}"


def _ab_snap(amount, valid, mx):
    """Làm tròn xuống mệnh giá hợp lệ gần nhất (không vượt max)."""
    amount = min(amount, mx)
    ok = [v for v in valid if v <= amount]
    return max(ok) if ok else 0


def ab_wallets(jwt, wtype="bank"):
    """STK / ví đã liên kết: GET payment-app/wallet-used?type=bank|momo -> list dict {type, wallet_number, wallet_name, id}."""
    if not jwt:
        return []
    for at in [_ab_at["v"]] + [t for t in AB_AT_TOKENS if t != _ab_at["v"]]:
        try:
            st, d, _ = _ab_req("GET", "https://gameapi.tele68.com/v1/payment-app/wallet-used", {**AB_P, "type": wtype, "at": at}, jwt=jwt, timeout=10)
        except Exception:  # noqa: BLE001
            continue
        if st != 200:
            continue
        if isinstance(d, dict):
            d = d.get("data") or []
        if isinstance(d, list):
            _ab_at["v"] = at
            return [w for w in d if isinstance(w, dict)]
    return []


def _ab_wd_schemas(kind, code, number, name, amount):
    """Các dạng payload thử lần lượt (server báo -1111 / 400 thì thử dạng kế)."""
    if kind == "bank":
        c_lo, c_up = (code or "").lower(), (code or "").upper()
    else:
        c_lo, c_up = "momo", "MOMO"
    wallet_style = {"type": c_lo, "wallet_number": number, "wallet_name": name, "amount": amount}
    sch = [
        {"bank_code": c_up, "bank_number": number, "bank_name": name, "amount": amount},
        wallet_style,
        {"type": c_up, "account_number": number, "account_name": name, "amount": amount},
        {"bank_type": c_up, "bank_account": number, "account_name": name, "amount": amount},
        {"bank_code": c_up, "phone": number, "name": name, "amount": amount},
        {"bankCode": c_up, "bankNumber": number, "bankName": name, "amount": amount},
        {"bank_code": c_up, "card_number": number, "card_name": name, "amount": amount},
        {"bank": {"code": c_up, "number": number, "name": name}, "amount": amount},
    ]
    if kind == "bank":
        sch.remove(wallet_style)
        sch.insert(0, wallet_style)
        sch.insert(1, {"bank_code": c_lo, "bank_number": number, "bank_name": name, "amount": amount})
    else:
        sch.append({"bank_code": c_up, "bank_number": number, "bank_name": name, "amount": amount // 1000})
    return sch


def ab_withdraw(jwt, amount, kind, code, number, name=""):
    """Rút tiền (kind = 'momo' | 'bank'): nhiều URL × nhiều payload. Trả (ok, message, resp)."""
    _, mn, mx = _ab_wd_limits(kind)
    if not jwt or amount <= 0 or not number:
        return False, "Thiếu thông tin", {}
    if amount < mn:
        return False, f"Số tiền tối thiểu: {mn:,}", {}
    if amount > mx:
        return False, f"Số tiền tối đa/lần: {mx:,}", {}
    urls = ["https://gameapi.tele68.com/v1/payment-app/cash-out/bank",
            "https://gameapi.tele68.com/v1/payment-app/withdraw",
            "https://wlb.tele68.com/v1/lobby/payment/withdraw",
            "https://wlb.tele68.com/v1/lobby/cash-out"]
    schemas = _ab_wd_schemas(kind, code, number, name, amount)
    last_msg, last_resp = "Tất cả URL + schema đều fail", {}
    for url in urls:
        for payload in schemas:
            try:
                st, resp, raw = _ab_req("POST", url, {**AB_P, "at": _ab_at["v"]}, jwt=jwt, body=payload, timeout=20)
            except Exception:  # noqa: BLE001
                continue
            resp = resp if isinstance(resp, dict) else {}
            code_r = resp.get("code", -1)
            msg = resp.get("message") or resp.get("msg") or raw[:100]
            last_msg, last_resp = msg, resp
            if code_r == -1111:                    # sai payload -> thử schema kế
                continue
            if st == 404:                          # endpoint sai -> bỏ URL này
                break
            if st in (200, 201):
                if code_r == 0 or resp.get("success") is True:
                    return True, msg, resp
                return False, f"API từ chối (code={code_r}): {msg}", resp     # lỗi nghiệp vụ -> dừng hẳn
            if st in (401, 403):
                return False, "JWT hết hạn", resp
    return False, str(last_msg), last_resp


# ── cấu hình mặc định + kiểm tra đầu vào ──
AB_CFG_DEFAULT = {
    "bet": 1000,                                       # cược gốc / ván
    "loss_mode": "keep",                               # khi THUA: "keep" giữ nguyên · "reset" về gốc · "x2" nhân đôi (Martingale)
    "loss_x2_on": False, "loss_x2_streak": 3,          # x2 MỘT LẦN sau N ván thua liên tiếp (thắng lại -> về gốc)
    "win_mode": "keep",                                # khi THẮNG: "keep" · "reset" · "x2" (x2 sau N ván thắng liên tiếp)
    "win_x2_streak": 1, "win_x2_keep": False,          # win_x2_keep: True = giữ x2 tới khi thua · False = thắng 1 ván x2 thì về gốc
    "reduce_on": False, "reduce_streak": 3, "reduce_bet": 0,       # thua N ván liên tiếp -> giảm cược xuống reduce_bet
    "pause_on": False, "pause_streak": 5, "resume_wins": 2,        # thua N ván liên tiếp -> pause (theo dõi ảo) · thắng M ván liên tiếp -> cược lại
    "target_on": False, "target": 0,                   # tự dừng khi lãi >= target
    "target_wd": False,                                # True = đạt mục tiêu lãi -> dừng cược + RÚT TOÀN BỘ số dư về tài khoản bên dưới
    "wd_on": False,                                    # (tự suy ra = target_on and target_wd — không chỉnh tay)
    "wd_kind": "momo", "wd_code": "MOMO", "wd_number": "", "wd_name": "",
}


def _ab_int(v, lo=0, hi=10**12):
    try:
        if isinstance(v, str):
            v = v.strip().lower().replace(",", "").replace(" ", "")
            if v.endswith("m"):
                v = float(v[:-1]) * 1_000_000
            elif v.endswith("k"):
                v = float(v[:-1]) * 1_000
            else:
                v = float(v)
        n = int(v)
    except (TypeError, ValueError):
        raise ValueError("số không hợp lệ")
    return max(lo, min(hi, n))


def ab_clean_cfg(raw, old=None):
    """Gộp cấu hình gửi lên vào cấu hình cũ, ép kiểu + kiểm tra. Ném ValueError(thông báo tiếng Việt) nếu sai."""
    c = dict(old or AB_CFG_DEFAULT)
    r = raw if isinstance(raw, dict) else {}
    c.setdefault("target_wd", False)                   # phiên lưu từ bản cũ chưa có khoá này
    for k in ("loss_x2_on", "win_x2_keep", "reduce_on", "pause_on", "target_on", "target_wd"):
        if k in r:
            c[k] = bool(r[k])
    for k, lo in (("bet", 1), ("loss_x2_streak", 1), ("win_x2_streak", 1), ("reduce_streak", 1), ("reduce_bet", 0),
                  ("pause_streak", 1), ("resume_wins", 0), ("target", 0)):
        if k in r:
            try:
                c[k] = _ab_int(r[k], lo)
            except ValueError:
                raise ValueError(f"Ô «{k}» phải là số nguyên ≥ {lo}")
    for k, allow in (("loss_mode", ("keep", "reset", "x2")), ("win_mode", ("keep", "reset", "x2")), ("wd_kind", ("momo", "bank"))):
        if k in r:
            if r[k] not in allow:
                raise ValueError(f"Giá trị «{k}» không hợp lệ")
            c[k] = r[k]
    for k, n in (("wd_code", 20), ("wd_number", 40), ("wd_name", 80)):
        if k in r:
            c[k] = str(r[k] or "").strip()[:n]
    if c["wd_kind"] == "momo":
        c["wd_code"] = "MOMO"
    if c["reduce_on"] and c["reduce_bet"] >= c["bet"]:
        raise ValueError("Mức cược giảm phải NHỎ HƠN cược gốc")
    if c["reduce_on"] and c["reduce_bet"] <= 0:
        raise ValueError("Nhập mức cược sau khi giảm")
    if c["target_on"] and c["target"] <= 0:
        raise ValueError("Nhập mục tiêu lãi lớn hơn 0")
    c["wd_on"] = bool(c["target_on"] and c["target_wd"])      # tự rút chỉ có nghĩa khi đang bật "Dừng khi đạt lãi"
    if c["wd_on"] and not c["wd_number"]:
        raise ValueError("Chọn nơi nhận tiền: nhập SĐT Momo / số tài khoản ngân hàng (hoặc bấm «Lấy từ LC79»)")
    return c


class AbLedger:
    """Số dư + lãi/lỗ theo ván (kèm chuỗi điểm cho biểu đồ)."""

    def __init__(self, start, nick):
        self.balance = start
        self.start_bal = start
        self.nick = nick
        self.rounds = 0
        self.w = self.l = 0
        self.withdrawn = 0
        self.staked = 0         # tổng tiền đã đặt cược (cộng dồn, không bị cắt như series)
        self.series = []        # mỗi ván đã chấm: {r, t, phien, side, res, amount, pnl, win, net, bal}
        self.t0 = time.time()

    def net(self):
        return self.balance + self.withdrawn - self.start_bal       # cộng tiền đã rút để lãi/lỗ không tụt khi rút

    def bet(self, side, amount, phien):
        self.balance -= amount
        self.staked += amount
        self.rounds += 1
        return {"r": self.rounds, "phien": phien, "side": side, "amount": amount, "res": None, "pnl": -amount, "win": None}

    def resolve(self, e, result):
        e["res"] = result
        win = e["side"] == result
        e["win"] = win
        if win:
            payout = math.floor(e["amount"] * AB_MULTI)
            self.balance += payout
            e["pnl"] = payout - e["amount"]
            self.w += 1
        else:
            self.l += 1
        pt = dict(e)
        pt["t"] = int(time.time())
        pt["net"] = self.net()
        pt["bal"] = self.balance
        self.series.append(pt)
        if len(self.series) > AB_SERIES_KEEP:
            del self.series[:len(self.series) - AB_SERIES_KEEP]
        return win

    def to_dict(self):
        return {"balance": self.balance, "start_bal": self.start_bal, "nick": self.nick, "rounds": self.rounds,
                "w": self.w, "l": self.l, "withdrawn": self.withdrawn, "staked": self.staked, "series": self.series, "t0": self.t0}

    @classmethod
    def from_dict(cls, d):
        o = cls(int(d.get("start_bal") or 0), d.get("nick") or "")
        o.balance = int(d.get("balance") or 0)
        o.rounds, o.w, o.l = int(d.get("rounds") or 0), int(d.get("w") or 0), int(d.get("l") or 0)
        o.withdrawn = int(d.get("withdrawn") or 0)
        o.series = [x for x in (d.get("series") or []) if isinstance(x, dict)][-AB_SERIES_KEEP:]
        o.staked = int(d.get("staked") or sum(int(x.get("amount") or 0) for x in o.series))
        o.t0 = d.get("t0") or time.time()
        return o


_ab_lock = threading.RLock()
_ab_sessions = {}               # sid -> AbSession
_ab_leader = {"ok": None, "fd": None}
_ab_save_t = {"t": 0.0}


def ab_sid(username):
    return hashlib.sha1(username.strip().lower().encode("utf-8")).hexdigest()[:10]


def _ab_owner_valid(owner):
    """Key chủ phiên còn dùng được không (còn tồn tại · đúng game autolc · chưa hết hạn). Phiên cũ không có owner -> coi như hợp lệ. Lỗi đọc file -> KHÔNG dừng oan."""
    if not owner:
        return True
    try:
        with _kv_lock:
            r = _kv_load()["keys"].get(owner)
        return bool(r and r.get("type") == "user" and _key_game(r) == "autolc" and not _is_expired(r, int(time.time())))
    except Exception:  # noqa: BLE001
        return True


class AbSession:
    """1 tài khoản LC79 đang auto cược. Toàn bộ logic thắng/thua/x2/giảm/pause ported nguyên từ AutoBetSession của bot."""

    def __init__(self, username, password, jwt, balance, nick):
        self.sid = ab_sid(username)
        self.username, self.password, self.jwt, self.nick = username, password, jwt, nick
        self.cfg = dict(AB_CFG_DEFAULT)
        self.ledger = AbLedger(balance, nick)
        self.mlock = threading.RLock()
        self.alive = False                 # luồng đang chạy
        self.hold = False                  # tạm dừng thủ công (không cược, không đổi trạng thái)
        self.stop_reason = "ready"         # ready | stopped | target | nofund | wd_stop | error | restart
        self.logs = []
        self.reset_state()
        self.open = None                   # ván đang chờ kết quả: {phien, side, entry|None(ảo), attempts}
        self.last_phien = 0                # phiên cuối đã xử lý (cược / theo dõi ảo / bỏ qua)
        self._attempts = {}                # phien -> số lần thử cược
        self.wd_count = 0
        self._wd_lock = False
        self._wd_fails = 0
        self._wd_next = 0.0
        self._bal_fail = 0
        self._fin_lk = threading.Lock()    # đảm bảo "dừng + rút khi đạt lãi" chỉ chạy 1 lần
        self._sync_lk = threading.Lock()   # tuần tự hoá các lần quét số dư (không 2 lần chạy chồng nhau)
        self._login_money = None           # số dư lấy từ lần đăng nhập lại gần nhất (dự phòng khi API số dư không đọc được)
        self._jwt_chk = 0.0                # lần cuối kiểm tra hạn JWT
        self.thread = None
        self.ws = AbWs(self)               # WebSocket cược (Socket.IO /txmd5)
        self.owner = ""                    # key AUTO CƯỢC LC sở hữu phiên này ("" = phiên cũ tạo trước bản có key)

    def reset_state(self):
        self.current_bet = self.cfg["bet"]
        self.loss_streak = self.win_streak = self.recovery_wins = 0
        self.paused = False
        self._is_reduced = self._loss_x2_triggered = self._x2_active = False

    # ── nhật ký sự kiện (hiện ở UI) ──
    def log(self, kind, msg, **extra):
        e = {"t": int(time.time()), "kind": kind, "msg": msg, "r": self.ledger.rounds}
        e.update(extra)
        self.logs.append(e)
        if len(self.logs) > AB_LOG_KEEP:
            del self.logs[:len(self.logs) - AB_LOG_KEEP]

    # ── dẫn xuất từ cấu hình (các công tắc trên UI) ──
    @property
    def base_bet(self):
        return self.cfg["bet"]

    @property
    def double_on_loss(self):
        return self.cfg["loss_mode"] == "x2"

    @property
    def reset_on_loss(self):
        return self.cfg["loss_mode"] == "reset"

    @property
    def double_on_win(self):
        return self.cfg["win_mode"] == "x2"

    @property
    def reset_on_win(self):
        return self.cfg["win_mode"] == "reset"

    @property
    def martingale(self):
        return self.double_on_loss

    # ── logic thắng / thua (ported) ──
    def on_win(self):
        c = self.cfg
        with self.mlock:
            self.win_streak += 1
            self.loss_streak = 0
            if self.paused:
                self.recovery_wins += 1
                return
            if self._loss_x2_triggered:
                self._loss_x2_triggered = False
                self.current_bet = self.base_bet
                return
            if self._is_reduced:
                self._is_reduced = False
                self.current_bet = self.base_bet
                return
            if self.double_on_win:
                threshold = c["win_x2_streak"] if c["win_x2_streak"] > 0 else 1
                if self.win_streak >= threshold:
                    doubled = min(self.base_bet * 2, self.ledger.balance)
                    if self.current_bet < doubled:
                        self.current_bet = doubled
                        self._x2_active = True
                    elif self._x2_active:
                        if not c["win_x2_keep"]:
                            self.current_bet = self.base_bet
                            self._x2_active = False
                            self.win_streak = 0
            elif self.reset_on_win or self.martingale:
                self.current_bet = self.base_bet
                self._x2_active = False
                self.win_streak = 0

    def on_loss(self):
        c = self.cfg
        with self.mlock:
            self.loss_streak += 1
            self.win_streak = 0
            if self.paused:
                self.recovery_wins = 0
                return
            lx2 = c["loss_x2_streak"] if c["loss_x2_on"] else 0
            if lx2 > 0 and self.loss_streak >= lx2:
                if not self._loss_x2_triggered:
                    self._loss_x2_triggered = True
                    self.current_bet = min(self.base_bet * 2, self.ledger.balance)
                return
            lsr = c["reduce_streak"] if c["reduce_on"] else 0
            if lsr > 0 and self.loss_streak >= lsr and not self._is_reduced:
                self._is_reduced = True
                self.current_bet = max(c["reduce_bet"] or self.base_bet, 1)
                return
            if self.double_on_win:
                self._is_reduced = False
                self._x2_active = False
                self.current_bet = self.base_bet
            elif self.double_on_loss:
                self.current_bet = min(self.current_bet * 2, self.ledger.balance)
            elif self.reset_on_loss:
                self.current_bet = self.base_bet

    def should_pause(self):
        return self.cfg["pause_on"] and self.cfg["pause_streak"] > 0 and self.loss_streak >= self.cfg["pause_streak"]

    def should_resume(self):
        return self.paused and self.cfg["resume_wins"] > 0 and self.recovery_wins >= self.cfg["resume_wins"]

    def hit_target(self):
        return self.cfg["target_on"] and self.cfg["target"] > 0 and self.ledger.net() >= self.cfg["target"]

    def apply_cfg(self, newcfg):
        """Đổi cấu hình khi đang chạy: cược gốc đổi thì cược hiện tại theo (nếu đang ở mức gốc); công tắc nào tắt thì bỏ trạng thái đặc biệt tương ứng."""
        with self.mlock:
            old = self.cfg
            self.cfg = newcfg
            was_base = self.current_bet == old["bet"]
            changed = False
            if not self.double_on_win and self._x2_active:
                self._x2_active, changed = False, True
            if not newcfg["loss_x2_on"] and self._loss_x2_triggered:
                self._loss_x2_triggered, changed = False, True
            if not newcfg["reduce_on"] and self._is_reduced:
                self._is_reduced, changed = False, True
            if not newcfg["pause_on"] and self.paused:
                self.paused, self.recovery_wins, self.loss_streak, changed = False, 0, 0, True
                self.log("info", "Đã tắt Pause — cược lại bình thường")
            if changed or was_base:
                self.current_bet = newcfg["bet"]

    # ── vòng đời ──
    def start(self):
        with _ab_lock:
            if self.alive:
                return
            self.alive = True
            self.stop_reason = "running"
            self.thread = threading.Thread(target=self._run, daemon=True, name=f"autobet-{self.sid}")
            self.thread.start()
            self.ws.start()
        self.log("info", "Bắt đầu auto cược")
        ab_save(force=True)

    def stop(self, reason="stopped", msg=None):
        self.alive = False
        self.stop_reason = reason
        try:
            self.ws.close()
        except Exception:  # noqa: BLE001
            pass
        if msg:
            self.log("warn" if reason in ("nofund", "error", "wd_stop", "expired") else "info", msg)
        ab_save(force=True)

    def _zero_guard(self):
        """Số dư về 0 -> DỪNG HẲN auto cược (kể cả đang pause / tạm dừng). Chỉ kết luận khi KHÔNG còn ván cược THẬT đang chờ kết quả
        (tiền cược vừa bị trừ khỏi số dư nên all-in sẽ tạm về 0 — phải chờ kết quả: thắng thì số dư có lại)."""
        if not self.alive:
            return False
        o = self.open
        if o and o.get("entry") is not None:
            return False
        if self.ledger.balance > 0:
            return False
        self.hold = False
        self.stop("nofund", "Số dư về 0 — đã dừng hẳn auto cược")
        return True

    def _run(self):
        nxt = 0.0
        while self.alive:
            try:
                now = time.time()
                if now >= nxt:                                             # định kỳ kiểm tra key chủ phiên: hết hạn / bị xoá / sai game -> tự dừng
                    nxt = now + AB_KEY_RECHECK
                    if not _ab_owner_valid(self.owner):
                        self.stop("expired", "Key auto cược đã hết hạn hoặc bị xoá — auto cược tự dừng")
                        break
                self._tick()
            except Exception as e:  # noqa: BLE001 - giữ luồng sống
                self.log("error", f"Lỗi nội bộ: {type(e).__name__}: {e}")
            time.sleep(AB_TICK)

    def _feed(self):
        tb = HIT_TABLES.get(AB_FEED_KEY)
        if tb is None or not tb.active:
            return None, 0, None
        pend = tb.pending if isinstance(tb.pending, dict) else None
        try:
            latest = max(tb.hist) if tb.hist else 0
        except ValueError:
            latest = 0
        return tb, latest, (dict(pend) if pend else None)

    def _tick(self):
        if self._zero_guard():                                             # số dư về 0 -> dừng hẳn (chạy mỗi nhịp, trước mọi việc khác)
            return
        if self.password and time.time() >= self._jwt_chk:                 # JWT sống 8 giờ -> tự đăng nhập lại khi còn < 15 phút (không đợi bị 401)
            self._jwt_chk = time.time() + 60
            ex = _ab_jwt_exp(self.jwt)
            if ex and ex - time.time() < 900:
                self._relogin()
        self.ws.watchdog()                                                 # WS không nghe được -> báo lý do vào nhật ký + ép nối lại
        tb, latest, pend = self._feed()
        if tb is None:
            return
        o = self.open
        if o:                                                              # 1) có ván đang chờ -> xem đã có kết quả chưa
            rec = tb.hist.get(o["phien"])
            if rec:
                self._on_result(o, rec["actual"])
            elif latest > o["phien"]:                                      # API không trả phiên đó -> huỷ ván, đồng bộ lại số dư
                self.open = None
                if o.get("entry"):
                    o["entry"]["res"], o["entry"]["win"], o["entry"]["pnl"] = "?", None, 0
                    self.ledger.rounds -= 1
                    self.ledger.staked -= int(o["entry"].get("amount") or 0)
                    self.log("warn", f"Phiên #{o['phien']} không có kết quả từ nguồn — đã bỏ qua ván, đồng bộ lại số dư")
                    self._sync_balance(o["phien"])
            return
        if not self.alive or self.hold:
            return
        if not pend or pend["phien"] <= latest or pend["phien"] <= self.last_phien:        # 2) phiên mới có dự đoán -> đặt cược
            return
        phien = pend["phien"]
        side = "TAI" if pend["du_doan"] == TAI else "XIU"
        if self.paused:                                                    # đang pause: theo dõi ảo, không tốn tiền
            self.last_phien = phien
            self.open = {"phien": phien, "side": side, "entry": None}
            return
        if self.ledger.balance < self.current_bet:
            self.stop("nofund", f"Không đủ số dư để cược (cần {self.current_bet:,}, còn {self.ledger.balance:,}) — đã dừng")
            return
        if not self.ws.can_bet():                                          # WS chưa vào namespace / state chưa phải BETTING -> chờ, chưa tính là lần thử
            return
        n = self._attempts.get(phien, 0)
        if n >= AB_BET_RETRY:
            self.last_phien = phien
            self.log("warn", f"Phiên #{phien}: gửi cược thất bại {n} lần — bỏ qua ván này")
            return
        self._attempts[phien] = n + 1
        if len(self._attempts) > 20:
            for k in sorted(self._attempts)[:-5]:
                del self._attempts[k]
        try:
            ok, st, raw = self.ws.send_bet(side, self.current_bet)
        except Exception as e:  # noqa: BLE001 - timeout: không rõ nhà cái đã nhận chưa -> KHÔNG thử lại để khỏi cược đôi
            self.last_phien = phien
            self.log("warn", f"Phiên #{phien}: không rõ cược đã gửi chưa ({type(e).__name__}) — bỏ qua, sẽ đồng bộ số dư")
            self._sync_after(AB_SYNC_DELAY, check_target=False)
            return
        if not ok:
            if st in (401, 403):
                self._relogin()
            self.log("warn", f"Phiên #{phien}: Gửi cược thất bại ({raw}) — thử lại ({n + 1}/{AB_BET_RETRY})")
            return
        self.last_phien = phien
        entry = self.ledger.bet(side, self.current_bet, phien)
        self.open = {"phien": phien, "side": side, "entry": entry}
        self.log("bet", f"#{phien} đặt {'Tài' if side == 'TAI' else 'Xỉu'} {self.current_bet:,}", phien=phien)
        self._sync_after(0.0, check_target=False)                          # quét số dư NGAY sau khi đặt cược (tiền cược vừa trừ -> không thể vừa đạt mục tiêu)

    def _on_result(self, o, actual):
        """Có kết quả phiên o['phien'] (actual = TÀI | XỈU)."""
        self.open = None
        phien = o["phien"]
        res = "TAI" if actual == TAI else "XIU"
        res_txt = "Tài" if res == "TAI" else "Xỉu"
        if o.get("entry") is None:                                         # ván ẢO (đang pause)
            virt_win = o["side"] == res
            self.on_win() if virt_win else self.on_loss()
            if self.should_resume():
                self.paused, self.recovery_wins, self.loss_streak = False, 0, 0
                self.current_bet = self.base_bet
                self.log("info", f"Thắng đủ {self.cfg['resume_wins']} ván liên tiếp — cược lại, mức {self.current_bet:,}")
            else:
                need = max(self.cfg["resume_wins"] - self.recovery_wins, 0)
                self.log("virt", f"#{phien} (theo dõi ảo) {'✅' if virt_win else '❌'} — còn cần thắng {need} ván liên tiếp", ok=virt_win)
            return
        entry = o["entry"]
        win = self.ledger.resolve(entry, res)
        pnl = entry["pnl"]
        self.log("win" if win else "loss", f"#{phien} KQ {res_txt} · {'+' if pnl > 0 else ''}{pnl:,}", phien=phien, pnl=pnl)
        if win:
            was_reduced, was_x2 = self._is_reduced, self._x2_active
            self.on_win()
            if was_reduced and not self._is_reduced:
                self.log("info", f"Thắng — về cược gốc {self.current_bet:,}")
            elif was_x2 and self.double_on_win and not self.cfg["win_x2_keep"] and not self._x2_active:
                self.log("info", f"Thắng x2 — về cược gốc {self.current_bet:,}")
            elif was_x2 is False and self._x2_active:
                self.log("info", f"Thắng {self.win_streak} ván liên tiếp — x2 cược: {self.current_bet:,}")
            if self.hit_target():
                time.sleep(AB_SYNC_DELAY)                                  # chờ nhà cái cộng tiền thắng rồi quét số dư thật
                with self._sync_lk:
                    self._sync_balance(phien, check_target=False)
                self._finish_target()                                      # dừng toàn bộ cược (+ rút luôn nếu đã chọn)
                return
        else:
            self.on_loss()
            if self._loss_x2_triggered and self.loss_streak == self.cfg["loss_x2_streak"]:
                self.log("info", f"Thua {self.loss_streak} ván liên tiếp — x2 một lần: {self.current_bet:,}")
            if self._is_reduced and self.loss_streak == self.cfg["reduce_streak"]:
                self.log("info", f"Thua {self.loss_streak} ván liên tiếp — giảm cược xuống {self.current_bet:,}")
            elif self.should_pause():
                self.paused, self.recovery_wins = True, 0
                need = self.cfg["resume_wins"] if self.cfg["resume_wins"] > 0 else "?"
                self.log("pause", f"Thua {self.loss_streak} ván liên tiếp — TẠM DỪNG, chờ thắng {need} ván liên tiếp để cược lại")
        self._sync_after(AB_SYNC_DELAY)                                    # có kết quả -> đợi ~2s rồi quét số dư 1 lần (nền)
        if self.alive and self.ledger.balance < self.current_bet and not self.paused:
            self.stop("nofund", f"Không đủ số dư để cược tiếp (cần {self.current_bet:,}, còn {self.ledger.balance:,}) — đã dừng")

    # ── đồng bộ số dư thật + auto rút ──
    def _relogin(self):
        if not (self.username and self.password):
            return False
        try:
            jwt, bal, nick, err = ab_login(self.username, self.password)
        except Exception:  # noqa: BLE001
            return False
        if jwt:
            self.jwt = jwt
            self._login_money = bal
            self.log("info", "Đã đăng nhập lại (JWT hết hạn)")
            try:
                self.ws.restart()
            except Exception:  # noqa: BLE001
                pass
            return True
        return False

    def _sync_after(self, delay=0.0, check_target=True):
        """Quét số dư thật ở luồng nền sau `delay` giây (không chặn vòng cược). Chỉ gọi theo SỰ KIỆN: ngay sau khi đặt cược · sau khi có kết quả + AB_SYNC_DELAY."""
        def run():
            if delay > 0:
                time.sleep(delay)
            with self._sync_lk:
                try:
                    self._sync_balance(self.last_phien, check_target)
                except Exception as e:  # noqa: BLE001
                    self.log("warn", f"Lỗi quét số dư: {type(e).__name__}: {e}")
        threading.Thread(target=run, daemon=True, name=f"abbal-{self.sid}").start()

    def _sync_balance(self, phien, check_target=True):
        real = ab_fetch_balance(self.jwt)
        if real is None and self._relogin():
            real = ab_fetch_balance(self.jwt)
        if real is None:
            self._bal_fail += 1
            if self._bal_fail == 3:
                self.log("warn", f"Không lấy được số dư thật ({self._bal_fail} lần) — đang dùng số dư ước tính {self.ledger.balance:,}")
            return
        self._bal_fail = 0
        diff = real - self.ledger.balance
        if diff:
            if abs(diff) >= 500 or abs(diff) / max(self.ledger.balance, 1) >= 0.01:
                self.log("info", f"Đồng bộ số dư: tool tính {self.ledger.balance:,} → thực tế {real:,} ({'+' if diff > 0 else ''}{diff:,})")
            self.ledger.balance = real
            if self.ledger.series:                                         # cập nhật điểm cuối của biểu đồ theo số dư thật
                self.ledger.series[-1]["bal"] = real
                self.ledger.series[-1]["net"] = self.ledger.net()
        ab_save()
        if check_target and self.alive and self.hit_target():              # quét số dư thật đạt ngưỡng lãi -> dừng hết + rút luôn
            self._finish_target()
        if self.alive:
            self._zero_guard()                                             # số dư thật về 0 -> dừng hẳn

    def _finish_target(self):
        """Đạt mục tiêu lãi: DỪNG TOÀN BỘ CƯỢC trước, rồi (nếu đã chọn) rút hết số dư về tài khoản đã chọn. Chỉ chạy 1 lần."""
        with self._fin_lk:
            if not self.alive:
                return
            c = self.cfg
            self.stop("target", f"Đạt mục tiêu lãi {self.ledger.net():+,} (≥ {c['target']:,}) — đã dừng toàn bộ cược")
            if not c["wd_on"]:
                return
            self._withdraw_all()

    def _withdraw_all(self):
        """Gửi ĐÚNG 1 lệnh rút bằng số tiền ngưỡng người dùng đặt (không làm tròn mệnh giá, không chia nhỏ, không áp hạn mức của tool)."""
        c = self.cfg
        dest = _ab_wd_label(c["wd_kind"], c["wd_code"], c["wd_number"])
        self._wd_lock = True
        try:
            bal = ab_fetch_balance(self.jwt)
            if bal is None and self._relogin():
                bal = ab_fetch_balance(self.jwt)
            if bal is not None:
                self.ledger.balance = bal
            amt = c["target"] if bal is None else min(c["target"], bal)      # số dư không đủ ngưỡng thì rút tối đa số dư đang có
            if amt <= 0:
                self.log("warn", "Rút: số dư bằng 0 — không có gì để rút", ok=False)
                return
            self.log("wd", f"Đang gửi lệnh rút {amt:,} → {dest}")
            ok, msg = False, ""
            for attempt in range(AB_WD_MAX_FAILS):
                ok, msg, _ = ab_withdraw(self.jwt, amt, c["wd_kind"], c["wd_code"], c["wd_number"], c["wd_name"])
                if not ok and "JWT hết hạn" in str(msg) and self._relogin():
                    ok, msg, _ = ab_withdraw(self.jwt, amt, c["wd_kind"], c["wd_code"], c["wd_number"], c["wd_name"])
                if ok:
                    break
                self.log("warn", f"Rút thất bại ({attempt + 1}/{AB_WD_MAX_FAILS}): {str(msg)[:160]}", ok=False)
                time.sleep(3)
            if ok:
                self.wd_count += 1
                self.ledger.balance -= amt
                self.ledger.withdrawn += amt
                self.log("wd", f"ĐÃ GỬI LỆNH RÚT {amt:,} → {dest}", amount=amt, ok=True)
            else:
                self.log("warn", f"Không gửi được lệnh rút {amt:,} — hãy rút tay trên LC79", ok=False)
        except Exception as e:  # noqa: BLE001
            self.log("warn", f"Lỗi khi rút: {type(e).__name__}: {e}", ok=False)
        finally:
            self._wd_lock = False
            ab_save(force=True)

    # ── xuất dữ liệu cho UI (KHÔNG có mật khẩu / JWT) ──
    def status(self):
        if not self.alive:
            return self.stop_reason if self.stop_reason in ("ready", "target", "nofund", "wd_stop", "error", "restart", "expired") else "stopped"
        if self.hold:
            return "hold"
        return "paused" if self.paused else "running"

    def view(self, full=False):
        L = self.ledger
        n = L.net()
        o = self.open
        d = {
            "id": self.sid, "username": self.username, "nick": self.nick, "status": self.status(), "alive": self.alive, "hold": self.hold,
            "paused": self.paused, "balance": L.balance, "start_bal": L.start_bal, "net": n, "rounds": L.rounds, "w": L.w, "l": L.l,
            "wr": round(L.w / (L.w + L.l) * 100, 1) if (L.w + L.l) else None,
            "bet": self.current_bet, "base_bet": self.base_bet, "withdrawn": L.withdrawn, "wd_count": self.wd_count,
            "loss_streak": self.loss_streak, "win_streak": self.win_streak, "recovery_wins": self.recovery_wins,
            "x2_active": self._x2_active or self._loss_x2_triggered, "reduced": self._is_reduced,
            "open": ({"phien": o["phien"], "side": o["side"], "virtual": o.get("entry") is None,
                      "amount": (o["entry"] or {}).get("amount")} if o else None),
            "cfg": self.cfg, "t0": L.t0, "has_pw": bool(self.password), "ws": self.ws.info(),
        }
        if full:
            d["series"] = [{"r": p["r"], "t": p["t"], "net": p["net"], "bal": p["bal"], "pnl": p["pnl"], "win": p["win"],
                            "side": p["side"], "res": p["res"], "amount": p["amount"], "phien": p["phien"]} for p in L.series]
            d["logs"] = self.logs[-AB_LOG_KEEP:]
        return d

    def dump(self):
        d = {"username": self.username, "nick": self.nick, "cfg": self.cfg, "ledger": self.ledger.to_dict(), "alive": self.alive,
             "hold": self.hold, "owner": self.owner, "stop_reason": self.stop_reason, "wd_count": self.wd_count, "logs": self.logs[-AB_LOG_KEEP:],
             "state": {"current_bet": self.current_bet, "loss_streak": self.loss_streak, "win_streak": self.win_streak,
                       "recovery_wins": self.recovery_wins, "paused": self.paused, "reduced": self._is_reduced,
                       "lx2": self._loss_x2_triggered, "x2": self._x2_active}, "last_phien": self.last_phien}
        if AB_SAVE_PW:
            _e = _ab_encrypt(self.password)
            if _e:                                          # không mã hoá được (thiếu SUNVIW_SECRET / thư viện cryptography) -> KHÔNG lưu mật khẩu
                d["pw_enc"], d["jwt"] = _e, ""
        return d


def _ab_fernet():
    sec = os.environ.get("SUNVIW_SECRET", "")
    if len(sec) < 24:
        return None
    try:
        from cryptography.fernet import Fernet
        return Fernet(base64.urlsafe_b64encode(hashlib.sha256(b"sunviw-ab-pw:" + sec.encode("utf-8")).digest()))
    except Exception:  # noqa: BLE001
        return None


def _ab_encrypt(pw):
    f = _ab_fernet()
    return f.encrypt(str(pw or "").encode("utf-8")).decode() if f and pw else ""


def _ab_decrypt(tok):
    f = _ab_fernet()
    try:
        return f.decrypt(str(tok).encode()).decode("utf-8") if f and tok else ""
    except Exception:  # noqa: BLE001
        return ""


def ab_save(force=False):
    """Lưu mọi phiên ra file (tối đa 1 lần / 2 giây trừ khi force)."""
    now = time.time()
    if not force and now - _ab_save_t["t"] < 2.0:
        return
    _ab_save_t["t"] = now
    try:
        with _ab_lock:
            data = {"luu_luc": _now(), "sessions": [s.dump() for s in _ab_sessions.values()]}
        tmp = AB_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, AB_PATH)
    except Exception:  # noqa: BLE001
        pass


def ab_is_leader():
    """Chỉ MỘT worker được chạy auto cược (khoá file) -> không bao giờ 2 tiến trình cùng đặt cược 1 ván."""
    if _ab_leader["ok"] is not None:
        return _ab_leader["ok"]
    if fcntl is None:
        _ab_leader["ok"] = True
        return True
    try:
        fd = open(AB_LOCK_PATH, "a+")
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _ab_leader["fd"] = fd                              # giữ fd mở suốt đời tiến trình
        _ab_leader["ok"] = True
    except Exception:  # noqa: BLE001
        _ab_leader["ok"] = False
    return _ab_leader["ok"]


def ab_boot():
    """Gọi 1 lần khi server khởi động: nạp phiên đã lưu. Có AUTOBET_SAVE_PW + mật khẩu -> tự chạy lại phiên đang chạy; không thì để ở trạng thái dừng (cần đăng nhập lại)."""
    if not AB_ENABLED or not ab_is_leader():
        return
    try:
        with open(AB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:  # noqa: BLE001
        return
    for d in (data.get("sessions") or []) if isinstance(data, dict) else []:
        try:
            u = str(d.get("username") or "")
            if not u:
                continue
            s = AbSession(u, _ab_decrypt(d.get("pw_enc") or ""), d.get("jwt") or "", 0, d.get("nick") or u)
            s.cfg = ab_clean_cfg(d.get("cfg") or {}, AB_CFG_DEFAULT) if d.get("cfg") else s.cfg
            s.ledger = AbLedger.from_dict(d.get("ledger") or {})
            s.logs = [x for x in (d.get("logs") or []) if isinstance(x, dict)][-AB_LOG_KEEP:]
            s.wd_count = int(d.get("wd_count") or 0)
            s.hold = bool(d.get("hold"))
            s.owner = str(d.get("owner") or "")
            st = d.get("state") or {}
            s.current_bet = int(st.get("current_bet") or s.cfg["bet"])
            s.loss_streak, s.win_streak = int(st.get("loss_streak") or 0), int(st.get("win_streak") or 0)
            s.recovery_wins, s.paused = int(st.get("recovery_wins") or 0), bool(st.get("paused"))
            s._is_reduced, s._loss_x2_triggered, s._x2_active = bool(st.get("reduced")), bool(st.get("lx2")), bool(st.get("x2"))
            s.last_phien = int(d.get("last_phien") or 0)
            was_alive = bool(d.get("alive"))
            s.stop_reason = d.get("stop_reason") or "stopped"
            _ab_sessions[s.sid] = s
            if was_alive and AB_SAVE_PW and s.password:
                if not s.jwt or ab_fetch_balance(s.jwt) is None:
                    s._relogin()
                real = ab_fetch_balance(s.jwt) if s.jwt else None
                if real is not None:
                    s.ledger.balance = real
                    s.log("info", "Server khởi động lại — tự chạy tiếp auto cược")
                    s.start()
                    continue
            if was_alive:
                s.stop_reason = "restart"
                s.log("warn", "Server đã khởi động lại — auto cược dừng, cần đăng nhập lại để chạy tiếp")
        except Exception:  # noqa: BLE001
            continue


# ── Trang + API ──
def _ab_gate():
    """MỖI request tới /tool/autocuoc/api/* (và /tool/autocuoc/ui) PHẢI kèm KEY AUTO CƯỢC LC (header X-User-Key) + HWID thiết bị (header X-HWID) — y như các endpoint dự đoán.
    Key sai / hết hạn / sai game (key Sun · Hit · LC79 không dùng được ở đây) / thiết bị đã đủ chỗ -> 401 / 403, KHÔNG trả dữ liệu (kể cả dự đoán).
    Trả None nếu cho qua (và ghi flask_g.ab_key = key đang dùng), ngược lại trả Response."""
    hw, alts, hfresh = req_hw_ids(request.get_json(silent=True) if request.method == "POST" else None)
    ip = client_ip()
    w = _rl_wait(ip)
    if w:
        return _json({"ok": False, "can_key": True, "loi": f"nhap sai qua nhieu, thu lai sau {w}s"}, 429)
    k = _norm_key(request.headers.get("X-User-Key", ""))
    if not _rate_ok(f"abip:{ip}", RATE_IP) or (k and not _rate_ok(f"abk:{k}", 240)):
        return _too_many()
    rec, err, exists, kg = _check_user_key(k, hw, ip, request.headers.get("User-Agent", ""), alts, hfresh, "autolc", bind=False)
    if not rec:
        if k and not exists:
            _rl_fail(ip)
        if err.startswith(WRONG_GAME_MSG):
            return _json({"ok": False, "sai_game": True, "can_key": True, "game_can": kg, "game": "autolc", "loi": err}, 403)
        hint = " (gui header X-User-Key)" if err in ("thieu key", "key khong hop le") else ""
        return _json({"ok": False, "can_key": True, "dev_locked": err.startswith("Key đã đủ"), "loi": err + hint}, 401)
    _rl_reset(ip)
    flask_g.ab_key = k
    if not AB_ENABLED:
        return _json({"ok": False, "loi": "Auto cược đang TẮT (AUTOBET=0)."}, 503)
    if not ab_is_leader():
        return _json({"ok": False, "loi": "Worker này không giữ khoá auto cược — hãy chạy gunicorn với --workers 1."}, 503)
    return None


def _ab_owner():
    return getattr(flask_g, "ab_key", "")


def _ab_feed_view():
    tb = HIT_TABLES.get(AB_FEED_KEY)
    if tb is None:
        return {"ok": False}
    pend = tb.pending if isinstance(tb.pending, dict) else None
    try:
        latest = max(tb.hist) if tb.hist else 0
    except ValueError:
        latest = 0
    with tb.slock:
        err = tb.state.get("error")
    last = tb.hist.get(latest) if latest else None
    return {"ok": bool(tb.active and not err), "ban": tb.label, "loi": ("nguon du doan tam thoi loi" if err else None),
            "phien": pend["phien"] if pend and pend["phien"] > latest else None,
            "du_doan": pend["du_doan"] if pend and pend["phien"] > latest else None,
            "phien_truoc": latest or None, "ket_qua_truoc": last["actual"] if last else None,
            "xuc_xac": [last["d1"], last["d2"], last["d3"]] if last else None}


def _ab_get(sid):
    """Phiên theo id, CHỈ khi thuộc key đang gọi (key này không thấy / không điều khiển được tài khoản của key khác)."""
    with _ab_lock:
        s = _ab_sessions.get(sid or "")
    return s if s is not None and s.owner == _ab_owner() else None


@app.route("/tool/autocuoc")
@app.route("/tool/autocuoc/")
@app.route("/api/autocuoc")
@app.route("/api/autocuoc/")
@app.route("/autocuoc")
def tool_autocuoc():
    """Chỉ trả MÀN NHẬP KEY (không chứa giao diện auto cược). Nhập đúng key -> trình duyệt gọi /tool/autocuoc/ui kèm key để nhận giao diện."""
    resp = Response(AB_SHELL.replace("/*__HWID_JS__*/", HWID_JS), content_type="text/html; charset=utf-8")
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


@app.route("/tool/autocuoc/ui")
def tool_autocuoc_ui():
    """Giao diện auto cược (css + html + js) — CHỈ trả khi key AUTO CƯỢC LC hợp lệ (header X-User-Key + X-HWID)."""
    g = _ab_gate()
    if g is not None:
        return g
    resp = _json({"ok": True, **AB_UI})
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/tool/autocuoc/api/state")
def tool_autocuoc_state():
    g = _ab_gate()
    if g is not None:
        return g
    own = _ab_owner()
    with _ab_lock:
        sess = [s for s in _ab_sessions.values() if s.owner == own]          # mỗi key chỉ thấy tài khoản của chính mình
    sel = _ab_get(request.args.get("id", ""))
    if sel is None and sess:
        sel = next((s for s in sess if s.alive), sess[0])
    return _json({"ok": True, "feed": _ab_feed_view(), "sessions": [s.view() for s in sess],
                  "selected": sel.view(full=True) if sel else None,
                  "luu_mk": AB_SAVE_PW, "multi": AB_MULTI,
                  "wd_limits": {"momo": [AB_MOMO_MIN, AB_MOMO_MAX], "bank": [AB_BANK_MIN, AB_BANK_MAX]}})


@app.route("/tool/autocuoc/api/login", methods=["POST"])
def tool_autocuoc_login():
    g = _ab_gate()
    if g is not None:
        return g
    b = request.get_json(silent=True) or {}
    u, p = str(b.get("username") or "").strip()[:60], str(b.get("password") or "")[:120]
    if not u or not p:
        return _json({"ok": False, "loi": "Nhập tên đăng nhập và mật khẩu LC79"}, 400)
    sid = ab_sid(u)
    owner = _ab_owner()
    with _ab_lock:
        cur = _ab_sessions.get(sid)
        if cur is not None and cur.owner and cur.owner != owner:
            if cur.alive:
                return _json({"ok": False, "loi": "Tài khoản LC79 này đang được key khác dùng để auto cược."}, 409)
            cur = None                                       # phiên cũ của key khác đã dừng -> bắt đầu phiên mới (không lộ lịch sử cũ)
        if cur is None and sid not in _ab_sessions and len(_ab_sessions) >= AB_MAX_SESSIONS:
            return _json({"ok": False, "loi": f"Tối đa {AB_MAX_SESSIONS} tài khoản"}, 400)
    if cur is not None and cur.alive:
        return _json({"ok": False, "loi": "Tài khoản này đang chạy auto cược — chọn nó ở danh sách bên trái."}, 409)
    jwt, bal, nick, err = ab_login(u, p)
    if not jwt:
        if "Không kết nối" in str(err):                      # LC79 không phản hồi (KHÔNG phải sai mật khẩu)
            return _json({"ok": False, "sai_tk": False, "loi": err}, 502)
        return _json({"ok": False, "sai_tk": True, "loi": "Sai tài khoản hoặc mật khẩu"}, 400)   # KHÔNG dùng 401: 401 = key hỏng -> giao diện bị đá về màn nhập key
    with _ab_lock:
        if cur is None:
            cur = AbSession(u, p, jwt, bal, nick)
            _ab_sessions[sid] = cur
        else:
            cur.password, cur.jwt, cur.nick, cur.ledger.nick = p, jwt, nick, nick
            cur.ledger.balance = bal                         # bắt đầu lại / chạy tiếp: số dư thật hiện tại
        cur.stop_reason = "ready" if not cur.ledger.rounds else cur.stop_reason
        cur.owner = owner
    ab_save(force=True)
    return _json({"ok": True, "id": sid, "nick": nick, "balance": bal, "co_lich_su": cur.ledger.rounds > 0, "cfg": cur.cfg})


@app.route("/tool/autocuoc/api/start", methods=["POST"])
def tool_autocuoc_start():
    g = _ab_gate()
    if g is not None:
        return g
    b = request.get_json(silent=True) or {}
    s = _ab_get(b.get("id"))
    if s is None:
        return _json({"ok": False, "loi": "Không thấy tài khoản — đăng nhập lại"}, 404)
    if s.alive:
        return _json({"ok": False, "loi": "Đang chạy rồi"}, 409)
    try:
        cfg = ab_clean_cfg(b.get("cfg") or {}, s.cfg)
    except ValueError as e:
        return _json({"ok": False, "loi": str(e)}, 400)
    real = ab_fetch_balance(s.jwt)
    if real is None and s._relogin():                        # JWT vừa lấy mới -> còn hạn; không đọc được số dư thì dùng số dư của lần login
        real = ab_fetch_balance(s.jwt)
        if real is None:
            real = s._login_money
    if real is None:
        return _json({"ok": False, "sai_tk": True, "loi": "Không lấy được số dư / phiên đăng nhập hết hạn — đăng nhập lại"}, 409)
    if b.get("reset") or not s.ledger.rounds:                # bắt đầu MỚI: vốn = số dư thật hiện tại, biểu đồ về 0
        s.ledger = AbLedger(real, s.nick)
        s.wd_count, s.logs, s.open, s.last_phien = 0, [], None, 0
    else:                                                    # chạy TIẾP lịch sử cũ
        s.ledger.balance = real
    s.cfg = cfg
    s.reset_state()
    s.hold, s._wd_fails, s._wd_next, s._bal_fail = False, 0, 0.0, 0
    if real < cfg["bet"]:
        return _json({"ok": False, "loi": f"Số dư {real:,} không đủ cho mức cược {cfg['bet']:,}"}, 400)
    s.start()
    return _json({"ok": True, "id": s.sid})


@app.route("/tool/autocuoc/api/config", methods=["POST"])
def tool_autocuoc_config():
    g = _ab_gate()
    if g is not None:
        return g
    b = request.get_json(silent=True) or {}
    s = _ab_get(b.get("id"))
    if s is None:
        return _json({"ok": False, "loi": "Không thấy tài khoản"}, 404)
    try:
        cfg = ab_clean_cfg(b.get("cfg") or {}, s.cfg)
    except ValueError as e:
        return _json({"ok": False, "loi": str(e)}, 400)
    s.apply_cfg(cfg)
    ab_save(force=True)
    return _json({"ok": True, "cfg": s.cfg})


@app.route("/tool/autocuoc/api/action", methods=["POST"])
def tool_autocuoc_action():
    g = _ab_gate()
    if g is not None:
        return g
    b = request.get_json(silent=True) or {}
    s = _ab_get(b.get("id"))
    if s is None:
        return _json({"ok": False, "loi": "Không thấy tài khoản"}, 404)
    act = b.get("act")
    if act == "hold":
        s.hold = True
        s.log("info", "Tạm dừng thủ công — không đặt cược mới")
    elif act == "unhold":
        s.hold = False
        s.log("info", "Tiếp tục cược")
    elif act == "stop":
        s.stop("stopped", "Đã dừng auto cược")
    elif act == "remove":
        if s.alive:
            return _json({"ok": False, "loi": "Dừng auto cược trước khi xoá"}, 409)
        with _ab_lock:
            _ab_sessions.pop(s.sid, None)
    else:
        return _json({"ok": False, "loi": "Lệnh không hợp lệ"}, 400)
    ab_save(force=True)
    return _json({"ok": True})


@app.route("/tool/autocuoc/api/wallets", methods=["POST"])
def tool_autocuoc_wallets():
    """Lấy STK ngân hàng / ví Momo đã liên kết trên LC79 (khỏi nhập tay)."""
    g = _ab_gate()
    if g is not None:
        return g
    b = request.get_json(silent=True) or {}
    s = _ab_get(b.get("id"))
    if s is None:
        return _json({"ok": False, "loi": "Không thấy tài khoản"}, 404)
    kind = "bank" if b.get("kind") == "bank" else "momo"
    ws = ab_wallets(s.jwt, kind)
    return _json({"ok": True, "wallets": [{"code": str(w.get("type") or ""), "number": str(w.get("wallet_number") or ""),
                                           "name": str(w.get("wallet_name") or "")} for w in ws]})




def _ab_mask(s, keep=4):
    s = str(s or "")
    return ("•" * max(0, len(s) - keep) + s[-keep:]) if s else ""


def ab_strategy(cfg):
    """Mô tả CHIẾN THUẬT cược từ cấu hình -> {"ten": tên ngắn, "dong": [các dòng mô tả]} (hiện ở hồ sơ tài khoản trên trang admin)."""
    c = cfg or {}
    gi = lambda k, d=0: int(c.get(k) or d)
    lm, wm = c.get("loss_mode", "keep"), c.get("win_mode", "keep")
    act = {"keep": "giữ nguyên mức cược", "reset": "về cược gốc", "x2": "nhân đôi cược"}
    dong = [f"Cược gốc {gi('bet'):,} / ván — theo dự đoán bàn LC MD5"]
    dong.append("Khi THUA → " + act.get(lm, str(lm)) + (" (gấp thếp / Martingale)" if lm == "x2" else ""))
    if wm == "x2":
        dong.append(f"Khi THẮNG → nhân đôi sau {gi('win_x2_streak', 1)} ván thắng liên tiếp" + (" · giữ x2 tới khi thua" if c.get("win_x2_keep") else " · thắng 1 ván x2 xong về cược gốc"))
    else:
        dong.append("Khi THẮNG → " + act.get(wm, str(wm)))
    if c.get("loss_x2_on"):
        dong.append(f"Thua {gi('loss_x2_streak', 3)} ván liên tiếp → nhân đôi một lần (thắng lại về gốc)")
    if c.get("reduce_on"):
        dong.append(f"Thua {gi('reduce_streak', 3)} ván liên tiếp → giảm cược xuống {gi('reduce_bet'):,}")
    if c.get("pause_on"):
        dong.append(f"Thua {gi('pause_streak', 5)} ván liên tiếp → pause (theo dõi ảo), thắng {gi('resume_wins')} ván liên tiếp thì cược lại")
    if c.get("target_on") and gi("target") > 0:
        tail = (" → dừng + tự rút về " + ("Momo" if c.get("wd_kind") == "momo" else "Ngân hàng")) if (c.get("target_wd") or c.get("wd_on")) else " → dừng cược"
        dong.append(f"Mục tiêu lãi {gi('target'):,}" + tail)
    dong.append("Số dư về 0 → tự dừng hẳn auto cược")
    if lm == "x2":
        ten = "Gấp thếp (x2 khi thua)"
    elif wm == "x2":
        ten = "Tăng cược khi thắng"
    elif c.get("loss_x2_on"):
        ten = "x2 một lần sau chuỗi thua"
    elif lm == "reset" or wm == "reset":
        ten = "Cược gốc, reset theo kết quả"
    else:
        ten = "Cược phẳng"
    ex = [t for t, on in (("giảm cược", c.get("reduce_on")), ("pause", c.get("pause_on")), ("mục tiêu lãi", c.get("target_on") and gi("target") > 0)) if on]
    if ex:
        ten += " + " + " · ".join(ex)
    return {"ten": ten, "dong": dong}


def _ab_admin_view(s):
    """Hồ sơ 1 tài khoản auto cược cho trang admin (KHÔNG có mật khẩu / JWT; số tài khoản rút bị che)."""
    L = s.ledger
    c = dict(s.cfg)
    c["wd_number"] = _ab_mask(c.get("wd_number"))
    c.pop("wd_name", None)
    tong = L.w + L.l
    st = ab_strategy(s.cfg)
    return {
        "id": s.sid, "username": s.username, "nick": s.nick or s.username, "owner": s.owner or "",
        "status": s.status(), "alive": s.alive, "hold": s.hold, "paused": s.paused,
        "balance": L.balance, "start_bal": L.start_bal, "net": L.net(), "withdrawn": L.withdrawn, "wd_count": s.wd_count,
        "rounds": L.rounds, "wins": L.w, "losses": L.l, "wr": round(L.w / tong * 100, 1) if tong else None,
        "total_bet": int(getattr(L, "staked", 0) or 0), "current_bet": s.current_bet,
        "win_streak": s.win_streak, "loss_streak": s.loss_streak, "t0": int(L.t0 or 0), "has_pw": bool(s.password),
        "ten": st["ten"], "chien_thuat": st["dong"], "cfg": c,
        "recent": [{k: p.get(k) for k in ("phien", "side", "res", "amount", "pnl", "win", "t", "bal")} for p in list(L.series[-12:])[::-1]],
        "logs": list(s.logs[-20:])[::-1],
    }


def _need_main_cuoc():
    s, err = _need_admin()
    if err:
        return None, err
    if s["r"] != "main":
        return None, _json({"ok": False, "loi": "chi admin chinh moi xem duoc trang thai cuoc"}, 403)
    return s, None


@app.route("/api/admin/cuocstatus")
def api_admin_cuocstatus():
    """Trạng thái auto cược cho trang admin (CHỈ admin chính): TOÀN BỘ tài khoản đang / đã dùng auto cược + hồ sơ từng tài khoản (chiến thuật, số dư, tổng lãi/lỗ...)."""
    s, err = _need_main_cuoc()
    if err:
        return err
    with _ab_lock:
        sess = list(_ab_sessions.values())
    out = []
    for ss in sess:
        try:
            out.append(_ab_admin_view(ss))
        except Exception:  # noqa: BLE001 - 1 phiên lỗi không làm hỏng cả bảng
            continue
    out.sort(key=lambda x: (not x["alive"], -x["balance"]))
    return _json({"ok": True, "sessions": out, "bat": AB_ENABLED, "so_phien": len(out), "dang_chay": sum(1 for x in out if x["alive"])})


@app.route("/api/admin/cuocstatus/action", methods=["POST"])
def api_admin_cuocstatus_action():
    """Admin chính: dừng auto cược của 1 tài khoản ({"id","act":"stop"}) hoặc xoá hẳn tài khoản khỏi danh sách ({"id","act":"remove"} — đang chạy thì dừng trước)."""
    s, err = _need_main_cuoc()
    if err:
        return err
    b = request.get_json(silent=True) or {}
    sid = str(b.get("id") or "")
    with _ab_lock:
        ss = _ab_sessions.get(sid)
    if ss is None:
        return _json({"ok": False, "loi": "Không thấy tài khoản"}, 404)
    act = b.get("act")
    if act == "stop":
        if ss.alive:
            ss.stop("stopped", "Admin đã dừng auto cược")
    elif act == "remove":
        if ss.alive:
            ss.stop("stopped", "Admin đã xoá tài khoản")
        with _ab_lock:
            _ab_sessions.pop(sid, None)
    else:
        return _json({"ok": False, "loi": "Lệnh không hợp lệ"}, 400)
    ab_save(force=True)
    return _json({"ok": True})


def ab_health():
    with _ab_lock:
        return {"bat": AB_ENABLED, "leader": _ab_leader["ok"], "luu_mk": AB_SAVE_PW, "so_tai_khoan": len(_ab_sessions),
                "dang_chay": sum(1 for s in _ab_sessions.values() if s.alive), "file": AB_PATH}



AB_HTML = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Auto cược LC79</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0a1417; --bg2:#0e1b1f; --surf:#12242a; --surf2:#183039; --line:#21393f; --line2:#2b4950;
  --tx:#e7f0ec; --mut:#82999a; --dim:#5c7377;
  --up:#5de0b2; --up2:rgba(93,224,178,.16); --dn:#ff7070; --dn2:rgba(255,112,112,.16);
  --gold:#e9c46a; --gold2:rgba(233,196,106,.14); --sky:#79b8ff;
  --r:14px; color-scheme:dark;
}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg)}
body{font-family:'Be Vietnam Pro',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;background:
  radial-gradient(900px 480px at 78% -8%,rgba(93,224,178,.07),transparent 60%),
  radial-gradient(700px 420px at -6% 30%,rgba(121,184,255,.05),transparent 60%),var(--bg);
  color:var(--tx);min-height:100vh;font-size:14px;line-height:1.45;font-variant-numeric:tabular-nums;
  padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
button,input,select{font:inherit;color:inherit}
button{cursor:pointer}
:focus-visible{outline:2px solid var(--sky);outline-offset:2px}
.up{color:var(--up)} .dn{color:var(--dn)} .gold{color:var(--gold)} .mut{color:var(--mut)}

/* ── cổng duyệt thiết bị ── */
#gate{position:fixed;inset:0;z-index:50;display:grid;place-items:center;background:var(--bg);padding:24px;text-align:center}
#gate .box{max-width:380px}
#gate h2{font-size:20px;font-weight:700;margin-bottom:8px}
#gate p{color:var(--mut)}
#gate .dot{width:10px;height:10px;border-radius:50%;background:var(--gold);margin:0 auto 18px;animation:pulse 1.4s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(233,196,106,.5)}100%{box-shadow:0 0 0 14px rgba(233,196,106,0)}}

/* ── khung ── */
.app{display:grid;grid-template-columns:272px minmax(0,1fr);min-height:100vh}
.rail{border-right:1px solid var(--line);background:linear-gradient(180deg,var(--bg2),var(--bg));padding:22px 16px;display:flex;flex-direction:column;gap:18px;position:sticky;top:0;height:100vh;overflow:auto}
.brand{display:flex;align-items:baseline;gap:8px;padding:0 6px}
.brand b{font-size:19px;font-weight:800;letter-spacing:-.2px}
.brand span{color:var(--mut);font-size:12px}
.acc-list{display:flex;flex-direction:column;gap:6px}
.acc{display:grid;grid-template-columns:auto 1fr auto;gap:2px 10px;align-items:center;text-align:left;width:100%;padding:11px 12px;border-radius:12px;border:1px solid transparent;background:transparent}
.acc:hover{background:var(--surf)}
.acc.sel{background:var(--surf);border-color:var(--line2)}
.acc .st{grid-row:1/3;width:9px;height:9px;border-radius:50%;background:var(--dim)}
.acc .st.running{background:var(--up);box-shadow:0 0 0 0 rgba(93,224,178,.5);animation:pulse2 1.8s infinite}
.acc .st.paused,.acc .st.hold{background:var(--gold)}
.acc .st.nofund,.acc .st.error,.acc .st.restart{background:var(--dn)}
@keyframes pulse2{0%{box-shadow:0 0 0 0 rgba(93,224,178,.5)}100%{box-shadow:0 0 0 9px rgba(93,224,178,0)}}
.acc .nm{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.acc .pl{font-weight:700;font-size:13px}
.acc .sub{grid-column:2/4;color:var(--mut);font-size:12px}
.btn-add{border:1px dashed var(--line2);background:transparent;border-radius:12px;padding:11px;color:var(--mut);font-weight:600}
.btn-add:hover{color:var(--tx);border-color:var(--mut)}
.rail .foot{margin-top:auto;color:var(--dim);font-size:11.5px;padding:0 6px;display:none}

.main{padding:22px clamp(16px,3vw,36px) 48px;display:flex;flex-direction:column;gap:22px;min-width:0;max-width:1280px;width:100%}

/* ── dải phiên ── */
.feed{display:flex;flex-wrap:wrap;align-items:center;gap:6px 22px;padding:10px 16px;border:1px solid var(--line);border-radius:var(--r);background:var(--bg2)}
.feed .k{color:var(--mut);margin-right:6px}
.feed .pill{display:inline-block;padding:2px 10px;border-radius:99px;font-weight:700;font-size:13px}
.pill.t{background:var(--up2);color:var(--up)} .pill.x{background:var(--dn2);color:var(--dn)} .pill.n{background:var(--surf2);color:var(--mut)}
.dice{display:inline-flex;gap:4px;vertical-align:middle}
.dice i{font-style:normal;display:grid;place-items:center;width:20px;height:20px;border-radius:6px;background:var(--surf2);font-size:12px;font-weight:700}

/* ── hero: lãi/lỗ + biểu đồ ── */
.hero{border:1px solid var(--line);border-radius:18px;background:linear-gradient(180deg,var(--surf),var(--bg2));padding:20px 22px 14px;position:relative;overflow:hidden}
.hero-top{display:flex;flex-wrap:wrap;justify-content:space-between;gap:14px 20px;align-items:flex-start}
.who{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.who h1{font-size:15px;font-weight:600;color:var(--mut)}
.chip{display:inline-flex;align-items:center;gap:7px;padding:3px 11px;border-radius:99px;font-size:12.5px;font-weight:600;background:var(--surf2);color:var(--mut)}
.chip.running{background:var(--up2);color:var(--up)} .chip.paused,.chip.hold{background:var(--gold2);color:var(--gold)}
.chip.nofund,.chip.error,.chip.restart{background:var(--dn2);color:var(--dn)} .chip.target{background:var(--up2);color:var(--up)}
.net{font-size:clamp(38px,6.4vw,64px);font-weight:800;letter-spacing:-1.5px;line-height:1.05;margin-top:6px}
.net small{font-size:.32em;font-weight:600;letter-spacing:0;color:var(--mut);margin-left:8px}
.actions{display:flex;gap:8px;flex-wrap:wrap}
.btn{border:1px solid var(--line2);background:var(--surf2);border-radius:10px;padding:8px 16px;font-weight:600}
.btn:hover{border-color:var(--mut)}
.btn.go{background:var(--up);border-color:var(--up);color:#06231a}
.btn.go:hover{filter:brightness(1.08)}
.btn.warn{color:var(--gold);border-color:rgba(233,196,106,.4)}
.btn.stop{color:var(--dn);border-color:rgba(255,112,112,.4)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.chart-bar{display:flex;justify-content:space-between;align-items:center;margin:14px 0 4px;gap:10px;flex-wrap:wrap}
.seg{display:inline-flex;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:3px}
.seg button{border:0;background:transparent;padding:5px 12px;border-radius:7px;color:var(--mut);font-weight:600;font-size:13px}
.seg button.on{background:var(--surf2);color:var(--tx)}
#chartwrap{position:relative;height:300px}
#chart{width:100%;height:100%;display:block}
#tip{position:absolute;pointer-events:none;background:rgba(10,20,23,.96);border:1px solid var(--line2);border-radius:10px;padding:8px 11px;font-size:12.5px;min-width:150px;display:none;z-index:3}
#tip b{display:block;margin-bottom:2px}
.empty{position:absolute;inset:0;display:grid;place-items:center;text-align:center;color:var(--mut);padding:20px}
.empty[hidden],.app[hidden]{display:none}

/* ── số liệu ── */
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border:1px solid var(--line);border-radius:var(--r);background:var(--bg2)}
.metrics>div{padding:14px 18px;border-right:1px solid var(--line)}
.metrics>div:last-child{border-right:0}
.metrics .l{color:var(--mut);font-size:12.5px}
.metrics .v{font-size:22px;font-weight:700;margin-top:2px}
.metrics .s{color:var(--dim);font-size:12px;margin-top:1px}

/* ── hai cột ── */
.cols{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:22px;align-items:start}
.panel{border:1px solid var(--line);border-radius:var(--r);background:var(--bg2);overflow:hidden}
.panel>h3{font-size:15px;font-weight:700;padding:15px 18px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:10px}
.panel>h3 .saved{font-size:12px;font-weight:500;color:var(--mut)}
.row{display:grid;grid-template-columns:1fr auto;gap:6px 14px;align-items:center;padding:13px 18px;border-bottom:1px solid var(--line)}
.row:last-child{border-bottom:0}
.row .t{font-weight:600}
.row .d{color:var(--mut);font-size:12.5px;grid-column:1}
.row .sub{grid-column:1/3;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;color:var(--mut);font-size:13px;padding-top:2px}
.row .sub[hidden]{display:none}
.sw{position:relative;width:44px;height:26px;flex:none}
.sw input{position:absolute;inset:0;opacity:0;cursor:pointer;margin:0;width:100%;height:100%;z-index:1}
.sw span{position:absolute;inset:0;border-radius:99px;background:var(--surf2);border:1px solid var(--line2);transition:background .18s}
.sw span::after{content:"";position:absolute;top:2px;left:2px;width:20px;height:20px;border-radius:50%;background:var(--mut);transition:transform .18s,background .18s}
.sw input:checked+span{background:var(--up2);border-color:var(--up)}
.sw input:checked+span::after{transform:translateX(18px);background:var(--up)}
.sw input:focus-visible+span{outline:2px solid var(--sky);outline-offset:2px}
.num{width:96px;background:var(--bg);border:1px solid var(--line2);border-radius:9px;padding:6px 9px;text-align:right}
.num.w{width:150px;text-align:left}
.num:focus{border-color:var(--sky);outline:0}
label.ck{display:inline-flex;align-items:center;gap:7px;cursor:pointer}
label.ck input{accent-color:var(--up);width:16px;height:16px}
.mini{border:1px solid var(--line2);background:var(--surf2);border-radius:8px;padding:4px 10px;font-size:12.5px;font-weight:600}
.err{color:var(--dn);padding:10px 18px;font-size:13px;border-top:1px solid var(--line)}
/* thẻ "Dừng khi đạt lãi" (gộp tự rút) */
.goal{margin:12px 14px;border:1px solid var(--line2);border-radius:16px;background:linear-gradient(180deg,var(--surf),var(--bg2));overflow:hidden;transition:border-color .2s,box-shadow .2s}
.goal.open{border-color:var(--up);box-shadow:0 0 0 1px var(--up2),0 8px 24px rgba(0,0,0,.25)}
.goal-h{display:flex;align-items:center;gap:12px;padding:14px 16px}
.goal-h.sm{padding:6px 0}
.goal-ic{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;font-size:19px;background:var(--up2);flex:none}
.goal-t{flex:1;min-width:0}.goal-t .t{font-weight:700}.goal-t .d{color:var(--mut);font-size:12.5px;margin-top:1px}
.goal-b{padding:0 16px 16px;display:flex;flex-direction:column;gap:10px}
.goal-b[hidden],.wd-box[hidden]{display:none}
.gl{font-size:12px;font-weight:600;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
.money{display:flex;align-items:center;background:var(--bg);border:1px solid var(--line2);border-radius:12px;padding:0 14px}
.money:focus-within{border-color:var(--up)}
.money input{flex:1;min-width:0;background:none;border:0;outline:0;font-size:22px;font-weight:800;padding:11px 0;color:var(--tx)}
.money em{font-style:normal;color:var(--mut);font-weight:700;font-size:13px}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip-q{border:1px solid var(--line2);background:var(--surf2);border-radius:99px;padding:5px 13px;font-size:12.5px;font-weight:700;color:var(--tx)}
.chip-q:hover{border-color:var(--up);color:var(--up)}
.goal-sep{height:1px;background:var(--line);margin:4px 0 0}
.wd-box{display:flex;flex-direction:column;gap:10px;padding:14px;border-radius:12px;background:var(--bg);border:1px dashed var(--line2)}
.seg.big{display:flex;margin-top:0}.seg.big button{flex:1;padding:9px 6px;font-size:14px}
.mini.pull{align-self:flex-start}
.wlist{display:flex;flex-direction:column;gap:6px}.wlist:empty{display:none}
.wcard{display:flex;flex-direction:column;align-items:flex-start;gap:1px;text-align:left;border:1px solid var(--line2);background:var(--surf);border-radius:10px;padding:9px 12px;color:var(--tx)}
.wcard small{color:var(--mut)}.wcard.on{border-color:var(--up);background:var(--up2)}
.fi{width:100%;background:var(--surf);border:1px solid var(--line2);border-radius:10px;padding:10px 12px;color:var(--tx)}
.fi:focus{border-color:var(--up);outline:0}
.wd-sum{font-size:13px;line-height:1.5;padding:10px 12px;border-radius:10px;background:var(--up2);color:var(--tx)}
.wd-sum i{color:var(--gold);font-style:normal}
.hint{font-size:12px;color:var(--dim)}

/* ── bảng ván / nhật ký ── */
.tabs{display:flex;border-bottom:1px solid var(--line)}
.tabs button{flex:1;border:0;background:transparent;padding:14px;font-weight:600;color:var(--mut);border-bottom:2px solid transparent}
.tabs button.on{color:var(--tx);border-bottom-color:var(--up)}
.list{max-height:520px;overflow:auto}
.bet{display:grid;grid-template-columns:62px 1fr auto;gap:2px 10px;padding:10px 18px;border-bottom:1px solid var(--line);align-items:center}
.bet .ph{color:var(--mut);font-size:12.5px}
.bet .dt{font-size:13.5px}
.bet .am{font-weight:700;text-align:right}
.bet.open{background:var(--gold2)}
.log{display:grid;grid-template-columns:54px 1fr;gap:10px;padding:9px 18px;border-bottom:1px solid var(--line);font-size:13px}
.log .tm{color:var(--dim);font-size:12px}
.log.warn,.log.error{color:var(--dn)} .log.wd{color:var(--gold)} .log.pause{color:var(--gold)} .log.win{color:var(--up)} .log.loss{color:var(--tx)} .log.virt,.log.info,.log.bet{color:var(--mut)}
.nothing{padding:34px 18px;text-align:center;color:var(--mut)}

/* ── đăng nhập ── */
.login{max-width:520px;margin:6vh auto 0;border:1px solid var(--line);border-radius:18px;background:linear-gradient(180deg,var(--surf),var(--bg2));padding:28px}
.login h2{font-size:24px;font-weight:800;letter-spacing:-.4px;margin-bottom:6px}
.login p.lead{color:var(--mut);margin-bottom:20px}
.fld{display:block;margin-bottom:14px}
.fld span{display:block;color:var(--mut);font-size:12.5px;margin-bottom:5px}
.fld input{width:100%;background:var(--bg);border:1px solid var(--line2);border-radius:10px;padding:11px 13px}
.fld input:focus{border-color:var(--sky);outline:0}
.pwb{position:relative}
.pwb input{padding-right:46px}
.pwb .eye{position:absolute;right:4px;top:50%;transform:translateY(-50%);width:38px;height:38px;border:0;background:none;color:var(--mut);display:grid;place-items:center;border-radius:8px}
.pwb .eye:hover{color:var(--tx)}
.pwb .eye svg{width:20px;height:20px}
.login .btn{width:100%;padding:12px}
.login .msg{margin-top:12px;font-size:13px;min-height:18px}
.note{margin-top:14px;font-size:12px;color:var(--dim)}

.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%);background:var(--surf2);border:1px solid var(--line2);padding:10px 18px;border-radius:12px;z-index:60;display:none;max-width:90vw}

@media (max-width:980px){
  .app{grid-template-columns:1fr}
  .rail{position:static;height:auto;flex-direction:row;align-items:center;overflow-x:auto;border-right:0;border-bottom:1px solid var(--line);padding:12px;gap:8px}
  .brand,.rail .foot{display:none}
  .acc-list{flex-direction:row}
  .acc{width:auto;min-width:170px}
  .btn-add{white-space:nowrap}
  .cols{grid-template-columns:1fr}
  .metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
  .metrics>div:nth-child(2){border-right:0}
  .metrics>div:nth-child(-n+2){border-bottom:1px solid var(--line)}
  #chartwrap{height:240px}
}
@media (max-width:600px){.row>.seg{grid-column:1/3;justify-self:stretch;display:flex}.row>.seg button{flex:1;padding:7px 4px}.main{padding-left:12px;padding-right:12px}.hero{padding:16px 14px 10px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<div id="gate"><div class="box"><div class="dot"></div><h2 id="gt">Đang kiểm tra thiết bị…</h2><p id="gm">Vui lòng chờ.</p></div></div>
<div id="toast" class="toast" role="status"></div>

<div class="app" id="app" hidden>
  <aside class="rail">
    <div class="brand"><b>Auto cược</b><span>LC79 · Tài Xỉu MD5</span></div>
    <div class="acc-list" id="accs"></div>
    <button class="btn-add" id="addbtn">+ Thêm tài khoản</button>
    <div class="foot" id="railfoot"></div>
  </aside>
  <main class="main" id="main"></main>
</div>

<script>
/*__HWID_JS__*/
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>Math.round(n||0).toLocaleString('en-US');
const fmtS=n=>(n>0?'+':'')+fmt(n);
const BASE='/tool/autocuoc/api/';
// ── Per-device account tracking: lưu username của máy này vào localStorage ──
const AB_LS_KEY='ab_accs_'+HWID;
function lsGetAccs(){try{return JSON.parse(localStorage.getItem(AB_LS_KEY)||'[]')}catch(e){return[]}}
function lsAddAcc(u){const a=lsGetAccs();if(!a.includes(u)){a.push(u);try{localStorage.setItem(AB_LS_KEY,JSON.stringify(a))}catch(e){}}}
function lsRemAcc(u){const a=lsGetAccs().filter(x=>x!==u);try{localStorage.setItem(AB_LS_KEY,JSON.stringify(a))}catch(e){}}
// Lọc sessions theo máy: chỉ hiện acc thuộc máy này (hoặc tất cả nếu chưa có data máy)
function filterMyAccs(sessions){const mine=lsGetAccs();if(!mine.length)return sessions;return sessions.filter(s=>mine.includes(s.username))}
const STATUS={expired:'Key hết hạn',running:'Đang cược',paused:'Pause · theo dõi ảo',hold:'Tạm dừng',ready:'Sẵn sàng',stopped:'Đã dừng',target:'Đạt mục tiêu lãi',nofund:'Hết số dư',wd_stop:'Dừng sau khi rút',error:'Lỗi',restart:'Cần đăng nhập lại'};

async function api(p,body){
  const o={headers:Object.assign({'Content-Type':'application/json','X-User-Key':ABKEY},HWID_HDR)};
  if(body!==undefined){o.method='POST';o.body=JSON.stringify(body)}
  const r=await fetch(BASE+p,o);let j={};try{j=await r.json()}catch(e){}
  if((r.status===401&&!j.sai_tk)||(r.status===403&&(j.sai_game||j.can_key))){ABK_BAD(j.loi);return j}   /* key hết hạn / bị xoá / sai game -> về màn nhập key */
  if(!r.ok&&!j.loi)j.loi='Lỗi '+r.status; j._st=r.status; return j;
}
function toast(m){const t=$('#toast');t.textContent=m;t.style.display='block';clearTimeout(toast._t);toast._t=setTimeout(()=>t.style.display='none',3200)}

/* ── vào thẳng giao diện (đã qua màn nhập key; mỗi request api() đều kèm key) ── */
function gate(){$('#app').hidden=false;init()}

/* ── trạng thái ── */
let PREFILL='', S=null, SEL=null, ADDING=false, FORMKEY='', F=null, LOGIN=null, TAB='bets', RANGE=0, MODE='net', saveT=0, saveMsg='';
async function poll(){
  try{
    const j=await api('state'+(SEL?('?id='+SEL):''));
    if(j.ok){S=j; if(!SEL&&j.selected)SEL=j.selected.id; render()}
  }catch(e){}
  setTimeout(poll,2000);
}
function init(){ $('#addbtn').onclick=()=>{ADDING=true;LOGIN=null;PREFILL='';FORMKEY='';render()}; poll(); }

function render(){
  if(!S)return;
  const acc=filterMyAccs(S.sessions);
  if(!acc.length&&!ADDING)ADDING=true;
  $('#accs').innerHTML=acc.map(a=>`<button class="acc ${a.id===SEL&&!ADDING?'sel':''}" data-id="${a.id}">
    <i class="st ${a.status}"></i><span class="nm">${esc(a.nick||a.username)}</span><span class="pl ${a.net>=0?'up':'dn'}">${fmtS(a.net)}</span>
    <span class="sub">${STATUS[a.status]||a.status} · ${fmt(a.balance)}</span></button>`).join('');
  document.querySelectorAll('.acc').forEach(b=>b.onclick=()=>{SEL=b.dataset.id;ADDING=false;FORMKEY='';poll_now()});
  $('#railfoot').innerHTML='<button class="btn-add" id="klo" type="button">Đăng xuất key</button>';$('#klo').onclick=()=>ABK_OUT();
  if(ADDING){renderLogin();return}
  const s=S.selected; if(!s||s.id!==SEL){return}
  renderSession(s);
}
async function poll_now(){const j=await api('state?id='+SEL);if(j.ok){S=j;render()}}

/* ── đăng nhập ── */
const EYE='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>';
const EYE_OFF='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.5 10.5 0 0 1 12 19c-6.4 0-10-7-10-7a18.6 18.6 0 0 1 4.06-5.06M9.9 4.24A9.9 9.9 0 0 1 12 5c6.4 0 10 7 10 7a18.5 18.5 0 0 1-2.16 3.19M14.12 14.12a3 3 0 1 1-4.24-4.24"/><path d="M1 1l22 22"/></svg>';
function renderLogin(){
  const m=$('#main'); const key='login'+(LOGIN?LOGIN.id:'');
  if(FORMKEY===key)return; FORMKEY=key;
  if(!LOGIN){
    m.innerHTML=`<section class="login"><h2>Thêm tài khoản LC79</h2><p class="lead">Đăng nhập để tool lấy số dư thật và đặt cược theo dự đoán của bàn LC MD5.</p>
      <label class="fld"><span>Tên đăng nhập</span><input id="lu" value="${esc(PREFILL)}" autocomplete="username" autocapitalize="none" spellcheck="false"></label>
      <div class="fld"><span>Mật khẩu</span><div class="pwb"><input id="lp" type="password" autocomplete="current-password"><button type="button" class="eye" id="lpe" aria-label="Hiện mật khẩu" title="Hiện / ẩn mật khẩu">${EYE}</button></div></div>
      <button class="btn go" id="lgo">Đăng nhập</button><div class="msg dn" id="lmsg"></div>
      </section>`;
    const go=async()=>{
      const u=$('#lu').value.trim(),p=$('#lp').value; if(!u||!p){$('#lmsg').textContent='Nhập đủ tên đăng nhập và mật khẩu';return}
      $('#lgo').disabled=true;$('#lgo').textContent='Đang đăng nhập…';$('#lmsg').textContent='';
      const j=await api('login',{username:u,password:p});
      if(!j.ok){$('#lgo').disabled=false;$('#lgo').textContent='Đăng nhập';$('#lmsg').textContent=j.loi||'Đăng nhập thất bại';const pe=$('#lp');if(pe){pe.focus();pe.select()}return}
      lsAddAcc(u); LOGIN=j;SEL=j.id;FORMKEY='';F=null;render();
    };
    $('#lgo').onclick=go; $('#lp').onkeydown=e=>{if(e.key==='Enter')go()};
    $('#lpe').onclick=()=>{const i=$('#lp'),sh=i.type==='password';i.type=sh?'text':'password';$('#lpe').innerHTML=sh?EYE_OFF:EYE;$('#lpe').setAttribute('aria-label',sh?'Ẩn mật khẩu':'Hiện mật khẩu');i.focus()};
    setTimeout(()=>{const e=PREFILL?$('#lp'):$('#lu');e&&e.focus()},50);
    return;
  }
  /* đã đăng nhập: chọn cấu hình rồi bắt đầu */
  F=Object.assign({},LOGIN.cfg||{});
  m.innerHTML=`<section class="login" style="max-width:720px;padding:0;overflow:hidden">
    <div style="padding:22px 24px;border-bottom:1px solid var(--line)"><h2 style="margin-bottom:2px">${esc(LOGIN.nick)}</h2>
    <p class="mut">Số dư thật: <b class="gold">${fmt(LOGIN.balance)}</b> — chọn cách cược rồi bấm Bắt đầu. Đổi được cả khi đang chạy.</p></div>
    <div id="cfgbox"></div>
    <div style="padding:18px 24px;display:flex;gap:10px;flex-wrap:wrap;border-top:1px solid var(--line)">
      <button class="btn go" id="sgo" style="width:auto;flex:1">Bắt đầu auto cược</button>
      ${LOGIN.co_lich_su?'<button class="btn" id="scont" style="width:auto">Tiếp tục lịch sử cũ</button>':''}
    </div><div class="msg dn" id="smsg" style="padding:0 24px 16px"></div></section>`;
  buildCfg($('#cfgbox'),false);
  const start=async reset=>{
    $('#smsg').textContent='';
    const j=await api('start',{id:LOGIN.id,cfg:F,reset});
    if(!j.ok){$('#smsg').textContent=j.loi||'Không bắt đầu được';return}
    ADDING=false;LOGIN=null;FORMKEY='';await poll_now();
  };
  $('#sgo').onclick=()=>start(true);
  if($('#scont'))$('#scont').onclick=()=>start(false);
}

/* ── bảng cấu hình (dùng cho cả lúc bắt đầu và lúc đang chạy) ── */
function buildCfg(box,live){
  const c=F, lim=S.wd_limits;
  const segBtn=(k,v,t)=>`<button data-k="${k}" data-v="${v}" class="${c[k]===v?'on':''}">${t}</button>`;
  box.innerHTML=`
  <div class="row"><div><div class="t">Cược gốc mỗi ván</div><div class="d">Mức cược khi không có luật nào đang áp dụng</div></div><input class="num" id="f_bet" inputmode="numeric" value="${c.bet}"></div>
  <div class="row"><div><div class="t">Khi thua</div><div class="d">Giữ nguyên · về gốc · nhân đôi (Martingale)</div></div>
    <div class="seg">${segBtn('loss_mode','keep','Giữ nguyên')}${segBtn('loss_mode','reset','Về gốc')}${segBtn('loss_mode','x2','Nhân đôi')}</div></div>
  <div class="row"><div><div class="t">x2 sau chuỗi thua</div><div class="d">Thua đủ N ván liên tiếp thì nhân đôi một lần; thắng lại về cược gốc</div></div>
    <label class="sw"><input type="checkbox" id="f_loss_x2_on" ${c.loss_x2_on?'checked':''}><span></span></label>
    <div class="sub" id="s_loss_x2" ${c.loss_x2_on?'':'hidden'}>Sau <input class="num" style="width:64px" id="f_loss_x2_streak" inputmode="numeric" value="${c.loss_x2_streak}"> ván thua liên tiếp</div></div>
  <div class="row"><div><div class="t">Khi thắng</div><div class="d">Giữ nguyên · về gốc · nhân đôi sau chuỗi thắng</div></div>
    <div class="seg">${segBtn('win_mode','keep','Giữ nguyên')}${segBtn('win_mode','reset','Về gốc')}${segBtn('win_mode','x2','Nhân đôi')}</div>
    <div class="sub" id="s_win_x2" ${c.win_mode==='x2'?'':'hidden'}>Nhân đôi sau <input class="num" style="width:64px" id="f_win_x2_streak" inputmode="numeric" value="${c.win_x2_streak}"> ván thắng liên tiếp
      <label class="ck"><input type="checkbox" id="f_win_x2_keep" ${c.win_x2_keep?'checked':''}> giữ x2 tới khi thua</label></div></div>
  <div class="row"><div><div class="t">Giảm cược khi thua liên tiếp</div><div class="d">Thua đủ N ván thì hạ xuống mức thấp hơn, thắng lại về gốc</div></div>
    <label class="sw"><input type="checkbox" id="f_reduce_on" ${c.reduce_on?'checked':''}><span></span></label>
    <div class="sub" id="s_reduce" ${c.reduce_on?'':'hidden'}>Sau <input class="num" style="width:64px" id="f_reduce_streak" inputmode="numeric" value="${c.reduce_streak}"> ván thua → cược <input class="num" id="f_reduce_bet" inputmode="numeric" value="${c.reduce_bet||''}" placeholder="mức giảm"></div></div>
  <div class="row"><div><div class="t">Pause khi thua dài</div><div class="d">Ngừng cược nhưng vẫn theo dõi ảo, đủ chuỗi thắng thì cược lại</div></div>
    <label class="sw"><input type="checkbox" id="f_pause_on" ${c.pause_on?'checked':''}><span></span></label>
    <div class="sub" id="s_pause" ${c.pause_on?'':'hidden'}>Pause sau <input class="num" style="width:64px" id="f_pause_streak" inputmode="numeric" value="${c.pause_streak}"> ván thua · cược lại khi thắng <input class="num" style="width:64px" id="f_resume_wins" inputmode="numeric" value="${c.resume_wins}"> ván liên tiếp</div></div>
  <div class="goal ${c.target_on?'open':''}" id="goalcard">
    <div class="goal-h"><div class="goal-ic">🎯</div>
      <div class="goal-t"><div class="t">Dừng khi đạt lãi</div><div class="d">Lãi chạm mục tiêu → dừng toàn bộ cược</div></div>
      <label class="sw"><input type="checkbox" id="f_target_on" ${c.target_on?'checked':''}><span></span></label></div>
    <div class="goal-b" id="s_target" ${c.target_on?'':'hidden'}>
      <div class="gl">Mục tiêu lãi</div>
      <div class="money"><input id="f_target" inputmode="numeric" value="${c.target||''}" placeholder="vd 200000"><em>VNĐ</em></div>
      <div class="chips">${[100000,200000,500000,1000000].map(v=>`<button type="button" class="chip-q" data-v="${v}">+${v>=1e6?(v/1e6)+'tr':(v/1e3)+'k'}</button>`).join('')}</div>
      <div class="goal-sep"></div>
      <div class="goal-h sm"><div class="goal-t"><div class="t">Tự động rút khi đạt lãi</div><div class="d">Dừng cược xong gửi lệnh rút đúng bằng mức mục tiêu</div></div>
        <label class="sw"><input type="checkbox" id="f_target_wd" ${c.target_wd?'checked':''}><span></span></label></div>
      <div class="wd-box" id="s_wd" ${c.target_wd?'':'hidden'}>
        <div class="gl">Rút về</div>
        <div class="seg big">${segBtn('wd_kind','momo','📱 Momo')}${segBtn('wd_kind','bank','🏦 Ngân hàng')}</div>
        <button type="button" class="mini pull" id="wd_pull">⬇ Lấy tài khoản đã liên kết từ LC79</button>
        <div id="wd_list" class="wlist"></div>
        <input class="fi" id="f_wd_number" placeholder="${c.wd_kind==='bank'?'Số tài khoản':'SĐT Momo'}" value="${esc(c.wd_number)}" inputmode="numeric">
        <input class="fi" id="f_wd_name" placeholder="Tên chủ tài khoản (tuỳ chọn)" value="${esc(c.wd_name)}">
        <div class="wd-sum" id="wd_sum"></div>
        <div class="hint">Tool gửi đúng số tiền bằng mục tiêu lãi, không làm tròn hay chia nhỏ — hạn mức do LC79 quyết định.</div>
      </div>
    </div>
  </div>`;
  const dirty=()=>{ if(live)scheduleSave() };
  const sum=()=>{const e=$('#wd_sum');if(!e)return;
    const to=F.wd_number?((F.wd_kind==='bank'?(F.wd_code&&F.wd_code!=='MOMO'?F.wd_code.toUpperCase()+' ':'Ngân hàng '):'Momo ')+esc(F.wd_number)):'<i>chưa chọn nơi nhận</i>';
    e.innerHTML='Khi lãi ≥ <b>'+(+F.target?fmt(+F.target):'…')+'</b> → dừng cược, gửi lệnh rút <b>'+(+F.target?fmt(+F.target):'…')+'</b> về <b>'+to+'</b>'};
  const num=(id,k)=>{const e=$('#'+id);if(e)e.oninput=()=>{F[k]=e.value.trim();sum();dirty()}};
  [['f_bet','bet'],['f_loss_x2_streak','loss_x2_streak'],['f_win_x2_streak','win_x2_streak'],['f_reduce_streak','reduce_streak'],['f_reduce_bet','reduce_bet'],
   ['f_pause_streak','pause_streak'],['f_resume_wins','resume_wins'],['f_target','target'],['f_wd_number','wd_number'],['f_wd_name','wd_name']].forEach(a=>num(a[0],a[1]));
  const tg=(id,k,sub,after)=>{const e=$('#'+id);if(e)e.onchange=()=>{F[k]=e.checked;if(sub)$('#'+sub).hidden=!e.checked;if(after)after(e.checked);sum();dirty()}};
  tg('f_loss_x2_on','loss_x2_on','s_loss_x2');tg('f_reduce_on','reduce_on','s_reduce');tg('f_pause_on','pause_on','s_pause');
  tg('f_target_on','target_on','s_target',on=>$('#goalcard').classList.toggle('open',on));tg('f_target_wd','target_wd','s_wd');tg('f_win_x2_keep','win_x2_keep');
  box.querySelectorAll('.chip-q').forEach(b=>b.onclick=()=>{const e=$('#f_target');F.target=String((+F.target||0)+(+b.dataset.v));e.value=F.target;sum();dirty()});
  box.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{
    const k=b.dataset.k;F[k]=b.dataset.v;
    b.parentNode.querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));
    if(k==='win_mode')$('#s_win_x2').hidden=F[k]!=='x2';
    if(k==='wd_kind'){$('#f_wd_number').placeholder=F[k]==='bank'?'Số tài khoản':'SĐT Momo';$('#wd_list').innerHTML='';if(F[k]==='momo')F.wd_code='MOMO';sum()}
    dirty();
  });
  $('#wd_pull').onclick=async()=>{
    const id=live?SEL:(LOGIN&&LOGIN.id); const l=$('#wd_list'); l.innerHTML='<span class="mut">Đang lấy…</span>';
    const j=await api('wallets',{id,kind:F.wd_kind});
    if(!j.ok||!j.wallets.length){l.innerHTML='<span class="mut">LC79 chưa liên kết '+(F.wd_kind==='bank'?'tài khoản ngân hàng':'ví Momo')+' nào — nhập tay bên dưới.</span>';return}
    l.innerHTML=j.wallets.map((w,i)=>`<button type="button" class="wcard ${w.number===F.wd_number?'on':''}" data-i="${i}"><b>${esc((w.code||F.wd_kind).toUpperCase())} · ${esc(w.number)}</b><small>${esc(w.name||'')}</small></button>`).join('');
    l.querySelectorAll('button').forEach(b=>b.onclick=()=>{const w=j.wallets[+b.dataset.i];
      F.wd_number=w.number;F.wd_name=w.name;if(F.wd_kind==='bank')F.wd_code=w.code;
      $('#f_wd_number').value=w.number;$('#f_wd_name').value=w.name;
      l.querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));sum();dirty()});
  };
  sum();
}
function scheduleSave(){
  clearTimeout(saveT);saveMsg='Đang lưu…';paintSaved();
  saveT=setTimeout(async()=>{
    const j=await api('config',{id:SEL,cfg:F});
    const e=$('#cfgerr');
    if(j.ok){saveMsg='Đã lưu';if(e){e.textContent='';e.style.display='none'}}
    else{saveMsg='Chưa lưu';if(e){e.textContent=j.loi||'Cấu hình chưa hợp lệ';e.style.display='block'}}
    paintSaved();
  },600);
}
function paintSaved(){const e=$('#saved');if(e)e.textContent=saveMsg}

/* ── màn hình 1 tài khoản ── */
function dice(a){return a?`<span class="dice">${a.map(x=>`<i>${x}</i>`).join('')}</span>`:''}
function sidePill(d){return d==='TÀI'||d==='TAI'?'<span class="pill t">TÀI</span>':d==='XỈU'||d==='XIU'?'<span class="pill x">XỈU</span>':'<span class="pill n">—</span>'}
function renderSession(s){
  const m=$('#main'); const key=s.id+'|'+(s.alive?1:0);
  if(FORMKEY!==key){
    FORMKEY=key; F=Object.assign({},s.cfg); saveMsg='';
    m.innerHTML=`
    <div class="feed" id="feed"></div>
    <section class="hero">
      <div class="hero-top"><div><div class="who"><h1 id="h_nick"></h1><span class="chip" id="h_chip"></span></div>
        <div class="net" id="h_net"></div></div><div class="actions" id="h_act"></div></div>
      <div class="chart-bar"><div class="seg" id="modeseg"><button data-m="net" class="on">Lãi / Lỗ</button><button data-m="bal">Số dư</button></div>
        <div class="seg" id="rangeseg"><button data-r="50">50 ván</button><button data-r="200">200 ván</button><button data-r="0" class="on">Tất cả</button></div></div>
      <div id="chartwrap"><canvas id="chart"></canvas><div id="tip"></div><div class="empty" id="chartempty" hidden>Chưa có ván nào có kết quả.<br>Biểu đồ chạy ngay khi ván đầu tiên được chấm.</div></div>
    </section>
    <div class="metrics" id="metrics"></div>
    <div class="cols">
      <section class="panel"><h3>Tính năng <span class="saved" id="saved"></span></h3><div id="cfgbox"></div><div class="err" id="cfgerr" style="display:none"></div></section>
      <section class="panel"><div class="tabs"><button data-t="bets" class="on">Ván cược</button><button data-t="logs">Nhật ký</button></div><div class="list" id="list"></div></section>
    </div>`;
    buildCfg($('#cfgbox'),true);
    $('#modeseg').querySelectorAll('button').forEach(b=>b.onclick=()=>{MODE=b.dataset.m;$('#modeseg').querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));drawChart()});
    $('#rangeseg').querySelectorAll('button').forEach(b=>b.onclick=()=>{RANGE=+b.dataset.r;$('#rangeseg').querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));drawChart()});
    document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{TAB=b.dataset.t;document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));paintList()});
    document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.t===TAB));
    $('#modeseg').querySelectorAll('button').forEach(x=>x.classList.toggle('on',x.dataset.m===MODE));
    $('#rangeseg').querySelectorAll('button').forEach(x=>x.classList.toggle('on',+x.dataset.r===RANGE));
    bindChart();
  }
  const f=S.feed;
  $('#feed').innerHTML=f.ok?`<span><span class="k">${esc(f.ban||'LC MD5')}</span>Phiên ${f.phien?('#'+f.phien):'—'} ${sidePill(f.du_doan)}</span>
    <span class="mut">Trước: ${f.phien_truoc?('#'+f.phien_truoc):'—'} ${sidePill(f.ket_qua_truoc)} ${dice(f.xuc_xac)}</span>`
    :`<span class="dn">Nguồn dự đoán đang lỗi: ${esc(f.loi||'chưa có dữ liệu')} — auto cược sẽ không đặt ván mới.</span>`;
  $('#h_nick').textContent=s.nick||s.username;
  const chip=$('#h_chip');chip.className='chip '+s.status;chip.textContent=STATUS[s.status]||s.status;
  const n=$('#h_net');n.className='net '+(s.net>=0?'up':'dn');n.innerHTML=fmtS(s.net)+'<small>lãi / lỗ</small>';
  const act=$('#h_act');
  let ah='';
  if(s.alive){ah=(s.hold?'<button class="btn go" data-a="unhold">Tiếp tục cược</button>':'<button class="btn warn" data-a="hold">Tạm dừng</button>')+'<button class="btn stop" data-a="stop">Dừng hẳn</button>'}
  else{ah='<button class="btn go" data-a="restart">Chạy lại</button><button class="btn" data-a="remove">Xoá</button>'}
  if(act.dataset.h!==ah){act.dataset.h=ah;act.innerHTML=ah;act.querySelectorAll('button').forEach(b=>b.onclick=()=>doAct(b.dataset.a))}
  const open=s.open;
  $('#metrics').innerHTML=`
   <div><div class="l">Số dư</div><div class="v gold">${fmt(s.balance)}</div><div class="s">vốn ${fmt(s.start_bal)}</div></div>
   <div><div class="l">Cược ván kế</div><div class="v">${fmt(s.bet)}</div><div class="s">${s.x2_active?'đang x2':s.reduced?'đang giảm':'gốc '+fmt(s.base_bet)}${s.paused?' · pause':''}</div></div>
   <div><div class="l">Thắng / Thua</div><div class="v"><span class="up">${s.w}</span> / <span class="dn">${s.l}</span></div><div class="s">${s.wr==null?'chưa có ván':s.wr+'% thắng'} · chuỗi ${s.win_streak?('thắng '+s.win_streak):s.loss_streak?('thua '+s.loss_streak):'—'}</div></div>
   <div><div class="l">Đã rút</div><div class="v">${fmt(s.withdrawn)}</div><div class="s">${s.wd_count} lần · ${s.cfg.wd_on?'auto rút BẬT':'auto rút tắt'}</div></div>`;
  window.__series=s.series||[];window.__logs=s.logs||[];window.__open=open;
  drawChart();paintList();paintSaved();
}
async function doAct(a){
  if(a==='restart'){const s=S.selected;ADDING=true;FORMKEY='';
    if(s&&s.has_pw){LOGIN={id:s.id,nick:s.nick||s.username,balance:s.balance,co_lich_su:s.rounds>0,cfg:s.cfg};PREFILL=''}
    else{LOGIN=null;PREFILL=s?s.username:''}
    render();return}
  if(a==='remove'&&!confirm('Xoá tài khoản này khỏi danh sách (mất lịch sử)?'))return;
  if(a==='stop'&&!confirm('Dừng hẳn auto cược?'))return;
  const j=await api('action',{id:SEL,act:a});
  if(!j.ok)toast(j.loi||'Không thực hiện được');
  if(a==='remove'){SEL=null;FORMKEY=''}
  await poll_now();
}
function paintList(){
  const L=$('#list');if(!L)return;
  const s=window.__series||[],lg=window.__logs||[],o=window.__open;
  const tm=t=>new Date(t*1000).toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  if(TAB==='bets'){
    let h='';
    if(o)h+=`<div class="bet open"><span class="ph">#${o.phien}</span><span class="dt">${o.virtual?'Theo dõi ảo':'Đang chờ kết quả'} · ${o.side==='TAI'?'Tài':'Xỉu'}</span><span class="am gold">${o.amount?fmt(o.amount):'—'}</span></div>`;
    h+=s.slice(-60).reverse().map(p=>`<div class="bet"><span class="ph">#${p.phien}</span><span class="dt">${p.side==='TAI'?'Tài':'Xỉu'} ${fmt(p.amount)} → ${p.res==='TAI'?'Tài':'Xỉu'} ${p.win?'✅':'❌'}</span><span class="am ${p.pnl>=0?'up':'dn'}">${fmtS(p.pnl)}</span></div>`).join('');
    L.innerHTML=h||'<div class="nothing">Chưa có ván nào. Ván đầu tiên sẽ hiện ở đây.</div>';
  }else{
    L.innerHTML=lg.slice().reverse().map(e=>`<div class="log ${e.kind}"><span class="tm">${tm(e.t)}</span><span>${esc(e.msg)}</span></div>`).join('')||'<div class="nothing">Chưa có sự kiện nào.</div>';
  }
}

/* ── biểu đồ lãi / lỗ (canvas, không dùng thư viện) ── */
let HOVER=-1, PTS=[];
function bindChart(){
  const cv=$('#chart');
  cv.onmousemove=e=>{const r=cv.getBoundingClientRect();hover(e.clientX-r.left)};
  cv.ontouchmove=e=>{const r=cv.getBoundingClientRect();hover(e.touches[0].clientX-r.left)};
  cv.onmouseleave=()=>{HOVER=-1;$('#tip').style.display='none';drawChart()};
  if(window.ResizeObserver)new ResizeObserver(()=>drawChart()).observe($('#chartwrap'));
}
function hover(x){
  if(!PTS.length)return; let best=0,bd=1e9;
  PTS.forEach((p,i)=>{const d=Math.abs(p.x-x);if(d<bd){bd=d;best=i}});
  HOVER=best;drawChart();
  const p=PTS[best],t=$('#tip');
  if(p.d.r===0){t.style.display='none';return}
  t.innerHTML=`<b>Ván ${p.d.r} · #${p.d.phien}</b>${p.d.side==='TAI'?'Tài':'Xỉu'} ${fmt(p.d.amount)} → ${p.d.res==='TAI'?'Tài':'Xỉu'} ${p.d.win?'✅':'❌'}<br>Ván này <span class="${p.d.pnl>=0?'up':'dn'}">${fmtS(p.d.pnl)}</span><br>Lãi/lỗ <span class="${p.d.net>=0?'up':'dn'}">${fmtS(p.d.net)}</span> · Dư ${fmt(p.d.bal)}`;
  t.style.display='block';const w=$('#chartwrap').clientWidth;t.style.left=Math.min(Math.max(p.x-75,4),w-160)+'px';t.style.top='6px';
}
function drawChart(){
  const cv=$('#chart');if(!cv)return;const wrap=$('#chartwrap');
  const W=wrap.clientWidth,H=wrap.clientHeight,dpr=window.devicePixelRatio||1;
  cv.width=W*dpr;cv.height=H*dpr;const g=cv.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,W,H);
  let ser=(window.__series||[]).slice();
  const emp=$('#chartempty');if(emp)emp.hidden=ser.length>0;
  const s=S&&S.selected; if(!s){return}
  const base=MODE==='net'?0:s.start_bal;
  let pts=[{r:0,v:base}].concat(ser.map(p=>Object.assign({v:MODE==='net'?p.net:p.bal},p)));
  if(RANGE>0&&pts.length>RANGE+1)pts=pts.slice(-(RANGE+1));
  const vals=pts.map(p=>p.v).concat([base]);
  let lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals); if(lo===hi){lo-=1;hi+=1}
  const pad=(hi-lo)*.1;lo-=pad;hi+=pad;
  const step=niceStep((hi-lo)/4);lo=Math.floor(lo/step)*step;hi=Math.ceil(hi/step)*step;
  const L=8,R=64,T=14,B=22,cw=W-L-R,ch=H-T-B;
  const X=i=>L+(pts.length<2?cw/2:i*cw/(pts.length-1)), Y=v=>T+(hi-v)/(hi-lo)*ch;
  g.font='11.5px "Be Vietnam Pro",system-ui,sans-serif';g.textBaseline='middle';
  /* lưới + trục giá trị */
  g.strokeStyle='rgba(130,153,154,.14)';g.fillStyle='#5c7377';g.lineWidth=1;
  for(let v=lo;v<=hi+step/2;v+=step){const y=Y(v);g.beginPath();g.moveTo(L,y);g.lineTo(W-R,y);g.stroke();g.textAlign='left';g.fillText((v>0&&MODE==='net'?'+':'')+shortN(v),W-R+8,y)}
  const zy=Y(base);g.save();g.setLineDash([4,4]);g.strokeStyle='rgba(231,240,236,.35)';g.beginPath();g.moveTo(L,zy);g.lineTo(W-R,zy);g.stroke();g.restore();
  g.textAlign='center';g.fillStyle='#5c7377';g.textBaseline='alphabetic';
  g.fillText(pts.length>1?('ván '+pts[1].r):'',L+14,H-6);g.fillText(pts.length>1?('ván '+pts[pts.length-1].r):'',W-R-16,H-6);
  PTS=pts.map((p,i)=>({x:X(i),y:Y(p.v),d:p}));
  if(pts.length<2)return;
  const path=()=>{g.beginPath();PTS.forEach((p,i)=>i?g.lineTo(p.x,p.y):g.moveTo(p.x,p.y))};
  const area=(clipTop,col0,col1,line)=>{
    g.save();g.beginPath();if(clipTop)g.rect(0,0,W,zy);else g.rect(0,zy,W,H-zy);g.clip();
    const gr=g.createLinearGradient(0,clipTop?T:zy,0,clipTop?zy:T+ch);gr.addColorStop(0,col0);gr.addColorStop(1,col1);
    path();g.lineTo(PTS[PTS.length-1].x,zy);g.lineTo(PTS[0].x,zy);g.closePath();g.fillStyle=gr;g.fill();
    path();g.strokeStyle=line;g.lineWidth=2.2;g.lineJoin='round';g.stroke();g.restore()};
  area(true,'rgba(93,224,178,.34)','rgba(93,224,178,0)','#5de0b2');
  area(false,'rgba(255,112,112,0)','rgba(255,112,112,.34)','#ff7070');
  /* mốc rút tiền */
  const r0=pts[1]?pts[1].r:0;
  (window.__logs||[]).filter(e=>e.kind==='wd'&&e.ok===true).forEach(e=>{
    const idx=pts.findIndex(p=>p.r>=e.r&&p.r>0);const i=idx<0?pts.length-1:idx; if(e.r<r0&&RANGE>0)return;
    const p=PTS[i];g.save();g.translate(p.x,p.y);g.rotate(Math.PI/4);g.fillStyle='#e9c46a';g.fillRect(-4.5,-4.5,9,9);g.restore()});
  /* điểm cuối + con trỏ */
  const last=PTS[PTS.length-1];g.beginPath();g.arc(last.x,last.y,4.5,0,7);g.fillStyle=pts[pts.length-1].v>=base?'#5de0b2':'#ff7070';g.fill();
  if(HOVER>=0&&PTS[HOVER]){const p=PTS[HOVER];g.strokeStyle='rgba(231,240,236,.4)';g.lineWidth=1;g.beginPath();g.moveTo(p.x,T);g.lineTo(p.x,T+ch);g.stroke();
    g.beginPath();g.arc(p.x,p.y,5,0,7);g.fillStyle='#e7f0ec';g.fill()}
}
function niceStep(r){const e=Math.pow(10,Math.floor(Math.log10(r)));const f=r/e;return (f<=1.5?1:f<=3?2:f<=7?5:10)*e}
function shortN(v){const a=Math.abs(v);if(a>=1e6)return (v/1e6).toFixed(a>=1e7?0:1)+'M';if(a>=1e3)return (v/1e3).toFixed(a>=1e4?0:1)+'k';return Math.round(v)}
gate();
</script>
</body>
</html>
"""


AB_SHELL = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Auto cược LC79</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#0a1417;color:#e7f0ec;font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
#kg{min-height:100vh;display:grid;place-items:center;padding:24px}
.kbox{width:100%;max-width:380px;background:#12242a;border:1px solid #21393f;border-radius:18px;padding:30px 26px;text-align:center}
.kbox h2{margin:0 0 6px;font-size:20px}.kbox p{margin:0 0 18px;color:#82999a;font-size:14px}
.kbox input{width:100%;height:46px;padding:0 14px;border-radius:12px;border:1px solid #2b4950;background:#0a1417;color:#e7f0ec;font:inherit;font-size:16px;margin-bottom:12px}
.kbox input:focus{outline:0;border-color:#e9c46a}
.kbox button{width:100%;height:46px;border:0;border-radius:12px;background:#e9c46a;color:#1a1405;font:inherit;font-weight:700;font-size:15px;cursor:pointer}
.kbox button:disabled{opacity:.6;cursor:wait}#kmsg{margin:12px 0 0!important;color:#ff7070!important;min-height:20px}
</style></head><body>
<div id="kg"><div class="kbox">
  <h2>🎲 Auto cược LC79</h2>
  <p>Nhập key Auto cược LC để mở công cụ</p>
  <input id="kin" type="password" placeholder="Nhập key auto cược LC" autocomplete="off" autocapitalize="characters" spellcheck="false">
  <button id="kgo" type="button">Vào</button>
  <p id="kmsg"></p>
</div></div>
<script>
/*__HWID_JS__*/
const ABK_LS='ablc_key';
let ABKEY='';
function ABK_BAD(m){try{localStorage.removeItem(ABK_LS)}catch(e){}try{sessionStorage.setItem('ablc_msg',m||'Key không hợp lệ hoặc đã hết hạn')}catch(e){}location.reload()}
function ABK_OUT(){try{localStorage.removeItem(ABK_LS)}catch(e){}location.reload()}
async function _kunlock(key){
  const r=await fetch('/tool/autocuoc/ui',{cache:'no-store',headers:Object.assign({'X-User-Key':key},HWID_HDR)});
  if(r.status===404){document.body.innerHTML='';return{fatal:true}}
  let j={};try{j=await r.json()}catch(e){}
  if(!r.ok||!j.ok)return{ok:false,loi:j.loi||('Lỗi '+r.status)};
  return{ok:true,ui:j};
}
function _kmount(ui,key){
  ABKEY=key;
  try{localStorage.setItem(ABK_LS,key)}catch(e){}
  const st=document.createElement('style');st.textContent=ui.css;document.head.appendChild(st);
  document.getElementById('kg').remove();
  document.body.insertAdjacentHTML('beforeend',ui.body);
  const sc=document.createElement('script');sc.textContent=ui.js;document.body.appendChild(sc);
}
async function _kgo(key,silent){
  const m=document.getElementById('kmsg'),b=document.getElementById('kgo');
  key=String(key||'').trim();
  if(!key){m.textContent='Nhập key để vào';return}
  b.disabled=true;b.textContent='Đang kiểm tra…';m.textContent='';
  try{
    const o=await _kunlock(key);
    if(o.fatal)return;
    if(o.ok){_kmount(o.ui,key);return}
    if(silent){try{localStorage.removeItem(ABK_LS)}catch(e){}}
    m.textContent=o.loi;
  }catch(e){m.textContent='Không kết nối được server…'}
  b.disabled=false;b.textContent='Vào';
}
document.getElementById('kgo').onclick=()=>_kgo(document.getElementById('kin').value,false);
document.getElementById('kin').onkeydown=e=>{if(e.key==='Enter')_kgo(e.target.value,false)};
(function(){
  let msg='',saved='';
  try{msg=sessionStorage.getItem('ablc_msg')||'';sessionStorage.removeItem('ablc_msg')}catch(e){}
  try{saved=localStorage.getItem(ABK_LS)||''}catch(e){}
  if(msg)document.getElementById('kmsg').textContent=msg;
  if(saved&&!msg){document.getElementById('kin').value=saved;_kgo(saved,true)}
})();
</script></body></html>"""


def _ab_split_ui():
    """Tách AB_HTML thành css / body / js — gửi qua /tool/autocuoc/ui SAU KHI key đúng (trang /tool/autocuoc không chứa giao diện)."""
    h = AB_HTML
    css = re.search(r"<style>(.*?)</style>", h, re.S).group(1)
    i = h.index("<body>") + len("<body>")
    j = h.index("<script>", i)
    body = re.sub(r'<div id="gate">.*?</p></div></div>', "", h[i:j], count=1, flags=re.S)
    js = h[j + len("<script>"):h.rindex("</script>")].replace("/*__HWID_JS__*/", "")
    return {"css": css, "body": body, "js": js}


AB_UI = _ab_split_ui()


@app.route("/")
def index():
    return _json({"ok": True, "api": "SUNVIW"})          # cố ý KHÔNG liệt kê endpoint (/api/html, /api/admin ...)


def _sec_report():
    w = []
    if not os.environ.get("SUNVIW_MAIN_PASS"):
        w.append("SUNVIW_MAIN_PASS CHUA DAT -> dang dung mat khau TAM ngau nhien (xem dong [SEC] o tren). Dat SUNVIW_MAIN_PASS (>= 16 ky tu)")
    elif len(os.environ.get("SUNVIW_MAIN_PASS", "")) < 16:
        w.append("SUNVIW_MAIN_PASS qua ngan (< 16 ky tu)")
    if AB_SAVE_PW and not _ab_fernet():
        w.append("AUTOBET_SAVE_PW=1 nhung thieu SUNVIW_SECRET (>= 24 ky tu) hoac thu vien cryptography -> mat khau LC79 se KHONG duoc luu xuong dia")
    if not (os.environ.get("LC_MD5_API_URL") or os.environ.get("TELE68_API_URL")) or not os.environ.get("LC_HU_API_URL"):
        w.append("LC_MD5_API_URL / LC_HU_API_URL chua dat -> URL (kem token at=) dang nam trong code")
    if not os.environ.get("AUTOBET_AT_TOKENS"):
        w.append("AUTOBET_AT_TOKENS chua dat -> token at dang nam trong code")
    if IP_TRUST_PROXY and not IP_HEADER:
        w.append(f"IP client lay tu X-Forwarded-For, phan tu thu {IP_PROXY_HOPS} tinh tu cuoi (SUNVIW_PROXY_HOPS). Neu nhieu nguoi bi tinh CHUNG 1 IP (khoa nham) thi tang SUNVIW_PROXY_HOPS hoac dat SUNVIW_IP_HEADER")
    if not DEV_TOKEN_STRICT:
        w.append("SUNVIW_DEV_TOKEN_STRICT=0: thiet bi panel da duyet tu truoc se tu gan token o lan mo panel dau tien. Sau khi moi may da mo panel 1 lan, dat =1")
    for x in w:
        print("[SEC] " + x, file=sys.stderr)


_sec_report()

# Chạy dưới gunicorn (Railway) thì main() không được gọi -> bật poller ngay khi import.
if __name__ != "__main__":
    ensure_poller()


def main():
    global UPSTREAM_URL, POLL_SEC, FLIP_FINAL, WR_FLIP_WEIGHT, HIT_ENABLED
    global AF_ENABLED, AF_FLIP_LOW, AF_FLIP_HIGH, AF_MIN_GAMES, AF_MODE_WINDOW, AF_MODE_BELOW, AF_FLIP_FINAL, AF_FLIP_FINAL_CT, AF_FLIP_FINAL_CAO, AF_FLIP_FINAL_THAP, AF_FLIP_FINAL_ALL, AF_MODE_FLIP
    global AF_FLIP_BAND, AF_FLIP_LOW_MIN, AF_FLIP_LOW_MAX, AF_FLIP_HIGH_MIN, AF_FLIP_HIGH_MAX
    global AF_GROUP_FLIPPED_ONLY, AF_GROUP_NEED_MAJORITY, AF_SWITCH, AF_SWITCH_NEED, AF_SWITCH_LEAD, AF_SWITCH_PRIO
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="SUNVIW - API JSON (SUN + HITCLUB: 13 logic chuoi/xuc xac/tong/so phien · key theo game)")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
    ap.add_argument("--upstream", default=UPSTREAM_URL, help="URL API phien moi nhat (…/api/tx)")
    ap.add_argument("--poll", type=float, default=POLL_SEC, help="chu ky quet upstream (giay)")
    ap.add_argument("--no-hit", action="store_true", help="TAT ca 2 ban HITCLUB (tx thuong + tx md5)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--flip", action="store_true", help="BẬT bẻ final (đảo TÀI<->XỈU)")
    g.add_argument("--no-flip", action="store_true", help="TẮT bẻ final (giữ nguyên final của các logic đang dùng)")
    wg = ap.add_mutually_exclusive_group()
    wg.add_argument("--wr-flip", action="store_true", help="BẬT flip trọng số WR của SUN (ván CŨ nhất nặng nhất -> giảm dần tới ván MỚI nhất)")
    wg.add_argument("--no-wr-flip", action="store_true", help="TẮT flip trọng số WR của SUN (ván mới nhất nặng nhất)")
    ag = ap.add_mutually_exclusive_group()
    ag.add_argument("--af", action="store_true", help="BẬT AF (auto-flip + CAO/THẤP + bẻ theo WR chế độ) cho SUN")
    ag.add_argument("--no-af", action="store_true", help="TẮT AF, quay về cách chốt cũ của SUN")
    ap.add_argument("--af-low", type=float, default=None, help="AF: WR logic dưới mức này (%%) -> bẻ logic (mặc định AF_FLIP_LOW_DEFAULT)")
    ap.add_argument("--af-high", type=float, default=None, help="AF: WR logic trên mức này (%%) -> bẻ logic (mặc định AF_FLIP_HIGH_DEFAULT)")
    bg = ap.add_mutually_exclusive_group()
    bg.add_argument("--af-band", action="store_true", help="BẬT giới hạn vùng bẻ logic của AF (chỉ bẻ khi WR trong vùng thấp / cao)")
    bg.add_argument("--af-no-band", action="store_true", help="TẮT giới hạn vùng bẻ (quay về ngưỡng --af-low / --af-high như cũ)")
    gfg = ap.add_mutually_exclusive_group()
    gfg.add_argument("--af-group-flipped", action="store_true", help="BẬT: chỉ logic ĐÃ BỊ BẺ mới vào nhóm CAO/THẤP (logic không bẻ mặc định ALL)")
    gfg.add_argument("--af-no-group-flipped", action="store_true", help="TẮT: mọi logic đều được chia nhóm CAO/THẤP như bản trước")
    gmg = ap.add_mutually_exclusive_group()
    gmg.add_argument("--af-group-majority", action="store_true", help="BẬT: nhóm CAO/THẤP phải có >= đa số toàn bộ logic, không thì dùng ALL")
    gmg.add_argument("--af-no-group-majority", action="store_true", help="TẮT: nhóm đông hơn luôn được chọn dù ít logic")
    swg = ap.add_mutually_exclusive_group()
    swg.add_argument("--af-switch", action="store_true", help="BẬT: đổi chế độ ALL/CAO/THẤP chỉ cần --af-switch-need phiếu (mặc định 6/13) thay vì đa số 7/13")
    swg.add_argument("--af-no-switch", action="store_true", help="TẮT: quay về cách gốc (nhóm đông hơn thắng, nhóm CAO/THẤP cần đa số 7/13)")
    ap.add_argument("--af-switch-need", type=int, default=None, help="AF: số phiếu (trên tổng số logic) để đổi sang chế độ khác (mặc định AF_SWITCH_NEED_DEFAULT = 6)")
    slg = ap.add_mutually_exclusive_group()
    slg.add_argument("--af-switch-lead", action="store_true", help="êm hơn: chế độ mới còn phải DẪN ĐẦU duy nhất (nhiều phiếu hơn cả chế độ đang chạy) mới đổi")
    slg.add_argument("--af-no-switch-lead", action="store_true", help="chỉ cần chế độ khác đủ --af-switch-need phiếu là đổi, kể cả khi chế độ đang chạy nhiều phiếu hơn (mặc định)")
    spg = ap.add_mutually_exclusive_group()
    spg.add_argument("--af-switch-prio", action="store_true", help="BẬT: 2 chế độ còn lại cùng đủ phiếu đổi -> ưu tiên theo chế độ ván trước (ALL->CAO · CAO->ALL · THẤP->CAO) (mặc định)")
    spg.add_argument("--af-no-switch-prio", action="store_true", help="TẮT: 2 chế độ cùng đủ phiếu -> lấy chế độ nhiều phiếu hơn, bằng nhau giữ chế độ hiện tại")
    ap.add_argument("--af-low-min", type=float, default=None, help="AF vùng bẻ THẤP: WR tối thiểu (%%) mới bẻ (mặc định 32)")
    ap.add_argument("--af-low-max", type=float, default=None, help="AF vùng bẻ THẤP: WR tối đa (%%) mới bẻ (mặc định 40)")
    ap.add_argument("--af-high-min", type=float, default=None, help="AF vùng bẻ CAO: WR tối thiểu (%%) mới bẻ (mặc định 60)")
    ap.add_argument("--af-high-max", type=float, default=None, help="AF vùng bẻ CAO: WR tối đa (%%) mới bẻ (mặc định 68)")
    ap.add_argument("--af-min", type=int, default=None, help="AF: số ván đã chấm tối thiểu mới bẻ logic / chia nhóm (mặc định AF_MIN_GAMES_DEFAULT)")
    ap.add_argument("--af-mode-window", type=int, default=None, help="AF: số ván gần nhất của mỗi chế độ để tính WR chế độ (mặc định AF_MODE_WINDOW_DEFAULT)")
    ap.add_argument("--af-mode-below", type=float, default=None, help="AF: WR chế độ dưới mức này (%%) -> bẻ final (mặc định AF_MODE_BELOW_DEFAULT)")
    amg = ap.add_mutually_exclusive_group()
    amg.add_argument("--af-mode-flip", action="store_true", help="BẬT bước 3 của AF: bẻ final theo WR chế độ (mặc định TẮT)")
    amg.add_argument("--af-no-mode-flip", action="store_true", help="TẮT bước 3 của AF: không bẻ final theo WR chế độ")
    afg = ap.add_mutually_exclusive_group()
    afg.add_argument("--af-flip", action="store_true", help="BẺ riêng kết quả AF (đảo TÀI<->XỈU)")
    afg.add_argument("--af-no-flip", action="store_true", help="TẮT bẻ riêng kết quả AF")
    afc = ap.add_mutually_exclusive_group()
    afc.add_argument("--af-flip-ct", action="store_true", help="CHỈ bẻ final của AF khi chế độ CAO/THẤP (chế độ ALL giữ nguyên)")
    afc.add_argument("--af-no-flip-ct", action="store_true", help="TẮT bẻ final riêng cho chế độ CAO/THẤP")
    afcao = ap.add_mutually_exclusive_group()
    afcao.add_argument("--af-flip-cao", action="store_true", help="CHỈ bẻ final của AF khi chế độ CAO (THẤP + ALL giữ nguyên)")
    afcao.add_argument("--af-no-flip-cao", action="store_true", help="TẮT bẻ final riêng cho chế độ CAO")
    afthap = ap.add_mutually_exclusive_group()
    afthap.add_argument("--af-flip-thap", action="store_true", help="CHỈ bẻ final của AF khi chế độ THẤP (CAO + ALL giữ nguyên)")
    afthap.add_argument("--af-no-flip-thap", action="store_true", help="TẮT bẻ final riêng cho chế độ THẤP")
    afa = ap.add_mutually_exclusive_group()
    afa.add_argument("--af-flip-all", action="store_true", help="CHỈ bẻ final của AF khi chế độ ALL (CAO/THẤP giữ nguyên)")
    afa.add_argument("--af-no-flip-all", action="store_true", help="TẮT bẻ final riêng cho chế độ ALL")
    a = ap.parse_args()
    UPSTREAM_URL, POLL_SEC = a.upstream, a.poll
    if a.no_hit:
        HIT_ENABLED = False
    if a.af:
        AF_ENABLED = True
    elif a.no_af:
        AF_ENABLED = False
    if a.af_low is not None:
        AF_FLIP_LOW = a.af_low
    if a.af_high is not None:
        AF_FLIP_HIGH = a.af_high
    if a.af_band:
        AF_FLIP_BAND = True
    elif a.af_no_band:
        AF_FLIP_BAND = False
    if a.af_group_flipped:
        AF_GROUP_FLIPPED_ONLY = True
    elif a.af_no_group_flipped:
        AF_GROUP_FLIPPED_ONLY = False
    if a.af_group_majority:
        AF_GROUP_NEED_MAJORITY = True
    elif a.af_no_group_majority:
        AF_GROUP_NEED_MAJORITY = False
    if a.af_switch:
        AF_SWITCH = True
    elif a.af_no_switch:
        AF_SWITCH = False
    if a.af_switch_need is not None:
        AF_SWITCH_NEED = a.af_switch_need
    if a.af_switch_prio:
        AF_SWITCH_PRIO = True
    elif a.af_no_switch_prio:
        AF_SWITCH_PRIO = False
    if a.af_switch_lead:
        AF_SWITCH_LEAD = True
    elif a.af_no_switch_lead:
        AF_SWITCH_LEAD = False
    if a.af_low_min is not None:
        AF_FLIP_LOW_MIN = a.af_low_min
    if a.af_low_max is not None:
        AF_FLIP_LOW_MAX = a.af_low_max
    if a.af_high_min is not None:
        AF_FLIP_HIGH_MIN = a.af_high_min
    if a.af_high_max is not None:
        AF_FLIP_HIGH_MAX = a.af_high_max
    if a.af_min is not None:
        AF_MIN_GAMES = a.af_min
    if a.af_mode_window is not None:
        AF_MODE_WINDOW = a.af_mode_window
    if a.af_mode_below is not None:
        AF_MODE_BELOW = a.af_mode_below
    if a.af_mode_flip:
        AF_MODE_FLIP = True
    elif a.af_no_mode_flip:
        AF_MODE_FLIP = False
    if a.af_flip:
        AF_FLIP_FINAL = True
    elif a.af_no_flip:
        AF_FLIP_FINAL = False
    if a.af_flip_ct:
        AF_FLIP_FINAL_CT = True
    elif a.af_no_flip_ct:
        AF_FLIP_FINAL_CT = False
    if a.af_flip_cao:
        AF_FLIP_FINAL_CAO = True
    elif a.af_no_flip_cao:
        AF_FLIP_FINAL_CAO = False
    if a.af_flip_thap:
        AF_FLIP_FINAL_THAP = True
    elif a.af_no_flip_thap:
        AF_FLIP_FINAL_THAP = False
    if a.af_flip_all:
        AF_FLIP_FINAL_ALL = True
    elif a.af_no_flip_all:
        AF_FLIP_FINAL_ALL = False
    af_apply_limits()                              # chuẩn hoá tham số AF
    if a.flip:
        FLIP_FINAL = True
    elif a.no_flip:
        FLIP_FINAL = False
    if a.wr_flip:
        WR_FLIP_WEIGHT = True
    elif a.no_wr_flip:
        WR_FLIP_WEIGHT = False
    ensure_poller()
    if DATA_PERSISTENT:
        print(f"DATA        ->  {DATA_DIR} (BEN · khoi dong lan thu {BOOT_INFO.get('count')} · lan dau {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(BOOT_INFO.get('first') or 0))})")
    else:
        print("!" * 100)
        print(f"!! DATA        ->  {DATA_DIR} KHONG BEN: dang chay tren Railway ma CHUA gan Volume -> key, lich su game, thiet bi duoc duyet se MAT sau moi lan deploy / restart.")
        print("!!                 Cach sua: Railway -> service -> Settings -> Volumes -> New Volume -> Mount path /data -> redeploy. Code tu nhan (RAILWAY_VOLUME_MOUNT_PATH).")
        print("!" * 100)
    print(f"KEY HAN     ->  {'tinh tu LAN DUNG DAU TIEN (kich hoat)' if KEY_START_ON_ACTIVATE else 'tinh tu luc TAO key (kieu cu)'} · key cu tao truoc do giu nguyen han")
    print(f"SUNVIW API  ->  http://{a.host}:{a.port}/api/predict")
    print(f"upstream    ->  {UPSTREAM_URL}")
    print(f"be final SUN ->  {'BAT' if FLIP_FINAL else 'TAT'}  (chi ap cho van quay ve cach cu; van do AF chot khong bi be)")
    print(f"IP          ->  theo doi {'BAT' if IP_TRACK_ENABLED else 'TAT'} · dang dung = co request trong {IP_ACTIVE_SEC}s · tin proxy {'BAT' if IP_TRUST_PROXY else 'TAT'} · admin key {'CO' if IP_ADMIN_KEY else 'KHONG (ai mo panel cung thay danh sach IP)'} · file {IP_PATH}")
    _be_logic = (f"chi be khi WR trong {AF_FLIP_LOW_MIN:g}-{AF_FLIP_LOW_MAX:g}% hoac {AF_FLIP_HIGH_MIN:g}-{AF_FLIP_HIGH_MAX:g}% (ngoai vung khong be)" if AF_FLIP_BAND
                 else f"be logic WR < {AF_FLIP_LOW:g}% hoac > {AF_FLIP_HIGH:g}%")
    print(f"AF SUN      ->  {'BAT' if AF_ENABLED else 'TAT'} · {_be_logic} (toi thieu {AF_MIN_GAMES} van) · be che do {('BAT (CAO/THAP khi WR ' + str(AF_MODE_WINDOW) + ' van gan nhat cua che do < ' + format(AF_MODE_BELOW, 'g') + '%, can ' + str(AF_MODE_MIN) + ' van)') if AF_MODE_FLIP else 'TAT'} · be rieng AF {'BAT' if AF_FLIP_FINAL else 'TAT'}")
    print(f"AF nhom     ->  chi logic bi be vao nhom CAO/THAP {'BAT (logic khong be = ALL)' if AF_GROUP_FLIPPED_ONLY else 'TAT'} · nhom phai >= da so toan bo logic (n//2+1) {'BAT (ít hon -> dung ALL)' if AF_GROUP_NEED_MAJORITY else 'TAT'}")
    print(f"AF doi che do ->  {('BAT · chi can ' + str(AF_SWITCH_NEED) + ' phieu (tren tong so logic) de doi giua ALL / CAO / THAP, thay vi da so 7/13 · nho che do van truoc · 2 che do con lai cung du phieu: ' + ('uu tien theo van truoc (ALL->CAO · CAO->ALL · THAP->CAO)' if AF_SWITCH_PRIO else 'lay che do nhieu phieu hon')) if AF_SWITCH else 'TAT (cach goc: nhom dong hon thang, can da so 7/13)'}")
    print(f"be final AF ->  moi che do {'BAT' if AF_FLIP_FINAL else 'TAT'} · CAO+THAP gop {'BAT (ALL giu nguyen)' if AF_FLIP_FINAL_CT else 'TAT'} · chi CAO {'BAT' if AF_FLIP_FINAL_CAO else 'TAT'} · chi THAP {'BAT' if AF_FLIP_FINAL_THAP else 'TAT'} · chi ALL {'BAT (CAO/THAP giu nguyen)' if AF_FLIP_FINAL_ALL else 'TAT'}")
    print(f"xoa lich su ->  nut o panel {'BAT' if HIST_CLEAR_ENABLED else 'TAT'} · chi an lich su hien thi (khong dung toi logic / WR / AF) · file moc {HIST_CLEAR_PATH}")
    print(f"OFF SERVER  ->  {'DANG BAT (tool ngoai khong nhan duoc du doan, chi panel / admin nhan)' if offsrv_state()['off'] else 'tat'} · bat / tat o trang /api/admin (chi admin chinh) · file {OFFSRV_PATH}")
    print(f"PANEL HTML  ->  thiet bi phai duoc admin chinh duyet (khong can key, vao ca Sun + Hit) · file {PANEL_DEV_PATH} · toi da {PANEL_MAX_PENDING_PER_IP} yeu cau cho duyet / IP")
    print(f"AUTO CUOC   ->  {'BAT' if AB_ENABLED else 'TAT'} · http://{a.host}:{a.port}/tool/autocuoc · nguon du doan {AB_FEED_KEY} · luu mat khau {'CO (AUTOBET_SAVE_PW=1)' if AB_SAVE_PW else 'KHONG (chi RAM)'} · file {AB_PATH}")
    print(f"WR 100 phien ->  luu toi da {PERSIST_KEEP} van da cham · WR dung/sai xet {EVAL_WINDOW} van gan nhat")
    print(f"WR          ->  xet {WR_WINDOW} van gan nhat, trong so cao nhat x{WR_WEIGHT_NEWEST}, flip trong so {'BAT (cu nhat nang nhat)' if WR_FLIP_WEIGHT else 'TAT (moi nhat nang nhat)'}, trong so (cu -> moi): "
          + " · ".join(f"{w:.2f}" for w in wr_weights_full()))
    print(f"KEY/ADMIN   ->  trang admin /api/admin (1 o nhap key, tu nhan dien · moi key chi thuoc 1 game (sun | hit | lc79, chon luc tao; key cu chua gan game = {KEY_LEGACY_GAME}) · moi key gan HWID thiet bi (nhieu thiet bi / key, admin chinh + admin phu deu chon duoc) · bat buoc HWID {'BAT' if HWID_REQUIRED else 'TAT'}) · mat khau admin chinh {'tu env SUNVIW_MAIN_PASS' if _ENV_MAIN_PASS else 'tu hash mac dinh trong code (nen dat SUNVIW_MAIN_PASS)'} · bat key cho API {'BAT' if KEY_GATE_API else 'TAT'} · file key {KEYS_PATH}")
    for _tb in HIT_TABLES.values():
        _c = _tb.cfg
        print(f"HITCLUB {_tb.label:<9} ->  {'BAT' if _tb.active else 'TAT'} · http://{a.host}:{a.port}/api/predict{_tb.key} · gid {_c.GID} · quet moi {_c.POLL_SEC:g}s · file {_tb.path} · "
              f"AF {'BAT' if _c.AF_ENABLED else 'TAT'} · WR xet {_c.WR_WINDOW} van · be final {'BAT' if _c.FLIP_FINAL else 'TAT'} · config RIENG (khoi CONFIG HITCLUB)")
    app.run(host=a.host, port=a.port, threaded=True)


if __name__ == "__main__":
    main()
