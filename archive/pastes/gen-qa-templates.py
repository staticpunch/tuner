question_template = """
Dựa vào đoạn văn bản sau:

{{text}}

Hãy tạo ra 4 câu hỏi có thể trả lời được bằng thông tin trong đoạn văn trên, với độ khó tăng dần.

Mức 1. **Câu hỏi dễ:**  Một câu hỏi tìm kiếm thông tin trực tiếp và rõ ràng được nêu trong đoạn văn. Câu trả lời có thể được tìm thấy dễ dàng bằng cách đọc lướt qua.

Mức 2. **Câu hỏi trung bình:** Một câu hỏi yêu cầu hiểu và tổng hợp một vài thông tin hoặc chi tiết liên quan trong đoạn văn. Câu trả lời đòi hỏi phải đọc kỹ hơn và kết nối các phần khác nhau.

Mức 3. **Câu hỏi khó:** Một câu hỏi đòi hỏi suy luận hoặc rút ra kết luận dựa trên thông tin trong đoạn văn. Câu trả lời không được nêu trực tiếp mà cần phải suy nghĩ và phân tích.

Mức 4. **Câu hỏi rất khó:** Một câu hỏi phức tạp, có thể yêu cầu so sánh, đối chiếu, đánh giá, hoặc áp dụng thông tin từ đoạn văn vào một bối cảnh mới (vẫn dựa trên thông tin trong văn bản). Câu trả lời có thể có nhiều cách diễn đạt và đòi hỏi sự hiểu biết sâu sắc về nội dung.

Các câu hỏi nên đa dạng về loại (Who, What, When, Where, Why and How). **Các câu hỏi phải bằng tiếng Việt và không bắt đầu bằng những cụm từ như "Theo văn bản", "Căn cứ vào nội dung", hoặc các cụm từ giới thiệu tương tự.** Chỉ sử dụng thông tin trong đoạn văn để đặt câu hỏi.

Yêu cầu định dạng output:

Danh sách câu hỏi phải được đặt trong cặp thẻ <QUESTIONS> và </QUESTIONS>. Mỗi câu hỏi được đánh số thứ tự từ 1 đến 4, mặc định độ khó tương ứng tăng dần từ mức 1 đến mức 4, không cần ghi chú thêm độ khó (dễ, trung bình, khó, rất khó). Ví dụ:

```
<QUESTIONS>
1. Câu hỏi 1
2. Câu hỏi 2
3. Câu hỏi 3
4. Câu hỏi 4
</QUESTIONS>
```

**Lưu ý quan trọng:** Phản hồi của bạn chỉ chứa danh sách câu hỏi theo định dạng được hướng dẫn bên trên, được bao bọc bởi thẻ `<QUESTIONS>` và `</QUESTIONS>`. Không thêm bất kỳ câu trả lời, lời giải thích hoặc thông tin bổ sung nào khác.
""".strip()

answer_template = """
Dựa vào đoạn văn bản sau:

{{text}}

Hãy trả lời câu hỏi sau đây, **chỉ sử dụng thông tin có trong đoạn văn bản được cung cấp:**

{{question}}

**Các yêu cầu và ràng buộc cụ thể:**

1. **Nguồn thông tin duy nhất:** Câu trả lời của bạn phải **hoàn toàn** dựa trên thông tin được cung cấp trong đoạn văn bản trên. **Nghiêm cấm** sử dụng bất kỳ kiến thức, thông tin hoặc dữ liệu nào nằm ngoài phạm vi của văn bản này.

2. **Tránh cụm từ thừa:**  **Tuyệt đối không** bắt đầu câu trả lời bằng các cụm từ như "Dựa trên văn bản", "Theo văn bản", "Căn cứ vào nội dung", hoặc bất kỳ cụm từ giới thiệu tương tự nào ám chỉ nguồn gốc của câu trả lời. Đi thẳng vào nội dung trả lời.

3. **Giải thích chi tiết và cụ thể:**  Câu trả lời cần được trình bày một cách **chi tiết**, **cụ thể** và **rõ ràng**, cung cấp đầy đủ thông tin để người đọc hiểu rõ. Hãy cố gắng làm cho câu trả lời của bạn trở nên **hữu ích** và **thuyết phục** bằng cách giải thích cặn kẽ.

4. **Thông tin liên quan từ văn bản:**  Hãy chủ động cung cấp các thông tin **liên quan trực tiếp** từ đoạn văn bản có thể giúp câu trả lời của bạn trở nên hữu ích hơn cho người dùng. Điều này không có nghĩa là thêm thông tin từ bên ngoài, mà là khai thác triệt để thông tin **trong** văn bản.

5. **Tránh đại từ và tên viết tắt không rõ ràng:** **Để đảm bảo tính rõ ràng và dễ hiểu, câu trả lời cần tránh sử dụng đại từ chỉ định (như "này", "nọ", "kia", v.v.) hoặc tên viết tắt khi chưa giới thiệu đầy đủ đối tượng mà chúng đề cập đến *trong chính câu trả lời*.**  Luôn sử dụng tên đầy đủ của đối tượng ít nhất một lần trước khi có thể sử dụng đại từ hoặc tên viết tắt (nếu cần thiết).

**Đảm bảo rằng câu trả lời của bạn tuân thủ nghiêm ngặt tất cả các yêu cầu trên.**

Yêu cầu định dạng output:

Câu trả lời phải được đặt trong cặp thẻ <ANSWER> và </ANSWER>. 
""".strip()

