import os
import glob

html_files = glob.glob(r"c:\jb\clinic app\frontend\static\*.html")

footer_html = '''
<div style="text-align: center; padding: 20px; font-size: 14px; color: #666; background-color: #f9fafb; border-top: 1px solid #e5e7eb; margin-top: auto; font-family: 'Inter', sans-serif;">
  made by JINENDRA BANTHIA contact 9124483008 or jinendra.banthia.iter@gmail.com
</div>
'''

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '</body>' in content:
        parts = content.rsplit('</body>', 1)
        new_content = parts[0] + footer_html + '</body>' + parts[1]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    print(f"Updated {file_path}")
