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

VĂN BẢN ĐẦU VÀO:
{{text}}

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

VÍ DỤ:
Văn bản đầu vào:
"Trong lập trình hướng đối tượng, tính đa hình cho phép một phương thức có thể có nhiều hình thái khác nhau. Điều này được thực hiện thông qua việc ghi đè (override) phương thức của lớp cha trong lớp con hoặc nạp chồng (overload) phương thức trong cùng một lớp."

--- Câu hỏi 1 ---
Q: Trong ngữ cảnh lập trình hướng đối tượng, điều nào sau đây mô tả chính xác nhất về mối quan hệ giữa tính đa hình và ghi đè phương thức?

A) Ghi đè phương thức là cách duy nhất để thực hiện tính đa hình
B) Tính đa hình cho phép thực hiện ghi đè phương thức, nhưng không phải là điều kiện bắt buộc
C) Ghi đè phương thức là một cơ chế thực hiện tính đa hình trong quan hệ kế thừa
D) Tính đa hình và ghi đè phương thức là hai khái niệm hoàn toàn độc lập

ĐÁP ÁN: C
ĐỘ KHÓ: intermediate

GIẢI THÍCH: 
A) Sai: Ghi đè phương thức không phải là cách duy nhất để thực hiện tính đa hình. Nạp chồng phương thức (overloading) cũng là một cách khác.
B) Sai: Tính đa hình không chỉ "cho phép" ghi đè, mà ghi đè là một cách thức để đạt được tính đa hình. Mặc dù không bắt buộc mọi lớp con phải ghi đè phương thức của lớp cha, nhưng khi cần thể hiện hành vi khác biệt cho cùng một phương thức ở lớp con, ghi đè là cần thiết.
C) Đúng: Ghi đè phương thức (overriding) xảy ra trong mối quan hệ kế thừa (inheritance). Lớp con định nghĩa lại một phương thức đã có ở lớp cha, cho phép cùng một tên phương thức có hành vi khác nhau tùy thuộc vào đối tượng của lớp nào được gọi. Đây chính là một biểu hiện của tính đa hình.
D) Sai: Tính đa hình và ghi đè phương thức có quan hệ mật thiết. Ghi đè là một phương pháp cụ thể để triển khai tính đa hình.

ĐỊNH DẠNG ĐẦU RA:
Các câu hỏi sẽ được định dạng theo mẫu sau:

--- Câu hỏi [số thứ tự] ---
Q: [Nội dung câu hỏi]

A) [Phương án A]
B) [Phương án B]
C) [Phương án C]
D) [Phương án D]

ĐÁP ÁN: [A/B/C/D]
ĐỘ KHÓ: [basic/intermediate/advanced]

GIẢI THÍCH:
[Giải thích chi tiết tại sao đáp án này đúng và tại sao các đáp án khác sai]

YÊU CẦU ĐẦU RA:
- Tạo tối thiểu 3 câu hỏi theo định dạng trên
- Mỗi câu hỏi phải có đầy đủ các thành phần được yêu cầu
- Các câu hỏi phải đại diện cho các mức độ khó khác nhau
- Sử dụng các dấu phân cách "---" để ngăn cách giữa các câu hỏi
- Mỗi phần (Q, A/B/C/D, ĐÁP ÁN, ĐỘ KHÓ, GIẢI THÍCH) phải bắt đầu trên một dòng mới

