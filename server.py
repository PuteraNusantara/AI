import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import ast

app = Flask(__name__)
CORS(app)

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"

SYSTEM_PROMPT = """
Kamu adalah asisten AI yang sangat sederhana. Tugas kamu hanya dua:

1. Jika user menyapa (contoh: "halo", "hai", "pagi"), jawab dengan salam singkat. Jangan membahas hal lain.

2. Jika user mengirim daftar angka harga saham atau simbol saham, tugasmu hanya:
- Menyebutkan apakah tren harga naik, turun, atau stabil.
- Jika data terlalu sedikit, jawab: "Data tidak cukup untuk analisis."

Jangan membuat prediksi, jangan memberi saran, jangan menyebutkan hal yang tidak diminta.
Jawab hanya sesuai pertanyaan user.
Gunakan bahasa Indonesia yang singkat dan jelas.


"""

def ai_khusus(prompt_user):
    # Buat prompt gabungan user + sistem dengan struktur jelas
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt_user}\nJawab secara singkat dan akurat tidak berlebihan:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()
        hasil = data.get("response", "❌ Tidak ada respons dari model.")
        hasil = hasil.replace('\\"', '"').strip()
        
        # Validasi output aneh
        if "maaf" not in hasil.lower() and (
            "bisbol" in hasil.lower() or 
            "hubungi dan terus menerka" in hasil.lower() or 
            len(hasil.split()) < 3
        ):
            return "❌ Maaf, respons tidak valid. Silakan ulangi pertanyaan yang sesuai topik PO."
        
        return hasil
    
    except requests.exceptions.RequestException as e:
        return f"❌ Gagal konek ke AI: {e}"
    


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response = ai_khusus(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        print("Linza AI Saham\nKetik 'exit' untuk keluar.\n")
        while True:
            user_input = input("Kamu: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                break
            print("AI:", ai_khusus(user_input), "\n")
    else:
        app.run(debug=True)
