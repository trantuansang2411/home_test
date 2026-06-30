# test_assistant.py
# Test OptiBot dung Gemini API voi file_search tren cac file da upload

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

UPLOADED_FILES_CACHE = "uploaded_files.json"

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
- Tone: helpful, factual, concise.
- Only answer using the uploaded docs.
- Max 5 bullet points; else link to the doc.
- Cite up to 3 "Article URL:" lines per reply."""


def load_file_refs():
    """Doc danh sach file da upload tu cache"""
    if not os.path.exists(UPLOADED_FILES_CACHE):
        print(f"ERROR: {UPLOADED_FILES_CACHE} not found. Run upload_vectorstore.py first.")
        return []

    with open(UPLOADED_FILES_CACHE, 'r') as f:
        cache = json.load(f)

    file_refs = []
    # Ưu tiên load các bài liên quan đến câu hỏi test
    priority_files = ["how-to-use-youtube-with-optisigns.md", "set-up-add-a-screen.md", "what-hardware-and-devices-are-supported.md"]
    
    # Đầu tiên load các file ưu tiên
    for pf in priority_files:
        if pf in cache:
            try:
                file_ref = client.files.get(name=cache[pf])
                file_refs.append(file_ref)
            except Exception as e:
                pass

    # Sau đó load thêm các file khác cho đủ 50 file (để tránh limit số lượng file đính kèm của API)
    for filename, file_name in list(cache.items()):
        if len(file_refs) >= 50:
            break
        if filename not in priority_files:
            try:
                file_ref = client.files.get(name=file_name)
                file_refs.append(file_ref)
            except Exception as e:
                print(f"  Could not load {filename}: {e}")

    print(f"Loaded {len(file_refs)} file references for context")
    return file_refs


def ask_question(question, file_refs):
    """Gui cau hoi toi Gemini kem theo cac file tai lieu"""
    print(f"\nQuestion: {question}")
    print("-" * 60)

    # Tao contents voi cac file reference va cau hoi
    contents = []
    for file_ref in file_refs:
        contents.append(types.Part.from_uri(
            file_uri=file_ref.uri,
            mime_type="text/plain"
        ))
    contents.append(question)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        )
    )

    print(f"Answer:\n{response.text}")
    return response.text


def main():
    print("=" * 60)
    print("OptiBot Test - Gemini API")
    print("=" * 60)

    # Load file references
    file_refs = load_file_refs()
    if not file_refs:
        return

    # Cau hoi bat buoc theo de bai (sanity check)
    ask_question("How do I add a YouTube video?", file_refs)

    # Test them
    ask_question("How do I set up a new screen?", file_refs)
    ask_question("What devices are supported by OptiSigns?", file_refs)

    print("\n" + "=" * 60)
    print("All tests completed!")


if __name__ == "__main__":
    main()