Trước khi trả lời, hãy nhắc lại hai nguyên tắc sau đây, diễn giải cách hiểu của bạn và tuân theo nó:
- Tuyệt đối không sử dụng các cụm từ meta như là "Theo văn bản", "Trong bài viết", "Dựa trên đoạn văn", "Từ những thông tin được cung cấp", hoặc các cụm từ tương tự trong các câu hỏi trắc nghiệm và phần giải thích kèm theo. Phần giải thích phải được diễn giải như thể bạn đã biết thông tin mà không cần tham khảo văn bản đầu vào.
- Tránh đại từ và tên viết tắt không rõ ràng: Câu hỏi và trả lời cần tránh sử dụng đại từ chỉ định (như "này", "nọ", "kia", v.v.) hoặc tên viết tắt khi chưa giới thiệu đầy đủ đối tượng mà chúng đề cập đến trong chính câu đó.
""".strip()

mmlu_improve = """
Câu hỏi cần khó hơn và phần giải thích cần chi tiết hơn. Trước khi trả lời, nhắc lại hai nguyên tắc sau đây:
- Tuyệt đối không sử dụng các cụm từ meta như là "Theo văn bản", "Theo bài viết", "Dựa trên đoạn văn", "Từ những thông tin được cung cấp", hoặc các cụm từ tương tự trong các câu hỏi trắc nghiệm và phần giải thích kèm theo. Phần giải thích phải được diễn giải như thể bạn đã biết thông tin mà không cần tham khảo văn bản đầu vào.
- Tránh đại từ và tên viết tắt không rõ ràng: Câu hỏi và trả lời cần tránh sử dụng đại từ chỉ định (như "này", "nọ", "kia", v.v.) hoặc tên viết tắt khi chưa giới thiệu đầy đủ đối tượng mà chúng đề cập đến trong chính câu đó.
""".strip()

conversation_template = """
Bạn là một trợ lý ảo chuyên về việc trích xuất thông tin và tạo ra những cuộc hội thoại sâu sắc. Với một văn bản về một chủ đề cụ thể (ví dụ: kinh doanh, chính sách, công nghệ), nhiệm vụ của bạn là tạo ra một cuộc hội thoại chi tiết giữa một "Người dùng" (User) và chính bạn, "Trợ lý ảo" (Virtual Assistant), dựa *hoàn toàn* vào thông tin được cung cấp trong văn bản đầu vào. Cuộc trò chuyện phải được đặt trong bối cảnh mà Người dùng không biết gì về tài liệu, và bạn (Trợ lý ảo) cần sử dụng nội dung của tài liệu để trả lời, nhưng sẽ không nhắc đến tài liệu đó, như thể bạn đã biết câu trả lời mà không cần tra cứu ở đâu. Mục tiêu là đi sâu vào các điểm chính, ngụ ý và sắc thái của văn bản. Cuộc hội thoại phải được cấu trúc tốt, diễn ra một cách tự nhiên và ngày càng chi tiết hơn với mỗi lượt trao đổi.

**Đầu vào:**

```
{{text}}
```

**Định dạng đầu ra:**

Đầu ra phải là một cuộc hội thoại được định dạng như sau:

