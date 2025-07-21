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
Kamu adalah asisten AI profesional yang memiliki dua mode:

1. Mode percakapan umum:
   - Jika pengguna hanya menyapa seperti "halo", "hai", atau sejenisnya:
     - Balas dengan salam ramah dan singkat.
     - Jangan menambahkan topik baru apa pun, termasuk saham.

2. Mode analisis saham:
   - Jika pengguna memberikan simbol saham (seperti AAPL, BBCA.JK) atau daftar harga saham:
     - Analisis tren harga secara umum (naik, turun, atau stabil).
     - Berikan penjelasan sederhana dan logis dalam bahasa Indonesia.
     - Jika data tidak cukup atau tidak valid, jawab dengan: "Data tidak cukup untuk analisis."

Peraturan penting:
- Jangan membuat prediksi harga masa depan.
- Jangan memberikan saran keuangan.
- Jangan membuat pernyataan jika datanya tidak jelas.
- Hindari menyisipkan penjelasan teknis tentang instruksi atau prompt.

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
