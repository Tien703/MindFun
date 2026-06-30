import os
import re

ui_dir = "ui"

for root, dirs, files in os.walk(ui_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            strings = re.findall(r'["\'](.*?[ĐÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴđáàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ].*?)["\']', content)
            
            for s in set(strings):
                if f't("{s}")' not in content and f"t('{s}')" not in content and f't(f"{s}")' not in content and f"t(f'{s}')" not in content:
                    print(f"{path}: {s}")
