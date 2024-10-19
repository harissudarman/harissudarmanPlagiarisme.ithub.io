import io
import PyPDF2
import streamlit as st
import requests
import Levenshtein
import time
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Download resources nltk
nltk.download('punkt_tab')
nltk.download('stopwords')

# Fungsi untuk preprocessing teks
def preprocess_text(text):
    text = text.lower()
    words = word_tokenize(text)
    stop_words = set(stopwords.words('indonesian'))
    words = [word for word in words if word not in stop_words]
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    words = [stemmer.stem(word) for word in words]
    return " ".join(words)
# Fungsi untuk membaca teks dari PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text()
    return text

# Fungsi untuk mendapatkan daftar URL PDF dari endpoint API
def fetch_pdf_links():
    url = "http://127.0.0.1:5000/get_pdf_links"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "pdf_links" in data:
            return data["pdf_links"]
        else:
            st.error("Tidak ada 'pdf_links' dalam response JSON.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mendapatkan data dari {url}. Error: {e}")
        return []

# Fungsi untuk mendownload teks PDF dari URL
def fetch_pdf_text_from_url(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
        return text
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mendownload PDF dari {pdf_url}. Error: {e}")
        return ""

# Fungsi untuk menghitung skor kemiripan
def calculate_similarity(text1, text2):
    return Levenshtein.ratio(text1, text2) * 100

# Fungsi utama aplikasi
def main():
    st.title("Aplikasi Deteksi Plagiarisme")

    # Upload PDF
    uploaded_pdf = st.file_uploader("Unggah file PDF", type="pdf")

    if uploaded_pdf:
        # Tampilkan teks hasil ekstraksi PDF
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        #st.subheader("Hasil Ekstraksi Teks dari PDF:")
        #st.write(pdf_text)  # Tampilkan teks PDF yang diekstrak

        if st.button("Cek Plagiarisme"):
            start_time = time.time()

            # Preprocessing teks PDF
            processed_pdf_text = preprocess_text(pdf_text)


            # Ambil daftar link PDF dari JSON via cURL
            pdf_links = fetch_pdf_links()

            if processed_pdf_text and pdf_links:
                highest_similarity = 0
                best_match_url = ""

                for pdf_url in pdf_links:
                    comparison_text = fetch_pdf_text_from_url(pdf_url)

                    if comparison_text:
                        processed_comparison_text = preprocess_text(comparison_text)
                        similarity = calculate_similarity(processed_pdf_text, processed_comparison_text)

                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match_url = pdf_url

                plagiarism_percentage = highest_similarity
                accuracy = 100 - highest_similarity

                end_time = time.time()
                processing_time = end_time - start_time

                st.success(f"Persentase plagiarisme : {plagiarism_percentage:.2f}% ")
                st.info(f"Akurasi deteksi: {accuracy:.2f}%")
                st.write(f"Lama proses: {processing_time:.2f} detik")
            else:
                st.error("Gagal memproses teks PDF atau mendapatkan data pembanding.")
        else:
            st.info("Tunggu tombol ditekan untuk memulai cek plagiarisme.")

if __name__ == "__main__":
    main()
