import asyncio  
import random  
  
import edge_tts  
from edge_tts import VoicesManager  
  
TEXT = "Use Microsoft Edge's online text-to-speech service from Python WITHOUT needing Microsoft Edge or Windows or an API key"  
OUTPUT_FILE ="tts\china.mp3"  
  
  
async def _main() -> None:  
    voices = await VoicesManager.create()  
    voice = voices.find(Gender="Female", Language="zh")  
  
    communicate = edge_tts.Communicate(TEXT, random.choice(voice)["Name"])  
    await communicate.save(OUTPUT_FILE)  
  
  
if __name__ == "__main__":  
    asyncio.run(_main())
