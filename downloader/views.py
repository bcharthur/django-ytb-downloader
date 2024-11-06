from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import yt_dlp
import os
from django.conf import settings
import logging

# Configurer le logger
logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'downloader/home.html')


def download_video(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            return render(request, 'downloader/home.html', {'error': 'Veuillez fournir une URL valide.'})
        try:
            logger.info(f"Téléchargement de l'URL : {url}")

            # Options pour yt-dlp
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(settings.BASE_DIR, 'downloads', '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'video')
                video_ext = info_dict.get('ext', 'mp4')
                download_path = ydl.prepare_filename(info_dict)
                download_path = os.path.splitext(download_path)[0] + '.' + video_ext
                logger.info(f"Vidéo téléchargée à : {download_path}")

            # Lire le fichier téléchargé
            with open(download_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(download_path)}"'

            # Optionnel : supprimer le fichier après le téléchargement
            os.remove(download_path)
            logger.info("Vidéo servie et fichier supprimé du serveur.")

            return response
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement : {e}")
            return render(request, 'downloader/home.html', {'error': f"Erreur lors du téléchargement : {str(e)}"})
    else:
        return HttpResponseRedirect(reverse('home'))
