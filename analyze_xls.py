with open('RTdata/CSU18M68-QFN16-2604222-FT20260224018-FT1-RT2-2026031707-3380D-0065-1.xls', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"总行数: {len(lines)}")
print("\n前30行内容:")
print("="*80)
for i, line in enumerate(lines[:30], 1):
    print(f"行{i}: {repr(line.rstrip())}")

print("\n" + "="*80)
print("\n检查分隔符类型:")
sample = lines[9] if len(lines) > 9 else lines[0]
print(f"示例行: {repr(sample[:100])}")
print(f"包含制表符: {'\t' in sample}")
print(f"包含逗号: {',' in sample}")

print("\n查找表头行:")
for i, line in enumerate(lines[:20], 1):
    if 'Time' in line and ('SITE' in line or 'H_bin' in line):
        print(f"表头在第{i}行: {repr(line.rstrip())}")
        print(
            f"分隔符: {'Tab' if '\t' in line else 'Comma' if ',' in line else 'Other'}")

print("\n数据行样本（表头后3行）:")
# 找到表头行
header_idx = None
for i, line in enumerate(lines[:20]):
    if 'Time' in line and 'SITE' in line:
        header_idx = i
        break

if header_idx:
    for i in range(header_idx+1, min(header_idx+4, len(lines))):
        print(f"行{i+1}: {repr(lines[i].rstrip())}")
