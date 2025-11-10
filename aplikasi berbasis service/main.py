from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
from datetime import datetime

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)

app = Flask(__name__)
CORS(app)

def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )

# ======================== TEMA HARRY POTTER CSS =========================
HP_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

  body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #eafaf1 0%, #c8f5d5 100%);
    margin: 0;
    padding: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .container {
    background: #ffffffcc;
    border: 2px solid #0b8a43;
    border-radius: 16px;
    box-shadow: 0 4px 25px rgba(11, 138, 67, 0.15);
    padding: 35px;
    width: 90%;
    max-width: 900px;
  }

  h2, h3 {
    color: #0b8a43;
    font-weight: 700;
    margin-bottom: 25px;
    text-align: center;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
  }

  th {
    background: #0b8a43;
    color: white;
    padding: 12px;
    font-size: 1rem;
    letter-spacing: 0.5px;
  }

  td {
    color: #333;
    padding: 10px;
    border-bottom: 1px solid #e0e0e0;
  }

  tr:nth-child(even) {
    background-color: #f7fdf9;
  }

  tr:hover {
    background-color: #eafaf1;
  }

  .btn {
    display: inline-block;
    background: #0b8a43;
    border: none;
    color: #fff;
    border-radius: 8px;
    padding: 8px 15px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  .btn:hover {
    background: #097a3a;
    box-shadow: 0 3px 8px rgba(11, 138, 67, 0.3);
  }

  .card {
    background: #ffffffcc;
    border: 1px solid #b9e6cb;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(11, 138, 67, 0.1);
  }

  input[type="text"], input[type="number"] {
    width: 100%;
    padding: 10px;
    border: 2px solid #b9e6cb;
    border-radius: 8px;
    background: #f9fff9;
    color: #333;
    font-size: 1rem;
    margin-bottom: 10px;
    transition: 0.3s;
  }

  input:focus {
    border-color: #0b8a43;
    outline: none;
    box-shadow: 0 0 5px #0b8a43;
  }

  label {
    color: #0b8a43;
    font-weight: 600;
  }

  .alert {
    background: #d4f5e1;
    color: #0b8a43;
    border: 1px solid #0b8a43;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 15px;
    text-align: center;
  }

  footer {
    margin-top: 20px;
    text-align: center;
    color: #0b8a43;
    font-size: 0.9rem;
  }
</style>
"""


# ======================== HTML TEMPLATE =========================
FORM_HTML = f"""
<!doctype html>
<html lang="id">
  <head>
    <meta charset="utf-8">
    <title>🪄 Form Mahasiswa Hogwarts</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {HP_STYLE}
  </head>
  <body>
    <div class="container my-5">
      <h2 class="mb-4 text-center">Tambah Mahasiswa Hogwarts 🦉</h2>
      {{% if msg %}}
        <div class="alert text-center">{{{{ msg }}}}</div>
      {{% endif %}}
      <form method="post" action="{{{{ url_for('post_mahasiswa') }}}}" class="p-4">
        <div class="mb-3">
          <label>NIM</label>
          <input name="nim" required class="form-control" />
        </div>
        <div class="mb-3">
          <label>Nama</label>
          <input name="nama" required class="form-control" />
        </div>
        <div class="mb-3">
          <label>Tahun Masuk</label>
          <input name="tahun_masuk" pattern="\\d{{4}}" required class="form-control" />
        </div>
        <div class="mb-3">
          <label>Alamat</label>
          <textarea name="alamat" class="form-control"></textarea>
        </div>
        <div class="mb-3">
          <label>Tanggal Lahir</label>
          <input name="tanggal_lahir" type="date" class="form-control" />
        </div>
        <button class="btn btn-primary" type="submit">✨ Kirim</button>
        <a href="{{{{ url_for('list_mahasiswa') }}}}" class="btn btn-outline-dark ms-2">📜 Lihat Data</a>
      </form>
    </div>
  </body>
</html>
"""

LIST_TEMPLATE = f"""
<!doctype html>
<html lang="id">
  <head>
    <meta charset="utf-8">
    <title>📜 Daftar Mahasiswa Hogwarts</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {HP_STYLE}
  </head>
  <body>
    <div class="container my-5 text-center">
      <h2 class="mb-4">Daftar Mahasiswa Hogwarts</h2>
      {{% if msg %}}<div class="alert">{{{{ msg }}}}</div>{{% endif %}}
      <table class="table table-striped table-dark shadow">
        <thead>
          <tr>
            <th>NIM</th><th>Nama</th><th>Tahun Masuk</th><th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          {{% for r in rows %}}
          <tr>
            <td>{{{{ r.nim }}}}</td>
            <td>{{{{ r.nama }}}}</td>
            <td>{{{{ r.tahun_masuk }}}}</td>
            <td>
              <a href="{{{{ url_for('detail_page', nim=r.nim) }}}}" class="btn btn-sm btn-primary">🔍 Detail</a>
              <a href="{{{{ url_for('hapus_mahasiswa', nim=r.nim) }}}}" class="btn btn-sm btn-danger"
                 onclick="return confirm('Yakin ingin menghapus?')">🗑️ Hapus</a>
            </td>
          </tr>
          {{% endfor %}}
        </tbody>
      </table>
      <a href="{{{{ url_for('index') }}}}" class="btn btn-outline-dark mt-3">⬅️ Kembali ke Form</a>
    </div>
  </body>
</html>
"""

DETAIL_TEMPLATE = f"""
<!doctype html>
<html lang="id">
  <head>
    <meta charset="utf-8">
    <title>🔮 Detail Mahasiswa</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {HP_STYLE}
  </head>
  <body>
    <div class="container my-5 text-center">
      <h3 class="mb-4">Detail Mahasiswa Hogwarts</h3>
      <table class="table table-bordered w-50 mx-auto">
        <tr><th>NIM</th><td>{{{{ mhs.nim }}}}</td></tr>
        <tr><th>Nama</th><td>{{{{ mhs.nama }}}}</td></tr>
        <tr><th>Tahun Masuk</th><td>{{{{ mhs.tahun_masuk }}}}</td></tr>
        <tr><th>Alamat</th><td>{{{{ mhs.alamat }}}}</td></tr>
        <tr><th>Tanggal Lahir</th><td>{{{{ mhs.tanggal_lahir }}}}</td></tr>
      </table>
      <a href="{{{{ url_for('list_mahasiswa') }}}}" class="btn btn-outline-dark mt-3">⬅️ Kembali</a>
    </div>
  </body>
</html>
"""

# ======================== ROUTES =========================
@app.route('/')
def index():
    msg = request.args.get('msg', '')
    return render_template_string(FORM_HTML, msg=msg)

@app.route('/mahasiswa')
def list_mahasiswa():
    msg = request.args.get('msg', '')
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM mahasiswa ORDER BY nim")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(LIST_TEMPLATE, rows=rows, msg=msg)

@app.route('/post', methods=['POST'])
def post_mahasiswa():
    payload = {k: request.form.get(k, '').strip() for k in
               ['nim', 'nama', 'tahun_masuk', 'alamat', 'tanggal_lahir']}
    if not all(payload.values()):
        return redirect(url_for('index', msg="⚠️ Semua kolom wajib diisi!"))
    try:
        datetime.strptime(payload['tanggal_lahir'], "%Y-%m-%d")
    except ValueError:
        return redirect(url_for('index', msg="⚠️ Format tanggal salah!"))
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT nim FROM mahasiswa WHERE nim=%s", (payload['nim'],))
        if cur.fetchone():
            cur.close()
            conn.close()
            return redirect(url_for('index', msg=f"❌ NIM {payload['nim']} sudah terdaftar!"))
        cur.execute("INSERT INTO mahasiswa (nim, nama, tahun_masuk, alamat, tanggal_lahir) VALUES (%s,%s,%s,%s,%s)",
                    (payload['nim'], payload['nama'], payload['tahun_masuk'], payload['alamat'], payload['tanggal_lahir']))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('list_mahasiswa', msg="✅ Data berhasil disimpan!"))
    except Exception as e:
        return redirect(url_for('index', msg=f"❌ Error: {e}"))

@app.route('/detail/<nim>')
def detail_page(nim):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM mahasiswa WHERE nim=%s", (nim,))
    mhs = cur.fetchone()
    cur.close()
    conn.close()
    if not mhs:
        return redirect(url_for('list_mahasiswa', msg="⚠️ Data tidak ditemukan!"))
    return render_template_string(DETAIL_TEMPLATE, mhs=mhs)

@app.route('/delete/<nim>')
def hapus_mahasiswa(nim):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM mahasiswa WHERE nim=%s", (nim,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    msg = "🗑️ Data berhasil dihapus!" if deleted else "⚠️ Data tidak ditemukan!"
    return redirect(url_for('list_mahasiswa', msg=msg))

@app.route('/get')
def get_mahasiswa_json():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM mahasiswa ORDER BY nim")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
