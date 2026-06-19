import os

# اسم الملف اللي هيتجمع فيه الكود
output_filename = "Rently_Backend_Full_Code.txt"

# الفولدرات اللي عايزين نتجاهلها عشان الملف ميكبرش على الفاضي
ignored_folders = ['venv', '.venv', '__pycache__', '.git', 'migrations']

with open(output_filename, 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk("."):
        # استبعاد الفولدرات غير المهمة
        dirs[:] = [d for d in dirs if d not in ignored_folders]
        
        for file in files:
            # هنجمع ملفات البايثون بس (وممكن تزود الـ json أو الـ csv لو حابب)
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                
                # كتابة اسم الملف كعنوان عشان الـ AI يفهم ده كود إيه
                outfile.write(f"\n\n{'='*50}\n")
                outfile.write(f"### FILE: {filepath} ###\n")
                outfile.write(f"{'='*50}\n\n")
                
                # قراءة محتوى الملف وكتابته
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}\n")

print(f"Done! All your code is now in {output_filename}")