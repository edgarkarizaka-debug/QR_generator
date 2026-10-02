import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador QR | ARIZAKA-ICS", page_icon="📱", layout="centered")

COLORES = {
    "Negro": "black", "Blanco": "white", "Azul Oscuro": "#003366",
    "Rojo": "darkred", "Verde": "darkgreen", "Naranja": "#FF8C00", "Morado": "purple"
}

# --- FUNCIÓN PRINCIPAL DE DIBUJO ---
def generar_arte_qr(datos, color_frontal, color_fondo, logo_subido, texto_base):
    qr = qrcode.QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(datos)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color=color_frontal, back_color=color_fondo).convert("RGBA")
    ancho_qr, alto_qr = img_qr.size

    # 1. Insertar Logo
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

    # 2. Insertar Texto Base
    if texto_base.strip():
        alto_texto = 80 
        img_final = Image.new("RGBA", (ancho_qr, alto_qr + alto_texto), color_fondo)
        img_final.paste(img_qr, (0, 0))

        fuente_default = ImageFont.load_default()
        img_texto_temp = Image.new("RGBA", (800, 100), (255, 255, 255, 0))
        dibujo_temp = ImageDraw.Draw(img_texto_temp)
        
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

    return img_final

# --- INTERFAZ WEB ---
st.title("Generador de Códigos QR Avanzado")
st.markdown("**Desarrollado por: ARIZAKA-ICS**")

# Controles de diseño globales (se aplican a todas las pestañas)
with st.expander("🎨 Ajustes de Diseño (Colores y Logo)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        color_qr_nombre = st.selectbox("Color del QR:", list(COLORES.keys()), index=0)
    with col2:
        color_fondo_nombre = st.selectbox("Color del Fondo:", list(COLORES.keys()), index=1)
    
    logo_subido = st.file_uploader("Logo central (opcional):", type=["png", "jpg", "jpeg", "webp"])
    texto_base = st.text_input("Texto en la base del QR (opcional):")

color_frontal = COLORES[color_qr_nombre]
color_fondo = COLORES[color_fondo_nombre]

# --- PESTAÑAS DE FUNCIONALIDAD ---
tab1, tab2, tab3 = st.tabs(["🔗 Enlace Único", "📇 Tarjeta de Contacto", "📂 Multi-Enlace (Notas)"])

# Variable para almacenar los datos a codificar
datos_a_codificar = None

with tab1:
    st.subheader("Redirigir a una sola página web")
    enlace_simple = st.text_input("Ingresa el enlace:", placeholder="https://www.arizaka-ics.com")
    if st.button("Generar QR Simple", type="primary"):
        if enlace_simple:
            datos_a_codificar = enlace_simple
        else:
            st.error("Por favor ingresa un enlace.")

with tab2:
    st.subheader("Crear Contacto Automático")
    st.info("Al escanear este QR, el teléfono abrirá la opción de guardar el contacto en la agenda.")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        nombres = st.text_input("Nombres:")
        apellidos = st.text_input("Apellidos:")
        telefono = st.text_input("Teléfono:")
    with col_c2:
        empresa = st.text_input("Empresa:", value="ARIZAKA-ICS")
        correo = st.text_input("Correo electrónico:")
        web = st.text_input("Sitio Web:")
    
    if st.button("Generar QR de Contacto", type="primary"):
        if nombres and telefono:
            # Formato estándar internacional vCard
            datos_a_codificar = f"BEGIN:VCARD\nVERSION:3.0\nN:{apellidos};{nombres}\nFN:{nombres} {apellidos}\nORG:{empresa}\nTEL:{telefono}\nEMAIL:{correo}\nURL:{web}\nEND:VCARD"
        else:
            st.error("Los campos 'Nombres' y 'Teléfono' son obligatorios.")

with tab3:
    st.subheader("Bloque de Enlaces Múltiples")
    st.info("Muestra una lista de texto con enlaces sin necesidad de pagar páginas de terceros.")
    
    titulo_bloque = st.text_input("Título principal (ej. Menú ARIZAKA-ICS):", value="📌 ENLACES DE INTERÉS")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("**Enlace 1**")
        t1 = st.text_input("Descripción 1:", placeholder="Catálogo de servicios")
        u1 = st.text_input("URL 1:", placeholder="https://...")
    with col_e2:
        st.markdown("**Enlace 2**")
        t2 = st.text_input("Descripción 2:", placeholder="Escríbenos por WhatsApp")
        u2 = st.text_input("URL 2:", placeholder="https://wa.me/...")
        
    nota_final = st.text_input("Nota final (opcional):", placeholder="¡Gracias por contactarnos!")

    if st.button("Generar QR Multi-Enlace", type="primary"):
        if u1 or u2:
            # Formatear el texto como un bloque de notas amigable
            bloque = f"{titulo_bloque}\n\n"
            if t1 and u1: bloque += f"🔹 {t1}:\n{u1}\n\n"
            if t2 and u2: bloque += f"🔹 {t2}:\n{u2}\n\n"
            if nota_final: bloque += f"{nota_final}"
            datos_a_codificar = bloque
        else:
            st.error("Debes incluir al menos un enlace para generar el bloque.")

# --- RENDERIZADO DEL RESULTADO ---
if datos_a_codificar:
    if color_frontal == color_fondo:
        st.warning("⚠️ El color del QR y el fondo no pueden ser iguales.")
    else:
        st.markdown("---")
        st.success("¡Código QR generado con éxito!")
        
        imagen_final = generar_arte_qr(datos_a_codificar, color_frontal, color_fondo, logo_subido, texto_base)
        
        col_res1, col_res2, col_res3 = st.columns([1, 2, 1])
        with col_res2:
            st.image(imagen_final, use_container_width=True)
            
            buffer = io.BytesIO()
            imagen_final.save(buffer, format="PNG")
            
            st.download_button(
                label="💾 Descargar Código QR",
                data=buffer.getvalue(),
                file_name="QR_Arizaka_Pro.png",
                mime="image/png",
                use_container_width=True
            )
