from typing import Union
from platformdirs import user_cache_dir
from pathlib import Path

app_name = "whatsapp_toolkit"
cache_dir = Path(user_cache_dir(app_name))
models_dir = cache_dir / "tts_models"


def generar_audio(texto: str, idioma: str = "es", voz: Union[str, None] = None, length_scale: float = 1.0, sentence_silence: float = 0.0) -> str:
    """Texto -> audio (base64) como nota de voz (OGG/OPUS).

    Por qué esta versión sí funciona:
    - En macOS, el wrapper Python de Piper a veces produce WAV vacío (44 bytes) con ciertos modelos/configs.
    - El binario `piper` (CLI) suele ser más estable en esos entornos.

    Estrategia (simple):
    1) Preferir `piper` CLI si existe (camino estable).
    2) Si no hay CLI, intentar el wrapper Python.
    3) Convertir WAV -> OGG/OPUS con ffmpeg (si existe).

    Parámetros adicionales para control de velocidad:
    - `length_scale`: 1.0 normal, >1.0 más lento, <1.0 más rápido.
    - `sentence_silence`: segundos de silencio entre oraciones cuando lo soporta el wrapper Python.
    """
    import base64
    import shutil
    import subprocess
    import tempfile
    import wave
    from pathlib import Path

    def _pick_voice_id(voz_value: Union[str, None]) -> str:
        vid = (voz_value or "mx_claude_high").strip() if isinstance(voz_value, str) else "mx_claude_high"
        if vid not in VOICES:
            print(f"[TTS] ⚠️  Voz desconocida: {vid!r}. Usando default 'mx_claude_high'.")
            return "mx_claude_high"
        return vid

    def _ensure_voice_files(voice_meta: dict, model_dst: Path, json_dst: Path) -> None:
        if not model_dst.exists():
            _download(voice_meta["onnx_url"], model_dst)
        if not json_dst.exists():
            _download(voice_meta["json_url"], json_dst)

    def _run_piper_cli(piper_bin: str, model_file: Path, wav_file: Path, text: str, ls: float) -> None:
        args = [piper_bin, "--model", str(model_file), "--output_file", str(wav_file)]
        # Speed control: higher length_scale => slower speech
        if ls and ls != 1.0:
            args.extend(["--length_scale", str(ls)])
        subprocess.run(
            args,
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def _try_import_pipervoice():
        # Different Piper Python packages expose different import paths.
        try:
            from piper import PiperVoice  # type: ignore

            return PiperVoice
        except Exception:
            try:
                from piper.voice import PiperVoice  # type: ignore

                return PiperVoice
            except Exception:
                return None

    def _run_piper_python(model_file: Path, wav_file: Path, text: str, ls: float, silence: float) -> None:
        PiperVoice = _try_import_pipervoice()
        if PiperVoice is None:
            raise ModuleNotFoundError("No module named 'piper'")

        voice_obj = PiperVoice.load(str(model_file))

        # Defaults
        sample_rate = 22050
        channels = 1
        cfg = getattr(voice_obj, "config", None)
        if isinstance(cfg, dict):
            sample_rate = int(cfg.get("sample_rate") or sample_rate)
            channels = int(cfg.get("num_channels") or channels)

        # Prefer streaming raw if available
        pcm_chunks: list[bytes] = []
        synth_kwargs = {}
        if ls and ls != 1.0:
            synth_kwargs["length_scale"] = float(ls)
        if silence and silence > 0:
            synth_kwargs["sentence_silence"] = float(silence)

        if hasattr(voice_obj, "synthesize_stream_raw"):
            for chunk in voice_obj.synthesize_stream_raw(text, **synth_kwargs):
                if chunk:
                    pcm_chunks.append(chunk)

        if pcm_chunks:
            pcm_bytes = b"".join(pcm_chunks)
            with wave.open(str(wav_file), "wb") as wav_out:
                wav_out.setnchannels(channels)
                wav_out.setsampwidth(2)
                wav_out.setframerate(sample_rate)
                wav_out.writeframes(pcm_bytes)
        else:
            with wave.open(str(wav_file), "wb") as wav_out:
                wav_out.setnchannels(channels)
                wav_out.setsampwidth(2)
                wav_out.setframerate(sample_rate)
                voice_obj.synthesize(text, wav_out, **synth_kwargs)

    def _wav_size(path: Path) -> int:
        return path.stat().st_size if path.exists() else 0

    def _to_b64(path: Path) -> str:
        return base64.b64encode(path.read_bytes()).decode("utf-8")

    def _convert_wav_to_ogg(ffmpeg: str, wav_file: Path, ogg_file: Path) -> None:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(wav_file),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "24000",
                "-c:a",
                "libopus",
                "-b:a",
                "24k",
                "-vbr",
                "on",
                "-application",
                "voip",
                str(ogg_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    # Directorio de modelos
    models_dir.mkdir(parents=True, exist_ok=True)

    # Voces sugeridas (Piper / rhasspy piper-voices). Puedes ir probando.
    # Nota: "famosa" tipo celebridad no es algo que venga legalmente/por defecto en Piper.
    VOICES = {
        # Español México (mejor calidad, suele sonar más natural que ald)
        "mx_claude_high": {
            "onnx": "es_MX-claude-high.onnx",
            "json": "es_MX-claude-high.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx.json?download=true",
        },
        # Español México (el que ya tienes)
        "mx_ald_medium": {
            "onnx": "es_MX-ald-medium.onnx",
            "json": "es_MX-ald-medium.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/ald/medium/es_MX-ald-medium.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/ald/medium/es_MX-ald-medium.onnx.json?download=true",
        },
        # Español España (varias opciones)
        "es_sharvard_medium": {
            "onnx": "es_ES-sharvard-medium.onnx",
            "json": "es_ES-sharvard-medium.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json?download=true",
        },
        "es_mls_9972_low": {
            "onnx": "es_ES-mls_9972-low.onnx",
            "json": "es_ES-mls_9972-low.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_9972/low/es_ES-mls_9972-low.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_9972/low/es_ES-mls_9972-low.onnx.json?download=true",
        },
        "es_davefx_medium": {
            "onnx": "es_ES-davefx-medium.onnx",
            "json": "es_ES-davefx-medium.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json?download=true",
        },
        # Español Argentina (alta calidad, acento diferente; vale la pena probar)
        "ar_daniela_high": {
            "onnx": "es_AR-daniela-high.onnx",
            "json": "es_AR-daniela-high.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_AR/daniela/high/es_AR-daniela-high.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_AR/daniela/high/es_AR-daniela-high.onnx.json?download=true",
        },
        # Español España (otra voz de dataset MLS; distinta a 9972)
        "es_mls_10246_low": {
            "onnx": "es_ES-mls_10246-low.onnx",
            "json": "es_ES-mls_10246-low.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx.json?download=true",
        },
        # Español España (carlfm es muy ligero; no es el más natural, pero es otra opción rápida)
        "es_carlfm_xlow": {
            "onnx": "es_ES-carlfm-x_low.onnx",
            "json": "es_ES-carlfm-x_low.onnx.json",
            "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/carlfm/x_low/es_ES-carlfm-x_low.onnx?download=true",
            "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/carlfm/x_low/es_ES-carlfm-x_low.onnx.json?download=true",
        },
    }

    def _download(url: str, dst: Path) -> None:
        import requests

        print(f"[TTS] Descargando: {dst.name}")
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            tmp = dst.with_suffix(dst.suffix + ".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            tmp.replace(dst)

    # Elegir voz: si pasas `voz="mx_claude_high"` o similar, usa esa; si no, default recomendado.
    voice_id = _pick_voice_id(voz)
    v = VOICES[voice_id]

    model_path = models_dir / v["onnx"]
    json_path = models_dir / v["json"]

    # Descargar si no existe
    _ensure_voice_files(v, model_path, json_path)

    print(f"[TTS] Usando modelo: {model_path}")
    print(f"[TTS] Voice id: {voice_id}")

    piper_cli = shutil.which("piper")
    ffmpeg_bin = shutil.which("ffmpeg")
    print(f"[TTS] piper cli: {piper_cli}")
    print(f"[TTS] ffmpeg bin: {ffmpeg_bin}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        wav_path = tmp_dir / "tts.wav"
        ogg_path = tmp_dir / "tts.ogg"

        # 1) Generar WAV
        if piper_cli:
            try:
                _run_piper_cli(piper_cli, model_path, wav_path, texto, length_scale)
            except subprocess.CalledProcessError as e:
                err = (e.stderr or b"").decode("utf-8", errors="ignore")
                print(f"[TTS] ❌ Falló piper CLI: {type(e).__name__}: {err}")

        # Si no hay CLI o falló, intentamos wrapper Python (best-effort)
        if (not wav_path.exists()) or (_wav_size(wav_path) <= 44):
            try:
                _run_piper_python(model_path, wav_path, texto, length_scale, sentence_silence)
            except Exception as e:
                print(f"[TTS] ❌ Falló Piper (wrapper Python): {type(e).__name__}: {e}")

        wav_size = _wav_size(wav_path)
        print(f"[TTS] WAV size: {wav_size} bytes")
        if wav_size <= 44:
            return ""  # no audio

        # 2) Convertir a OGG/OPUS (nota de voz)
        if ffmpeg_bin:
            try:
                _convert_wav_to_ogg(ffmpeg_bin, wav_path, ogg_path)
            except subprocess.CalledProcessError as e:
                err = (e.stderr or b"").decode("utf-8", errors="ignore")
                print(f"[TTS] ❌ Falló ffmpeg: {type(e).__name__}: {err}")
                return _to_b64(wav_path)

            ogg_size = _wav_size(ogg_path)
            print(f"[TTS] OGG size: {ogg_size} bytes")
            if ogg_size > 0:
                return _to_b64(ogg_path)

        # Sin ffmpeg: devolvemos WAV
        return _to_b64(wav_path)
