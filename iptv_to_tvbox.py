import re

def parse_m3u(file_path):
    channels = {}
    current_channel = None
    current_group = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#EXTINF'):
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    current_group = match.group(1)
                    if current_group not in channels:
                        channels[current_group] = []
                
                name_match = re.search(r',(.*?)$', line)
                if name_match:
                    current_channel = name_match.group(1).strip()
            elif line.startswith('http'):
                if current_channel and current_group in channels:
                    channels[current_group].append((current_channel, line))
                current_channel = None

    return channels

def format_output(channels):
    output = []
    for group, channel_list in channels.items():
        output.append(f"{group},#genre#")
        for channel, url in channel_list:
            output.append(f"{channel},{url}")
        output.append("")  # Add an empty line between groups
    return "\n".join(output).strip()

# 文件路径
file_path = 'freetv.txt'  # 请替换为实际的文件路径

# 解析文件并格式化输出
parsed_channels = parse_m3u(file_path)
formatted_output = format_output(parsed_channels)

# 打印格式化后的输出
print(formatted_output)

# 如果你想将结果保存到新文件，可以取消下面的注释
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(formatted_output)