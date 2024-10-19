from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/get_pdf_links', methods=['GET'])
def get_pdf_links():
    pdf_links = {
        "pdf_links": [
            "https://eprints.unmer.ac.id/id/eprint/282/1/JURNAL%20PENELITIAN%20PENDIDIKAN.pdf",
            "https://pustaka.ut.ac.id/lib/wp-content/uploads/2022/05/Panduan_Scopus.pdf",
            "https://drive.google.com/uc?export=download&id=1FhVv9nDSwha6kbOyqFb46-5bnTHkCKRK",

        ]
    }
    
    return jsonify(pdf_links)

if __name__ == '__main__':
    app.run(debug=True)
