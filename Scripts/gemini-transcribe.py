import sys
import os
from google import genai

# Self-healing: If env var is missing, try to read it from a local file
api_key = os.getenv("GOOGLE_API_KEY")

# MODEL = "gemini-2.5-flash"
MODEL = "gemini-3.1-pro-preview"

# PROMPT = """
#     You are an Expert Bilingual Transcriptionist specializing in High-Fidelity, Full-Verbatim records for legal and technical documentation.
#     Task: Transcribe the attached audio into a structured Markdown document.
#     Insert a double line break and a new bolded identifier every time the speaker changes.
# """

# PROMPT = """
#     Act as a professional transcriptionist. 
#     Transcribe the provided audio file strictly following these rules:

#     1. **Full Verbatim**: Include every word exactly as spoken, including filler words (um, uh, like), false starts, and repetitions. Do not clean up the grammar.
#     2. **Speaker Identification**: Identify different speakers as 'Speaker 1', 'Speaker 2', etc., unless their names are mentioned in the audio. Use the format **Speaker Name**: [Text].
#     4. insert a line break every time the speaker changes
#     3. **Markdown Formatting**: 
#         - Use bold for speaker names.
#         - Use clear paragraph breaks for each turn in the conversation and insert a line break every time the speaker changes.
#         - Use [bracketed timestamps] every 2 minutes or when a major speaker shift occurs.
#         - Use *italics* for non-verbal sounds that provide context (e.g., *laughter*, *door slams*, *long pause*).
#     4. **Language**: Transcribe in the original language spoken (English or French). If there is code-switching, transcribe it exactly as it sounds.
# """

# PROMPT = "Transcribe this audio exactly. Detect if it is French or English."

# PROMPT = """
#     # ROLE
#     You are an Expert Multilingual Transcriptionist. Your goal is to produce a high-fidelity, Full-Verbatim record for legal and technical documentation.

#     # TASK
#     Transcribe the attached audio exactly as heard into a structured Markdown document. 

#     # CONSTRAINTS & RULES
#     1. **Full-Verbatim Integrity**: 
#        - Capture ALL spoken content including filler words (uh, um, euh, ah), stutters, false starts, and repetitions.
#        - Do not normalize grammar or "clean up" the speech.
#        - If a word is unintelligible, mark it as [unclear hh:mm:ss].

#     2. **Speaker Identification (Diarization)**:
#        - Identify distinct voices as **Speaker 1**, **Speaker 2**, etc. 
#        - If a name is mentioned in the audio, use the name (e.g., **Yann**, **Julia**).
#        - Insert a double line break and a new bolded identifier every time the speaker changes.

#     3. **Formatting**:
#        - Use Markdown headers for different sections if the audio has distinct phases.
#        - Insert [hh:mm:ss] timestamps at the start of every speaker change.
#        - Insert a line break at every speaker change
#        - Use *italics* for significant non-speech sounds (e.g., *laughter*, *piano playing*, *ambient street noise*).

#     4. **Bilingual Handling**:
#        - Transcribe in the language spoken. If speakers switch between languages, capture the transition exactly without translating.

#     # OUTPUT FORMAT
#     **[Timestamp] Speaker Name**: [Verbatim Text]
# """

PROMPT = """
    # ROLE
    You are an Expert Multilingual Transcriptionist. Your goal is to produce a high-fidelity, Full-Verbatim record for legal and technical documentation.

    # TASK
    - Create a structured summary
    - Give key points
    - Create action items    
    - Transcription of the attached audio exactly as heard into a structured Markdown document. 


    # CONSTRAINTS & RULES
    1. **Full-Verbatim Integrity**: 
       - Capture ALL spoken content including filler words (uh, um, euh, ah), stutters, false starts, and repetitions.
       - Do not normalize grammar or "clean up" the speech.
       - If a word is unintelligible, mark it as [unclear hh:mm:ss].

    2. **Speaker Identification (Diarization)**:
       - Identify distinct voices as **Speaker 1**, **Speaker 2**, etc. 
       - If a name is mentioned in the audio, use the name (e.g., **Yann**, **Julia**).
       - Insert a double line break and a new bolded identifier every time the speaker changes.

    3. **Formatting**:
       - Use Markdown headers for different sections if the audio has distinct phases.
       - Insert [hh:mm:ss] timestamps at the start of every speaker change.
       - Insert a line break at every speaker change
       - Use *italics* for significant non-speech sounds (e.g., *laughter*, *piano playing*, *ambient street noise*).

    4. **Bilingual Handling**:
       - Transcribe in the language spoken. If speakers switch between languages, capture the transition exactly without translating.

    # OUTPUT FORMAT FOR TRANSCRIPTION
    **[Timestamp] Speaker Name**: [Verbatim Text]
"""

if not api_key:
    # Look for a .env file in the same directory as the script
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=")[1].strip().strip('"')

# Now initialize the client
if not api_key:
    print("Error: No API Key found in environment or .env file.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    # Handle paths with spaces
    file_path = " ".join(sys.argv[1:])
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    try:
        # Upload using the new Files service
        # This handles the Telegram .m4a/AAC natively
        uploaded_file = client.files.upload(file=file_path)

        # Transcribe using the latest Flash model
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                PROMPT,
                uploaded_file
            ]
        )

        print(response.text.strip())

        # Cleanup
        client.files.delete(name=uploaded_file.name)

    except Exception as e:
        print(f"Transcription Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()