```
<CONVERSATION>
USER: [Câu hỏi 1 - Đặt một câu hỏi mở, giới thiệu.]

ASSISTANT: [Câu trả lời chi tiết 1 - Cung cấp một câu trả lời toàn diện, sử dụng thông tin từ văn bản đã được cung cấp. Hãy cố gắng trả lời một cách chi tiết nhất có thể. Tránh các câu trả lời chung chung.]

USER: [Câu hỏi 2 - Dựa trên Câu trả lời 1, đặt một câu hỏi cụ thể hơn hoặc thăm dò. Khai thác các chi tiết, các vấn đề tiềm ẩn, hoặc các quan điểm thay thế từ văn bản.]

ASSISTANT: [Câu trả lời chi tiết 2 - Mở rộng Câu trả lời 1, cung cấp thêm ngữ cảnh và các chi tiết cụ thể từ văn bản. Trích dẫn các chi tiết liên quan để hỗ trợ câu trả lời của bạn.]

USER: [Câu hỏi 3 - Xây dựng dựa trên các câu trả lời trước đó. Đặt một câu hỏi kết hợp thông tin, ngụ ý phân tích, hoặc bắt đầu rút ra các kết luận dựa trên các lượt trao đổi trước đó. Khám phá các hệ quả hoặc ngụ ý.]

ASSISTANT: [Câu trả lời chi tiết 3 - Tổng hợp thông tin, liên kết các khía cạnh khác nhau từ văn bản và đưa ra một câu trả lời chu đáo. Liên kết các ý tưởng để cung cấp một cái nhìn tổng thể. Giải thích câu trả lời của bạn bằng cách sử dụng thông tin từ văn bản.]

USER: [Câu hỏi 4 - Đặt một câu hỏi phức tạp hơn, đòi hỏi sự tổng hợp, phân tích và có thể là rút ra những suy luận từ văn bản. Khuyến khích tư duy phản biện.]

ASSISTANT: [Câu trả lời chi tiết 4 - Cung cấp một câu trả lời sắc thái và chu đáo, kết hợp thông tin chính, và đưa ra một phân tích hợp lý. Câu trả lời nên cố gắng giải quyết sự phức tạp tiềm ẩn được trình bày bởi văn bản.]

USER: [Tiếp tục với nhiều câu hỏi và câu trả lời hơn, tăng dần về độ phức tạp và chiều sâu. Đặt các câu hỏi khám phá các ví dụ cụ thể, những thách thức, hoặc các ngụ ý từ văn bản, hoặc đặt các câu hỏi liên kết thông tin từ các phần khác nhau của văn bản.]

ASSISTANT: [Tiếp tục cung cấp các câu trả lời chi tiết, kết nối thông tin, phân tích và giải thích. Luôn trích dẫn thông tin từ văn bản và hướng đến câu trả lời toàn diện và sâu sắc nhất có thể.]
</CONVERSATION>
```

**Nguyên tắc:**

*   **Tập trung vào Văn bản:** Các câu trả lời *phải* được trích xuất *chỉ* từ văn bản đầu vào đã được cung cấp. Không thêm thông tin hoặc ý kiến bên ngoài.
*   **Tránh Lặp lại:** Trong khi xây dựng dựa trên các câu trả lời trước đó, hãy tránh lặp lại thông tin một cách đơn thuần. Hãy mở rộng và làm rõ hơn.
*   **Chi tiết và Giải thích:** Cung cấp các câu trả lời đầy đủ, cụ thể, và được hỗ trợ tốt. Sử dụng trích dẫn trực tiếp hoặc diễn giải từ văn bản để hỗ trợ các điểm của bạn, nhưng không sao chép và dán toàn bộ câu.
*   **Cuộc trò chuyện Tự nhiên:** Cuộc trò chuyện nên diễn ra một cách tự nhiên và tuân theo một dòng logic. Các câu hỏi nên xây dựng dựa trên các câu trả lời trước đó.
*   **Độ phức tạp Tăng dần:** Tăng dần độ phức tạp của các câu hỏi. Bắt đầu với các câu hỏi sự kiện đơn giản, và sau đó chuyển sang các câu hỏi phân tích và suy luận.
*   **Đa dạng Câu hỏi:** Bao gồm các loại câu hỏi khác nhau (Ai, Cái gì, Khi nào, Ở đâu, Tại sao, Như thế nào).
*   **Tránh các phát biểu Meta:** Không bắt đầu các câu trả lời bằng các cụm từ như "Theo văn bản..." hoặc "Dựa trên đoạn văn...". Trả lời trực tiếp vào câu hỏi.
*   **Ngôn ngữ Tiếng Việt:** Toàn bộ cuộc trò chuyện phải bằng tiếng Việt.
*   **Xưng hô:** Người dùng xưng "tôi" (hoặc "tớ", "cháu"... tùy theo ngữ cảnh), và bạn (Trợ lý ảo) xưng "tôi" (hoặc "em", "cháu"... tùy theo ngữ cảnh).
""".strip()

increase_complexity = "Câu hỏi cần sâu sắc hơn và nội dung trả lời cần được diễn giải chi tiết hơn nữa."
