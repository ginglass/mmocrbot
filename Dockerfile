FROM python

#RUN apt-get update
#RUN apt-get install -y software-properties-common

RUN apt-get update; \
   apt-get install -y tesseract-ocr tesseract-ocr-por

RUN apt-get install -y libgl1-mesa-glx

RUN pip install mattermost
RUN pip install websockets
RUN pip install websocket-client
RUN pip install pytesseract
RUN pip install cv2-tools
RUN pip install opencv-python


