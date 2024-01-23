import asyncio

import edge_tts

INPUT_FILE = "tts\input.txt"

VOICE = ["zh-CN-XiaoyiNeural", "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-XiaoyiNeural", "zh-CN-YunjianNeural",
         "zh-CN-liaoning-XiaobeiNeural", "zh-CN-HuihuiRUS", "zh-CN-YunyeNeural", "zh-CN-YunzhiNeural",
         "zh-CN-XiaoxuanNeural", "zh-CN-XiaohanNeural", "zh-CN-XiaomoNeural", "zh-CN-XiaorongNeural", "zh-CN-YunyangNeural",
         "zh-CN-XiaoxueNeural", "zh-CN-XiaoyanNeural", "zh-CN-XiaoyuNeural", "zh-CN-YunxiaNeural", "zh-CN-shaanxi-XiaoniNeural"]
OUTPUT_FILE = r"tts\test.mp3"
WEBVTT_FILE = r"tts\test.vtt"


async def _main() -> None:
    with open(INPUT_FILE, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    communicate = edge_tts.Communicate(text, VOICE[4])
    submaker = edge_tts.SubMaker()
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub(
                    (chunk["offset"], chunk["duration"]), chunk["text"])

    with open(WEBVTT_FILE, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())


if __name__ == "__main__":
    asyncio.run(_main())
