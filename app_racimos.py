import streamlit as st
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import io
import tempfile

# ---------------------------------
# TAMAÑO ETIQUETA
# 76 mm x 25 mm
# ---------------------------------

page_width = 2.5 * cm
page_height = 7.6 * cm


# ---------------------------------
# CÓDIGOS
# ---------------------------------

def codigo_material(material):

    mapa = {
        "CARGADOR": "C",
        "PITON": "P",
        "BRAZO": "B"
    }

    return mapa.get(material, "X")


def codigo_racimo(tipo_racimo):

    mapa = {
        "SIMPLE": "SIM",
        "DOBLE": "DOB"
    }

    return mapa.get(tipo_racimo, "XXX")


# ---------------------------------
# PDF
# ---------------------------------

def generar_pdf(
    campaña,
    tipo_conteo,
    material,
    tipo_racimo,
    numero_inicial,
    cantidad
):

    temp_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    c = canvas.Canvas(
        temp_pdf.name,
        pagesize=(page_width, page_height)
    )

    for numero in range(
        numero_inicial,
        numero_inicial + cantidad
    ):

        codigo_racimo_num = f"R{numero:05d}"

        codigo_qr = (
            f"{campaña}-"
            f"{tipo_conteo}-"
            f"{codigo_material(material)}-"
            f"{codigo_racimo(tipo_racimo)}-"
            f"{codigo_racimo_num}"
        )

        # -------------------------
        # GENERAR QR
        # -------------------------

        qr = qrcode.make(codigo_qr)

        buffer = io.BytesIO()

        qr.save(
            buffer,
            format="PNG"
        )

        buffer.seek(0)

        img = Image.open(buffer)

        # -------------------------
        # ESPACIO SUPERIOR
        # PARA AMARRE
        # -------------------------

        espacio_superior = 2.4 * cm

        # -------------------------
        # QR
        # -------------------------

        qr_size = 2.4 * cm

        qr_y = (
            page_height
            - espacio_superior
            - qr_size
        )

        c.drawInlineImage(
            img,
            (page_width - qr_size) / 2,
            qr_y,
            qr_size,
            qr_size
        )

        # -------------------------
        # TEXTO PEQUEÑO BAJO QR
        # -------------------------

        c.setFont(
            "Helvetica",
            4.5
        )

        c.drawCentredString(
            page_width / 2,
            qr_y - 0.10 * cm,
            codigo_qr
        )

        # -------------------------
        # TEXTO PRINCIPAL
        # -------------------------

        c.setFont(
                "Helvetica-Bold",
                9
            )
            
            y_texto = qr_y - 1.0 * cm
            
            c.drawCentredString(
                page_width / 2,
                y_texto,
                f"{tipo_conteo} CONTEO"
            )
            
            c.drawCentredString(
                page_width / 2,
                y_texto - 0.45 * cm,
                material
            )
            
            c.drawCentredString(
                page_width / 2,
                y_texto - 0.90 * cm,
                tipo_racimo
            )
            
            c.drawCentredString(
                page_width / 2,
                y_texto - 1.35 * cm,
                f"{numero}"
            )
        c.showPage()

    c.save()

    return temp_pdf.name


# ---------------------------------
# STREAMLIT
# ---------------------------------

st.title("Generador de Etiquetas de Racimos")

campaña = st.text_input(
    "Campaña",
    value="UV26"
)

tipo_conteo = st.selectbox(
    "Tipo de conteo",
    [
        "1ER",
        "2DO",
        "3RO",
        "4TO"
    ]
)

material = st.selectbox(
    "Tipo de material",
    [
        "CARGADOR",
        "PITON",
        "BRAZO"
    ]
)

tipo_racimo = st.selectbox(
    "Tipo de racimo",
    [
        "SIMPLE",
        "DOBLE"
    ]
)

numero_inicial = st.number_input(
    "Número inicial",
    min_value=1,
    value=1
)

cantidad = st.number_input(
    "Cantidad de etiquetas",
    min_value=1,
    value=100
)

if st.button("Generar PDF"):

    pdf = generar_pdf(
        campaña,
        tipo_conteo,
        material,
        tipo_racimo,
        numero_inicial,
        cantidad
    )

    with open(pdf, "rb") as f:

        st.download_button(
            label="Descargar PDF",
            data=f,
            file_name=(
                f"{campaña}_"
                f"{tipo_conteo}_"
                f"{material}_"
                f"{tipo_racimo}.pdf"
            ),
            mime="application/pdf"
        )
