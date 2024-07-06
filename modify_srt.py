import re

# 文件路径
txt_path = r'D:\doc\印度贫民视频口播文案.txt'
srt_path = r'D:\download\ffmpeg-2024-05-15-git-7b47099bc0-full_build\ffmpeg-2024-05-15-git-7b47099bc0-full_build\bin\output.wav.srt'
output_path = r'D:\doc\corrected_subtitle.srt'

# 读取txt文件内容
with open(txt_path, 'r', encoding='utf-8') as f:
    txt_content = f.read()

# 提取txt文件中的句子
txt_sentences = txt_content.replace('！', '!').replace('？', '?').replace('。', '.').split(' ')

# 读取srt文件内容
with open(srt_path, 'r', encoding='utf-8') as f:
    srt_content = f.readlines()

# 定义一个函数来修正srt文件中的错别字
def correct_subtitles(srt_lines, txt_sentences):
    corrected_lines = []
    sentence_index = 0
    
    for line in srt_lines:
        if re.match(r'^\d+\s*$', line):
            # 如果是序号行，直接添加到结果中
            corrected_lines.append(line)
        elif re.match(r'^\d{2}:\d{2}:\d{2},\d{3}\s-->\s\d{2}:\d{2}:\d{2},\d{3}\s*$', line):
            # 如果是时间行，直接添加到结果中
            corrected_lines.append(line)
        else:
            # 如果是字幕行，修正错别字
            corrected_line = line.strip()
            if sentence_index < len(txt_sentences):
                txt_sentence = txt_sentences[sentence_index]
                corrected_line = txt_sentence[:len(corrected_line)]
                sentence_index += 1
            corrected_lines.append(corrected_line + '\n')
    
    return corrected_lines

# 修正srt文件中的错别字
corrected_srt = correct_subtitles(srt_content, txt_sentences)

# 将修正后的srt文件内容保存到本地
with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(corrected_srt)

print(f"修正后的字幕已保存到 {output_path}")
