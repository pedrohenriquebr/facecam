#!/usr/bin/python3

# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

import os
import cv2
import time
import threading
import requests
import json
import settings
import sys
import time
import argparse


RECOGNITION_HOST = settings.RECOGNITION_HOST
TMP_IMG = settings.TMP_IMG
FACECAM_DATA_DIR = settings.FACECAM_DATA_DIR
WEBCAM_LOCKFILE = settings.WEBCAM_LOCKFILE
WEBCAM_ERRFILE = settings.WEBCAM_ERRFILE
WEBCAM_LOGFILE = settings.WEBCAM_LOGFILE

class Recognition:
    """
    :param duration -> duração do reconhecimento (=-1)
    :param height -> altura das fotos a serem reconhecidas (=240)
    :param width -> largura das fotos a serem reconhecidas (=320)
    :param n_camera -> número da camera a ser usada (=0)
    :param video -> para exibir janela de vídeo da camera (=True)
    :param resize -> redimensionar o quadro de fotos da camera pra alcançar bom desempenho (=True)
    """

    def __init__(self,height=240, width=320, n_camera=0, video=True, resize=True):

        # Camera settings
        self.height = height
        self.width = width
        self.camera = cv2.VideoCapture(n_camera)
        self.video = video
        self.resize = resize

    def start_recognize(self):
        self.run()

    def draw_box(self, name, frame, location):
        top, right, left, bottom = location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35),
                      (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    font, 1.0, (255, 255, 255), 1)

    def run(self):
        print(time.ctime())
        counter = 0
        process_frame = True
        self.names = {}
        while True:
            ret, frame = self.camera.read()
            if self.resize:
                height, width = frame.shape[:2]
                h_scale = self.height/height
                w_scale = self.width/width

                newX, newY = frame.shape[1]*w_scale, frame.shape[0]*h_scale

                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (int(newX), int(newY)))

            # Only process every other frame of video to save time
            if process_frame:
                # salva o frame atual temporariamente
                if self.resize:
                    cv2.imwrite(TMP_IMG, small_frame)
                else:
                    cv2.imwrite(TMP_IMG, frame)
                # envio a imagem temporária pro servidor de reconhecimento
                predictions = send_image(TMP_IMG)
                for person in predictions:
                    name, (top, right, bottom, left) = person[0], person[1]

                    print("encontrei {name} em ({left},{top})".format(
                        name=name, left=left, top=top))

                    if name != 'desconhecido':
                        # marcando a entrada da pessoa
                        if name not in self.names:
                            self.names[name] = [0, 0]
                            self.names[name][0] = int(time.time())

                        else:
                            # atualiza o timestamp da  saida
                            self.names[name][1] = int(time.time())
                    if self.resize:
                        top = int(top / h_scale)
                        left = int(left / w_scale)
                        right = int(right / w_scale)
                        bottom = int(bottom / h_scale)

                    if self.video:
                        # Draw a box around the face
                        self.draw_box(name, frame, (top, right, left, bottom))

            process_frame = not process_frame

            # Display the resulting ima
            if self.video:
                cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q') or os.path.exists(WEBCAM_LOCKFILE):
                break

        # Release handle to the webcam
        self.camera.release()
        cv2.destroyAllWindows()
        # salva em algum arquivo de log
        recognized_file = os.path.join(FACECAM_DATA_DIR,'recognized.log')
        with open(recognized_file, 'w') as f:
            for name in self.names:
                current = self.names[name]
                f.write("{}:{},{}\n".format(name,current[0],current[1]))
        
        print(time.ctime())


def send_image(image_path):
    url = 'http://{RECOGNITION_HOST}:5000/api/recognition'.format(
        RECOGNITION_HOST=RECOGNITION_HOST)
    files = {'file': open(image_path, 'rb')}
    r = requests.post(url, files=files)
    return json.loads(r.text)

def main():
    parser = argparse.ArgumentParser(
        description='Programa para reconhecer alunos com a camera')
    
    parser.add_argument('--camera', dest='n_camera', type=int, default=0,
                        nargs='?', help='número da webcam a ser usada, 0 por padrão ')
    parser.add_argument('--video', dest='use_video', action='store_const', default=False,
                        const=True, help='indicar para exibir vídeo capturado, falso por padrão', required=False)
    arguments = parser.parse_args()

    n_camera = arguments.n_camera
    use_video = arguments.use_video

    recog = Recognition(n_camera=arguments.n_camera, video=use_video)

    recog.start_recognize()


if __name__ == "__main__":
    main()
