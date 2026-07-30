import io
from http import HTTPStatus

import soundfile as sf
from django.http import HttpResponse
from django.shortcuts import render
from neutts import NeuTTS2E
from rest_framework.views import APIView

SPEAKERS = ["emily", "paul", "sophie", "steven"]
MOODS = ["neutral", "angry", "sad", "happy", "surprised", "disgusted", "fearful"]

DEFAULT_SPEAKER = "emily"
DEFAULT_MOOD = "neutral"
SAMPLE_RATE = 24_000


def frontend(request):
    return render(
        request,
        "tts/index.html",
        {"speakers": SPEAKERS, "moods": MOODS},
    )


_tts = None


def get_tts():
    """Charge le modele NeuTTS-2e (poids telecharges au premier appel) une
    seule fois puis le reutilise pour toutes les requetes."""
    global _tts
    if _tts is None:
        _tts = NeuTTS2E()
    return _tts


class SayView(APIView):
    """
    GET /say/?sentence=...&speaker=...&mood=...

    Genere un WAV en local via le modele NeuTTS-2e (package `neutts`) et le
    renvoie tel quel.
    """

    def get(self, request):
        sentence = (request.query_params.get("sentence") or "").strip()
        speaker = (request.query_params.get("speaker") or DEFAULT_SPEAKER).strip().lower()
        mood = (request.query_params.get("mood") or DEFAULT_MOOD).strip().lower()

        if not sentence:
            return HttpResponse(
                'Parametre "sentence" requis.', status=HTTPStatus.BAD_REQUEST
            )
        if speaker not in SPEAKERS:
            return HttpResponse(
                f'speaker invalide "{speaker}", valeurs possibles : {", ".join(SPEAKERS)}',
                status=HTTPStatus.BAD_REQUEST,
            )
        if mood not in MOODS:
            return HttpResponse(
                f'mood invalide "{mood}", valeurs possibles : {", ".join(MOODS)}',
                status=HTTPStatus.BAD_REQUEST,
            )

        try:
            tts = get_tts()
            wav = tts.infer(sentence, speaker=speaker, emotion=mood)
        except Exception as exc:
            return HttpResponse(
                f"Erreur du modele NeuTTS-2e : {exc}",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        buffer = io.BytesIO()
        sf.write(buffer, wav, SAMPLE_RATE, format="WAV")
        return HttpResponse(buffer.getvalue(), content_type="audio/wav")
