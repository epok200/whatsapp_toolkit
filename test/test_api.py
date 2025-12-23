import os

from colorstreak import Logger as log
from dotenv import load_dotenv

from whatsapp_toolkit import (
    PDFGenerator,
    WhatsappClient,
    MongoCacheBackend,
    generar_audio,
    obtener_gif_base64,
    obtener_imagen_base64,
)
from whatsapp_toolkit.schemas import Groups

# =========== FUNCIONES AUXILIARES ============


def _test_mensaje(numero: str, mensaje: str, cantidad: int):
    """ ENVIO DE MENSAJE DE TEXTO SIMPLE """
    log.info("--- Enviando mensaje de texto ---")
    reps = cantidad
    for i in range(1, reps + 1):
        mensaje_i = f"[{i}/{reps}]  {mensaje}"
        engine.send_text(numero, mensaje_i, delay_ms=0)


def _test_pdf(numero: str, titulo: str, contenido: str, filename: str, caption: str):
    """ ENVIO DE PDF COMO DOCUMENTO """
    log.info("--- Enviando PDF como documento ---")
    pdf_b64 = PDFGenerator.generar_pdf_base64(titulo, contenido)
    engine.send_media(
        numero,
        pdf_b64,
        filename=filename,
        caption=caption,
    )


def _test_stiker(numero: str):
    """ ENVIO DE STICKER """
    log.info("--- Enviando sticker ---")
    gif_b64 = obtener_gif_base64()
    engine.send_sticker(numero, gif_b64)
    
    
    
def _test_imagen(numero: str, filename: str, caption: str):
    """ ENVIO DE IMAGEN COMO FOTO """
    log.info("--- Enviando imagen en vez de stiker ---")
    imagen_b64 = obtener_imagen_base64()
    engine.send_media(
        numero,
        imagen_b64,
        filename=filename,
        caption=caption,
        mediatype="image",
        mimetype="image/jpeg",
    )


def _test_ubicacion(numero: str,name: str, address: str, latitude: float, longitude: float):
    """ ENVIO DE UBICACIÓN """
    log.info("--- Enviando ubicación ---")
    engine.send_location(
        numero,
        name=name,
        address=address,
        latitude=latitude,
        longitude=longitude,
    )


def _test_audio(numero: str, texto: str):
    """ ENVIO DE MENSAJE DE AUDIO """
    log.info("--- Enviando audio ---")
    audio_b64 = generar_audio(
        texto=texto,
        idioma="es",
        voz="ar_daniela_high",
        length_scale=1.2, # Velocidad de habla (1.0 = normal)
        sentence_silence=0.3, # Silencio entre oraciones (en segundos)
    )
    if audio_b64:
        resp_audio = engine.send_audio(numero, audio_b64)
        print(f"[AUDIO] Respuesta API: {resp_audio}")
    else:
        print("⚠️  Saltando envío de audio: no se pudo generar el audio (Piper falló o no está configurado).")
        
        

def _obtener_grupo(numero: str, cache: bool = True):
    from time import perf_counter
    log.info("--- Obteniendo lista de grupos ---")
    start_time_all = perf_counter()
    grupos: Groups | None = engine.get_groups_typed(get_participants=False, cache=cache)
    stop_time  = perf_counter()
    
    if grupos is None:
        log.error("❌ No se pudo obtener la lista de grupos.")
        return
    
    conteo_por_tipo = grupos.count_by_kind()
    tiempo_api = stop_time - start_time_all
    log.debug(f"✅ Grupos obtenidos (tiempo API: {tiempo_api:.2f} segundos):")
    log.debug(conteo_por_tipo)
    
    

    


# ============ PRUEBAS BÁSICAS DE LA API CRUDA ============