answers_template = """
Dựa vào đoạn văn bản sau:

{{text}}

Hãy trả lời các câu hỏi sau đây, **chỉ sử dụng thông tin có trong đoạn văn bản được cung cấp:**

**Câu hỏi 1:** {{question1}}
**Câu hỏi 2:** {{question2}}
**Câu hỏi 3:** {{question3}}
**Câu hỏi 4:** {{question4}}

**Các yêu cầu và ràng buộc cụ thể (áp dụng cho từng câu trả lời):**

1. **Nguồn thông tin duy nhất:** Mỗi câu trả lời của bạn phải **hoàn toàn** dựa trên thông tin được cung cấp trong đoạn văn bản trên. **Nghiêm cấm** sử dụng bất kỳ kiến thức, thông tin hoặc dữ liệu nào nằm ngoài phạm vi của văn bản này.

2. **Tránh cụm từ thừa:**  **Tuyệt đối không** bắt đầu bất kỳ câu trả lời nào bằng các cụm từ như "Dựa trên văn bản", "Theo văn bản", "Căn cứ vào nội dung", hoặc bất kỳ cụm từ giới thiệu tương tự nào ám chỉ nguồn gốc của câu trả lời. Đi thẳng vào nội dung trả lời.

3. **Giải thích chi tiết và cụ thể:**  Mỗi câu trả lời cần được trình bày một cách **chi tiết**, **cụ thể** và **rõ ràng**, cung cấp đầy đủ thông tin để người đọc hiểu rõ. Hãy cố gắng làm cho mỗi câu trả lời của bạn trở nên **hữu ích** và **thuyết phục** bằng cách giải thích cặn kẽ.

4. **Thông tin liên quan từ văn bản:**  Hãy chủ động cung cấp các thông tin **liên quan trực tiếp** từ đoạn văn bản có thể giúp mỗi câu trả lời của bạn trở nên hữu ích hơn cho người dùng. Điều này không có nghĩa là thêm thông tin từ bên ngoài, mà là khai thác triệt để thông tin **trong** văn bản.

5. **Tránh đại từ và tên viết tắt không rõ ràng:** **Để đảm bảo tính rõ ràng và dễ hiểu, mỗi câu trả lời cần tránh sử dụng đại từ chỉ định (như "này", "nọ", "kia", v.v.) hoặc tên viết tắt khi chưa giới thiệu đầy đủ đối tượng mà chúng đề cập đến *trong chính câu trả lời đó*.**  Luôn sử dụng tên đầy đủ của đối tượng ít nhất một lần trước khi có thể sử dụng đại từ hoặc tên viết tắt (nếu cần thiết) **trong từng câu trả lời**.

**Đảm bảo rằng mỗi câu trả lời của bạn tuân thủ nghiêm ngặt tất cả các yêu cầu trên.**

Yêu cầu định dạng output:

Các câu trả lời phải được đặt trong cặp thẻ `<ANSWERS>` và `</ANSWERS>`, với mỗi câu trả lời được đánh số thứ tự từ 1 đến 4  tương ứng với thứ tự câu hỏi. Ví dụ:

```
<ANSWERS>
1. Câu trả lời 1
2. Câu trả lời 2
3. Câu trả lời 3
4. Câu trả lời 4
</ANSWERS>
""".strip()

