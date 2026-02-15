from typing import Optional
import threading
import time
from datetime import datetime
import numpy as np
import cv2
from PIL import ImageGrab

# Responsável pela gravação da tela (sáida em vídeo)
class Grav:
    
    def __init__(self):
        self._gravacao_ativa: bool = False
        self._video_writer: Optional[cv2.VideoWriter] = None
        self._thread_gravacao: Optional[threading.Thread] = None
        self._nome_arquivo: str = ""

    def iniciar_gravacao(self, nome_base: str, fps: float = 10.0) -> str:
        """Inicia a gravação da tela e retorna o nome do arquivo gerado."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._nome_arquivo = f"{nome_base}_{timestamp}.avi"

      # Captura uma imagem para obter o tamanho da tela
        screen = ImageGrab.grab()
        screen_size = (screen.width, screen.height)

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self._video_writer = cv2.VideoWriter(
            self._nome_arquivo,
            fourcc,
            fps,
            screen_size
        )

        self._gravacao_ativa = True
        self._thread_gravacao = threading.Thread(target=self._gravar_continuamente, daemon=True)
        self._thread_gravacao.start()

        print(f"Gravação iniciada: {self._nome_arquivo}")
        return self._nome_arquivo

    def _gravar_continuamente(self):
        while self._gravacao_ativa:
            try:
                img = ImageGrab.grab()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if self._video_writer is not None:
                    self._video_writer.write(frame)
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠ Erro na gravação: {e}")
                break

    def parar_gravacao(self):
        """Para a gravação e libera recursos."""
        self._gravacao_ativa = False
        if self._thread_gravacao and self._thread_gravacao.is_alive():
            self._thread_gravacao.join(timeout=5)
        if self._video_writer:
            self._video_writer.release()
            print(f"Gravação finalizada: {self._nome_arquivo}")

    def get_nome_arquivo(self) -> str:
        return self._nome_arquivo


    