def iniciar_prueba_api_cruda(numero:str, mensaje: bool = False, pdf: bool = False, sticker: bool = False, imagen: bool = False, ubicacion: bool = False, enviar_audio: bool = False, obtener_grupo: bool = False):
    """Pruebas básicas de la API cruda de Envole (envío de mensajes, medios, audio, ubicación, etc.)."""
    
    if mensaje:
        texto: str = "¡Hola! Esta es una prueba de envío de mensajes vía Envole API 🚀"
        cantidad: int = 1
        _test_mensaje(numero, mensaje=texto, cantidad=cantidad)

    if pdf:
        titulo: str = "Prueba de PDF"
        contenido: str = "Este es un PDF generado y enviado vía Envole API.\n\n¡Saludos!"
        filename: str = "prueba_envole_api.pdf"
        caption: str = "Aquí tienes el PDF solicitado."
        _test_pdf(numero, titulo, contenido, filename, caption)

    if sticker:
        _test_stiker(numero)
        
    
    if imagen:
        filename: str = "prueba_imagen.jpg"
        caption: str = "Aquí tienes la imagen solicitada."
        _test_imagen(numero, filename, caption)


    if ubicacion:
        name: str = "Ubicación de prueba"
        address: str = "Calle Falsa 123, Ciudad Ejemplo"
        latitude: float = 19.4326
        longitude: float = -99.1332
        _test_ubicacion(numero, name, address, latitude, longitude)
    
    
    if enviar_audio:
        texto = """
         Este es un texto de prueba largo, cuidadosamente escrito, pensado para evaluar la pronunciación, la entonación y el ritmo de la voz sintética. Incluye palabras cortas y largas, frases interrogativas y exclamativas, así como enumeraciones y cambios de tono que deberían notarse claramente en el audio.

         En esta grabación se mencionan números, como 1, 2, 3 y 47, además de fechas aproximadas, por ejemplo: “un día cualquiera de septiembre del año dos mil veinticinco”. También se utilizan abreviaturas comunes, tales como Sr., Sra., Dr. y etcétera, para comprobar cómo las interpreta el sistema.

         Además, se mezclan algunos extranjerismos, como “software”, “startup”, “feedback” y “workflow”, junto con palabras en español de uso cotidiano: computadora, teléfono, mensaje, ejercicio, creatividad y precisión. El objetivo es disponer de un texto variado, natural y fluido, que permita apreciar con claridad la calidad general del modelo de voz y detectar posibles errores de pronunciación o de prosodia.

         Por último, este párrafo final sirve para cerrar la prueba con una cadencia suave y comprensible. Si todo funciona correctamente, el resultado debería ser un audio agradable, estable y fácil de entender, ideal para utilizarse en demostraciones, tutoriales o mensajes automatizados de alta calidad.
         """
        _test_audio(numero=numero, texto=texto)
        
    
    if obtener_grupo:
        _obtener_grupo(numero=numero, cache=True)
    
    
# ============ VARIABLS DE ENTORNO ============

load_dotenv(".env.example")


WHATSAPP_API_KEY=os.getenv("WHATSAPP_API_KEY", "")
WHATSAPP_INSTANCE=os.getenv("WHATSAPP_INSTANCE", "")
#WHATSAPP_SERVER_URL=https://evo.apps.leonesfrancos.com/ (SI SE DESEA USAR EL SERVIDOR REMOTO)
WHATSAPP_SERVER_URL=os.getenv("WHATSAPP_SERVER_URL", "http://localhost:8080/")

API_KEY : str = WHATSAPP_API_KEY
INSTANCE : str = WHATSAPP_INSTANCE
SERVER_URL : str = WHATSAPP_SERVER_URL

# ============ CACHCE ENGINE ============
# EJEMPLO DE UNA URL: mongodb://usuario:contraseña@localhost:27017/mi_basededatos
URL_MONGO = os.getenv("URL_MONGO", "")


cache_engine = MongoCacheBackend(
    uri=URL_MONGO,
    ttl_seconds=1000,
)
cache_engine.warmup()


# ============ INICIALIZAR CLIENTE DE WHATSAPP ============
engine = WhatsappClient(
    api_key=API_KEY, 
    server_url=SERVER_URL, 
    instance_name=INSTANCE,
    cache=cache_engine,
)

# ============ CONTACTOS Y GRUPOS ============

contactos_usuarios = {
    "yo": "4778966517",
    "mayra": "4773955633",
    "rodrigo": "4771725703"
}




id_grupos = {
    "epok": "120363402051212345",
    "club_emprendedores": "120363420776163209"
}


def get_group_id(name: str) -> str:
    return id_grupos.get(name, "")


def get_number(name: str) -> str:
    prefix = "521"
    numero_completo = prefix + contactos_usuarios.get(name, "")
    return numero_completo



def get_chat_id(name: str) -> str:
    if name in contactos_usuarios:
        return get_number(name)
    elif name in id_grupos:
        return get_group_id(name)
    else:
        return ""


numero = get_chat_id("yo")


iniciar_prueba_api_cruda(
    numero, 
    # mensaje=True, 
    # pdf=False, 
    # sticker=True,
    # imagen=True, 
    # ubicacion=True,
    # enviar_audio=True,
    obtener_grupo = True
)