mmlu_template = """
Bạn là một chuyên gia trong việc tạo câu hỏi trắc nghiệm chất lượng cao. Nhiệm vụ của bạn là tạo các câu hỏi trắc nghiệm dựa trên văn bản đầu vào, tuân theo định dạng và tiêu chuẩn của bộ câu hỏi MMLU (Massive Multitask Language Understanding).

HƯỚNG DẪN:

1. Phân tích văn bản đầu vào và xác định:
   - Các khái niệm chính
   - Các mối quan hệ quan trọng
   - Các sự kiện hoặc quy trình đáng chú ý
   - Các ứng dụng thực tế của kiến thức

2. Tạo câu hỏi theo các nguyên tắc sau:
   - Mỗi câu hỏi phải đo lường được khả năng hiểu sâu, không chỉ ghi nhớ đơn thuần
   - Tập trung vào suy luận, phân tích và ứng dụng kiến thức
   - Đảm bảo độ khó tương đương cấp độ đại học hoặc sau đại học
   - Câu hỏi phải rõ ràng, không mơ hồ
   - Tránh các gợi ý không chủ ý về đáp án đúng

3. Tạo các phương án trả lời:
   - Luôn có đúng 4 phương án (A, B, C, D)
   - Chỉ có một đáp án đúng
   - Các phương án sai phải hợp lý và có tính đánh lừa
   - Độ dài các phương án nên tương đương nhau
   - Tránh các từ như "tất cả", "không bao giờ" trong phương án

4. Định dạng câu hỏi:
Câu hỏi 1:
[Nội dung câu hỏi]

A) [Phương án A]
B) [Phương án B]
C) [Phương án C]
D) [Phương án D]

Đáp án đúng: [Chữ cái đáp án]
Giải thích: [Giải thích ngắn gọn tại sao đáp án này đúng]

VÍ DỤ:

Văn bản đầu vào:
"Trong lập trình hướng đối tượng, tính đa hình cho phép một phương thức có thể có nhiều hình thái khác nhau. Điều này được thực hiện thông qua việc ghi đè (override) phương thức của lớp cha trong lớp con hoặc nạp chồng (overload) phương thức trong cùng một lớp."

Câu hỏi mẫu:
Trong ngữ cảnh lập trình hướng đối tượng, điều nào sau đây mô tả chính xác nhất về mối quan hệ giữa tính đa hình và ghi đè phương thức?

A) Ghi đè phương thức là cách duy nhất để thực hiện tính đa hình
B) Tính đa hình cho phép thực hiện ghi đè phương thức, nhưng không phải là điều kiện bắt buộc
C) Ghi đè phương thức là một cơ chế thực hiện tính đa hình trong quan hệ kế thừa
D) Tính đa hình và ghi đè phương thức là hai khái niệm hoàn toàn độc lập

Đáp án đúng: C
Giải thích: Ghi đè phương thức là một cách cụ thể để thực hiện tính đa hình trong quan hệ kế thừa giữa các lớp, cho phép lớp con định nghĩa lại hành vi của phương thức từ lớp cha.

YÊU CẦU ĐẦU VÀO:
Hãy cung cấp văn bản mà bạn muốn tạo câu hỏi. Văn bản nên chứa đủ thông tin để tạo ít nhất 3-5 câu hỏi chất lượng cao.

ĐỊNH DẠNG ĐẦU RA:
Các câu hỏi phải được định dạng chính xác theo cấu trúc sau, sử dụng các tag XML để dễ dàng parse:

<questions>
    <question id="1">
        <text>
        [Nội dung câu hỏi]
        </text>
        <choices>
            <choice id="A">[Phương án A]</choice>
            <choice id="B">[Phương án B]</choice>
            <choice id="C">[Phương án C]</choice>
            <choice id="D">[Phương án D]</choice>
        </choices>
        <answer>[A/B/C/D]</answer>
        <explanation>
        [Giải thích chi tiết tại sao đáp án này đúng]
        </explanation>
        <difficulty>[basic/intermediate/advanced]</difficulty>
        <skill>[understanding/application/analysis/evaluation]</skill>
    </question>
</questions>

YÊU CẦU ĐẦU RA:
- Tối thiểu 3 câu hỏi trắc nghiệm theo định dạng XML ở trên
- Mỗi câu hỏi phải có đầy đủ các thành phần được định nghĩa trong cấu trúc
- Các câu hỏi phải đại diện cho các mức độ khó và kỹ năng khác nhau
- Nội dung trong các tag phải được viết trên một dòng (không xuống dòng)
""".strip()
