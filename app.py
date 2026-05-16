import os
import io
from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

W = 190  # largura util A4 (210mm - 10mm margens)


def get_openai_client():
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY nao configurada no arquivo .env")
    return OpenAI(api_key=api_key)


def formatar_em_topicos(descricao, cargo, empresa):
    """Chama a OpenAI para organizar a descricao em topicos (um por linha)."""
    if not descricao.strip():
        return descricao
    try:
        client = get_openai_client()
        prompt = (
            "Divida o texto abaixo em topicos, um por linha, comecando cada um com '-'.\n"
            "IMPORTANTE: nao altere, resuma nem reescreva o conteudo. "
            "Apenas identifique onde cada atividade comeca e coloque em uma linha separada.\n"
            f"Texto: {descricao}\n"
            "Retorne apenas os topicos, sem introducao nem explicacao."
        )
        response = get_openai_client().chat.completions.create(
            model="gpt-5.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return descricao


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    dados = request.json

    # Formata automaticamente cada descricao de experiencia em topicos via IA
    for exp in dados.get("experiencias", []):
        if exp.get("descricao") and exp.get("empresa"):
            exp["descricao"] = formatar_em_topicos(
                exp["descricao"], exp.get("cargo", ""), exp.get("empresa", "")
            )

    pdf = CurriculoPDF()
    pdf._add_fonts()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.cabecalho(dados)

    if dados.get("objetivo"):
        pdf.titulo_secao("OBJETIVO")
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, dados["objetivo"])
        pdf.ln(4)

    formacoes = [f for f in dados.get("formacoes", []) if f.get("instituicao")]
    if formacoes:
        pdf.titulo_secao("FORMAÇÃO ACADÊMICA")
        for form in formacoes:
            pdf.linha_formacao(form)

    experiencias = [e for e in dados.get("experiencias", []) if e.get("empresa")]
    if experiencias:
        pdf.titulo_secao("EXPERIÊNCIAS PROFISSIONAIS")
        for exp in experiencias:
            pdf.linha_experiencia(exp)

    if dados.get("habilidades"):
        pdf.titulo_secao("HABILIDADES E COMPETÊNCIAS")
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, dados["habilidades"])
        pdf.ln(4)

    certificacoes = [c for c in dados.get("certificacoes", []) if c.get("nome")]
    if certificacoes:
        pdf.titulo_secao("CERTIFICAÇÕES E CURSOS")
        for cert in certificacoes:
            pdf.linha_certificacao(cert)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    nome_arquivo = dados.get("nome", "curriculo").replace(" ", "_")
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"curriculo_{nome_arquivo}.pdf",
    )


WINDOWS_FONTS = "C:/Windows/Fonts"

class CurriculoPDF(FPDF):
    def header(self):
        pass

    def _add_fonts(self):
        self.add_font("Arial", style="",  fname=f"{WINDOWS_FONTS}/arial.ttf")
        self.add_font("Arial", style="B", fname=f"{WINDOWS_FONTS}/arialbd.ttf")
        self.add_font("Arial", style="I", fname=f"{WINDOWS_FONTS}/ariali.ttf")
        self.add_font("Arial", style="BI",fname=f"{WINDOWS_FONTS}/arialbi.ttf")

    def _linha(self):
        self.set_draw_color(0, 0, 0)
        self.line(self.l_margin, self.get_y(), self.l_margin + W, self.get_y())

    def cabecalho(self, dados):
        self.set_font("Arial", "B", 22)
        self.cell(0, 12, dados.get("nome", "").upper(), new_x="LMARGIN", new_y="NEXT", align="C")

        partes = []
        if dados.get("cidade"):   partes.append(dados["cidade"])
        if dados.get("telefone"): partes.append(dados["telefone"])
        if dados.get("email"):    partes.append(dados["email"])
        if dados.get("linkedin"): partes.append(dados["linkedin"])

        self.set_font("Arial", "", 9)
        self.cell(0, 5, "   ".join(partes), new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)

    def titulo_secao(self, titulo):
        self.set_font("Arial", "B", 11)
        self.cell(0, 6, titulo, new_x="LMARGIN", new_y="NEXT")
        self._linha()
        self.ln(3)

    def _linha_dupla(self, esq_bold, esq_italic, dir_bold, dir_italic):
        col_esq = W * 0.72
        col_dir = W * 0.28

        self.set_font("Arial", "B", 10)
        self.cell(col_esq, 5, esq_bold)
        self.cell(col_dir, 5, dir_bold, align="R", new_x="LMARGIN", new_y="NEXT")

        if esq_italic or dir_italic:
            self.set_font("Arial", "I", 9)
            self.cell(col_esq, 4, esq_italic)
            self.cell(col_dir, 4, dir_italic, align="R", new_x="LMARGIN", new_y="NEXT")

    def _bullets(self, texto):
        if not texto.strip():
            return
        self.set_font("Arial", "", 10)
        indent = 5
        for linha in texto.strip().splitlines():
            linha = linha.strip().lstrip("-•").strip()
            if not linha:
                continue
            self.set_x(self.l_margin + indent)
            self.multi_cell(
                self.epw - indent, 5,
                "• " + linha,
                new_x="LMARGIN",
                new_y="NEXT",
            )

    def linha_experiencia(self, exp):
        periodo = f"{exp.get('inicio', '')} - {exp.get('fim', 'Momento')}"
        self._linha_dupla(
            exp.get("empresa", ""), exp.get("cargo", ""),
            periodo, exp.get("cidade", "")
        )
        self._bullets(exp.get("descricao", ""))
        self.ln(3)

    def linha_formacao(self, form):
        self._linha_dupla(
            form.get("instituicao", ""), form.get("curso", ""),
            form.get("ano_conclusao", ""), ""
        )
        self.ln(3)

    def linha_certificacao(self, cert):
        col_esq = W * 0.72
        col_dir = W * 0.28
        self.set_font("Arial", "B", 10)
        self.cell(col_esq, 5, cert.get("nome", ""))
        self.cell(col_dir, 5, cert.get("data", ""), align="R", new_x="LMARGIN", new_y="NEXT")
        if cert.get("competencias"):
            self.set_font("Arial", "", 9)
            self.set_x(self.l_margin + 5)
            self.multi_cell(W - 5, 4, f"Competências: {cert['competencias']}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


if __name__ == "__main__":
    app.run(debug=True)
