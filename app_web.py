import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración inicial de la página web
st.set_page_config(page_title="Generador QR | ARIZAKA-ICS", page_icon="📱", layout="centered")

# Diccionario de colores
COLORES = {
    "Negro": "black",
    "Blanco": "white",
    "Azul Oscuro": "#003366",
    "Rojo": "darkred",
    "Verde": "darkgreen",
    "Naranja": "#FF8C00",
    "Morado": "purple"
}

# --- INTERFAZ WEB ---
st.title("Generador de Códigos QR Pro")
st.markdown("**Desarrollado por: ARIZAKA-ICS**")

# Controles organizados
datos = st.text_input("1. Enlace o texto principal del QR:", placeholder="https://www.arizaka-ics.com")

col1, col2 = st.columns(2)
with col1:
    color_qr_nombre = st.selectbox("Color del QR:", list(COLORES.keys()), index=0)
with col2:
    color_fondo_nombre = st.selectbox("Color del Fondo:", list(COLORES.keys()), index=1)

logo_subido = st.file_uploader("2. Opcional: Sube un logo central", type=["png", "jpg", "jpeg", "webp"])
texto_base = st.text_input("3. Opcional: Texto en la base (Pie del QR)")

# --- LÓGICA DE GENERACIÓN ---
if datos:
    color_frontal = COLORES[color_qr_nombre]
    color_fondo = COLORES[color_fondo_nombre]

    if color_frontal == color_fondo:
        st.warning("⚠️ El color del QR y el fondo no pueden ser iguales.")
    else:
        # Generar QR base
        qr = qrcode.QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(datos)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color=color_frontal, back_color=color_fondo).convert("RGBA")
        ancho_qr, alto_qr = img_qr.size

        # Insertar Logo
        if logo_subido is not None:
            tamano_caja = int(ancho_qr * 0.3)
            caja_x = (ancho_qr - tamano_caja) // 2
            caja_y = (alto_qr - tamano_caja) // 2

            dibujo = ImageDraw.Draw(img_qr)
            dibujo.rectangle([caja_x, caja_y, caja_x + tamano_caja, caja_y + tamano_caja], fill=color_fondo)

            logo = Image.open(logo_subido).convert("RGBA")
            proporcion = min((tamano_caja * 0.9) / logo.width, (tamano_caja * 0.9) / logo.height)
            nuevo_w, nuevo_h = int(logo.width * proporcion), int(logo.height * proporcion)
            logo = logo.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)
            
            pos_logo_x = caja_x + (tamano_caja - nuevo_w) // 2
            pos_logo_y = caja_y + (tamano_caja - nuevo_h) // 2
            img_qr.paste(logo, (pos_logo_x, pos_logo_y), mask=logo)

        # Insertar Texto en la base
        if texto_base.strip():
            alto_texto = 80 
            img_final = Image.new("RGBA", (ancho_qr, alto_qr + alto_texto), color_fondo)
            img_final.paste(img_qr, (0, 0))

            fuente_default = ImageFont.load_default()
            img_texto_temp = Image.new("RGBA", (800, 100), (255, 255, 255, 0))
            dibujo_temp = ImageDraw.Draw(img_texto_temp)
            
            # Usar textbbox para compatibilidad con versiones recientes de Pillow
            bbox = dibujo_temp.textbbox((0, 0), texto_base, font=fuente_default)
            w_txt, h_txt = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            if w_txt > 0 and h_txt > 0:
                img_txt_recortado = Image.new("RGBA", (w_txt, h_txt + 4), (255, 255, 255, 0))
                ImageDraw.Draw(img_txt_recortado).text((0, 0), texto_base, font=fuente_default, fill=color_frontal)
                
                max_w_txt = int(ancho_qr * 0.8)
                max_h_txt = int(alto_texto * 0.5)
                prop_txt = min(max_w_txt / w_txt, max_h_txt / h_txt)
                
                img_txt_final = img_txt_recortado.resize((int(w_txt * prop_txt), int(h_txt * prop_txt)), Image.Resampling.NEAREST)
                
                pos_txt_x = (ancho_qr - img_txt_final.width) // 2
                pos_txt_y = alto_qr + (alto_texto - img_txt_final.height) // 2
                img_final.paste(img_txt_final, (pos_txt_x, pos_txt_y), mask=img_txt_final)
        else:
            img_final = img_qr

        # --- MOSTRAR RESULTADO ---
        st.markdown("---")
        st.subheader("Vista Previa")
        
        # Mostrar imagen en la web
        st.image(img_final, width=300)

        # Preparar archivo para descarga
        buffer = io.BytesIO()
        img_final.save(buffer, format="PNG")
        byte_im = buffer.getvalue()

        # Botón nativo de descarga
        st.download_button(
            label="💾 Descargar Código QR",
            data=byte_im,
            file_name="QR_Arizaka.png",
            mime="image/png"
        )
else:
    st.info("👆 Ingresa un enlace o texto arriba para generar el código QR.")