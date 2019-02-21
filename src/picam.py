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
import picamera
import numpy as np

RECOGNITION_HOST = settings.RECOGNITION_HOST
WEBSERVER_HOST = settings.WEBSERVER_HOST
TMP_IMG = settings.TMP_IMG
FACECAM_DATA_DIR = settings.FACECAM_DATA_DIR
WEBCAM_LOCKFILE = settings.WEBCAM_LOCKFILE

class Recognition:
    """
    :param id_aula -> id da aula a ser iniciada, obrigatório
    :param height -> altura das fotos a serem reconhecidas (=240)
    :param width -> largura das fotos a serem reconhecidas (=320)
    :param video -> para exibir janela de vídeo da camera (=True)
    """

    def __init__(self, id_aula, height=240, width=320, video=True):

        # Camera settings
        self.height = height
        self.width = width
        self.camera = picamera.PiCamera()
        self.video = video

        # Smartroom settings
        self.id_aula = id_aula

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
        # "pedro" : [entrada,saida],"fulano":[entrada,saida],...
        self.names = {}
        output = np.empty((self.width * self.height *3, ), dtype=np.uint8)
        self.camera.resolution = (self.width,self.height)
        for x in self.camera.capture_continuous(output,format="bgr",use_video_port=True):
            frame = output.reshape((self.height, self.width, 3))

            # Only process every other frame of video to save time
            if process_frame:
                # salva o frame atual temporariamente
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
        self.camera.close()
        cv2.destroyAllWindows()
        # salva em algum arquivo de log
        with open(FACECAM_DATA_DIR+'/reconhecidos.log', 'w') as f:
            f.write('alunos reconhecidos: \n')
            f.writelines(json.dumps(self.names))
            f.write('\n')

        for name in self.names:
            entrada, saida = self.names[name]
            r = marcar_presenca(name, self.id_aula, entrada, saida)
            print('{aluno} : {marcado}'.format(aluno=name, marcado=r))
        print(time.ctime())


def send_image(image_path):
    url = 'http://{RECOGNITION_HOST}:5002/api/recognition'.format(
        RECOGNITION_HOST=RECOGNITION_HOST)
    files = {'file': open(image_path, 'rb')}
    r = requests.post(url, files=files)
    return json.loads(r.text)


def marcar_presenca(id_aluno, id_aula, entrada, saida):
    if(id_aula > 0):
        r = requests.post('http://{WEBSERVER_HOST}/marcar_presenca.php'.format(WEBSERVER_HOST=WEBSERVER_HOST), data={
            "aula": id_aula, "presente": id_aluno, "entrada": entrada, "saida": saida, "key": "Cefet123"})
        return r.text
    return ''


def main():
    parser = argparse.ArgumentParser(
        description='Programa para reconhecer alunos com a camera')

    parser.add_argument('--aula', dest='id_aula', type=int,
                        help='id  da aula ', required=True)
    parser.add_argument('--video', dest='use_video', action='store_const', default=False,
                        const=True, help='indicar para exibir vídeo capturado, falso por padrão', required=False)
    arguments = parser.parse_args()

    id_aula = arguments.id_aula
    use_video = arguments.use_video

    recog = Recognition(id_aula=arguments.id_aula,video=use_video)
    # inicia o reconhecimento

    recog.start_recognize()


if __name__ == "__main__":
    main()
