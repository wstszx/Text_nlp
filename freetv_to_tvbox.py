import re

def parse_tv_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to match the TV channel and URL lines
    pattern = re.compile(r'#EXTINF:-1 tvg-name="([^"]+)" tvg-logo="[^"]+" tvg-id="[^"]+" group-title="([^"]+)",([^#\n]+)\n(https?://[^\s]+)')

    matches = pattern.findall(content)

    output = {}
    for match in matches:
        tvg_name, group_title, display_name, url = match
        if group_title not in output:
            output[group_title] = []
        output[group_title].append((display_name.strip(), url.strip()))

    return output

def save_formatted_output(parsed_data, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for group_title, channels in parsed_data.items():
            file.write(f"{group_title},#genre#\n")
            for display_name, url in channels:
                file.write(f"{display_name},{url}\n")

if __name__ == "__main__":
    input_file_path = 'freetv.txt'  # Replace with the path to your input txt file
    output_file_path = 'output.txt'  # Replace with the path to your desired output txt file
    parsed_data = parse_tv_data(input_file_path)
    save_formatted_output(parsed_data, output_file_path)